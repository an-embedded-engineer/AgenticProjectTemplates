---
title: "user-agent-assets-update-workflow skill"
category: "spec_change"
created: "2026-05-11"
components:
  - project-skills/user-agent-assets-update-workflow
  - scripts/sync_project_skills.sh
  - scripts/sync_project_skills.ps1
  - scripts/sync_project_skills.bat
  - .gitignore
  - README.md
  - docs/history/change_history_2026.md
status: "implemented"
design_status: "done"
impl_status: "done"
verification_status: "in_progress"
completion_status: "in_progress"
related_commits:
  - "9c40c1d: Add project-local user agent assets workflow"
  - "06c7a53: Review user agent assets update workflow impl"
---

# user-agent-assets-update-workflow skill meta

この topic は、AgenticProjectTemplates の `user-agent-assets/` 更新を branch から review、dry-run、tmp 仮インストール、実インストール、merge 承認まで扱う project-local workflow skill を追加した記録である。
