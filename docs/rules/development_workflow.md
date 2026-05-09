# 開発・実行ルール

## 環境

- Python テンプレート検証: Python 3.10+ / pytest
- C# テンプレート検証: system の `dotnet` で利用可能な .NET 9 SDK / runtime
- Agent CLI tmux 監視: `tmux`, `codex`, `claude`, 必要に応じて `copilot`

## 基本検証

```bash
# Root の Agent CLI tmux 補助スクリプト
python3 -m py_compile scripts/agent_cli_tmux.py

# user-level assets installer
bash user-agent-assets/install/install_user_agent_assets.sh --help

# Python pytest
python3 -m pytest tests/test_agent_cli_tmux.py
python3 -m pytest tests/test_extract_git_diff.py

# C# Agent CLI tmux 補助ツール
dotnet build user-agent-assets/runtime/agent-cli-tmux/csharp/AgentCliTmux/AgentCliTmux.csproj
dotnet run --project tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj

# 実行前確認（必要に応じて）
dotnet --list-sdks
dotnet --list-runtimes

# C# git diff 抽出ツール
dotnet build user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff/ExtractGitDiff.csproj
```

## 変更種別ごとの確認

- root `docs/` / `user-agent-assets/` / `scripts/`: 関連リンク、workflow 参照、installer / bootstrap 契約の整合を確認し、root script は `py_compile` または `--help` で検証する
- `scripts/agent_cli_tmux.py`: root 側を正本とし、`tests/test_agent_cli_tmux.py` で直接検証する
- `user-agent-assets/install/`: shell / PowerShell の `--help` と、必要に応じて `--dry-run` で install 挙動を確認する
- root `.github/` と template `AGENTS.md` / `CLAUDE.md`: checked-in canonical docs として扱い、旧 sync source や repo-local skills を再導入しない
- `user-agent-assets/skills/project-doc-bootstrap/templates/python/tools/extract_git_diff.py`: Python pytest で検証する
- `user-agent-assets/runtime/agent-cli-tmux/csharp/AgentCliTmux` / `tests/AgentCliTmux.Tests`: 対象 `.csproj` の `dotnet build` と test runner を実行する
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff`: 対象 `.csproj` の `dotnet build` を実行する
- Python / C# bootstrap template 両方へ横展開する変更: `user-agent-assets/skills/project-doc-bootstrap/templates/python` と `templates/csharp` の両方で整合を確認する

## 生成物管理

- `bin/`, `obj/`, `__pycache__/`, `.pytest_cache/`, `output/` は commit しない
- `reference/` は横展開元の参照用であり、明示指示がない限り commit しない
