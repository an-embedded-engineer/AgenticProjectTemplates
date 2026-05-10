# TODO Archive 2026

## Closed

### TODO-2026-001: workflow skill Phase 簡略化の仕様変更

- workflow: `spec-change`
- status: `done`
- completed_at: `2026-05-11`
- source_branch: `research/workflow-phase-simplification-20260510`
- merge_commit: `pending`
- source_report: `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/report.md`
- source_review: `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/workflow_phase_simplification_report_review.md`
- meta: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/meta.md`
- adr: `docs/adr/0001_workflow_phase_simplification.md`
- design: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/design/workflow_phase_simplification_design.md`
- impl: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/impl/workflow_phase_simplification_impl.md`
- review: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/review/workflow_phase_simplification_impl_review.md`
- change_report: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/change_report.md`
- diff_archive: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/diff.zip`
- installed_targets: `codex,claude,copilot`
- related_commits:
	- `3fdc918`: 調査開始
	- `9f8c568`: research review 最終承認
	- `262e7e0`: workflow skill Phase 簡略化実装
	- `10cca57`: Claude 実装レビュー
	- `1153778`: レビュー指摘対応承認
	- `8fb8540`: `change_report.md` 命名補正
	- `8ec0551`: 追加修正レビュー承認

#### 概要

core workflow skill を 4 ゲート構成へ簡略化し、Phase 2 を方針・設計レビュー、Phase 3 を実装・恒久ドキュメント反映レビュー、Phase 4 を動作確認・完了処理・merge 承認へ再構成した。大規模変更の計画は `wbs-planning-workflow` へ分離し、review automation / orchestrator / ai-review-response 系 skill と bootstrap template の運用文書も同期した。

Phase 4-b の差分・変更レポート名は `change_report.md` に統一し、research-analysis / WBS の `report.md` と衝突しないよう整理した。user-level assets は `codex,claude,copilot` に overwrite install 済み。

### SC-20260508-001: ユーザレベル Agent 資産化

- workflow: `spec-change`
- status: `done`
- merged_at: `2026-05-09`
- merge_commit: `55075be`
- source_research: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
- review: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/user_level_agent_assets_report_review.md`
- meta: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/meta.md`
- plan: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md`
- design: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md`
- impl: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/impl/user_level_agent_assets_impl.md`
- impl_reviews:
	- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_codex.md`
	- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_claude.md`
	- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_copilot_cli.md`
- docs_review: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_docs_review.md`
- report: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/report.md`
- improvement_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- follow_up_issues:
	- `docs/issues/cross/issues.md#c-2026-001-review-automation-preflight-標準化`
	- `docs/issues/cross/issues.md#c-2026-002-新規プロジェクト向け-pre-review-bootstrap-支援`
	- `docs/issues/cross/issues.md#c-2026-003-skill-間参照パスの正規化と存在確認`
	- `docs/issues/cross/issues.md#c-2026-004-copilot-cli-初回-prompt-投入の-handshaking-導入`
	- `docs/issues/cross/issues.md#c-2026-005-review-session-の権限ダイアログ運用改善`
	- `docs/issues/cross/issues.md#c-2026-006-bootstrap-後の検証依存準備を明示`
	- `docs/issues/cross/issues.md#c-2026-007-_example_component-再配置ノイズの低減`
	- `docs/issues/cross/issues.md#c-2026-008-review-agent-の-tool-error-復帰方針明文化`

#### 概要

Python / C# project 向けに分散していた汎用 Agent instructions / workflow skills / docs templates を user-level Agent 資産として正本化し、repo 自体も user-level assets と bootstrap 資産の保守構成へ移行した。
