# P0-03M 本地 checkout 迁移记录（2026-08-28 14:34 +08:00 / 06:34 UTC）

## 授权
ALLOW_KNOWN_CHECKOUT_RENAME=true；commit/push/GitHub/云 均 false（未执行任何 git 写操作）。

## 迁移前后对照

| 项 | cuflash | paged-serving |
|----|---------|---------------|
| 迁移前路径 | /home/shane/github/open-infra-ai/cuflash-attn | /home/shane/github/open-infra-ai/paged-infer |
| 迁移后路径 | /home/shane/github/open-infra-ai/cuflash | /home/shane/github/open-infra-ai/paged-serving |
| HEAD（不变） | d53a5301bf5e014f1f258db41e2a9d2a1252d00d（v0.6.0） | 080f26f91fb339f85b54d338cfed1b68d59190c7 |
| 迁移前 remote | https://github.com/open-infra-ai/cuflash-attn.git | https://github.com/open-infra-ai/paged-infer.git |
| 迁移后 remote | https://github.com/open-infra-ai/cuflash.git | https://github.com/open-infra-ai/paged-serving.git |
| dirty（迁移前后一致，均本会话已知） | M docs/design/flash-decoding.md（P0-03）、M docs/performance/benchmarks.md（CUF-01） | M README.md（P0-03）、M tests/tokenizer_real_diff.rs（P0-04） |

## 预检（迁移前）
- 源目录存在 ✓；目标目录不存在（无冲突）✓
- dirty 全部归属 P0-03/P0-04/CUF-01 已知改动 ✓
- lsof + ps 无进程占用 ✓；无 .vscode/全局配置引用旧路径 ✓（命中仅 handoff 执行文档的事实描述）
- 根 README 目录索引在 P0-03 已改为 canonical（cuflash/、paged-serving/）→ mv 后一致 ✓

## 验证（迁移后）
- `git status --short --branch`：分支/上游跟踪正常，dirty 保持
- `git remote -v`：新 URL ✓；`git fetch origin` 两仓 OK（新 URL 连通）
- 构建入口：cuflash CMakeLists.txt + build/release/ 存在；paged-serving Cargo.toml + target/ 存在
- **已知副作用**：cuflash build/release/CMakeCache.txt 的 `CMAKE_HOME_DIRECTORY` 仍记录旧路径
  `/home/shane/github/open-infra-ai/cuflash-attn`——重新 `cmake --preset release` 配置即可恢复
  （本轮未重跑构建，避免超出迁移授权范围）；paged-serving 的 cargo target 增量缓存同理，
  首次 `cargo build` 会因路径变化重新编译

## Rollback 命令（如需回退）
```bash
mv /home/shane/github/open-infra-ai/cuflash /home/shane/github/open-infra-ai/cuflash-attn
mv /home/shane/github/open-infra-ai/paged-serving /home/shane/github/open-infra-ai/paged-infer
git -C /home/shane/github/open-infra-ai/cuflash-attn remote set-url origin https://github.com/open-infra-ai/cuflash-attn.git
git -C /home/shane/github/open-infra-ai/paged-infer remote set-url origin https://github.com/open-infra-ai/paged-infer.git
# 验证：git status --short --branch && git remote -v
```

## 未执行
- 未 commit / push / 改 GitHub 元数据；未删除任何文件；未改动 .git 历史
- 未重跑构建（构建入口验证为静态检查；CMakeCache/target 缓存路径失效已记录）