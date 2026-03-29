# Phase 6 共通: 完了処理

## 実施内容

1. `plan_status` / `design_status` / `impl_status` が全て `done` であることを確認する
2. `meta.md` の `related_commits` を規定フォーマットで更新してコミットする
3. ソース差分レポートを生成してコミットする
   - ブランチの分岐元コミットを取得する: `git merge-base master HEAD`
   - `tools/ExtractGitDiff` を実行する:
     ```
     dotnet run --project tools/ExtractGitDiff -- \
       --commit-from <分岐元コミットID> --commit-to HEAD \
       -d src tests -e .cs .csproj .json \
       -o <課題ディレクトリ>
     ```
   - 課題ディレクトリ配下に生成された `diff/` ディレクトリと `report.md` をコミットする
4. ユーザの最終承認後に `master` へ `--no-ff` でマージする

> ⛔ **STOP**: ユーザに最終マージの承認を求める。承認なしにマージしてはならない。
5. マージ後に `meta.md` の `status` を `merged` に更新し、確定コミット ID を反映する
6. 追跡元の項目を完了状態へ更新し、archive へ移動する
   - `docs/todo/README.md` と `docs/issues/README.md` の運用ルールに従って整理する
7. `docs/history/README.md` のガイドラインに従って変更履歴文書を追加または更新する
   - 設計書ディレクトリ、ブランチ、最終コミットを対応付けて記載する
   - 既存文書に追記可能な場合は新規ファイルを増やさず追記する
8. 残課題があれば follow-up を作成する

## 完了条件

- `meta.md` の工程ステータスと `related_commits` が確定している
- ソース差分レポート（`diff/` + `report.md`）が課題ディレクトリに生成・コミットされている
- マージと `status=merged` 更新が完了している
- 追跡元の項目が archive 方針に従って整理されている
- `docs/history/README.md` の運用に沿って変更履歴が更新されている

## 注意

- ブランチ削除はマージ直後に必須としない
- 後日不要になったタイミングでユーザが手動削除する
