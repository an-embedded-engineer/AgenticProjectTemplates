# User-Level Agent Assets Install

このディレクトリは `user-agent-assets/` 配下の正本を user-level skills / helper / instructions へ配布する install script を管理する。

## サポート対象

- Copilot: `~/.copilot/skills/`, `~/.agents/skills/`
- Claude: `~/.claude/skills/`
- Codex: `~/.codex/skills/`
- 共通 helper: `~/.agentic-project-templates/`
- 共通 instructions: `~/.agentic-project-templates/instructions/`

## 使い方

### macOS / Linux

```bash
bash user-agent-assets/install/install_user_agent_assets.sh --dry-run
bash user-agent-assets/install/install_user_agent_assets.sh --targets copilot,claude
```

### Windows PowerShell

```powershell
pwsh -File user-agent-assets/install/install_user_agent_assets.ps1 -DryRun
pwsh -File user-agent-assets/install/install_user_agent_assets.ps1 -Targets copilot,claude
```

## 既定動作

- mode は `missing`
- user-level skills は既存 file を上書きしない
- helper / runtime directory がなければ作成する
- `--dry-run` / `-DryRun` では変更を加えない