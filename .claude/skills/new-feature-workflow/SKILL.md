---
name: new-feature-workflow
description: AgenticProjectTemplatesの新機能追加で、要求整理、設計、レビュー、実装、検証、文書反映、完了処理までを一貫実施する手順。
---

# new-feature-workflow

## いつ使う

- 新しい機能やユーザ価値を追加する時

## 実行ルール（索引）

- 手順本体: `docs/procedure/new_feature_workflow.md`
- workflow 選択: `docs/procedure/workflow_selection.md`
- レビュー観点詳細: `docs/procedure/review_checkpoints.md`
- 共通ルール: `docs/rules/coding_rules.md`
- 実行コマンド: `docs/rules/development_workflow.md`

## 禁止事項

- Phase 0（要求整理）と Phase 1（ブランチ作成）を飛ばして Phase 2 以降に進んではならない
- ユーザ承認なしに次の Phase に進んではならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. Phase 0 で対象ユーザ、ユースケース、受け入れ条件を定義する
2. `docs/todo/todo.md` に対象項目を記録する
3. Phase 1 で新機能専用ブランチと `meta.md` を作成する
4. 計画で最小提供範囲と非対象を明確化する
5. 設計で既存機能との統合点と拡張性を整理する
6. 関連する Python pytest と .NET build/test を通す
7. 設計文書は `plan` / `design` / `impl` に分離して管理する
8. レビュー文書はレビュー担当 Agent が作成する
9. 恒久ドキュメントへ利用方法・制約を反映する
10. Phase 6 のマージ前にソース差分レポート（`report.md`、必要に応じて `diff.zip`）を生成してコミットする
11. 完了時は `todo_archive_<year>.md` へ移し、各 STOP ゲートで承認を待つ
