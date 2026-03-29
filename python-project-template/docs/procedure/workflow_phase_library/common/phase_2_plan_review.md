# Phase 2 共通: 計画作成・計画レビュー

## 実施内容

1. workflow 固有の観点で `plan/` 文書を作成する
2. `meta.md` の `plan_status` を `draft` に更新する
3. 計画書と `meta.md` をコミットする
4. ユーザへレビュー依頼準備完了を報告し、レビュー完了まで待機する

> ⛔ **STOP**: ユーザにレビュー依頼の準備完了を報告する。ユーザがレビュー担当 Agent を起動し、計画レビューが完了するまで待機する。

> 補足: `claude-review-automation` を使う場合、準備完了の報告後はユーザの追加承認を待たずに Codex が Claude review を起動してよい。監視は `15s -> 30s -> 60s` の backoff を使い、5 分程度の `thinking` は通常範囲として扱う。10 分程度進捗が見えない場合のみ、再起動前にユーザへ対応方針を確認する。Phase 区切りでは短い状態要約を残し、利用可能なら `/compact` を実行してよい。

5. レビュー文書作成完了後、`plan_status` を `in_review` に更新して指摘を反映する
6. 未対応指摘がゼロになったら `plan_status` を `done` に更新し、反映結果をコミットする

> ⛔ **STOP**: Phase 2 完了をユーザに報告し、Phase 3 への進行承認を待つ。承認なしに Phase 3 に進んではならない。

## レビュー担当への依頼

- レビュー担当 Agent は `docs/procedure/ai_review_response_workflow.md` に従う
- レビュー観点詳細は `docs/procedure/review_checkpoints.md` を参照する

## 完了条件

- 計画書が最新レビュー結果を反映している
- `plan_status=done`
- レビュー前後の更新がコミットされている

## 承認ゲート

- 計画レビュー完了後、ユーザ承認なしに Phase 3 へ進まない
