# 仕様変更ワークフロー

## 適用条件

- 既存機能の振る舞い・仕様・UI 契約を変更するタスク
- 新機能追加は `new-feature-workflow` skill、振る舞い不変の構造改善は `refactoring-workflow` skill を使用する

## 起票・成果物

- 起票先: `docs/todo/todo.md`
- 完了後 archive: `docs/todo/todo_archive_<year>.md`
- 設計/レビュー文書: `docs/design_analysis/spec_change/<yyyymmdd>_<topic>/`
- workflow 選択基準: workflow 判定ルール

## Phase 一覧

| Phase | 目的 | 共通手順 | 固有観点 |
|------|------|----------|----------|
| 0 | 要求整理 | - | `references/procedure/workflow_phase_library/spec_change/phase_0_item_definition.md` |
| 1 | ブランチ・meta 初期化 | `references/procedure/workflow_phase_library/common/phase_1_branch_and_meta.md` | - |
| 2 | 方針・設計レビュー | `references/procedure/workflow_phase_library/common/phase_2_design_review.md` | `references/procedure/workflow_phase_library/spec_change/phase_2_design_focus.md` |
| 3 | 実装・恒久ドキュメント反映レビュー | `references/procedure/workflow_phase_library/common/phase_3_impl_and_docs_review.md` | `references/procedure/workflow_phase_library/spec_change/phase_3_impl_and_docs_focus.md` |
| 4 | 動作確認・完了処理 | `references/procedure/workflow_phase_library/common/phase_4_verification_and_completion.md` | `references/procedure/workflow_phase_library/spec_change/phase_4_completion_focus.md` |

## 主なレビュー観点

- 受け入れ条件が設計・実装・恒久ドキュメントまで追跡可能か
- 既存仕様との互換性と副作用が整理されているか
- 類似ロジックの共通化、過剰な互換レイヤーの排除、不要なフォールバック抑止が一貫しているか
- `todo` から archive へ移すための完了証跡が揃っているか

## ユーザ承認が必要なタイミング

- Phase 0 完了後
- Phase 2 レビュー完了後
- Phase 3 レビュー完了後
- Phase 4-a ユーザ動作確認結果待ち
- Phase 4-c マージ前

## コミット運用

- 原則: Phase 0 / 1 は各 Phase 完了時に 1 コミット
- Phase 2 / 3 は「レビュー依頼前」と「レビュー反映完了後」の 2 コミットを基本とする
- Phase 4 は動作確認、完了処理、最終承認の境界が分かる commit を残す
- レビュー担当 Agent は `*_review.md` 作成時にレビュー成果を 1 コミットで残す
- `related_commits` は completion で主要 commit をまとめて記録する
- `related_commits` の形式: `- <commit_hash> : Phase <番号> <要約>`
