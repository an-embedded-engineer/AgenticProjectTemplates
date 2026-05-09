#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODE="missing"
DRY_RUN=0
TARGETS="copilot,claude,codex"
SOURCE_ROOT="${ASSETS_ROOT}"

usage() {
    cat <<'EOF'
Usage:
  bash user-agent-assets/install/install_user_agent_assets.sh [options]

Options:
  --dry-run               Show planned operations without writing files
  --mode <missing|overwrite>
                          Copy mode (default: missing)
  --targets <list>        Comma-separated targets: copilot,claude,codex
  --source-root <path>    Override source root for testing
  -h, --help              Show this help
EOF
}

log() {
    printf '%s\n' "$*"
}

is_supported_target() {
    case "$1" in
        copilot|claude|codex)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

run_mkdir() {
    local path="$1"
    if [ "${DRY_RUN}" -eq 1 ]; then
        log "[dry-run] mkdir -p ${path}"
    else
        mkdir -p "${path}"
    fi
}

merge_missing_dir() {
    local source_dir="$1"
    local target_dir="$2"
    local source_path

    run_mkdir "${target_dir}"
    for source_path in "${source_dir}"/* "${source_dir}"/.[!.]* "${source_dir}"/..?*; do
        [ -e "${source_path}" ] || continue
        copy_path "${source_path}" "${target_dir}/$(basename "${source_path}")"
    done
}

copy_path() {
    local source_path="$1"
    local target_path="$2"

    if [ -d "${source_path}" ] && [ -e "${target_path}" ] && [ "${MODE}" = "missing" ]; then
        merge_missing_dir "${source_path}" "${target_path}"
        return
    fi

    if [ -e "${target_path}" ] && [ "${MODE}" = "missing" ]; then
        log "[skip] ${target_path}"
        return
    fi

    if [ "${DRY_RUN}" -eq 1 ]; then
        log "[dry-run] copy ${source_path} -> ${target_path}"
        return
    fi

    mkdir -p "$(dirname "${target_path}")"
    rm -rf "${target_path}"
    if [ -d "${source_path}" ]; then
        cp -R "${source_path}" "${target_path}"
    else
        cp "${source_path}" "${target_path}"
    fi
}

ensure_shell_wrapper_executable() {
    local wrapper_path="$1"
    if [ "${DRY_RUN}" -eq 1 ]; then
        log "[dry-run] chmod 755 ${wrapper_path}"
        return
    fi

    if [ -f "${wrapper_path}" ]; then
        chmod 755 "${wrapper_path}"
    fi
}

hydrate_workflow_phase_library_common() {
    local target_skill_dir="$1"
    local source_root="$2"
    local source_skill_dir="$3"
    local shared_common_dir="${source_root}/shared/references/procedure/workflow_phase_library/common"
    local workflow_phase_root="${target_skill_dir}/references/procedure/workflow_phase_library"
    local source_workflow_phase_root="${source_skill_dir}/references/procedure/workflow_phase_library"

    if [ ! -d "${shared_common_dir}" ]; then
        echo "shared workflow phase common directory not found: ${shared_common_dir}" >&2
        exit 1
    fi

    if [ "${DRY_RUN}" -eq 1 ]; then
        if [ ! -d "${source_workflow_phase_root}" ]; then
            return
        fi
    elif [ ! -d "${workflow_phase_root}" ]; then
        return
    fi

    copy_path "${shared_common_dir}" "${workflow_phase_root}/common"
}

copy_skill_dir() {
    local skill_dir="$1"
    local target_dir="$2"
    local source_root="$3"

    copy_path "${skill_dir}" "${target_dir}"
    hydrate_workflow_phase_library_common "${target_dir}" "${source_root}" "${skill_dir}"
}

normalize_targets() {
    echo "${TARGETS}" | tr ',' '\n' | awk 'NF {print $1}'
}

validate_targets() {
    local target
    while IFS= read -r target; do
        [ -n "${target}" ] || continue
        if ! is_supported_target "${target}"; then
            echo "Unsupported target: ${target}" >&2
            exit 1
        fi
    done < <(normalize_targets)
}

install_copilot() {
    local skill_root="$1"
    local source_root="$2"
    local skill_dir
    for target_dir in "${HOME}/.copilot/skills" "${HOME}/.agents/skills"; do
        run_mkdir "${target_dir}"
        for skill_dir in "${skill_root}"/*; do
            [ -d "${skill_dir}" ] || continue
            copy_skill_dir "${skill_dir}" "${target_dir}/$(basename "${skill_dir}")" "${source_root}"
        done
    done
}

install_single_runtime() {
    local source_root="$1"
    local helper_root="${HOME}/.agentic-project-templates"
    run_mkdir "${helper_root}"
    run_mkdir "${helper_root}/bin"
    run_mkdir "${helper_root}/instructions"
    run_mkdir "${helper_root}/runtime"
    copy_path "${source_root}/bin/agentic-agent-cli-tmux.sh" "${helper_root}/bin/agentic-agent-cli-tmux.sh"
    copy_path "${source_root}/bin/agentic-agent-cli-tmux.ps1" "${helper_root}/bin/agentic-agent-cli-tmux.ps1"
    copy_path "${source_root}/instructions" "${helper_root}/instructions"
    copy_path "${source_root}/runtime/agent-cli-tmux" "${helper_root}/runtime/agent-cli-tmux"
    ensure_shell_wrapper_executable "${helper_root}/bin/agentic-agent-cli-tmux.sh"
}

install_claude() {
    local skill_root="$1"
    local source_root="$2"
    local target_dir="${HOME}/.claude/skills"
    local skill_dir
    run_mkdir "${target_dir}"
    for skill_dir in "${skill_root}"/*; do
        [ -d "${skill_dir}" ] || continue
        copy_skill_dir "${skill_dir}" "${target_dir}/$(basename "${skill_dir}")" "${source_root}"
    done
}

install_codex() {
    local skill_root="$1"
    local source_root="$2"
    local target_dir="${HOME}/.codex/skills"
    local skill_dir
    run_mkdir "${target_dir}"
    for skill_dir in "${skill_root}"/*; do
        [ -d "${skill_dir}" ] || continue
        copy_skill_dir "${skill_dir}" "${target_dir}/$(basename "${skill_dir}")" "${source_root}"
    done
}

parse_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --dry-run)
                DRY_RUN=1
                ;;
            --mode)
                shift
                MODE="${1:-}"
                ;;
            --targets)
                shift
                TARGETS="${1:-}"
                ;;
            --source-root)
                shift
                SOURCE_ROOT="${1:-}"
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                usage >&2
                exit 1
                ;;
        esac
        shift
    done

    if [ "${MODE}" != "missing" ] && [ "${MODE}" != "overwrite" ]; then
        echo "--mode must be missing or overwrite" >&2
        exit 1
    fi
}

main() {
    parse_args "$@"
    validate_targets

    local resolved_root
    resolved_root="$(cd "${SOURCE_ROOT}" && pwd)"
    local skill_root="${resolved_root}/skills"

    if [ ! -d "${skill_root}" ]; then
        echo "skills directory not found: ${skill_root}" >&2
        exit 1
    fi

    install_single_runtime "${resolved_root}"

    local target
    while IFS= read -r target; do
        case "${target}" in
            copilot)
                install_copilot "${skill_root}" "${resolved_root}"
                ;;
            claude)
                install_claude "${skill_root}" "${resolved_root}"
                ;;
            codex)
                install_codex "${skill_root}" "${resolved_root}"
                ;;
            '')
                ;;
            *)
                echo "Unsupported target: ${target}" >&2
                exit 1
                ;;
        esac
    done < <(normalize_targets)

    log "install complete"
}

main "$@"