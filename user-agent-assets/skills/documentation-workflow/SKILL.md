---
name: documentation-workflow
description: プロジェクトのドキュメントのみを作成・更新・整理する手順。ソースコード、生成ツール、実行時挙動を変更せず、README、docs、設計分析、履歴、手順書、索引、archive などの文書だけを扱う時に使う。動作確認フローやソース差分用 diff.zip を不要とし、リンク・整合・構成確認を中心に完了処理する。
---

# documentation-workflow

## いつ使う

- README、docs、設計分析、履歴、手順書、索引、archive など、文書だけを作成・更新・整理する時
- ソースコード、テンプレート生成ツール、runtime、テスト対象の実行時挙動を変更しない時
- 既存 workflow の完了処理だけでは重すぎる、軽量な docs-only 変更として扱いたい時

## 使わない時

- ソースコード、スクリプト、設定、テンプレート、runtime asset を変更する時は、変更内容に応じて `spec-change-workflow` / `new-feature-workflow` / `bugfix-workflow` / `issue-resolution-workflow` / `refactoring-workflow` を使う
- 調査レポートそのものを作成する時は `research-analysis-workflow` を使う
- 大規模変更を work package へ分解する時は `wbs-planning-workflow` を使う

## 実行ルール（索引）

- 手順本体: `references/procedure/documentation_workflow.md`
- workflow 選択: workflow 判定ルール
- 共通ルール: `各プロジェクトのドキュメント運用ルール`
- 検証コマンド: `各プロジェクトの開発・検証コマンド定義` のうち、文書変更で必要なものだけを使う

## 禁止事項

- ソースコード、スクリプト、設定、runtime、生成テンプレートの挙動を変更してはならない
- アプリ起動やユーザ動作確認を必須工程にしてはならない
- ソース変更がない場合に `diff.zip` を作成してはならない
- レビュー文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. 対象文書、目的、非対象を固定する
2. 変更が docs-only であることを確認する
3. 必要なら `docs/todo/todo.md` に対象項目を記録する
4. 専用ブランチと `meta.md` を作成する
5. 文書更新方針を設計文書にまとめ、必要時は設計レビューを受ける
6. 文書を更新し、リンク、索引、重複、archive、履歴の整合を確認する
7. `change_report.md` を作成するが、docs-only では `diff.zip` を作成しない
8. 完了時は `todo_archive_<year>.md` へ移し、必要な STOP ゲートで承認を待つ
