# 【姓名待填】 · 简历

**求职意向**：LLM Inference Performance / GPU Kernel 工程师  
**联系方式**：手机【待填】｜邮箱【待填】｜微信【待填】｜现居地【待填】  
**GitHub**：<https://github.com/open-infra-ai>（五个技术仓 + 组织导航仓）

> **一句话定位**：【真实年限待填】年后端/系统开发经验，独立完成从 CUDA/Triton kernel
> 到真实模型 decode 的可复现学习栈；在 RTX 3060 Laptop 6GB 上完成 tiny-llm 的
> M==1 GEMM 与 CUDA Graph 优化，并用差分测试、消融与完整口径约束性能结论。

证据编号对应组织 meta 仓的
[历史证据矩阵](https://github.com/open-infra-ai/open-infra-ai/blob/master/interview/EVIDENCE_MATRIX.md)；
当前事实以各技术仓 current HEAD 为准。

---

## 工作经历

### 【公司名待填】｜【职位待填】｜【起止时间待填】

【只填写真实职责。优先选择性能定位、高并发、资源调度、C++/系统工程或线上稳定性成果，
每条写清规模、个人动作和结果；无法证明的数字删除。】

---

## 项目经历

### tiny-llm —— CUDA 原生 LLM 推理运行时（旗舰，C++17 + CUDA）

从 GGUF 权重加载、W8A16 重量化、tokenizer、KV Cache 到逐 token decode 的真实模型链路，
并导出 C ABI 供 Serving 控制面使用。

1. 为 decode 的 M==1 GEMM 增加转置权重快路径，lm_head microbenchmark
   10.0002→0.9794 ms；该 microbenchmark 与端到端指标分开报告，不把局部加速比冒充整体收益。→ E15
2. 在 clean commit `565da79` 上完成 CUDA Graph 五组交错配对 A/B：TPOT
   8.322→5.225 ms/token（-37.2%），decode 吞吐 120.168→191.384 tok/s（+59.3%）；
   10 个进程原始 JSONL、模型哈希和限制
   [可复现](https://github.com/open-infra-ai/tiny-llm/blob/master/docs/performance/results/2026-08-23-cuda-graphs-ab.md)，
   on/off greedy 输出逐 token 一致；TTFT 波动不作改善声明。→ E16
3. 真实 Qwen2.5-0.5B-Instruct 一条命令生成；tokenizer 与 HuggingFace 30 例、417 token
   逐 id 对齐；2026-08-23 当前 193 项测试通过。→ E10/E11

> 外部 llama.cpp 参考为 Q4_K_M，而本实现执行 W8A16，1.65× 差距不是同量化公平基准，
> 只用于定位剩余优化空间。

### cuflash-attn —— FlashAttention / FlashDecoding 专项（CUDA C++）

1. 实现 FlashAttention 前后向 FP32/FP16/BF16，FP16/BF16 前向使用 WMMA；用 CPU/PyTorch
   参考覆盖 causal、非整除形状和多精度误差。→ E7
2. 将 `grid.y=B×H` 展平，修复 B×H>65535 的 launch 越界并加入回归；当前 RTX 3060
   Laptop 81/81 项测试通过。→ E7
3. 实现 decode 用 Split-KV FlashDecoding 与 CPU reference；causal 边界块跳过实测仅 ±2%
   噪声范围，保留负结果而不包装成加速。→ E8/E9

### cuda-foundations + triton-fused-ops —— 基础与横向对照

- CUDA SGEMM 从 naive 0.58 推进到 WMMA 1.09 TFLOPS，保留 bank-conflict-free 版本降至
  0.66 TFLOPS 的负优化，解释 occupancy、寄存器与访存权衡。→ E1
- Triton 实现 SGEMM、RMSNorm+RoPE、SwiGLU 与 FlashAttention，对独立 NumPy/PyTorch
  reference 差分并注册 `torch.ops.triton_ops.*`；RTX 3060 Laptop 123/123 项测试通过。→ E3/E5

### paged-infer —— Serving/调度扩展（Rust，简述）

Paged KV + continuous batching 控制面经 C ABI 接入 tiny-llm；属性测试锁定资源守恒，
3 并发 e2e 用于证明跨语言与生命周期正确性，不把它表述为生产 QPS。→ E19/E21/E23

---

## 技能

- **CUDA/性能**：CUDA C++、Tensor Core/WMMA、online softmax、Nsight Systems/Compute、
  CUDA Graph、差分测试与 benchmark 统计。
- **推理运行时**：GGUF、W8A16、KV Cache、decode、tokenizer、C ABI/FFI。
- **语言/工程**：C++17/23、Python/Triton、Rust；CMake、CI、Sanitizer、属性测试。

**注**：性能数字来自 RTX 3060 Laptop 6GB、clean commit `565da79` 的 schema v2
CUDA Graph A/B，不等价于整体推理或生产成熟度；历史 schema v1 不与之混算。
【】处必须由本人填写真实信息，未填写前不可投递。
