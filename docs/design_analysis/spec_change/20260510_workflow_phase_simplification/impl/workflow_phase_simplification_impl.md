# workflow skill Phase 簡略化 実装記録

## 実装内容

- shared common phase library を 4 ゲート構成へ更新した
- 5 種 core workflow の Phase 一覧、承認ゲート、commit 運用を更新した
- workflow 別 focus 文書を `phase_2_design_focus.md`、`phase_3_impl_and_docs_focus.md`、`phase_4_completion_focus.md` に再編した
- `ai-review-response-workflow`、`claude-review-automation`、`copilot-review-automation`、orchestrator 系 skill の Phase 契約を更新した
- 大規模変更を work package へ分解する `wbs-planning-workflow` を追加した
- `docs/design_analysis/README.md` と Python / C# bootstrap template の同等 README を更新した
- ADR-0001 を追加した

## 決定事項

- 恒久 docs は Phase 3 の impl review 対象として code と同時更新する
- todo / issue archive、history、report、merge 承認は Phase 4 completion に残す
- WBS 分解の成果物は `docs/design_analysis/wbs/<yyyymmdd>_<topic>/` に配置する

## 検証

- 残存参照チェック
- user-level assets installer dry-run
- project-level instruction sync help
- Python compile / pytest
- .NET build / test

検証結果は `report.md` に記録する。
