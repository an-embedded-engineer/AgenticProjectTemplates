# User-Level Agent 共通原則

## 1. 目的

このファイルは、user-level に配置した共通 Agent 資産の入口である。
プロジェクト固有の制約は、各リポジトリの `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` を正本とする。

## 2. 必須参照

- workflow 選択: `workflow_selection.md`
- 言語方針: `language_policy.md`
- インストール済み workflow / review skill: `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/`、`~/.codex/skills/`

## 3. 運用ルール

- まず workflow を選び、その skill の `SKILL.md` と同梱 `references/procedure/` に従う
- アーキテクチャ、コーディング規約、検証コマンド、ADR 判定は各プロジェクトのローカル規約を優先する
- tmux ベースの Agent orchestration には `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh` を使う
- user-level skill は self-contained を前提とし、リポジトリ側の `docs/procedure/` や `skill_catalog.md` を前提にしない
