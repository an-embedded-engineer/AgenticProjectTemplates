# {{PROJECT_NAME}} Agent Project Instructions (Sync Source)

## 1. 目的

このファイルは `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の共通同期元として使う。
各 Agent 向けファイルは `scripts/sync_agent_instructions.*` で本ファイルを実体コピーして生成する。

## 2. 必須参照

- ADR 索引: `docs/adr/README.md`
- プロジェクト概要: `docs/rules/project_overview.md`
- アーキテクチャ概要: `docs/architecture/overview.md`
- コードパターン: `docs/architecture/code_patterns.md`
- よくある落とし穴: `docs/architecture/common_pitfalls.md`
- 開発・実行ルール: `docs/rules/development_workflow.md`
- 言語ルール: `docs/rules/language_rules.md`
- コーディングルール: `docs/rules/coding_rules.md`
- sync ガイド: `instructions/agent_sync_guide.md`

## 3. project 固有ルール

- Python project として `./.venv/bin/pyright --outputjson > pylance_error.json` の診断を 0 に維持する
- project 固有の実行・テスト・静的解析コマンドは `docs/rules/development_workflow.md` を正とする
- template 固有の instructions / docs 更新後は、影響した Python 検証コマンドを実行する

## 4. 生成物運用

- `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` は直接編集せず、`instructions/` 側の同期元を編集する
- `scripts/sync_agent_instructions.*` は project-level instruction 出力 3 種の再生成だけを扱う
- user home 配下や workspace fallback skill の配布は repo root `user-agent-assets/install/` の責務であり、template sync script では扱わない

## 5. user-level assets 利用前提

- workflow / review / orchestration skill の正本は repo root `user-agent-assets/` 配下で管理される
- user-level 配布は repo root `user-agent-assets/install/install_user_agent_assets.sh` または `install_user_agent_assets.ps1` を使う
- workflow 実行時の詳細手順は user-level skill 同梱の `references/procedure/` を優先し、project-level 手順書への実行時依存を増やさない