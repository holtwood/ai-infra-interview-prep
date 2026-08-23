# llama.cpp GGUF 健壮性参与包（已本地验证版，2026-08-23）

> 状态：两个 issue 的本地复现与验证**已完成**。发布前只需按「发布清单」走最后一步。
> 所有命令在 RTX 3060 Laptop / WSL2 / x86-64 上实测。
> 上游实时状态核验（2026-08-23）：[#26366](https://github.com/ggml-org/llama.cpp/issues/26366)
> 仍为 open，但当前 master 已不再复现；[#26978](https://github.com/ggml-org/llama.cpp/issues/26978)
> 与修复 [PR #26979](https://github.com/ggml-org/llama.cpp/pull/26979) 均为 open。

## 一、调查结论（2026-08-23 实测）

| Issue | 问题 | 当前 master 状态 | 你的机会 |
|-------|------|------------------|----------|
| [#26366](https://github.com/ggml-org/llama.cpp/issues/26366) | 零维度张量 → 除法除零 SIGFPE | **代码路径已修复、issue 仍 open**（`ggml_nelements > 0` 守卫） | 不重复刷评论；仅在维护者需要回归信息时补充 |
| [#26978](https://github.com/ggml-org/llama.cpp/issues/26978) | `GGML_PAD` 加法回绕 → 尺寸账本失真 → 越界读 | **仍存在**（守卫检查回绕后的 padded_size 而非 nbytes） | **PR #26979 开放中，已有本地独立验证** |

## 二、已完成的验证（全部有 rc/输出证据）

构建：`/tmp/llama.cpp`（master 浅克隆 + PR fork 分支），`-DLLAMA_BUILD_EXAMPLES=ON -DGGML_CUDA=OFF`，target `llama-gguf`。

**master（2026-08-23 当日 HEAD）上复现 #26978**：
```
$ python3 gen_pad_wrap_gguf.py /tmp/pad_wrap.gguf
written /tmp/pad_wrap.gguf (96 bytes); declared tensor nbytes = 18446744073709551600 (= 2^64 - 16)
$ bin/llama-gguf /tmp/pad_wrap.gguf r
rc=139   # SIGSEGV——解析器接受了回绕尺寸，下游越界读崩溃
```

**PR #26979 分支（x14ngch3n:gguf-pad-wrap-guard，commit 264618b）上验证修复**：
```
$ bin/llama-gguf /tmp/pad_wrap.gguf r
gguf_init_from_reader: tensor 'b' size 18446744073709551600 overflows after padding (alignment 32)
gguf_ex_read_0: failed to load '/tmp/pad_wrap.gguf'   # 解析期优雅拒绝，不再段错误
```

**回归检查（修复不破坏 #26366 的零维度场景）**：
```
$ bin/llama-gguf /tmp/zero_dim.gguf r
gguf_ex_read_0: tensor[0]: name = t, size = 0, offset = 0   # 零维度张量仍正常接受
```

**跨实现佐证（你自己的 tiny-llm，commit e37cd06）**：
- 零维度文件：`tiny_llm_demo --inspect` 正常显示 `1x0` 张量，无崩溃（rc=0）
- 同族审计修复了两个隐患：n_dims 无上界（恶意值 → ~32GB 分配 → bad_alloc abort）、
  `data_offset + tensor.offset` 无溢出检查（64 位回绕 → 静默读垃圾）

## 三、发布清单

1. 在 PR #26979 下评论（英文草稿见下，第一人称改写，填你的环境）
2. 不要同时去 #26366 刷屏（已修）；#26978 issue 本体可不评（PR 评论足够）
3. 若想再进一步：把 `gen_pad_wrap_gguf.py` 附在评论里（或 gist），
   让维护者一行命令复现——这是验证类评论的最高规格

## 四、PR 评论草稿（英文）

Independently verified this on x86-64 (WSL2, `<CPU/OS/compiler 待填>`).

On current master, the crafted file (F32 tensor, `ne = [4, 1073741823,
1073741825, 1]`, declared nbytes = 2^64 − 16) is accepted by the parser and
crashes downstream with SIGSEGV (rc=139) — the wrapped `padded_size` of 0
passes the `SIZE_MAX` guard, so the size accounting no longer reflects the
declared extent.

On this branch (264618b) the same file is rejected at parse time:

    gguf_init_from_reader: tensor 'b' size 18446744073709551600 overflows after padding (alignment 32)

Also checked that the guard does not disturb the zero-element case from
#26366: a tensor with `ne = [1, 0]` still loads fine (size 0, n_elts 0) on
this branch.

For what it's worth, I audited my own small GGUF reader against this bug
family and found/fixed two adjacent issues there (unbounded `n_dims` →
bad_alloc abort; unchecked `data_offset + tensor.offset` addition → 64-bit
wrap and silent garbage reads), which suggests this class of overflow is
easy to miss in hand-written readers — glad to see it hardened here.

## 五、为什么这次参与有价值（面试叙事）

完整闭环故事，每一步都有证据：
1. 用 `issue_scout.sh` 筛选出与自身技能对口的 issue（GGUF 解析——你写过）
2. 独立复现：master SIGSEGV rc=139（PoC 生成器自己写）
3. 发现 #26366 已被修、#26978 仍活——**没有盲目评论，而是重新定位到 PR 验证**
4. 双向验证修复（拒绝恶意文件 + 不误伤零维度回归）
5. 审计自己的实现，修掉同族两个 bug（tiny-llm e37cd06 当时 192 测试全绿；
   2026-08-23 当前套件为 193 项）
6. 向上游提交验证报告

这个故事讲的是「如何专业地参与开源」：不刷存在感、不重复劳动、
用可复现证据说话——正是维护者愿意内推的人。
