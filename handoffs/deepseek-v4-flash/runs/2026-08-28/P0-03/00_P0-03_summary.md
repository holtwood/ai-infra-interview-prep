# P0-03 收口 canonical 名称 - 完成部分与等待授权清单（2026-08-28）

## 已完成（live-fix 文本替换，local-only）

工作区 27 个文件 + 个人执行仓 19 个文件，全部为 `cuflash-attn → cuflash` / `paged-infer → paged-serving`
精确 token 替换（链接、路径引用、叙述、代码注释）。逐文件 diff 已审查，各仓 `git diff --check` 通过，
残留复查确认仅剩 P0-02 分类豁免集（audit / 历史计划 / 已发布 CHANGELOG / interview 材料 / .git 内部 /
handoff 执行文档中的迁移期事实描述）。

涉及仓（均为本地修改，0 提交）：`.github`、`open-infra-ai`（meta）、`tiny-llm`、`paged-infer`（目录名待迁移）、
`cuflash-attn`（目录名待迁移）、`cuda-foundations`、`triton-fused-ops`、个人执行仓（19 文件）。

## 等待授权 1：本地 checkout 目录迁移（ALLOW_KNOWN_CHECKOUT_RENAME=false）

预检（2026-08-28 12:20 快照）：
- `cuflash-attn/`：master @ d53a530（v0.6.0），clean，无后台进程假设（未发现占用），.git/config remote 为旧 URL
- `paged-infer/`：master @ 080f26f，clean，remote 为旧 URL
- 无新旧目录并存（工作区仅 cuflash-attn/ 与 paged-infer/ 各一）

授权后命令（译者：两仓均 clean、无进程占用时）：
```bash
mv /home/shane/github/open-infra-ai/cuflash-attn /home/shane/github/open-infra-ai/cuflash
mv /home/shane/github/open-infra-ai/paged-infer /home/shane/github/open-infra-ai/paged-serving
git -C /home/shane/github/open-infra-ai/cuflash remote set-url origin https://github.com/open-infra-ai/cuflash.git
git -C /home/shane/github/open-infra-ai/paged-serving remote set-url origin https://github.com/open-infra-ai/paged-serving.git
git -C /home/shane/github/open-infra-ai/cuflash status --short --branch && git -C /home/shane/github/open-infra-ai/cuflash remote -v
git -C /home/shane/github/open-infra-ai/paged-serving status --short --branch && git -C /home/shane/github/open-infra-ai/paged-serving remote -v
# 引用检查：rg 'cuflash-attn/|paged-infer/' -- 根 README、AGENTS.md 等已用 canonical 名；models/ 路径不受影响
```
影响范围：仅本地目录名与 remote URL；不影响 Git history、tag、工作树内容。
风险：若 IDE/脚本/其他代理依赖旧绝对路径会失效（当前未发现）；post-move 验证 remote fetch 一次。
rollback：`mv` 反向 + set-url 反向。

## 等待授权 2：GitHub 元数据核对（ALLOW_GITHUB_WRITE=false）

已确认线上（gh API 2026-08-28T04:18Z）：
- 仓库名：cuflash / paged-serving 已生效（旧 URL 自动重定向）✓ 无需操作
- description：均为 canonical 名（cuflash 自述 / paged-serving 自述）✓
- Pages：tiny-llm / cuflash / paged-serving / cuda-foundations 均为 open-infra-ai.github.io/<canonical>/ ✓ 无需操作
- topics：cuflash=stable、paged-serving=active、triton-fused-ops=stable、cuda-foundations=active ✓
- `.github` 仓 topics 为空（可选补充，需授权：`gh repo edit open-infra-ai/.github --add-topic ai-infra` 等）

## 等待授权 3（P0-05 范围，不在此任务执行）

- tiny-llm Latest Release 漂移（v2.0.1 @ 2026-04 vs 主分支源码）
- paged-serving v0.2.0 tag 存在但 Latest Release 仍 v0.1.0
详见 P0-05。

## 验证

- 七仓 `git diff --check` 通过（本任务只动了 6 个仓 + 个人仓）
- 残留复查：工作区 47 命中文件全部 ∈ 豁免集；个人仓 13 个 ∈ 豁免集（CHANGELOG 历史 + handoff 文档迁移期描述 + 本轮 runs/ 审计输出）
- 修改后链接均可达：cuflash / paged-serving GitHub URL 与 Pages URL 由 gh API 验证过