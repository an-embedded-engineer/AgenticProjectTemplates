---
name: new-feature-workflow
description: プロジェクトの新機能追加で、要求整理、設計、レビュー、実装、検証、文書反映、完了処理までを一貫実施する手順。
---

# new-feature-workflow

## いつ使う

- 新しい機能やユーザ価値を追加する時

## 実行ルール（索引）

- 手順本体: `references/procedure/new_feature_workflow.md`
- workflow 選択: workflow 判定ルール
- レビュー観点詳細: `ai-review-response-workflow` skill に同梱された `references/procedure/review_checkpoints.md`
- 共通ルール: `各プロジェクトのコーディング規約`
- 実行コマンド: `各プロジェクトの開発・検証コマンド定義`

## 禁止事項

- Phase 0（要求整理）と Phase 1（ブランチ作成）を飛ばして Phase 2 以降に進んではならない
- ユーザ承認なしに次の Phase に進んではならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. Phase 0 で対象ユーザ、ユースケース、受け入れ条件を定義する
2. `docs/todo/todo.md` に対象項目を記録する
3. Phase 1 で新機能専用ブランチと `meta.md` を作成する
4. Phase 2 の設計で最小提供範囲、非対象、統合点、拡張性を整理する
5. Phase 3 で実装差分と恒久ドキュメント反映を同時に行う
6. 対象プロジェクトで定義された検証コマンドを実行する
7. 設計文書は `design` / `impl` を中心に管理し、独立した `plan` 文書を標準成果物にしない
8. レビュー文書はレビュー担当 Agent が作成する
9. 恒久ドキュメントへ利用方法・制約を反映する
10. Phase 4-b でソース差分レポート（`report.md`、必要に応じて `diff.zip`）を生成してコミットする
11. 完了時は `todo_archive_<year>.md` へ移し、各 STOP ゲートで承認を待つ
