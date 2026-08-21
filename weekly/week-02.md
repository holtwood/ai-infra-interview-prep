---
week: 2
title: GEMM、访存、Tiling、共享内存、WMMA
start: 2026-08-31
end: 2026-09-06
hours: 24
status: upcoming
---

# 第 2 周：GEMM、访存、Tiling、共享内存、WMMA

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡

## 本周目标

把 SGEMM 优化阶梯讲成"每步解决什么瓶颈"的故事，并配上 Nsight Compute 量化证据。

## 先修知识

W1 的 CUDA 线程/内存层次；roofline 概念。

## 时间预算

24h：理论+重读代码 8h · Nsight 实验 8h · C++/算法 2h · 证据整理 4h · 复盘 2h。
18h：实验只做 3 个代表性阶梯。12h：只做阶梯讲解 + 1 次 ncu。

## 阅读范围

- open-infra-ai/cuda-foundations：SGEMM 全部阶梯（主线）
- Fork siboehm/SGEMM_CUDA（已中文化）：对照第 5/6/7 步
- lectures（Fork）：memory coalescing、bank conflict 相关讲义
- cuda-samples（Fork）：仅 matrixMul、transpose 两个示例

## 动手实验

1. 用 ncu 对 naive → tiling → WMMA 三个版本各采一次：SOL、DRAM 吞吐、occupancy、warp stall 原因。
2. 人为制造一次 bank conflict（去掉 padding），观察差距，再修复。
3. 画本机 roofline，标出各版本位置。

## 可验证交付物

- [ ] 优化阶梯讲解文档（含每步的 roofline 移动方向）
- [ ] ncu 报告（版本、命令、硬件口径齐全）
- [ ] INTERVIEW_MATRIX Q2 达到 B 级以上

## 面试问题

- Bank conflict 如何产生、如何消除（padding/swizzle）？
- Occupancy 与寄存器压力的权衡？
- 为什么要 vectorize load？与合并访存的关系？

## 退出条件

能不看笔记把阶梯讲清楚，且每个数字能溯源到 ncu 报告。

## 未完成时

WMMA 深挖可顺延至 W3；ncu 报告为硬交付，不可降级。
