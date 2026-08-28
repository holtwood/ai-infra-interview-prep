# UP-01 follow-up 草稿（存档，未发布；需 ALLOW_GITHUB_WRITE=true + 用户审核）

目标：SGLang PR #36115（一次有信息增量的 follow-up，不刷屏）

## 草稿（英文，符合 SGLang maintainer 沟通惯例）

```
Hi maintainers — quick update on this PR:

- The targeted function (`page_aligned_decode_alloc_lens`) is unchanged between
  this PR's head and current main (verified against commit 76d1401881), so no
  rebase risk.
- I re-ran the 7 assertions locally as a dependency-free logic check: all 7
  pass against the current function implementation.
- Lint is green; the full CPU/GPU matrices still need the `run-ci` label —
  could someone with triage rights add it? Thank you.
```

## 备选（若不想请求 label，仅汇报状态）

```
Quick status: Lint is green, and I verified the 7 assertions against current
main (function identical to PR head, no rebase needed). I'll leave the
`run-ci`-gated matrices to a maintainer's judgment. Happy to rebase or adjust
on review.
```

## 发布规则（PROMPT §10）

- 外部评论与 PR 正文先展示给用户审核，再在 ALLOW_GITHUB_WRITE=true 时发布
- 最多一次有信息增量的 follow-up，不刷屏
- 不声称未运行的 CI/合并结果；run-ci label 缺失写成等待状态而非代码失败