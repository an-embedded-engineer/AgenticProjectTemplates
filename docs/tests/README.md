# テスト

## 概要

AgenticProjectTemplates では、テンプレートごとに自然なテスト実行方式を使う。root 直下に単一のアプリケーションテストスイートは置かず、変更対象テンプレートの検証を実行する。

## テスト構成

```
python-project-template/tests/
└── test_agent_cli_tmux_python_template.py

csharp-project-template/tests/
└── AgentCliTmux.Tests/
    ├── AgentCliTmux.Tests.csproj
    └── Program.cs
```

## 実行方法

- Python テンプレート: `python3 -m pytest python-project-template/tests/test_agent_cli_tmux_python_template.py`
- C# テンプレート: `dotnet run --project csharp-project-template/tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj`
- 詳細: `docs/rules/development_workflow.md` を参照

## ドキュメント構成

- テスト方針: `docs/tests/strategy.md`
