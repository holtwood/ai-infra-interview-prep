# SUP-01 辅助仓改名、状态与入口收口（2026-08-28）

## 审计结果

| 项 | cuda-foundations | triton-fused-ops |
|----|------------------|------------------|
| live 旧链接残留 | 无（P0-03 已替换，含 aicl-lab 复查） | 无 |
| README 首屏角色 | ✓ 系统性 CUDA 算子工程学习路径；badge 全部 canonical 链接 | ✓ Triton 融合算子 + torch.library；定位为 cuflash 独立参考实现 |
| 状态 | README **active**（"correctness fixes and teaching"）与 meta topics(active) 一致 | README **stable**（新功能暂停，维护正确性/兼容性/复现）与 meta topics(stable) 一致 |
| 安装/CI 命令 | cmake --preset default + ctest（README 所述） | python -m venv + pip install -e '.[dev]' + pytest |
| 实测验证 | 构建 exit 0；ctest 261/261 通过（RTX 3060，2026-08-28） | pytest 123 passed（19.43s，仓库 .venv） |

## stable 评估（cuda-foundations）

已满足 stable 条件：README 明确"不再新增模块；后续精力投入 tiny-llm 与 paged-serving"、
正确性维护中、261/261 测试稳定。**但当前 active 状态与 meta README 注册表/GitHub topics 三处一致**
（active），将状态改为 stable 需三处同步且 GitHub topics 写操作需授权 → **标记为待授权项**，
不单独改一处造成不一致。建议并入 P0-06 统一状态复核时处理。

## 结论

- 两仓不抢旗舰叙事 ✓；链接 canonical ✓；状态三处一致（当前值）✓；CI/安装命令实测可用 ✓
- 变更：无源码/文档修改（P0-03 已完成链接替换；本任务为验证与评估）
- 证据：runs/2026-08-28/SUP-01/（本文件）；实测命令输出（pytest 123 passed、ctest 261/261）

## 限制

- GitHub topics/description 未改（无写授权）；cuda-foundations 状态升级 stable 待授权三处同步
- 未 push