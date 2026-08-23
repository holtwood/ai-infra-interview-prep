# 12 周路线图（ROADMAP）

**执行周期：2026-08-24（周一）～ 2026-11-15（周日）**，从执行日后的第一个完整周开始。

- 目标岗位与边界：[TARGET_ROLES.md](TARGET_ROLES.md)
- 时间预算：[TOPIC_WEIGHTS.md](TOPIC_WEIGHTS.md)（默认 24h/周，另附 12h/18h 缩放档）
- 项目选择：[PROJECT_STRATEGY.md](PROJECT_STRATEGY.md)（已定，无"待定"）
- 仓库导航与深读：[github-repos-hub](https://github.com/holtwood/github-repos-hub)
- 逐周文件：[weekly/](weekly/)，进度：[progress-tracker.md](progress-tracker.md)

| 周 | 日期 | 核心主题 | 必须交付 |
|----|------|---------|---------|
| 1 | 08-24～08-30 | 基线评估、CUDA 模型、环境与性能工具 | 能力基线自评、CUDA 问答、可复现基准（cuda-foundations） |
| 2 | 08-31～09-06 | GEMM、访存、Tiling、共享内存、WMMA | 优化阶梯讲解 + Nsight Compute 性能报告 |
| 3 | 09-07～09-13 | Attention、Online Softmax、FlashAttention | 手推公式、cuflash-attn 代码定位、正确性实验复述 |
| 4 | 09-14～09-20 | Triton、PyTorch 自定义算子 | 至少一个 kernel 的 CUDA/Triton 对照报告 |
| 5 | 09-21～09-27 | Transformer 推理、量化、模型加载 | tiny-llm 主调用链讲解 + 白板图 |
| 6 | 09-28～10-04 | KV Cache、Decode、CUDA Graph、性能指标 | TTFT/TPOT/吞吐/显存指标报告 + CUDA Graph 对照实验 |
| 7 | 10-05～10-11 | Paged KV、Continuous Batching、调度 | paged-infer 状态机与不变量讲解 |
| 8 | 10-12～10-18 | HTTP/SSE、压测、可观测性、Linux 调优 | paged-infer 压测报告与故障分析 |
| 9 | 10-19～10-25 | NCCL、并行策略、通信/计算重叠 | 理论学习与单机模拟实验；**不得伪造多 GPU 数据** |
| 10 | 10-26～11-01 | 项目证据包、简历项目、GitHub 展示 | 两个主项目 STAR 条目 + Demo 脚本 |
| 11 | 11-02～11-08 | CUDA/C++/系统设计模拟面试 | 至少两次有评分的完整模拟 |
| 12 | 11-09～11-15 | 查漏补缺、投递、复盘 | 最终简历、项目清单、投递与复盘机制 |

## 每周文件统一结构

weekly/week-NN.md 必须包含：

1. 本周目标
2. 先修知识
3. 时间预算（24h 基准 + 12h/18h 缩放说明）
4. 阅读范围（具体到仓库目录/文件）
5. 动手实验
6. 可验证交付物
7. 面试问题（加入 [INTERVIEW_MATRIX.md](INTERVIEW_MATRIX.md)）
8. 退出条件
9. 未完成任务如何降级或顺延

## 阅读量纪律

- P2 大仓（vllm、sglang、TensorRT-LLM、triton、flashinfer、flash-attention、LightLLM）
  一律目标导向阅读，每仓只产出"五个一"（架构图/调用链/数据结构/实验/面试题）。
- cuda-samples、tvm 等不做全仓通读（详见 github-repos-hub 的 catalog/ai-infra.md）。
