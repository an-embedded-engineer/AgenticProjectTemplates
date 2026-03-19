#!/usr/bin/env bash
# skills 同期スクリプト
# instructions/skills/ 配下の SKILL.master.md を .claude/ .github/ ~/.codex/ へ配布する
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MASTER_DIR="${PROJECT_ROOT}/instructions/skills"
BACKUP_TAG="$(date +%Y%m%d_%H%M%S)_skill_sync"

CLAUDE_SKILLS="${PROJECT_ROOT}/.claude/skills"
GITHUB_SKILLS="${PROJECT_ROOT}/.github/skills"
CODEX_SKILLS="${HOME}/.codex/skills"

echo "=== Skill Sync Start ==="
echo "Master:  ${MASTER_DIR}"
echo "Backup:  ${BACKUP_TAG}"

# master ディレクトリ内の skill を動的に検出
for skill_dir in "${MASTER_DIR}"/*/; do
    [ -d "${skill_dir}" ] || continue
    skill_name="$(basename "${skill_dir}")"
    master_file="${skill_dir}/SKILL.master.md"

    if [ ! -f "${master_file}" ]; then
        echo "SKIP: ${skill_name} (no SKILL.master.md)"
        continue
    fi

    echo "--- ${skill_name} ---"

    # .claude/skills — symlink
    target_dir="${CLAUDE_SKILLS}/${skill_name}"
    mkdir -p "${target_dir}"
    target_file="${target_dir}/SKILL.md"
    if [ -f "${target_file}" ] && [ ! -L "${target_file}" ]; then
        cp "${target_file}" "${target_file}.bak"
    fi
    ln -sfn "../../../instructions/skills/${skill_name}/SKILL.master.md" "${target_file}"
    echo "  .claude: symlink OK"

    # .github/skills — symlink
    target_dir="${GITHUB_SKILLS}/${skill_name}"
    mkdir -p "${target_dir}"
    target_file="${target_dir}/SKILL.md"
    if [ -f "${target_file}" ] && [ ! -L "${target_file}" ]; then
        cp "${target_file}" "${target_file}.bak"
    fi
    ln -sfn "../../../instructions/skills/${skill_name}/SKILL.master.md" "${target_file}"
    echo "  .github: symlink OK"

    # ~/.codex/skills — copy (symlink 非対応)
    target_dir="${CODEX_SKILLS}/${skill_name}"
    mkdir -p "${target_dir}"
    target_file="${target_dir}/SKILL.md"
    if [ -f "${target_file}" ]; then
        backup_dir="${CODEX_SKILLS}/_obsoleted/${BACKUP_TAG}/${skill_name}"
        mkdir -p "${backup_dir}"
        cp "${target_file}" "${backup_dir}/SKILL.md"
    fi
    cp "${master_file}" "${target_file}"
    echo "  ~/.codex: copy OK"
done

echo "=== Skill Sync Complete ==="
