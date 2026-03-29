# refactoring Phase 3: 設計書の観点

## 設計書

- `docs/design_analysis/refactoring/<yyyymmdd>_<topic>/design/<topic>_refactoring_design.md`

## 必須観点

- before / after の責務分割
- 依存方向と切り出し単位
- 既存 API / UI / データ契約を変えない保証点
- 類似ロジックの抽象化・共通化方針
- `reflection` / `dynamic` / `object` / `Dictionary<string, object?>` を使う必要がある場合の局所化方針
- 明示要求または外部契約がある場合に限った段階的置換や互換層の要否、および撤去条件
- プロジェクト内で閉じる仕様不一致をフォールバックで吸収しない方針

## レビュー観点

- 設計差分が振る舞い不変前提に沿っているか
- 責務境界が改善しているか
- 共通ルールと矛盾する互換レイヤーや不要フォールバックを前提にしていないか
- 将来の保守性向上に実際につながるか
