# 手順書索引

## 目的

workflow の選択、Phase 進行、レビュー対応、完了処理を統一する。

## workflow 一覧

1. 仕様変更: `docs/procedure/spec_change_workflow.md`
2. 新機能追加: `docs/procedure/new_feature_workflow.md`
3. 不具合修正: `docs/procedure/bugfix_workflow.md`
4. 課題解決: `docs/procedure/issue_resolution_workflow.md`
5. リファクタリング: `docs/procedure/refactoring_workflow.md`

## 共通参照

1. workflow 選択ガイド: `docs/procedure/workflow_selection.md`
2. AIレビュー対応: `docs/procedure/ai_review_response_workflow.md`
3. レビュー観点詳細: `docs/procedure/review_checkpoints.md`
4. 設計/レビュー文書運用ガイド: `docs/design_analysis/README.md`
5. todo 運用ガイド: `docs/todo/README.md`
6. issue 運用ガイド: `docs/issues/README.md`

## 共通ルール

- 手順変更時は `docs/rules/` と整合確認する
- 課題ディレクトリ構成と `meta.md` の運用は `docs/design_analysis/README.md` を参照する
- `spec-change` / `new-feature` / `refactoring` は `docs/todo/todo.md` を正本とする
- `bugfix` / `issue-resolution` は `docs/issues/` を正本とする
