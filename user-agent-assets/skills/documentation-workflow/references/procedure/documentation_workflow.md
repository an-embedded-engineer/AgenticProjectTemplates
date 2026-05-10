# ドキュメント更新ワークフロー

## 適用条件

- README、docs、設計分析、履歴、手順書、索引、archive などのドキュメントだけを作成・更新・整理するタスク
- ソースコード、生成ツール、runtime、設定、テンプレートの実行時挙動を変更しないタスク

## 起票・成果物

- 起票先: `docs/todo/todo.md`
- 完了後 archive: `docs/todo/todo_archive_<year>.md`
- 設計/レビュー文書: `docs/design_analysis/documentation/<yyyymmdd>_<topic>/`
- 必須成果物: `meta.md`, `design/<topic>_design.md`, `impl/<topic>_impl.md`, `change_report.md`
- 任意成果物: `review/<topic>_design_review.md`, `review/<topic>_impl_review.md`, `review/<topic>_completion_review.md`

## Phase 一覧

| Phase | 目的 | 主な出力 |
|---|---|---|
| 0 | 対象整理 | 対象文書、目的、非対象、docs-only 判定 |
| 1 | ブランチ・meta 初期化 | documentation 専用ブランチ、`meta.md` |
| 2 | 方針・構成レビュー | `design/<topic>_design.md`、必要時の design review |
| 3 | 文書更新・整合レビュー | `impl/<topic>_impl.md`、必要時の impl review |
| 4 | 文書確認・完了処理 | `change_report.md`、todo archive、history 更新 |

## Phase 0: 対象整理

1. 依頼内容を、目的、対象文書、期待する読者、完了条件に分けて整理する
2. 変更対象がドキュメントだけであることを確認する
3. 次のいずれかに該当する場合は、この workflow から外して適切な workflow を選ぶ
   - ソースコード、スクリプト、設定、生成テンプレート、runtime を変更する
   - 仕様や挙動の変更を伴う
   - 不具合修正、課題解決、リファクタリング、調査レポート作成が主目的である
4. 必要なら `docs/todo/todo.md` に `workflow: documentation` として追跡項目を追加する

### Phase 0 完了条件

- docs-only であることが明確である
- 対象文書と非対象が明確である
- 追跡が必要な場合は todo に記録済みである

## Phase 1: ブランチ・meta 初期化

1. `master` を最新化して、documentation 専用ブランチを作成する
2. `docs/design_analysis/documentation/<yyyymmdd>_<topic>/` を作成する
3. `meta.md` を作成し、最低限次を記録する
   - `title`
   - `created`
   - `category: documentation`
   - `components`
   - `status`
   - `design_status`
   - `impl_status`
   - `completion_status`
   - `related_commits`
4. Phase 1 の成果を 1 コミットで残す

### Phase 1 完了条件

- 専用ブランチで作業している
- 課題ディレクトリと `meta.md` が作成済みである
- Phase 1 成果がコミットされている

## Phase 2: 方針・構成レビュー

1. `design/<topic>_design.md` に次を記録する
   - 背景と目的
   - 対象文書と非対象
   - 読者と利用場面
   - 更新方針
   - 削除、統合、移動、archive の判断
   - リンク、索引、重複、用語、履歴の確認観点
2. 影響範囲が小さく、単純な誤字修正やリンク補正だけの場合は、レビューを省略してよい理由を design に残す
3. 構成変更、文書統合、archive、運用ルール変更を含む場合は `review/<topic>_design_review.md` の作成をレビュー担当 Agent に依頼する
4. レビュー指摘がある場合は design を更新し、レビュー担当 Agent に指摘対応確認を依頼する
5. `design_status` を `done` に更新し、Phase 2 成果をコミットする

### Phase 2 完了条件

- 文書更新方針が design にまとまっている
- 必要な design review が完了している
- `design_status=done` である

## Phase 3: 文書更新・整合レビュー

1. design の方針に沿ってドキュメントだけを更新する
2. `impl/<topic>_impl.md` に次を記録する
   - 実際に更新した文書
   - 移動、削除、統合した文書
   - リンク、索引、参照元、archive、履歴の整合結果
   - 実行した文書検証コマンド
   - ソース変更を含まないことの確認
3. 次の確認を行う
   - `rg` で旧パス、旧見出し、旧 workflow 名、重複記述が残っていないか確認する
   - README、索引、architecture、rules、todo、issues、history など、関連する入口文書のリンクを確認する
   - markdown lint、link check、template validation など、対象プロジェクトが定義する文書向け検証だけを実行する
4. 変更が構成整理、運用ルール変更、archive、複数 docs の横断更新を含む場合は `review/<topic>_impl_review.md` の作成をレビュー担当 Agent に依頼する
5. レビュー指摘がある場合は docs と impl を更新し、レビュー担当 Agent に指摘対応確認を依頼する
6. `impl_status` を `done` に更新し、Phase 3 成果をコミットする

### Phase 3 完了条件

- design で定義した文書更新が完了している
- リンク、索引、重複、archive、履歴の整合を確認済みである
- 必要な impl review が完了している
- `impl_status=done` である

## Phase 4: 文書確認・完了処理

1. `completion_status` を `in_progress` に更新する
2. ユーザ動作確認は要求しない。必要な場合でも、文書の最終確認依頼に限定する
3. アプリ起動、E2E、単体テスト、手動操作確認は必須にしない
4. `change_report.md` を作成し、次を記録する
   - 変更概要
   - 更新した文書一覧
   - 削除、移動、統合した文書
   - 実行した確認コマンド
   - docs-only であり `diff.zip` を作成しない理由
5. `diff.zip` は作成しない。ソース変更が後から混入した場合は、この workflow を中止して適切な core workflow へ切り替える
6. `meta.md` の `related_commits` を主要 commit 中心で更新する
7. 追跡元の todo を完了状態へ更新し、必要なら `docs/todo/todo_archive_<year>.md` へ移動する
8. `docs/history/README.md` の運用に従い、テンプレート利用者や運用者に影響する変更を history に記録する
9. 残課題があれば follow-up を作成する
10. archive / history / merge 前確認が重い場合だけ、`review/<topic>_completion_review.md` の作成をレビュー担当 Agent に依頼する
11. `completion_status` を `done` に更新し、完了処理成果をコミットする
12. ユーザの最終承認後に merge する

### Phase 4 完了条件

- `change_report.md` が作成され、docs-only の確認結果が記録されている
- `diff.zip` が作成されていない
- `meta.md` の `design_status` / `impl_status` / `completion_status` / `related_commits` が確定している
- 追跡元の todo と archive が整理されている
- 必要な history が更新されている
- マージ前の最終承認を受けている

## コミット運用

- Phase 0 / 1 は各 Phase 完了時に 1 コミットを基本とする
- Phase 2 / 3 は「レビュー依頼前」と「レビュー反映完了後」の 2 コミットを基本とする
- 軽微な docs-only 変更でレビューを省略する場合は、省略理由を design または impl に残す
- Phase 4 は change report、archive、history、最終承認の境界が分かる commit を残す
- `related_commits` は completion で主要 commit をまとめて記録する

## 注意

- docs-only workflow は、検証を不要にする workflow ではない。実行時動作確認の代わりに、リンク、索引、構成、重複、archive、history の整合を確認する
- 文書更新中にソース変更が必要だと分かった場合は、ユーザへ報告し、適切な workflow へ切り替える
- レビュー文書はレビュー担当 Agent が作成する
