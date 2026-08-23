# PR #26979 最终评论（可直接粘贴发布）

发布位置：https://github.com/ggml-org/llama.cpp/pull/26979
状态核验（2026-08-24）：PR 仍 OPEN、head 仍 264618b、master 未合入修复——评论内容全部有效。
以下正文从分隔线之间整体复制即可（已填好环境信息，第一人称）。

---

Independently verified this on x86-64 (WSL2, Ubuntu 24.04, AMD Ryzen 7 5800H,
g++ 13.3.0, CPU-only build: `-DGGML_CUDA=OFF -DLLAMA_BUILD_EXAMPLES=ON`).

On current master, the crafted file (F32 tensor, `ne = [4, 1073741823,
1073741825, 1]`, declared nbytes = 2^64 − 16) is accepted by the parser and
crashes downstream with SIGSEGV (rc=139) — the wrapped `padded_size` of 0
passes the `SIZE_MAX` guard, so the size accounting no longer reflects the
declared extent.

On this branch (264618b) the same file is rejected at parse time:

```
gguf_init_from_reader: tensor 'b' size 18446744073709551600 overflows after padding (alignment 32)
```

Also checked that the guard does not disturb the zero-element case from
#26366: a tensor with `ne = [1, 0]` still loads fine (size 0, n_elts 0) on
this branch.

For what it's worth, I audited my own small GGUF reader against this bug
family and found/fixed two adjacent issues there (unbounded `n_dims` →
bad_alloc abort; unchecked `data_offset + tensor.offset` addition → 64-bit
wrap and silent garbage reads), which suggests this class of overflow is
easy to miss in hand-written readers — glad to see it hardened here.

<details>
<summary>Minimal PoC generator (96-byte file)</summary>

```python
import struct
buf  = b"GGUF" + struct.pack("<I", 3) + struct.pack("<Q", 1) + struct.pack("<Q", 0)
buf += struct.pack("<Q", 1) + b"b"                      # tensor name
buf += struct.pack("<I", 3)                             # n_dims
buf += struct.pack("<Q", 4) + struct.pack("<Q", 1073741823) + struct.pack("<Q", 1073741825)
buf += struct.pack("<I", 0) + struct.pack("<Q", 0)      # F32, offset 0
buf += b"\x00" * ((((len(buf) + 31) // 32) * 32) - len(buf))  # pad to data offset
open("pad_wrap.gguf", "wb").write(buf)
```

`bin/llama-gguf pad_wrap.gguf r` → SIGSEGV on master, clean rejection on this branch.
</details>

---

## 发布后记录（回填到 community/README.md 的参与证据）

- 评论链接：【发布后填】
- 若维护者回应，24h 内跟进；若被要求改措辞/补材料，优先响应
- 不要在 #26366 与 #26978 issue 本体重复评论（PR 评论已覆盖）
