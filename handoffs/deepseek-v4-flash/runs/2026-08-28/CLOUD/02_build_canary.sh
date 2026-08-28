#!/usr/bin/env bash
# 云部署包 - 02 云端构建与 canary（开机后）
# 目标实例：Runpod L40S 48GB（sm_89），Ubuntu 22.04 / CUDA 12.x 容器
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "== 环境记录（写入 metadata）=="
mkdir -p /workspace/results
{
  nvidia-smi
  echo "---"
  nvcc --version 2>/dev/null | tail -2 || echo "nvcc missing"
  echo "---"
  nproc; free -g | head -2
  echo "---"
  cat /workspace/VERSIONS.txt
} > /workspace/results/00_metadata.txt
cat /workspace/results/00_metadata.txt

echo "== 构建依赖 =="
apt-get update -qq >/dev/null 2>&1 || true
which cmake g++ ninja rustc cargo >/dev/null 2>&1 || apt-get install -y -qq cmake g++ ninja-build rustc cargo >/dev/null 2>&1
cmake --version | head -1
rustc --version 2>/dev/null || echo "no rust"

echo "== 构建 cuflash（sm_89）=="
cd /workspace/src/cuflash
cmake --preset release -DCMAKE_CUDA_ARCHITECTURES="89" > /workspace/results/cuf_configure.log 2>&1
cmake --build --preset release -j"$(nproc)" >> /workspace/results/cuf_configure.log 2>&1
ls -la build/release/cuflash_tests build/release/cuflash_bench

echo "== 构建 tiny-llm（sm_89）=="
cd /workspace/src/tiny-llm
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -DCMAKE_CUDA_ARCHITECTURES="89" > /workspace/results/tllm_configure.log 2>&1
cmake --build build -j"$(nproc)" >> /workspace/results/tllm_configure.log 2>&1
ls -la build/tiny_llm_tests build/tiny_llm_bench

echo "== canary 1: cuflash correctness =="
cd /workspace/src/cuflash/build/release
ctest --output-on-failure --timeout 300 > /workspace/results/cuf_canary.log 2>&1 || {
  echo '{"overall":"FAILURE","stage":"canary","step":"cuflash ctest","detail":"见 cuf_canary.log"}' > /workspace/results/STATUS.json
  echo "CUFLASH CANARY FAILED"; exit 1; }
tail -3 /workspace/results/cuf_canary.log

echo "== canary 2: tiny-llm correctness =="
cd /workspace/src/tiny-llm
TLLM_GGUF_TEST_MODEL=/workspace/models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  ctest --test-dir build --output-on-failure --timeout 300 > /workspace/results/tllm_canary.log 2>&1 || {
  echo '{"overall":"FAILURE","stage":"canary","step":"tiny-llm ctest","detail":"见 tllm_canary.log"}' > /workspace/results/STATUS.json
  echo "TINY-LLM CANARY FAILED"; exit 1; }
tail -3 /workspace/results/tllm_canary.log

echo "== canary 通过 =="
touch /workspace/results/CANARY_PASSED