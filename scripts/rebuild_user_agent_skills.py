from __future__ import annotations

import shutil
from pathlib import Path
from typing import TypedDict


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_SOURCE_ROOT = REPO_ROOT / "instructions" / "skills"
PROCEDURE_SOURCE_ROOT = REPO_ROOT / "docs" / "procedure"
SKILL_OUTPUT_ROOT = REPO_ROOT / "user-agent-assets" / "skills"
RUNTIME_HELPER_SOURCE = REPO_ROOT / "scripts" / "agent_cli_tmux.py"
RUNTIME_HELPER_DESTINATION = (
    REPO_ROOT / "user-agent-assets" / "runtime" / "agent-cli-tmux" / "python" / "agent_cli_tmux.py"
)
WRAPPER_PATH = "~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh"
WORKFLOW_SELECTION_LABEL = "workflow 判定ルール"
EXTERNAL_REVIEW_CHECKPOINTS = (
    "`ai-review-response-workflow` skill に同梱された "
    "`references/procedure/review_checkpoints.md`"
)
PROJECT_RULES_LABEL = "各プロジェクトのコーディング規約"
PROJECT_COMMANDS_LABEL = "各プロジェクトの開発・検証コマンド定義"

class SkillDefinition(TypedDict):
    procedures: list[str]
    phase_dirs: list[str]
    local_review_checkpoints: bool


WORKFLOW_SKILLS: dict[str, SkillDefinition] = {
    "spec-change-workflow": {
        "procedures": ["spec_change_workflow.md"],
        "phase_dirs": ["spec_change"],
        "local_review_checkpoints": False,
    },
    "new-feature-workflow": {
        "procedures": ["new_feature_workflow.md"],
        "phase_dirs": ["new_feature"],
        "local_review_checkpoints": False,
    },
    "bugfix-workflow": {
        "procedures": ["bugfix_workflow.md"],
        "phase_dirs": ["bugfix"],
        "local_review_checkpoints": False,
    },
    "issue-resolution-workflow": {
        "procedures": ["issue_resolution_workflow.md"],
        "phase_dirs": ["issue_resolution"],
        "local_review_checkpoints": False,
    },
    "refactoring-workflow": {
        "procedures": ["refactoring_workflow.md"],
        "phase_dirs": ["refactoring"],
        "local_review_checkpoints": False,
    },
    "research-analysis-workflow": {
        "procedures": ["research_analysis_workflow.md"],
        "phase_dirs": [],
        "local_review_checkpoints": False,
    },
    "ai-review-response-workflow": {
        "procedures": ["ai_review_response_workflow.md", "review_checkpoints.md"],
        "phase_dirs": [],
        "local_review_checkpoints": True,
    },
    "copilot-review-automation": {
        "procedures": [],
        "phase_dirs": [],
        "local_review_checkpoints": False,
    },
    "claude-review-automation": {
        "procedures": ["autonomous_workflow_orchestrator.md"],
        "phase_dirs": [],
        "local_review_checkpoints": False,
    },
    "autonomous-workflow-orchestrator": {
        "procedures": ["autonomous_workflow_orchestrator.md"],
        "phase_dirs": [],
        "local_review_checkpoints": False,
    },
    "copilot-cli-workflow-orchestrator": {
        "procedures": ["autonomous_workflow_orchestrator_copilot_cli.md"],
        "phase_dirs": [],
        "local_review_checkpoints": False,
    },
}


