#!/usr/bin/env python3
"""progress.py — 进度统计与汇总更新。

做什么:
1. 扫描 weekly/week-*.md 的「可验证交付物」checkbox(`- [x]` / `- [ ]`),
   计算每周完成率。
2. 更新 progress-tracker.md:
   - 每周进度表格的「日期范围」「完成度」列(从 frontmatter 读取日期)。
   - 每日打卡表格保持不动(手动填写)。
3. 更新每个周文件 frontmatter 的 status:
   100% → done;>0% → active;0% → upcoming。
4. 更新 README.md 文档地图的每周状态列(若有)。

用法:
  python3 scripts/progress.py            # 只读统计,输出摘要
  python3 scripts/progress.py --write    # 写回 progress-tracker / frontmatter / README
退出码:0 = 成功。
"""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKBOX_RE = re.compile(r"^(\s*)-\s+\[([ xX])\]\s+(.+)$", re.M)
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def set_frontmatter_field(text: str, field: str, value: str) -> str:
    """在 YAML frontmatter 中设置/更新单个字段。"""
    m = FM_RE.match(text)
    if not m:
        return text
    body = m.group(1)
    lines = body.splitlines()
    out, replaced = [], False
    for line in lines:
        if line.startswith(f"{field}:"):
            out.append(f"{field}: {value}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.insert(0, f"{field}: {value}")
    return f"---\n{chr(10).join(out)}\n---\n{text[m.end():]}"


def week_stats() -> list[dict]:
    stats = []
    for f in sorted(REPO_ROOT.glob("weekly/week-*.md")):
        text = read(f)
        fm = parse_frontmatter(text)
        done = 0
        total = 0
        for line in text.splitlines():
            m = CHECKBOX_RE.match(line)
            if m:
                total += 1
                if m.group(2).lower() == "x":
                    done += 1
        pct = round(done * 100 / total) if total else 0
        n = int(re.search(r"week-(\d+)\.md$", f.name).group(1))
        stats.append({
            "file": f.name,
            "week": n,
            "done": done,
            "total": total,
            "pct": pct,
            "start": fm.get("start", "-"),
            "end": fm.get("end", "-"),
            "status": fm.get("status", "upcoming"),
            "title": fm.get("title", ""),
        })
    return stats


def render_progress_table(stats: list[dict]) -> list[str]:
    """生成每周进度表格行。"""
    rows = []
    for s in sorted(stats, key=lambda x: x["week"]):
        theme = s["title"] if s["title"] else "-"
        date_range = f"{s['start']} ~ {s['end']}" if s["start"] != "-" else "-"
        rows.append(
            f"| 第 {s['week']} 周 | {date_range} | {theme} | {s['pct']}% | "
            f"[笔记](./weekly/week-{s['week']:02d}.md) |"
        )
    return rows


def update_progress_tracker(stats: list[dict]) -> bool:
    pt = REPO_ROOT / "progress-tracker.md"
    if not pt.exists():
        return False
    text = read(pt)
    rows = render_progress_table(stats)
    # 找到「## 每周进度」与「## 每日打卡」之间的表格,整体替换
    start_m = re.search(r"^## 每周进度.*?\n", text, re.M)
    end_m = re.search(r"^## 每日打卡", text, re.M)
    if not start_m or not end_m:
        return False
    header = "| 周次 | 日期范围 | 主题 | 完成度 | 笔记链接 |\n|------|----------|------|--------|----------|\n"
    new_block = f"## 每周进度\n\n{header}" + "\n".join(rows) + "\n\n"
    new_text = text[: start_m.start()] + new_block + text[end_m.start():]
    # 更新 frontmatter 的 updated 字段
    import datetime
    new_text = set_frontmatter_field(new_text, "updated", datetime.date.today().isoformat())
    pt.write_text(new_text, encoding="utf-8")
    return True


def update_frontmatter_status(stats: list[dict]) -> int:
    changed = 0
    for s in stats:
        f = REPO_ROOT / "weekly" / s["file"]
        text = read(f)
        target = "done" if s["pct"] == 100 else ("active" if s["pct"] > 0 else "upcoming")
        if s["status"] != target:
            new_text = set_frontmatter_field(text, "status", target)
            f.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


def update_readme_status(stats: list[dict]) -> bool:
    """更新 README 文档地图中的每周状态列(若表格存在该列)。"""
    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        return False
    text = read(readme)
    icon = {"done": "✅", "active": "🔄", "upcoming": "⬜"}
    changed = False
    for n in range(1, 13):
        # 按本次完成度推断目标状态(与 update_frontmatter_status 一致)
        s = next((x for x in stats if x["week"] == n), None)
        if not s:
            continue
        target = "done" if s["pct"] == 100 else ("active" if s["pct"] > 0 else "upcoming")
        new = icon[target]
        # 匹配「[文本](weekly/week-NN.md) | 主题 | 日期 | 状态 |」,只替换第 4 列状态
        pat = re.compile(
            rf"(\[[^\]]*\]\(weekly/week-{n:02d}\.md\)\s*\|[^|]*\|[^|]*\|\s*)[^|]*\s*\|"
        )
        m = pat.search(text)
        if m:
            cur_status = m.group(0).split("|")[-2].strip()
            if cur_status != new:
                text = pat.sub(rf"\g<1>{new} |", text, count=1)
                changed = True
    if changed:
        readme.write_text(text, encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="进度统计与汇总更新")
    ap.add_argument("--write", action="store_true", help="写回 progress-tracker / frontmatter / README")
    args = ap.parse_args()

    stats = week_stats()
    overall_done = sum(s["done"] for s in stats)
    overall_total = sum(s["total"] for s in stats)
    overall = round(overall_done * 100 / overall_total) if overall_total else 0

    print(f"📊 全局完成度: {overall_done}/{overall_total} 项交付物 = {overall}%")
    for s in sorted(stats, key=lambda x: x["week"]):
        bar = "█" * (s["pct"] // 10) + "░" * (10 - s["pct"] // 10)
        print(f"  W{s['week']:02d} [{bar}] {s['pct']:3d}%  ({s['done']}/{s['total']})  {s['title'][:28]}")

    if args.write:
        w1 = update_progress_tracker(stats)
        w2 = update_frontmatter_status(stats)
        w3 = update_readme_status(stats)
        print(f"✅ 已写回: progress-tracker={'是' if w1 else '否'} · frontmatter 更新 {w2} 个 · README={'是' if w3 else '否'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
