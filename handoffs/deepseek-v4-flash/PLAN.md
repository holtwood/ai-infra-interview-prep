# open-infra-ai 12 周执行计划（DeepSeek V4 Flash Handoff）

> 版本：1.0
>
> 计划快照：2026-08-28
>
> 执行周期：2026-08-24 ～ 2026-11-15
>
> 适用工作区：`/home/shane/github/open-infra-ai` 及本执行仓
>
> 任务状态权威来源：[TASKS.md](TASKS.md)
>
> 执行代理入口：[PROMPT.md](PROMPT.md)

## 0. 文件职责与事实来源

本文件把现有 12 周求职路线转换为可由编码代理执行的跨仓技术计划。它不取代以下权威文件：

- 周次、日期、总时数：[ROADMAP.md](../../ROADMAP.md)、[TOPIC_WEIGHTS.md](../../TOPIC_WEIGHTS.md)；
- 项目边界：[PROJECT_STRATEGY.md](../../PROJECT_STRATEGY.md)；
- 云资源、预算和实验闭环：[CLOUD_GPU_PLAYBOOK.md](../../CLOUD_GPU_PLAYBOOK.md)；
- 每周人工学习与面试交付：[weekly/](../../weekly/)；
- 技术事实：各技术仓当前代码、测试、结果文件和 GitHub 上游状态。

三份 handoff 文件的职责如下：

| 文件 | 唯一职责 |
|------|----------|
| `PLAN.md` | 固定目标、边界、阶段、依赖、资源、风险和完成标准 |
| `TASKS.md` | 保存可执行任务、状态、验证命令和证据产物 |
| `PROMPT.md` | 约束执行代理的行为、权限、汇报和停止条件 |

若三者冲突，优先级为：用户最新明确指令 > 适用的 `AGENTS.md` > `TASKS.md` 当前任务 >
本文件 > 旧计划档案。任何性能或完成状态都以本轮实际命令与原始产物为准。

## 1. 最终定位

### 1.1 求职定位

主定位：**LLM Inference Runtime / GPU Performance Engineer**。

组织的一句话叙事：

> Verifiable LLM inference systems: CUDA kernels, a C++ runtime, and a Rust
> serving control plane.

个人转型叙事不是“从零学习 AI”，而是把既有 C++/HPC、并发、数据布局和性能工程经验迁移到
LLM 推理系统。

### 1.2 三条公开技术叙事

| 叙事 | 仓库 | 证明内容 | 展示级别 |
|------|------|----------|----------|
| 主旗舰 | `tiny-llm` + `paged-serving` | GGUF/W8A16、decode、Paged KV、C ABI、continuous batching、HTTP/SSE、Serving 评测 | 简历与面试主讲 |
| Kernel 深度 | `cuflash` | online softmax、WMMA、前后向、FlashDecoding、数值验证与 profiler | Kernel 岗主讲 |
| 基础与横向对照 | `cuda-foundations` + `triton-fused-ops` | CUDA 优化阶梯、Triton 表达、`torch.library`、独立参考实现 | 辅助证据 |

五仓不平铺成五个同等重要项目，不新增同类玩具仓，也不把 `cuflash` 接入 `tiny-llm`
generate 路径。

## 2. 已确认的固定决策

### 2.1 Canonical 名称

用户已于 2026-08-27 确认以下名字为最终名称：

- `cuflash`，GitHub：<https://github.com/open-infra-ai/cuflash>；
- `paged-serving`，GitHub：<https://github.com/open-infra-ai/paged-serving>。

其余技术仓保持：`tiny-llm`、`triton-fused-ops`、`cuda-foundations`。完成本轮迁移后，五个
技术仓名称永久冻结。

本地 checkout 已于 2026-08-28（P0-03M）迁移为 canonical 目录：

| Canonical 仓名 | 本地目录（已迁移） | 说明 |
|----------------|--------------------|------|
| `cuflash` | `/home/shane/github/open-infra-ai/cuflash` | 迁移完成（2026-08-28），remote 已更新为 canonical URL |
| `paged-serving` | `/home/shane/github/open-infra-ai/paged-serving` | 迁移完成（2026-08-28），remote 已更新为 canonical URL |

