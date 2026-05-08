$RuntimeRoot = if ($env:AGENTIC_PROJECT_TEMPLATES_RUNTIME) {
    $env:AGENTIC_PROJECT_TEMPLATES_RUNTIME
} else {
    Join-Path $HOME '.agentic-project-templates/runtime/agent-cli-tmux'
}

$ExePath = Join-Path $RuntimeRoot 'win-x64/AgentCliTmux.exe'
if (-not (Test-Path $ExePath)) {
    Write-Error "runtime helper not found: $ExePath"
    exit 1
}

& $ExePath @args
exit $LASTEXITCODE