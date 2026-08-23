#!/usr/bin/env bash
# issue_scout.sh —— AI Infra 上游 issue 筛选管线（社区贡献用）
#
# 目的：把"爬 issue"变成有纪律的筛选——只挑与自身优势匹配、竞争少的 issue，
#      做深度复现与有价值的评论/PR，而不是批量刷存在感。
#
# 用法：
#   ./issue_scout.sh                          # 默认仓库与标签
#   LABELS="help wanted" ./issue_scout.sh     # 只扫某标签
#   REPOS="vllm-project/vllm" ./issue_scout.sh
#
# 依赖：gh（已 gh auth login）、python3
#
# 输出：按仓库分组的 issue 表，★ 标记命中你的优势关键词；评论数升序（0 评=无人认领）。

set -euo pipefail

# 目标仓库：优先与技能栈（serving / KV cache / GGUF / 量化 / tokenizer）对口的
REPOS="${REPOS:-vllm-project/vllm sgl-project/sglang ggml-org/llama.cpp flashinfer-ai/flashinfer}"

# 要扫的标签（竖线分隔）
LABELS="${LABELS:-good first issue|help wanted}"

# 你的优势关键词（命中标题则标 ★）——与作品集能力链对齐
KEYWORDS="${KEYWORDS:-gguf|kv cache|kv-cache|scheduler|quantiz|tokenizer|paged|batching|attention|rope|sampling|ffi}"

LIMIT="${LIMIT:-15}"

command -v gh >/dev/null || { echo "需要 gh CLI 并已 gh auth login"; exit 1; }

echo "AI Infra issue 筛选  $(date +%F)  关键词: $KEYWORDS"
echo "======================================================================"

for repo in $REPOS; do
  echo
  echo "## $repo"
  IFS='|' read -ra LABEL_ARR <<< "$LABELS"
  for label in "${LABEL_ARR[@]}"; do
    gh issue list -R "$repo" --label "$label" --state open --limit "$LIMIT" \
      --json number,title,comments,createdAt 2>/dev/null \
    | KEYWORDS="$KEYWORDS" python3 -c '
import json, os, re, sys
kw = re.compile(os.environ["KEYWORDS"], re.I)
rows = []
for i in json.load(sys.stdin):
    star = "★" if kw.search(i["title"]) else " "
    ncomments = len(i.get("comments") or [])
    rows.append((star, ncomments, i["number"], i["createdAt"][:10], i["title"][:78]))
# ★ 优先，其次评论数升序（竞争少的排前）
rows.sort(key=lambda r: (0 if r[0] == "★" else 1, r[1]))
for star, comments, num, date, title in rows:
    print(f"  {star} #{num:<7} {comments:<3}评 {date}  {title}")
' 2>/dev/null || echo "  （该标签无结果或查询失败）"
  done
done

echo
echo "----------------------------------------------------------------------"
echo "解读：★=命中优势关键词；评论数越少机会越大（0 评=无人认领）。"
echo "下一步：对候选逐个 gh issue view <n> -R <repo> 读全文，判断能否本地复现。"
