---
name: refactoring-workflow
description: AgenticProjectTemplatesのリファクタリングで、対象整理、設計、レビュー、実装、振る舞い不変確認、文書反映、完了処理までを行う手順。
---

# refactoring-workflow

## いつ使う

- 外部仕様を変えずに内部構造を整理する時

## 実行ルール（索引）

- 手順本体: `docs/procedure/refactoring_workflow.md`
- workflow 選択: `docs/procedure/workflow_selection.md`
- レビュー観点詳細: `docs/procedure/review_checkpoints.md`
- 共通ルール: `docs/rules/coding_rules.md`
- 実行コマンド: `docs/rules/development_workflow.md`

## 禁止事項

- Phase 0（対象整理）と Phase 1（ブランチ作成）を飛ばして Phase 2 以降に進んではならない
- 仕様変更を混ぜ込んではならない
- ユーザ承認なしに次の Phase に進んではならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. Phase 0 で振る舞い不変条件と改善対象を定義する
2. `docs/todo/todo.md` に対象項目を記録する
3. Phase 1 で専用ブランチと `meta.md` を作成する
4. 計画で現状の構造問題と分割戦略を明記する
5. 実装記録に振る舞い不変の確認結果を残す
6. 関連する Python pytest と .NET build/test を通す
7. 設計文書は `plan` / `design` / `impl` に分離して管理する
8. レビュー文書はレビュー担当 Agent が作成する
9. 恒久ドキュメントへ責務分割変更を反映する
10. Phase 6 のマージ前にソース差分レポート（`report.md`、必要に応じて `diff.zip`）を生成してコミットする
11. 完了時は `todo_archive_<year>.md` へ移し、各 STOP ゲートで承認を待つ
