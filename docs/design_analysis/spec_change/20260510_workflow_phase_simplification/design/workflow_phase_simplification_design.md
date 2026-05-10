# workflow skill Phase 簡略化 設計

## 背景・要求

`TODO-2026-001` と調査レポートに基づき、core workflow の `plan -> design -> impl -> docs反映` を簡略化し、review loop と meta 更新の固定費を減らす。

## 採用方針

- Phase 2 は要求、範囲、採否理由、リスク、テスト観点を含む「方針・設計レビュー」にする
- Phase 3 は実装、`impl/` 文書、恒久ドキュメント反映をまとめた「実装・恒久ドキュメント反映レビュー」にする
- Phase 4 は `4-a 動作確認`、`4-b 完了処理`、`4-c merge 承認` に分ける
- `meta.md` は `design_status`、`impl_status`、`completion_status` を使う
- `related_commits` は core workflow では completion 集約にする
- completion review は optional とし、標準 review は design / impl の 2 本にする
- Phase 簡略化は横断判断として ADR-0001 に記録する

## 非対象

- install / sync script の仕様変更

## 影響範囲

- shared common phase library
- 5 種の core workflow procedure と focus 文書
- review automation / orchestrator / ai-review-response workflow
- wbs-planning-workflow
- `docs/design_analysis/README.md`
- Python / C# bootstrap template の design_analysis README

## 恒久ドキュメント更新予定先

- `docs/adr/README.md`
- `docs/adr/0001_workflow_phase_simplification.md`
- `docs/design_analysis/README.md`
- `user-agent-assets/skills/project-doc-bootstrap/templates/python/docs/design_analysis/README.md`
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/docs/design_analysis/README.md`

## 検証観点

- shared common phase library が Phase 2/3/4 の新手順だけを持っている
- 5 種 core workflow が Phase 2/3/4 の新 common 手順と新 focus 文書を参照している
- review automation の標準命名が design / impl / optional completion に揃っている
- installer の dry-run が shared common の hydrate 経路を維持している
