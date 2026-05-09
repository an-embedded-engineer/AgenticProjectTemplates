#!/usr/bin/env python3
"""gitコミット履歴から指定範囲の差分を抽出するツール。

指定した期間またはコミットID範囲で変更されたファイルのbefore/afterソースと
unified diffを出力する。
"""
from __future__ import annotations

import argparse
import difflib
import logging
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# データ構造
# ---------------------------------------------------------------------------

class FileChangeStatus(Enum):
    """ファイル変更種別。"""
    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"


@dataclass(frozen=True)
class ChangedFile:
    """変更対象ファイルの情報。"""
    path: str
    status: FileChangeStatus


@dataclass(frozen=True)
class CommitInfo:
    """コミットのID・メッセージ。"""
    commit_id: str
    message: str


@dataclass(frozen=True)
class DateRange:
    """日付範囲指定。"""
    date_from: str
    date_to: str


@dataclass(frozen=True)
class CommitRange:
    """コミットID範囲指定。"""
    commit_from: str
    commit_to: str


@dataclass(frozen=True)
class DiffStat:
    """ファイルごとの差分行数統計。"""
    path: str
    added: int
    deleted: int


@dataclass(frozen=True)
class ExtractConfig:
    """CLI引数から生成される抽出設定。"""
    range_spec: DateRange | CommitRange
    dirs: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    output_dir: Path = field(default_factory=lambda: Path("output/git_diff"))


# ---------------------------------------------------------------------------
# Git操作
# ---------------------------------------------------------------------------

def _run_git(*args: str, binary: bool = False) -> str:
    """gitコマンドを実行して標準出力を返す。"""
    result: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=not binary,
        check=True,
    )
    if binary:
        # binary=True時はbytesが返るが、型注釈の都合上strとして扱わない
        # → この関数はtext出力専用。バイナリ用は別関数を使う
        raise ValueError("Use _run_git_bytes for binary output")
    return result.stdout


def _run_git_bytes(*args: str) -> bytes:
    """gitコマンドを実行してバイト列で標準出力を返す。"""
    result: subprocess.CompletedProcess[bytes] = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=False,
        check=True,
    )
    return result.stdout


def _validate_commit(commit_id: str) -> str:
    """コミットIDの存在を検証し、完全なSHAを返す。"""
    output: str = _run_git("rev-parse", "--verify", commit_id)
    return output.strip()


def _check_has_parent(commit_sha: str) -> bool:
    """コミットに親があるかを確認する。"""
    try:
        _run_git("rev-parse", "--verify", f"{commit_sha}^")
        return True
    except subprocess.CalledProcessError:
        return False


def _resolve_date_range(date_range: DateRange) -> tuple[str, str]:
    """日付範囲からコミットSHA範囲を解決する。"""
    output: str = _run_git(
        "log", "--format=%H", "--reverse",
        f"--since={date_range.date_from}",
        f"--until={date_range.date_to}",
    )
    lines: list[str] = [line for line in output.strip().splitlines() if line]
    if not lines:
        logger.error("No commits found in date range: %s to %s",
                      date_range.date_from, date_range.date_to)
        sys.exit(1)
    start_sha: str = lines[0]
    end_sha: str = lines[-1]
    return start_sha, end_sha


def _resolve_commit_range(commit_range: CommitRange) -> tuple[str, str]:
    """コミットID範囲を検証してSHAを返す。"""
    try:
        start_sha: str = _validate_commit(commit_range.commit_from)
    except subprocess.CalledProcessError:
        logger.error("Invalid start commit: %s", commit_range.commit_from)
        sys.exit(1)
    try:
        end_sha: str = _validate_commit(commit_range.commit_to)
    except subprocess.CalledProcessError:
        logger.error("Invalid end commit: %s", commit_range.commit_to)
        sys.exit(1)
    return start_sha, end_sha


def resolve_commit_range(config: ExtractConfig) -> tuple[str, str]:
    """設定に基づきコミットSHA範囲を解決する。"""
    if isinstance(config.range_spec, DateRange):
        return _resolve_date_range(config.range_spec)
    return _resolve_commit_range(config.range_spec)


# ---------------------------------------------------------------------------
# コミット・変更ファイル取得
# ---------------------------------------------------------------------------

