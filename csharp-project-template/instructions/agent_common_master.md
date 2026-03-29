# {{PROJECT_NAME}} Agent Common Instructions (Draft Master)

## 1. 目的

このファイルは `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の共通 master として使う。
各 Agent 向けファイルは本ファイルへのシンボリックリンク化を前提とする。

## 2. 必須参照（索引）

- プロジェクト概要: `docs/rules/project_overview.md`
- アーキテクチャ概要: `docs/architecture/overview.md`
- コードパターン: `docs/architecture/code_patterns.md`
- よくある落とし穴: `docs/architecture/common_pitfalls.md`
- 開発・実行ルール: `docs/rules/development_workflow.md`
- 言語ルール: `docs/rules/language_rules.md`
- コーディングルール: `docs/rules/coding_rules.md`
- skills カタログ: `docs/rules/skill_catalog.md`
- 手順書索引: `docs/procedure/README.md`

## 3. 最重要ルール（抜粋）

- 内部思考は英語、チャット応答は日本語
- コメント/XML Doc は日本語、ログ/UI/エラー文字列は英語
- 類似ロジックは重複実装より抽象化・共通化を優先して検討する
- `reflection` / `dynamic` / `object` / `Dictionary<string, object?>` の乱用を避け、抽象化・共通化・汎用化に必要な局所利用だけを許容する
- 明示的に指示されない限り、後方互換レイヤーや旧経路は残さない
- 例外を握りつぶさない
- 不必要なフォールバックを実装せず、プロジェクト内で閉じる仕様不一致は例外として顕在化させる
- `dotnet build --warnaserrors` の警告・エラーを 0 にする

## 4. skills 適用

- 仕様変更: `spec-change-workflow`
- 新機能追加: `new-feature-workflow`
- 課題解決: `issue-resolution-workflow`
- リファクタリング: `refactoring-workflow`
- 調査・分析: `research-analysis-workflow`
- レビュー反映: `ai-review-response-workflow`
- 不具合修正: `bugfix-workflow`

詳細は `docs/procedure/` の各手順書を参照する。
