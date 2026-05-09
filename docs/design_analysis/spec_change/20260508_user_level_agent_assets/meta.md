---
title: "ユーザレベル Agent 資産化（SC-20260508-001）"
created_date: "2026-05-08"
category: spec_change
components:
  - instructions
  - skills
  - docs
  - scripts
  - python-project-template
  - csharp-project-template
status: in_progress
plan_status: done
source_plan_path: docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md
design_status: done
source_design_path: docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md
impl_status: done
branch: feature/spec-user-level-agent-assets-20260508
source_research_path: docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md
source_research_review_path: docs/design_analysis/research_analysis/20260507_user_level_agent_assets/user_level_agent_assets_report_review.md
related_commits:
  - 4bc2fec : Phase 2 pre-review plan
  - eca2abe : Phase 2 plan review Round 1
  - cea5833 : Phase 2 post-review plan fix
  - b92d3a5 : Phase 2 plan review Round 2 approval
  - fb34c22 : Phase 3 pre-review design
  - 8f0767f : Phase 3 design review Round 1
  - c4171ce : Phase 3 post-review design fix
  - 2e68fd4 : Phase 3 design review Round 2 approval
  - cf4045b : Phase 3 post-review design refine (migration policy)
  - 0b98917 : Phase 3 design review Round 3 approval
  - 6d96e46 : Phase 3 post-review design simplify (no fallback)
  - d115d62 : Phase 4 user-level assets foundation
  - c233403 : Finalize review fixes for user-level agent assets
  - 05ce753 : Record latest user-level agent assets review results
  - 986c735 : Address latest user-level agent assets review findings
  - 398bb58 : Record PowerShell validation for user-level agent assets
  - 5cc9ec2 : Record final PowerShell review confirmations
  - 787b3db : Phase 5 capture follow-up items
---

# メタ情報

## 変更目的

Python / C# プロジェクトテンプレートに同梱している共通 Agent instructions、workflow skills、docs 雛形の正本をユーザレベル資産へ寄せ、各テンプレートには project-level の薄い索引と固有ルールだけを残す。

## Phase 2 の入力

- 調査レポート: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
- 調査レビュー: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/user_level_agent_assets_report_review.md`
- 追跡項目: `docs/todo/todo.md` の `SC-20260508-001`

## この Phase で固定した前提

- 本件は新機能追加ではなく、テンプレート構成と運用導線を変更する `spec-change` として扱う
- workflow / orchestration skill の正本は user-level 配置を前提に再設計する
- プロジェクト固有の検証コマンド、責務境界、docs 実体は project-level に残す
- `docs/procedure/` は project-level 依存を外し、workflow skill 同梱 `references/` へ移す方向で設計する

## 未着手の後続 Phase

- Phase 6: 完了処理、マージ、archive、history 反映

## 最新検証メモ

- 2026-05-09: 隔離した Python target project へ `project-doc-bootstrap` を実行し、docs 雛形、`instructions/agent_common_master.md`、`instructions/agent_sync_guide.md`、`scripts/sync_agent_instructions.*` が配置されることを確認した
- 2026-05-09: 同 target project で `scripts/sync_agent_instructions.sh --help` と `scripts/sync_agent_instructions.sh` の直接実行が成功し、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` が再生成されることを確認した
- 2026-05-09: `copy_doc_templates.sh` の placeholder scan を `docs` に加えて `instructions` と既存生成物 3 種へ拡張し、sync 後の再 scan ガイドを追加した
- 2026-05-09: `sync_agent_instructions.ps1` の `param(...)` を script 先頭へ移動し、PowerShell script としての parameter binding に合わせた
- 2026-05-09: `pwsh -File user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.ps1 -Language python`、`pwsh -File <tmp>/scripts/sync_agent_instructions.ps1 -Help/-All`、`install_user_agent_assets.ps1 -DryRun` が成功し、PowerShell 系の bootstrap / sync / installer dry-run を確認した
- 2026-05-09: `bash user-agent-assets/install/install_user_agent_assets.sh --mode overwrite` により実ユーザールートへ install を実施し、`~/.copilot/skills`、`~/.agents/skills`、`~/.claude/skills`、`~/.codex/skills`、`~/.agentic-project-templates` への展開と wrapper mode `-rwxr-xr-x` を確認した
- 2026-05-09: 新規 Python サンプルプロジェクトで `project-doc-bootstrap`、`copilot-review-automation`、`new-feature-workflow` を実地検証し、改善メモを `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md` に記録した
- 2026-05-09: 改善メモの内容を `docs/issues/cross/issues.md` の `C-2026-001` 〜 `C-2026-008` として follow-up issue 化した
