# ルール索引

このディレクトリは、AI Agent向け共通インストラクションの詳細ルールを管理します。

## 読み順（推奨）

1. `docs/rules/project_overview.md`
2. `docs/architecture/overview.md`
3. `docs/architecture/code_patterns.md`
4. `docs/architecture/common_pitfalls.md`
5. `docs/rules/development_workflow.md`
6. `docs/rules/language_rules.md`
7. `docs/rules/coding_rules.md`

## 運用方針

- `instructions/agent_common_master.md` を project-level instruction の同期元とし、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は再生成物として扱う
- 詳細ルールは本ディレクトリ配下へ集約する
- ルール更新時は、関連する user-level skill 本文と `references/procedure/` も整合確認する
