@echo off
setlocal enabledelayedexpansion
rem project-skills\ 配下の project-local skills を Agent ごとの discovery path へ同期する

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "SOURCE_ROOT=%PROJECT_ROOT%\project-skills"
set "SYNC_GITHUB=0"
set "SYNC_CLAUDE=0"
set "SYNC_CODEX=0"
set "DRY_RUN=0"
set "SAW_TARGET=0"

if "%~1"=="" goto no_args
:parse_args
if "%~1"=="" goto after_parse
if /I "%~1"=="--github" (
    set "SYNC_GITHUB=1"
    set "SAW_TARGET=1"
    shift
    goto parse_args
)
if /I "%~1"=="--copilot" (
    set "SYNC_GITHUB=1"
    set "SAW_TARGET=1"
    shift
    goto parse_args
)
if /I "%~1"=="--claude" (
    set "SYNC_CLAUDE=1"
    set "SAW_TARGET=1"
    shift
    goto parse_args
)
if /I "%~1"=="--codex" (
    set "SYNC_CODEX=1"
    set "SAW_TARGET=1"
    shift
    goto parse_args
)
if /I "%~1"=="--all" (
    set "SYNC_GITHUB=1"
    set "SYNC_CLAUDE=1"
    set "SYNC_CODEX=1"
    set "SAW_TARGET=1"
    shift
    goto parse_args
)
if /I "%~1"=="--dry-run" (
    set "DRY_RUN=1"
    shift
    goto parse_args
)
if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
echo [ERROR] Unknown option: %~1>&2
goto usage_error

:no_args
set "SYNC_GITHUB=1"
set "SYNC_CLAUDE=1"
set "SYNC_CODEX=1"
goto after_parse

:after_parse
if "%SAW_TARGET%"=="0" (
    set "SYNC_GITHUB=1"
    set "SYNC_CLAUDE=1"
    set "SYNC_CODEX=1"
)

echo === Project Skill Sync Start ===
echo Project root: %PROJECT_ROOT%
echo Source:       %SOURCE_ROOT%

if "%SYNC_GITHUB%"=="1" call :sync_target "%PROJECT_ROOT%\.github\skills" ".github\skills"
if errorlevel 1 exit /b 1
if "%SYNC_CLAUDE%"=="1" call :sync_target "%PROJECT_ROOT%\.claude\skills" ".claude\skills"
if errorlevel 1 exit /b 1
if "%SYNC_CODEX%"=="1" call :sync_target "%PROJECT_ROOT%\.codex\skills" ".codex\skills"
if errorlevel 1 exit /b 1

echo === Project Skill Sync Complete ===
exit /b 0

:usage
echo Usage:
echo   scripts\sync_project_skills.bat [--github] [--claude] [--codex] [--dry-run]
echo   scripts\sync_project_skills.bat --all
echo.
echo Options:
echo   --github   Sync .github\skills
echo   --copilot  Alias for --github
echo   --claude   Sync .claude\skills
echo   --codex    Sync .codex\skills
echo   --all      Sync every supported target ^(default when no target is given^)
echo   --dry-run  Show planned operations without writing files
echo   -h, --help Show this help
exit /b 0

:usage_error
echo Usage:
echo   scripts\sync_project_skills.bat [--github] [--claude] [--codex] [--dry-run]
echo   scripts\sync_project_skills.bat --all
exit /b 1

:sync_target
set "TARGET_ROOT=%~1"
set "LABEL=%~2"
echo --- %LABEL% ---
if not exist "%SOURCE_ROOT%" (
    echo [ERROR] project skills source not found: %SOURCE_ROOT%>&2
    exit /b 1
)
if "%DRY_RUN%"=="1" (
    echo [dry-run] rmdir /s /q "%TARGET_ROOT%"
    echo [dry-run] mkdir "%TARGET_ROOT%"
    for /d %%S in ("%SOURCE_ROOT%\*") do echo [dry-run] xcopy "%%~fS" "%TARGET_ROOT%\%%~nxS\"
    exit /b 0
)
if exist "%TARGET_ROOT%" rmdir /s /q "%TARGET_ROOT%"
mkdir "%TARGET_ROOT%"
for /d %%S in ("%SOURCE_ROOT%\*") do (
    xcopy /e /i /q /y "%%~fS" "%TARGET_ROOT%\%%~nxS" >nul
    if errorlevel 1 exit /b 1
)
echo   %LABEL%: project skills synced
exit /b 0
