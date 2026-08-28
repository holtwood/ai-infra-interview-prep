# 云部署 bundle 修复与本地审计（2026-08-28）

> 本轮无云操作：未启动实例、未安装云 CLI、未读取/打印凭证；费用 $0。

## 1. bundle 产物（hash 权威清单）

- tar.gz：`/tmp/opencode/cloud-bundle-20260828-155733.tar.gz`（458M）
- 权威 manifest：`/tmp/opencode/cloud-bundle-20260828-155733.tar.gz.manifest.json`
- bundle_sha256 = `2445a4eadf4c2426aae70bb0bea08f08b7b38cbe68b321f8d6e2315f859a6485`（实测 sha256sum 与 manifest 记录一致，已校验）

## 2. 解压后实际路径（真实解压 dry-run，非 bash -n）

解压到 `/tmp/opencode/workspace-final/`（等价 `/workspace/` 扁平布局）：

```
00_run_all.sh            01_pack_local.sh         02_build_canary.sh
03_formal_matrix.sh      04_download.sh           VERSIONS.txt
manifest.json            src/cuflash/CMakeLists.txt   src/tiny-llm/CMakeLists.txt
models/qwen2.5-0.5b-instruct-q4_k_m.gguf           models/tokenizer.json
```

11 项关键路径全部存在；src 内无 `.git`/`.zcode`/`*.gguf`/`build`（排除校验通过）；
5 个脚本解压后可执行、`bash -n` 全过、`shellcheck -S warning` 全 CLEAN。

## 3. VERSIONS.txt / manifest.json 记录

- cuflash_commit=599836b…（== origin/master，tracked-dirty=0）
- tiny_llm_commit=d2838f3…（== origin/master，tracked-dirty=0）
- gguf_sha256=74a4da8c…；tokenizer_sha256=c0382117…
- bundle_sha256=2445a4ea…；pack_time=2026-08-28T07:57:33Z

## 4. benchmark 口径（03_formal_matrix.sh）

- cuflash：`--benchmark_filter` **显式含 `BM_Decode_FP16/(1024|4096|16384)/64/manual_time`**（FlashDecoding 覆盖，bench_flash_attention.cu:651/704 实测存在）；`--benchmark_repetitions=10` 且**不用 aggregates_only**（保留逐次 raw，3 个独立进程 → 30 样本/配置，python 汇总 p50/p95/mean 到 cuf_summary.json）
- tiny-llm：graph on/off × short/long 各自独立进程（warmup 3 + iters 10）；每个配置独立 stdout/stderr，失败配置在 STEPS.log 记录 rc 与 stderr 尾部
- 任一正式矩阵失败 → `STATUS.json`（overall=FAILURE + 每步 detail）且脚本 `exit 1`，不静默成功；canary 失败（02）同样写 STATUS.json 并退出
- metadata.json（03 第 0 步）：git 说明、nvidia-smi GPU/driver、CUDA、CPU/RAM、容器 digest（RUNPOD_IMAGE/cgroup）、模型与 tokenizer 身份、实验命令与时间
- 显存纪律：只报常驻差值（cudaMemGetInfo 起止），不称峰值；ncu/nsys 不可用时记录 ERR_NVGPUCTRPERM/缺工具为环境限制，不伪装完成

## 5. 04_download.sh 安全

显式 `INSTANCE_USER`（默认 root）/`INSTANCE_PORT`（默认 22）/`INSTANCE_KEY` 参数；
host key 校验 `StrictHostKeyChecking=accept-new + UserKnownHostsFile`；密钥仅作 `-i`，从不打印/回显。

## 6. 无 rm -rf

全部 5 个脚本经 `rg 'rm -rf|rm -fr'` 检查为 0；打包用时间戳唯一临时目录。

## 7. 文档指针更新

- PLAN.md §2.1 表格：本地目录迁移完成（cuflash/、paged-serving/ + remote 已 canonical），旧目录名仅存于历史执行记录（不改写）
- PROMPT.md §4.2：本地 checkout 已迁移，指向 P0-03M 记录
- TASKS.md：P0-03/P0-03M 均 done；活动 todo/blocked 任务无旧目录名引用（剩余旧名命中均为 P0-02 任务定义与其执行记录，属语义/历史内容，保留）

## 8. 校验结果

- `bash -n` 5 脚本全过；`shellcheck -S warning` 5 脚本全 CLEAN
- bundle 解压 dry-run：11 路径全存在、sha 匹配、排除校验通过
- 7 仓 `git diff --check` 全 OK（无新增源码改动）
- `make check`（66 文件链接）与 `make verify`（288h/100%）exit 0

## 9. 未完成项 / 待授权

- TLLM-06、CUF-02：**仍 blocked**（部署包已备，缺云凭证/实例）
- `paged-servingence-system` 6 处 doc 注释（src/kv_cache.rs×4、gpu_executor.rs×1、tokenizer.rs×1）与 FFI 注释旧名：**本轮不修**，待授权（记录于 runs/2026-08-28/CORRECTION/00_paged-servingence-followup.md）
- PSERV-04：未执行（流式 F1 未解决，明确排除）

## 10. 费用

**未启动实例、费用 $0**；无待清理资源、无云 CLI 安装。