def get_commit_list(start_sha: str, end_sha: str) -> list[CommitInfo]:
    """範囲内のコミット一覧を取得する。"""
    has_parent: bool = _check_has_parent(start_sha)
    range_spec: str = f"{start_sha}^..{end_sha}" if has_parent else f"{start_sha}..{end_sha}"

    output: str = _run_git("log", "--format=%H\t%s", "--reverse", range_spec)
    commits: list[CommitInfo] = []

    # start_sha自体が含まれない場合（親なし）、先頭コミットを追加
    if not has_parent:
        start_output: str = _run_git("log", "--format=%H\t%s", "-1", start_sha)
        start_line: str = start_output.strip()
        if start_line:
            parts: list[str] = start_line.split("\t", 1)
            commits.append(CommitInfo(
                commit_id=parts[0],
                message=parts[1] if len(parts) > 1 else "",
            ))

    for line in output.strip().splitlines():
        if not line:
            continue
        parts = line.split("\t", 1)
        commits.append(CommitInfo(
            commit_id=parts[0],
            message=parts[1] if len(parts) > 1 else "",
        ))
    return commits


def get_changed_files(start_sha: str, end_sha: str) -> list[ChangedFile]:
    """範囲内で変更されたファイル一覧を取得する。"""
    has_parent: bool = _check_has_parent(start_sha)
    diff_from: str = f"{start_sha}^" if has_parent else start_sha

    output: str = _run_git(
        "diff", "--name-status", "--diff-filter=ADM",
        diff_from, end_sha,
    )
    files: list[ChangedFile] = []
    status_map: dict[str, FileChangeStatus] = {
        "A": FileChangeStatus.ADDED,
        "M": FileChangeStatus.MODIFIED,
        "D": FileChangeStatus.DELETED,
    }
    for line in output.strip().splitlines():
        if not line:
            continue
        parts: list[str] = line.split("\t", 1)
        if len(parts) < 2:
            continue
        status_char: str = parts[0].strip()
        file_path: str = parts[1].strip()
        status: FileChangeStatus | None = status_map.get(status_char)
        if status is not None:
            files.append(ChangedFile(path=file_path, status=status))
    return files


# ---------------------------------------------------------------------------
# フィルタ
# ---------------------------------------------------------------------------

def filter_files(
    files: list[ChangedFile],
    config: ExtractConfig,
) -> list[ChangedFile]:
    """ディレクトリ・拡張子でフィルタする。"""
    filtered: list[ChangedFile] = []
    for f in files:
        # ディレクトリフィルタ
        if config.dirs:
            matched: bool = any(
                f.path == d or f.path.startswith(d.rstrip("/") + "/")
                for d in config.dirs
            )
            if not matched:
                continue
        # 拡張子フィルタ
        if config.extensions:
            ext_matched: bool = any(
                f.path.endswith(ext) for ext in config.extensions
            )
            if not ext_matched:
                continue
        filtered.append(f)
    return filtered


# ---------------------------------------------------------------------------
# 統計・分析
# ---------------------------------------------------------------------------

# コミットメッセージから課題IDを抽出するパターン
# 例: m1, m2, H-1, H-2, C-2026-003, S-DA-006, S-SCENARIO-001,
#      GUI-DA-003, GUI-IMP-001, #123
_ISSUE_ID_PATTERN: re.Pattern[str] = re.compile(
    r"(?:(?:[A-Z]+-)?[A-Z]+-\d+(?:-\d+)?)"  # H-1, C-2026-003, S-DA-006, GUI-IMP-001
    r"|(?:m\d+)"                               # m1, m2, ...
    r"|(?:#\d+)",                              # #123
    re.IGNORECASE,
)

# コミット種別プレフィックス
_COMMIT_TYPE_PATTERN: re.Pattern[str] = re.compile(
    r"^(feat|fix|refactor|docs|style|test|chore|perf|ci|build|revert)"
    r"(?:\(.+?\))?:",
    re.IGNORECASE,
)


