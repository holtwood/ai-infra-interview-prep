# TLLM-01 固化 tiny-llm 当前正确性基线（2026-08-28）

## 基线（binding）

- repo：tiny-llm@f9d4b99fd643a1d863a395a2a2ab5ae06e90e328（master，工作树含 P0-03/P0-04 未提交改动）
- 硬件：NVIDIA GeForce RTX 3060 Laptop 6GB（6144MiB，sm_86），driver 610.57.01 / CUDA UMD 13.3
- 工具链：nvcc 12.0.140（本地，非 CI 11.8）、gcc 13.3.0、cmake 3.28.3、clang-format 18.1.8
- 构建：`cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -DCMAKE_CUDA_ARCHITECTURES=86`；`cmake --build build -j$(nproc)`（exit 0）
- 模型：`models/qwen2.5-0.5b-instruct-q4_k_m.gguf`（491400032 B，sha256 74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db），tokenizer.json 7031645 B

## correctness 结果

```
TLLM_GGUF_TEST_MODEL=... PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
ctest --test-dir build --output-on-failure --timeout 300
=> 192 passed + 1 skipped（SecondModelTest.LoadsAndGeneratesWithDistinctGQA，
   因 TLLM_GGUF_TEST_MODEL_2 未设置，属 TLLM-02 范围；共 193 项）
   （第一轮 246.14s，第二轮 146.90s；ctest 汇总行显示 "100% tests passed, 0 failed" 是因为 skipped 不计失败）
```
覆盖：CPU（tokenizer/types/parser/quantization/kv_cache/execution-common）+ GPU（kernels/w8a16/transformer/integration/ffi Paged KV/GGUF real/tokenizer real 等 19 个 CUDA 测试）+ C ABI（FFITest.LoadAllocateStepFree/InvalidArgs/BatchedLogprobs/PagedKVStrategyMatchesContiguous）。

## schema v2 A/B（validator 重算）

- `tiny_llm_bench --json`（graph on）→ 02_bench_graph_on.json：cuda_graphs{enabled:true,captured:true}，tpot mean 4.959ms，decode 201.646 tok/s，resident_delta 3368MB
- `tiny_llm_bench --no-graphs --json`（graph off）→ 03_bench_graph_off.json：cuda_graphs{enabled:false,captured:false}，tpot mean 8.057ms，decode 124.114 tok/s，resident_delta 3364MB
- validator：`python3 validate_bench_json.py <json> <expected>` 两文件均 exit 0
- 手工复算：decode_tok_per_s = 1000/tpot_mean，两文件 delta 0.0%
- 注：resident_memory_delta_mb 为 cudaMemGetInfo 起止差，按纪律只能称“常驻显存差值”，不称峰值

## 限制

- 本机 nvcc 12.0 vs CI 11.8：构建产物 arch 只针对 sm_86；正确性结论限于本机范围
- 性能数字（tpot/tok/s）仅作 A/B 正确性佐证，非正式 benchmark（口径、warmup 简化）
- 未 push、未跑远端 CI
- 第二模型 skip（TLLM-02）

## 证据文件（runs/2026-08-28/TLLM-01/）

- 01_ctest_full.log（全量 193 测试原始输出，两轮各一次）
- 02_bench_graph_on.json / 03_bench_graph_off.json（schema v2 原始 JSON）
- 02/03_bench_*.stderr（off 时 TLLM_CUDA_GRAPHS=0 诊断）
- 04_model_sha256.txt
- validate_bench_json.py