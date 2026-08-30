# TLLM-04 证据缺口说明（review 校正，2026-08-28）

## 缺口

TASKS.md / 00_TLLM-04_summary.md 声称曲线 "5 success + 2 failure"，其中：
- **failure 2（16384 E2BIG）**：原始证据完整
  - `bench_len_16384_fail.log`（87B："argument list too long ... exit=127 (E2BIG 参数超限)"）
  - `bench_len_16384.json`（0B，失败时无输出）+ `bench_len_16384.stderr`（40B）✓
- **failure 1（8192 首次 iters=3 超时 rc=124）**：**原始输出未独立保留**
  - 首次命令 `timeout 300 ./build/tiny_llm_bench ... > bench_len_8192.json 2> bench_len_8192.stderr` 超时（rc=124）
  - 随后降为 iters=1 的**成功运行覆盖了同一个 `bench_len_8192.json`**（现为 605B 成功数据）
  - `bench_len_8192.stderr` 现为 0B（被成功运行覆盖）
  - 唯一超时证据为当时命令回显 "FAILED (rc=124)"（会话记录，不在 runs/ 文件中）

## 结论与处置

- 该失败事实真实发生（当时 rc=124 回显 + 成功点以 iters=1 重跑），但**原始失败日志未被保留**，
  不符合"失败点原始 JSON/日志保留"纪律的严格口径。
- 处置：本说明文件记录缺口；TASKS.md TLLM-04 执行记录同步标注。未来长上下文扫描若遇超时，
  应以独立文件名（如 `bench_len_8192_try1_*.json/stderr`）保留每次尝试，避免覆盖。
- 不删除任何现存文件（16384 失败证据保留）。