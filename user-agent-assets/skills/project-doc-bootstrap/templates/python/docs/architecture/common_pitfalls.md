# よくある落とし穴

<!-- TODO: プロジェクト固有の落とし穴を番号付きで追加する -->

## 1. モジュールパス

- すべての import は `src/` が `PYTHONPATH` に含まれている前提
- 実行例: `PYTHONPATH=src .venv/bin/python -m main`
- テスト: `PYTHONPATH=src .venv/bin/pytest`

## 2. 型安全性

- `Any` 型の安易な使用は Pyright エラーの原因になる
- `Optional` を使う場合は必ず `None` ガードとセットにする
- `getattr` / `setattr` は型推論を壊すため使わない

## 3. 例外処理

- `except Exception: pass` は絶対に書かない
- 例外を catch したら必ずログに原因情報を残す
- 上位に re-raise するか、明示的にハンドリングする

<!-- TODO: 以下にプロジェクト固有の落とし穴を追加する -->
<!--
## 4. (例: パフォーマンス関連)

## 5. (例: 状態管理関連)

## 6. (例: データ整合性関連)
-->
