# ADR-0001: workflow Phase 簡略化

## Status

Accepted

## Context

`user-agent-assets/skills` の core workflow は、従来 `plan -> design -> impl -> docs反映 -> completion` を個別 Phase として扱っていた。通常規模の変更でも review loop、meta 更新、ユーザ承認が増え、実行コストが大きくなっていた。

## Decision

新規の core workflow topic は、次の 4 ゲート構成を標準にする。

| Phase | 目的 |
|---|---|
| 0 | 要求・課題・事象の固定 |
| 1 | ブランチ・meta 初期化 |
| 2 | 方針・設計レビュー |
| 3 | 実装・恒久ドキュメント反映レビュー |
| 4 | 動作確認・完了処理 |

Phase 2 の `design/` 文書には、実装前に合意すべき要求、範囲、採否理由、リスク、テスト観点を記録する。

恒久仕様・設計ドキュメントは Phase 3 で code / `impl/` 文書と同時に更新し、todo / issue archive、history、report、merge 前承認は Phase 4 に残す。

`meta.md` は `design_status`、`impl_status`、`completion_status` を使う。core workflow の `related_commits` は Phase 途中で逐次追記せず、completion で主要 commit をまとめて記録する。research-analysis workflow と多段レビュー topic は round 単位の証跡を維持してよい。

大規模変更は `wbs-planning-workflow` で work package へ分解してから、各 work package を通常 workflow で扱う。

## Consequences

- core workflow の標準 review 文書は `<topic>_design_review.md` と `<topic>_impl_review.md` になる。
- completion review は必要時のみ `<topic>_completion_review.md` として扱う。
- 大規模変更の上位計画は `docs/design_analysis/wbs/` に配置する。
- WBS 分解後の work package は通常 workflow で個別に完了させる。

## References

- `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/report.md`
- `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/`
