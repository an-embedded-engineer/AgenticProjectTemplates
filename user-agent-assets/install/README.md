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
- `missing` では既存 file を上書きせず、未配置 file だけを補完する
- 既存 skill を user-level 正本へ移行する場合、既存 `SKILL.md` は `missing` では更新されないため `overwrite` を使う
- `overwrite` は対象 skill directory を置き換えるため、手動追加ファイルも消える
- helper / runtime directory がなければ作成する
- 各 target には選択した skill 一式をまとめて配布する
- review / orchestrator 系 suite skill は関連 workflow skill との同時 install を前提にする
- `--dry-run` / `-DryRun` では変更を加えない
- Windows では `AgentCliTmux.exe` が未配置でも、`python` / `python3` / `py -3` があれば PowerShell wrapper から Python runtime helper を利用できる

## 移行時の推奨

- 既存の user-level skill を新正本へ揃える時は、まず `--dry-run` で確認してから `--mode overwrite` を使う
- `missing` は未配置 file の補完専用であり、既存 `SKILL.md` や既存 managed file の書換えは行わない