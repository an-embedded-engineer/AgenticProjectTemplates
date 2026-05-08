---
name: spec-change-workflow
description: プロジェクトの仕様変更で、要求整理、ブランチ作成、レビュー反映、実装、テスト、文書同期、完了処理までを一貫実施する手順。
---

# spec-change-workflow

## いつ使う

- 既存機能の振る舞い・仕様・UI 契約を変更する時
- 新機能追加なら `new-feature-workflow`、外部仕様を変えない構造改善なら `refactoring-workflow` を使う

## 実行ルール（索引）

- 手順本体: `references/procedure/spec_change_workflow.md`
- workflow 選択: workflow 判定ルール
- レビュー観点詳細: `ai-review-response-workflow` skill に同梱された `references/procedure/review_checkpoints.md`
- 共通ルール: `各プロジェクトのコーディング規約`
- 実行コマンド: `各プロジェクトの開発・検証コマンド定義`

## 禁止事項

- Phase 0（要求整理）と Phase 1（ブランチ作成）を飛ばして Phase 2 以降に進んではならない
- ユーザ承認なしに次の Phase に進んではならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. Phase 0 で目的、範囲、受け入れ条件を整理する
2. `docs/todo/todo.md` に対象項目を記録する
3. Phase 1 で仕様変更専用ブランチと `meta.md` を作成する
4. Phase ごとにコミットする
5. 対象プロジェクトで定義された検証コマンドを実行する
6. 設計文書は `plan` / `design` / `impl` に分離して管理する
7. レビュー文書はレビュー担当 Agent が作成する
8. `meta.md` の `plan_status` / `design_status` / `impl_status` を更新する
9. 関連ドキュメントへ反映する
10. Phase 6 のマージ前にソース差分レポート（`report.md`、必要に応じて `diff.zip`）を生成してコミットする
11. 完了時は `todo_archive_<year>.md` へ移し、各 STOP ゲートでユーザへ報告し、承認を待つ
