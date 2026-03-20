#!/usr/bin/env python3
"""List project-specific placeholders remaining after template application."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict

PROJECT_MACRO_PATTERN = re.compile(r"\{\{PROJECT_NAME(?:_LOWER)?\}\}")
HTML_TODO_PATTERN = re.compile(r"<!--\s*TODO:\s*(.*?)\s*-->")

DEFAULT_GLOBS = ("docs/**/*.md", "instructions/**/*.md", ".github/**/*.md", "*.md")
EXAMPLE_COMPONENT_DIR = "docs/components/_example_component"
CURRENT_SKILL_ROOT = Path(__file__).resolve().parent.parent


class ScanRecord(TypedDict):
    """スキャン結果の1ファイル分のレコード。"""
    path: str
    priority: int
    project_macros: list[str]
    project_macro_count: int
    todos: list[str]
    todo_count: int


PRIORITY_MAP = {
    "instructions/agent_common_master.md": 0,
    "docs/rules/project_overview.md": 1,
    "docs/architecture/overview.md": 2,
    "docs/rules/development_workflow.md": 3,
    "docs/tests/README.md": 4,
    "docs/tests/strategy.md": 5,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan a project adapted from csharp-project-template and list remaining "
            "project-specific placeholders."
        )
    )
    parser.add_argument("root", help="Project root to scan")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of text",
    )
    return parser.parse_args()


def iter_candidate_files(root: Path) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in DEFAULT_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if CURRENT_SKILL_ROOT == resolved or CURRENT_SKILL_ROOT in resolved.parents:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(path)
    return sorted(files)


def scan_file(path: Path, root: Path) -> ScanRecord | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None

    macros = PROJECT_MACRO_PATTERN.findall(text)
    todos = HTML_TODO_PATTERN.findall(text)
    if not macros and not todos:
        return None

    rel_path = path.relative_to(root).as_posix()
    return {
        "path": rel_path,
        "priority": PRIORITY_MAP.get(rel_path, 99),
        "project_macros": sorted(set(macros)),
        "project_macro_count": len(macros),
        "todos": todos,
        "todo_count": len(todos),
    }


def check_example_component(root: Path) -> bool:
    """_example_component ディレクトリが残っているかを返す。"""
    return (root / EXAMPLE_COMPONENT_DIR).is_dir()


def render_text(
    results: list[ScanRecord],
    root: Path,
    example_component_exists: bool,
) -> str:
    lines = [f"Project root: {root}", f"Files with placeholders: {len(results)}"]
    if example_component_exists:
        lines.append(
            f"[WARN] {EXAMPLE_COMPONENT_DIR}/ が残っています — "
            "実コンポーネントへ置き換えてください"
        )
    for item in results:
        lines.append(f"- {item['path']}")
        if item["project_macro_count"]:
            macro_list = ", ".join(item["project_macros"])
            lines.append(
                f"  project-macros: {item['project_macro_count']} ({macro_list})"
            )
        for todo in item["todos"]:
            lines.append(f"  todo: {todo}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"[ERROR] root does not exist: {root}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"[ERROR] root is not a directory: {root}", file=sys.stderr)
        return 1

    results = []
    for path in iter_candidate_files(root):
        record = scan_file(path, root)
        if record is not None:
            results.append(record)

    results.sort(key=lambda item: (int(item["priority"]), str(item["path"])))

    example_component_exists = check_example_component(root)

    if args.json:
        output = {
            "files": results,
            "example_component_exists": example_component_exists,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(render_text(results, root, example_component_exists))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
