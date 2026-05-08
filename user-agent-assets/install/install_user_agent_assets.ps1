param(
    [switch]$DryRun,
    [ValidateSet('missing', 'overwrite')]
    [string]$Mode = 'missing',
    [string]$Targets = 'copilot,claude,codex',
    [string]$SourceRoot = ''
)

$ErrorActionPreference = 'Stop'

function Write-Plan {
    param([string]$Message)
    Write-Host $Message
}

function Ensure-Directory {
    param([string]$Path)
    if ($DryRun) {
        Write-Plan "[dry-run] mkdir -p $Path"
        return
    }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Sync-MissingDirectory {
    param(
        [string]$SourceDir,
        [string]$TargetDir
    )

    Ensure-Directory $TargetDir
    Get-ChildItem -LiteralPath $SourceDir -Force | ForEach-Object {
        Copy-PathSafe $_.FullName (Join-Path $TargetDir $_.Name)
    }
}

function Copy-PathSafe {
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )

    $sourceIsDirectory = Test-Path $SourcePath -PathType Container

    if ($sourceIsDirectory -and (Test-Path $TargetPath) -and $Mode -eq 'missing') {
        Sync-MissingDirectory $SourcePath $TargetPath
        return
    }

    if ((Test-Path $TargetPath) -and $Mode -eq 'missing') {
        Write-Plan "[skip] $TargetPath"
        return
    }

    if ($DryRun) {
        Write-Plan "[dry-run] copy $SourcePath -> $TargetPath"
        return
    }

    if (Test-Path $TargetPath) {
        Remove-Item -Recurse -Force $TargetPath
    }

    $targetParent = Split-Path -Parent $TargetPath
    if (-not [string]::IsNullOrWhiteSpace($targetParent)) {
        Ensure-Directory $targetParent
    }

    if ($sourceIsDirectory) {
        Copy-Item -Recurse -Force $SourcePath $TargetPath
    }
    else {
        Copy-Item -Force $SourcePath $TargetPath
    }
}

function Sync-WorkflowPhaseLibraryCommon {
    param(
        [string]$TargetSkillDir,
        [string]$SharedCommonDir,
        [string]$SourceSkillDir
    )

    $workflowPhaseRoot = Join-Path $TargetSkillDir 'references/procedure/workflow_phase_library'
    $sourceWorkflowPhaseRoot = Join-Path $SourceSkillDir 'references/procedure/workflow_phase_library'

    if ($DryRun) {
        if (-not (Test-Path $sourceWorkflowPhaseRoot)) {
            return
        }
    }
    elseif (-not (Test-Path $workflowPhaseRoot)) {
        return
    }

    Copy-PathSafe $SharedCommonDir (Join-Path $workflowPhaseRoot 'common')
}

function Copy-SkillDirectory {
    param(
        [string]$SkillDir,
        [string]$TargetDir,
        [string]$SharedCommonDir
    )

    Copy-PathSafe $SkillDir $TargetDir
    Sync-WorkflowPhaseLibraryCommon -TargetSkillDir $TargetDir -SharedCommonDir $SharedCommonDir -SourceSkillDir $SkillDir
}

function Get-NormalizedTargets {
    return ($Targets -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

function Validate-Targets {
    param(
        [string[]]$ResolvedTargets,
        [hashtable]$KnownTargetMap
    )

    foreach ($Target in $ResolvedTargets) {
        if (-not $KnownTargetMap.ContainsKey($Target)) {
            throw "Unsupported target: $Target"
        }
    }
}

if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    $SourceRoot = Split-Path -Parent $PSScriptRoot
}

$SourceRoot = (Resolve-Path $SourceRoot).Path
$SkillRoot = Join-Path $SourceRoot 'skills'
if (-not (Test-Path $SkillRoot)) {
    throw "skills directory not found: $SkillRoot"
}

$SharedWorkflowPhaseCommonDir = Join-Path $SourceRoot 'shared/references/procedure/workflow_phase_library/common'
if (-not (Test-Path $SharedWorkflowPhaseCommonDir)) {
    throw "shared workflow phase common directory not found: $SharedWorkflowPhaseCommonDir"
}

$TargetMap = @{
    copilot = @(
        (Join-Path $HOME '.copilot/skills'),
        (Join-Path $HOME '.agents/skills')
    )
    claude = @((Join-Path $HOME '.claude/skills'))
    codex = @((Join-Path $HOME '.codex/skills'))
}

$ResolvedTargets = Get-NormalizedTargets
Validate-Targets -ResolvedTargets $ResolvedTargets -KnownTargetMap $TargetMap

$HelperRoot = Join-Path $HOME '.agentic-project-templates'
Ensure-Directory $HelperRoot
Ensure-Directory (Join-Path $HelperRoot 'bin')
Ensure-Directory (Join-Path $HelperRoot 'instructions')
Ensure-Directory (Join-Path $HelperRoot 'runtime')
Copy-PathSafe (Join-Path $SourceRoot 'bin/agentic-agent-cli-tmux.sh') (Join-Path $HelperRoot 'bin/agentic-agent-cli-tmux.sh')
Copy-PathSafe (Join-Path $SourceRoot 'bin/agentic-agent-cli-tmux.ps1') (Join-Path $HelperRoot 'bin/agentic-agent-cli-tmux.ps1')
Copy-PathSafe (Join-Path $SourceRoot 'instructions') (Join-Path $HelperRoot 'instructions')
Copy-PathSafe (Join-Path $SourceRoot 'runtime/agent-cli-tmux') (Join-Path $HelperRoot 'runtime/agent-cli-tmux')
foreach ($Target in $ResolvedTargets) {
    foreach ($Root in $TargetMap[$Target]) {
        Ensure-Directory $Root
        Get-ChildItem -Path $SkillRoot -Directory | ForEach-Object {
            Copy-SkillDirectory $_.FullName (Join-Path $Root $_.Name) $SharedWorkflowPhaseCommonDir
        }
    }
}

Write-Host 'install complete'