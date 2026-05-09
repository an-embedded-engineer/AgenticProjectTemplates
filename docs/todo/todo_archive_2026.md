# TODO Archive 2026

## Closed

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