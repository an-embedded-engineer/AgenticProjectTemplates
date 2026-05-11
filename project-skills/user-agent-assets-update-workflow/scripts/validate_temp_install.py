#!/usr/bin/env python3
"""user-agent-assets の tmp 仮インストール結果を検証する。"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


TARGET_SKILL_ROOTS = {
    "copilot": [Path(".copilot/skills"), Path(".agents/skills")],
    "claude": [Path(".claude/skills")],
    "codex": [Path(".codex/skills")],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate user-agent-assets install into a temporary HOME."
    )
    parser.add_argument("--source-root", default="user-agent-assets")
    parser.add_argument("--install-script", default=None)
    parser.add_argument("--temp-root", default="tmp/user-agent-assets-install-check")
    parser.add_argument("--targets", default="copilot,claude,codex")
    parser.add_argument("--mode", choices=("missing", "overwrite"), default="overwrite")
    parser.add_argument(
        "--exact-skill",
        action="append",
        default=[],
        help="Skill name that must match source exactly. Can be specified multiple times.",
    )
    parser.add_argument(
        "--forbid-skill",
        action="append",
        default=[],
        help="Skill name that must not be installed. Can be specified multiple times.",
    )
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    repo_root = Path.cwd().resolve()
    source_root = Path(args.source_root).resolve()
    temp_root = Path(args.temp_root).resolve()
    install_script = (
        Path(args.install_script).resolve()
        if args.install_script
        else source_root / "install" / "install_user_agent_assets.sh"
    )

    if not source_root.is_dir():
        fail(f"source root not found: {source_root}")
    if not install_script.is_file():
        fail(f"install script not found: {install_script}")
    if args.clean and not temp_root.is_relative_to(repo_root):
        fail(f"refuse to clean outside repository: {temp_root}")
    return repo_root, source_root, install_script, temp_root


def run_install(
    source_root: Path, install_script: Path, temp_home: Path, targets: str, mode: str
) -> None:
    env = os.environ.copy()
    env["HOME"] = str(temp_home)
    command = [
        "bash",
        str(install_script),
        "--mode",
        mode,
        "--targets",
        targets,
        "--source-root",
        str(source_root),
    ]
    print("Running temp install:", flush=True)
    print("  " + " ".join(command), flush=True)
    subprocess.run(command, env=env, check=True)


def source_skill_dirs(source_root: Path) -> list[Path]:
    skills_root = source_root / "skills"
    if not skills_root.is_dir():
        fail(f"skills directory not found: {skills_root}")
    return sorted(path for path in skills_root.iterdir() if path.is_dir())


def compare_file(source_file: Path, target_file: Path) -> None:
    if not target_file.is_file():
        fail(f"missing installed file: {target_file}")
    if not filecmp.cmp(source_file, target_file, shallow=False):
        fail(f"installed file differs: {target_file}")


def ensure_source_files_present(source_dir: Path, target_dir: Path) -> None:
    for source_file in source_dir.rglob("*"):
        relative = source_file.relative_to(source_dir)
        target_file = target_dir / relative
        if source_file.is_dir():
            if not target_file.is_dir():
                fail(f"missing installed directory: {target_file}")
            continue
        compare_file(source_file, target_file)


def ensure_exact_dir(source_dir: Path, target_dir: Path) -> None:
    source_paths = {
        path.relative_to(source_dir)
        for path in source_dir.rglob("*")
    }
    target_paths = {
        path.relative_to(target_dir)
        for path in target_dir.rglob("*")
    }
    extra_paths = sorted(target_paths - source_paths)
    if extra_paths:
        fail(f"unexpected extra paths under {target_dir}: {extra_paths[:5]}")
    ensure_source_files_present(source_dir, target_dir)


def validate_skill_targets(
    source_root: Path,
    temp_home: Path,
    targets: list[str],
    exact_skills: set[str],
    forbidden_skills: set[str],
) -> None:
    source_skills = source_skill_dirs(source_root)
    source_names = {path.name for path in source_skills}

    for target in targets:
        if target not in TARGET_SKILL_ROOTS:
            fail(f"unsupported target: {target}")

        for relative_root in TARGET_SKILL_ROOTS[target]:
            target_root = temp_home / relative_root
            if not target_root.is_dir():
                fail(f"target skill root not found: {target_root}")

            installed_names = {
                path.name for path in target_root.iterdir() if path.is_dir()
            }
            forbidden_installed = sorted(forbidden_skills & installed_names)
            if forbidden_installed:
                fail(
                    f"forbidden skills installed at {target_root}: "
                    f"{forbidden_installed}"
                )
            if installed_names != source_names:
                missing = sorted(source_names - installed_names)
                extra = sorted(installed_names - source_names)
                fail(
                    f"skill set mismatch at {target_root}; "
                    f"missing={missing}, extra={extra}"
                )

            for source_skill in source_skills:
                target_skill = target_root / source_skill.name
                if source_skill.name in exact_skills:
                    ensure_exact_dir(source_skill, target_skill)
                else:
                    ensure_source_files_present(source_skill, target_skill)


def validate_runtime(source_root: Path, temp_home: Path) -> None:
    helper_root = temp_home / ".agentic-project-templates"
    required_paths = [
        helper_root / "bin" / "agentic-agent-cli-tmux.sh",
        helper_root / "bin" / "agentic-agent-cli-tmux.ps1",
        helper_root / "instructions",
        helper_root / "runtime" / "agent-cli-tmux",
    ]
    for path in required_paths:
        if not path.exists():
            fail(f"missing helper asset: {path}")

    shell_wrapper = helper_root / "bin" / "agentic-agent-cli-tmux.sh"
    if not shell_wrapper.stat().st_mode & stat.S_IXUSR:
        fail(f"shell wrapper is not executable: {shell_wrapper}")

    source_wrapper = source_root / "bin" / "agentic-agent-cli-tmux.sh"
    compare_file(source_wrapper, shell_wrapper)


def main() -> None:
    args = parse_args()
    _, source_root, install_script, temp_root = resolve_paths(args)
    temp_home = temp_root / "home"
    targets = [target for target in args.targets.split(",") if target]

    if args.clean and temp_root.exists():
        shutil.rmtree(temp_root)
    temp_home.mkdir(parents=True, exist_ok=True)

    run_install(source_root, install_script, temp_home, args.targets, args.mode)
    validate_skill_targets(
        source_root,
        temp_home,
        targets,
        set(args.exact_skill),
        set(args.forbid_skill),
    )
    validate_runtime(source_root, temp_home)

    print("Temp install validation passed.")
    print(f"Temp HOME: {temp_home}")
    print(f"Targets: {', '.join(targets)}")
    print(f"Source skills: {len(source_skill_dirs(source_root))}")


if __name__ == "__main__":
    main()
