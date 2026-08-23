#!/usr/bin/env python3
"""gen_zero_dim_gguf.py —— llama.cpp#26366 的最小 PoC 生成器

构造一个合法 GGUF 文件，其唯一张量带零维度（ne=[1,0]）。这是 issue #26366 的
历史最小复现器：旧实现的溢出预检会在 x86-64 上因 IDIV 除零触发 SIGFPE（rc=136），
而 arm64 行为不同。2026-08-23 的当前 master 已有 `ggml_nelements > 0` 守卫，
本文件应被正常接受；脚本现在用于回归验证，不再把当前 master 描述为必崩溃。

用法：
    python3 gen_zero_dim_gguf.py /tmp/zero_dim.gguf

验证（在 llama.cpp 构建后）：
    bin/llama-gguf /tmp/zero_dim.gguf r     # 当前 master 预期正常接受
    python3 -c "import gguf; r=gguf.GGUFReader('/tmp/zero_dim.gguf'); \
        print([(t.name, t.shape) for t in r.tensors])"   # gguf-py 正常接受

注意：只有在 issue 报告对应的旧 commit 上才预期 SIGFPE；本脚本只生成测试文件。
"""
import struct
import sys

MAGIC = b"GGUF"
VERSION = 3
GGML_TYPE_F32 = 0


def gguf_string(s: str) -> bytes:
    b = s.encode("utf-8")
    return struct.pack("<Q", len(b)) + b


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/zero_dim.gguf"
    buf = bytearray()
    # header: magic, version, tensor_count, metadata_kv_count
    buf += MAGIC
    buf += struct.pack("<I", VERSION)
    buf += struct.pack("<Q", 1)  # 1 tensor
    buf += struct.pack("<Q", 0)  # 0 metadata kv
    # tensor info: name, n_dims, dims, type, offset
    buf += gguf_string("t")
    buf += struct.pack("<I", 2)          # n_dims = 2
    buf += struct.pack("<Q", 1)          # ne[0] = 1
    buf += struct.pack("<Q", 0)          # ne[1] = 0  <- 触发点
    buf += struct.pack("<I", GGML_TYPE_F32)
    buf += struct.pack("<Q", 0)          # offset
    # 数据区起点按默认对齐 32 取整；文件必须延伸到该偏移，
    # 否则示例读取器在 "seek to data section" 处先行失败，
    # 到不了触发除法的代码路径（这正是原报告文件为 96 字节的原因）。
    data_offset = ((len(buf) + 31) // 32) * 32
    buf += b"\x00" * (data_offset - len(buf))
    with open(out, "wb") as f:
        f.write(buf)
    print(f"written {out} ({len(buf)} bytes, data offset {data_offset})")


if __name__ == "__main__":
    main()
