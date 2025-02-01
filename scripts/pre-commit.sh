#!/bin/sh
changed_files="$(git diff --cached --name-only)"
if echo "$changed_files" | grep -q "^articles/"; then
  echo "检测到 articles/ 目录变化，更新 README..."
  python scripts/update_readme.py
  
  # 如果 README.md 有变化，将其添加到当前 commit
  if git diff --quiet README.md; then
    echo "README.md 无变化"
  else
    echo "将更新后的 README.md 添加到 commit..."
    git add README.md
  fi
fi 