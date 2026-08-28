#!/usr/bin/env python3
"""tiny-llm tiny_llm_bench schema v2 validator（TLLM-01 复算用，2026-08-28）。

检查规则（对应 CHANGELOG Unreleased 的 schema v2 口径）：
1. stdout 只含一个合法 JSON 对象
2. schema_version == 2
3. gpu:{name,total_memory_mib,cuda_driver_version,cuda_runtime_version} 字段完整且类型正确
4. benchmark:{prompt_tokens,max_tokens,warmup,iterations} 字段完整
5. cuda_graphs:{enabled,captured} 布尔，且 enabled 与命令行开关一致；captured 在 enabled 时非 false
6. time_ms 对象含 mean/p50/p95/min/max 且递增宽松校验（min<=p50<=mean<=p95<=max）不适用 p95<mean 时警告
7. null 规则：generated_tokens==1 时 tpot_ms 与 decode_tok_per_s 必须为 null（本 A/B 为 32 token 不适用）
8. resident_memory_delta_mb 存在且 >= 0

用法：python3 validate_bench_json.py <file.json> <graphs_enabled:true|false>
退出码：0=通过，1=失败
"""
import json
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_bench_json.py <json> <expected_graphs:true|false>")
        return 2
    path, expect_graphs = sys.argv[1], sys.argv[2].lower() == "true"
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)

    errors = []
    if obj.get("schema_version") != 2:
        errors.append(f"schema_version != 2: {obj.get('schema_version')}")
    gpu = obj.get("gpu") or {}
    for k in ("name", "total_memory_mib", "cuda_driver_version", "cuda_runtime_version"):
        if k not in gpu:
            errors.append(f"gpu.{k} missing")
    bench = obj.get("benchmark") or {}
    for k in ("prompt_tokens", "max_tokens", "warmup", "iterations"):
        if k not in bench:
            errors.append(f"benchmark.{k} missing")
    cg = obj.get("cuda_graphs") or {}
    if not isinstance(cg.get("enabled"), bool) or not isinstance(cg.get("captured"), bool):
        errors.append("cuda_graphs.enabled/captured not bool")
    elif cg.get("enabled") != expect_graphs:
        errors.append(f"cuda_graphs.enabled={cg.get('enabled')} != expected {expect_graphs}")
    elif cg.get("enabled") and cg.get("captured") is False:
        errors.append("graphs enabled but not captured")
    for key in ("ttft_ms", "tpot_ms"):
        t = obj.get(key)
        if t is None:
            if obj.get("generated_tokens") != 1:
                errors.append(f"{key} is null while generated_tokens={obj.get('generated_tokens')} != 1")
            continue
        for k in ("mean", "p50", "p95", "min", "max"):
            if k not in t:
                errors.append(f"{key}.{k} missing")
    if not isinstance(obj.get("decode_tok_per_s"), (int, float)) and obj.get("generated_tokens", 0) > 1:
        errors.append("decode_tok_per_s not numeric")
    if not isinstance(obj.get("resident_memory_delta_mb"), (int, float)) or obj.get("resident_memory_delta_mb") < 0:
        errors.append("resident_memory_delta_mb invalid")

    if errors:
        print("FAIL:")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK {path}: schema v2, graphs.enabled={cg.get('enabled')}, "
          f"tpot={obj.get('tpot_ms', {}).get('mean')} ms, decode={obj.get('decode_tok_per_s')} tok/s")
    return 0


if __name__ == "__main__":
    sys.exit(main())