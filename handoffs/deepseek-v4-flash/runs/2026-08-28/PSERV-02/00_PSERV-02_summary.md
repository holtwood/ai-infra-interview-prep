# PSERV-02 审计 loadgen 与 token coverage（2026-08-28）

## 审计范围

paged-infer（crate paged-serving 0.2.0）@080f26f：src/bin/loadgen.rs（1027 行）全量源码审计 +
单元测试 + 端到端实测 + 独立复算。

## 审计结论（源码逐项）

| 项 | 结论 |
|----|------|
| 计时点 | TTFT = 请求发送前（Instant::now 在 POST 前）→ 首个非空 SSE 文本 chunk（loadgen.rs:277,426-428），涵盖连接+排队+prefill ✓ |
| 失败分类 | timeout / connection / http_429 / http_4xx / http_5xx / stream_error / protocol_error / no_done（:291-424）；收到部分 chunk 但无 [DONE] 判失败（成功率不掺水）✓ |
| token 来源 | 优先 usage.completion_tokens（"usage"），否则 tokenizer.encode(output_text)（"tokenizer_text"），否则 None（:434-441）；source_counts 汇总 ✓ |
| warmup 排除 | warmup 阶段（closed：跑满 warmup_secs 丢弃；poisson：warmup 流量丢弃，:750-859）结果不写入 records ✓ |
| TPOT | (duration−ttft)/(tokens−1)，tokens>1 且 ttft 存在（:507-517）✓ |
| tok/s 门控 | total_tokens/wall_secs，**仅当 known==ok（100% coverage），否则 None**（:548-552）✓ 符合纪律 |
| coverage | known（有 completion_tokens 的 ok 请求）/ok（:543-547）；**Some(0) 零 token 也算 known**（usage 明确给 0，设计语义） |
| 分位数 | nearest-rank：idx=round(p/100×(n−1))（Rust round = half away from zero；:478-485）✓ |
| itl_ms | 恒为 None，注释明示"标准 ITL 需要 token 级时间戳；普通 OpenAI SSE 不提供"✓ 诚实 |
| schema | schema_version=1；summary.json 含 config/wall/requests/ttft/chunk-latency/itl/tpot/completion_tokens/throughput/errors ✓ |
| 单元测试 | 4 个单测（SSE UTF-8 边界/CRLF/多 data 行、coverage 门控、summary 路径），cargo test --bin loadgen 全过 ✓ |

## 核心发现 F1：HF tokenizer 下 SSE 非真正逐 token 流式（重大口径问题）

- **根因**：`HuggingFaceTokenizer` decoder 的 `push()` 只缓冲 token 并返回 `Ok(None)`
  （tokenizer.rs:382-385），`finish()` 才一次性 decode 全部文本（:388-395）。server 的
  `step_events()` 因此每步不产生 chunk（engine.rs:389-392 只在非空文本时 push），请求完成时
  `collect_completed_requests` 把整段文本作为单个 tail_chunk 推送（engine.rs:483-486）。
- **实测证据**（端到端 6 请求 closed 模式）：per_request.jsonl 每条 `chunks=1`、
  `ttft_ms≈duration_ms`（差 ~0.05ms）、TPOT≈0.002ms；inter_chunk_latency 0 样本。
- **后果**：在这种模式下 loadgen 计到的"TTFT"实际是**整段生成完成时间**（首 chunk=唯一 chunk），
  TPOT 无意义（≈0）。usage 与 completion_tokens 仍真实（coverage 100%、tok/s 有效）。
- **loadgen 自身无 bug**（如实记录观察到的 chunk），但 **PSERV-03 的 TTFT/TPOT A/B 不能基于
  当前 server SSE 语义**。
- **修复路径（建议，属代码改动）**：把 HF decoder 改为真增量解码（按 UTF-8 安全边界分段输出，
  如 detokenizer 策略），使每步产生文本 chunk。需用户确认新增改动（PSERV-02 只审计不改功能）。

## 验证记录

1. `cargo test --bin loadgen`：4/4 passed（exit 0）
2. 端到端：server（tiny-llm 后端）+ loadgen closed 2 并发 × 6 请求：6/6 成功、coverage 100%、
   summary.json/per_request.jsonl schema 正确
3. 独立复算（recompute_aggregation.py，与 loadgen 算法同构）：已知样本 11 项断言全过——
   混合样本（成功/失败/缺 token/零 token）的 TTFT p50/TTPOT p50p95/coverage 75%/tok/s=None 门控、
   full coverage→11.2 tok/s、零 token→coverage 100% 且 tok/s=0.0（合法值）、TPOT 0 样本
4. 交叉验证：summary.json 的 tok/s=5.31864794976901 与独立复算**精确相等**（最强一致性证据）；
   ttft p50 差异 ~0.2μs（浮点排序细节，不计）

## 证据（runs/2026-08-28/PSERV-02/）

- dataset_smoke.jsonl、per_request.jsonl、summary.json、server.log（端到端原始产物）
- recompute_aggregation.py（11/11 PASS）
- 本汇总

## 限制

- 未修改任何源码（审计任务）；HF decoder 增量解码修复待用户授权
- 端到端数字（TTFT 12s、5.3 tok/s）为单机 debug build + 6GB 卡 + 并发 2 的观测，不代表正式结论
- 未 push、未跑远端 CI