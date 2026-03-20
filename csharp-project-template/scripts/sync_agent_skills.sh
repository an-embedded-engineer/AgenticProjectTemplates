#!/usr/bin/env bash
# skills 同期スクリプト
# instructions/skills/ 配下の legacy skill と structured skill を .claude/ .github/ ~/.codex/ へ配布する
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MASTER_DIR="${PROJECT_ROOT}/instructions/skills"
BACKUP_TAG="$(date +%Y%m%d_%H%M%S)_skill_sync"
RESOURCE_DIRS=(agents references scripts assets)

CLAUDE_SKILLS="${PROJECT_ROOT}/.claude/skills"
GITHUB_SKILLS="${PROJECT_ROOT}/.github/skills"
CODEX_SKILLS="${HOME}/.codex/skills"

echo "=== Skill Sync Start ==="
echo "Master:  ${MASTER_DIR}"
echo "Backup:  ${BACKUP_TAG}"

sync_link_resources() {
    local skill_dir="$1"
    local skill_name="$2"
    local target_dir="$3"

    for resource_dir in "${RESOURCE_DIRS[@]}"; do
        local source_dir="${skill_dir}/${resource_dir}"
        local target_path="${target_dir}/${resource_dir}"
        rm -rf "${target_path}"
        if [ -e "${source_dir}" ]; then
            ln -sfn "../../../instructions/skills/${skill_name}/${resource_dir}" "${target_path}"
        fi
    done
}

copy_skill_dir() {
    local skill_dir="$1"
    local source_file="$2"
    local target_dir="$3"
    local mode="$4"

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

# skill ディレクトリ内の skill を動的に検出
for skill_dir in "${MASTER_DIR}"/*/; do
    [ -d "${skill_dir}" ] || continue
    skill_name="$(basename "${skill_dir}")"
    legacy_file="${skill_dir}/SKILL.master.md"
    structured_file="${skill_dir}/SKILL.md"

    if [ -f "${legacy_file}" ]; then
        mode="legacy"
        source_file="${legacy_file}"
        source_rel="../../../instructions/skills/${skill_name}/SKILL.master.md"
    elif [ -f "${structured_file}" ]; then
        mode="structured"
        source_file="${structured_file}"
        source_rel="../../../instructions/skills/${skill_name}/SKILL.md"
    else
        echo "SKIP: ${skill_name} (no SKILL.master.md or SKILL.md)"
        continue
    fi

    echo "--- ${skill_name} (${mode}) ---"

    # .claude/skills — symlink
    target_dir="${CLAUDE_SKILLS}/${skill_name}"
    mkdir -p "${target_dir}"
    target_file="${target_dir}/SKILL.md"
    if [ -f "${target_file}" ] && [ ! -L "${target_file}" ]; then
        cp "${target_file}" "${target_file}.bak"
    fi
    ln -sfn "${source_rel}" "${target_file}"
    sync_link_resources "${skill_dir}" "${skill_name}" "${target_dir}"
    echo "  .claude: symlink OK"

    # .github/skills — symlink
    target_dir="${GITHUB_SKILLS}/${skill_name}"
    mkdir -p "${target_dir}"
    target_file="${target_dir}/SKILL.md"
    if [ -f "${target_file}" ] && [ ! -L "${target_file}" ]; then
        cp "${target_file}" "${target_file}.bak"
    fi
    ln -sfn "${source_rel}" "${target_file}"
    sync_link_resources "${skill_dir}" "${skill_name}" "${target_dir}"
    echo "  .github: symlink OK"

    # ~/.codex/skills — copy (symlink 非対応)
    target_dir="${CODEX_SKILLS}/${skill_name}"
    if [ -d "${target_dir}" ]; then
        backup_dir="${CODEX_SKILLS}/_obsoleted/${BACKUP_TAG}/${skill_name}"
        mkdir -p "${backup_dir}"
        cp -R "${target_dir}/." "${backup_dir}/"
    fi
    rm -rf "${target_dir}"
    copy_skill_dir "${skill_dir}" "${source_file}" "${target_dir}" "${mode}"
    echo "  ~/.codex: copy OK"
done

echo "=== Skill Sync Complete ==="
