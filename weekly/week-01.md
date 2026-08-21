---
week: 1
title: 基线评估、CUDA 模型、环境与性能工具
start: 2026-08-24
end: 2026-08-30
hours: 24
status: upcoming
---

# 第 1 周：基线评估、CUDA 模型、环境与性能工具

> 📅 2026-08-24 ～ 2026-08-30

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡
- [BASELINE](../BASELINE.md) — 能力基线
- [study-plan](../study-plan.md) — 每周节奏

## 本周目标

建立可信的能力基线；复习 CUDA 编程模型；跑通 profiling 工具链，产出第一个可复现基准。

## 先修知识

C++、基本 GPU 概念。不需要读完任何大仓源码。

## 时间预算

24h 基准：CUDA/工具 12h · 实验与记录 6h · C++/算法维持 2h · 计划与复盘 4h。
18h 档：实验减半，砍"拓展实验"。12h 档：只做 CUDA 问答 + 一个基准。

## 阅读范围

- open-infra-ai/cuda-foundations 的 SGEMM 阶梯（自己已有仓，快速重激活）
- cuda-samples（Fork）：仅 `0_Introduction`（vectorAdd、deviceQuery、asyncAPI）
- gpu-mode/lectures（Fork）：性能分析相关讲义
- CUDA C++ Programming Guide 第 1–3 章（概念）

## 动手实验

1. `deviceQuery` 记录 RTX 3060 Laptop 6GB 的 SM 数、时钟、带宽规格。
2. 重跑 cuda-foundations 的 SGEMM naive vs 最优版，记录数字。
3. 安装并跑通 Nsight Systems + Nsight Compute 各一次（对 vectorAdd / naive SGEMM）。

## 可验证交付物

- [ ] SKILL_MATRIX.md 完成首次自评（附证据链接）
- [ ] 一页 CUDA 问答（线程层次、内存层次、warp、同步）——INTERVIEW_MATRIX 格式
- [ ] 基准记录：硬件、驱动/CUDA 版本、命令、结果（可复现）

## 面试问题

- Thread/Block/Grid/Warp 层次与硬件（SM）的对应关系？
- Global/Shared/Register/Constant 内存的延迟与用途？
- Stream 和 Event 是什么，如何重叠 kernel 与 memcpy？
- （加入 INTERVIEW_MATRIX.md 并写要点）

## 退出条件

三份交付物完成且基准数字可复现（重跑误差 < 1%）。

## 未完成时

基准实验优先；问答可顺延到 W2 周日；Nsight 可降级为"跑通一次"。
