# P0-01 不可变工作区与线上基线（2026-08-28 12:20 +08）

采集时间：2026-08-28 12:17–12:21 +08（GitHub API 时间戳 2026-08-28T04:18:46Z / 04:19:36Z）
采集方式：git CLI + gh CLI (2.97.0)，全程只读（仅 fetch 更新 remote-tracking，不 merge、不改 remote、不写工作树）。

## 本地 git 基线（/home/shane/github/open-infra-ai）

| 仓 | 本地目录 | 分支 | HEAD | upstream 同步 | remote URL | dirty/untracked |
|----|---------|------|------|----------------|------------|-----------------|
| meta `open-infra-ai` | open-infra-ai/ | master | 5e0f570 | **behind origin 5** | https://github.com/open-infra-ai/open-infra-ai.git | clean |
| org profile `.github` | .github/ | main | 366d407 | 同步 | https://github.com/open-infra-ai/.github.git | clean |
| tiny-llm | tiny-llm/ | master | f9d4b99 | 同步 | https://github.com/open-infra-ai/tiny-llm.git | `?? .zcode/`（用户内容，不动） |
| cuflash | cuflash-attn/（旧目录名） | master | d53a530 | 同步 | **https://github.com/open-infra-ai/cuflash-attn.git（旧 URL）** | clean |
| paged-serving | paged-infer/（旧目录名） | master | 080f26f | 同步 | **https://github.com/open-infra-ai/paged-infer.git（旧 URL）** | clean |
| triton-fused-ops | triton-fused-ops/ | master | 5764758 | 同步 | https://github.com/open-infra-ai/triton-fused-ops.git | clean |
| cuda-foundations | cuda-foundations/ | master | 28e070b | 同步 | https://github.com/open-infra-ai/cuda-foundations.git | clean |

## GitHub 线上状态（gh API）

- 仓库名全部 canonical：cuflash、paged-serving 已生效，`cuflash-attn`/`paged-infer` URL 重定向到新名。
- 默认分支：6 仓 master，`.github` 为 main。
- 最新 master push CI：tiny-llm **FAILURE**（run 33042427022, "fix(cuda): 适配 CUDA 13..."，19s，疑 clang-format 红灯）；paged-serving **FAILURE**（run 33051255489, "refactor(tests): PINF-* → PSERV-*"，43s，疑 rustfmt 红灯）；cuflash / triton-fused-ops / cuda-foundations 最新 GREEN；open-infra-ai / .github 无 CI run。
- Latest Release：cuflash v0.6.0 (2026-08-27)；paged-serving **v0.1.0**（有 v0.2.0 tag，Latest 未更新）；tiny-llm v2.0.1 (2026-04-21)；triton-fused-ops v2.0.1 (2026-08-23)；cuda-foundations v1.0.0 (2026-04-21)；open-infra-ai / .github 无 Release。
- GitHub Pages：tiny-llm / cuflash / paged-serving / cuda-foundations 有 Pages；open-infra-ai、.github、triton-fused-ops 无。
- topics：cuflash 含 `stable`；paged-serving 含 `active`；triton-fused-ops 含 `stable`；cuda-foundations 含 `active`；open-infra-ai = active,ai-infra,learning-path,portfolio；.github 无 topics。

## 工具链（本机）

- git 2.43.0；gh 2.97.0
- nvcc 12.0.140（旧；CI 用 11.8）
- driver 610.57.01 / CUDA UMD 13.3；GPU：NVIDIA GeForce RTX 3060 Laptop 6GB（6144MiB，采集时占用约 3.5GiB）
- cmake 3.28.3；gcc 13.3.0；make 4.3；rustc/cargo 1.90.0
- python3 3.12.3（system，**无 torch/triton**）
- conda env `triton-b4`：torch 2.5.1+cu121，triton 3.1.0，CUDA 可用（RTX 3060 Laptop GPU）
- `triton-fused-ops/.venv`：torch 2.13.0+cu130，triton 3.7.1
- **clang-format-18 缺失**（tiny-llm format 门禁障碍，需 apt 安装或用户授权）
- models/：qwen2.5-0.5b-instruct-q4_k_m.gguf、tokenizer.json（已在本机）

## 用户/未知归属内容（不动）

- `tiny-llm/.zcode/`（untracked，用户内容）
- 工作区根 `roofline_data_{512,1024,2048,4096}.csv`（未知归属，不触碰）
- `models/`（复现命令引用，不挪动）

## 备注

- meta 仓本地落后 origin 5 个 commit（c9f8a13/8b293bc/5de6621/144b47c/3f0128b，均为改名文档），未 merge（P0-01 只读）。
- 线上已有其他代理推送的改名 commit（cuflash rename 系列已推送且 CI 绿；paged-serving 改名 commit CI 红）。
