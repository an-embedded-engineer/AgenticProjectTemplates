# Phase 3 共通: 実装・恒久ドキュメント反映レビュー

## 実施内容

1. workflow 固有の観点で実装、`impl/` 文書、恒久ドキュメントを更新する
2. `impl/` 文書には、設計差分、実装差分、恒久ドキュメント反映内容、検証結果を対応付けて記録する
3. `docs/rules/development_workflow.md` に従い、変更対象テンプレートの build / test / script 検証を実行する
4. 関連テストを実行する
5. 次のいずれかに該当する場合は、`docs/rules/development_workflow.md` に従って統合テストまたはエンドツーエンド検証も実行する
   - 外部 I/O、永続化、シリアライズ / デシリアライズ経路を変更した
   - アプリケーションの主要導線やエントリポイントを変更した
   - `integration_tests/` やそれに相当する検証コードを変更した
6. `meta.md` の `impl_status` を `draft` に更新する
7. 実装・`impl/` 文書・恒久ドキュメント・`meta.md` をコミットする
8. ユーザへレビュー依頼準備完了を報告し、レビュー完了まで待機する

> STOP: ユーザにレビュー依頼の準備完了を報告する。ユーザがレビュー担当 Agent を起動し、実装レビューが完了するまで待機する。

> 補足: `claude-review-automation` を使う場合、準備完了の報告後はユーザの追加承認を待たずに Codex が Claude review を起動してよい。監視は `15s -> 30s -> 60s` の backoff を使い、5 分程度の `thinking` は通常範囲として扱う。10 分程度進捗が見えない場合のみ、再起動前にユーザへ対応方針を確認する。Phase 区切りでは短い状態要約を残し、利用可能なら `/compact` を実行してよい。

9. レビュー文書作成完了後、`impl_status` を `in_review` に更新して指摘を反映する
10. 未対応指摘がゼロになったら `impl_status` を `done` に更新する
11. `meta.md` の `status` を `implemented` に更新し、反映結果をコミットする

> STOP: Phase 3 完了をユーザに報告し、Phase 4-a のユーザ動作確認へ進む承認を待つ。承認なしに Phase 4 に進んではならない。

## 実装時の必須判断

- 類似ロジックがある場合は、重複した分岐や処理を増やす前に抽象化・共通化で既存経路へ統合する
- 新規関数は責務に合ったクラス / 層へ追加し、呼び出し元近傍への場当たり配置で類似関数を増やさない
- モジュール直下のグローバル関数は原則増やさず、インスタンスメソッド / クラスメソッド / スタティックメソッドの選択理由が説明できる形にする
- フレームワーク契約や既存公開 API 等の明示要件で例外を採る場合は、理由と境界をコードまたは `impl/` 文書へ残す
- Python の `getattr` / `setattr` / `Any` / `Dict`、C# の `dynamic` / reflection / `Dictionary<string, object?>` を使う場合は、局所利用に限定し、理由をコードまたは `impl/` 文書へ残す
- 明示要求または外部契約がない限り、不要な分岐や代替経路を残さず、呼び出し元・テスト・文書を採用経路へ揃える
- プロジェクト内で閉じる仕様不一致は不要なフォールバックで吸収せず、例外や明示的エラーで失敗を顕在化させる
- 恒久仕様・設計ドキュメントは code と同じ Phase で更新し、ユーザ動作確認 NG の場合は code / docs をまとめて Phase 3 へ差し戻す
- todo / issue の完了証跡、archive 準備、history 更新、最終 report は Phase 4-b に残す

## 統合テスト

- 必要な統合テストの実行コマンドは `docs/rules/development_workflow.md` を参照する
- プロジェクト固有の統合テストが未整備なら、実行できなかった理由を `impl/` 文書へ残す

## レビュー担当への依頼

- レビュー担当 Agent は `ai-review-response-workflow` skill に従う
- レビュー観点詳細は `ai-review-response-workflow` skill に同梱された `references/procedure/review_checkpoints.md` を参照する

## 完了条件

- 実装、実装記録、恒久ドキュメントが最新レビュー結果を反映している
- `impl_status=done`
- `status=implemented`
- レビュー前後の更新がコミットされている

## 承認ゲート

- 実装レビュー完了後、ユーザ承認なしに Phase 4 へ進まない
