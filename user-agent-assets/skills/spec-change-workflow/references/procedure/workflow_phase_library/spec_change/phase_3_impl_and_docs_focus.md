# spec-change Phase 3: 実装・恒久ドキュメント反映の観点

## 実装記録

- `docs/design_analysis/spec_change/<yyyymmdd>_<topic>/impl/<topic>_impl.md`

## 恒久ドキュメント反映先

- `docs/components/<component>/README.md`
- `docs/components/<component>/basic_design.md`
- `docs/components/<component>/detail_design.md`
- `docs/components/<component>/interface_spec.md`

## 必須観点

- 設計差分と実装差分を対応付けて記録する
- 互換性に影響する変更は明示する
- 変更後仕様を恒久ドキュメントへ反映する
- 類似ロジックを重複追加せず、既存経路へ統合・共通化する
- 明示要求がない互換分岐や不要な経路は削除し、内部仕様不一致は例外で顕在化する
- テスト結果と未解決事項を残す

## レビュー観点

- 設計通りに仕様差分が実装されているか
- 想定外の振る舞い変更が混入していないか
- 重複実装・互換レイヤー・不要フォールバックの追加で複雑化していないか
- テストが受け入れ条件を十分にカバーしているか
- 実装結果と恒久ドキュメントの説明が一致しているか
