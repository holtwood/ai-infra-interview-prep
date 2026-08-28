# TLLM-04 长上下文曲线与 OOM 边界（2026-08-28）

## 基线（binding）

- tiny-llm@f9d4b99（Release build，-DCMAKE_CUDA_ARCHITECTURES=86），CUDA Graph decode ON
- RTX 3060 Laptop 6GB（sm_86），nvcc 12.0.140，driver 610.57.01/CUDA UMD 13.3
- 模型 qwen2.5-0.5b-instruct-q4_k_m.gguf（sha256 74a4da8c…）
- 固定输出：max_tokens=32（128-4096 点 warmup=1 iters=3）或 16（8192 点 warmup=0 iters=1，因 prefill 耗时）
- prompt 为固定英文重复句；实际 token 以 bench 报告为准

## 曲线（05_curve.csv，原始 JSON 见 bench_len_*.json）

| target | 实际 prompt tokens | TTFT mean (ms) | TPOT mean (ms) | decode tok/s | 常驻显存差值 (MB) | 结果 |
|-------:|-------------------:|---------------:|---------------:|-------------:|------------------:|:----:|
| 128 | 220 | 308.61 | 6.251 | 159.98 | 4088.16 | ok |
| 512 | 884 | 1178.5 | 9.139 | 109.42 | 3368 | ok |
| 2048 | 3535 | 6144.3 | 20.017 | 49.96 | 3368 | ok |
| 4096 | 7069 | 20700.3 | 45.458 | 22.00 | 4117.67 | ok |
| 8192 | 14138 | 58287.5 | 69.202 | 14.45 | 3368 | ok |
| 16384 | – | – | – | – | – | **E2BIG**：prompt 147KB 超过 Linux MAX_ARG_STRLEN 128KB，exec 失败（exit 127） |

观察：prefill（TTFT）随长度超线性增长（3535→14138 tokens：6.1s→58.3s，约 9.5×），decode TPOT 随长度增长
（6.3→69.2ms，KV 访问不再 cache 友好，本实现无 FlashDecoding——预期行为）；常驻显存差值稳定在
3368–4118MB 量级（首点 4088 为进程冷启动含 CUDA context 初始化）。**全部为 cudaMemGetInfo 起止差值口径，非峰值。**

## 结果计数（校正口径）

- **5 success + 2 failure**（失败原始 JSON/日志均保留，未删除）：
  - failure 1：8192 点首次运行（warmup=1, iters=3, timeout 300s）超时 rc=124 → 降为 iters=1 后成功
  - failure 2：16384 点命令行参数超限 E2BIG（exit 127），bench/demo 均无法接收 128KB+ prompt（无文件输入选项）——工具/接口限制
- **尚未达到真实 OOM 边界**：0.5B 模型 KV 非显存瓶颈，扫描范围内无 OOM 点可记录；"OOM 边界"未实测，不宣称已达

## 失败点（原始证据保留）

1. 8192 点首次运行（warmup=1, iters=3, timeout 300s）超时 rc=124 → 降为 iters=1 后成功（bench_len_8192.stderr / 命令记录）
2. 16384 点：命令行参数超限 E2BIG（exit 127），bench/demo 均无法接收 128KB+ prompt（无文件输入选项）——记录为工具/接口限制（bench_len_16384_fail.log）

## 正确性抽样

3535-token prompt 经 demo CLI 生成 24 tokens：无崩溃/OOM，prefill 9792ms、decode 468ms、tps 51.24；
输出为重复填充 prompt 下 Q4 0.5B 的噪声文本（与 TLLM-01 一致性基线无关，仅验证长上下文路径可运行）。

## 限制

- 未跑 16K+（参数接口限制）；OOM 边界未达（KV 非瓶颈，0.5B 模型），故无 OOM 点可记录
- 数字为单机观测，非正式 benchmark；TPOT 含 CUDA Graph，随长度上升属预期
- 未 push；复算：任一曲线点可由 bench_len_*.json + 命令复现

## 证据

runs/2026-08-28/TLLM-04/{bench_len_{128,512,2048,4096,8192}.json, prompts.json, 04_correctness_sampling.log, 05_curve.csv, 00 本文件}