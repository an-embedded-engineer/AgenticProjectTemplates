# Change History 2026

## 2026-05-11

### ドキュメント専用 workflow skill を追加

- skill: `user-agent-assets/skills/documentation-workflow/`

ドキュメントのみの作成・更新・整理を扱う `documentation-workflow` を追加した。ソース変更を伴う core workflow と分け、アプリ動作確認や docs-only 変更での `diff.zip` 作成を不要とし、リンク、索引、重複、archive、history の整合確認を完了条件にした。

あわせて design analysis の `documentation` カテゴリ、WBS の推奨 workflow 候補、review / orchestrator 系 skill の workflow 判定を同期した。

### workflow skill Phase 簡略化を main へ統合

- design_analysis: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/`
- source_branch: `research/workflow-phase-simplification-20260510`
- adr: `docs/adr/0001_workflow_phase_simplification.md`
- change_report: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/change_report.md`
- merge_commit: `4440093`

core workflow skill を 4 ゲート構成へ簡略化し、Phase 2 を方針・設計レビュー、Phase 3 を実装・恒久ドキュメント反映レビュー、Phase 4 を動作確認・完了処理・merge 承認へ再構成した。

あわせて、大規模変更の計画を core workflow に戻さず `wbs-planning-workflow` として独立させ、review automation / orchestrator / ai-review-response 系 skill の Phase 名と review 文書命名を同期した。Phase 4-b の差分・変更レポートは `change_report.md`、ソース変更時の差分アーカイブは `diff.zip` として扱う。

## 2026-05-09

### ユーザレベル Agent 資産化を main へ統合

- design_analysis: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/`
- source_branch: `feature/spec-user-level-agent-assets-20260508`
- merge_commit: `55075be`

Python / C# project 向けに分散していた Agent instructions、workflow skills、docs bootstrap assets を user-level 配布前提の `user-agent-assets/` へ集約した。あわせて runtime / bootstrap tool の責務を再配置し、旧 template ディレクトリと repo-local skill 資産を撤去した。

追加で、Copilot CLI の skill load error を引き起こしていた `copilot-review-automation` の YAML frontmatter を修正し、user root への再 install と実起動確認まで完了した。
