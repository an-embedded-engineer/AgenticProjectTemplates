---
name: copilot-review-automation
description: {{PROJECT_NAME}} のワークフロー全 Phase を設計・実装 Agent（Copilot Chat または Copilot CLI）が自律実行し、各 Phase のレビューを Copilot CLI（デフォルト: claude-sonnet-4.6）に委任して完了させる手順。spec-change/new-feature/bugfix/issue-resolution/refactoring の Phase 2/3/4/5 レビューと指摘対応確認を自動化する。Codex ではなく Copilot が設計・実装担当として直接動作する構成。
---

# copilot-review-automation

## いつ使う

- ユーザから追跡項目 ID と本スキルを指定された時
- Copilot Chat または Copilot CLI が設計・実装担当として動作し、Copilot CLI をレビュー担当として起動したい時
- 全 Phase を設計・実装担当が自律実行し、各 Phase のレビューを Copilot CLI に委任したい時

## この skill の役割

| 役割 | 担当 | 起動方法 |
|------|------|---------|
| 設計・実装 Agent | Copilot Chat / Copilot CLI | ユーザが直接操作 |
| レビュー Agent | Copilot CLI（デフォルト: `claude-sonnet-4.6`） | `tools/AgentCliTmux` 経由で起動 |

レビュー Agent のデフォルトモデルは `claude-sonnet-4.6`。ユーザが別モデルを指示した場合はそちらを優先する。

## 実行ルール（索引）

- workflow 選択: `docs/procedure/workflow_selection.md`
- workflow Phase 構成: `docs/procedure/workflow_phase_library/README.md`
- 仕様変更: `docs/procedure/spec_change_workflow.md`
- 新機能追加: `docs/procedure/new_feature_workflow.md`
- 不具合修正: `docs/procedure/bugfix_workflow.md`
- 課題解決: `docs/procedure/issue_resolution_workflow.md`
- リファクタリング: `docs/procedure/refactoring_workflow.md`
- レビュー反映手順: `docs/procedure/ai_review_response_workflow.md`
- レビュー観点: `docs/procedure/review_checkpoints.md`
- tmux / Agent CLI 共通スクリプト: `tools/AgentCliTmux`

## 設計・実装 Agent（自身）の責務

1. 追跡項目の workflow 種別を判定して対応する workflow skill を選択する
2. 選択した workflow skill に従い、現在の Phase に必要な成果物だけを作成・更新する
3. 各 Phase の「レビュー依頼前コミット」が完了したら、レビュー Agent にレビューを委任する
4. レビュー Agent の監視・承認ダイアログ対応・指摘取り込みを行う
5. 指摘対応後はレビュー Agent に follow-up を依頼し、承認を確認してから次 Phase へ進む

## Phase 進行ゲート

1. Phase は 1 つずつ順番に進める
2. Phase 2 review 完了前に Phase 3 の設計成果物を作り始めてはならない
3. Phase 3 review 完了前に Phase 4 の実装成果物を作り始めてはならない
4. Phase 4 review 完了とユーザ動作確認完了前に、Phase 5 の恒久ドキュメント同期を始めてはならない
5. 1 Phase の標準ループは `commit -> review -> fix -> follow-up -> approval` の順とする
6. 後続 Phase の正式成果物を承認前に先行生成してはならない

## 運用方針

1. レビュー依頼はユーザの追加承認を待たずに実行してよい
2. レビュー指摘を反映したら、必ずレビュー Agent に対応内容を通知して再確認を依頼する
3. レビュー Agent の再確認で未解決指摘が 0、または明示承認が出た場合にのみ次 Phase へ進む
4. 同一 topic の Phase 2 / 3 / 4 / 5 と follow-up review では、同じ tmux session と同じ Copilot CLI process を継続利用する
5. 監視は一定間隔ポーリングで行う。初回は `send-prompt --submit-delay 5 --sleep-after 5 --capture-after-sleep`、以降は `capture --sleep-before 10`、`capture --sleep-before 30`、`capture --sleep-before 60` のように待機時間を伸ばす
6. 停止判定は保守的に行う。Copilot CLI process 終了、tmux session 消滅、明示エラーがない限り終了や session 再作成を行ってはならない
7. 再作成が必要な場合でも、まず既存 session 再利用を確認し、Copilot CLI process だけ落ちている時は共通スクリプトの `ensure` による再開を優先してよい
8. レビュー Agent が承認待ちダイアログで停止した場合、安全なツール操作は設計・実装 Agent が内容確認後に承認してよい。危険な操作はユーザ確認を優先する
9. Phase 完了や review/follow-up 完了など区切りの良いタイミングで短い状態要約を残す
10. Phase 6 の main マージと後片付けが完了した後だけ、レビュー Agent に終了入力を送り、tmux session も削除する

