# PSERV-03 F1 设计审查：HF tokenizer 增量解码方案（2026-08-28）

> 状态：设计草稿（只读研究产出）。未修改任何源码；本回合不提交、不 push。
> 本文档供用户决策，决策后授权代码修改再进入实现。

## 0. 问题与约束（F1 证据）

- 实测：HF tokenizer 后端下 SSE 每请求仅 1 个整段文本 chunk（`chunks=1`、`TTFT≈duration`、
  `TPOT≈0` 失真），因为 `BufferedDecoder::push` 只缓冲返回 `Ok(None)`、`finish` 一次性解码
  （src/tokenizer.rs:382-395）。loadgen 无 bug，但 PSERV-03 的 TTFT/TPOT A/B 基于此语义无意义。
- 等价性基准（方案正确性的判定标准）：
  `HuggingFaceTokenizer::try_decode(tokens) == self.inner.decode(tokens, true)`
  （src/tokenizer.rs:341-343 = tokenizers 0.19.1 `Tokenizer::decode(&[u32], skip_special_tokens=true)`，
  内部：id → added_vocabulary 查 token 字符串 → 过滤 `is_special_token` → `Decoder::decode` 链）。
- 增量解码的正确性定义（本项目纪律）：对任意成功生成的 token 序列，增量输出的全部片段拼接
  必须等于一次性 `try_decode` 的文本（src/tokenizer.rs:85-95 已有的 `TokenizerTrait` 契约注释）。
- **禁止方案**：完整 prefix 重解码后取 suffix（每次对全部历史 token 重 decode）。原因：
  byte-level 等 decoder 会修改尾部字节序列（`from_utf8_lossy` 替换未完成序列为 U+FFFD），
  已发送文本无法撤回；且 O(n²) 时间。

## 1. 现状代码路径（研究结论）

| 路径 | 现状 | 与 F1 的关系 |
|------|------|--------------|
| Qwen2 decoder 链 | `{"type":"ByteLevel", add_prefix_space:false}`（models/tokenizer.json）；tokenizers 0.19.1 实现 `decode_chain`：token 字符串字符经 CHAR_BYTES 表还原字节 → 拼接 → `from_utf8_lossy` 整体解码（pre_tokenizers/byte_level.rs:156-173） | 字节流模型：**跨 token 的 UTF-8 码点拆分**可能被整体 decode 修正；单块 decode 会 lossy 替换 → 流式必须字节级安全边界 |
| 特殊 token | added_tokens 22 个（`<|endoftext|>` 等，全部 `special=true`）；decode 时按 `is_special_token` 过滤（tokenizer/mod.rs:850-855） | 增量解码必须镜像同一过滤 |
| engine 每步 | `step_events`：apply_stop_sequences（**先于** decoder.push）→ 对 generated 逐 token `decoder.push` → `collect_completed_requests`（成功请求 `decoder.finish`；失败/取消 remove 不 finish） | stop 命中时 `decoders.remove`（无 finish）→ 与增量 decoder 兼容（见 §6） |
| server SSE | `stream_response`：`RequestEvent::Chunk` → 逐 chunk event；**Chunk 发送失败 == 客户端断开 → engine.cancel_request**（server.rs:720-732） | **BufferedDecoder 下断开检测被推迟到 finish 时刻**（每请求仅 1 个 chunk）；增量 decoder 每 token 一个 chunk → 断开检测及时（方案 A 附加收益） |
| n>1 | server 为每个候选独立 submit（独立 request/decoder/事件流）→ `stream_response_multi` fan-in | 每个候选 decoder 独立，无共享状态；但 multi 路径**无客户端断开→cancel 的反向信号**（fan-in 只 break 内部通道）→ n>1 取消缺口（属 PSERV-05，设计需标注） |
| cancel | `engine.cancel_request` → scheduler.cancel_by_request_id → 请求终态排出，decoder remove 不 finish | 增量 decoder 无泄漏（decoder 随 request 销毁） |

## 2. 方案 A：安全的增量 decoder（字节级 look-behind + UTF-8 安全边界）