迁移记录见 handoffs/deepseek-v4-flash/runs/2026-08-28/P0-03M/。执行代理不再按旧目录名
（`cuflash-attn`、`paged-infer`）定位仓库；历史执行记录中的旧目录名保持为当时事实，不改写。

### 2.2 永不批量改写的历史内容

以下内容记录当时事实，只能在发现安全或正确性问题时单独讨论，不能参加全局改名：

- `open-infra-ai/docs/organization-audit/`；
- 各仓 `CHANGELOG` 已发布历史和历史 Release 链接；
- meta 仓历史计划与 `interview/` 历史材料；
- tokenizer fixture 原文及其生成器；
- Git commit、tag、上游 issue/PR 的历史标题和正文。

live README、状态注册表、当前路线图、代码注释、构建元数据、badge、Pages、仓库 description、
topics 和未发布 changelog 必须使用 canonical 名称。

### 2.3 证据纪律

- correctness 未通过时禁止采集或发布性能数字；
- 原始 JSON/JSONL、逐请求/逐迭代数据是权威，图表必须可由原始数据重建；
- 不同 GPU、模型、量化、请求分布和软件栈不能合并成同一 before/after；
- `cudaMemGetInfo` 两点差值只能称“常驻显存差值”，不能称峰值；
- token coverage 不完整时，Serving tok/s/TPOT 保持不可用，不从 SSE chunk 数猜 token；
- 脚手架、本地 smoke、云端正式结果、上游 open PR 和已合入贡献必须明确区分；
- 负结果、OOM、429、启动失败、回归和 profiler 限制都要归档。

## 3. 2026-08-28 基线与主要缺口

| 仓库 | 当前优势 | 当前主要缺口 | 计划角色 |
|------|----------|--------------|----------|
| `tiny-llm` | 真实 Qwen2.5-0.5B、W8A16、分页 KV、CUDA Graph schema v2 A/B、C ABI | 主分支格式 CI 红；第二模型、同口径 llama.cpp 基线、长上下文与正式 profiler 未闭环；源码/Release 不同步 | P0 + 主旗舰 |
| `paged-serving` | Rust 控制面、Paged KV、continuous batching、真实 tiny-llm 后端、可信 loadgen/结果 schema | 主分支 rustfmt CI 红；正式 GPU Serving 结果未发布；v0.2.0 tag/Latest Release 不同步 | P0 + 主旗舰 |
| `cuflash` | FP32/FP16/BF16 前后向、WMMA、FlashDecoding、v0.6.0 | 改名残留；live 文档仍可看到不可审计旧表；缺正式原始 JSON/Nsight 结果包 | 稳定维护 + 一次正式证据 |
| `triton-fused-ops` | 三个自定义 op、Triton/参考差分、`torch.library`、v2.0.1 | 旧链接；缺 CUDA/Triton/C++ 统一讲述 | stable 辅助 |
| `cuda-foundations` | 四模块、CUDA 优化阶梯、广泛正确性覆盖 | 旧链接；已声明不扩模块但状态仍 active | 收口为 stable 辅助 |
| meta / `.github` | 能力链、状态注册表、跨仓契约 | 线上新名与本地治理/组织 profile 不一致 | P0 治理 |

组织当前不是“功能不够”，而是“公开状态、Release、正式硬件证据和外部合入不足”。所有阶段按此
优先级排序。

## 4. 12 周可验收结果

周期结束时必须能够直接提供以下证据：

1. 五个技术仓默认分支最新 required checks 全绿；
2. live 文档、仓库元数据、Pages 和本地 checkout 使用最终 canonical 名称；
3. `tiny-llm` 源码、tag、Release、CHANGELOG 和文档版本一致；
4. `paged-serving` v0.2.x GitHub Release 与当前控制面能力一致；
5. `tiny-llm` 至少两个真实模型或两种真实架构门控，其中第二模型有端到端日志；
6. 一份同口径、限制清楚的 llama.cpp 外部基线；
7. 一份绑定硬件、双仓 commit、模型、量化、请求分布和原始逐请求数据的 GPU Serving 结果包；
8. 一份 `cuflash` 当前版本的正式 benchmark/profiler 结果包，保留更慢和负优化形状；
9. 至少一个已合入的 SGLang/vLLM/LightLLM/llama.cpp 代码或测试贡献，理想目标为两个；
10. 两个 10 分钟 live demo、两个 STAR 条目和一篇深度技术文章；
11. 所有公开数字可以从仓库结果文件、命令和 commit 追溯；
12. 没有新增同类仓库、没有未经测量的性能主张、没有吞入用户或并行代理的改动。

