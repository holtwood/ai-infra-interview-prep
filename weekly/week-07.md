---
week: 7
title: Paged KV、Continuous Batching、调度
start: 2026-10-05
end: 2026-10-11
hours: 24
status: upcoming
---

# 第 7 周：Paged KV、Continuous Batching、调度

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡

## 本周目标

把 paged-serving 的调度器状态机与不变量讲清楚，形成"推理系统设计"的完整叙事。

## 先修知识

W5–W6。

## 时间预算

24h：paged-serving 代码重读 8h · 状态机/不变量文档 6h · 对照阅读 4h · C++/算法 2h · 复盘 4h。

## 阅读范围

- open-infra-ai/paged-serving（主线）：block 分配器、调度循环、HTTP 控制面
- Fork mini-sglang（P1）：对照调度主循环
- Fork vllm（P2，"五个一"）：core scheduler 与 block manager
- Fork sglang（P2，"五个一"）：scheduler 与 router

## 动手实验

1. 整理状态机图：请求生命周期（waiting→running→preempted→finished）与迁移条件。
2. 写出分配器不变量清单（如"引用计数=使用该 block 的请求数"），逐条对应代码。
3. 复跑 3 并发 e2e 对齐实验，复述量化差异的诚实记录方式。

## 可验证交付物

- [ ] 状态机图 + 不变量清单（代码行级定位）
- [ ] INTERVIEW_MATRIX Q3 达 B 级以上
- [ ] vllm + sglang 的"五个一"产出

## 面试问题

- 抢占式调度 recompute vs swap 的取舍？
- copy-on-write 前缀共享怎么实现？
- block size 怎么选（碎片 vs 元数据开销）？

## 退出条件

状态机图能徒手画出并能答两层追问。

## 未完成时

sglang"五个一"可砍；vllm 与状态机文档不可降级。