**核心思想**：对 ByteLevel 链，解码等价于「token 字符串 → 字节流 → UTF-8 解码」。
UTF-8 是自同步编码：**已完整落入 UTF-8 码点边界之前的字节前缀，追加任何后续字节都不会改变**。
因此按码点边界增量 flush 是单调且无后向依赖的——这是等价性可证明的基础，
不是"重解码取后缀"（每次只对**未决尾部**解码，历史部分从不重算）。

### 2.1 API 与生命周期

```rust
// 保持现有 trait 不变（src/tokenizer.rs:97-106）
pub trait IncrementalDecoder: Send {
    fn push(&mut self, token: TokenId) -> Result<Option<String>, String>;
    fn finish(&mut self) -> Result<Option<String>, String>;
}
```
- 实现 `ByteLevelIncrementalDecoder`（或 `BytesAndUtf8SafeDecoder`）替换 `BufferedDecoder`
  （仅替换 `HuggingFaceTokenizer::create_decoder` 一处；SimpleTokenizer 不动）。
- 生命周期（与现状一致，无需改 engine/server）：
  请求 submit → create_decoder 持有 → 每 step `push`（返回可下发片段）→
  成功终态 `finish`（冲刷尾段）→ 失败/取消/stop 命中 `remove`（不 finish）。

### 2.2 状态与算法

```
状态：pending_tokens: Vec<TokenId>   // 未决尾部（未 flush 的 token）
      pending_bytes: Vec<u8>         // pending_tokens 还原的字节（惰性维护）
      flushed: String                // 已发送文本（测试断言用，可关）
```
- 每 `push(token)`：
  1. 镜像一次性 decode 的过滤：`id_to_token(token)` → None（未知 id）跳过；
     `is_special_token(token)` 且 skip_special → 跳过（不进入字节流）。
     **这些 token 不产生文本**——与 `Tokenizer::decode(tokens, true)` 行为一致。
  2. 非特殊 token：还原字节（CHAR_BYTES 表逐字符映射；字符不在表内则取该字符自身 UTF-8 字节，
     与 byte_level.rs:161-169 的 `unwrap_or_else(|| t.as_bytes())` 完全一致）→ append 到 pending_bytes，
     token 记录到 pending_tokens。
  3. 计算安全边界：从 pending_bytes 尾部按 UTF-8 前缀规则扫描，找到「最后完整码点」的位置 `k`；
     `flushed_bytes = pending_bytes[..k]`、`pending_bytes = pending_bytes[k..]`
     （相应地从 pending_tokens 尾部切分同字节长度的 token 集合——按 token 字节序跟踪，保证
     未决 token 与未决字节对应；若 k 落在 token 中间（跨 token 拆码点），允许该 token 保留在
     pending 中）。UTF-8 前缀校验：对尾部 1-3 个字节做标准前缀判定（0b0xxxxxxx 独立；
     0b110xxxxx 需 1 续字节；0b1110xxxx 需 2；0b11110xxx 需 3），不完整则全部保留。
  4. 若 `flushed_bytes` 非空：`String::from_utf8(flushed_bytes)`（必成功，完整码点）→ 返回
     `Some(text)`；否则 `Ok(None)`。
- `finish()`：对剩余 pending_bytes `String::from_utf8`（若非法——理论不可能，字节来自合法
  token——则与一次性 decode 一致用 `from_utf8_lossy` 兜底并保留错误告警）返回 `Some(tail)`。

### 2.3 Unicode、ByteFallback、WordPiece、特殊 token 边界

