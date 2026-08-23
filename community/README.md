# 上游社区参与

这里保存参与上游前的筛选工具、最小复现和调查记录；最终贡献证据以上游 issue、PR、
review 与合入 commit 为准。

- `issue_scout.sh`：按标签、关键词与讨论热度筛选候选 issue。
- `llama-cpp/`：GGUF 整数溢出问题的本地复现器和独立验证记录。

执行纪律：先读贡献指南和现有讨论，再在当前主分支复现；每次只认领一个可在 1–3 天内
闭环的问题。没有新增证据时不评论，不用批量评论换曝光。

## 贡献主线

按与现有证据的距离排序，而不是按仓库 star 数排序：

1. **llama.cpp**：GGUF/parser、量化与 CPU/CUDA 正确性；适合复用 tiny-llm 的字节级
   fixture、差分测试和 sanitizer 经验。
2. **vLLM / GuideLLM**：benchmark、指标、OpenAI 协议、scheduler 回归；适合复用
   paged-infer 的 loadgen、SSE 和 summary 经验。
3. **FlashInfer**：attention、sampling、量化 kernel 的正确性矩阵与性能回归；先贡献
   最小复现/测试，再碰需要新架构硬件的大 kernel。
4. **SGLang**：先用 Mini-SGLang 理解 runtime，再选 scheduler/KV/metrics 小问题；
   不同时追 vLLM 与 SGLang 两条大仓主线。

每周只分配 2–4 小时社区时段。一个 issue 评分达到 6 分才投入：当前硬件可复现 +2、
与现有项目同一调用链 +2、能增加回归测试 +2、维护者已确认 +1、无活跃 PR +1、
预计 1–3 天闭环 +1。硬件不匹配或已有活跃 PR 时直接换题。

## 评论与 PR 证据格式

issue 评论只包含维护者可用的新信息：

1. 当前 main/commit、完整环境与最小命令；
2. expected / actual、稳定复现率和最小输入；
3. 首个坏 commit 或代码路径（若已定位）；
4. raw log、测试或小型 fixture；
5. 明确说明愿意提交哪一个有限范围的修复。

不要在无复现时发“我也遇到”、不要粘贴 AI 生成的大段猜测、不要同时认领多个问题。
内推是持续高质量协作的副产品；至少有合入 PR 或多次有效 review 后再自然建立联系，
不在首次互动中直接索要内推。
