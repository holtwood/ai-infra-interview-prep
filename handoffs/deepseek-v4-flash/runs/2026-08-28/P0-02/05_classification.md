# P0-02 旧仓名/旧链接分类审计清单（2026-08-28）

搜索时间：2026-08-28 12:21–12:35 +08
搜索命令：`rg -n --hidden --glob '!.git/**' -e 'cuflash-attn' -e 'paged-infer' ...`
命中总数：工作区 448 行 / 87 文件；个人执行仓 522 行 / ~46 文件
替换规则：仅 `cuflash-attn → cuflash`、`paged-infer → paged-serving`（显示名/链接/叙述文本）；
文件路径 `src/tiny_llm_ffi.rs`、`include/tiny_llm/ffi.h` 本身不变（仓名前缀除外）。

## A. E. ABI/构建名分析结论（P0-02 第 3 步）

- Rust crate `paged-infer/Cargo.toml` 已为 `name = "paged-serving"`（已 canonical，非 breaking）。
- `cuflash-attn/CMakeLists.txt` 已为 `project(cuflash)` / `add_library(cuflash)` /
  `include/cuflash/`，CHANGELOG [0.6.0] 声明 C++ 命名空间 `cuflash::`、C API、`CUFLASH_*` 宏不变。
- ABI 双源 `tiny-llm/include/tiny_llm/ffi.h` ⇄ `paged-serving/src/tiny_llm_ffi.rs` 文件名、参数布局
  不变；命中仅为注释/文档中的仓名文本。**结论：全部命中为显示名/文本引用，无 breaking interface。**

## B. live-fix 清单（P0-03 唯一修改范围）

### 工作区根与组织
| 文件 | 行 | 类型 |
|------|----|------|
| README.md（根目录索引） | 26, 28 | live 链接/目录名 |
| AGENTS.md（live 治理） | 12（名称冻结表）、16（契约路径）、21（不接入 generate 路径） | live，且与用户最新指令（canonical 名）冲突，需更新 |
| .github/profile/README.md | 15, 17, 20 | org profile live 链接 |

### meta 仓（open-infra-ai/）
| 文件 | 行 | 类型 |
|------|----|------|
| README.md | 16, 18, 27, 29, 37, 50, 55, 71, 73 | 权威状态注册表 + live 链接 |
| docs/cross-repo-contracts.md | 6, 190, 193, 194, 206 | live 语义契约（仓名引用） |
| docs/repository-boundaries.md | 25, 27, 29, 54, 55 | live 治理文档 |
| LEARNING_PATH.md | 11, 13 | live 学习路径 |

### tiny-llm
| 文件 | 行 | 类型 |
|------|----|------|
| README.md | 30, 34, 35, 48 | live |
| ROADMAP.md | 77, 78 | active 路线图 |
| docs/architecture/kv-cache.md | 204, 242, 244 | live 架构文档（含 paged-infer 仓名目录引用） |
| docs/performance/optimization.md | 52, 55 | live 文档 |
| src/ffi.cpp | 1 | 代码注释 |
| include/tiny_llm/ffi.h | 1, 3, 9 | ABI 双源注释（仅文本） |
| CHANGELOG.md | 123（`## Unreleased` 节 L5-148） | **未发布 changelog**（已发布节 exempt） |
| DEVELOPMENT_PLAN.md | 97, 585, 589, 629, 653 | 历史执行计划，**exempt**（记录当时事实） |

### paged-serving（本地目录 paged-infer）
| 文件 | 行 | 类型 |
|------|----|------|
| README.md | 61, 396 | live |
| DEVELOPMENT_PLAN.md | 678 | 历史计划 **exempt** |

### cuflash（本地目录 cuflash-attn）
| 文件 | 行 | 类型 |
|------|----|------|
| docs/design/flash-decoding.md | 85 | live 文档 |
| CHANGELOG.md L20（[0.6.0]）+ L347-365（历史链接） | 已发布历史 **exempt**（正式规则：已发布 Release 链接不改，GitHub 自动重定向） |

### cuda-foundations
| 文件 | 行 | 类型 |
|------|----|------|
| README.md | 58, 64, 78, 79, 81 | live |
| README.zh-CN.md | 52, 58, 72, 73, 75 | live |
| ROADMAP.md | 8 | live |
| docs/zh/modules/03/flash-attention.md | 8 | live |
| docs/en/modules/03/flash-attention.md | 8 | live |
| 03-hpc-advanced/README.md | 19 | live |
| 03-hpc-advanced/docs/04_flash_attention.md | 4 | live |
| 03-hpc-advanced/src/05_attention/flash_attention.cuh | 4 | 代码注释 |
| CHANGELOG.md | 20（历史条目 [0.x]） | **exempt** |
| DEV_PLAN.md | 301, 303, 332, 335 | 历史计划 **exempt** |

### triton-fused-ops
| 文件 | 行 | 类型 |
|------|----|------|
| README.md | 18, 20, 160, 162 | live |
| ROADMAP.md | 6, 15 | live |
| triton_ops/kernels/flash_attention.py | 3, 5 | 代码注释 |

### 根 changelog/
| 文件 | 类型 |
|------|------|
| changelog/2026-08-21-org-reorg.md、2026-08-19-workspace-governance.md | 治理历史记录 **exempt** |

### 个人执行仓（live-fix，文本引用替换）
README.md、PROJECT_STRATEGY.md、SKILL_MATRIX.md、CLOUD_GPU_PLAYBOOK.md、APPLICATION_PLAN.md、
TARGET_ROLES.md、BASELINE.md、JOB_MARKET_EVIDENCE.md、INTERVIEW_MATRIX.md、ROADMAP.md、
applications/target-companies.md、community/README.md、resume/README.md、resume/resume-performance.zh.md、
resume/resume-serving.zh.md、weekly/week-03.md、weekly/week-07.md、weekly/week-08.md、weekly/week-11.md
（参照链接与叙述中的旧仓名）
**exempt**：CHANGELOG.md（历史条目）、weekly 已过周次（如有）、handoffs/ 历史执行快照与本轮 runs/ 审计输出

## C. generated / git 内部（不处理）
- 各仓 `.git/config`（remote URL 旧名，P0-03 仅输出 `git remote set-url` 命令草案，移动/修改需授权）
- `.git/logs/*`、`.git/FETCH_HEAD`（历史记录）

## D. 已确认无命中
- tokenizer fixture（tests/tokenizer_fixture_cases.h、tests/data/tokenizer_fixture.json、scripts/gen_tokenizer_fixture.py）✓
- docs/organization-audit/（审计快照）✓ exempt
- meta 历史计划（MASTER_PLAN.md、PHASE*.md、PLAN_v3.md、PLAN_I.md）✓ exempt
- meta interview/（面试历史材料）✓ exempt（talks/*.md 文件名含旧名如 05-paged-infer.md 为文件名，不改）

## 验证方法
- 每个修改文件：`git diff --check`；替换后全文复查 `rg -n 'cuflash-attn|paged-infer' <repo>` 仅剩 exempt 文件
- 链接可达性：`gh api` 已确认 cuflash/paged-serving URL 生效（2026-08-28T04:18Z 快照）