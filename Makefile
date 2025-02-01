# 设置 git hooks 目标
setup_hooks:
	@cp scripts/pre-commit.sh .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit

update_readme:
	python scripts/update_readme.py

md2wechat:
	python scripts/md2wechat.py $(md_file)