def get_diff_stats(
    start_sha: str, end_sha: str, files: list[ChangedFile],
) -> dict[str, DiffStat]:
    """ファイルごとの追加・削除行数を取得する。"""
    has_parent: bool = _check_has_parent(start_sha)
    diff_from: str = f"{start_sha}^" if has_parent else start_sha

    output: str = _run_git("diff", "--numstat", diff_from, end_sha)
    file_set: set[str] = {f.path for f in files}
    stats: dict[str, DiffStat] = {}

    for line in output.strip().splitlines():
        if not line:
            continue
        parts: list[str] = line.split("\t", 2)
        if len(parts) < 3:
            continue
        added_str, deleted_str, path = parts
        if path not in file_set:
            continue
        # バイナリファイルは "-" で表示される
        added: int = int(added_str) if added_str != "-" else 0
        deleted: int = int(deleted_str) if deleted_str != "-" else 0
        stats[path] = DiffStat(path=path, added=added, deleted=deleted)

    return stats


def extract_issue_ids(commits: list[CommitInfo]) -> dict[str, list[CommitInfo]]:
    """コミットメッセージから課題IDを抽出し、ID→コミットリストのマップを返す。"""
    issue_map: dict[str, list[CommitInfo]] = defaultdict(list)
    for c in commits:
        ids: list[str] = _ISSUE_ID_PATTERN.findall(c.message)
        for issue_id in ids:
            issue_map[issue_id].append(c)
    return dict(issue_map)


def classify_commit_types(commits: list[CommitInfo]) -> Counter[str]:
    """コミットメッセージのプレフィックスで種別を分類する。"""
    type_counter: Counter[str] = Counter()
    for c in commits:
        m: re.Match[str] | None = _COMMIT_TYPE_PATTERN.match(c.message)
        commit_type: str = m.group(1).lower() if m else "other"
        type_counter[commit_type] += 1
    return type_counter


def aggregate_by_directory(
    files: list[ChangedFile], depth: int = 2,
) -> dict[str, dict[str, int]]:
    """ディレクトリ単位でA/M/Dファイル数を集計する。

    depthはパスの何階層目までをキーにするか（例: depth=2 → src/models）。
    """
    dir_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"A": 0, "M": 0, "D": 0, "total": 0},
    )
    for f in files:
        parts: list[str] = f.path.split("/")
        dir_key: str = "/".join(parts[:depth]) if len(parts) > depth else "/".join(parts[:-1]) or "."
        dir_stats[dir_key][f.status.value] += 1
        dir_stats[dir_key]["total"] += 1
    return dict(dir_stats)


# ---------------------------------------------------------------------------
# ファイル抽出・差分生成
# ---------------------------------------------------------------------------

def prepare_output_dir(output_dir: Path) -> None:
    """出力ディレクトリを初期化する。"""
    output_dir.mkdir(parents=True, exist_ok=True)

    diff_dir: Path = output_dir / "diff"
    diff_zip_path: Path = output_dir / "diff.zip"
    report_path: Path = output_dir / "report.md"

    if diff_dir.exists():
        shutil.rmtree(diff_dir)
    if diff_zip_path.exists():
        diff_zip_path.unlink()
    if report_path.exists():
        report_path.unlink()


def _get_file_at_commit(commit_sha: str, file_path: str) -> bytes | None:
    """特定コミット時点のファイル内容を取得する。取得失敗時はNoneを返す。"""
    try:
        return _run_git_bytes("show", f"{commit_sha}:{file_path}")
    except subprocess.CalledProcessError:
        return None


def extract_file_versions(
    files: list[ChangedFile],
    start_sha: str,
    end_sha: str,
    output_dir: Path,
) -> None:
    """before/afterのファイルを出力ディレクトリに保存する。"""
    diff_dir: Path = output_dir / "diff"
    before_dir: Path = diff_dir / "before"
    after_dir: Path = diff_dir / "after"

    has_parent: bool = _check_has_parent(start_sha)
    # before取得元: 開始コミットの直前（親）
    before_ref: str = f"{start_sha}^" if has_parent else start_sha

    for f in files:
        # before側（削除・変更ファイル）
        if f.status in (FileChangeStatus.DELETED, FileChangeStatus.MODIFIED):
            content: bytes | None = _get_file_at_commit(before_ref, f.path)
            if content is not None:
                before_path: Path = before_dir / f.path
                before_path.parent.mkdir(parents=True, exist_ok=True)
                before_path.write_bytes(content)
            else:
                logger.warning("Failed to get before version: %s", f.path)

        # after側（追加・変更ファイル）
        if f.status in (FileChangeStatus.ADDED, FileChangeStatus.MODIFIED):
            content = _get_file_at_commit(end_sha, f.path)
            if content is not None:
                after_path: Path = after_dir / f.path
                after_path.parent.mkdir(parents=True, exist_ok=True)
                after_path.write_bytes(content)
            else:
                logger.warning("Failed to get after version: %s", f.path)