def rewrite_text(text: str, *, local_review_checkpoints: bool) -> str:
    text = text.replace("python scripts/agent_cli_tmux.py", WRAPPER_PATH)
    text = text.replace("scripts/agent_cli_tmux.py", WRAPPER_PATH)
    text = text.replace("`docs/procedure/workflow_selection.md`", WORKFLOW_SELECTION_LABEL)
    text = text.replace("AgenticProjectTemplatesの", "プロジェクトの")
    text = text.replace("docs/rules/coding_rules.md", PROJECT_RULES_LABEL)
    text = text.replace("docs/rules/development_workflow.md", PROJECT_COMMANDS_LABEL)
    text = text.replace("関連する Python pytest と .NET build/test を通し、検証エラーを 0 件にする", "対象プロジェクトで定義された検証コマンドを実行し、失敗を残さない")
    text = text.replace("関連する Python pytest と .NET build/test を通す", "対象プロジェクトで定義された検証コマンドを実行する")
    text = text.replace("agentic-project-templates", "agentic")

    if local_review_checkpoints:
        text = text.replace(
            "`docs/procedure/review_checkpoints.md`",
            "`references/procedure/review_checkpoints.md`",
        )
        text = text.replace(
            "docs/procedure/review_checkpoints.md",
            "references/procedure/review_checkpoints.md",
        )
    else:
        text = text.replace("`docs/procedure/review_checkpoints.md`", EXTERNAL_REVIEW_CHECKPOINTS)
        text = text.replace("docs/procedure/review_checkpoints.md", EXTERNAL_REVIEW_CHECKPOINTS)

    text = text.replace("docs/procedure/", "references/procedure/")

    return text


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sync_runtime_helper() -> None:
    RUNTIME_HELPER_DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RUNTIME_HELPER_SOURCE, RUNTIME_HELPER_DESTINATION)


def copy_skill_master(skill_name: str, *, local_review_checkpoints: bool) -> None:
    source = SKILL_SOURCE_ROOT / skill_name / "SKILL.master.md"
    destination = SKILL_OUTPUT_ROOT / skill_name / "SKILL.md"
    write_text(destination, rewrite_text(source.read_text(encoding="utf-8"), local_review_checkpoints=local_review_checkpoints))


def copy_procedure(skill_name: str, relative_path: str, *, local_review_checkpoints: bool) -> None:
    source = PROCEDURE_SOURCE_ROOT / relative_path
    destination = SKILL_OUTPUT_ROOT / skill_name / "references" / "procedure" / relative_path
    write_text(destination, rewrite_text(source.read_text(encoding="utf-8"), local_review_checkpoints=local_review_checkpoints))


def copy_phase_directory(skill_name: str, phase_dir: str, *, local_review_checkpoints: bool) -> None:
    source_dir = PROCEDURE_SOURCE_ROOT / "workflow_phase_library" / phase_dir
    for source in sorted(source_dir.glob("*.md")):
        relative_path = Path("workflow_phase_library") / phase_dir / source.name
        copy_procedure(skill_name, str(relative_path), local_review_checkpoints=local_review_checkpoints)


def apply_per_skill_fixes(skill_name: str) -> None:
    if skill_name == "spec-change-workflow":
        path = SKILL_OUTPUT_ROOT / skill_name / "references" / "procedure" / "spec_change_workflow.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "- 新機能追加は `references/procedure/new_feature_workflow.md`、振る舞い不変の構造改善は `references/procedure/refactoring_workflow.md` を使用する",
            "- 新機能追加は `new-feature-workflow` skill、振る舞い不変の構造改善は `refactoring-workflow` skill を使用する",
        )
        write_text(path, text)

    if skill_name == "bugfix-workflow":
        path = SKILL_OUTPUT_ROOT / skill_name / "references" / "procedure" / "bugfix_workflow.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "- bug ではない既知課題は `references/procedure/issue_resolution_workflow.md` を使用する",
            "- bug ではない既知課題は `issue-resolution-workflow` skill を使用する",
        )
        write_text(path, text)


def rebuild() -> None:
    if SKILL_OUTPUT_ROOT.exists():
        shutil.rmtree(SKILL_OUTPUT_ROOT)
    SKILL_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    sync_runtime_helper()

    for skill_name, definition in WORKFLOW_SKILLS.items():
        copy_skill_master(
            skill_name,
            local_review_checkpoints=definition["local_review_checkpoints"],
        )
        for relative_path in definition["procedures"]:
            copy_procedure(
                skill_name,
                relative_path,
                local_review_checkpoints=definition["local_review_checkpoints"],
            )
        for phase_dir in definition["phase_dirs"]:
            copy_phase_directory(
                skill_name,
                phase_dir,
                local_review_checkpoints=definition["local_review_checkpoints"],
            )
        apply_per_skill_fixes(skill_name)


if __name__ == "__main__":
    rebuild()