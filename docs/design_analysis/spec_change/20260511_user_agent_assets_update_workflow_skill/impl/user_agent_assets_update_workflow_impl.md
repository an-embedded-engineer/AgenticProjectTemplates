# user-agent-assets-update-workflow skill 実装

## 変更概要

- `project-skills/user-agent-assets-update-workflow/` を追加した
- 詳細手順を `references/procedure/user_agent_assets_update_workflow.md` に分離した
- `tmp/` 仮インストール検証用 script として `scripts/validate_temp_install.py` を追加した
- `project-skills/` から `.github/skills` / `.claude/skills` / `.codex/skills` へ同期する `scripts/sync_project_skills.*` を追加した
- `README.md` に project-local maintenance skill として `user-agent-assets-update-workflow` を追加した
- `docs/history/change_history_2026.md` に変更履歴を追加した

## 実装方針

`SKILL.md` は発火条件、禁止事項、最低限の必須チェックに絞り、Phase 詳細は reference に置いた。仮インストール検証は毎回同じ確認を手作業で再実装しないよう script 化した。

## 検証観点

- skill frontmatter が valid であること
- `sync_project_skills.sh` が `.github/skills` / `.claude/skills` / `.codex/skills` へ project-local skill を同期できること
- installer dry-run が新 skill を配布対象に含めないこと
- tmp 仮インストールで各 target に source skill set が展開されること
- `user-agent-assets-update-workflow` が project-local にだけ存在すること
- helper runtime が tmp HOME に展開されること