def _read_text_or_binary_placeholder(path: Path) -> list[str]:
    """テキストファイルを行リストで返す。バイナリならプレースホルダを返す。"""
    try:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (UnicodeDecodeError, FileNotFoundError):
        return ["(Binary file)\n"]


def generate_diffs(files: list[ChangedFile], output_dir: Path) -> None:
    """unified diff ファイルを生成する。"""
    diff_dir: Path = output_dir / "diff"
    before_dir: Path = diff_dir / "before"
    after_dir: Path = diff_dir / "after"

    for f in files:
        before_path: Path = before_dir / f.path
        after_path: Path = after_dir / f.path

        before_lines: list[str] = (
            _read_text_or_binary_placeholder(before_path)
            if before_path.exists() else []
        )
        after_lines: list[str] = (
            _read_text_or_binary_placeholder(after_path)
            if after_path.exists() else []
        )

        diff_lines: list[str] = list(difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"a/{f.path}",
            tofile=f"b/{f.path}",
        ))

        if diff_lines:
            diff_path: Path = diff_dir / (f.path + ".diff")
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path.write_text("".join(diff_lines), encoding="utf-8")


def archive_diff_dir(output_dir: Path) -> None:
    """diffディレクトリをzip化し、展開ディレクトリを削除する。"""
    diff_dir: Path = output_dir / "diff"
    if not diff_dir.exists():
        logger.warning("Diff directory does not exist: %s", diff_dir)
        return

    archive_base_path: Path = output_dir / "diff"
    shutil.make_archive(
        base_name=str(archive_base_path),
        format="zip",
        root_dir=output_dir,
        base_dir=diff_dir.name,
    )
    shutil.rmtree(diff_dir)


# ---------------------------------------------------------------------------
# レポート生成
# ---------------------------------------------------------------------------

def _render_file_tree(
    lines: list[str],
    files: list[ChangedFile],
    diff_stats: dict[str, DiffStat],
) -> None:
    """ファイル一覧をマークダウンのネストリスト形式で描画する。

    ファイル名はdiff配下のunified diffファイルへの相対リンクにする。
    """
    sorted_files: list[ChangedFile] = sorted(files, key=lambda f: f.path)

    # ディレクトリ→子要素のツリー構造を構築
    tree: dict[str, object] = {}
    file_info: dict[str, ChangedFile] = {}
    for f in sorted_files:
        parts: list[str] = f.path.split("/")
        node: dict[str, object] = tree
        for part in parts[:-1]:
            if part not in node:
                node[part] = {}
            next_node: object = node[part]
            if isinstance(next_node, dict):
                node = next_node
            else:
                break
        node[parts[-1]] = None  # リーフ（ファイル）
        file_info[f.path] = f

    def _render(
        node: dict[str, object],
        depth: int,
        path_parts: list[str],
    ) -> None:
        indent: str = "  " * depth
        for name, child in node.items():
            if child is None:
                # ファイル（リーフ） — diffへのリンク付き
                full_path: str = "/".join([*path_parts, name])
                f_info: ChangedFile | None = file_info.get(full_path)
                status_char: str = f_info.status.value if f_info else "?"
                stat: DiffStat | None = diff_stats.get(full_path)
                stat_str: str = f" (+{stat.added}, -{stat.deleted})" if stat else ""
                diff_link: str = f"diff/{full_path}.diff"
                lines.append(
                    f"{indent}- [{name}]({diff_link}) "
                    f"`[{status_char}]`{stat_str}\n",
                )
            else:
                # ディレクトリ
                assert isinstance(child, dict)
                lines.append(f"{indent}- **{name}/**\n")
                _render(child, depth + 1, [*path_parts, name])

    _render(tree, 0, [])


