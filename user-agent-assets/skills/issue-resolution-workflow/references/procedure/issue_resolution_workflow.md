# 課題解決ワークフロー

## 適用条件

- bug 以外の既知課題を解決するタスク
- 例: 性能改善、設計負債解消、文書欠落補完、運用上の阻害要因解消

## 起票・成果物

- 起票先: `docs/issues/<component>/issues.md` または `docs/issues/cross/issues.md`
- 完了後 archive: `issues_archive_<year>.md`
- 設計/レビュー文書: `docs/design_analysis/issue_resolution/<yyyymmdd>_<topic>/`

## Phase 一覧

| Phase | 目的 | 共通手順 | 固有観点 |
|------|------|----------|----------|
| 0 | 課題定義 | - | `references/procedure/workflow_phase_library/issue_resolution/phase_0_item_definition.md` |
| 1 | ブランチ・meta 初期化 | `references/procedure/workflow_phase_library/common/phase_1_branch_and_meta.md` | - |
| 2 | 方針・設計レビュー | `references/procedure/workflow_phase_library/common/phase_2_design_review.md` | `references/procedure/workflow_phase_library/issue_resolution/phase_2_design_focus.md` |
| 3 | 実装・恒久ドキュメント反映レビュー | `references/procedure/workflow_phase_library/common/phase_3_impl_and_docs_review.md` | `references/procedure/workflow_phase_library/issue_resolution/phase_3_impl_and_docs_focus.md` |
| 4 | 動作確認・完了処理 | `references/procedure/workflow_phase_library/common/phase_4_verification_and_completion.md` | `references/procedure/workflow_phase_library/issue_resolution/phase_4_completion_focus.md` |

## 主なレビュー観点

- issue を閉じる定義が明確か
- 改善効果の確認方法が妥当か
- 類似ロジックの共通化、型安全性、互換レイヤー抑制、不要フォールバック排除ができているか
- 残課題が適切に切り出されているか

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
