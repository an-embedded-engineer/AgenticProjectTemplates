---
name: issue-resolution-workflow
description: {{PROJECT_NAME}}の既知課題解決で、課題定義、設計、レビュー、実装、効果確認、文書反映、完了処理までを行う手順。
---

# issue-resolution-workflow

## いつ使う

- bug ではない既知課題を解決する時
- 例: 性能改善、設計負債解消、文書欠落補完、運用阻害要因の解消

## 実行ルール（索引）

- 手順本体: `docs/procedure/issue_resolution_workflow.md`
- workflow 選択: `docs/procedure/workflow_selection.md`
- レビュー観点詳細: `docs/procedure/review_checkpoints.md`
- 共通ルール: `docs/rules/coding_rules.md`
- 実行コマンド: `docs/rules/development_workflow.md`

## 禁止事項

- Phase 0（課題定義）と Phase 1（ブランチ作成）を飛ばして Phase 2 以降に進んではならない
- bug なのに issue-resolution として進めてはならない
- ユーザ承認なしに次の Phase に進んではならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. Phase 0 で課題の背景、完了条件、非対象を定義する
2. `docs/issues/` 正本へ対象 issue を登録または紐付ける
3. Phase 1 で専用ブランチと `meta.md` を作成する
4. 計画で効果確認方法と follow-up 切り出し条件を明記する
5. 実装記録に完了条件を満たした証跡を残す
6. pyright と関連テストを通す
7. 設計文書は `plan` / `design` / `impl` に分離して管理する
8. レビュー文書はレビュー担当 Agent が作成する
9. issue 正本へ達成根拠を反映する
10. Phase 6 のマージ前にソース差分レポート（`diff/` + `report.md`）を生成してコミットする
11. 完了時は archive 方針に従い、各 STOP ゲートでユーザへ報告し、承認を待つ