上游是否合入受维护者控制。若周期结束时 PR 仍 open，必须保存复现、测试、review、CI 和维护者
互动证据，但不能把 open PR 写成“完成上游贡献”。

## 5. 阶段计划

### Phase 0：公共可信度恢复（W1，2026-08-24 ～ 2026-08-30）

目标：先让公开组织名称一致、旗舰主分支绿色、发布状态可解释。

执行顺序：

1. `P0-01` 建立所有仓库 HEAD、dirty、remote、CI、Release 的只读基线；
2. `P0-02` 生成旧名称命中清单，区分 live 与历史豁免；
3. `P0-03` 完成 canonical 名称迁移及本地 checkout 收口；
4. `P0-04` 修复 `tiny-llm` 与 `paged-serving` 当前格式门禁；
5. `P0-05` 准备并在授权后完成 Release 同步；
6. `P0-06` 做组织级链接、topics、Pages、CI 和状态复核。

退出条件：

- live 用户入口不再出现旧名；
- 历史豁免未被改写；
- 五仓本地验证按风险通过；
- 线上 CI 已通过或清楚记录尚待外部运行；
- Release 操作若未授权，已有可审查的 tag/release checklist，不能假装完成。

### Phase 1：Runtime 旗舰证据（W2–W5，2026-08-31 ～ 2026-09-27）

目标：证明 `tiny-llm` 不只在单一模型上“能跑”，还具备可解释的正确性、失败行为和外部基线。

主要任务：`TLLM-01` ～ `TLLM-07`。

执行原则：

- 先固定当前 HEAD 的 Qwen2.5 correctness 与 schema v2 基线；
- 第二模型优先验证另一组真实 GQA/MQA 配置，不为了模型数量重复相同架构；
- llama.cpp 只做外部参照，量化不同必须醒目标注，不能宣传公平加速比；
- 长上下文实验同时记录 correctness、常驻/峰值口径、OOM 边界；
- profiler 只在有权限的云实例执行；
- 新优化必须从测量热点产生，一次只改变一个主要因素；
- speculative decoding 不属于本周期默认范围。

退出条件：第二模型端到端门控、外部基线、长上下文/失败矩阵至少完成两项；任何顺延项有明确原因、
最小替代证据和恢复条件。

### Phase 2：Serving 与 Kernel 正式证据（W6–W8，2026-09-28 ～ 2026-10-18）

目标：把已有评测脚手架变成能经受追问的正式结果包。

主要任务：`PSERV-01` ～ `PSERV-06`、`CUF-01` ～ `CUF-03`。

Serving 需要分成两类实验：

1. **内部隔离实验**：同一 `tiny-llm` 后端下 continuous batching on/off，用于证明调度变化；
2. **跨引擎系统观察**：`paged-serving` / `llama-server` / `vLLM` 使用统一 loadgen，绑定各自模型、
   量化和 commit；若实现栈无法同量化，只报告观测值与限制，不得得出实现优胜结论。

建议矩阵：

- synthetic 128/128、512/128、2048/256，加一组真实对话长度分布；
- 并发 1/2/4/8，显存允许时 16；
- closed-loop 与 Poisson offered load；
- 指标：成功率、错误类型、TTFT p50/p95/p99、TPOT、输出 token 吞吐、请求吞吐、KV 利用率；
- 场景：取消、HOL、fairness、429、OOM、客户端断开和长短请求混合。

`cuflash` 只做一次当前版本的正式证据闭环。若 profiler 未发现清晰且可在 1–3 天内验证的优化点，
输出“未优化”结论并保持 stable，不为勾选任务修改 kernel。

退出条件：至少一个完整 GPU Serving 结果包和一个当前 `cuflash` 结果包通过各自 validator/复算；
云资源不可用时只能标记 blocked，不能用 CPU 或旧表替代。

### Phase 3：上游与对外表达（W9–W10，2026-10-19 ～ 2026-11-01）

