# issue-resolution Phase 4: 実装の観点

## 実装記録

- `docs/design_analysis/issue_resolution/<yyyymmdd>_<topic>/impl/<topic>_issue_resolution_impl.md`

## 必須観点

- 完了条件を満たした根拠を実装記録へ残す
- 改善前後の差分を必要に応じて測定値付きで記録する
- 類似ロジックを重複実装せず、既存責務へ統合・共通化する
- `reflection` / `dynamic` / `object` / `Dictionary<string, object?>` を使う場合は局所利用に限定し、理由を記録する
- 明示要求がない旧経路や互換分岐は残さず、内部仕様不一致は例外で顕在化する
- 未解決事項は明確に follow-up へ分離する

## レビュー観点

- issue を閉じる証跡があるか
- 実装がスコープ内で完結しているか
- 重複実装・互換レイヤー・不要フォールバックで複雑化していないか
- 測定結果や確認結果が恣意的でないか
