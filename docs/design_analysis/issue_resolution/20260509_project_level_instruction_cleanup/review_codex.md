# project-level instruction 整理 レビュー（Codex）

## 対象

- commit: `ac93c7ee9fec794654fe840d0c65414648f4806a`
- summary: `Clean up project-level agent instruction assets`
- review date: 2026-05-09
- reviewer: Codex

## Findings

### [Medium] macOS / Linux 向けの案内どおりに sync script を直接実行できない

- 対象:
  - `scripts/sync_agent_instructions.sh`
  - `README.md:55`
  - `instructions/agent_sync_guide.md:25`
- 内容:
  - `README.md` と `instructions/agent_sync_guide.md` は macOS / Linux の実行方法として `./scripts/sync_agent_instructions.sh` を案内している。
  - しかし、対象コミットで追加された root script の git mode は `100644` であり、実行権限が付いていない。
  - 実測でも `./scripts/sync_agent_instructions.sh --help` は `permission denied` で失敗した。
  - 一方、同一内容の bootstrap template 側 `user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh` は `100755` で、root 側だけ mode が落ちている。
- 影響:
  - README / sync guide の主要導線どおりに project-level instruction sync を実行できない。
  - root `development_workflow.md` は `bash ./scripts/sync_agent_instructions.sh` を案内しているため検証では見落としやすいが、ユーザー向け手順と実ファイル状態が不整合になっている。
- 推奨対応:
  - `scripts/sync_agent_instructions.sh` に実行権限を付け、git mode を `100755` に揃える。
  - 併せて `./scripts/sync_agent_instructions.sh --help` を検証に追加する。

## 確認済み事項

- `instructions/agent_common_master.md`、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` は `cmp` で一致を確認した。
- `bash ./scripts/sync_agent_instructions.sh --help` は成功した。
- `bash ./scripts/sync_agent_instructions.sh` は成功し、git diff は発生しなかった。
- `pwsh -File scripts/sync_agent_instructions.ps1 -Help` は成功した。
- active docs / instructions / user-level skill 導線に対する `docs/procedure`、`instructions/skills`、`rebuild_user_agent_skills.py`、`sync_agent_skills` の検索では、削除済み経路への実運用依存は確認されなかった。
- `docs/design_analysis/` 配下の過去文書には旧 path が残っているが、今回の report の補足どおり履歴文脈として扱える範囲と判断した。

## 総評

責務境界の整理自体は、`user-agent-assets/skills/*/references/procedure/` を正本とする方針に沿っている。root docs / generated instructions / sync source の関係も概ね一貫している。

ただし、追加された root shell script の file mode だけが template 側および README / sync guide の実行例と食い違っているため、修正後に再確認するのがよい。
