# Agent Sync Guide

## 概要

Agent 向けの instruction ファイルと skills は、リポジトリ直下へシンボリックリンクとして配置しない。
`instructions/` 配下のマスターファイルを、必要な Agent 向けターゲットへ同期スクリプトで実体コピーする。

## 同期元

- 共通 instruction: `instructions/agent_common_master.md`
- skill 一覧: `instructions/skills/`

## 生成先

- Copilot
  - `.github/copilot-instructions.md`
  - `.github/skills/*`
- Claude
  - `CLAUDE.md`
  - `.claude/skills/*`
- Codex
  - `AGENTS.md`
  - `~/.codex/skills/*`

## 実行方法

macOS / Linux:

```bash
./scripts/sync_agent_skills.sh
./scripts/sync_agent_skills.sh --copilot --claude
./scripts/sync_agent_skills.sh --copilot
./scripts/sync_agent_skills.sh --claude --codex
```

Windows PowerShell:

```powershell
.\scripts\sync_agent_skills.ps1
.\scripts\sync_agent_skills.ps1 -Copilot -Claude
.\scripts\sync_agent_skills.ps1 -Copilot
.\scripts\sync_agent_skills.ps1 -Claude -Codex
```

Windows Command Prompt:

```bat
scripts\sync_agent_skills.bat
scripts\sync_agent_skills.bat --copilot --claude
scripts\sync_agent_skills.bat --copilot
scripts\sync_agent_skills.bat --claude --codex
```

## オプション

- `--copilot`: `.github/copilot-instructions.md` と `.github/skills` を同期する
- `--claude`: `CLAUDE.md` と `.claude/skills` を同期する
- `--codex`: `AGENTS.md` と `~/.codex/skills` を同期する
- オプション未指定時は全ターゲットを同期する
- Claude / Copilot の slash command 有効化だけが目的なら `--copilot --claude` を指定し、`~/.codex` には同期しない

## 運用ルール

- `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は手編集せず、`instructions/agent_common_master.md` を更新して再同期する
- skills は `instructions/skills/` を更新して再同期する
- Agent が導入されていない環境では、必要なターゲットだけ同期する
- 同期先はバックアップを作成せずに上書きする。必要なら実行前に手動で退避する
