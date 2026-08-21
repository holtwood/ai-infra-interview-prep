---
week: 5
title: Transformer 推理、量化、模型加载
start: 2026-09-21
end: 2026-09-27
hours: 24
status: upcoming
---

# 第 5 周：Transformer 推理、量化、模型加载

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡

## 本周目标

把 tiny-llm 的主调用链（GGUF 加载 → 量化反量化 → decode 循环）讲成白板图。

## 先修知识

Transformer 结构；W3 的 attention。

## 时间预算

24h：tiny-llm 代码重读 8h · 量化实验 6h · 白板图+讲解 4h · C++/算法 2h · 复盘 4h。

## 阅读范围

- open-infra-ai/tiny-llm：权重加载、W8A16、decode 主循环（主线）
- Fork nano-vllm（P1）：对照极简实现的主链路
- Fork minGPT（P3）：仅看 Transformer block 结构（如需补基础）
- PagedAttention 论文（SOSP'23）第一遍通读

## 动手实验

1. 重跑 tiny-llm W8A16 benchmark，复现 TPOT ≈ 6.1 ms/token，记录完整口径（模型、prompt、硬件、命令）。
2. 对比 int8 权重 vs fp16 权重的显存占用与逐 token 输出差异。
3. 画主调用链时序图（加载/预热/单步 decode）。

## 可验证交付物

- [ ] tiny-llm 主调用链白板图 + 讲解文档
- [ ] 量化实验记录（误差与收益）
- [ ] INTERVIEW_MATRIX Q4 达 B 级以上

## 面试问题

- per-channel scale 为什么比 per-tensor 误差小？
- dequant 放在 kernel 内外各有什么代价？
- GGUF 里除了权重还存什么（metadata、rope 参数）？

## 退出条件

白板图能徒手画出；TPOT 数字可复现。

## 未完成时

nano-vllm 对照可砍；tiny-llm 主链路不可降级。
