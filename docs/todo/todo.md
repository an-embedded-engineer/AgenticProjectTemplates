# TODO

`spec-change` / `new-feature` / `refactoring` の追跡項目を管理する。

## Open

### SC-20260508-001: ユーザレベル Agent 資産化

- workflow: `spec-change`
- status: `phase_5_done`
- source_research: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
- review: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/user_level_agent_assets_report_review.md`
- meta: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/meta.md`
- plan: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md`
- design: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md`
- impl_reviews:
	- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_codex.md`
	- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_claude.md`
- docs_review: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_docs_review.md`
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

#### 目的

Python / C# プロジェクトテンプレートに同梱している汎用的な Agent instructions / workflow skills / docs templates を、ユーザレベル Agent 資産として正本化し、各プロジェクトテンプレートにはプロジェクト固有の薄い instructions と成果物置き場だけを残す。

#### 変更対象

- user-level workflow skills の正本ディレクトリと install script
- docs bootstrap skill と docs template 配布方式
- `instructions/agent_common_master.md` と `instructions/*.draft.md` の project-level index 化
- `docs/procedure/` の workflow skill `references/` 化
- `docs/rules/skill_catalog.md` の削除方向整理と参照元更新
- `agent_cli_tmux` / `AgentCliTmux` の OS 別 wrapper または publish 済み executable 同梱方針

#### 非対象

- Phase 0 時点での実装変更
- Copilot / Claude / Codex 以外の Agent runtime への対応
- user-level skill install 後の個人環境設定そのものの強制上書き

#### 受け入れ条件

- `~/.copilot/skills` に配置した最小 skill を Copilot Chat / Copilot CLI から検出できるかを smoke test として確認する
- workflow skill が `docs/procedure/` を project-level に要求せず、skill 内 `references/` から必要手順を参照できる
- user-level install script は `dry-run`、`missing-only default`、既存 user skill の上書き保護、未作成 skill directory の作成に対応する
- `SKILL.master.md` 由来の user-level `SKILL.md` はプロジェクト名 placeholder を除去した一般 skill になる
- `docs/rules/skill_catalog.md` を削除方向で整理し、`CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md` / 各 `SKILL.master.md` の参照も同時に更新される
- Agent CLI helper は `python` / `dotnet` 全体ではなく、OS 別 wrapper または publish 済み executable 単位で allowlist できる
- Python / C# テンプレートの project-level instructions は、共通原則ではなくプロジェクト固有のルール、検証コマンド、成果物置き場の索引に縮小される
