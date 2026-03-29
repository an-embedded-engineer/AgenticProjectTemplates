# issue-resolution Phase 0: 課題定義

## 起票先

- `docs/issues/<component>/issues.md`
- 横断課題は `docs/issues/cross/issues.md`

## 実施内容

1. 課題の現象、背景、なぜ今解くのかを定義する
2. bug かどうかを判定し、bug なら `bugfix` に切り替える
3. 完了条件を測定可能な形で issue 正本へ記録する
4. 影響コンポーネントと非対象を列挙する
5. Phase 0 の成果をコミットする

## 調査観点

- 課題が性能、保守性、文書欠落、設計負債のどれに属するか
- 完了判定を何で行うか
- 別 issue に分割すべき範囲が混ざっていないか

## 完了条件

- 問題定義と完了条件が issue 正本で追跡可能
- bugfix と混同しない分類になっている
- Phase 0 成果がコミットされている
