---
title: "ユーザレベル Agent 資産化の妥当性調査"
created_date: "2026-05-07"
category: research_analysis
components:
  - instructions
  - skills
  - docs_templates
  - python-project-template
  - csharp-project-template
status: in_review
related_commits:
  - dd6e612 : Phase 1 meta 初期化
  - e40aabe : Phase 2 調査レポート作成
  - 51cc2b1 : Phase 3 レビュー依頼前ステータス更新
  - 5fa6c58 : Phase 3 Claude レビュー Round 1
source_design_path: docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md
---

# メタ情報

## 調査目的

`instructions`、`skills`、`docs` 基盤を Python / C# プロジェクトテンプレートからユーザレベルの Agent 資産へ移す案について、妥当性と実現方法を整理する。

## 調査観点

- 現行テンプレート構成と同期元の責務
- ユーザレベル instructions / skills へ移す利点と制約
- docs テンプレートを skill 経由で配布する場合の変更範囲
- Python / C# テンプレート間同期ルールへの影響

## 非対象

- 実装変更そのもの
- 新しいユーザレベル skill の実装
- 既存テンプレートからのファイル削除

## 期待成果物

- 調査レポート
- Claude によるレビュー文書
- 次 workflow への推奨
