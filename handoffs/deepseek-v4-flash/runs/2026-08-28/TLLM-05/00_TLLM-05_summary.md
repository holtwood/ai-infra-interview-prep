# TLLM-05 Runtime 失败路径矩阵（2026-08-28）

## 可复现脚本矩阵（tiny_llm_demo，本机实测）

| 场景 | 命令 | exit | 错误消息（可诊断性） |
|------|------|:----:|------|
| 文件不存在 | demo /nonexistent/xxx.gguf --prompt "hi" | 1 | `GGUF parse failed: Failed to open file: /nonexistent/xxx.gguf` |
| 空文件 | demo empty.gguf --prompt "hi" | 1 | `GGUF parse failed: Failed to read GGUF header` |
| 截断 GGUF（metadata 区，1KB） | demo truncated.gguf --prompt "hi" | 1 | `Failed to read metadata value for key: tokenizer.ggml.tokens: Array too large: 151936` |
| 截断 GGUF（tensor 数据区，100MB） | demo truncated_tensors.gguf --prompt "hi" | 1 | `Failed to load GGUF model: token embedding: Failed to read tensor data`（定位到具体 tensor） |
| 随机字节文件 | demo random.gguf --prompt "hi" | 1 | `Invalid GGUF magic number. Expected 0x1179993927, got 0x2062531900` |
| 文本文件冒充 GGUF | demo notgguf.gguf --prompt "hi" | 1 | `Invalid GGUF magic number. Expected 0x1179993927, got 0x1936287860` |

全部：exit 1 + 明确可定位错误；无崩溃、无静默成功、无环境敏感信息泄露（路径仅文件名）。

## 已有测试覆盖（TLLM-01 ctest 193/193 已实测通过）

- C ABI 非法参数：`FFITest.InvalidArgsReturnError`（否决负 logprobs_k、空缓冲区契约等）
- GGUF 解析防御：`GGUFParser.RejectsVersion1 / RejectsNestedArray / RejectsExcessiveTensorDims / RejectsTensorOffsetOverflow`（TLLM-01 前 GGUF 健壮性加固对应 CHANGELOG Unreleased：n_dims 上限 GGML_MAX_DIMS、offset 溢出检查）
- 缺失文件：`InferenceEngineTest.GGUFLoadFailsOnMissingFile`
- 无 CUDA 设备：`cudaErrorNoDevice` 时 GPU 测试跳过而非误判（CHANGELOG 已记录；本机有设备，无法实测该分支，如实标注）

## 未覆盖（如实记录）

- 不支持量化/架构：工作区仅有 Qwen2.5 Q4_K_M 单一模型文件，无法构造其他量化/架构的失败输入；由 GGUFParser 校验路径与 tests 覆盖，不编造结果
- tokenizer 资源缺失：GGUF 内嵌 metadata 缺失时已在"截断 GGUF"场景实测（Array too large 路径）

## 变更

无源码改动（全部为已有代码行为的复现取证）；证据：runs/2026-08-28/TLLM-05/{s1..s6_*.log}

## 限制

- 本机缺少多量化/多架构模型，部分场景用测试覆盖说明；未 push