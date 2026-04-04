#!/usr/bin/env bash
# Agent 向け skills / instructions 同期スクリプト
# instructions/ 配下のマスターファイルを .github/ .claude/ AGENTS.md ~/.codex/ へ実体コピーする
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MASTER_SKILLS_DIR="${PROJECT_ROOT}/instructions/skills"
COMMON_INSTRUCTIONS="${PROJECT_ROOT}/instructions/agent_common_master.md"
RESOURCE_DIRS=(agents references scripts assets)

SYNC_COPILOT=0
SYNC_CLAUDE=0
SYNC_CODEX=0

usage() {
    cat <<'EOF'
Usage:
  ./scripts/sync_agent_skills.sh [--copilot] [--claude] [--codex]
  ./scripts/sync_agent_skills.sh --all

Options:
  --copilot  Sync .github/copilot-instructions.md and .github/skills
  --claude   Sync CLAUDE.md and .claude/skills
  --codex    Sync AGENTS.md and ~/.codex/skills
  --all      Sync every supported target (default when no option is given)
  -h, --help Show this help
EOF
}

parse_args() {
    if [ "$#" -eq 0 ]; then
        SYNC_COPILOT=1
        SYNC_CLAUDE=1
        SYNC_CODEX=1
        return
    fi

    for arg in "$@"; do
        case "${arg}" in
            --copilot)
                SYNC_COPILOT=1
                ;;
            --claude)
                SYNC_CLAUDE=1
                ;;
            --codex)
                SYNC_CODEX=1
                ;;
            --all)
                SYNC_COPILOT=1
                SYNC_CLAUDE=1
                SYNC_CODEX=1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "[ERROR] Unknown option: ${arg}" >&2
                usage >&2
                exit 1
                ;;
        esac
    done
}

copy_instruction_file() {
    local target_file="$1"
    local label="$2"

    mkdir -p "$(dirname "${target_file}")"
    rm -f "${target_file}"
    cp "${COMMON_INSTRUCTIONS}" "${target_file}"
    echo "  ${label}: instruction copied"
}

copy_skill_dir() {
    local skill_dir="$1"
    local target_dir="$2"

    local skill_name
    local legacy_file
    local structured_file
    local source_file
    local mode

    skill_name="$(basename "${skill_dir}")"
    legacy_file="${skill_dir}/SKILL.master.md"
    structured_file="${skill_dir}/SKILL.md"

    if [ -f "${legacy_file}" ]; then
        mode="legacy"
        source_file="${legacy_file}"
    elif [ -f "${structured_file}" ]; then
        mode="structured"
        source_file="${structured_file}"
    else
        echo "  SKIP ${skill_name}: no SKILL.master.md or SKILL.md"
        return
    fi

    rm -rf "${target_dir}"
    mkdir -p "${target_dir}"
    cp "${source_file}" "${target_dir}/SKILL.md"

    if [ "${mode}" = "structured" ]; then
        for resource_dir in "${RESOURCE_DIRS[@]}"; do
            local source_dir="${skill_dir}/${resource_dir}"
            if [ -e "${source_dir}" ]; then
                cp -R "${source_dir}" "${target_dir}/${resource_dir}"
            fi
        done
    fi
}

sync_skills_to() {
    local root_dir="$1"
    local label="$2"

    mkdir -p "${root_dir}"
    echo "  ${label}: skills sync start"

    local skill_dir
    for skill_dir in "${MASTER_SKILLS_DIR}"/*/; do
        [ -d "${skill_dir}" ] || continue
        copy_skill_dir "${skill_dir}" "${root_dir}/$(basename "${skill_dir}")"
    done

    echo "  ${label}: skills copied"
}

sync_copilot() {
    echo "--- copilot ---"
    copy_instruction_file "${PROJECT_ROOT}/.github/copilot-instructions.md" ".github"
    sync_skills_to "${PROJECT_ROOT}/.github/skills" ".github"
}

sync_claude() {
    echo "--- claude ---"
    copy_instruction_file "${PROJECT_ROOT}/CLAUDE.md" "CLAUDE.md"
    sync_skills_to "${PROJECT_ROOT}/.claude/skills" ".claude"
}

sync_codex() {
    echo "--- codex ---"
    copy_instruction_file "${PROJECT_ROOT}/AGENTS.md" "AGENTS.md"
    sync_skills_to "${HOME}/.codex/skills" "~/.codex"
}

parse_args "$@"

echo "=== Agent Sync Start ==="
echo "Project root: ${PROJECT_ROOT}"
echo "Skill master:  ${MASTER_SKILLS_DIR}"
echo "Instruction:   ${COMMON_INSTRUCTIONS}"

if [ "${SYNC_COPILOT}" -eq 1 ]; then
    sync_copilot
fi

if [ "${SYNC_CLAUDE}" -eq 1 ]; then
    sync_claude
fi

if [ "${SYNC_CODEX}" -eq 1 ]; then
    sync_codex
fi

echo "=== Agent Sync Complete ==="
