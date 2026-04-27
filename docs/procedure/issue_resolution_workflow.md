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
| 0 | 課題定義 | - | `docs/procedure/workflow_phase_library/issue_resolution/phase_0_item_definition.md` |
| 1 | ブランチ・meta 初期化 | `docs/procedure/workflow_phase_library/common/phase_1_branch_and_meta.md` | - |
| 2 | 計画・計画レビュー | `docs/procedure/workflow_phase_library/common/phase_2_plan_review.md` | `docs/procedure/workflow_phase_library/issue_resolution/phase_2_plan_focus.md` |
| 3 | 設計・設計レビュー | `docs/procedure/workflow_phase_library/common/phase_3_design_review.md` | `docs/procedure/workflow_phase_library/issue_resolution/phase_3_design_focus.md` |
| 4 | 実装・実装レビュー | `docs/procedure/workflow_phase_library/common/phase_4_impl_review.md` | `docs/procedure/workflow_phase_library/issue_resolution/phase_4_impl_focus.md` |
| 5 | 動作確認・文書反映 | `docs/procedure/workflow_phase_library/common/phase_5_verification_and_docs.md` | `docs/procedure/workflow_phase_library/issue_resolution/phase_5_sync_focus.md` |
| 6 | 完了処理 | `docs/procedure/workflow_phase_library/common/phase_6_completion.md` | - |

## 主なレビュー観点

- issue を閉じる定義が明確か
- 改善効果の確認方法が妥当か
- 類似ロジックの共通化、型安全性、互換レイヤー抑制、不要フォールバック排除ができているか
- 残課題が適切に切り出されているか

## ユーザ承認が必要なタイミング

- Phase 2 レビュー完了後
- Phase 3 レビュー完了後
- Phase 4 レビュー完了後
- Phase 5 ユーザ動作確認結果待ち
- Phase 5 ドキュメントレビュー完了後
- Phase 6 マージ前

## コミット運用

- 原則: Phase 0 / 1 は各 Phase 完了時に 1 コミット
- Phase 2 / 3 / 4 / 5 は「レビュー依頼前」と「レビュー反映完了後」の 2 コミットを基本とする
- レビュー担当 Agent は `*_review.md` 作成時にレビュー成果を 1 コミットで残す
- `related_commits` の形式: `- <commit_hash> : Phase <番号> <要約>`
