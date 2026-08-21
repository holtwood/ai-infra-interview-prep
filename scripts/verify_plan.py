#!/usr/bin/env python3
"""verify_plan.py — 计划一致性健康检查。

校验项:
1. TOPIC_WEIGHTS.md 各桶小时合计 = 288(24h × 12 周),权重合计 = 100%。
2. weekly/week-*.md 的 YAML frontmatter 完整且合法
   (week 连续 1..12 / start、end 日期格式 / 每周 7 天连续 / hours ∈ {12,18,24} / status 合法)。
3. weekly 文件 H1 标题与 frontmatter title 一致。
4. progress-tracker.md 周次列表与 weekly 文件一一对应。
5. 每周文件存在且可读。

用法:
  python3 scripts/verify_plan.py
退出码:0 = 全部通过;1 = 发现问题。
"""
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_HOURS = {12, 18, 24}
VALID_STATUS = {"upcoming", "active", "done"}

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+)\s*\|\s*(\d+)%\s*\|\s*([\dh]+)\s*\|")


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


def check_topic_weights() -> list[str]:
    """校验 TOPIC_WEIGHTS 小时合计与权重。"""
    errors = []
    f = REPO_ROOT / "TOPIC_WEIGHTS.md"
    if not f.exists():
        return [f"缺少 {f.name}"]
    text = f.read_text(encoding="utf-8")
    hours_total, weight_total, rows = 0, 0, 0
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        weight = cells[1].rstrip("%")
        hours = cells[2].rstrip("h")
        try:
            w, h = float(weight), float(hours)
        except ValueError:
            continue
        weight_total += w
        hours_total += h
        rows += 1
    if rows < 5:
        errors.append(f"TOPIC_WEIGHTS: 只解析到 {rows} 行数据,表格可能被改动")
    if abs(hours_total - 288) > 0.5:
        errors.append(f"TOPIC_WEIGHTS: 小时合计 {hours_total:.0f}h ≠ 288h")
    if abs(weight_total - 100) > 0.5:
        errors.append(f"TOPIC_WEIGHTS: 权重合计 {weight_total:.0f}% ≠ 100%")
    return errors


def check_weeks() -> list[str]:
    """校验 weekly/*.md 的 frontmatter、日期连续性与 H1 一致性。"""
    errors = []
    files = sorted(REPO_ROOT.glob("weekly/week-*.md"))
    if len(files) != 12:
        errors.append(f"weekly/ 下应有 12 个周文件,实际 {len(files)} 个")

    week_map: dict[int, Path] = {}
    for f in files:
        m = re.search(r"week-(\d+)\.md$", f.name)
        if m:
            week_map[int(m.group(1))] = f

    for n in range(1, 13):
        f = week_map.get(n)
        if not f:
            errors.append(f"缺少 week-{n:02d}.md")
            continue
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm:
            errors.append(f"{f.name}: 缺少 YAML frontmatter")
            continue
        # 基础字段
        for k in ("week", "title", "start", "end", "hours", "status"):
            if k not in fm:
                errors.append(f"{f.name}: frontmatter 缺字段 '{k}'")
        # week 号
        if "week" in fm and str(fm["week"]) != str(n):
            errors.append(f"{f.name}: frontmatter week={fm['week']} 与文件名不符({n})")
        # 日期
        for k in ("start", "end"):
            if k in fm:
                try:
                    datetime.strptime(fm[k], "%Y-%m-%d")
                except ValueError:
                    errors.append(f"{f.name}: {k}={fm[k]} 日期格式应为 YYYY-MM-DD")
        # hours / status 枚举
        if "hours" in fm:
            try:
                if int(fm["hours"]) not in VALID_HOURS:
                    errors.append(f"{f.name}: hours={fm['hours']} 不在 {sorted(VALID_HOURS)}")
            except ValueError:
                errors.append(f"{f.name}: hours={fm['hours']} 不是数字")
        if "status" in fm and fm["status"] not in VALID_STATUS:
            errors.append(f"{f.name}: status='{fm['status']}' 不在 {sorted(VALID_STATUS)}")
        # H1 与 title 一致(容忍「第 N 周:」前缀)
        h1 = H1_RE.search(text)
        if h1 and "title" in fm:
            h1_text = re.sub(r"^第\s*\d+\s*周[：:]?\s*", "", h1.group(1).strip())
            if h1_text != fm["title"]:
                errors.append(f"{f.name}: H1「{h1.group(1).strip()}」与 frontmatter title「{fm['title']}」不一致")

    # 日期连续性:每周 7 天,周与周之间无缝衔接
    starts = {}
    for n, f in week_map.items():
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if "start" in fm and "end" in fm:
            try:
                starts[n] = datetime.strptime(fm["start"], "%Y-%m-%d")
                end = datetime.strptime(fm["end"], "%Y-%m-%d")
                if (end - starts[n]).days != 6:
                    errors.append(f"week-{n:02d}: 日期跨度 {(end - starts[n]).days + 1} 天,应为 7 天")
            except ValueError:
                pass
    for n in sorted(starts):
        if n > 1 and (n - 1) in starts:
            gap = (starts[n] - starts[n - 1]).days
            if gap != 7:
                errors.append(f"week-{n:02d} 与 week-{n - 1:02d} 间隔 {gap} 天,应为 7 天")

    # progress-tracker 周次一致性
    pt = REPO_ROOT / "progress-tracker.md"
    if pt.exists():
        pt_text = pt.read_text(encoding="utf-8")
        pt_weeks = set(re.findall(r"week-(\d{2})\.md", pt_text))
        fs_weeks = {f"{n:02d}" for n in range(1, 13)}
        missing = fs_weeks - pt_weeks
        extra = pt_weeks - fs_weeks
        if missing:
            errors.append(f"progress-tracker 缺少周文件链接: {sorted(missing)}")
        if extra:
            errors.append(f"progress-tracker 含不存在的周文件链接: {sorted(extra)}")
    return errors


def main() -> int:
    errors = check_topic_weights() + check_weeks()
    if errors:
        print(f"❌ 计划校验发现 {len(errors)} 个问题:")
        for e in errors:
            print("   " + e)
        return 1
    print("✅ 计划一致性校验通过:权重 288h/100%,12 周 frontmatter 完整、日期连续、枚举合法")
    return 0


if __name__ == "__main__":
    sys.exit(main())
