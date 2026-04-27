# Instructions

## 目的

AgenticProjectTemplates 自体を保守する Agent 向け instructions と workflow skills を管理する。

## 構成

- `agent_common_master.md`: Agent 共通索引
- `agent_sync_guide.md`: `.github` / `.claude` / Codex への同期手順
- `skills/`: workflow skill 定義

## 運用

- リポジトリ直下の Agent 向け指示は、本ディレクトリと `docs/` を正本として更新する
- Copilot / Claude から slash command として skills を使う場合は、`scripts/sync_agent_skills.sh --copilot --claude` で `.github/` と `.claude/` を再同期する
- テンプレート内の `instructions/` 変更と混同しない
- テンプレート共通ルールを変更する場合は、root 側 docs と各テンプレート側 docs の両方の整合を確認する
