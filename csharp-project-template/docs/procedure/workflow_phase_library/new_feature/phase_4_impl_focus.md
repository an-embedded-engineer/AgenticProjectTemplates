# new-feature Phase 4: 実装の観点

## 実装記録

- `docs/design_analysis/new_feature/<yyyymmdd>_<topic>/impl/<topic>_feature_impl.md`

## 必須観点

- ユーザ価値に直結するシナリオを優先して実装する
- 追加した状態・設定・UI を一覧化する
- 類似ロジックを重複実装せず、既存責務へ統合・共通化する
- `reflection` / `dynamic` / `object` / `Dictionary<string, object?>` を使う場合は局所利用に限定し、理由を記録する
- 明示要求がない旧経路や互換分岐は残さず、内部仕様不一致は例外で顕在化する
- テスト結果と既知制約を残す

## レビュー観点

- 機能が計画したユースケースを満たしているか
- 既存機能との統合に破綻がないか
- 重複実装・互換レイヤー・不要フォールバックで説明不能な複雑化を持ち込んでいないか