def generate_report(
    commits: list[CommitInfo],
    files: list[ChangedFile],
    start_sha: str,
    end_sha: str,
    output_dir: Path,
    diff_stats: dict[str, DiffStat],
) -> None:
    """report.mdを生成する。"""
    lines: list[str] = []
    lines.append("# Git Diff Report\n\n")
    lines.append("## Artifacts\n\n")
    lines.append("- Unified diff archive: [diff.zip](diff.zip)\n")
    lines.append("- `diff.zip` を同じディレクトリで展開すると、以下の `diff/...` リンクを参照できる\n\n")

    # 範囲情報
    lines.append("## Range\n\n")
    lines.append(f"- From: `{start_sha[:8]}`\n")
    lines.append(f"- To: `{end_sha[:8]}`\n\n")

    # --- サマリー統計 ---
    total_added: int = sum(s.added for s in diff_stats.values())
    total_deleted: int = sum(s.deleted for s in diff_stats.values())
    added_files: list[ChangedFile] = [f for f in files if f.status == FileChangeStatus.ADDED]
    modified_files: list[ChangedFile] = [f for f in files if f.status == FileChangeStatus.MODIFIED]
    deleted_files: list[ChangedFile] = [f for f in files if f.status == FileChangeStatus.DELETED]

    lines.append("## Summary\n\n")
    lines.append(f"- Commits: **{len(commits)}**\n")
    lines.append(f"- Files changed: **{len(files)}** "
                 f"(Added: {len(added_files)}, Modified: {len(modified_files)}, "
                 f"Deleted: {len(deleted_files)})\n")
    lines.append(f"- Lines: **+{total_added}** / **-{total_deleted}**\n\n")

    # --- コミット種別分布 ---
    type_counts: Counter[str] = classify_commit_types(commits)
    lines.append("## Commit Types\n\n")
    lines.append("| Type | Count |\n")
    lines.append("|------|-------|\n")
    for ctype, count in type_counts.most_common():
        lines.append(f"| {ctype} | {count} |\n")
    lines.append("\n")

    # --- 課題ID別コミット ---
    issue_map: dict[str, list[CommitInfo]] = extract_issue_ids(commits)
    if issue_map:
        lines.append("## Issue / Ticket References\n\n")
        lines.append("| Issue ID | Commits | Messages (first) |\n")
        lines.append("|----------|---------|-------------------|\n")
        for issue_id, issue_commits in sorted(issue_map.items()):
            first_msg: str = issue_commits[0].message[:80]
            lines.append(
                f"| {issue_id} | {len(issue_commits)} | {first_msg} |\n",
            )
        lines.append("\n")

    # --- ディレクトリ別変更集計 ---
    dir_agg: dict[str, dict[str, int]] = aggregate_by_directory(files)
    lines.append("## Changes by Directory\n\n")
    lines.append("| Directory | Added | Modified | Deleted | Total |\n")
    lines.append("|-----------|-------|----------|---------|-------|\n")
    for dir_path, counts in sorted(dir_agg.items(), key=lambda x: -x[1]["total"]):
        lines.append(
            f"| `{dir_path}` | {counts['A']} | {counts['M']} | {counts['D']} "
            f"| {counts['total']} |\n",
        )
    lines.append("\n")

    # --- コミット一覧（課題ID付き） ---
    lines.append(f"## Commits ({len(commits)})\n\n")
    lines.append("| # | Issue ID | Commit | Message |\n")
    lines.append("|---|----------|--------|--------|\n")
    prev_ids_str: str = ""
    for i, c in enumerate(commits, 1):
        ids: list[str] = _ISSUE_ID_PATTERN.findall(c.message)
        ids_str: str = ", ".join(ids) if ids else ""
        # 直前と同じIDセットなら空にする
        display_ids: str = ids_str if ids_str != prev_ids_str else ""
        prev_ids_str = ids_str
        lines.append(
            f"| {i} | {display_ids} | `{c.commit_id[:8]}` | {c.message} |\n",
        )
    lines.append("\n")

    # --- 変更ファイル一覧（ツリー形式） ---
    lines.append(f"## Changed Files ({len(files)})\n\n")
    _render_file_tree(lines, files, diff_stats)
    lines.append("\n")

    report_path: Path = output_dir / "report.md"
    report_path.write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_config(args: argparse.Namespace) -> ExtractConfig:
    """CLI引数からExtractConfigを構築する。"""
    date_from: str | None = args.date_from
    date_to: str | None = args.date_to
    commit_from: str | None = args.commit_from
    commit_to: str | None = args.commit_to
    dirs: list[str] = args.dirs
    extensions: list[str] = args.extensions
    output: Path = args.output

    has_date: bool = date_from is not None or date_to is not None
    has_commit: bool = commit_from is not None or commit_to is not None

    if has_date and has_commit:
        logger.error("Cannot specify both date range and commit range")
        sys.exit(1)
    if not has_date and not has_commit:
        logger.error("Must specify either date range (--date-from/--date-to) "
                      "or commit range (--commit-from/--commit-to)")
        sys.exit(1)

    range_spec: DateRange | CommitRange
    if has_date:
        if date_from is None or date_to is None:
            logger.error("Both --date-from and --date-to are required")
            sys.exit(1)
        range_spec = DateRange(date_from=date_from, date_to=date_to)
    else:
        if commit_from is None or commit_to is None:
            logger.error("Both --commit-from and --commit-to are required")
            sys.exit(1)
        range_spec = CommitRange(commit_from=commit_from, commit_to=commit_to)

    return ExtractConfig(
        range_spec=range_spec,
        dirs=dirs,
        extensions=extensions,
        output_dir=output,
    )


