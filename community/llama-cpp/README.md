# llama.cpp GGUF 健壮性练习

- [`gguf-overflow-validation.md`](gguf-overflow-validation.md)：#26366 与 #26978/#26979
  的调查、实测输出、评论草稿和边界说明。
- `gen_zero_dim_gguf.py`：零维度张量历史回归文件生成器。
- `gen_pad_wrap_gguf.py`：`GGML_PAD` 整数回绕最小文件生成器。

这些文件证明“读 issue → 当前主分支复现 → 验证候选修复 → 审计自己的实现”的过程。
它们不代表已经向上游发布评论或获得合入；发布后应在调查记录中补上真实上游链接。
