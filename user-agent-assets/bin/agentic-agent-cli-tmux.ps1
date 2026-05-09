$RuntimeRoot = if ($env:AGENTIC_PROJECT_TEMPLATES_RUNTIME) {
    $env:AGENTIC_PROJECT_TEMPLATES_RUNTIME
} else {
    Join-Path $HOME '.agentic-project-templates/runtime/agent-cli-tmux'
}

$NativeCandidates = @(
    (Join-Path $RuntimeRoot 'csharp/win-x64/AgentCliTmux.exe'),
    (Join-Path $RuntimeRoot 'csharp/osx-arm64/AgentCliTmux')
)

foreach ($nativeCandidate in $NativeCandidates) {
    if (Test-Path $nativeCandidate) {
        & $nativeCandidate @args
        exit $LASTEXITCODE
    }
}

$PythonEntry = Join-Path $RuntimeRoot 'python/agent_cli_tmux.py'
if (-not (Test-Path $PythonEntry)) {
    Write-Error "runtime helper not found: $($NativeCandidates -join ', ') or $PythonEntry"
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