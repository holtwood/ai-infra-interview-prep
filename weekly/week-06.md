---
week: 6
title: KV Cache、Decode、CUDA Graph、性能指标
start: 2026-09-28
end: 2026-10-04
hours: 24
status: upcoming
---

# 第 6 周：KV Cache、Decode、CUDA Graph、性能指标

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡

## 本周目标

建立推理性能指标体系（TTFT/TPOT/吞吐/显存/尾延迟），在 current HEAD 上重跑
CUDA Graph 可归因对照实验。

## 先修知识

W5 的 decode 循环。

## 时间预算

24h：指标体系+测量实验 8h · CUDA Graph 实验 6h · KV Cache 策略复述 4h · C++/算法 2h · 复盘+SKILL_MATRIX 中期重评 4h。

## 阅读范围

- open-infra-ai/tiny-llm：分页 KV（策略 1）实现与差分测试
- Fork vllm（P2，"五个一"）：只读 metrics 定义与 benchmark 脚本目录
- 论文：vLLM / PagedAttention（SOSP'23）第二遍（KV 管理部分精读）

## 动手实验

1. 在 tiny-llm 上测量：序列长度 vs TPOT 曲线、KV 显存占用曲线。
2. CUDA Graph 实验：同一 commit、模型、prompt 与输出长度下做 on/off ≥5 次 A/B，
   用 nsys 时间线确认差异来自 launch 开销，而不只比较一个总耗时。
3. 用统一口径计算并记录 TTFT（首次 token）与稳态 TPOT。

## 可验证交付物

- [ ] 指标报告：TTFT/TPOT/吞吐/显存，全部带口径
- [ ] CUDA Graph current HEAD A/B 记录（原始输出 + nsys 时间线）
- [ ] SKILL_MATRIX 中期重评（附证据）
- [ ] INTERVIEW_MATRIX Q4 补量化数字口径

## 面试问题

- TTFT 与 TPOT 分别由什么主导？
- CUDA Graph 能加速 decode 的根本原因（launch 开销占比）？
- KV Cache 显存公式（layers × 2 × seq × head_dim × dtype）？

## 退出条件

指标报告数字可复现；公式能徒手推导。

## 未完成时

CUDA Graph 实验可降级为"捕获成功+定性结论"；指标报告不可降级。
