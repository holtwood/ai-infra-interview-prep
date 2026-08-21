---
week: 9
title: NCCL、并行策略、通信/计算重叠
start: 2026-10-19
end: 2026-10-25
hours: 24
status: upcoming
---

# 第 9 周：NCCL、并行策略、通信/计算重叠

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡

## 本周目标

分布式推理的**理论** mastery。本机单卡，无多 GPU 实验条件——一切产出必须标注
"理论学习/模拟"，不得伪造实验数据。

## 先修知识

矩阵分块乘法；W7 的系统观。

## 时间预算

24h：理论 10h · 源码/论文研读 6h · 单机模拟 4h · C++/算法 2h · 复盘 2h。

## 阅读范围

- NCCL 文档（collectives、topology、ring/tree 算法）
- Fork ompi（P3）：只看通信抽象层（选读）
- TensorRT-LLM（P2，"五个一"）：TP 相关文档与 benchmark 目录
- 论文：Megatron-LM（TP 划分）、sequence parallelism 综述

## 动手实验

1. 单机模拟：在 CPU/单 GPU 上模拟 TP 的通信量计算（每层 2 次集合通信的公式推导）。
2. 用小脚本演示 ring AllReduce 的步骤分解（时间步 × 数据块表）。
3. 推导并验证：TP 对小 batch 不友好的原因（通信占比公式）。

## 可验证交付物

- [ ] 并行策略对比笔记（TP/PP/SP/DP：通信量、显存、适用 batch）
- [ ] ring AllReduce 带宽公式推导
- [ ] INTERVIEW_MATRIX Q6 达 B 级（明确声明理论级）

## 面试问题

- ring AllReduce 总数据量公式（2(n-1)/n × size）？
- TP 每层哪两次通信？怎么与计算重叠？
- NVLink vs PCIe 带宽差对重叠收益的影响？

## 退出条件

公式推导与策略对比能白板完成，且口头明确"单卡环境，以下为理论结论"。

## 未完成时

模拟实验可砍；公式推导与策略对比不可降级。
