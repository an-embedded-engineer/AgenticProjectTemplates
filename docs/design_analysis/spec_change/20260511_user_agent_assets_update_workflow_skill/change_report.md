# user-agent-assets-update-workflow skill change report

## 変更概要

`user-agent-assets/` 更新専用の project-local `user-agent-assets-update-workflow` を追加し、レビュー、dry-run、tmp 仮インストール、実インストール、merge 承認を標準化した。

この `change_report.md` は Phase 3 時点の検証中間結果である。実インストール結果、最終承認、merge 結果は Phase 6 で追記する。

## 更新ファイル

- `README.md`
- `docs/history/change_history_2026.md`
- `docs/design_analysis/spec_change/20260511_user_agent_assets_update_workflow_skill/meta.md`
- `docs/design_analysis/spec_change/20260511_user_agent_assets_update_workflow_skill/design/user_agent_assets_update_workflow_design.md`
- `docs/design_analysis/spec_change/20260511_user_agent_assets_update_workflow_skill/impl/user_agent_assets_update_workflow_impl.md`
- `project-skills/user-agent-assets-update-workflow/SKILL.md`
- `project-skills/user-agent-assets-update-workflow/references/procedure/user_agent_assets_update_workflow.md`
- `project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py`
- `scripts/sync_project_skills.sh`
- `scripts/sync_project_skills.ps1`
- `scripts/sync_project_skills.bat`
- `.gitignore`

## 実行した確認

- `python3 /Users/shin/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py project-skills/user-agent-assets-update-workflow`
  - `Skill is valid!`
- `python3 -m py_compile project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py`
  - 成功
- `bash -n scripts/sync_project_skills.sh scripts/sync_agent_instructions.sh`
  - 成功
- `./scripts/sync_project_skills.sh --dry-run`
  - `.github/skills`、`.claude/skills`、`.codex/skills` への同期予定を確認
- `./scripts/sync_project_skills.sh --all`
  - 3 target へ同期完了
- `pwsh -NoProfile -File scripts/sync_project_skills.ps1 -DryRun`
  - PowerShell 版の dry-run 成功
- `diff -qr project-skills/user-agent-assets-update-workflow <target>/user-agent-assets-update-workflow`
  - `.github/skills`、`.claude/skills`、`.codex/skills` の 3 target すべて source と一致
- `for skill in user-agent-assets/skills/*; do ... quick_validate.py "$skill" ...; done`
  - `all skills valid`
- `bash user-agent-assets/install/install_user_agent_assets.sh --dry-run --mode overwrite --targets copilot,claude,codex --source-root user-agent-assets | rg "user-agent-assets-update-workflow|install complete|agentic-agent-cli-tmux"`
  - `user-agent-assets-update-workflow` が install 対象に含まれないことを確認
- `python3 project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py --source-root user-agent-assets --temp-root tmp/user-agent-assets-install-check --targets copilot,claude,codex --mode overwrite --clean --forbid-skill user-agent-assets-update-workflow`
  - `Temp install validation passed.`
  - `Source skills: 14`
- `git diff --check`
  - 成功

## レビュー指摘対応

- `M-1`: `meta.md` の `components` から未変更の `user-agent-assets/skills/wbs-planning-workflow` を除外し、実変更ファイルへ揃えた
- `m-1`: `.gitignore` に `*/.codex/skills/` を追加した
- `m-2`: この `change_report.md` が Phase 3 時点の検証中間結果であり、Phase 6 で実インストール結果、最終承認、merge 結果を追記することを明記した
- `m-3`: README に `sync_project_skills.ps1 -All` と `sync_project_skills.bat --all` を追記した
- `m-4`: `validate_temp_install.py` の `--forbid-skill` 判定に意図コメントを追加した

## 指摘対応後の確認

- `python3 /Users/shin/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py project-skills/user-agent-assets-update-workflow`
  - `Skill is valid!`
- `python3 -m py_compile project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py`
  - 成功
- `bash -n scripts/sync_project_skills.sh scripts/sync_agent_instructions.sh`
  - 成功
- `./scripts/sync_project_skills.sh --all`
  - 3 target へ同期完了
- `python3 project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py --source-root user-agent-assets --temp-root tmp/user-agent-assets-install-check --targets copilot,claude,codex --mode overwrite --clean --forbid-skill user-agent-assets-update-workflow`
  - `Temp install validation passed.`
  - `Source skills: 14`
- `for skill in user-agent-assets/skills/*; do ... quick_validate.py "$skill" ...; done`
  - `all user-agent-assets skills valid`
- `git diff --check`
  - 成功
