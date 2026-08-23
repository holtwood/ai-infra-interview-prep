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

24h：压测设计与执行 12h · 可观测性核验 2h · Linux perf/nsys 实验 4h · C++/算法 2h · 复盘 4h。

## 阅读范围

- paged-infer：HTTP/SSE 接口与现有日志
- Cerebras/Perplexity JD 的压测与可观测性要求（见 JOB_MARKET_EVIDENCE.md）
- Linux perf/火焰图教程 + lectures（Fork）相关讲义

## 动手实验

1. 使用仓库现有 serving harness：固定数据集、模型、commit、采样与输出上限，分别跑
   closed-loop 并发阶梯和 Poisson 到达率阶梯；每档 ≥5 次，直到触发 SLO 拐点或显存上限。
2. 真实 tiny-llm 后端报告 TTFT、TPOT、吞吐、失败率、token 计数覆盖率和峰值显存；
   CPU 参考后端只做协议 smoke，不进入性能结论。
3. 用 perf/火焰图定位 Rust/HTTP 热点，用 nsys 定位 GPU 时间线；核验 Prometheus 指标与
   `summary.json` 是否一致，不为了“看起来完整”重复加指标。

## 可验证交付物

- [ ] 压测报告：并发/到达率-吞吐-尾延迟曲线 + 容量拐点（含原始 `summary.json`）
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
