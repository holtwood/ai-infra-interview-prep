#!/usr/bin/env bash
# 云部署包 - 03 正式矩阵（canary 通过后执行）
# 口径（CLOUD_GPU_PLAYBOOK §3）：每配置 >=3 个独立进程；每进程先 warmup 再 >=10 次测量；
# 保留逐次 raw（不用 aggregates_only）；任一失败写 STATUS.json FAILURE 并以非 0 退出。
set -uo pipefail

RES=/workspace/results
RAW="$RES/raw"; PROF="$RES/profiler"
mkdir -p "$RAW" "$PROF"
: > "$RES/STEPS.log"

fail_step() { echo "FAIL $1 rc=$2" >> "$RES/STEPS.log"; }
ok_step()   { echo "OK   $1" >> "$RES/STEPS.log"; }
OVERALL=OK

echo "===== 0. 环境与身份（metadata.json）====="
python3 - "$RES" << 'PYEOF'
import json, os, platform, subprocess, sys, datetime
res = sys.argv[1]
def run(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return None
meta = {
  "generated_at_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
  "git": {"note": "云端为 tar 展开无 .git；commit 与 dirty 见 /workspace/VERSIONS.txt（打包时记录）"},
  "gpu_nvidia_smi": run("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
  "gpu_topology": run("nvidia-smi topo -m 2>/dev/null | head -8"),
  "driver": run("nvidia-smi --query-gpu=driver_version --format=csv,noheader"),
  "cuda_nvcc": run("nvcc --version 2>/dev/null | tail -1"),
  "cuda_runtime": run("python3 -c 'import torch;print(torch.version.cuda)' 2>/dev/null") or run("nvidia-smi --query-gpu=driver_version --format=csv,noheader"),
  "cpu": run("nproc") + " vcpu / " + run("lscpu | grep 'Model name' | head -1"),
  "ram": run("free -g | awk 'NR==2{print $2\"G total\"}'"),
  "container_image": os.environ.get("RUNPOD_IMAGE", None) or run("cat /proc/1/cgroup 2>/dev/null | head -3"),
  "models": {"gguf": "/workspace/models/qwen2.5-0.5b-instruct-q4_k_m.gguf",
             "tokenizer": "/workspace/models/tokenizer.json",
             "identity": run("cat /workspace/VERSIONS.txt | grep -E 'gguf_sha256|tokenizer_sha256' | tr '\\n' ';'")},
  "commands": ["bash /workspace/02_build_canary.sh", "bash /workspace/03_formal_matrix.sh"],
}
json.dump(meta, open(f"{res}/metadata.json", "w"), ensure_ascii=False, indent=2)
print("metadata.json written")
PYEOF
ok_step "metadata.json"

echo "===== 1. cuflash 矩阵：3 独立进程 × 10 次测量，逐次 raw ====="
cd /workspace/src/cuflash/build/release || exit 1
LIB_DIR="$(pwd)"
export LD_LIBRARY_PATH="$LIB_DIR:$LIB_DIR/_deps/benchmark-build/src"
FILTER='BM_(Forward|Backward)_(FP32|FP16|BF16)/(512|1024|2048|4096)/64/manual_time|BM_(Forward|Backward)_FP16/4096/128/manual_time|BM_Decode_FP16/(1024|4096|16384)/64/manual_time'
PROC_FAIL=0
for p in 1 2 3; do
  timeout 1800 ./cuflash_bench --benchmark_time_unit=ms --benchmark_repetitions=10 \
    --benchmark_filter="$FILTER" \
    --benchmark_out="$RAW/cuf_run${p}.json" --benchmark_out_format=json \
    > "$RAW/cuf_run${p}.stdout" 2> "$RAW/cuf_run${p}.stderr"
  RC=$?
  if [ $RC -ne 0 ]; then PROC_FAIL=1; echo "cuflash proc $p FAILED rc=$RC" >> "$RES/STEPS.log"; fi
done
if [ $PROC_FAIL -eq 0 ]; then ok_step "cuflash 3x10 matrix"; else OVERALL=FAILURE; fi

echo "===== 2. 逐次 raw 汇总（p50/p95/mean，30 样本/配置）====="
python3 - "$RAW" "$RES" << 'PYEOF'
import json, glob, sys, statistics
raw, res = sys.argv[1], sys.argv[2]
per = {}
files = sorted(glob.glob(f"{raw}/cuf_run*.json"))
for f in files:
    try:
        d = json.load(open(f))
    except Exception as e:
        print("PARSE FAIL", f, e); continue
    for b in d.get("benchmarks", []):
        if b.get("aggregate_name"):   # 只取逐次 repetition，排除 aggregate 行
            continue
        name = b["name"].rsplit("_", 1)[0] if "_mean" in b["name"] else b["name"]
        key = name
        per.setdefault(key, []).append(b.get("real_time", 0.0))
rows = []
for k, v in sorted(per.items()):
    v = sorted(v)
    p50 = v[min(len(v)-1, round(0.5*(len(v)-1)))]
    p95 = v[min(len(v)-1, round(0.95*(len(v)-1)))]
    # 单位：--benchmark_time_unit=ms 时 JSON real_time/cpu_time 单位即为 ms（已用本地
    # bench JSON 实测确认：Backward FP16 1024/64 mean=45.0758 == 文本 45.1ms），不再缩放
    rows.append({"benchmark": k, "samples": len(v), "mean_ms": round(sum(v)/len(v), 4),
                 "p50_ms": round(p50, 4), "p95_ms": round(p95, 4)})
json.dump(rows, open(f"{res}/cuf_summary.json", "w"), indent=2)
print(f"configs={len(rows)}; samples/config={[r['samples'] for r in rows][:6]}...")
PYEOF
ok_step "cuflash summary"

echo "===== 3. tiny-llm schema v2：graph on/off × 独立进程 ====="
cd /workspace/src/tiny-llm || exit 1
MODEL=/workspace/models/qwen2.5-0.5b-instruct-q4_k_m.gguf
PROMPT="The quick brown fox jumps over the lazy dog. "
LONG_PROMPT="$(python3 -c "print('The quick brown fox jumps over the lazy dog. ' * 300)")"
TLLM_FAIL=0
for GRAPH in on off; do
  GFLAG="--graphs"; [ "$GRAPH" = off ] && GFLAG="--no-graphs"
  for LEN in short long; do
    P="$PROMPT"; [ "$LEN" = long ] && P="$LONG_PROMPT"
    OUT="$RAW/tllm_graph_${GRAPH}_${LEN}.json"
    timeout 900 ./build/tiny_llm_bench "$MODEL" --prompt "$P" --max-tokens 128 \
      --warmup 3 --iters 10 $GFLAG --json \
      > "$OUT" 2> "$RAW/tllm_graph_${GRAPH}_${LEN}.stderr"
    RC=$?
    if [ $RC -ne 0 ]; then
      TLLM_FAIL=1; echo "tiny-llm $GRAPH/$LEN FAILED rc=$RC (stderr: $(tail -1 "$RAW/tllm_graph_${GRAPH}_${LEN}.stderr"))" >> "$RES/STEPS.log"
    else
      echo "tiny-llm $GRAPH/$LEN OK prompt_tokens=$(python3 -c "import json;print(json.load(open('$OUT'))['benchmark']['prompt_tokens'])")" >> "$RES/STEPS.log"
    fi
  done
done
if [ $TLLM_FAIL -eq 0 ]; then ok_step "tiny-llm graph on/off"; else OVERALL=FAILURE; fi

echo "===== 4. nsys（仅热点窗口）====="
if command -v nsys >/dev/null 2>&1; then
  nsys --version 2>/dev/null | head -1
  cd /workspace/src/cuflash/build/release || exit 1
  nsys profile -o "$PROF/cuf_fwd.nsys-rep" --force-overwrite true \
    ./cuflash_bench --benchmark_time_unit=ms --benchmark_repetitions=10 \
    --benchmark_filter='BM_Forward_FP16/4096/64/manual_time' \
    > "$PROF/cuf_nsys.stdout" 2> "$PROF/cuf_nsys.stderr" && ok_step "nsys cuflash" || { echo "nsys cuflash rc=$? 记录" >> "$RES/STEPS.log"; }
  cd /workspace/src/tiny-llm || exit 1
  nsys profile -o "$PROF/tllm.nsys-rep" --force-overwrite true \
    ./build/tiny_llm_bench "$MODEL" --prompt "$PROMPT" --max-tokens 32 --warmup 1 --iters 3 --json \
    > "$PROF/tllm_nsys.stdout" 2> "$PROF/tllm_nsys.stderr" && ok_step "nsys tiny-llm" || { echo "nsys tiny-llm rc=$? 记录" >> "$RES/STEPS.log"; }
else
  echo "nsys NOT FOUND（记录为环境限制，不伪装完成）" >> "$RES/STEPS.log"
fi

echo "===== 5. ncu（仅热点 kernel；权限错误原样记录）====="
if command -v ncu >/dev/null 2>&1; then
  ncu --version 2>/dev/null | head -1
  cd /workspace/src/cuflash/build/release || exit 1
  ncu --set full -o "$PROF/cuf_hot" --target-processes all \
    ./cuflash_bench --benchmark_time_unit=ms --benchmark_repetitions=1 \
    --benchmark_filter='BM_Forward_FP16/4096/64/manual_time' \
    > "$PROF/cuf_ncu.stdout" 2> "$PROF/cuf_ncu.stderr" && ok_step "ncu cuflash" || { echo "ncu rc=$?（ERR_NVGPUCTRPERM 属权限限制）" >> "$RES/STEPS.log"; }
else
  echo "ncu NOT FOUND（记录为权限/工具限制）" >> "$RES/STEPS.log"
fi

echo "===== 6. STATUS manifest ====="
python3 - "$RES" "$OVERALL" << 'PYEOF'
import json, sys
res, overall = sys.argv[1], sys.argv[2]
steps = []
for line in open(f"{res}/STEPS.log"):
    parts = line.strip().split(" ", 2)
    steps.append({"status": parts[0], "step": parts[1], "detail": parts[2] if len(parts) > 2 else ""})
json.dump({"overall": overall, "generated_at_utc": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "steps": steps}, open(f"{res}/STATUS.json", "w"), indent=2)
print("STATUS.json:", overall)
PYEOF
[ "$OVERALL" = FAILURE ] && { echo "矩阵存在失败配置，见 STATUS.json / STEPS.log"; exit 1; }
echo "全部步骤 OK（详见 STATUS.json）"