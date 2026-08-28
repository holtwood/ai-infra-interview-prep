# CUF-01 清理 cuflash live 文档证据口径（2026-08-28）

## 审计结果

- cuflash v0.5.1（2026-08-24）起 live 文档已有证据纪律基础，本次复核确认并修复残留漂移。
- 旧名/旧 URL：`rg 'cuflash-attn|aicl-lab|paged-infer'`（排除 CHANGELOG/.git）在 README + docs 无残留（P0-03 已清理）。

## 逐项复核

| 项 | 状态 |
|----|------|
| README 性能节 | ✓ 明确"仓库不维护无法持续复测的固定性能数字，请在目标硬件上运行自带 benchmark"；无性能表 |
| benchmarks.md 跨 GPU 表（V100/A100/H100、SDPA 对比、内存对比、Scaling） | ✓ 顶部声明"不可审计历史快照（禁止引用）"：无原始 JSON/Nsight/Release 附件，禁止用于 README/Release/简历/面试/横向比较；第 7 节正式结果发布门槛（metadata.json+原始 JSON+对照+nsys/ncu+失败形状） |
| benchmarks.md 1.5 本机快照（RTX 3060，2026-08-18，commit 6860cbc） | ✓ 声明"原始 JSON 尚未随仓库归档，只用于 sanity check，不可替代正式结果包"；附复现命令 |
| causal-boundary-skip.md | ✓ 数据快照标注（2026-08-18 RTX 3060 本机）+ 复现命令；结论为"增益低于噪声"的负结果，未夸大 |
| roofline-analysis.md | ✓ 旧快照数值均标注"只作旧快照参考/历史快照"；硬件规格数字（共享内存/带宽/TFLOPS 理论值）为公开规格有来源 |
| algorithm.md / building.md / troubleshooting.md | ✓ 数字为硬件规格/兼容性事实，非实验主张 |
| tensor-core-migration.md | ✓ 设计文档，无无来源实验数字（"约 90% 可达吞吐来自 Tensor Core"为定性叙述） |
| project-status.md / index.md / guide/ | ✓ 无性能数字 |
| docs/development/PLAN-v1.0.md | ✓ 标注"归档"的历史计划，豁免 |
| 仓库无 benchmark 原始 JSON | ✓ 与文档声明一致（仅 CMakePresets/package 等配置 JSON） |

## 本次修改（live-fix）

`docs/performance/benchmarks.md`：
- L51-52（1.4 编译参数）：`-DCUFASH_ATTN_BENCHMARKS=ON -DCUFASH_ATTN_ARCHS="70;80;90"` → `-DBUILD_BENCHMARKS=ON -DCMAKE_CUDA_ARCHITECTURES="70;80;90"`（与 CMakeLists `BUILD_BENCHMARKS` option 及 CMake 标准 `CMAKE_CUDA_ARCHITECTURES` 对齐；旧名为 cuflash_attn 时代残留）
- L266：`git clone https://github.com/your-org/cuflash.git` → `open-infra-ai/cuflash.git`（占位符收口为 canonical）
- L270/L306：`-DCUFASH_ATTN_BENCHMARKS=ON` → `-DBUILD_BENCHMARKS=ON`（2 处）
- git diff 统计：benchmarks.md 10 行变更（含 P0-03 的 paged-serving 1 行于 flash-decoding.md；CHANGELOG 未动）

## 验证

- `cd docs && npm run docs:build`：exit 0，build complete in 23.02s（vitepress 1.6.4，node v24.18.0，npm 12.0.2；node_modules 已存在，未重新 npm ci）
- 残留复查：`CUFASH_ATTN_*` 仅存在于归档历史计划 docs/development/PLAN-v1.0.md:340（豁免）

## 限制

- 未跑 npm ci（node_modules 已存在且 docs:build 通过）；如需完整复现可后续执行
- 本机无 V100/A100/H100，跨 GPU 快照维持"禁止引用"状态；正式结果包属 CUF-02（需云）
- 未 push、未跑远端 CI/Pages 部署