| 边界 | 处理 |
|------|------|
| UTF-8 多字节跨 token | 字节级安全边界算法（§2.2 步骤 3）保证不拆码点；等价性证明依赖 UTF-8 自同步 |
| ByteFallback | 当前 Qwen2 链无 ByteFallback；若未来启用（token 为 `<0xXX>` 形式），其解码在**文本层**合并（tokenizer/mod.rs 的 decoder 链），不在字节层面——增量策略需退化为「尾随 look-behind K 个 token 不 flush（K≥2）+ ByteFallback 文本合并校验」，并扩展 property test。设计上为 decoder 链增加 `supports_byte_model() -> bool` 能力标志：ByteLevel/无 decoder → true（A1 精确）；Fuse/ByteFallback/WordPiece/Sequence → false（回退 A2，§2.5） |
| WordPiece | 与 ByteFallback 同理：跨 token 的 `##` 拼接在文本层 → 回退 A2；Qwen2 不适用（BPE） |
| 特殊 token | decode 过滤镜像（§2.2 步骤 1）；特殊 token 夹在中间时，其前后字节各自独立 flush，拼接后与一次性 decode 等价（因为 filter 在字节还原前执行） |
| `add_prefix_space` | 仅影响 pre-tokenize（编码侧），解码侧 ByteLevel 的 prefix space 由 token 的字节还原自然携带；与一次性 decode 一致（token 字符串本身就含 Ġ 等字符） |

### 2.4 正确性论证（等价性）

设 token 序列 T = t1..tn，B(T) = 一次性字节流（过滤特殊 token 后按字节还原拼接），
D(x) = from_utf8 解码。一次性输出 = D(B(T))。
增量算法每步输出 D(p_i)，其中 B(T) = f1 f2 … fm（按码点边界切分，fi 为完整码点字节序列），
且每次 flush 的正是连续的完整码点前缀：即输出 = D(f1) + D(f2) + … + D(fm) + 尾段。
因 UTF-8 序列的码点边界判定是**前缀闭包**（一个码点要么完整出现要么完全不出现，不可能
"先出现半个、再被后续字节补成同一个码点且改变前段"），故 {fi} 的分割与一次性解码的分割
一致，拼接 == 一次性输出。**证明前提**：字节还原函数确定性（CHAR_BYTES 映射）且与
`decode_chain` 的前半段逐一对应——实现时用**同一份**字节表的移植并做差分测试。

### 2.5 通用 decoder 链回退（A2）

- 对非字节模型链（ByteFallback/WordPiece/Fuse/Sequence/Strip），保留尾部 K（默认 16，可配置）
  token 不 flush，只把 `pending[..len-K]` decode（每次对新出现的可作为边界的完整 token 块做
  一次性 decode 取其文本并丢弃尾部）——这是 llama.cpp/vLLM 常用的 look-behind 近似。
- **诚实边界**：A2 无法对任意链证明严格等价（尾部可能被后续 token 改写）；用 property test
  在大 K 下覆盖常见链；发现不等价用例则提示增大 K 或拒绝该链（`create_decoder` 返回错误）。
- 当前 Qwen2（ByteLevel）走 A1 精确路径，**不触发 A2**。

### 2.6 stop / cancel / finish / n>1

| 路径 | 行为 |
|------|------|
| stop 序列命中 | `apply_stop_sequences` 在 push 之前运行（engine.rs:374）：`try_decode(output_tokens)`（全量，与增量 decoder 无关）→ 命中则 `tokens_before_char` 截断 + `decoders.remove`。已推送片段均为 stop 之前的 token 文本（合法）；残留尾段不 finish、不发送 → 无撤回问题。**对照现状注释"已推送片段无法撤回"的前提变弱**：stop 命中 token 不再 push，唯一残留是 stop 序列首 token 之前已 flush 的正常文本 ✓ |
| cancel（客户端断开） | Chunk 发送失败 → `cancel_request` → decoder remove 不 finish（server.rs:720-732）。增量 decoder 使断开检测从「finish 时刻」提前到「每个 token 时刻」→ **资源回收更快**（PSERV-05 改善项） |
| finish（成功） | `collect_completed_requests` → `decoder.finish()` flush 尾段；拼接完整 ✓ |
| 失败请求 | 不 finish，remove；尾段丢弃；SSE 端已发送的片段仍留在客户端（不可撤回，可接受——错误上报在 Done/final event） |
| n>1 | 每个候选独立 decoder（server 为每个候选独立 submit，fan-in SSE）；无共享状态、无同步需求。**风险标注**：multi 路径客户端断开不会触发 `cancel_request`（fan-in 转发任务只 break 内部通道），请求会继续生成至终态——属既有限制（位于 n>1 与 PSERV-05 边界），方案 A 不扩大也不修复它，设计上明确此缺口 |

