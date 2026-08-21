# AI Infra Interview Prep — 仓库维护统一入口
# 用法: make check / verify / progress / all
PY ?= python3
SCRIPTS := scripts

.PHONY: check check-online verify progress progress-write all help

## check       链接健康检查(本地模式,离线可用)
check:
	$(PY) $(SCRIPTS)/check_links.py

## check-online 链接健康检查(含外部链接可访问性,需联网)
check-online:
	$(PY) $(SCRIPTS)/check_links.py --online

## verify      计划一致性校验(权重 288h、周次日期连续、frontmatter 完整)
verify:
	$(PY) $(SCRIPTS)/verify_plan.py

## progress    只读查看进度统计
progress:
	$(PY) $(SCRIPTS)/progress.py

## progress-write 统计并写回 progress-tracker / frontmatter status / README 状态列
progress-write:
	$(PY) $(SCRIPTS)/progress.py --write

## all         一次跑完 check + verify + progress
all: check verify progress

help:
	@grep -E "^## " $(MAKEFILE_LIST) | sed 's/## //'
