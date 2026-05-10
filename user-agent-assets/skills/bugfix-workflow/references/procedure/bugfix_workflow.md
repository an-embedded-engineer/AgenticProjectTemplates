# 不具合修正ワークフロー

## 適用条件

- 既存機能の不具合を修正するタスク
- bug ではない既知課題は `issue-resolution-workflow` skill を使用する

## 起票・成果物

- 起票先: `docs/issues/<component>/issues.md` または `docs/issues/cross/issues.md`
- 完了後 archive: `issues_archive_<year>.md`
- 設計/レビュー文書: `docs/design_analysis/fix_issues/<yyyymmdd>_<topic>/`
- workflow 選択基準: workflow 判定ルール

## Phase 一覧

| Phase | 目的 | 共通手順 | 固有観点 |
|------|------|----------|----------|
| 0 | 事象固定 | - | `references/procedure/workflow_phase_library/bugfix/phase_0_incident_capture.md` |
| 1 | ブランチ・meta 初期化 | `references/procedure/workflow_phase_library/common/phase_1_branch_and_meta.md` | - |
| 2 | 方針・設計レビュー | `references/procedure/workflow_phase_library/common/phase_2_design_review.md` | `references/procedure/workflow_phase_library/bugfix/phase_2_design_focus.md` |
| 3 | 実装・恒久ドキュメント反映レビュー | `references/procedure/workflow_phase_library/common/phase_3_impl_and_docs_review.md` | `references/procedure/workflow_phase_library/bugfix/phase_3_impl_and_docs_focus.md` |
| 4 | 動作確認・完了処理 | `references/procedure/workflow_phase_library/common/phase_4_verification_and_completion.md` | `references/procedure/workflow_phase_library/bugfix/phase_4_completion_focus.md` |

## 主なレビュー観点

- 再現手順と根本原因が追跡可能か
- 応急回避ではなく恒久修正になっているか
- 条件分岐の継ぎ足しではなく、共通化・単一路線化・不要フォールバック排除に寄せられているか
- issue 正本と archive へ移すための証跡が揃っているか

## ユーザ承認が必要なタイミング

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
