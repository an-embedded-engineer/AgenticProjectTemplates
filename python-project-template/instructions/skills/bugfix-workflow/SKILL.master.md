---
name: bugfix-workflow
description: {{PROJECT_NAME}}の不具合修正で、再現、原因分析、修正、回帰テスト、文書反映、完了処理までを行う手順。
---

# bugfix-workflow

## いつ使う

- 既存機能の不具合修正を行う時
- bug ではない既知課題なら `issue-resolution-workflow` を使う

## 実行ルール（索引）

- 手順本体: `docs/procedure/bugfix_workflow.md`
- workflow 選択: `docs/procedure/workflow_selection.md`
- レビュー観点詳細: `docs/procedure/review_checkpoints.md`
- 共通ルール: `docs/rules/coding_rules.md`
- 実行コマンド: `docs/rules/development_workflow.md`

## 禁止事項

- Phase 0（事象固定）と Phase 1（ブランチ作成）を飛ばして Phase 2 以降に進んではならない
- ユーザ承認なしに次の Phase に進んではならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. Phase 0 で症状・期待値・再現手順を固定する
2. `docs/issues/` 正本へ対象 issue を登録または紐付ける
3. Phase 1 で修正専用ブランチと `meta.md` を作成する
4. 根本原因を特定して恒久修正方針を立てる
5. 回帰テストを追加または実行する
6. pyright を 0 件にする
7. 設計文書は `plan` / `design` / `impl` に分離して管理する
8. レビュー文書はレビュー担当 Agent が作成する
9. `meta.md` の `plan_status` / `design_status` / `impl_status` を更新する
10. Phase 6 のマージ前にソース差分レポート（`diff.zip` + `report.md`）を生成してコミットする
11. issue 正本と関連文書を更新し、完了時は archive 方針に従う
