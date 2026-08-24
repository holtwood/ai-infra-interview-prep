# 【姓名待填】 · LLM Inference Performance / GPU Kernel 工程师

**联系方式**：手机【待填】｜邮箱【待填】｜现居地【待填】
**GitHub**：[holtwood](https://github.com/holtwood)｜[open-infra-ai](https://github.com/open-infra-ai)

> 【真实年限待填】年 C++ / 后端 / 系统工程经验，转向 LLM 推理性能方向。具备从 CUDA
> kernel、真实模型 decode 到可复验性能实验的工程实践；所有项目数字均标明硬件、输入、
> commit 与适用边界。

## 工作经历

### 【公司】｜【岗位】｜【起止时间】

- 【填写真实的高并发、实时系统、性能优化、资源调度或线上稳定性成果；每条写清规模、个人动作和结果。】
- 【无法证明的数字删除；不要把学习项目改写成商业生产成果。】

## 开源项目

### [tiny-llm](https://github.com/open-infra-ai/tiny-llm)｜CUDA C++ GGUF 推理运行时

- 实现 GGUF 权重加载、W8A16 重量化、KV Cache、tokenizer 和逐 token decode；通过 C ABI
  向 Serving 控制面暴露真实后端，而不把调度逻辑混入运行时。
- 在 RTX 3060 Laptop 6GB、Qwen2.5-0.5B-Instruct、64-token greedy decode 上完成
  clean-commit CUDA Graph **decode A/B**：TPOT 8.322→5.225 ms/token（-37.2%），decode
  吞吐 120.168→191.384 tok/s（+59.3%）。五组交错配对、原始 JSONL、模型 SHA-256 与
  限制均可[复验](https://github.com/open-infra-ai/tiny-llm/blob/master/docs/performance/results/2026-08-23-cuda-graphs-ab.md)；TTFT 未作改善声明。

### [cuflash-attn](https://github.com/open-infra-ai/cuflash-attn)｜FlashAttention / FlashDecoding CUDA 专项

- 实现 FP32/FP16/BF16 FlashAttention 前后向、FP16/BF16 WMMA 前向和 Split-KV FlashDecoding；
  用 CPU/PyTorch 参考覆盖 causal、非整除形状与多精度数值误差。
- 将 `grid.y = B × H` 展平，修复大批量头数下的 launch 越界；因果边界块跳过实验收益低于噪声时保留负结果，不包装为性能优化。跨 GPU 历史表格未保留原始产物，不作为个人性能数字。

## 技能

- **CUDA/性能**：CUDA C++、Tensor Core / WMMA、online softmax、CUDA Graph、CUDA Event 基准、数值差分与性能统计。
- **推理运行时**：GGUF、W8A16、KV Cache、decode、tokenizer、C ABI / FFI。
- **工程**：C++17、Rust、Python/Triton、CMake、CI、Sanitizer、属性测试。

**投递前检查**：填写真实工作经历、联系方式和教育背景；CUDA Graph 数字只能表述为固定环境下的
decode A/B，不得扩写为整体推理或生产性能；Nsight 仅在形成正式 profiler 报告后再写为技能证据。
