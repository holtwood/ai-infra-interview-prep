# CUF-02 当前版本 benchmark/profiler 包 - 本地 correctness 部分（2026-08-28）

## 绑定

- cuflash@d53a5301bf（v0.6.0 tag commit，master clean 除 P0-03 的 flash-decoding.md 修改）
- RTX 3060 Laptop 6GB（sm_86），nvcc 12.0.140，driver 610.57.01/CUDA UMD 13.3
- 构建：cmake --preset release + build（exit 0）；build/release/cuflash_bench、cuflash_tests

## 1. correctness（本地实测）

- `ctest --output-on-failure`（build/release）：**70 passed + 1 skipped，共 71 项**（33.61s；
  ctest 汇总行显示 "100% tests passed, 0 failed" 因为 skipped 不计失败）
  - 覆盖：FP32/FP16/BF16 前向（test_forward/test_dtype）、反向（test_backward）、FlashDecoding
    （test_flash_decoding）、causal mask、online softmax、数值稳定性、stress/edge cases、
    matmul/tile_io、error handling、api_smoke、package_smoke
  - 1 Skipped：cuflash_pytorch_comparison（系统 python3 无 torch）
- PyTorch SDPA 对照（triton-b4 env：torch 2.5.1+cu121）：**9 passed, 0 failed**——FP16/BF16
  前向/反向 equivalence（dQ/dK/dV max diff 1e-3 量级）+ 4 种 shape 全过

## 2. 本机 benchmark 快照（非正式包，仅本机可复现）

- `cuflash_bench` 代表形状（1024/64 前向 FP32/FP16/BF16 + 反向、4096/128 FP16），5 次重复，
  原始 JSON：bench_local.json
- 关键观测（median，FP16 1024/64）：前向 ~2.0ms、反向 ~45ms；4096/128 FP16 前向 ~96ms
  （本机 6GB 卡 + debug-free Release 的参考级实现；不与任何正式数字合并）
- 按 benchmarks.md 纪律：本快照绑定 d53a530 + 本机硬件 + 5 reps，原始 JSON 已留档，
  不冒充跨硬件正式结果

## 3. 云部分（blocked）

- 正式结果包（多架构矩阵、nsys/ncu profiler、validation.log、metadata.json）需云 GPU
  （ALLOW_CLOUD_RESOURCE_CHANGES=false、ALLOW_PAID_ACTIONS=false）
- 本地 Nsight 尝试不适用（本机 nvcc 12.0 无 ncu 采样授权验证；按纪律不做 profiler 结论）
- 恢复条件：用户授权启动云 GPU（按 CLOUD_GPU_PLAYBOOK）后，先 correctness canary，
  再 nsys → 热点 ncu；实例停机

## 证据

runs/2026-08-28/CUF-02/{bench_local.json, 00 本文件}；ctest 输出见构建目录
（cuflash-attn/build/release/Testing/）

## 限制

- 性能数字仅本机 6GB 卡观测；正式包（含更慢/OOM/不支持形状矩阵）需云
- 未 push；本地结果未写入仓库结果体系（按 TASKS 规则：正式结果进目标仓 schema，云包完成后一并归档）