### 2.7 Property tests（proptest 已在 dev-deps：v1.11.0）

1. **拼接等价**：随机 token id 序列（含：已知特殊 id、vocab 内随机 id、混合长度）
   → `增量输出拼接 == try_decode(序列)`。生成器用词汇表内合法 id（防未知 id 路径）+
   专门特殊 id 注入。
2. **字节边界**：构造「同一 UTF-8 码点被拆分到相邻 token」的 token 对（手工从 Qwen2 词表
   找或合成字节序列）→ 断言不产生 U+FFFD 且拼接一致。
3. **特殊 token 过滤**：特殊 token 位于开头/中间/末尾/连续多个 → 输出无痕迹且与一次性一致。
4. **finish 尾段**：随机序列 finish 后拼接仍等于一次性的尾。
5. **空/单 token/全特殊**：边界空序列（finish 返回 None 语义）、单 token、全特殊序列。
6. **与现有契约测试对接**：tokenizer_real_diff / tiny_llm_text_e2e 的现有逐 token 对齐断言
   继续通过（3 并发分页 llama.cpp 对齐）。
7. 差分回归：对线上真实模型 tokenizer.json 跑一轮随机序列（固定 seed，样本数 ≥ 5000）。

### 2.8 性能与兼容性风险

- 性能：每 token 一次 O(pending_bytes) 解码 + O(bytes) 边界扫描；pending 通常 ≤ 4 字节
  （A1 路径），可忽略；HTTP 层每 token 一个 SSE event 的开销与 llama-server 同类（可接受，
  需在 PSERV-03 A/B 中观察）。
- 兼容性：不触碰 ABI（ffi.h/tiny_llm_ffi.rs 无变化）；不改 engine/server 接口；仅替换
  decoder 实现 + 新增单元/属性测试。`TokenizerTrait` 契约注释（拼接=一次性）已被实现满足。
- 风险①：CHAR_BYTES 表的移植与 tokenizers 内部表不一致 → 差分测试（对所有 vocab token
  单独字节还原，与 tokenizers 输出的 decode 对照）消除。
- 风险②：Qwen2 之外未来 tokenizer（如含 Fuse 链）→ A2 回退 + `supports_byte_model`
  能力检测，不接受支持的链直接返回可诊断错误（不回退静默错误输出）。

## 3. 方案 B：保留 buffered HF decoder，TTFT/TPOT/ITL 标 null

- 改动：**不改 tokenizer**。loadgen/文档层面把流式指标语义修正：
  - `TTFT` 改为「完整生成完成时间」（字段名/文档明示，或标 null）；
  - `TPOT`、`itl_ms` 恒 null（无 token 级时间戳）；
  - 报告只给成功率、端到端吞吐（tok/s 基于 usage 有效）、常驻显存、KV 利用。
- 等价性：无流式 → 自动满足（无增量输出）。
- 优点：改动最小（loadgen schema 注释/文档/labels），零实现风险，立刻可做 PSERV-03 的
  「吞吐/成功率」A/B。
- 缺点：TTFT/TPOT 这两个面试常问指标在本后端不可用；连续 batching 的调度收益只能以
  吞吐/存在性证明（弱证据）；断开检测仍滞后（finish 时刻）。
- 性能：无额外开销。兼容性：无风险。

## 4. 方案 C：改用真正支持增量语义的 tokenizer backend

