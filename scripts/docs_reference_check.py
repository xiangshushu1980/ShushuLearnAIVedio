#!/usr/bin/env python3
# Owner: Sean
"""Read-only checks for documentation links, legacy numbering, and ledger IDs."""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEDGER = ROOT / ".pi" / "ledger"
INDEX = DOCS / "INDEX.md"
LEDGER_INDEX = LEDGER / "README.md"
LINK_RE = re.compile(r"!?\[[^\]]*\]\((<[^>\n]+>|[^)\n]+)\)")
DOC_NAME_RE = re.compile(r"^(\d{2})_.+\.md$")
LEDGER_ID_RE = re.compile(r"^###\s+(C-[A-Z0-9-]+)\s+\|")


def markdown_files() -> list[Path]:
    files: set[Path] = set()
    for folder in (DOCS, LEDGER, ROOT / ".pi" / "skills", ROOT / "experiments"):
        if folder.exists():
            files.update(p for p in folder.rglob("*.md") if p.is_file())
    return sorted(files)


def check_links() -> list[str]:
    errors: list[str] = []
    checked = 0
    external_absolute = 0
    for source in markdown_files():
        for line_no, line in enumerate(source.read_text(errors="replace").splitlines(), 1):
            for match in LINK_RE.finditer(line):
                raw = match.group(1).strip()
                target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw.split()[0]
                target = unquote(target)
                if not target or target.startswith("#"):
                    continue
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("//"):
                    continue
                path_part = parsed.path
                if not path_part:
                    continue
                path = Path(path_part)
                if path.is_absolute():
                    resolved = path.resolve()
                    if not resolved.is_relative_to(ROOT):
                        external_absolute += 1
                        continue
                else:
                    resolved = source.parent / path
                checked += 1
                if resolved.exists():
                    continue
                rel_source = source.relative_to(ROOT)
                errors.append(f"{rel_source}:{line_no}: missing local link target: {path_part}")
    print(f"  检查本地 Markdown 链接：{checked} 个")
    if external_absolute:
        print(f"  跳过仓库外绝对路径：{external_absolute} 个（主机相关路径）")
    return errors


def check_number_collisions() -> list[str]:
    groups: dict[str, list[str]] = defaultdict(list)
    for path in DOCS.glob("[0-9][0-9]_*.md"):
        match = DOC_NAME_RE.match(path.name)
        if match:
            groups[match.group(1)].append(path.name)

    index_text = INDEX.read_text(errors="replace") if INDEX.exists() else ""
    match = re.search(r"^### 历史编号例外\s*$([\s\S]*?)(?=^## |\Z)", index_text, re.M)
    exception_text = match.group(1) if match else ""
    errors: list[str] = []
    for number, names in sorted(groups.items()):
        if len(names) < 2:
            continue
        missing = [name for name in names if name not in exception_text]
        if missing:
            errors.append(f"duplicate docs number {number} lacks an explicit legacy exception: {', '.join(names)}")
        else:
            print(f"  已登记历史重复编号 {number}: {', '.join(sorted(names))}")
    return errors


def check_ledger_ids() -> list[str]:
    entries: dict[str, list[str]] = defaultdict(list)
    for path in LEDGER.glob("*.md"):
        if path.name == "README.md":
            continue
        for line in path.read_text(errors="replace").splitlines():
            match = LEDGER_ID_RE.match(line)
            if match:
                entries[match.group(1)].append(path.name)

    index_text = LEDGER_INDEX.read_text(errors="replace") if LEDGER_INDEX.exists() else ""
    in_registry = False
    registry: dict[tuple[str, str], str] = {}
    canonical_ids: list[str] = []
    for line in index_text.splitlines():
        if line.startswith("## 〇-A、"):
            in_registry = True
            continue
        if in_registry and line.startswith("## "):
            break
        if not in_registry or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0].startswith("`") or not cells[1].startswith("`"):
            continue
        legacy = cells[0].strip("`")
        canonical = cells[1].strip("`")
        target_match = re.search(r"\]\(([^)]+)\)", cells[3])
        if not target_match:
            continue
        filename = Path(target_match.group(1)).name
        registry[(legacy, filename)] = canonical
        canonical_ids.append(canonical)

    errors: list[str] = []
    duplicates = {legacy: sorted(set(files)) for legacy, files in entries.items() if len(set(files)) > 1}
    for legacy, files in duplicates.items():
        missing = [name for name in files if (legacy, name) not in registry]
        if missing:
            errors.append(f"duplicate ledger ID {legacy} lacks registry mappings for: {', '.join(missing)}")
    duplicate_canonicals = [cid for cid, count in Counter(canonical_ids).items() if count > 1]
    if duplicate_canonicals:
        errors.append(f"canonical ledger IDs are not unique: {', '.join(duplicate_canonicals)}")
    if duplicates and not errors:
        print(f"  已登记跨账本 legacy ID 冲突: {len(duplicates)} 组")
    return errors


def main() -> int:
    print("== Markdown 本地链接检查 ==")
    errors = check_links()
    print("== docs 编号冲突检查 ==")
    errors.extend(check_number_collisions())
    print("== Ledger ID 冲突检查 ==")
    errors.extend(check_ledger_ids())
    if errors:
        for error in errors:
            print(f"  ✗ {error}")
        print(f"FAIL：发现 {len(errors)} 项文档引用或 ID 问题")
        return 1
    print("OK：本地链接、已登记编号例外和 Ledger ID 映射均通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