def main() -> None:
    """CLIエントリポイント。"""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Extract git diffs for a specified range of commits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # 日付範囲指定
  python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01

  # コミットID範囲指定
  python tools/extract_git_diff.py --commit-from abc1234 --commit-to def5678

  # ディレクトリ・拡張子フィルタ付き
  python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01 -d src tests -e .py

  # 出力先指定
  python tools/extract_git_diff.py --commit-from abc1234 --commit-to def5678 -o output/my_diff
        """,
    )

    # 日付範囲指定
    date_group: argparse._ArgumentGroup = parser.add_argument_group("date range")
    date_group.add_argument("--date-from", type=str, default=None,
                            help="Start date (ISO format, e.g. 2024-01-01)")
    date_group.add_argument("--date-to", type=str, default=None,
                            help="End date (ISO format, e.g. 2024-02-01)")

    # コミットID範囲指定
    commit_group: argparse._ArgumentGroup = parser.add_argument_group("commit range")
    commit_group.add_argument("--commit-from", type=str, default=None,
                              help="Start commit ID (inclusive)")
    commit_group.add_argument("--commit-to", type=str, default=None,
                              help="End commit ID (inclusive)")

    # フィルタオプション
    parser.add_argument("--dirs", "-d", nargs="+", default=[],
                        help="Target directories to filter (e.g. src tests)")
    parser.add_argument("--extensions", "-e", nargs="+", default=[],
                        help="File extensions to filter (e.g. .py .ts)")

    # 出力
    parser.add_argument("--output", "-o", type=Path,
                        default=Path("output/git_diff"),
                        help="Output directory (default: output/git_diff)")

    parsed_args: argparse.Namespace = parser.parse_args()

    try:
        config: ExtractConfig = _build_config(parsed_args)

        # コミット範囲を解決
        start_sha: str
        end_sha: str
        start_sha, end_sha = resolve_commit_range(config)
        logger.info("Commit range: %s..%s", start_sha[:8], end_sha[:8])

        # コミット一覧取得
        commits: list[CommitInfo] = get_commit_list(start_sha, end_sha)
        logger.info("Found %d commits", len(commits))

        # 変更ファイル取得
        all_files: list[ChangedFile] = get_changed_files(start_sha, end_sha)
        files: list[ChangedFile] = filter_files(all_files, config)
        logger.info("Found %d changed files (%d after filter)",
                     len(all_files), len(files))

        if not files:
            logger.info("No files to process")
            sys.exit(0)

        # 出力ディレクトリ準備
        prepare_output_dir(config.output_dir)

        # ファイル抽出
        extract_file_versions(files, start_sha, end_sha, config.output_dir)

        # 差分生成
        generate_diffs(files, config.output_dir)

        # 差分行数統計取得
        diff_stats: dict[str, DiffStat] = get_diff_stats(start_sha, end_sha, files)

        # レポート生成
        generate_report(commits, files, start_sha, end_sha, config.output_dir, diff_stats)

        # diff成果物を圧縮し、展開ディレクトリは残さない
        archive_diff_dir(config.output_dir)

        logger.info("Output written to: %s", config.output_dir)
    except subprocess.CalledProcessError as e:
        logger.error("Git command failed: %s", e.stderr or e)
        sys.exit(1)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
