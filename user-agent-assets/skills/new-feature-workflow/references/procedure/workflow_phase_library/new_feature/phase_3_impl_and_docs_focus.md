# new-feature Phase 3: 実装・恒久ドキュメント反映の観点

## 実装記録

- `docs/design_analysis/new_feature/<yyyymmdd>_<topic>/impl/<topic>_feature_impl.md`

## 恒久ドキュメント反映先

- `docs/components/<component>/README.md`
- `docs/components/<component>/basic_design.md`
- `docs/components/<component>/detail_design.md`
- `docs/components/<component>/interface_spec.md`

## 必須観点

- ユーザ価値に直結するシナリオを優先して実装する
- 追加した状態・設定・UI を一覧化する
- 新機能の使い方、制約、既存機能との関係を恒久ドキュメントへ反映する
- 類似ロジックを重複実装せず、既存責務へ統合・共通化する
- 明示要求がない不要な経路や互換分岐は残さず、内部仕様不一致は例外で顕在化する
- テスト結果と既知制約を残す

## レビュー観点

- 機能が設計したユースケースを満たしているか
- 既存機能との統合に破綻がないか
- 重複実装・互換レイヤー・不要フォールバックで説明不能な複雑化を持ち込んでいないか
- 新機能の導線と制約が文書で再現できるか
