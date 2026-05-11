# documentation-workflow skill 設計

## 背景

既存の `spec-change-workflow`、`new-feature-workflow`、`bugfix-workflow`、`issue-resolution-workflow`、`refactoring-workflow` はソース変更や実行時挙動変更を含む前提で、Phase 4 に動作確認と、ソース変更時の `diff.zip` 作成を持つ。

README、docs、設計分析、履歴、手順書、索引、archive だけを更新する場合、この Phase 4 は過剰になる。そのため、docs-only 変更専用の `documentation-workflow` を追加する。

## 方針

- `documentation-workflow` はソースコード、生成ツール、runtime、設定、テンプレートの実行時挙動を変更しないタスクだけを扱う
- ソース変更が必要になった時点で workflow を中止し、適切な core workflow へ切り替える
- アプリ起動、E2E、単体テスト、手動操作確認は必須にしない
- `diff.zip` は作成しない
- 代わりに、リンク、索引、archive、history、重複記述、文書入口の整合確認を完了条件にする

## Phase Library 非共有の判断

`documentation-workflow` は `workflow_phase_library/common/phase_4_verification_and_completion.md` を直接共有しない。

理由は、共通 Phase 4 がユーザ動作確認とソース変更時の `diff.zip` 作成を前提にしているためである。documentation ではこの前提を持たせず、文書最終確認、`change_report.md`、archive / history、merge 前承認に絞る。

Phase 1 の `meta.md` も documentation 固有の差分を持つ。実行時動作確認を行わないため `verification_status` は持たず、`design_status` / `impl_status` / `completion_status` を使う。

## Phase 4 構造

orchestrator と整合させるため、Phase 4 は次の 3 段に分ける。

| Step | 目的 | シグナル / 文言 |
|---|---|---|
| 4-a | 文書最終確認 | `[NEED_USER_VERIFICATION]`, `文書の最終確認をお願いします`, `docs-only の確認をお願いします` |
| 4-b | 完了処理 | `change_report.md`, todo archive, history |
| 4-c | merge 前承認 | `マージしてよいですか`, `[ALL_PHASES_COMPLETE]` |

Phase 0 / 1 / 2 / 3 の完了時は `[PHASE_COMPLETE: <phase_number>]` を出力してよい。

## Workflow 判定

明示指定を優先する。明示指定がない場合は、`docs/design_analysis/documentation/` 配下、または `docs/todo/todo.md` の追跡項目に `workflow: documentation` がある場合に documentation と判定する。

## WBS 連携

WBS の `recommended_workflow` に `documentation` を追加する。documentation work package では、完了条件と検証観点にリンク、索引、archive、history、重複記述の整合確認を含め、動作確認や `diff.zip` 作成を必須にしない。

## 配置と列挙順

`docs/design_analysis/README.md` と bootstrap template のカテゴリ列挙では、`refactoring` の直後に `documentation` を置く。

順序は `spec_change` / `new_feature` / `fix_issues` / `issue_resolution` / `refactoring` / `documentation` / `wbs` / `research_analysis` とする。
