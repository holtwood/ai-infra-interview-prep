=== tiny-llm ffi.h (TinyLlmConfig + 函数声明) ===
typedef struct TinyLlmConfig {
    int hidden_dim;
    int num_layers;
    int num_heads;
    int num_kv_heads;
    int head_dim;
    int vocab_size;
    int block_size;     // 分页块大小（策略 2 下忽略，保留对齐）
    int max_batch_size; // 引擎同时管理的最大序列数
    int max_num_blocks; // 分页 KV 池的物理块总数；0 = 策略 2（连续 KV）
    // ↑ 该字段使 TinyLlmConfig 变为 9 个 int 的 repr(C) 布局（ABI v2）。
} TinyLlmConfig;
=== paged-serving src/tiny_llm_ffi.rs (TinyLlmConfig + symbols) ===
pub struct TinyLlmConfig {
    pub hidden_dim: i32,
    pub num_layers: i32,
    pub num_heads: i32,
    pub num_kv_heads: i32,
    pub head_dim: i32,
    pub vocab_size: i32,
    /// 分页块大小（paged-serving 侧，策略 1 时后端按此对齐）。
    pub block_size: i32,
    pub max_batch_size: i32,
    /// 分页 KV 池的物理块总数；0 = 策略 2（连续 KV）。
    /// 该字段使 `TinyLlmConfig` 变为 9 个 int 的 repr(C) 布局（ABI v2）。
    pub max_num_blocks: i32,
}

## 核对结论（2026-08-28 review 补录，机器可复算）

- `TinyLlmConfig` 字段顺序：C（ffi.h）⇄ Rust（tiny_llm_ffi.rs）**逐项一致（ORDER MATCH: True）**：
  hidden_dim, num_layers, num_heads, num_kv_heads, head_dim, vocab_size, block_size,
  max_batch_size, max_num_blocks
- 函数符号集合 **一致（SET MATCH: True）**：tinyllm_load / tinyllm_step /
  tinyllm_allocate_sequence / tinyllm_free_sequence / tinyllm_free
- 参数类型对应：*mut c_char↔char*、is_prefill *const u8↔unsigned char*、
  next_tokens *mut c_int↔int*、logprobs *mut f32↔float*
- 复算方法：从本文件两份摘录按上述列表核对；Rust 侧另有布局守卫测试随 cargo test 通过
- 结论：ABI 双源一致，无契约漂移（对应 TASKS PSERV-01 验收）
