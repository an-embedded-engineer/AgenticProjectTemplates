@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "MASTER_SKILLS_DIR=%PROJECT_ROOT%\instructions\skills"
set "COMMON_INSTRUCTIONS=%PROJECT_ROOT%\instructions\agent_common_master.md"
set "CODEX_SKILLS=%USERPROFILE%\.codex\skills"
set "SYNC_COPILOT=0"
set "SYNC_CLAUDE=0"
set "SYNC_CODEX=0"

if "%~1"=="" (
    set "SYNC_COPILOT=1"
    set "SYNC_CLAUDE=1"
    set "SYNC_CODEX=1"
    goto run
)

:parse_args
if "%~1"=="" goto run
set "ARG=%~1"
if /I "%ARG%"=="--copilot" set "SYNC_COPILOT=1" & shift & goto parse_args
if /I "%ARG%"=="-copilot" set "SYNC_COPILOT=1" & shift & goto parse_args
if /I "%ARG%"=="/copilot" set "SYNC_COPILOT=1" & shift & goto parse_args
if /I "%ARG%"=="--claude" set "SYNC_CLAUDE=1" & shift & goto parse_args
if /I "%ARG%"=="-claude" set "SYNC_CLAUDE=1" & shift & goto parse_args
if /I "%ARG%"=="/claude" set "SYNC_CLAUDE=1" & shift & goto parse_args
if /I "%ARG%"=="--codex" set "SYNC_CODEX=1" & shift & goto parse_args
if /I "%ARG%"=="-codex" set "SYNC_CODEX=1" & shift & goto parse_args
if /I "%ARG%"=="/codex" set "SYNC_CODEX=1" & shift & goto parse_args
if /I "%ARG%"=="--all" set "SYNC_COPILOT=1" & set "SYNC_CLAUDE=1" & set "SYNC_CODEX=1" & shift & goto parse_args
if /I "%ARG%"=="-all" set "SYNC_COPILOT=1" & set "SYNC_CLAUDE=1" & set "SYNC_CODEX=1" & shift & goto parse_args
if /I "%ARG%"=="/all" set "SYNC_COPILOT=1" & set "SYNC_CLAUDE=1" & set "SYNC_CODEX=1" & shift & goto parse_args
if /I "%ARG%"=="-h" goto usage
if /I "%ARG%"=="--help" goto usage
if /I "%ARG%"=="/?" goto usage
echo [ERROR] Unknown option: %ARG%
goto usage_error

:usage
echo Usage:
echo   scripts\sync_agent_skills.bat [--copilot] [--claude] [--codex]
echo   scripts\sync_agent_skills.bat --all
echo.
echo Options:
echo   --copilot  Sync .github\copilot-instructions.md and .github\skills
echo   --claude   Sync CLAUDE.md and .claude\skills
echo   --codex    Sync AGENTS.md and %%USERPROFILE%%\.codex\skills
echo   --all      Sync every supported target ^(default when no option is given^)
echo   -h, --help Show this help
exit /b 0

:usage_error
echo.
echo Run with --help to see available options.
exit /b 1

:run
echo === Agent Sync Start ===
echo Project root: %PROJECT_ROOT%
echo Skill master:  %MASTER_SKILLS_DIR%
echo Instruction:   %COMMON_INSTRUCTIONS%

if "%SYNC_COPILOT%"=="1" (
    call :sync_copilot
    if errorlevel 1 exit /b 1
)
if "%SYNC_CLAUDE%"=="1" (
    call :sync_claude
    if errorlevel 1 exit /b 1
)
if "%SYNC_CODEX%"=="1" (
    call :sync_codex
    if errorlevel 1 exit /b 1
)

echo === Agent Sync Complete ===
exit /b 0

:sync_copilot
echo --- copilot ---
call :copy_instruction "%PROJECT_ROOT%\.github\copilot-instructions.md" ".github"
if errorlevel 1 exit /b 1
call :sync_skills "%PROJECT_ROOT%\.github\skills" ".github"
exit /b %errorlevel%

:sync_claude
echo --- claude ---
call :copy_instruction "%PROJECT_ROOT%\CLAUDE.md" "CLAUDE.md"
if errorlevel 1 exit /b 1
call :sync_skills "%PROJECT_ROOT%\.claude\skills" ".claude"
exit /b %errorlevel%

:sync_codex
echo --- codex ---
call :copy_instruction "%PROJECT_ROOT%\AGENTS.md" "AGENTS.md"
if errorlevel 1 exit /b 1
call :sync_skills "%CODEX_SKILLS%" "~/.codex"
exit /b %errorlevel%

:copy_instruction
set "TARGET_FILE=%~1"
set "LABEL=%~2"
for %%I in ("%TARGET_FILE%") do set "TARGET_DIR=%%~dpI"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
if exist "%TARGET_FILE%" del /f /q "%TARGET_FILE%" >nul 2>nul
copy /y "%COMMON_INSTRUCTIONS%" "%TARGET_FILE%" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy instruction: %TARGET_FILE%
    exit /b 1
)
echo   %LABEL%: instruction copied
exit /b 0

:sync_skills
set "ROOT_DIR=%~1"
set "LABEL=%~2"
if not exist "%ROOT_DIR%" mkdir "%ROOT_DIR%"
echo   %LABEL%: skills sync start
for /d %%D in ("%MASTER_SKILLS_DIR%\*") do (
    call :copy_skill "%%~fD" "%ROOT_DIR%\%%~nxD"
    if errorlevel 1 exit /b 1
)
echo   %LABEL%: skills copied
exit /b 0

:copy_skill
set "SKILL_DIR=%~1"
set "TARGET_DIR=%~2"
set "SOURCE_FILE="
set "MODE="

if exist "%SKILL_DIR%\SKILL.master.md" (
    set "SOURCE_FILE=%SKILL_DIR%\SKILL.master.md"
    set "MODE=legacy"
) else if exist "%SKILL_DIR%\SKILL.md" (
    set "SOURCE_FILE=%SKILL_DIR%\SKILL.md"
    set "MODE=structured"
) else (
    echo   SKIP %~nx1: no SKILL.master.md or SKILL.md
    exit /b 0
)

if exist "%TARGET_DIR%" rmdir /s /q "%TARGET_DIR%"
mkdir "%TARGET_DIR%"
copy /y "%SOURCE_FILE%" "%TARGET_DIR%\SKILL.md" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy skill: %SKILL_DIR%
    exit /b 1
)

if /I "%MODE%"=="structured" (
    call :copy_resource "%SKILL_DIR%" "%TARGET_DIR%" "agents"
    if errorlevel 1 exit /b 1
    call :copy_resource "%SKILL_DIR%" "%TARGET_DIR%" "references"
    if errorlevel 1 exit /b 1
    call :copy_resource "%SKILL_DIR%" "%TARGET_DIR%" "scripts"
    if errorlevel 1 exit /b 1
    call :copy_resource "%SKILL_DIR%" "%TARGET_DIR%" "assets"
    if errorlevel 1 exit /b 1
)
exit /b 0

:copy_resource
set "FROM_DIR=%~1\%~3"
set "TO_DIR=%~2\%~3"
if not exist "%FROM_DIR%" exit /b 0
xcopy "%FROM_DIR%" "%TO_DIR%\" /e /i /y /q >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy resource: %FROM_DIR%
    exit /b 1
)
exit /b 0
