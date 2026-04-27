# AgenticProjectTemplates Agent Common Instructions

## 1. 目的

このファイルは、AgenticProjectTemplates 自体を保守する Agent 向けの共通索引である。
本リポジトリはテンプレートを生成するアプリではなく、複数言語向けプロジェクトテンプレートと Agent 運用文書を管理するメタプロジェクトである。

## 2. 必須参照（索引）

- ADR 索引: `docs/adr/README.md`
- プロジェクト概要: `docs/rules/project_overview.md`
- アーキテクチャ概要: `docs/architecture/overview.md`
- コードパターン: `docs/architecture/code_patterns.md`
- よくある落とし穴: `docs/architecture/common_pitfalls.md`
- 開発・実行ルール: `docs/rules/development_workflow.md`
- 言語ルール: `docs/rules/language_rules.md`
- コーディングルール: `docs/rules/coding_rules.md`
- skills カタログ: `docs/rules/skill_catalog.md`
- 手順書索引: `docs/procedure/README.md`

## 3. 最重要ルール

- 内部思考は英語、チャット応答は日本語
- コメント/Docstring/XML Doc は日本語、ログ/UI/エラー文字列は英語
- `python-project-template/` と `csharp-project-template/` の同等概念は、意図的な差異を除き同期する
- Python テンプレートに Python ツールを追加した場合、C# テンプレートでは同等の .NET tool を優先して検討する
- テンプレート内の生成物 (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.claude/skills/`, `.github/skills/`) は直接編集せず、`instructions/` 側の同期元を編集する
- 関連 ADR が存在する場合は、計画前・実装前・レビュー時に `docs/adr/README.md` の索引規則で対象 ADR を判定して先に参照する
- 不要な後方互換レイヤーやフォールバックを追加しない
- 変更後は、影響したテンプレートごとの検証コマンドを実行する

## 4. skills 適用

- 仕様変更: `spec-change-workflow`
- 新機能追加: `new-feature-workflow`
- 課題解決: `issue-resolution-workflow`
- リファクタリング: `refactoring-workflow`
- 調査・分析: `research-analysis-workflow`
- レビュー反映: `ai-review-response-workflow`
- 不具合修正: `bugfix-workflow`
- Claude レビュー自動化: `claude-review-automation`

詳細は `docs/procedure/` の各手順書を参照する。
