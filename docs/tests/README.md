# テスト

## 概要

AgenticProjectTemplates では、repo root の scripts、user-level runtime、bootstrap template 同梱 tool を Python pytest と C# test runner で検証する。

## テスト構成

```
tests/
├── test_agent_cli_tmux.py
├── test_extract_git_diff.py
└── AgentCliTmux.Tests/
    ├── AgentCliTmux.Tests.csproj
    └── Program.cs
```

## 実行方法

- Python: `python3 -m pytest tests/test_agent_cli_tmux.py tests/test_extract_git_diff.py`
- C#: `dotnet run --project tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj`
    - 前提: system の `dotnet` で .NET 9 SDK / runtime が利用可能であること
- 詳細: `docs/rules/development_workflow.md` を参照

## ドキュメント構成

- テスト方針: `docs/tests/strategy.md`
