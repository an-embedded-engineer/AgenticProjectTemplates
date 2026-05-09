# AgenticProjectTemplates Agent Instructions

## 1. 目的

この文書は、AgenticProjectTemplates を保守する Agent 向けの共通索引である。
本リポジトリはテンプレートを生成する単一アプリではなく、複数言語向け project bootstrap 資産、user-level skills、shared runtime、関連ドキュメントを保守するメタプロジェクトである。

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

- 内部思考は英語、チャット応答は日本語
- コメント / Docstring / XML Doc は日本語、ログ / UI / エラー文字列は英語
- Python / C# 向け bootstrap template の同等概念は、意図的な差異を除き同期する
- Python / C# のいずれかへ bootstrap asset や tool を追加した場合、もう一方でも同等の asset / tool を優先して検討する
- workflow / review / orchestration skill は user-level install 済み assets を前提にする
- 関連 ADR が存在する場合は、計画前・実装前・レビュー時に `docs/adr/README.md` の索引規則で対象 ADR を判定して先に参照する
- 不要な後方互換レイヤーやフォールバックを追加しない

## 4. 検証ルール

- project 固有の実行・テスト・静的解析コマンドは `docs/rules/development_workflow.md` を正とする
- root docs / user-agent-assets / scripts を変更した場合は、影響した Python 検証と .NET 検証を実行する
- 変更後は repo toolchain の検証エラーを 0 件に維持する

## 5. 生成物運用

- `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` は直接編集せず、`instructions/` 側の同期元を編集する
- `scripts/sync_agent_instructions.*` は project-level instruction 出力 3 種の再生成だけを扱う
- user home 配下や workspace fallback skill の配布は `user-agent-assets/install/` の責務であり、template sync script では扱わない

## 6. user-level assets 利用前提

- workflow / review / orchestration skill の正本は `user-agent-assets/` 配下で管理される
- user-level 配布は `user-agent-assets/install/install_user_agent_assets.sh` または `install_user_agent_assets.ps1` を使う
- workflow 実行時の詳細手順は `user-agent-assets/skills/*/references/procedure/` を正とし、project-level `docs/procedure/` や repo-local skill source を前提にしない
