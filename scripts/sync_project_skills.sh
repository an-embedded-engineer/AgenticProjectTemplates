#!/usr/bin/env bash
# project-skills/ 配下の project-local skills を Agent ごとの discovery path へ同期する
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_ROOT="${PROJECT_ROOT}/project-skills"

SYNC_GITHUB=0
SYNC_CLAUDE=0
SYNC_CODEX=0
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  ./scripts/sync_project_skills.sh [--github] [--claude] [--codex] [--dry-run]
  ./scripts/sync_project_skills.sh --all

Options:
  --github   Sync .github/skills
  --copilot  Alias for --github
  --claude   Sync .claude/skills
  --codex    Sync .codex/skills
  --all      Sync every supported target (default when no target is given)
  --dry-run  Show planned operations without writing files
  -h, --help Show this help
EOF
}

parse_args() {
    local saw_target=0
    if [ "$#" -eq 0 ]; then
        SYNC_GITHUB=1
        SYNC_CLAUDE=1
        SYNC_CODEX=1
        return
    fi

    for arg in "$@"; do
        case "${arg}" in
            --github|--copilot)
                SYNC_GITHUB=1
                saw_target=1
                ;;
            --claude)
                SYNC_CLAUDE=1
                saw_target=1
                ;;
            --codex)
                SYNC_CODEX=1
                saw_target=1
                ;;
            --all)
                SYNC_GITHUB=1
                SYNC_CLAUDE=1
                SYNC_CODEX=1
                saw_target=1
                ;;
            --dry-run)
                DRY_RUN=1
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

    if [ "${saw_target}" -eq 0 ]; then
        SYNC_GITHUB=1
        SYNC_CLAUDE=1
        SYNC_CODEX=1
    fi
}

copy_project_skills() {
    local target_root="$1"
    local label="$2"

    echo "--- ${label} ---"
    if [ ! -d "${SOURCE_ROOT}" ]; then
        echo "[ERROR] project skills source not found: ${SOURCE_ROOT}" >&2
        exit 1
    fi

    if [ "${DRY_RUN}" -eq 1 ]; then
        echo "[dry-run] rm -rf ${target_root}"
        echo "[dry-run] mkdir -p ${target_root}"
        for skill_dir in "${SOURCE_ROOT}"/*; do
            [ -d "${skill_dir}" ] || continue
            echo "[dry-run] copy ${skill_dir} -> ${target_root}/$(basename "${skill_dir}")"
        done
        return
    fi

    rm -rf "${target_root}"
    mkdir -p "${target_root}"
    for skill_dir in "${SOURCE_ROOT}"/*; do
        [ -d "${skill_dir}" ] || continue
        cp -R "${skill_dir}" "${target_root}/$(basename "${skill_dir}")"
    done
    echo "  ${label}: project skills synced"
}

parse_args "$@"

echo "=== Project Skill Sync Start ==="
echo "Project root: ${PROJECT_ROOT}"
echo "Source:       ${SOURCE_ROOT}"

if [ "${SYNC_GITHUB}" -eq 1 ]; then
    copy_project_skills "${PROJECT_ROOT}/.github/skills" ".github/skills"
fi

if [ "${SYNC_CLAUDE}" -eq 1 ]; then
    copy_project_skills "${PROJECT_ROOT}/.claude/skills" ".claude/skills"
fi

if [ "${SYNC_CODEX}" -eq 1 ]; then
    copy_project_skills "${PROJECT_ROOT}/.codex/skills" ".codex/skills"
fi

echo "=== Project Skill Sync Complete ==="
