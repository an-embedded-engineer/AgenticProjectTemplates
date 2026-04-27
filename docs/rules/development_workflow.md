# 開発・実行ルール

## 環境

- Python テンプレート検証: Python 3.10+ / pytest
- C# テンプレート検証: .NET 9 SDK
- Agent CLI tmux 監視: `tmux`, `codex`, `claude`, 必要に応じて `copilot`

## 基本検証

```bash
# Root の Agent CLI tmux 補助スクリプト
python3 -m py_compile scripts/agent_cli_tmux.py

# Python テンプレートの Agent CLI tmux 補助スクリプト
python3 -m py_compile python-project-template/scripts/agent_cli_tmux.py
python3 -m pytest python-project-template/tests/test_agent_cli_tmux_python_template.py

# C# テンプレートの Agent CLI tmux 補助ツール
dotnet build csharp-project-template/tools/AgentCliTmux/AgentCliTmux.csproj
dotnet run --project csharp-project-template/tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj

# C# git diff 抽出ツール
dotnet build csharp-project-template/tools/ExtractGitDiff/ExtractGitDiff.csproj
```

## 変更種別ごとの確認

- root `docs/` / `instructions/` / `scripts/`: 関連リンク、プレースホルダ、workflow 参照の整合を確認し、root script は `py_compile` を実行する
- `python-project-template/` の scripts/tools/tests: Python 側の該当 pytest / py_compile を実行する
- `csharp-project-template/` の tools/tests: 対象 `.csproj` の `dotnet build` と該当 test runner を実行する
- 両テンプレートへ横展開する変更: Python / C# の両方で同等の検証を行う

## 生成物管理

- `bin/`, `obj/`, `__pycache__/`, `.pytest_cache/`, `output/` は commit しない
- `reference/` は横展開元の参照用であり、明示指示がない限り commit しない
