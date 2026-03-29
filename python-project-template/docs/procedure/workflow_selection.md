# ワークフロー選択ガイド

## 目的

- タスクの性質に応じて、適切な workflow と起票先を選択する。
- `docs/issues/` と `docs/todo/` の使い分けを明確化する。

## 選択表

| workflow | 適用条件 | 起票先 | 設計/レビュー文書 | ブランチ例 | 主なレビュー観点 |
|----------|----------|--------|------------------|------------|------------------|
| `spec-change` | 既存機能の振る舞い・仕様・UI 契約を変更する | `docs/todo/todo.md` | `docs/design_analysis/spec_change/<yyyymmdd>_<topic>/` | `feature/spec-<topic>-<yyyymmdd>` | 仕様整合、受け入れ条件、互換性、副作用 |
| `new-feature` | 新しい機能やユーザ価値を追加する | `docs/todo/todo.md` | `docs/design_analysis/new_feature/<yyyymmdd>_<topic>/` | `feature/new-<topic>-<yyyymmdd>` | ユースケース、導線、拡張性、既存機能との統合 |
| `bugfix` | 既存機能の不具合を修正する | `docs/issues/<component>/issues.md` または `docs/issues/cross/issues.md` | `docs/design_analysis/fix_issues/<yyyymmdd>_<topic>/` | `fix/bug-<topic>-<yyyymmdd>` | 再現性、根本原因、回帰防止、例外処理 |
| `issue-resolution` | bug 以外の既知課題を解決する | `docs/issues/<component>/issues.md` または `docs/issues/cross/issues.md` | `docs/design_analysis/issue_resolution/<yyyymmdd>_<topic>/` | `issue/resolve-<topic>-<yyyymmdd>` | 完了条件、スコープ閉鎖、測定可能な改善、残課題 |
| `refactoring` | 振る舞いを変えずに構造を整理する | `docs/todo/todo.md` | `docs/design_analysis/refactoring/<yyyymmdd>_<topic>/` | `refactor/<topic>-<yyyymmdd>` | 振る舞い不変、依存整理、可読性、変更容易性 |
| `research-analysis` | 実装前に現状調査、論点整理、根拠収集、選択肢比較を行う | 依頼メッセージ、既存 issue、既存 todo のいずれかに紐付ける | `docs/design_analysis/research_analysis/<yyyymmdd>_<topic>/` | `research/<topic>-<yyyymmdd>` | 根拠、網羅性、コード/文書整合、前提、次 workflow への引き継ぎ可能性 |

## 判定ルール

1. ユーザから見える仕様や操作結果が変わるなら `spec-change` または `new-feature`
2. 既存仕様からの逸脱修正なら `bugfix`
3. 実装や修正の前に、まず現状調査や論点整理が必要なら `research-analysis`
4. bug ではないが、性能・保守性・文書欠落・設計負債などの既知課題を閉じるなら `issue-resolution`
5. 外部仕様を変えず、内部構造だけを整理するなら `refactoring`

## 運用補足

- `spec-change` / `new-feature` / `refactoring` は今後追加する項目から `docs/todo/todo.md` を使用する。
- 完了した `todo` 項目は `docs/todo/todo_archive_<year>.md` へ移動する。
- `research-analysis` は standalone で使えるが、後続 workflow が確定したら関連 issue / todo へ参照を残す。
- 詳細な Phase 手順は各 workflow 文書を参照し、共通 Phase を使う workflow では `docs/procedure/workflow_phase_library/` も参照する。
