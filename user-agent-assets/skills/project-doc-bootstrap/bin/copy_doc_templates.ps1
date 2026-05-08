param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('python', 'csharp')]
    [string]$Language,
    [string]$ProjectRoot = (Get-Location).Path,
    [ValidateSet('missing', 'overwrite')]
    [string]$Mode = 'missing',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Split-Path -Parent $ScriptDir
$TemplatesRoot = Join-Path $SkillRoot 'templates'

function Write-Plan {
    param([string]$Message)
    Write-Host $Message
}

function Copy-TemplateFile {
    param(
        [string]$SourceFile,
        [string]$TargetFile
    )

    if ((Test-Path $TargetFile) -and $Mode -eq 'missing') {
        Write-Plan "[skip] $TargetFile"
        return
    }

    if ($DryRun) {
        Write-Plan "[dry-run] copy $SourceFile -> $TargetFile"
        return
    }

    $targetParent = Split-Path -Parent $TargetFile
    if (-not (Test-Path $targetParent)) {
        New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
    }

    Copy-Item -Force $SourceFile $TargetFile
}

function Copy-TemplateTree {
    param([string]$SourceRoot)

    if (-not (Test-Path $SourceRoot)) {
        return
    }

    Get-ChildItem -Path $SourceRoot -Recurse -File | Sort-Object FullName | ForEach-Object {
        $relativePath = $_.FullName.Substring($SourceRoot.Length).TrimStart([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        Copy-TemplateFile $_.FullName (Join-Path $ProjectRoot $relativePath)
    }
}

function Show-Placeholders {
    $docsRoot = Join-Path $ProjectRoot 'docs'
    if (-not (Test-Path $docsRoot)) {
        return
    }

    Write-Plan '=== Placeholder scan ==='
    Get-ChildItem -Path $docsRoot -Recurse -File -Include *.md | ForEach-Object {
        $matches = Select-String -Path $_.FullName -Pattern '\{\{PROJECT_NAME(_LOWER)?\}\}|<!--\s*TODO:' -AllMatches
        foreach ($match in $matches) {
            Write-Host ("{0}:{1}:{2}" -f $_.FullName, $match.LineNumber, $match.Line.Trim())
        }
    }

    $exampleComponentDir = Join-Path $docsRoot 'components/_example_component'
    if (Test-Path $exampleComponentDir) {
        Write-Plan '[warn] docs/components/_example_component が残っています'
    }
}

if (-not (Test-Path $ProjectRoot)) {
    throw "project root not found: $ProjectRoot"
}

Copy-TemplateTree (Join-Path $TemplatesRoot 'common')
Copy-TemplateTree (Join-Path $TemplatesRoot $Language)
Show-Placeholders