## 前提

1. `docs/design_analysis/.../<yyyymmdd>_<topic>/` が作成済みである
2. 対象 Phase の「レビュー依頼前コミット」が完了済みである
3. `tmux` と `copilot` コマンドが実行可能である
4. 設計・実装 Agent が `tools/AgentCliTmux` を実行できる

## workflow 判定

1. 明示指定を優先する
   - 仕様変更: `spec-change`
   - 新機能追加: `new-feature`
   - 不具合修正: `bugfix`
   - 課題解決: `issue-resolution`
   - リファクタリング: `refactoring`

2. 明示指定がない時は `issue-dir` から判定する
   - `docs/design_analysis/spec_change/` 配下 → `spec-change`
   - `docs/design_analysis/new_feature/` 配下 → `new-feature`
   - `docs/design_analysis/fix_issues/` 配下 → `bugfix`
   - `docs/design_analysis/issue_resolution/` 配下 → `issue-resolution`
   - `docs/design_analysis/refactoring/` 配下 → `refactoring`
   - 判定不能時はユーザへ確認する

## review 文書命名

1. Phase 2 / 3 / 4 は workflow 共通
   - Phase 2: `<topic>_plan_review.md`
   - Phase 3: `<topic>_design_review.md`
   - Phase 4: `<topic>_impl_review.md`

2. Phase 5 は workflow ごとの suffix を使う
   - `spec-change`: `<topic>_docs_review.md`
   - `new-feature`: `<topic>_feature_docs_review.md`
   - `bugfix`: `<topic>_bugfix_docs_review.md`
   - `issue-resolution`: `<topic>_issue_resolution_docs_review.md`
   - `refactoring`: `<topic>_refactoring_docs_review.md`

## レビュー Agent セッション管理

1. tmux session 名は topic 単位で固定する
   - 書式: `{{PROJECT_NAME_LOWER}}-review-<topic>`
   - 同じ issue の Phase 2 / 3 / 4 / 5 と再レビューでは同じ session を再利用する
   - session 再作成は、tmux 消失、Copilot CLI 異常終了、明示エラー、ユーザ指示のいずれかがある時だけ許可する

2. レビュー Agent は共通スクリプトで起動・再利用する

```bash
REVIEW_MODEL="${REVIEW_MODEL:-claude-sonnet-4.6}"
SESSION_NAME="{{PROJECT_NAME_LOWER}}-review-${TOPIC}"
MAIN_PROJECT_DIR=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')

dotnet run --project tools/AgentCliTmux -- ensure \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --cwd "${MAIN_PROJECT_DIR}" \
  --agent copilot \
  --model "${REVIEW_MODEL}"
```

3. 必要に応じてユーザへ `tmux attach -t <session_name>` を案内してよいが、通常の監視と承認処理は設計・実装 Agent が担当する

## 監視ポリシー

1. レビュー依頼直後は `send-prompt --submit-delay 5 --sleep-after 5 --capture-after-sleep` で、貼り付け 5 秒後に Enter を送り、送信 5 秒後に初回 capture する
2. 以降は `capture --sleep-before 10`、次に `capture --sleep-before 30`、長い処理では `capture --sleep-before 60` のように待機時間を伸ばして監視する
3. レビュー Agent が承認ダイアログで停止して設計・実装 Agent が承認した直後は、連続承認待ちを拾うため `capture --sleep-before 5` に戻す
4. 完全に thinking / tool 実行中であることが見えた場合だけ、再び `10s -> 30s -> 60s` へ伸ばす
5. さらに長い処理では必要に応じて `sleep` サブコマンド単体で待機してから capture する
6. thinking 表示、token 増減、ツール使用、review ファイル更新、コミット作成のいずれかが見える間は「進行中」とみなす
7. 5 分未満の無変化は通常範囲として扱い、停止扱いしない
8. 10 分程度、意味のある進捗が見えない場合は、ユーザへ対応方針を確認する
9. Copilot CLI process 終了、tmux session 消失、明示エラーが確認できる場合は、ユーザ確認前でも再起動してよい

## レビュー依頼の基本手順

