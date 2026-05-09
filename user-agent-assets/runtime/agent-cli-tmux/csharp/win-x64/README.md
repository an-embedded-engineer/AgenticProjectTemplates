Windows native payload placeholder.

`agentic-agent-cli-tmux.ps1` は `runtime/agent-cli-tmux/csharp/win-x64/AgentCliTmux.exe` を優先して呼び出す。
現時点では macOS 向け `csharp/osx-arm64/AgentCliTmux` を先行配置し、Windows は follow-up で publish 済み executable を追加する。