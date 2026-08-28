# PSERV-01 固化双仓集成基线（2026-08-28）

## 基线（binding）

- tiny-llm@f9d4b99fd6（master，工作树含 P0-03/P0-04 未提交改动）；libtiny_llm.a（2663344 B）+ _deps/spdlog-build/libspdlog.a，构建于 2026-08-28 12:35（-DCMAKE_CUDA_ARCHITECTURES=86）
- paged-serving（本地目录 paged-infer）@080f26f9，crate 0.2.0；`cargo build --features tiny-llm` exit 0
- 模型：models/qwen2.5-0.5b-instruct-q4_k_m.gguf（sha256 74a4da8c…）；models/tokenizer.json
- 硬件：RTX 3060 Laptop 6GB（sm_86），driver 610.57.01；nvcc 12.0.140

## 1. ABI 双源核对（静态）

- `TinyLlmConfig`：C 9×int ⇄ Rust 9×i32，字段顺序逐项一致（ORDER MATCH: True）：
  hidden_dim, num_layers, num_heads, num_kv_heads, head_dim, vocab_size, block_size, max_batch_size, max_num_blocks
- 函数符号集合一致（5/5）：tinyllm_load / tinyllm_step / tinyllm_allocate_sequence / tinyllm_free_sequence / tinyllm_free
- 参数类型对应：*mut c_char↔char*、is_prefill *const u8↔unsigned char*、next_tokens *mut c_int↔int*、logprobs *mut f32↔float*
- Rust 布局守卫测试随 cargo test 通过（P0-04 记录 215 passed）
- 无契约漂移，不需要 breaking task

## 2. 真实后端 e2e（cargo test --features tiny-llm）

```
TINY_LLM_DIR=…/tiny-llm/build TINY_LLM_MODEL=…/models/*.gguf PSERV_TOKENIZER_JSON=…/models/tokenizer.json \
cargo test --features tiny-llm --test tiny_llm_text_e2e
=> 3 passed; 0 failed（29.07s）：
  qwen2_chat_prompt_matches_llama_cpp
  qwen2_text_generation_end_to_end
  qwen2_three_concurrent_paged_requests_match_llama_cpp
```
模型配置日志：hidden_dim=896, num_layers=24, num_heads=14, num_kv_heads=2, vocab_size=151936（Qwen2.5-0.5B GQA）

## 3. HTTP server smoke（paged-serving -c config --serve，端口 3010）

- 启动：healthz `{"status":"ok"}`、readyz `{"status":"ready"}`（约 5s 内就绪）
- 单请求 SSE：data 流式 × N + usage{prompt_tokens:7,completion_tokens:32} + `data: [DONE]`，exit 0
- 多请求并发：2 流式（max_tokens=128）+ 1 非流式（max_tokens=16），全部 [DONE]/finish_reason=length，exit 0
- 取消：512-token 流式请求 3s 后 kill 客户端（exit 143），server 仍 healthz OK，后续新请求正常（cmpl-6）
- shutdown：SIGTERM 后 ~2s 进程干净退出（无 panic），端口释放（connection refused）
- 配置注意：max_batch_size <= max_num_seqs 校验；--config 不能与单项参数混用；HF tokenizer 需 kind=hugging_face

## 限制

- 取消语义的深度验证（KV 回收、队列移除）属 PSERV-05；本任务只验证取消后系统健康
- chokepoint：HTTP 层使用 config.serving 端口 3010（非默认 3000）
- 未 push、未跑远端 CI；GPU 常驻显存参考 TLLM-01 bench（resident_delta 3368MB，cudaMemGetInfo 差值口径）

## 证据（runs/2026-08-28/PSERV-01/）

- 00 本文件、01 server.log、02_single_request_sse.txt、03_multi_{a,b,c}、04_cancel.txt、05_abi_dualsource.md、config.smoke.json、server.pid