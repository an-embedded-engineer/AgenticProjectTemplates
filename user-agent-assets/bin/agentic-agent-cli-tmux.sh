#!/usr/bin/env bash
set -euo pipefail

RUNTIME_ROOT="${AGENTIC_PROJECT_TEMPLATES_RUNTIME:-${HOME}/.agentic-project-templates/runtime/agent-cli-tmux}"
PYTHON_BIN="${AGENTIC_PROJECT_TEMPLATES_PYTHON:-python3}"
NATIVE_BIN="${RUNTIME_ROOT}/csharp/osx-arm64/AgentCliTmux"
PYTHON_ENTRY="${RUNTIME_ROOT}/python/agent_cli_tmux.py"

if [ -x "${NATIVE_BIN}" ]; then
    exec "${NATIVE_BIN}" "$@"
fi

if [ ! -f "${PYTHON_ENTRY}" ]; then
    echo "runtime helper not found: ${NATIVE_BIN} or ${PYTHON_ENTRY}" >&2
    exit 1
fi

exec "${PYTHON_BIN}" "${PYTHON_ENTRY}" "$@"