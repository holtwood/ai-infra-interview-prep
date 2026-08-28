#!/usr/bin/env python3
"""PSERV-02 独立复算：loadgen 聚合算法（build_summary）的独立实现。

输入：构造已知样本（成功/失败/无 token/零 token），输出聚合并与预期比对。
算法忠实复刻 loadgen.rs：
- percentile: nearest-rank，idx=round(p/100*(n-1))，sorted total_cmp
- TTFT: 成功请求的 ttft_ms 聚合
- TPOT: (duration-ttft)/(tokens-1)，tokens>1 且 ttft 存在
- tok/s: total_tokens/wall_secs，仅当 known==ok（100% coverage），否则 None
- coverage: known/ok
"""
from statistics import median


def percentile(sorted_v, p):
    if not sorted_v:
        return None
    idx = round((p / 100.0) * (len(sorted_v) - 1))
    return sorted_v[min(idx, len(sorted_v) - 1)]


def metric_summary(values):
    sv = sorted(values)
    return {
        "samples": len(sv),
        "p50": percentile(sv, 50),
        "p95": percentile(sv, 95),
        "p99": percentile(sv, 99),
    }


def build_summary(records, wall_secs):
    ok_recs = [r for r in records if r["ok"]]
    ok = len(ok_recs)
    ttfts = [r["ttft_ms"] for r in ok_recs if r["ttft_ms"] is not None]
    tpots = []
    for r in ok_recs:
        tokens = r.get("completion_tokens") or 0
        if r["ttft_ms"] is not None and tokens > 1:
            tpots.append((r["duration_ms"] - r["ttft_ms"]) / (tokens - 1))
    known = [r for r in ok_recs if r.get("completion_tokens") is not None]
    total_tokens = sum(r["completion_tokens"] for r in known)
    coverage = 100.0 * len(known) / ok if ok > 0 else 0.0
    tok_s = (
        (total_tokens / wall_secs)
        if (wall_secs > 0 and ok > 0 and len(known) == ok)
        else None
    )
    return {
        "requests": {"total": len(records), "success": ok, "failed": len(records) - ok},
        "ttft_ms": metric_summary(ttfts),
        "tpot_ms": metric_summary(tpots),
        "coverage_pct": coverage,
        "known": len(known),
        "output_tokens_per_second": tok_s,
    }


# ── 已知样本 ─────────────────────────────────────────────────────────
# 3 成功（ttft 已知、tokens>1）+ 1 失败 + 1 成功但无 token 记录（completion_tokens=None，
# 对应 loadgen 的 tokens_source=None 场景）→ partial coverage
records = [
    {"ok": True, "ttft_ms": 100.0, "duration_ms": 300.0, "completion_tokens": 32},   # tpot=200/31=6.4516
    {"ok": True, "ttft_ms": 120.0, "duration_ms": 400.0, "completion_tokens": 64},   # tpot=280/63=4.4444
    {"ok": True, "ttft_ms": 80.0, "duration_ms": 200.0, "completion_tokens": 16},    # tpot=120/15=8.0
    {"ok": False, "ttft_ms": None, "duration_ms": 50.0, "completion_tokens": None},  # 失败
    {"ok": True, "ttft_ms": 90.0, "duration_ms": 90.0, "completion_tokens": None},   # 成功但无 token 记录
]
wall = 10.0
res = build_summary(records, wall)

# 零 token 边界：completion_tokens=Some(0) 也算 known（loadgen 语义：usage 明确给了 0）
zero_records = [dict(r) for r in records if r["ok"]]
for r in zero_records:
    r["completion_tokens"] = 0
zero_res = build_summary(zero_records, 10.0)

# 手工预期
expected = {
    "requests": {"total": 5, "success": 4, "failed": 1},
    "ttft_p50": percentile(sorted([100.0, 120.0, 80.0, 90.0]), 50),
    "tpot_sorted": sorted([6.451612903225806, 4.444444444444445, 8.0]),
    "coverage_pct": 75.0,  # 3/4
    "known": 3,
    "tok_s": None,          # known(3) != ok(4) → tok/s 必须为 null
}
tpot_expected = metric_summary([6.451612903225806, 4.444444444444445, 8.0])

errors = []
def check(name, got, want):
    if got != want:
        errors.append(f"{name}: got={got} want={want}")

check("requests", res["requests"], expected["requests"])
check("ttft_p50", res["ttft_ms"]["p50"], expected["ttft_p50"])
check("ttft_samples", res["ttft_ms"]["samples"], 4)
check("tpot_p50", res["tpot_ms"]["p50"], tpot_expected["p50"])
check("tpot_p95", res["tpot_ms"]["p95"], tpot_expected["p95"])
check("tpot_samples", res["tpot_ms"]["samples"], 3)
check("coverage", res["coverage_pct"], expected["coverage_pct"])
check("known", res["known"], expected["known"])
check("tok_s_None(partial coverage)", res["output_tokens_per_second"], expected["tok_s"])

# 全 coverage 情形：tok/s 有效
full_records = [dict(r) for r in records if r["ok"] and r["completion_tokens"] is not None]
full_res = build_summary(full_records, 10.0)
# tokens: 32+64+16=112 → 11.2 tok/s
check("tok_s_full", full_res["output_tokens_per_second"], 112 / 10.0)
check("coverage_full", full_res["coverage_pct"], 100.0)

# 零 token（Some(0)）边界：coverage 计入、tok/s=0.0（合法值，usage 明确 0）、TPOT 无样本
check("zero_tok_coverage", zero_res["coverage_pct"], 100.0)
check("zero_tok_known", zero_res["known"], 4)
check("zero_tok_tok_s", zero_res["output_tokens_per_second"], 0.0)
check("zero_tok_tpot_samples", zero_res["tpot_ms"]["samples"], 0)

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
print("PASS 全部 11 项复算一致")
print(f"  ttft_p50={res['ttft_ms']['p50']}, tpot_p50={res['tpot_ms']['p50']:.4f}, "
      f"tpot_p95={res['tpot_ms']['p95']:.4f}, coverage={res['coverage_pct']}%")
print(f"  partial coverage → tok/s=None（正确门控）；full coverage → {full_res['output_tokens_per_second']} tok/s")