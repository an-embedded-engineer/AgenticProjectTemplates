# リファクタリングワークフロー

## 適用条件

- 外部仕様を変えずに内部構造を整理するタスク

## 起票・成果物

- 起票先: `docs/todo/todo.md`
- 完了後 archive: `docs/todo/todo_archive_<year>.md`
- 設計/レビュー文書: `docs/design_analysis/refactoring/<yyyymmdd>_<topic>/`

## Phase 一覧

| Phase | 目的 | 共通手順 | 固有観点 |
|------|------|----------|----------|
| 0 | 対象整理 | - | `docs/procedure/workflow_phase_library/refactoring/phase_0_item_definition.md` |
| 1 | ブランチ・meta 初期化 | `docs/procedure/workflow_phase_library/common/phase_1_branch_and_meta.md` | - |
| 2 | 計画・計画レビュー | `docs/procedure/workflow_phase_library/common/phase_2_plan_review.md` | `docs/procedure/workflow_phase_library/refactoring/phase_2_plan_focus.md` |
| 3 | 設計・設計レビュー | `docs/procedure/workflow_phase_library/common/phase_3_design_review.md` | `docs/procedure/workflow_phase_library/refactoring/phase_3_design_focus.md` |
| 4 | 実装・実装レビュー | `docs/procedure/workflow_phase_library/common/phase_4_impl_review.md` | `docs/procedure/workflow_phase_library/refactoring/phase_4_impl_focus.md` |
| 5 | 動作確認・文書反映 | `docs/procedure/workflow_phase_library/common/phase_5_verification_and_docs.md` | `docs/procedure/workflow_phase_library/refactoring/phase_5_sync_focus.md` |
| 6 | 完了処理 | `docs/procedure/workflow_phase_library/common/phase_6_completion.md` | - |

## 主なレビュー観点

- 仕様変更が混入していないか
- 責務分割と依存方向が改善しているか
- 抽象化・共通化、互換レイヤー抑制、不要フォールバック排除が矛盾なく成立しているか
- 振る舞い不変を示す証跡があるか

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
