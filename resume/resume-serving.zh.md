# 【姓名待填】 · 简历

**求职意向**：AI Infra / 大模型推理 Serving 工程师
**联系方式**：手机【待填】｜邮箱【待填】｜微信【待填】｜现居地【待填】
**GitHub**：<https://github.com/open-infra-ai>（五个技术仓 + 组织导航仓，全部公开可复现）

> **一句话定位**：【真实年限待填】年后端/系统开发经验，独立构建 CUDA 内核 → 推理运行时 →
> Serving 控制面的可验证学习栈；真实 Qwen2.5-0.5B 模型已有 TPOT 优化链，
> Rust 控制面 3 并发正确性用例接入真实后端，全部数字带硬件与复现口径。

证据编号 E1–E30 对应组织 meta 仓的
[历史证据矩阵](https://github.com/open-infra-ai/open-infra-ai/blob/master/interview/EVIDENCE_MATRIX.md)；
当前测试数量与文档口径以各技术仓 current HEAD 为准。

---

## 工作经历

### 【公司名待填】｜【职位待填】｜【起止时间待填】
【职责概要待填：1-2 句你实际负责的系统或服务。】

**可迁移能力引导**（从过往经历中挑选量化成果填入，删掉不适用项）：

- **高并发服务**：【句式】负责/主导过 QPS【数字待填】的在线服务，完成【连接模型/线程模型/缓存】改造，P99 延迟【前→后待填】。
- **分布式系统**：【句式】参与过【存储/消息/微服务】体系，负责【一致性/重试/超时/容灾】机制，支撑【规模待填】。
- **资源调度**：【句式】管理过【任务队列/资源池/配额】分配策略，处理【排队/优先级/抢占】场景，资源利用率【数字待填】。
- **性能优化闭环**：【句式】完整走通 profiling → 定位瓶颈 → 重构 → 复测 流程，【指标】提升【倍数待填】。

（*有相关经验请用以上句式替换为具体成果并量化；与目标岗位无关的经历淡化处理。*）

---

## 项目经历（开源作品集，github.com/open-infra-ai）

### paged-infer —— Serving 主项目（Rust）

PagedAttention 分页 KV + continuous batching + OpenAI 兼容 API；经 C ABI 接 tiny-llm 真实 C++ 后端，调度器覆盖状态机 / 三层准入 / 内存水位线 + decode reserve / HOL / 优先级。

1. C ABI v2 九整型布局，Rust `sizeof==36` 守卫防漂移，跨语言边界靠布局守卫锁死。→ E19
2. 属性测试锁定 `used+free==total`：取消与失败路径必须归还块，调度资源守恒硬化成不变量。→ E23
3. OpenAI 兼容 API + SSE 流式 + `paged_*` Prometheus metrics：当前 server 集成测试 38 项，
   默认套件 232 项。→ E25
4. 3 并发分页请求与 llama.cpp greedy 对齐（请求 1 全序列一致）；W8A16 vs Q4_K_M 量化分歧如实记录，不伪造全序列一致。→ E21

### tiny-llm —— 推理加速旗舰（C++17 + CUDA）

CUDA 原生推理引擎：GGUF 解析 → W8A16 重量化 → 分页 KV → token 流式；导出 C ABI v2 供上层控制面调用。

1. 一条命令从 GGUF 跑通真实 Qwen2.5-0.5B Instruct 生成。→ E10
2. clean commit `565da79` 的 CUDA Graph 五组配对 A/B 中，TPOT
   8.322→5.225 ms/token（-37.2%），decode 吞吐 120.168→191.384 tok/s（+59.3%）；
   10 个进程原始 JSONL与完整边界
   [可复现](https://github.com/open-infra-ai/tiny-llm/blob/master/docs/performance/results/2026-08-23-cuda-graphs-ab.md)。→ E15/E16
3. Graphs on/off greedy 输出逐 token 一致；TTFT 配对波动不作改善声明，相对 llama.cpp
   的历史数据因 W8A16 vs Q4_K_M 非同量化只作外部参考。→ E16
4. tokenizer 与 HuggingFace 逐 id 差分对齐：30 例共 417 token。→ E11

### cuda-foundations / triton-fused-ops / cuflash-attn —— 基础层（合并为一行）

CUDA SGEMM naive→WMMA 阶梯 0.58→1.09 TFLOPS，负优化留表不隐藏（E1）；Triton 三算子独立 reference 差分 + `torch.ops` 注册（E3/E5）；FlashAttention 前后向多精度 + FlashDecoding，B×H>65535 grid 越界修复并回归（E7/E9）；causal 跳过实测 ±2% 低于噪声，负结果如实归档（E8）。

### 全局（收尾）

四层五仓可验证学习链：CUDA→Triton→FlashAttention→runtime→serving，每仓独立差分、
不变量或契约测试；面试主线聚焦 tiny-llm，不把五仓平铺成五个“旗舰”。→ E30

---

## 技能清单

- **语言与计算**：C++17（推理运行时）、Rust（控制面/调度器/服务端）、CUDA C++（内核优化 + WMMA）、Python（Triton / torch.library / 差分测试）。
- **推理系统**：GGUF 解析与反量化、W8A16 量化推理、PagedAttention 分页 KV、CUDA Graphs、continuous batching、内存水位线与 decode reserve。
- **调度与工程**：序列状态机、HOL 缓解、优先级、集中式 BlockPool 分配、C ABI / FFI 跨语言集成、HTTP/SSE + OpenAI 兼容契约、Prometheus metrics。
- **测试方法论**：GPU vs CPU 参考差分、属性测试（资源不变量）、FFI 布局守卫、契约测试；量化分歧与负结果如实记录，不报喜不报忧式伪造。

---

**注**：本页性能数字来自 RTX 3060 Laptop 6GB、clean commit `565da79` 的 schema v2
CUDA Graph A/B；2026-08-23 当前验证为 tiny-llm 193 项、paged-infer 默认 232 项测试通过。
测试数量不是性能结论；“非同量化”、“CPU 参考后端”和负结果等限制必须保留。
【】处未填写前不可投递。
