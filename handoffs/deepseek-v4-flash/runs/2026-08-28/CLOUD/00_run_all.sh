#!/usr/bin/env bash
# 云部署包 - 00 执行编排（云端：开机后一次运行）
# canary 失败即停（02 内 exit 1 终止本脚本）；通过后正式矩阵；
# 全部原始产物留在 /workspace/results，下载由 04 完成；实例随后停机删除。
set -euo pipefail
echo "[$(date -u +%F\ %T)] ==== 开始：环境记录+构建+canary ===="
bash /workspace/02_build_canary.sh
echo "[$(date -u +%F\ %T)] ==== canary 通过，正式矩阵 ===="
bash /workspace/03_formal_matrix.sh
echo "[$(date -u +%F\ %T)] ==== 完成；结果清单："
find /workspace/results -type f | sort
echo "==== 关键产物可以下载（04_download）====
实例保留至下载完成，随后删除/停止。"