# refactoring Phase 3: 実装・恒久ドキュメント反映の観点

## 実装記録

- `docs/design_analysis/refactoring/<yyyymmdd>_<topic>/impl/<topic>_refactoring_impl.md`

## 恒久ドキュメント反映先

- `docs/components/<component>/README.md`
- `docs/components/<component>/basic_design.md`
- `docs/components/<component>/detail_design.md`
- `docs/components/<component>/interface_spec.md`

## 必須観点

- 振る舞い不変を確認したテストと証跡を残す
- 依存整理や重複削減の結果を記録する
- 類似ロジックを重複実装せず、既存責務へ統合・共通化する
- 明示要求または外部契約がある場合を除き、互換レイヤーや不要な経路を残さない
- 段階的置換を行う場合は、段階差分と撤去条件を明記する
- 責務分割や依存方向の変更を恒久ドキュメントへ反映する
- 外部仕様不変であることを恒久ドキュメントにも明記する

## レビュー観点

- 仕様変更が紛れ込んでいないか
- コード量や責務分散が妥当な方向へ改善しているか
- 互換レイヤーや不要フォールバックで複雑化していないか
- 文書上でも責務境界の改善が読み取れるか
- 外部仕様不変の説明が欠けていないか
