# よくある落とし穴

## 1. テンプレートと root infra の混同

- root `docs/` / `instructions/` は AgenticProjectTemplates 自体の運用向け
- `python-project-template/docs/` と `csharp-project-template/docs/` はコピー先プロジェクトへ渡るテンプレート
- root の都合だけでテンプレート内文書を変えない

## 2. C# テンプレートへ Python 実行前提を持ち込む

- C# テンプレート利用者に Python を要求する保守ツールは避ける
- 同等機能は `tools/<ToolName>/` の .NET console tool として実装する

## 3. 参照プロジェクトの誤コミット

- `reference/` は横展開元調査用であり、通常は未追跡のまま扱う
- commit 前に `git status --short` で `reference/` が staged されていないことを確認する

## 4. 生成物の混入

- `.pytest_cache/`, `__pycache__/`, `bin/`, `obj/`, `output/` は commit しない
- 検証後に必要なら生成物を削除する
