---
name: copilot-cli-workflow-orchestrator
description: CopilotがCopilot CLI（実装Agent・レビューAgent）を指揮し、追跡項目のworkflowを判定してspec-change/new-feature/bugfix/issue-resolution/refactoringを全Phase自律完了させる手順。実装AgentはCodex系モデル、レビューAgentはClaude Opus系モデルをCopilot CLIのモデル選択で切替えて実行する。
---

# copilot-cli-workflow-orchestrator

## いつ使う

- ユーザから追跡項目 ID（例: `TODO-2026-001`, `C-2026-010`）と本スキルを指定された時
- `spec-change` / `new-feature` / `bugfix` / `issue-resolution` / `refactoring` の全フェーズを Copilot CLI のみで自律的に完了させたい時
- GitHub Copilot サブスクリプションのみで完結させたい時

## 役割分担

| 役割 | 担当 | 責務 |
|------|------|------|
| 指揮者 (Conductor) | **Copilot（本スキルを実行する）** | 追跡項目判定、workflow 選択、Phase 管理、レビュー評価、ユーザ通知、エスカレーション判断 |
| 実装 Agent | **Copilot CLI** (`--model gpt-5.3-codex` 等、tmux 監視インタラクティブ) | 対応 workflow の全 Phase 実行・コミット |
| レビュー Agent | **Copilot CLI** (`--model claude-opus-4.6` 等、tmux 監視インタラクティブ) | 各 Phase 成果物のレビュー文書作成・指摘追跡 |

## 実行ルール（索引）

- 手順本体: `docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md`
- workflow 選択: `docs/procedure/workflow_selection.md`
- 実装ワークフロー
  - `docs/procedure/spec_change_workflow.md`
  - `docs/procedure/new_feature_workflow.md`
  - `docs/procedure/bugfix_workflow.md`
  - `docs/procedure/issue_resolution_workflow.md`
  - `docs/procedure/refactoring_workflow.md`
- レビュー反映: `docs/procedure/ai_review_response_workflow.md`
- レビュー観点: `docs/procedure/review_checkpoints.md`

## 禁止事項

- ユーザへの確認なしに master マージを行ってはならない
- 実装 Agent の tmux ペインを Phase 途中で破棄してはならない
- 実装 Agent に git worktree を作成させてはならない
- Phase 5 のユーザ動作確認ゲートをスキップしてはならない
- レビュー Agent の承認なしに次の Phase に進んではならない

## 最低限の必須チェック

1. `docs/todo/` または `docs/issues/` の追跡項目を読み、5 種類の workflow から正しく判定する
2. 判定結果に応じて対応 skill を選択する
3. `git worktree list` でメインプロジェクトディレクトリを特定し、実装 Agent の作業先として指定する
4. モデル構成を確定する（デフォルト: 実装 `gpt-5.3-codex` / レビュー `claude-opus-4.6`）
5. tmux セッション `{{PROJECT_NAME_LOWER}}-orchestrator` を作成し、実装 Agent をペイン 0・レビュー Agent をペイン 1 に起動する
6. 各 Phase 完了後に待機メッセージを検知してから次の指示を送る
7. 各 Phase のレビュー後に open 指摘が 0 になるまで修正ループを継続する
8. Phase 5 ではユーザ動作確認を必ず要求し、結果を待つ
9. open 指摘の修正ループは最大 3 回とし、超過時はユーザへエスカレーションする
10. 最終マージ前に必ずユーザ承認を取得する
11. 完了後にユーザへ結果サマリーを報告する
