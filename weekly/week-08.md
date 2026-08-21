---
week: 8
title: HTTP/SSE、压测、可观测性、Linux 调优
start: 2026-10-12
end: 2026-10-18
hours: 24
status: upcoming
---

# 第 8 周：HTTP/SSE、压测、可观测性、Linux 调优

## 相关文档

- [INTERVIEW_MATRIX](../INTERVIEW_MATRIX.md) — 本周面试题加入矩阵
- [SKILL_MATRIX](../SKILL_MATRIX.md) — 能力自评与证据
- [knowledge-map](../knowledge-map.md) — 主题知识地图
- [progress-tracker](../progress-tracker.md) — 进度打卡

## 本周目标

给 paged-infer 产出第一份系统压测报告（这是 Serving 方向最大证据缺口）。

## 先修知识

W7 的调度；Linux 基础。

## 时间预算

24h：压测设计与执行 10h · 可观测性改造 4h · Linux perf 实验 4h · C++/算法 2h · 复盘 4h。

## 阅读范围

- paged-infer：HTTP/SSE 接口与现有日志
- Cerebras/Perplexity JD 的压测与可观测性要求（见 JOB_MARKET_EVIDENCE.md）
- Linux perf/火焰图教程 + lectures（Fork）相关讲义

## 动手实验

1. 压测设计：固定 prompt 长度 × 并发数矩阵（1/2/4/8/16），测 TTFT 分布、TPOT、吞吐、p50/p99。
2. 用 perf + 火焰图定位 paged-infer 服务端热点（本机可做）。
3. 加最小可观测性：请求级耗时日志与 Prometheus 风格计数器（只加指标，不加新功能）。

## 可验证交付物

- [ ] 压测报告：并发-吞吐-延迟曲线 + 容量拐点分析（口径齐全）
- [ ] 火焰图 + 热点分析
- [ ] INTERVIEW_MATRIX Q5 达 B 级以上

## 面试问题

- 怎么压尾延迟（batch 上限、chunked prefill、抢占、CUDA Graph）？
- 容量规划怎么做？
- warmup 与测量统计口径的坑？

## 退出条件

压测报告可复现（脚本入库或命令记录）。

## 未完成时

可观测性改造可降级为日志；压测报告不可降级。
