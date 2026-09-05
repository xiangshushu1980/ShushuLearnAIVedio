#!/usr/bin/env bash
# docs 一致性检查（幂等：只读不改文件，可重复运行）
# 检查：
#   1. docs/ 顶层参考文档全部被 INDEX.md 收录
#   2. docs/ 与 .pi/ 内对本地 docs/NN_*.md 的引用目标存在（防合并/删除后断链）
#   3. 编号缺口提示（已归档号需在 INDEX「已归档」行登记；范围随现有最大编号变化）
#   4. docs/ 下未跟踪文件告警（如交付物副本误入）
# 用法：bash scripts/docs_check.sh  （在 comfy-ops 根目录或任意处）
set -u
cd "$(dirname "$0")/.." || exit 1
DOCS=docs
INDEX="$DOCS/INDEX.md"
fail=0

echo "== 1. INDEX 收录检查 =="
for f in "$DOCS"/*.md; do
  name=$(basename "$f")
  [ "$name" = "INDEX.md" ] && continue
  if ! grep -q "$name" "$INDEX"; then
    echo "  ✗ $name 未被 INDEX 收录"; fail=1
  fi
done

echo "== 2. docs 内引用存在性 =="
for r in $(rg --only-matching --no-filename 'docs/[0-9]{2}_[A-Za-z0-9_]+\.md' "$DOCS" --glob '*.md' --glob '!docs/project/**' --glob '!docs/archive/**' 2>/dev/null | sort -u); do
  f="$DOCS/$(basename "$r")"
  if [ ! -f "$f" ]; then
    echo "  ✗ 引用断裂: $r"; fail=1
  fi
done

echo "== 3. .pi/skills 内 docs 引用存在性 =="
for r in $(rg --only-matching --no-filename 'docs/[0-9]{2}_[A-Za-z0-9_]+\.md' .pi/skills --glob '*.md' 2>/dev/null | sort -u); do
  f="$DOCS/$(basename "$r")"
  if [ ! -f "$f" ]; then
    echo "  ✗ 引用断裂: $r"; fail=1
  fi
done

echo "== 4. 编号缺口（已归档号应在 INDEX 登记） =="
nums=$(find "$DOCS" -maxdepth 1 -type f -printf '%f\n' | grep -oE '^[0-9]{2}' | sort -u)
max_num=$(printf '%s\n' "$nums" | sort -n | tail -1)
archived=$(sed -n '/已归档/,/^$/p' "$INDEX" | grep -oE '\b[0-9]{2}\b' | sort -u)
for n in $(seq 1 "${max_num:-0}"); do
  nn=$(printf "%02d" "$n")
  echo "$nums" | grep -q "$nn" || {
    echo "$archived" | grep -q "$nn" || echo "  提示: ${nn} 号空缺（未标记归档）"
  }
done

echo "== 5. docs/ 未跟踪文件 =="
git status --short "$DOCS/" 2>/dev/null | grep '^??' || echo "  无"

if [ "$fail" -eq 0 ]; then
  echo "OK：引用一致"
else
  echo "FAIL：存在断裂引用（见上 ✗）"
fi
exit "$fail"
