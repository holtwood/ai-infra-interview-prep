# Changelog

遵循 [Keep a Changelog](https://keepachangelog.com/) 格式。

## [Unreleased] — 2026-08-23

### Added

- `scripts/` 目录（Python 3，零外部依赖）：
  - `check_links.py`：Markdown 链接健康检查（相对链接 + 锚点；`--online` 可查外部链接）。
  - `verify_plan.py`：计划一致性校验（TOPIC_WEIGHTS 288h/100%、12 周 frontmatter 完整、日期每周 7 天连续、枚举合法）。
  - `progress.py`：解析 weekly checkbox 汇总完成度，写回 progress-tracker / frontmatter status / README 状态列。
- `Makefile`：统一入口（`make check` / `verify` / `progress` / `progress-write`）。
- `AGENTS.md`：AI 代理操作指南（仓库地图、约定、命令），遵循 GitHub AGENTS.md 规范。
- `llms.txt`：LLM 可读文档索引，遵循 llmstxt.org 规范（H1 + blockquote + H2 分段）。
- `INDEX.md`：全仓文档按「规划 / 执行 / 追踪 / 参考」归档索引。
- `weekly-review.md`：集中式周复盘模板（完成/时间预算/原因/收获/下周调整/自评）。
- `resume/`：新增 v-performance 与 v-serving 两版公开脱敏简历，并约定真实信息使用
  Git 忽略的 `.local` 副本。
- `applications/`：迁入目标公司候选池与投递跟踪模板；新增 JD 评分和隐私边界。
- `community/`：迁入上游 issue 筛选脚本，以及 llama.cpp #26366、#26978/#26979
  的最小复现器与独立验证记录。
- `.gitignore`：排除真实简历、真实投递记录和本地 Python 产物。
- `CLOUD_GPU_PLAYBOOK.md`：新增 2026-08-23 云 GPU 价格快照、默认 L40S 48GB
  选型、$300 预算止损、12 周项目映射、每日实验闭环和 kernel/engine/serving 评测矩阵。

### Changed

- 全部 `weekly/week-01..12.md`：新增 YAML frontmatter（week/title/start/end/hours/status）与
  「相关文档」交叉引用；修正 week-06..12 日期行缺年份。
- `README.md`：文档地图加分类列；新增「每周状态」表（⬜/🔄/✅，由脚本自动更新）；
  「快速开始」升级为「执行入口」（周一启动 → 执行 → 周日复盘）。
- `progress-tracker.md`：结构化（YAML frontmatter + 每周进度表自动更新 + 周复盘存档表），
  主题与周文件标题对齐。
- 执行闭环：勾选 `- [x]` 后运行 `make progress-write`，自动更新完成度、frontmatter status 与 README 状态。
- 明确仓库职责：本仓承载公开脱敏的计划、面试、求职与社区执行材料；技术作品与跨仓
  契约仍以 `open-infra-ai` 组织为准。
- `PROJECT_STRATEGY.md`：将 `tiny-llm` 定为推理加速旗舰，`cuflash-attn` 定为
  kernel 深挖，`paged-infer` 定为 serving 扩展；冻结技术仓命名并增加新仓库门槛。
- `APPLICATION_PLAN.md`、`BASELINE.md`、`SKILL_MATRIX.md` 与 W6/W8/W10–W12 计划：
  更新当前证据、评测口径、简历版本、社区时段和单卡/多卡诚实边界。
- `tiny-llm` 的历史 schema v1 TPOT 明确标为“跨请求估算”，不得与 schema v2
  同表汇总；简历投递前必须在 clean commit 上按 schema v2 重跑正式数据。
- 全仓个人账号链接由已重定向的 `LessUp` 更新为当前 `holtwood`；删除已退出使用的
  `open-infra-ai/aicl-lab` 活跃入口。
- `community/README.md`：建立 llama.cpp → vLLM/GuideLLM → FlashInfer → SGLang
  的贡献梯度、issue 评分门槛、证据型评论模板与非交易式社区边界。

## [2026-08-19]

### Added

- 岗位与能力模型五件套：`TARGET_ROLES.md`（岗位方向与边界）、
  `JOB_MARKET_EVIDENCE.md`（2026-08-19 实时采样 23 个岗位 + 技能频次）、
  `BASELINE.md`（优势与短板）、`SKILL_MATRIX.md`（等级/证据/差距行动）、
  `TOPIC_WEIGHTS.md`（288h 权重表，含 12/18/24h 三档缩放，合计可核对）。
- `PROJECT_STRATEGY.md`：项目从"待定"改为已定组合——
  tiny-llm + paged-infer（推理系统）、cuda-foundations + cuflash-attn +
  triton-fused-ops（Kernel）、fq-compressor（C++ 辅助）。
- `INTERVIEW_MATRIX.md`：面试题五要素矩阵（答案要点/追问树/代码定位/实验证据/评分标准）。
- `APPLICATION_PLAN.md`：简历版本、投递节奏、迭代规则与手动事项。

### Changed

- `README.md` 重写：修正过期事实（旧 README 写"29 个仓库/21 deep-dives 在本仓库"），
  deep-dives 指向 github-repos-hub。
- `ROADMAP.md` 重写：12 周主线带真实日期（2026-08-24 ～ 2026-11-15），
  每周必须交付明确；大型仓库改为"五个一"目标导向阅读，不再安排全仓通读。
- `study-plan.md` 重写：周节奏与三档时间预算，与 TOPIC_WEIGHTS 数字一致。
- `weekly/week-01..12.md` 全部重写：统一结构（目标/先修/时间预算/阅读范围/实验/
  交付物/面试题/退出条件/降级规则）。
- `resources.md`：deep-dive 链接保持指向 github-repos-hub，周次映射更新为新路线。

### Removed

- `deep-dives/`（21 个文件）与 `repo-index.md`：与 github-repos-hub 逐字节相同
  （diff 验证），deep-dives 唯一事实来源移回 github-repos-hub，Git 历史保留。
- `projects/project-ideas.md`（想法已被 PROJECT_STRATEGY 的现有项目覆盖）与
  `projects/personal-projects.md`（"项目待定"文件，已被 PROJECT_STRATEGY.md 取代）。
