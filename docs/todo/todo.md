# TODO

`spec-change` / `new-feature` / `refactoring` の追跡項目を管理する。

## Open

### TODO-2026-001: workflow skill Phase 簡略化の仕様変更

- status: `open`
- priority: `high`
- recommended_workflow: `spec-change-workflow`
- source_report: `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/report.md`
- source_review: `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/workflow_phase_simplification_report_review.md`
- scope:
	- `user-agent-assets/shared/references/procedure/workflow_phase_library/common`
	- `user-agent-assets/skills/spec-change-workflow`
	- `user-agent-assets/skills/new-feature-workflow`
	- `user-agent-assets/skills/bugfix-workflow`
	- `user-agent-assets/skills/issue-resolution-workflow`
	- `user-agent-assets/skills/refactoring-workflow`
	- `user-agent-assets/skills/ai-review-response-workflow`
	- `user-agent-assets/skills/claude-review-automation`
	- `user-agent-assets/skills/copilot-review-automation`
	- `user-agent-assets/skills/autonomous-workflow-orchestrator`
	- `user-agent-assets/skills/copilot-cli-workflow-orchestrator`
	- `docs/design_analysis/README.md`
- summary:
	- core workflow の `plan -> design -> impl -> docs反映` を簡略化し、標準を 4 ゲート構成へ移行する
	- Phase 2 は plan/design を統合した「方針・設計レビュー」にし、要求・完了条件・対象/非対象・採否理由・リスク・テスト観点を design 文書へ必須章として残す
	- Phase 3 は実装と恒久 docs 反映方針の確定を扱い、docs 実体更新は「案 A: impl 同時更新」または「案 B: completion 更新」を Phase 0 で確定する
	- Phase 4 は `4-a 動作確認 STOP`、`4-b 完了処理`、`4-c merge 承認 STOP` の内部 step に分け、archive / history / merge をユーザ確認 OK 前に進めない
	- 大規模 planning は core workflow に重い plan Phase を戻さず、WBS 分解 skill または research-analysis 派生として別 workflow 化する
	- core workflow の `related_commits` は completion 集約を検討し、research / 多段レビュー topic は round 単位記録を維持する
- phase0_decisions:
	- WBS 分解を案 A（独立 `docs/design_analysis/wbs/` category + `wbs-planning-workflow`）にするか、案 B（`research-analysis-workflow` 派生 + `wbs.md`）にするか
	- 恒久 docs 実体更新を Phase 3 同時更新にするか、Phase 4-b 更新にするか
	- `meta.md` status は移行期互換（`plan_status: N/A` + `design_status` + `impl_status` + `completion_status`）で開始し、完全な `phase_status` 移行は別 ADR / spec-change にするか
	- `related_commits` は core workflow では substantive commit 中心にするか、meta-only 更新 commit も含めるか
	- Phase 簡略化を ADR 候補として起票するか
- acceptance:
	- shared common phase library の正本が 4 ゲート構成へ更新され、install / sync の hydrate 結果で各 workflow skill に反映される
	- 5 種 core workflow と workflow 別 focus 文書が plan/design 統合後の構成で揃う
	- review automation / orchestrator / ai-review-response-workflow の Phase 名、review 文書命名、ユーザ確認ゲートが新構成へ同期される
	- `docs/design_analysis/README.md` が新規 topic 用の標準構成、completion review optional、旧文書非移行方針を説明する
	- 小さな文書変更タスクで smoke test を行い、design / impl review と optional completion review の運用が破綻しない
