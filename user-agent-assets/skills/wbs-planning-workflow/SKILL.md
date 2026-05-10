---
name: wbs-planning-workflow
description: 大規模変更を通常 workflow で完了可能な work package へ分解し、依存順序、推奨 workflow、完了条件、検証観点、docs 更新先を整理する手順。
---

# wbs-planning-workflow

## いつ使う

- 1 回の `spec-change` / `new-feature` / `bugfix` / `issue-resolution` / `refactoring` / `documentation` では範囲が大きすぎる時
- 複数コンポーネント、複数 workflow 種別、段階的な実施順序を先に整理する必要がある時
- 実装前に作業分解、依存関係、受け入れ条件、検証観点を固定したい時

## 実行ルール（索引）

- 手順本体: `references/procedure/wbs_planning_workflow.md`
- workflow 選択: workflow 判定ルール
- 共通ルール: `各プロジェクトの開発・検証コマンド定義`

## 禁止事項

- WBS topic 内で実装を開始してはならない
- work package を、1 つの通常 workflow で完了できない粒度のまま残してはならない
- 推奨 workflow、依存 work package、完了条件、検証観点が空の work package を作ってはならない

## 最低限の必須チェック

1. 背景、目的、完了条件、非対象を固定する
2. `docs/design_analysis/wbs/<yyyymmdd>_<topic>/` を作成する
3. `meta.md`、`wbs.md`、`report.md` を作成する
4. work package は `WP-001` 形式で ID を付与する
5. 各 work package に推奨 workflow、依存、目的、完了条件、変更対象、docs 更新先、検証観点を記録する
6. 分解後の実行順序と、通常 workflow へ引き継ぐ追跡項目を明記する
7. WBS 完了時はユーザへ報告し、次に着手する work package の承認を待つ