目标：把自有仓经验转成外部维护者可验证的价值。

主要任务：`UP-01` ～ `UP-03`、`SUP-01` ～ `SUP-02`、`EVID-01`。

社区主线固定为 SGLang；LightLLM 文档 PR 和 llama.cpp 只作为已有上下文，不继续同时扩散。优先级：

1. 推动已有测试 PR 获得 review/CI；
2. 选择一个 scheduler/KV/cache/benchmark 相关真实 issue；
3. 最小复现、失败测试、有限修复、完整本地验证；
4. 由用户审核外部措辞后再发布评论或 PR。

外部写操作、review、comment、PR、label、Release 和仓库设置都需要单独授权。

退出条件：至少一个外部 PR 获得实质性维护者反馈；合入目标未达成时保留完整证据并诚实标记状态。

### Phase 4：面试与投递闭环（W11–W12，2026-11-02 ～ 2026-11-15）

目标：停止探索新技术，把已验证工作压缩成可演示、可追问、可投递的材料。

主要任务：`EVID-01` ～ `EVID-02`，并执行现有 week-11/week-12 交付物。

退出条件：

- Runtime 与 Kernel/Serving 两套岗位叙事都能在 10 分钟内完成；
- 所有数字链接到结果文件；
- 模拟面试暴露的问题已回填到能力矩阵；
- 已开始投递，不以可选功能未完成为由继续延迟。

## 6. 时间与资源分配

沿用 24h/周、12 周 288h 的总预算。执行代理只管理技术和证据任务，不自动代替人工学习、算法练习、
模拟面试和投递。

建议每周平均：

| 工作流 | 小时/周 | 说明 |
|--------|--------:|------|
| `tiny-llm` Runtime 与正式证据 | 8h | 主旗舰 |
| `paged-serving` / Serving 评测 | 6h | 与 Runtime 共用结果链 |
| 上游复现、review、PR | 4h | 固定连续投入，不临时撒网 |
| `cuflash` 正式证据 | 2h | 仅 W3/W6–W8 集中使用 |
| 面试、投递、STAR/Demo | 2h | 后四周提高占比 |
| 组织治理、Release、辅助仓维护 | 2h | P0 后降为维护 |

云 GPU 沿用 [CLOUD_GPU_PLAYBOOK.md](../../CLOUD_GPU_PLAYBOOK.md) 的预算与止损规则。执行代理默认没有购买、
创建、续费或删除云实例的权限；只能准备命令、清单和本地 canary，得到用户单独授权后才能操作。

## 7. 验证层级与完成口径

| 层级 | 可以声称 | 不可以声称 |
|------|----------|------------|
| 静态检查 | 格式、lint、链接或 schema 检查通过 | 运行时正确 |
| CPU/Mock | 调度、协议、参考逻辑或错误路径通过 | CUDA 后端或 GPU 性能通过 |
| 本地 RTX 3060 | 该机器、该 commit、该模型下的 correctness/性能 | 数据中心 GPU、生产容量或跨硬件结论 |
| 云单卡 | 指定实例与结果包覆盖的矩阵 | 多 GPU、全架构或生产 SLO |
| 上游 open PR | 已提交、已有 CI/review 的贡献 | 已合入或已被上游采用 |
| 上游 merged PR | 对应 commit 已合入 | 超出 PR 范围的社区影响 |

每个任务只有同时满足以下条件才能标记 `done`：

1. 任务范围内实现或文档完成；
2. 任务指定验证命令实际运行并记录退出码；
3. 结果/日志/报告保存到指定位置；
4. 限制、跳过和失败已写清；
5. `git diff --check` 通过且未混入其他改动；
6. 若任务包含线上状态，已通过 GitHub/API 重新确认，而不是依赖本地 remote-tracking ref；
7. `TASKS.md` 状态与证据链接已更新。

## 8. 权限矩阵

### 8.1 Handoff Prompt 默认授权

- 读取计划范围内的本地仓库和公开网页；
- 修改计划明确列出的本地源码、测试、文档与配置；
- 运行本地格式、构建、测试、benchmark smoke 和只读诊断；
- 更新 `TASKS.md` 的状态和证据；
- 为后续 commit 准备精确文件清单。

