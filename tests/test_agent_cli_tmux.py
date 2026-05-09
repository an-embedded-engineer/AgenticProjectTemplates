from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "agent_cli_tmux.py"


def load_agent_cli_tmux():
    spec = importlib.util.spec_from_file_location("agent_cli_tmux", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Failed to load agent_cli_tmux.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_agent_command_builder_builds_codex_command() -> None:
    module = load_agent_cli_tmux()
    builder = module.AgentCommandBuilder()

    command = builder.build(
        module.AgentCommandSpec(
            agent="codex",
            mode="start",
            model=None,
            cwd=Path("/project path"),
        )
    )

    assert command == (
        "codex --no-alt-screen -C '/project path' -s workspace-write -a on-request"
    )


def test_agent_command_builder_builds_claude_command_as_single_string() -> None:
    module = load_agent_cli_tmux()
    builder = module.AgentCommandBuilder()

    command = builder.build(
        module.AgentCommandSpec(
            agent="claude",
            mode="start",
            model=None,
            cwd=Path("/project"),
        )
    )

    assert command == "TERM=dumb claude"


def test_agent_command_builder_builds_copilot_continue_command() -> None:
    module = load_agent_cli_tmux()
    builder = module.AgentCommandBuilder()

    command = builder.build(
        module.AgentCommandSpec(
            agent="copilot",
            mode="continue",
            model="claude-sonnet-4.6",
            cwd=Path("/project"),
        )
    )

    assert command == "copilot --continue --model claude-sonnet-4.6 --no-ask-user"


def test_copilot_requires_model() -> None:
    module = load_agent_cli_tmux()
    builder = module.AgentCommandBuilder()

    try:
        builder.build(
            module.AgentCommandSpec(
                agent="copilot",
                mode="start",
                model=None,
                cwd=Path("/project"),
            )
        )
    except ValueError as exc:
        assert str(exc) == "copilot requires --model"
    else:
        raise AssertionError("Expected ValueError")


def test_start_dry_run_prints_tmux_new_session_and_send_keys() -> None:
    result = run_script(
        "start",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.0",
        "--cwd",
        str(REPO_ROOT),
        "--agent",
        "codex",
    )

    assert result.returncode == 0
    assert "tmux new-session -d -s template-test" in result.stdout
    assert "tmux send-keys -t template-test:0.0" in result.stdout
    assert "codex --no-alt-screen" in result.stdout


def test_ensure_dry_run_without_mode_uses_default_ensure_mode() -> None:
    result = run_script(
        "ensure",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.0",
        "--cwd",
        str(REPO_ROOT),
        "--agent",
        "copilot",
        "--model",
        "claude-sonnet-4.6",
    )

    assert result.returncode == 0
    assert "copilot --continue --model claude-sonnet-4.6 --no-ask-user" in result.stdout


def test_send_prompt_dry_run_prints_buffer_and_enter(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("review this\n", encoding="utf-8")

    result = run_script(
        "send-prompt",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.1",
        "--file",
        str(prompt_file),
    )

    assert result.returncode == 0
    assert f"tmux load-buffer {prompt_file}" in result.stdout
    assert "tmux paste-buffer -t template-test:0.1" in result.stdout
    assert "tmux send-keys -t template-test:0.1 Enter" in result.stdout


def test_send_prompt_dry_run_can_sleep_then_capture(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("review this\n", encoding="utf-8")

    result = run_script(
        "send-prompt",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.1",
        "--file",
        str(prompt_file),
        "--sleep-after",
        "5",
        "--capture-after-sleep",
        "--lines",
        "320",
    )

    assert result.returncode == 0
    assert "tmux send-keys -t template-test:0.1 Enter" in result.stdout
    assert "sleep 5" in result.stdout
    assert "tmux capture-pane -t template-test:0.1 -p -S -320" in result.stdout


def test_send_prompt_dry_run_can_delay_submit_then_sleep_then_capture(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("review this\n", encoding="utf-8")

    result = run_script(
        "send-prompt",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.1",
        "--file",
        str(prompt_file),
        "--submit-delay",
        "5",
        "--sleep-after",
        "10",
        "--capture-after-sleep",
        "--lines",
        "320",
    )

    assert result.returncode == 0
    output_lines = result.stdout.splitlines()
    assert output_lines == [
        f"tmux load-buffer {prompt_file.resolve()}",
        "tmux paste-buffer -t template-test:0.1",
        "sleep 5",
        "tmux send-keys -t template-test:0.1 Enter",
        "sleep 10",
        "tmux capture-pane -t template-test:0.1 -p -S -320",
    ]


def test_send_prompt_dry_run_allows_missing_file() -> None:
    missing_prompt_file = REPO_ROOT / "tmp" / "template_missing_prompt_for_dry_run.md"

    result = run_script(
        "send-prompt",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.1",
        "--file",
        str(missing_prompt_file),
    )

    assert result.returncode == 0
    expected_path = missing_prompt_file.resolve()
    assert f"tmux load-buffer {expected_path}" in result.stdout


def test_stop_dry_run_sends_exit_to_pane() -> None:
    result = run_script(
        "stop",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0.0",
        "--agent",
        "claude",
    )

    assert result.returncode == 0
    assert "tmux send-keys -t template-test:0.0 /exit Enter" in result.stdout


def test_sleep_dry_run_prints_sleep_duration() -> None:
    result = run_script("sleep", "--dry-run", "30")

    assert result.returncode == 0
    assert result.stdout == "sleep 30\n"


def test_sleep_rejects_negative_duration() -> None:
    result = run_script("sleep", "--dry-run", "-1")

    assert result.returncode == 2
    assert "sleep seconds must be zero or positive" in result.stderr


def test_invalid_pane_returns_error() -> None:
    result = run_script(
        "start",
        "--dry-run",
        "--session",
        "template-test",
        "--pane",
        "0",
        "--cwd",
        str(REPO_ROOT),
        "--agent",
        "claude",
    )

    assert result.returncode == 2
    assert "--pane must be in window.pane format" in result.stderr
