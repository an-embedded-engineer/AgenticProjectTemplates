# Phase 4 共通: 動作確認・完了処理

## 内部 step

| Step | 目的 | STOP / 進行条件 |
|---|---|---|
| 4-a 動作確認 | ユーザ動作確認と最終検証を受ける | ユーザ確認 OK まで 4-b / 4-c へ進まない |
| 4-b 完了処理 | `report.md`、必要に応じた `diff.zip`、todo / issue 完了証跡、archive 準備、`docs/history/` 更新を行う | completion checklist、必要時は completion review で確認する |
| 4-c merge 承認 | merge 前の最終承認を受ける | ユーザの明示承認後に merge / `status=merged` 更新へ進む |

## 4-a 動作確認

1. ユーザ向けの動作確認観点を整理して共有する
2. アプリ起動または成果物確認での動作確認を依頼し、結果報告を待つ

> STOP: ユーザの動作確認結果が返るまで、次の工程に進んではならない。自動化から扱う場合は `[NEED_USER_VERIFICATION]` を Phase 4-a の停止シグナルとして使う。

3. NG の場合は原因分析を記録して Phase 3 へ戻る
4. OK の場合だけ 4-b へ進む

## 4-b 完了処理

1. `design_status=done`、`impl_status=done` であることを確認する
2. `completion_status` を `in_progress` に更新する
3. `meta.md` の `related_commits` を主要 commit 中心で更新する
   - Phase 境界、review commit、follow-up commit、最終 report / archive commit など意思決定に必要な commit に絞る
   - `related_commits` 追記だけの meta-only commit を Phase 途中で増やさない
   - やむを得ず複数 Phase が 1 commit にまとまった場合は `Phase 1+2` のように記録する
4. ソース差分レポートを生成してコミットする。root には共通差分抽出ツールがないため、必要に応じて `git diff --stat` / `git diff --name-only` / テンプレート内 `tools/ExtractGitDiff` を使い、実行した方法を `report.md` に記録する
   - ブランチの分岐元コミットを取得する: `git merge-base master HEAD`
   - 差分対象が C# テンプレートの tool だけなら `dotnet build` / C# test runner の結果も併記する
   - 課題ディレクトリ配下に `report.md` を作成し、必要なら `diff.zip` も追加する
5. 追跡元の項目を完了状態へ更新し、archive へ移動または archive 準備状態へ整える
   - `docs/todo/README.md` と `docs/issues/README.md` の運用ルールに従って整理する
6. `docs/history/README.md` のガイドラインに従って変更履歴文書を追加または更新する
   - 設計書ディレクトリ、ブランチ、最終コミットを対応付けて記載する
   - 既存文書に追記可能な場合は新規ファイルを増やさず追記する
7. 残課題があれば follow-up を作成する
8. 重い archive / history / merge 前確認が必要な場合だけ、`review/<topic>_completion_review.md` を作成して completion review を依頼する
9. `completion_status` を `done` に更新し、完了処理成果をコミットする

## 4-c merge 承認

1. ユーザの最終承認後に `master` へ `--no-ff` でマージする

> STOP: ユーザに最終マージの承認を求める。承認なしにマージしてはならない。

2. マージ後に `meta.md` の `status` を `merged` に更新し、確定コミット ID を反映する

## 完了条件

- ユーザ動作確認の結果が記録されている
- `meta.md` の工程ステータス、`completion_status`、`related_commits` が確定している
- ソース差分レポート（`report.md`、必要に応じて `diff.zip`）が課題ディレクトリに生成・コミットされている
- 追跡元の項目が archive 方針に従って整理されている
- `docs/history/README.md` の運用に沿って変更履歴が更新されている
- マージと `status=merged` 更新が完了している

## 注意

- core workflow では `related_commits` を completion 集約にする
- research-analysis workflow や多段レビュー topic は round 単位の証跡が重要なため、従来通り逐次追記を維持する
- ブランチ削除はマージ直後に必須としない
- 後日不要になったタイミングでユーザが手動削除する
