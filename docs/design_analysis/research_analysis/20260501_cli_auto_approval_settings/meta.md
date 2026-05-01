---
title: "CLI command auto approval settings survey"
created_date: "2026-05-01"
category: "research_analysis"
components:
  - "scripts/agent_cli_tmux.py"
  - "python-project-template/tools/extract_git_diff.py"
  - "docs/procedure/autonomous_workflow_orchestrator.md"
  - "docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md"
status: "merged"
related_commits:
  - "01ff5e0 : Phase 1 initialize research meta for cli auto approval settings"
  - "6369b9e : Phase 2 add cli auto approval settings research report"
  - "95e86ac : Phase 3 reviewer add cli auto approval settings report review"
source_design_path: "docs/design_analysis/research_analysis/20260501_cli_auto_approval_settings/report.md"
---

## Phase 0 固定事項

- 調査目的: GitHub Copilot Chat/CLI、Codex、Claude Code で、非破壊寄りコマンドの承認を不要化する設定方法と制約を整理する。
- 主観点:
  - コマンド単位の allowlist を設定できるか。
  - 対話モードと非対話モードで挙動差があるか。
  - 共有設定としてテンプレートへ落とし込めるか。
  - `agent_cli_tmux` と `extract_git_diff` のような repo 実装へ適用しやすいか。
- 非対象:
  - 実際の設定反映やテンプレート実装変更。
  - 危険コマンドまで無条件許可する運用設計。
  - 各 CLI の認証や課金体系の比較。
- 期待成果物:
  - 各ツールの設定方法・制約・推奨運用をまとめた `report.md`
  - レビュー結果をまとめた `cli_auto_approval_settings_report_review.md`