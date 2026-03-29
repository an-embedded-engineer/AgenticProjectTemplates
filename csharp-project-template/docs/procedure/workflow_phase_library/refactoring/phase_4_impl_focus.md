# refactoring Phase 4: 実装の観点

## 実装記録

- `docs/design_analysis/refactoring/<yyyymmdd>_<topic>/impl/<topic>_refactoring_impl.md`

## 必須観点

- 振る舞い不変を確認したテストと証跡を残す
- 依存整理や重複削減の結果を記録する
- 類似ロジックを重複実装せず、既存責務へ統合・共通化する
- `reflection` / `dynamic` / `object` / `Dictionary<string, object?>` を使う場合は局所利用に限定し、理由を記録する
- 明示要求または外部契約がある場合を除き、互換レイヤーや旧経路を残さない
- 段階的置換を行う場合は、段階差分と撤去条件を明記する

## レビュー観点

- 仕様変更が紛れ込んでいないか
- コード量や責務分散が妥当な方向へ改善しているか
- 互換レイヤーや不要フォールバックで複雑化していないか
- 今後の変更容易性が上がっているか
