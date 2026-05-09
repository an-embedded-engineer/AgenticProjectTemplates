# bugfix Phase 0: 事象固定

## 起票先

- `docs/issues/<component>/issues.md`
- 横断課題は `docs/issues/cross/issues.md`

## 実施内容

1. 症状、期待値、実際値を明文化する
2. 影響範囲を定義する
3. 最小再現手順を確立する
4. 追跡先 issue へ事象を登録または紐付けする
5. Phase 0 の成果をコミットする

## 調査観点

- 再現条件が安定しているか
- 表面症状と根本原因候補を分離できているか
- データ破損や silent failure がないか

## 完了条件

- 事象、影響範囲、再現手順が追跡可能
- issue 正本との紐付けが完了
- Phase 0 成果がコミットされている
