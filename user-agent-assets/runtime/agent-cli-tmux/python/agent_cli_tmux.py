#!/usr/bin/env python3
"""tmux 経由の Agent CLI 操作を共通化する補助 CLI。"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


AGENT_CHOICES = ("codex", "claude", "copilot")
MODE_CHOICES = ("start", "continue")
SHELL_COMMANDS = {"bash", "fish", "sh", "zsh"}
PANE_PATTERN = re.compile(r"^\d+\.\d+$")
SIZE_PATTERN = re.compile(r"^(\d+)x(\d+)$")


@dataclass(frozen=True)
class AgentCommandSpec:
    agent: str
    mode: str
    model: str | None
    cwd: Path


@dataclass(frozen=True)
class TmuxTarget:
    session: str
    pane: str

    @property
    def value(self) -> str:
        return f"{self.session}:{self.pane}"


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class PaneProcess:
    command: str
    pid: str

    @property
    def is_shell(self) -> bool:
        return Path(self.command).name in SHELL_COMMANDS


class AgentCommandBuilder:
    def build(self, spec: AgentCommandSpec) -> str:
        if spec.agent == "codex":
            self._require_mode(spec, "start")
            return (
                "codex --no-alt-screen "
                f"-C {shlex.quote(str(spec.cwd))} "
                "-s workspace-write -a on-request"
            )
        if spec.agent == "claude":
            self._require_mode(spec, "start")
            return "TERM=dumb claude"
        if spec.agent == "copilot":
            if spec.mode == "start":
                return f"copilot --model {self._require_model(spec)} --no-ask-user"
            if spec.mode == "continue":
                return (
                    "copilot --continue "
                    f"--model {self._require_model(spec)} --no-ask-user"
                )
        raise ValueError(
            f"Unsupported agent/mode combination: {spec.agent}/{spec.mode}"
        )

    def exit_input(self, agent: str) -> str:
        if agent in AGENT_CHOICES:
            return "/exit"
        raise ValueError(f"Unsupported agent: {agent}")

    def default_mode_for_ensure(self, agent: str) -> str:
        if agent == "copilot":
            return "continue"
        if agent in ("codex", "claude"):
            return "start"
        raise ValueError(f"Unsupported agent: {agent}")

    def _require_mode(self, spec: AgentCommandSpec, expected: str) -> None:
        if spec.mode != expected:
            raise ValueError(f"{spec.agent} supports only {expected} mode")

    def _require_model(self, spec: AgentCommandSpec) -> str:
        if not spec.model:
            raise ValueError("copilot requires --model")
        return spec.model


class TmuxRunner:
    def __init__(self, dry_run: bool = False) -> None:
        self._dry_run = dry_run

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    def run(self, argv: list[str]) -> CommandResult:
        if self._dry_run:
            print(shlex.join(argv))
            return CommandResult(0, "", "")
        completed = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
        )
        return CommandResult(
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )

    def has_session(self, target: TmuxTarget) -> bool:
        result = self.run(["tmux", "has-session", "-t", target.session])
        return result.returncode == 0

    def has_pane(self, target: TmuxTarget) -> bool:
        result = self.run(
            [
                "tmux",
                "list-panes",
                "-t",
                f"{target.session}:0",
                "-F",
                "#{window_index}.#{pane_index}",
            ]
        )
        if result.returncode != 0:
            return False
        return target.pane in result.stdout.splitlines()

    def capture(self, target: TmuxTarget, lines: int) -> CommandResult:
        return self.run(
            ["tmux", "capture-pane", "-t", target.value, "-p", "-S", f"-{lines}"]
        )

    def sleep(self, seconds: float) -> None:
        if self._dry_run:
            print(f"sleep {format_seconds(seconds)}")
            return
        time.sleep(seconds)

    def current_process(self, target: TmuxTarget) -> PaneProcess | None:
        result = self.run(
            [
                "tmux",
                "display-message",
                "-p",
                "-t",
                target.value,
                "#{pane_current_command}\t#{pane_pid}",
            ]
        )
        if result.returncode != 0:
            return None
        parts = result.stdout.strip().split("\t")
        if len(parts) != 2 or not parts[0]:
            return None
        return PaneProcess(parts[0], parts[1])

    def new_session(self, target: TmuxTarget, cwd: Path, cols: int, rows: int) -> None:
        self._must_run(
            [
                "tmux",
                "new-session",
                "-d",
                "-s",
                target.session,
                "-x",
                str(cols),
                "-y",
                str(rows),
                "-c",
                str(cwd),
            ]
        )

    def split_window(
        self,
        target: TmuxTarget,
        cwd: Path,
        split: str,
        split_from: str | None,
    ) -> None:
        tmux_target = f"{target.session}:{split_from}" if split_from else target.session
        flag = "-h" if split == "horizontal" else "-v"
        self._must_run(
            ["tmux", "split-window", flag, "-t", tmux_target, "-c", str(cwd)]
        )

    def send_keys(self, target: TmuxTarget, *keys: str) -> None:
        self._must_run(["tmux", "send-keys", "-t", target.value, *keys])

    def load_and_paste(self, target: TmuxTarget, prompt_file: Path) -> None:
        self._must_run(["tmux", "load-buffer", str(prompt_file)])
        self._must_run(["tmux", "paste-buffer", "-t", target.value])

    def kill_session(self, target: TmuxTarget) -> None:
        self._must_run(["tmux", "kill-session", "-t", target.session])

    def _must_run(self, argv: list[str]) -> None:
        result = self.run(argv)
        if result.returncode != 0:
            stderr = result.stderr.strip() or "tmux command failed"
            raise RuntimeError(stderr)


def parse_target(args: argparse.Namespace) -> TmuxTarget:
    if not PANE_PATTERN.match(args.pane):
        raise ValueError("--pane must be in window.pane format, for example 0.0")
    return TmuxTarget(args.session, args.pane)


def parse_size(size: str) -> tuple[int, int]:
    match = SIZE_PATTERN.match(size)
    if not match:
        raise ValueError("--size must be in COLSxROWS format, for example 220x60")
    cols = int(match.group(1))
    rows = int(match.group(2))
    if cols <= 0 or rows <= 0:
        raise ValueError("--size values must be positive")
    return cols, rows


def resolve_cwd(cwd: str) -> Path:
    path = Path(cwd).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"--cwd must be an existing directory: {path}")
    return path


def parse_sleep_seconds(seconds: float) -> float:
    if seconds < 0:
        raise ValueError("sleep seconds must be zero or positive")
    return seconds


def format_seconds(seconds: float) -> str:
    if seconds.is_integer():
        return str(int(seconds))
    return str(seconds)


def start_agent(
    args: argparse.Namespace,
    runner: TmuxRunner,
    builder: AgentCommandBuilder,
    allow_existing_inactive: bool,
) -> int:
    target = parse_target(args)
    cwd = resolve_cwd(args.cwd)
    cols, rows = parse_size(args.size)

    if runner.dry_run:
        if allow_existing_inactive:
            mode = args.mode or builder.default_mode_for_ensure(args.agent)
        else:
            mode = args.mode or "start"
        command = builder.build(AgentCommandSpec(args.agent, mode, args.model, cwd))
        if target.pane == "0.0":
            runner.new_session(target, cwd, cols, rows)
        else:
            runner.split_window(target, cwd, args.split, args.split_from)
        runner.send_keys(target, command, "Enter")
        return 0

    if not runner.has_session(target):
        if target.pane != "0.0":
            raise RuntimeError("Cannot create a new session for non-0.0 pane")
        runner.new_session(target, cwd, cols, rows)
        mode = args.mode or "start"
    elif runner.has_pane(target):
        if not allow_existing_inactive:
            raise RuntimeError(f"Target pane already exists: {target.value}")
        process = runner.current_process(target)
        if process is None:
            raise RuntimeError(f"Cannot determine current process: {target.value}")
        if not process.is_shell:
            print(f"Agent process already appears active: {process.command}")
            return 0
        mode = args.mode or builder.default_mode_for_ensure(args.agent)
    else:
        runner.split_window(target, cwd, args.split, args.split_from)
        if not runner.has_pane(target):
            raise RuntimeError(f"Split did not create requested pane: {target.value}")
        mode = args.mode or "start"

    command = builder.build(AgentCommandSpec(args.agent, mode, args.model, cwd))
    runner.send_keys(target, command, "Enter")
    return 0


def send_prompt(args: argparse.Namespace, runner: TmuxRunner) -> int:
    target = parse_target(args)
    prompt_file = Path(args.file).expanduser().resolve()
    if not runner.dry_run and not prompt_file.is_file():
        raise ValueError(f"--file must be an existing file: {prompt_file}")
    if not runner.dry_run and (
        not runner.has_session(target) or not runner.has_pane(target)
    ):
        raise RuntimeError(f"Target pane does not exist: {target.value}")
    runner.load_and_paste(target, prompt_file)
    submit_delay = parse_sleep_seconds(args.submit_delay)
    if submit_delay > 0:
        runner.sleep(submit_delay)
    runner.send_keys(target, "Enter")
    sleep_after = parse_sleep_seconds(args.sleep_after)
    if sleep_after > 0:
        runner.sleep(sleep_after)
    if args.capture_after_sleep:
        result = runner.capture(target, args.lines)
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            return result.returncode
        sys.stdout.write(result.stdout)
    return 0


def capture_pane(args: argparse.Namespace, runner: TmuxRunner) -> int:
    target = parse_target(args)
    sleep_before = parse_sleep_seconds(args.sleep_before)
    if sleep_before > 0:
        runner.sleep(sleep_before)
    if not runner.has_session(target) or not runner.has_pane(target):
        raise RuntimeError(f"Target pane does not exist: {target.value}")
    result = runner.capture(target, args.lines)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode
    sys.stdout.write(result.stdout)
    return 0


def show_status(args: argparse.Namespace, runner: TmuxRunner) -> int:
    target = parse_target(args)
    sleep_before = parse_sleep_seconds(args.sleep_before)
    if sleep_before > 0:
        runner.sleep(sleep_before)
    session_exists = runner.has_session(target)
    pane_exists = session_exists and runner.has_pane(target)
    print(f"session: {target.session}")
    print(f"session_exists: {str(session_exists).lower()}")
    print(f"pane: {target.pane}")
    print(f"pane_exists: {str(pane_exists).lower()}")
    if not pane_exists:
        return 1

    process = runner.current_process(target)
    if process:
        print(f"current_command: {process.command}")
        print(f"pane_pid: {process.pid}")
    else:
        print("current_command: unknown")
        print("pane_pid: unknown")

    result = runner.capture(target, args.lines)
    print(f"capture_success: {str(result.returncode == 0).lower()}")
    if result.returncode == 0 and result.stdout:
        print("capture:")
        sys.stdout.write(result.stdout)
    elif result.returncode != 0:
        sys.stderr.write(result.stderr)
    return result.returncode


def sleep_only(args: argparse.Namespace, runner: TmuxRunner) -> int:
    runner.sleep(parse_sleep_seconds(args.seconds))
    return 0


def stop_agent(
    args: argparse.Namespace,
    runner: TmuxRunner,
    builder: AgentCommandBuilder,
) -> int:
    target = parse_target(args)
    exit_input = builder.exit_input(args.agent)
    if not runner.dry_run and (
        not runner.has_session(target) or not runner.has_pane(target)
    ):
        raise RuntimeError(f"Target pane does not exist: {target.value}")
    runner.send_keys(target, exit_input, "Enter")
    if args.kill_session:
        runner.kill_session(target)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Control Agent CLI processes through tmux."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_target(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--session", required=True)
        subparser.add_argument("--pane", required=True)

    def add_start_options(subparser: argparse.ArgumentParser) -> None:
        add_target(subparser)
        subparser.add_argument("--cwd", required=True)
        subparser.add_argument("--agent", choices=AGENT_CHOICES, required=True)
        subparser.add_argument("--mode", choices=MODE_CHOICES, default="start")
        subparser.add_argument("--model")
        subparser.add_argument("--size", default="220x60")
        subparser.add_argument(
            "--split", choices=("horizontal", "vertical"), default="horizontal"
        )
        subparser.add_argument("--split-from")
        subparser.add_argument("--dry-run", action="store_true")

    start_parser = subparsers.add_parser("start")
    add_start_options(start_parser)

    ensure_parser = subparsers.add_parser("ensure")
    add_start_options(ensure_parser)
    ensure_parser.set_defaults(mode=None)

    send_parser = subparsers.add_parser("send-prompt")
    add_target(send_parser)
    send_parser.add_argument("--file", required=True)
    send_parser.add_argument("--submit-delay", type=float, default=0.0)
    send_parser.add_argument("--sleep-after", type=float, default=0.0)
    send_parser.add_argument("--capture-after-sleep", action="store_true")
    send_parser.add_argument("--lines", type=int, default=120)
    send_parser.add_argument("--dry-run", action="store_true")

    capture_parser = subparsers.add_parser("capture")
    add_target(capture_parser)
    capture_parser.add_argument("--lines", type=int, default=120)
    capture_parser.add_argument("--sleep-before", type=float, default=0.0)

    status_parser = subparsers.add_parser("status")
    add_target(status_parser)
    status_parser.add_argument("--lines", type=int, default=20)
    status_parser.add_argument("--sleep-before", type=float, default=0.0)

    stop_parser = subparsers.add_parser("stop")
    add_target(stop_parser)
    stop_parser.add_argument("--agent", choices=AGENT_CHOICES, required=True)
    stop_parser.add_argument("--kill-session", action="store_true")
    stop_parser.add_argument("--dry-run", action="store_true")

    sleep_parser = subparsers.add_parser("sleep")
    sleep_parser.add_argument("seconds", type=float)
    sleep_parser.add_argument("--dry-run", action="store_true")

    return parser


def run_command(args: argparse.Namespace) -> int:
    arg_values = vars(args)
    dry_run = bool(arg_values["dry_run"]) if "dry_run" in arg_values else False
    runner = TmuxRunner(dry_run=dry_run)
    builder = AgentCommandBuilder()
    if args.command == "start":
        return start_agent(args, runner, builder, allow_existing_inactive=False)
    if args.command == "ensure":
        return start_agent(args, runner, builder, allow_existing_inactive=True)
    if args.command == "send-prompt":
        return send_prompt(args, runner)
    if args.command == "capture":
        return capture_pane(args, runner)
    if args.command == "status":
        return show_status(args, runner)
    if args.command == "stop":
        return stop_agent(args, runner, builder)
    if args.command == "sleep":
        return sleep_only(args, runner)
    raise ValueError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_command(args)
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