### 8.2 必须再次向用户申请

- `git commit`、`git push`、force push、rebase 已公开分支；
- GitHub comment/review/PR/issue、Release、tag、仓库设置、topics、Pages 或分支保护写操作；
- 云 GPU 购买、启动、停止、删除、扩容和任何付费资源；
- 下载需要接受许可证或登录的模型；
- 删除、覆盖或移动无法确认归属的文件/目录；
- 修改历史豁免内容；
- 任务范围外的架构变化、ABI breaking change 或新增仓库。

### 8.3 永不允许

- 伪造命令、测试、云实验、profiler、上游反馈或性能数字；
- 使用 `git add .`、`git add -A` 或吞入并行/用户改动；
- `git reset --hard`、强制清理整个工作区、改写公开历史；
- 提交模型权重、token、SSH key、真实联系方式、投递状态或云凭据；
- 为完成 checkbox 写冗余防御代码、无依据 fallback 或无关 README 美化。

## 9. 工作树与提交边界

- `/home/shane/github/open-infra-ai` 是并排工作区，不是 monorepo；每仓独立验证和提交；
- 任务开始前记录所有仓 `git status --short`，结束后再次比较；
- 已知未跟踪内容如个人执行仓 `evidence/`、`tiny-llm/.zcode/` 默认属于用户，禁止纳入；
- 一次只修改一个仓的一个任务主题，跨仓 breaking contract 除外；
- 跨仓 ABI 变更必须先改 live 契约，再同批修改 `tiny-llm` / `paged-serving` 和两仓 CHANGELOG；
- 提交前运行 `git diff --check`、指定测试和疑似凭证扫描；
- 用户授权 commit 后精确暂存任务文件，提交信息描述事实，不写不存在的验证结果。

## 10. 证据包标准

正式结果目录至少包含：

```text
README.md                  # 问题、结论、限制、复现方法
metadata.json              # 硬件、软件、commit、dirty、模型、量化
commands.sh                # 实际执行命令，不含凭据
stdout.log / stderr.log
raw/*.json 或 *.jsonl      # 权威原始样本
summary.json               # 机器可读聚合
plots/*.csv / *.png        # 可由 raw 重建
profiler/*                 # nsys/ncu 报告及版本
validation.log             # validator/复算结果
```

若仓库已有更严格 schema，以仓库 schema 为准。正式报告必须能回答：比较基线、唯一变化、硬件、模型、
量化、请求分布、warmup、重复次数、统计方法、失败率、反证条件和不适用范围。

## 11. 风险与止损

| 风险 | 触发信号 | 处理 |
|------|----------|------|
| 改名迁移破坏历史 | 命中 CHANGELOG/tag/审计快照 | 恢复历史文件，仅修 live 入口 |
| 多仓工作吞入他人改动 | preflight 已 dirty 或 diff 扩大 | 停止该仓，绕开或请求用户处理 |
| 本机 profiler 不可用 | `ERR_NVGPUCTRPERM`、缺 importer | 保存限制；转云任务，不能伪装结果 |
| 云成本失控 | 空闲、反复构建、有效产物不足 50% | 立即停机，回本地修流程 |
| 比较不公平 | 模型/量化/输出长度不同 | 拆成系统观察，取消优胜结论 |
| 功能扩张 | 想做 speculative/prefix cache/multi-GPU runtime | 先完成当前证据；默认拒绝扩 scope |
| 上游无人响应 | 一次人工 follow-up 后仍无反馈 | 保留证据，转下一个真实 issue，不刷屏 |
| 文档再次漂移 | README、Release、topics 状态不一致 | P0/P4 组织审计门禁失败，不发布新结论 |

## 12. 计划更新规则

- 日常执行只更新 [TASKS.md](TASKS.md)；
- 目标、边界、周期或资源预算变化时才更新本文件；
- 新增任务必须写明它替代或推迟哪个现有任务，不能无成本扩容；
- blocked 任务必须写阻塞证据、所需权限和可继续的独立任务；
- 每周复盘仍写入现有 `weekly/week-NN.md` 与 `progress-tracker.md`，handoff 不复制周报；
- 计划周期结束后，本 handoff 作为执行快照归档，不改写为“全部成功”。
