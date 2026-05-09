# 開発・実行ルール

## 環境

- Python 3.10+
- 仮想環境: `.venv`
- 実行時 `PYTHONPATH=src` を必須とする

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## アプリケーション実行

<!-- TODO: プロジェクト固有の実行コマンドを記述する -->
```bash
# 例: メインアプリケーション起動
PYTHONPATH=src .venv/bin/python -m main
```

## テスト

```bash
# 全テスト実行
PYTHONPATH=src .venv/bin/pytest

# 詳細出力で全テスト実行
PYTHONPATH=src .venv/bin/pytest -v

# 特定のテストファイルを実行
PYTHONPATH=src .venv/bin/pytest tests/test_example.py -v

# 特定のテストケースを実行
PYTHONPATH=src .venv/bin/pytest tests/test_example.py::test_name -v

# 遅いテストをスキップ
PYTHONPATH=src .venv/bin/pytest -m "not slow"

# 失敗したテストのみ再実行
PYTHONPATH=src .venv/bin/pytest --lf

# 最初の失敗で停止
PYTHONPATH=src .venv/bin/pytest -x
```

## 統合テスト

<!-- TODO: プロジェクト固有の統合テストコマンドを記述する -->
```bash
# 例: 統合テスト実行
PYTHONPATH=src .venv/bin/python -m integration_tests.pipeline
```

## 静的解析（必須）

```bash
# Pyright型チェック（JSON出力）— 完了条件: エラー 0 件
.venv/bin/pyright --outputjson > pylance_error.json

# Pyright型チェック（標準出力）
.venv/bin/pyright

# 特定ファイルのみ型チェック
.venv/bin/pyright src/
```
