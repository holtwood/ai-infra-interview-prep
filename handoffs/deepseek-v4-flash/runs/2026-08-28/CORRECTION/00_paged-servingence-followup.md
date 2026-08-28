# 校正回合 2026-08-28：paged-servingence-system 残余 follow-up 记录

扫描时间：2026-08-28 15:15 +08:00
扫描命令：`rg -n 'paged-servingence|paged-inference|servingence' /home/shane/github/open-infra-ai/paged-infer/ --glob '!.git/**' --glob '!target/**'`

## 命中清单（6 处，全部为源码 doc 注释，无代码/无运行时语义）

| 文件 | 行 | 原文 |
|------|-----|------|
| src/kv_cache.rs | 409 | `/// **Feature: paged-servingence-system, Property 5: Block Count Invariant**` |
| src/kv_cache.rs | 453 | `/// **Feature: paged-servingence-system, Property 3: Block Allocation on Sequence Start**` |
| src/kv_cache.rs | 492 | `/// **Feature: paged-servingence-system, Property 4: Block Allocation on Growth**` |
| src/kv_cache.rs | 534 | `/// **Feature: paged-servingence-system, Property 12: Memory Statistics Invariant**` |
| src/gpu_executor.rs | 267 | `/// **Feature: paged-servingence-system, Property 11: Variable Sequence Length Handling**` |
| src/tokenizer.rs | 723 | `/// **Feature: paged-servingence-system, Property 15: Tokenizer Round-Trip**` |

## 原始来源推断

字符串形态为 `paged-serving` + `ence-system`，与相邻的 `paged-inference-system` 结构吻合：
当项目从 `paged-infer` 改名为 `paged-serving` 时，对旧 Feature 标识 `paged-inference-system`
执行 "infer → serving" 的机械替换，`inference` 中的 `infer` 被替换后残留 `ence`，
产生损坏字符串 `paged-servingence-system`。属于改名工具/人工替换的遗漏型损坏，
非有意命名。

## 影响评估

- 全部位于 `///` doc 注释（纯文本，无 rustdoc 代码块），不参与编译或执行
- 不作为测试标识符使用（Property 编号是 rustdoc 标题的一部分而非代码标识符）
- 不影响 ABI、命名空间、crate 名（crate 名已为 paged-serving）
- 不影响任何测试结果（cargo test 215 passed + 17 doc-tests 已实测）

## 处置（本轮禁止修改源码）

本校正回合 `ALLOW_CODE_CHANGES=false`，仅记录。建议修复方案（后续需用户授权
`ALLOW_CODE_CHANGES=true` 后执行）：

- 将 6 处 `paged-servingence-system` 统一替换为 `paged-serving-system`（与当前 canonical
  crate 名一致的最短修复），或恢复原 `paged-inference-system`（若该 Feature 命名属于历史
  ABI/测试标识需要保留——但从纯 doc 注释判断无此要求）
- 推荐 `paged-serving-system`，替换后 `cargo test --locked` 回归 + `cargo doc` 检查渲染
- 修复任务建议挂到 P0-06（组织级复核）或作为 PSERV-05 的附带清理项

## 证据

本记录；原始命中输出见会话日志（已脱敏无敏感信息）。未修改任何源码。