#!/usr/bin/env pwsh
# project-skills/ 配下の project-local skills を Agent ごとの discovery path へ同期する

param(
    [switch]$Github,
    [switch]$Copilot,
    [switch]$Claude,
    [switch]$Codex,
    [switch]$All,
    [switch]$DryRun,
    [switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Output "Usage:"
    Write-Output "  .\scripts\sync_project_skills.ps1 [-Github] [-Claude] [-Codex] [-DryRun]"
    Write-Output "  .\scripts\sync_project_skills.ps1 -All"
    Write-Output ""
    Write-Output "Options:"
    Write-Output "  -Github   Sync .github/skills"
    Write-Output "  -Copilot  Alias for -Github"
    Write-Output "  -Claude   Sync .claude/skills"
    Write-Output "  -Codex    Sync .codex/skills"
    Write-Output "  -All      Sync every supported target (default when no target is given)"
    Write-Output "  -DryRun   Show planned operations without writing files"
    Write-Output "  -Help     Show this help"
}

if ($Help) {
    Show-Usage
    exit 0
}

if ($Copilot) {
    $Github = $true
}

if ($All -or (-not $Github -and -not $Claude -and -not $Codex)) {
    $Github = $true
    $Claude = $true
    $Codex = $true
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$sourceRoot = Join-Path $projectRoot "project-skills"

function Copy-ProjectSkills {
    param(
        [string]$TargetRoot,
        [string]$Label
    )

    Write-Output "--- $Label ---"
    if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
        throw "project skills source not found: $sourceRoot"
    }

    if ($DryRun) {
        Write-Output "[dry-run] Remove-Item -Recurse -Force $TargetRoot"
        Write-Output "[dry-run] New-Item -ItemType Directory $TargetRoot"
        Get-ChildItem -LiteralPath $sourceRoot -Directory | ForEach-Object {
            Write-Output "[dry-run] Copy-Item $($_.FullName) -> $(Join-Path $TargetRoot $_.Name)"
        }
        return
    }

    if (Test-Path -LiteralPath $TargetRoot) {
        Remove-Item -LiteralPath $TargetRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null

    Get-ChildItem -LiteralPath $sourceRoot -Directory | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $TargetRoot $_.Name) -Recurse -Force
    }
    Write-Output "  ${Label}: project skills synced"
}

Write-Output "=== Project Skill Sync Start ==="
Write-Output "Project root: $projectRoot"
Write-Output "Source:       $sourceRoot"

if ($Github) {
    Copy-ProjectSkills -TargetRoot (Join-Path $projectRoot ".github/skills") -Label ".github/skills"
}

if ($Claude) {
    Copy-ProjectSkills -TargetRoot (Join-Path $projectRoot ".claude/skills") -Label ".claude/skills"
}

if ($Codex) {
    Copy-ProjectSkills -TargetRoot (Join-Path $projectRoot ".codex/skills") -Label ".codex/skills"
}

Write-Output "=== Project Skill Sync Complete ==="
