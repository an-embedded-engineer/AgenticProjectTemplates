---
name: research-analysis-workflow
description: AgenticProjectTemplatesの調査・分析で、依頼整理、ブランチ作成、ソース/ドキュメント調査、レポート作成、レビュー依頼、指摘対応ループ、完了通知までを行う手順。
---

# research-analysis-workflow

## いつ使う

- 実装・仕様変更・不具合修正に入る前に、現状調査、論点整理、選択肢比較、リスク洗い出しを行う時
- 既存コードと既存文書の整合確認、レビュー指摘の深掘り、設計前提の棚卸しを行う時
- 実装や恒久修正そのものが主目的なら、対応する workflow へ切り替える

## 実行ルール（索引）

- 手順本体: `docs/procedure/research_analysis_workflow.md`
- workflow 選択: `docs/procedure/workflow_selection.md`
- レビュー観点詳細: `docs/procedure/review_checkpoints.md`
- design_analysis 運用: `docs/design_analysis/README.md`
- 共通ルール: `docs/rules/coding_rules.md`
- 実行コマンド: `docs/rules/development_workflow.md`

## 禁止事項

- Phase 0（依頼整理）と Phase 1（ブランチ作成）を飛ばして調査成果物を追加してはならない
- 調査担当 Agent が自分でレビュー文書を作成してはならない
- 根拠を示せない推測を、事実のように `report.md` へ記載してはならない
- 調査・分析 workflow のまま実装変更を進めてはならない
- レビュー未完了のまま結論を確定してはならない

## 最低限の必須チェック

1. Phase 0 で調査目的、観点、非対象、期待成果物を固定する
2. Phase 1 で調査専用ブランチを作成する
3. `docs/design_analysis/research_analysis/<YYYYMMDD>_<topic>/` を作成する
4. `meta.md` と `report.md` を作成する
5. `report.md` に調査対象、根拠ソース、現状整理、論点、推奨方針、未解決事項を残す
6. レビュー担当 Agent は同ディレクトリに `<topic>_report_review.md` を作成する
7. 調査担当 Agent とレビュー担当 Agent は各ラウンドで必ずコミットを残す
8. 指揮者はレビュー完了を調査担当 Agent に通知し、指摘がなくなるまでレビューと対応を繰り返す
9. `meta.md` の `status` と `related_commits` を更新する
10. 完了時はユーザへ結論、根拠、次の推奨 workflow を報告する
