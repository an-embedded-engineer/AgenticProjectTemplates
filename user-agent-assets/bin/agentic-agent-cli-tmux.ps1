$RuntimeRoot = if ($env:AGENTIC_PROJECT_TEMPLATES_RUNTIME) {
    $env:AGENTIC_PROJECT_TEMPLATES_RUNTIME
} else {
    Join-Path $HOME '.agentic-project-templates/runtime/agent-cli-tmux'
}

$ExePath = Join-Path $RuntimeRoot 'win-x64/AgentCliTmux.exe'
if (Test-Path $ExePath) {
    & $ExePath @args
    exit $LASTEXITCODE
}

$PythonEntry = Join-Path $RuntimeRoot 'python/agent_cli_tmux.py'
if (-not (Test-Path $PythonEntry)) {
    Write-Error "runtime helper not found: $ExePath or $PythonEntry"
    exit 1
}

$PythonCommand = if ($env:AGENTIC_PROJECT_TEMPLATES_PYTHON) {
    $env:AGENTIC_PROJECT_TEMPLATES_PYTHON
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    'py'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    'python'
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    'python3'
} else {
    $null
}

if (-not $PythonCommand) {
    Write-Error "Python runtime helper requires py, python, or python3 in PATH"
    exit 1
}

if ($PythonCommand -eq 'py') {
    & $PythonCommand -3 $PythonEntry @args
}
else {
    & $PythonCommand $PythonEntry @args
}

exit $LASTEXITCODE