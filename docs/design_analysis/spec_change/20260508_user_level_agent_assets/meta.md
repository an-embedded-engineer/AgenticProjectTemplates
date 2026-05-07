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
impl_status: not_started
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

- Phase 4: user-level assets / bootstrap skill / sync source 再編の実装
- Phase 5: smoke test、テンプレート検証、恒久ドキュメント同期