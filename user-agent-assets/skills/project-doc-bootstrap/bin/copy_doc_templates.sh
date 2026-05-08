#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATES_ROOT="${SKILL_ROOT}/templates"
PROJECT_ROOT="$(pwd)"
LANGUAGE=""
MODE="missing"
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  bash bin/copy_doc_templates.sh --language <python|csharp> [options]

Options:
  --project-root <path>    Target project root (default: current directory)
  --mode <missing|overwrite>
                           Copy mode (default: missing)
  --dry-run                Show planned operations without writing files
  -h, --help               Show this help
EOF
}

log() {
    printf '%s\n' "$*"
}

copy_file() {
    local source_file="$1"
    local target_file="$2"

    if [ -e "${target_file}" ] && [ "${MODE}" = "missing" ]; then
        log "[skip] ${target_file}"
        return
    fi

    if [ "${DRY_RUN}" -eq 1 ]; then
        log "[dry-run] copy ${source_file} -> ${target_file}"
        return
    fi

    mkdir -p "$(dirname "${target_file}")"
    cp "${source_file}" "${target_file}"
}

copy_tree() {
    local source_root="$1"
    local file_path

    [ -d "${source_root}" ] || return
    while IFS= read -r file_path; do
        local relative_path="${file_path#${source_root}/}"
        copy_file "${file_path}" "${PROJECT_ROOT}/${relative_path}"
    done < <(find "${source_root}" -type f | sort)
}

list_placeholders() {
    local docs_root="${PROJECT_ROOT}/docs"
    if [ ! -d "${docs_root}" ]; then
        return
    fi

    log "=== Placeholder scan ==="
    if command -v rg >/dev/null 2>&1; then
        rg -n '\{\{PROJECT_NAME(_LOWER)?\}\}|<!--\s*TODO:' "${docs_root}" || true
    else
        grep -R -n -E '\{\{PROJECT_NAME(_LOWER)?\}\}|<!--[[:space:]]*TODO:' "${docs_root}" || true
    fi

    if [ -d "${docs_root}/components/_example_component" ]; then
        log "[warn] docs/components/_example_component が残っています"
    fi
}

parse_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --language)
                shift
                LANGUAGE="${1:-}"
                ;;
            --project-root)
                shift
                PROJECT_ROOT="${1:-}"
                ;;
            --mode)
                shift
                MODE="${1:-}"
                ;;
            --dry-run)
                DRY_RUN=1
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

    if [ -z "${LANGUAGE}" ]; then
        echo "--language is required" >&2
        exit 1
    fi
    if [ "${LANGUAGE}" != "python" ] && [ "${LANGUAGE}" != "csharp" ]; then
        echo "--language must be python or csharp" >&2
        exit 1
    fi
    if [ "${MODE}" != "missing" ] && [ "${MODE}" != "overwrite" ]; then
        echo "--mode must be missing or overwrite" >&2
        exit 1
    fi
    if [ ! -d "${PROJECT_ROOT}" ]; then
        echo "project root not found: ${PROJECT_ROOT}" >&2
        exit 1
    fi
}

main() {
    parse_args "$@"
    copy_tree "${TEMPLATES_ROOT}/common"
    copy_tree "${TEMPLATES_ROOT}/${LANGUAGE}"
    list_placeholders
}

main "$@"