#!/usr/bin/env python3
"""check_links.py — 仓库 Markdown 链接健康检查。

用法:
  python3 scripts/check_links.py            # 本地检查(相对链接 + 锚点)
  python3 scripts/check_links.py --online   # 额外用 HEAD 请求检查外部链接
  python3 scripts/check_links.py --file X.md  # 只检查指定文件

设计原则:
- 零外部依赖(纯标准库),本地默认只做本地校验,离线可用。
- 相对链接:解析路径并确认目标文件存在。
- 锚点 #xxx:按 GitHub 风格 slug(小写、空格/下划线转 -、去标点)匹配目标文件标题。
- 外部链接 http/https:默认仅校验格式;--online 时才发起请求。
退出码:0 = 全部通过;1 = 存在坏链接。
"""
import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")          # [text](url)
REF_LINK_RE = re.compile(r"^\s*\[[^\]]*\]:\s*(\S+)", re.M)  # [ref]: url
IMG_RE = re.compile(r"!\[[^\]]*\]\(")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.M)


def github_slug(text: str) -> str:
    """GitHub 风格锚点 slug。"""
    slug = text.strip().lower()
    slug = re.sub(r"[^\w一-鿿 \-]", "", slug)  # 去标点(保留中文)
    slug = slug.replace(" ", "-").replace("_", "-")
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def collect_headings(path: Path) -> set[str]:
    """收集文件中所有标题的 GitHub slug。"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return set()
    return {github_slug(m.group(1)) for m in HEADING_RE.finditer(text)}


def find_md_targets(rel_target: str, src_file: Path) -> list[Path]:
    """把相对链接解析为仓库内存在的 md 文件(支持目录 + 无扩展名两种情况)。"""
    candidates = []
    base = src_file.parent / rel_target
    for p in (base, base.with_suffix(".md"), src_file.parent / (rel_target + ".md")):
        if p.is_file():
            candidates.append(p)
    # 目录链接 → 尝试目录内 README.md 或同名 md
    if base.is_dir():
        for name in ("README.md", "index.md"):
            p = base / name
            if p.is_file():
                candidates.append(p)
    return candidates


def split_anchor(url: str) -> tuple[str, str]:
    if "#" in url:
        path, anchor = url.split("#", 1)
        return path, anchor
    return url, ""


def check_file(path: Path, check_online: bool) -> list[str]:
    """检查单个文件,返回坏链接列表 [文件:行 链接 -> 原因]。"""
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"{path}: 无法读取 ({e})"]

    links = []
    for m in MD_LINK_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        url = m.group(1)
        if IMG_RE.search(text, m.start() - 1, m.start() + 1):
            continue  # 图片链接跳过
        links.append((line, url))
    for m in REF_LINK_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        links.append((line, m.group(1)))

    seen = set()
    for line, url in links:
        url = url.strip().strip("<>")
        if url in seen:
            continue
        seen.add(url)

        if url.startswith(("http://", "https://")):
            if check_online:
                import urllib.request
                try:
                    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "link-checker"})
                    with urllib.request.urlopen(req, timeout=10):
                        pass
                except Exception as e:
                    errors.append(f"{path}:{line} 外部链接 {url} -> {type(e).__name__}: {e}")
            continue
        if url.startswith(("mailto:", "tel:")) or url.startswith("#"):
            continue

        rel_target, anchor = split_anchor(url)
        targets = find_md_targets(rel_target, path)
        if not targets:
            # 指向存在的目录(如 weekly/)是合法链接,视为通过
            if (path.parent / rel_target).is_dir():
                continue
            errors.append(f"{path}:{line} 相对链接 {url} -> 目标不存在")
            continue
        if anchor and anchor != "L":
            anchor_slug = github_slug(anchor)
            ok = any(anchor_slug in collect_headings(t) for t in targets)
            if not ok:
                errors.append(f"{path}:{line} 锚点 #{anchor} -> 目标 {rel_target} 中无此标题")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="仓库 Markdown 链接检查")
    ap.add_argument("--online", action="store_true", help="额外检查外部链接可访问性")
    ap.add_argument("--file", type=str, help="只检查指定文件(相对仓库根)")
    args = ap.parse_args()

    if args.file:
        files = [REPO_ROOT / args.file]
    else:
        files = sorted(
            p for p in REPO_ROOT.rglob("*.md")
            if ".git" not in p.parts and "node_modules" not in p.parts
        )

    total_errors = []
    for f in files:
        total_errors.extend(check_file(f, args.online))

    if total_errors:
        print(f"❌ 发现 {len(total_errors)} 个坏链接:")
        for e in total_errors:
            print("   " + e)
        return 1
    print(f"✅ 链接检查通过({len(files)} 个文件"
          + (",含外部链接" if args.online else ",本地模式")
          + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
