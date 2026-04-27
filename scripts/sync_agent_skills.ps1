#!/usr/bin/env pwsh
# Agent 向け skills / instructions 同期スクリプト
# instructions/ 配下のマスターファイルを .github/ .claude/ AGENTS.md ~/.codex/ へ実体コピーする

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
    [switch]$Copilot,
    [switch]$Claude,
    [switch]$Codex,
    [switch]$All,
    [Alias("h")]
    [switch]$Help
)

function Show-Usage {
    Write-Output "Usage:"
    Write-Output "  .\scripts\sync_agent_skills.ps1 [-Copilot] [-Claude] [-Codex]"
    Write-Output "  .\scripts\sync_agent_skills.ps1 -All"
    Write-Output ""
    Write-Output "Options:"
    Write-Output "  -Copilot  Sync .github/copilot-instructions.md and .github/skills"
    Write-Output "  -Claude   Sync CLAUDE.md and .claude/skills"
    Write-Output "  -Codex    Sync AGENTS.md and ~/.codex/skills"
    Write-Output "  -All      Sync every supported target (default when no option is given)"
    Write-Output "  -Help     Show this help"
}

if ($Help) {
    Show-Usage
    exit 0
}

if ($All -or (-not $Copilot -and -not $Claude -and -not $Codex)) {
    $Copilot = $true
    $Claude = $true
    $Codex = $true
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$masterSkillsDir = Join-Path $projectRoot "instructions/skills"
$commonInstructions = Join-Path $projectRoot "instructions/agent_common_master.md"
$resourceDirs = @("agents", "references", "scripts", "assets")

function Copy-InstructionFile {
    param(
        [string]$TargetFile,
        [string]$Label
    )

    $targetParent = Split-Path -Parent $TargetFile
    if (-not (Test-Path -LiteralPath $targetParent)) {
        New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
    }

    if (Test-Path -LiteralPath $TargetFile) {
        Remove-Item -LiteralPath $TargetFile -Force
    }

    Copy-Item -LiteralPath $commonInstructions -Destination $TargetFile -Force
    Write-Output "  ${Label}: instruction copied"
}

function Copy-SkillDirectory {
    param(
        [string]$SkillDir,
        [string]$TargetDir
    )

    $legacyFile = Join-Path $SkillDir "SKILL.master.md"
    $structuredFile = Join-Path $SkillDir "SKILL.md"
    $sourceFile = $null
    $mode = $null

    if (Test-Path -LiteralPath $legacyFile) {
        $mode = "legacy"
        $sourceFile = $legacyFile
    }
    elseif (Test-Path -LiteralPath $structuredFile) {
        $mode = "structured"
        $sourceFile = $structuredFile
    }
    else {
        Write-Output "  SKIP $([IO.Path]::GetFileName($SkillDir)): no SKILL.master.md or SKILL.md"
        return
    }

    if (Test-Path -LiteralPath $TargetDir) {
        Remove-Item -LiteralPath $TargetDir -Recurse -Force
    }

    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    Copy-Item -LiteralPath $sourceFile -Destination (Join-Path $TargetDir "SKILL.md") -Force

    if ($mode -eq "structured") {
        foreach ($resourceDir in $resourceDirs) {
            $sourceDir = Join-Path $SkillDir $resourceDir
            if (Test-Path -LiteralPath $sourceDir) {
                Copy-Item -LiteralPath $sourceDir -Destination (Join-Path $TargetDir $resourceDir) -Recurse -Force
            }
        }
    }
}

function Sync-SkillsTo {
    param(
        [string]$RootDir,
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $RootDir)) {
        New-Item -ItemType Directory -Path $RootDir -Force | Out-Null
    }

    Write-Output "  ${Label}: skills sync start"

    Get-ChildItem -LiteralPath $masterSkillsDir -Directory | ForEach-Object {
        $targetDir = Join-Path $RootDir $_.Name
        Copy-SkillDirectory -SkillDir $_.FullName -TargetDir $targetDir
    }

    Write-Output "  ${Label}: skills copied"
}

function Sync-Copilot {
    Write-Output "--- copilot ---"
    Copy-InstructionFile -TargetFile (Join-Path $projectRoot ".github/copilot-instructions.md") -Label ".github"
    Sync-SkillsTo -RootDir (Join-Path $projectRoot ".github/skills") -Label ".github"
}

function Sync-Claude {
    Write-Output "--- claude ---"
    Copy-InstructionFile -TargetFile (Join-Path $projectRoot "CLAUDE.md") -Label "CLAUDE.md"
    Sync-SkillsTo -RootDir (Join-Path $projectRoot ".claude/skills") -Label ".claude"
}

function Sync-Codex {
    Write-Output "--- codex ---"
    Copy-InstructionFile -TargetFile (Join-Path $projectRoot "AGENTS.md") -Label "AGENTS.md"
    Sync-SkillsTo -RootDir (Join-Path (Join-Path $env:USERPROFILE ".codex") "skills") -Label "~/.codex"
}

Write-Output "=== Agent Sync Start ==="
Write-Output "Project root: $projectRoot"
Write-Output "Skill master:  $masterSkillsDir"
Write-Output "Instruction:   $commonInstructions"

if ($Copilot) {
    Sync-Copilot
}

if ($Claude) {
    Sync-Claude
}

if ($Codex) {
    Sync-Codex
}

Write-Output "=== Agent Sync Complete ==="
