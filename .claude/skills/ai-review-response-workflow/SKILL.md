---
name: ai-review-response-workflow
description: AIレビュー結果を分類し、設計書とレビュードキュメントへ反映し、未解決事項を管理する手順。
---

# ai-review-response-workflow

## いつ使う

- 設計レビュー/コードレビューの結果を反映する時

## 実行ルール（索引）

- 手順本体: `docs/procedure/ai_review_response_workflow.md`
- レビュー観点詳細: `docs/procedure/review_checkpoints.md`
- 共通ルール: `docs/rules/coding_rules.md`

## 最低限の必須チェック

1. 指摘を重大度・優先度で分類する
2. 指摘を `plan` / `design` / `impl` の工程で分類する
3. 対象工程文書とレビュー文書の両方を更新する
4. レビュードキュメントを原則 `docs/design_analysis/<category>/<yyyymmdd>_<topic>/review/` に配置する
5. 全指摘に対応ステータスを付ける
6. 未解決事項を質問または follow-up として明示する
