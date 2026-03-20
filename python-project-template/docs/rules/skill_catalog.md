# Skills カタログ

## 目的

skills の用途を共通化し、適切なトリガー条件で使い分けるための索引です。

## 共通前提

- 設計/実装/レビュー文書は `docs/design_analysis/README.md` の運用ルールに従う
- 標準構成は `plan/` `design/` `impl/` `review/` と `meta.md`
- `meta.md` は `plan_status` / `design_status` / `impl_status` / `related_commits` を更新する

## 一覧

- `spec-change-workflow`
  - トリガー: 仕様変更の要求を受けた時
  - 用途: 仕様変更（設計→レビュー→実装→検証→反映）
  - 詳細: `docs/procedure/spec_change_workflow.md`
- `new-feature-workflow`
  - トリガー: 新機能追加の要求を受けた時
  - 用途: 新機能追加（要求整理→設計→レビュー→実装→検証→反映）
  - 詳細: `docs/procedure/new_feature_workflow.md`
- `ai-review-response-workflow`
  - トリガー: 設計レビュー/コードレビューの結果を反映する時
  - 用途: AIレビュー結果の分類、反映、追跡
  - 詳細: `docs/procedure/ai_review_response_workflow.md`
- `bugfix-workflow`
  - トリガー: 既存機能の不具合修正を行う時
  - 用途: 不具合調査、再現、修正、回帰確認、ドキュメント反映
  - 詳細: `docs/procedure/bugfix_workflow.md`
- `issue-resolution-workflow`
  - トリガー: bug ではない既知課題を解決する時
  - 用途: 課題定義、設計、効果確認、文書反映
  - 詳細: `docs/procedure/issue_resolution_workflow.md`
- `refactoring-workflow`
  - トリガー: 外部仕様を変えない構造改善を行う時
  - 用途: リファクタリング（対象整理→設計→レビュー→実装→検証→反映）
  - 詳細: `docs/procedure/refactoring_workflow.md`
- `claude-review-automation`
  - トリガー: `spec-change` / `new-feature` / `bugfix` / `issue-resolution` / `refactoring` の Phase 2/3/4/5 で、Codex から Claude Code CLI を tmux 経由で起動してレビュー依頼したい時
  - 用途: Claude のインタラクティブ起動、tmux 監視、review 文書更新依頼、指摘対応確認ループの定型化
  - 詳細: `instructions/skills/claude-review-automation/SKILL.master.md`
- `autonomous-workflow-orchestrator`
  - トリガー: 追跡項目 ID を指定して 5 種類の workflow を全 Phase 自律完了させたい時
  - 用途: Copilot が指揮者となり実装 Agent とレビュー Agent を協調させて対象項目を自律解決する
  - 詳細: `docs/procedure/autonomous_workflow_orchestrator.md`
- `copilot-cli-workflow-orchestrator`
  - トリガー: 追跡項目 ID を指定して 5 種類の workflow を Copilot CLI だけで全 Phase 自律完了させたい時
  - 用途: Copilot が指揮者となり Copilot CLI の実装 Agent とレビュー Agent を協調させて対象項目を自律解決する
  - 詳細: `docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md`
- `python-template-doc-filler`
  - トリガー: `python-project-template` を既存プロジェクトへ適用した直後に、プロジェクト名置換や `docs/` の TODO 解消を進めたい時
  - 用途: 既存の Python コードベース、設定、テスト、README を根拠にテンプレート文書を具体化する
  - 詳細: `instructions/skills/python-template-doc-filler/SKILL.md`

## 補足

- workflow の選択基準は `docs/procedure/workflow_selection.md` を参照する
