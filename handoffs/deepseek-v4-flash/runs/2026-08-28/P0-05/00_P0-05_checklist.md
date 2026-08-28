# P0-05 版本同步 checklist（2026-08-28，等待授权执行）

查询时间：2026-08-28 ~13:40 +08（gh API / git 本地）
结论：两仓都存在真实版本漂移，均需 commit/push/tag/Release 授权才能闭环。

## 一、tiny-llm：源码 2.0.2 > Latest Release v2.0.1

| 项 | 值 |
|----|----|
| CMakeLists VERSION | 2.0.2 |
| CHANGELOG | `## Unreleased`（L5-148，实质内容：指标口径修复、logprobs ABI 收紧、GGUF 健壮性、CUDA Graph schema v2 正式 A/B 等） |
| tags | v2.0.0, v2.0.1（无 v2.0.2） |
| Latest Release | v2.0.1（2026-04-21T19:41Z，无资产） |
| release workflow | .github/workflows/release.yml：tag `v*.*.*` 触发 → CUDA 11.8/gcc-10 构建 + ctest + tar.gz + softprops/action-gh-release（generate_release_notes=true） |

**执行步骤（授权后）：**
1. `CHANGELOG.md`：`## Unreleased` → `## [2.0.2] - 2026-08-28`（内容即 HEAD 已提交事实）
2. commit（精确暂存 CHANGELOG.md，含 P0-03/P0-04 未提交改动一起？——注意：工作树有 P0-03/P0-04 未提交改动，发布应基于包含格式修复的新 HEAD）
3. `git tag v2.0.2` @ 新 HEAD；`git push origin master v2.0.2`（触发 release workflow）
4. 观察 workflow：build+test 绿 → release v2.0.2 生成
5. 验证：`gh release view v2.0.2`（Latest 生效、资产 tar.gz 存在、校验和 sha256sum）

## 二、paged-serving：v0.2.0 tag 存在，Latest Release 仍 v0.1.0

| 项 | 值 |
|----|----|
| Cargo.toml version | 0.2.0 |
| CHANGELOG | `[0.2.0] - 2026-08-17`（已归档 L59-175）+ `[Unreleased]`（L8-58：loadgen、容量调节、改名、正式结果包等） |
| tags | v0.2.0 @ f3f94c7（release: freeze v0.2.0 (T13)），v0.1.0 |
| HEAD | 080f26f（v0.2.0 之后 22 commit：改名 4a8807b/080f26f、loadgen、正式评测包 0b9ac8a、B1-B17 修复等） |
| Latest Release | v0.1.0（2026-04-16，无资产） |
| release workflow | 无（仅 ci.yml）→ Release 需手动 `gh release create` |

**执行步骤（授权后，二选一，需用户定夺）：**
- 方案 A（最小补漏）：`gh release create v0.2.0 -R open-infra-ai/paged-serving --title "paged-serving v0.2.0" --notes-from-tag`（notes 用 CHANGELOG [0.2.0] 节）。但 v0.2.0 tag 内容落后 HEAD（不含改名与 loadgen），不满足"与当前控制面能力一致"。
- 方案 B（推荐，满足 PLAN 验收 4）：在 HEAD 打 v0.3.0（或 v0.2.1）tag：CHANGELOG Unreleased → `[0.3.0] - 2026-08-28`；`git tag v0.3.0 && git push origin master v0.3.0`；`gh release create v0.3.0`（可顺带为 v0.2.0 补 Release 或留作 tag-only）。发布后 Latest = 新版本。
- 两种方案下 v0.2.0 与 v0.3.0 的 CHANGELOG 链接引用 `[0.2.0]: https://github.com/open-infra-ai/paged-serving/compare/...` 需核对。

## 三、共同前置与限制

- 两仓当前工作树含本会话未提交改动（P0-03 名称收口 + P0-04 格式修复），发布 commit 必须一起暂存
- 授权清单：`ALLOW_GIT_COMMIT=true`（两仓各 1 个 commit）、`ALLOW_GIT_PUSH=true`（master + tag）、
  `ALLOW_GITHUB_WRITE=true`（gh release create / workflow 触发）
- 所有 release notes 只陈述可由 commit/test 证明的变化
- 不重打已有公开 tag（v2.0.1/v2.0.0/v0.1.0/v0.2.0 均不动）
- rollback：release 可 `gh release delete` + 本地 tag 可 `git tag -d`（仅限本次新建的 tag）