1. workflow / phase / issue-dir / topic / 最新コミット hash を確定する
2. review 文書の出力先を決める
3. prompt file を作成する
   - 一時ファイル例: `${MAIN_PROJECT_DIR}/tmp/{{PROJECT_NAME_LOWER}}_copilot_review_prompt.txt`
   - 長文は `send-prompt` サブコマンドで送る

4. レビュー Agent にレビューを依頼する

```bash
mkdir -p "${MAIN_PROJECT_DIR}/tmp"
PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/{{PROJECT_NAME_LOWER}}_copilot_review_prompt.txt"

dotnet run --project tools/AgentCliTmux -- send-prompt \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --file "${PROMPT_FILE}" \
  --submit-delay 5 \
  --sleep-after 5 \
  --capture-after-sleep \
  --lines 120
```

5. 一定間隔で出力を監視する

```bash
dotnet run --project tools/AgentCliTmux -- capture \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --lines 120 \
  --sleep-before 10

dotnet run --project tools/AgentCliTmux -- capture \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --lines 120 \
  --sleep-before 30
```

6. レビュー Agent が承認ダイアログで停止したら内容を確認し、安全な操作は承認する。承認後は次の capture を `--sleep-before 5` に戻し、連続する承認待ちがないか確認する
7. レビュー Agent が review 文書をコミットした hash を取得して、次の処理に進む

## 初回レビュー依頼テンプレート

```text
<workflow-skill-name> スキルのレビュー手順に従ってください。
あなたはレビュー担当 Agent です。
<issue-file>
<issue-id>. <issue-title>
の Phase <plan|design|impl|docs> レビューをお願いします。
下記コミットから必要なファイルを取得して確認してください。
<commit-hash>

レビュー結果は <review-document-path> に反映し、コミットまで実施してください。
レビュー観点は docs/procedure/review_checkpoints.md と現在の workflow 文書に従ってください。
```

## 指摘対応確認テンプレート

```text
レビュー指摘の対応が完了しました。
下記コミットから差分を取得して再確認してください。
<fix-commit-hash>

未解決指摘があれば <review-document-path> に追記してコミットしてください。
問題なければ、承認したことが分かる形で出力してください。
```

## 反復ルール

1. レビュー Agent が未承認なら、最新 review コミット hash を設計・実装 Agent の作業コンテキストへ取り込み、`ai-review-response-workflow` に従って対応する
2. 対応後は fix コミット hash を使ってレビュー Agent に再確認を依頼する
3. レビュー Agent の再確認で未解決指摘が 0 になるまで繰り返す
4. 同じ Phase で 3 回連続で未承認になったら、論点を整理してユーザへエスカレーションする

## 最低限の必須チェック

1. レビュー対象ファイルが保存済みであることを確認する
2. `REVIEW_MODEL` を確定する
3. レビュー Agent session 起動後は状態監視する
4. 生成された review 文書が空でないことを確認する
5. レビュー Agent が review 文書をコミットした hash を取得してから次の処理に進む
6. Follow-up 時は未解決指摘ゼロ、または明示承認を確認する
7. Phase 5 の review 文書名が workflow ごとの命名規則に一致していることを確認する
8. レビュー指摘反映後は必ずレビュー Agent に follow-up を送って確認結果を取得する
9. review 完了確認後は停滞せず、そのまま指摘対応を開始する
10. review ループが 1 Phase 分完了したら、次 Phase へ進む前に短い状態要約を残す
11. 後続 Phase へ移る前に、現 Phase の review / follow-up / 承認 / post-review update が閉じていることを確認する

## 終了処理

Phase 2-5 の review / 指摘対応 / follow-up の途中では tmux session を終了しない。
Phase 6 の main マージと後片付けが完了した後、またはユーザが終了を明示指示した時だけ session を削除する。

```bash
dotnet run --project tools/AgentCliTmux -- stop \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --agent copilot \
  --kill-session
```

## トラブルシューティング

- Agent 出力が取得できない: `status` サブコマンドで session / pane / current command を確認する
- プロンプト投入が崩れる: prompt file を作り直し、`send-prompt --submit-delay 5` で再投入する
- レビュー Agent が review 文書をコミットしない: 「レビュー文書の更新とコミットまでお願いします」と追送する
- 承認ダイアログで停止する: まず設計・実装 Agent がコマンド内容を確認し、安全なら承認、危険ならユーザへ確認する。承認後は `capture --sleep-before 5` に戻す