- 选项分析：
  - tokenizers 0.19：**无官方 streaming decode API**（`Decoder` trait 为一次性列表输入，
    tokenizer/mod.rs:154-162；无可增量状态机）。排除作为"现成增量 API"。
  - tiktoken-rs：字节级 BPE，decode 也是列表式；有 `decode_with_offsets` 但无 streaming
    状态机；vocab 格式与 HuggingFace tokenizer.json 不同 → 需额外词表转换，且 Qwen2 的
    added tokens 语义不通用。排除。
  - llama.cpp ggml tokenizer：自带 streaming detokenizer（字节级状态机成熟参考），但引入
    C++/GGML 依赖到 Rust 仓，与「不扩 scope、不新增重依赖」冲突。排除（作为参考实现）。
  - **实质结论**：C 的务实形态 =「在 Rust 侧自建与 ByteLevel 语义一致的字节级状态机
    （独立于 Tokenizer::decode 路径，只用 vocab + CHAR_BYTES）」——这与方案 A1 的算法
    同构，区别在于 A1 复用 tokenizers 的 id_to_token/is_special_token 与 decoder 配置
    （单源），C 需要独立复制字节表与过滤逻辑（**双源漂移风险**，必须差分测试兜底）。
- 优点：不依赖 tokenizers 的 lossy 行为（可控性最高）；理论上最"干净"的增量语义。
- 缺点：实现量最大；与 tokenizers 的解码语义必须逐字节对齐（否则对特定 token 产生差异）；
  维护成本高。
- 风险：双源漂移、测试矩阵膨胀；对非字节链仍需 A2 类回退。

## 5. 方案对比与推荐

| 维度 | A（A1 精确 + A2 回退） | B（buffered + null 指标） | C（独立字节状态机） |
|------|------------------------|---------------------------|---------------------|
| 增量 SSE 逐 token | ✓ | ✗（现状） | ✓ |
| TTFT/TPOT/ITL 可用 | ✓ | ✗（null） | ✓ |
| 等价性保证 | 可证明（ByteLevel）+ property test | 平凡 | 需差分测试兜底 |
| 实现/改动面 | tokenizer.rs decoder 实现 + 测试；不动 ABI/engine/server | loadgen 文档/标签 | tokenizer.rs 新实现 + 字节表移植 + 测试 |
| 实现风险 | 中（字节表一致性） | 低 | 高（双源） |
| 取消检测延迟 | 每 token 即时 | finish 时刻 | 每 token 即时 |
| n>1 / stop / cancel 兼容 | ✓（§2.6，n>1 取消缺口为既有事实如实标注） | ✓（无变化） | ✓ |
| 面试叙事价值 | 高（真流式 + 正确性测试） | 低 | 中 |

**推荐：方案 A**（ByteLevel 精确路径 A1 为主 + 非字节链 A2 回退 + proptest；方案 B 作为
A 落地前的临时口径或 A 失败后的降级）。理由：等价性可证明、改动集中在 decoder 实现、
解锁 PSERV-03 全部指标；C 与 A1 同构但引入双源风险，不选。

## 6. 落地步骤（收到授权后）

1. 复现基线：跑 `cargo test` + 一次 loadgen closed（记录 chunks=1 证据，已验证存在 → 直接引用 PSERV-02 证据即可）
2. 实现 `ByteLevelIncrementalDecoder`（A1）+ `supports_byte_model()` 能力检测（A2 回退）
3. proptest 套件（§2.7 的 1-7）+ 差分回归（真实 tokenizer.json）
4. 验证矩阵：`cargo test`（含 tiny_llm_text_e2e 3 并发对齐）→ server + loadgen：chunks>1、
   usage 正确、取消即时回收、stop 命中无撤回、n>1 候选独立
5. 回归：PSERV-02 复算脚本对同一输入在新语义下重算（TTFT/TPOT 恢复为真实值）
6. 不改 ABI、不改 engine 调度、不顺手重构；失败路径保留为负结果

## 7. 文档证据

- 本文档；PSERV-02 F1 证据（runs/2026-08-28/PSERV-02/00_PSERV-02_summary.md）
- tokenizers 0.19.1 源码：decoder trait（tokenizer/mod.rs:154-162）、decode（:847-864）、
  ByteLevel decode_chain（pre_tokenizers/byte_level.rs:156-173）
- 本仓代码：tokenizer.rs:331-343（try_decode=decode(tokens,true)）、:370-395（BufferedDecoder）、
  engine.rs:374（stop 先于 push）、:440-500（finish/失败不 finish）、server.rs:720-732（断开→cancel）、
  :1280-1310（n>1 fan-in，无断开反向信号）
- 未修改任何源码；未提交、未 push