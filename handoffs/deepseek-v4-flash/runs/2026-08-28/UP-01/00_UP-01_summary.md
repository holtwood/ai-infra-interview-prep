# UP-01 审计并推动已有上游贡献（2026-08-28）

查询时间：2026-08-28 13:55–14:05 +08（gh API / GitHub REST，run 快照）

## 状态总表（author=holtwood 为历史 PR 作者账号；本机 gh 账号 LessUp）

| 项 | 状态 | 关键事实 |
|----|------|----------|
| SGLang #36115 [Test] Cover page-aligned decode allocation sizing | open（mergeable_state=blocked） | 1 文件 +90（test/registered/unit/mem_cache/test_allocation_sizing.py，CPU 单测，注册 base-a-test-cpu）；Lint job **success**；GPU 矩阵全 skipped（无 run-ci label）；pr-gate 红**仅因 "Require run-ci label (optional)"**（非代码失败）；唯一 comment 是作者自己的 /tag-and-rerun-ci（2026-08-23T23:27）；无 review、无 maintainer 互动 |
| SGLang #36116 [docs] Slurm fix + examples | open（blocked） | 1 文件 +192/-35；label=documentation；requested 4 个 reviewer（wisclmy0611/zijiexia/sogalin/JustinTong0323）无实质反馈；comment 为作者自己的 /tag-and-rerun-ci |
| SGLang #35443（wes-lyu：Fix reasoning metrics + TPOT to bench_multiturn） | open（blocked） | 4 files +179/-4；labels=[hicache,run-ci,run-ci-extra]；4 comments：maintainer hzh0425 "pls fix the lint"（2026-08-20）→ wes-lyu 已修复并回复"remaining CI failures unrelated"（2026-08-21）；holtwood 于 2026-08-23 COMMENTED review，仍在 requested reviewers |
| LightLLM #1492 docs: document uv installation | open（mergeable_state=unstable） | 2 files +40/-6；mergeable=true（无冲突）；无 GitHub check-runs 可见（LightLLM CI 不通过 Actions checks 暴露）；0 comments |

## #36115 本地复现与边界（重点项）

- 被测函数 `page_aligned_decode_alloc_lens`：已存在于 upstream main
  （third_party/sglang@76d1401881 python/sglang/srt/mem_cache/allocation_sizing.py:57，
  由 #35382/#35424 引入）；**PR head（9c449782）与 upstream main 函数完全一致** → 无 rebase 风险
- 本地 harness：尝试 `pip install orjson/psutil` 于 triton-b4 后 sglang 包导入链仍缺
  （pybase64→…，完整 SGLang 安装含 CUDA 扩展不在本机）；**记录边界：未能运行 sglang 完整测试**。
  SGLang 本机未安装；此环境复现非 CI 等价
- 逻辑复现：提取 PR head 函数 + PR 7 个测试断言，无依赖 python 运行 → **7/7 断言通过**（repro_36115_logic.py）
- lint：SGLang Lint workflow success（run 32678442819）
- 完整 CI 边界：`base-a-test-cpu` 等矩阵需 `run-ci` label（maintainer/有权者）；缺 label 时
  pr-gate 输出 "Require run-ci label (optional)" → 红；**未把 label 缺失写成代码失败**

## 可执行跟进（等待授权）

- #36115 follow-up 草稿（see 02_followup_draft.md）：向维护者请求 run-ci label + 说明本地逻辑验证与
  无 rebase 状态；一次有信息增量，不刷屏
- #35443：用户仍被列为 requested reviewer——是否补充 review 由用户决定（holtwood 已 COMMENTED）
- LightLLM #1492 / #36116：docs PR，低优先；无代码问题发现

## 证据

- runs/2026-08-28/UP-01/01_pr_head_func.py（PR head 函数源码）、02_upstream_main_func.txt（一致）
- 03_pr36115_test.patch（PR 测试全量 patch，7 个 test_ 方法）
- repro_36115_logic.py（7/7 通过）
- 外部 URL：https://github.com/sgl-project/sglang/pull/36115 / pull/36116 / pull/35443 |
  https://github.com/ModelTC/LightLLM/pull/1492

## 限制

- 外部状态均为 GitHub API 快照（2026-08-28 14:05 +08）；未发布任何 comment/PR
- 未在完整 SGLang 环境运行测试（环境边界已写明）