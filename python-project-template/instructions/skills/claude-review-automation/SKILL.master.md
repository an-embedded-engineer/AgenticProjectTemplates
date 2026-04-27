---
name: claude-review-automation
description: {{PROJECT_NAME}} のレビュー依頼を Claude Code CLI のインタラクティブモードで自動化する手順。Codex が scripts/agent_cli_tmux.py 経由で Claude を起動・監視し、spec-change/new-feature/bugfix/issue-resolution/refactoring の Phase 2/3/4/5 レビューと指摘対応確認を代行する。
---

# claude-review-automation

## いつ使う

- Codex から Claude Code CLI へレビューを委任したい時
- `spec-change` / `new-feature` / `bugfix` / `issue-resolution` / `refactoring` の Phase 2 / 3 / 4 / 5 で review 文書作成と follow-up 確認を回したい時

## 実行ルール（索引）

- workflow 選択: `docs/procedure/workflow_selection.md`
- 仕様変更: `docs/procedure/spec_change_workflow.md`
- 新機能追加: `docs/procedure/new_feature_workflow.md`
- 不具合修正: `docs/procedure/bugfix_workflow.md`
- 課題解決: `docs/procedure/issue_resolution_workflow.md`
- リファクタリング: `docs/procedure/refactoring_workflow.md`
- レビュー反映手順: `docs/procedure/ai_review_response_workflow.md`
- レビュー観点: `docs/procedure/review_checkpoints.md`
- tmux 監視の基準手順: `docs/procedure/autonomous_workflow_orchestrator.md`
- tmux / Agent CLI 共通スクリプト: `scripts/agent_cli_tmux.py`

## この skill の役割

- この skill は、ユーザが Codex を指揮している状況で、Codex がレビュー担当の Claude を代理起動してレビュー依頼する時に使う
- `autonomous-workflow-orchestrator` と違い、Codex 自身は tmux 管理しない。tmux で起動・監視するのは Claude だけでよい
- レビュー依頼後の指摘反映は `ai-review-response-workflow` に従う

## 運用方針

1. Claude へのレビュー依頼は、対象 Phase のレビュー依頼前コミットが揃っていればユーザの追加承認を待たずに実行してよい
2. レビュー指摘を反映したら、必ず Claude に対応内容を通知して再確認を依頼する
3. Claude の再確認で未解決指摘が 0、または明示承認が出た場合にのみ次 Phase へ進む
4. Claude のレビュー中は `sleep` を使った一定間隔ポーリングで状態監視する。レビューは 5 分程度かかることがあるため、短時間の `thinking` / token 増加だけで停止扱いしてはならない
5. 停止判定は保守的に行う。明示的な失敗（Claude プロセス終了、tmux セッション消滅、エラー出力、承認ダイアログ放置以外でプロンプトへ戻る等）がない限り、`/exit` やセッション再作成を行ってはならない
6. Claude が承認待ちダイアログで停止した場合、危険なコマンド（例: `rm`, `git reset`, 破壊的 checkout 等）はユーザ確認を優先し、それ以外（review 文書編集、`git add`, `git commit`, 通常の `git status` 等）は Codex が内容確認後に承認してよい
7. review 文書の作成完了と reviewer commit を確認できたら、Codex はその結果を取り込んで直ちに指摘対応へ進む
8. Phase 完了や review/follow-up 完了など区切りの良いタイミングでは、Codex は短い状態要約を残してコンテキストを整理する。利用中の CLI が `/compact` を提供している場合は、その時点で実行してよい
9. すべての Phase が完了したら Claude に `/exit` を送り、tmux セッションも削除する

## 前提

1. `docs/design_analysis/.../<yyyymmdd>_<topic>/` が作成済みである
2. 対象 Phase の「レビュー依頼前コミット」が完了済みである
3. `tmux` と `claude` コマンドが実行可能である
4. Codex が `scripts/agent_cli_tmux.py` を実行できる

## workflow 判定

1. 明示指定を優先する
- 仕様変更: `spec-change`
- 新機能追加: `new-feature`
- 不具合修正: `bugfix`
- 課題解決: `issue-resolution`
- リファクタリング: `refactoring`

2. 明示指定がない時は `issue-dir` から判定する
- `docs/design_analysis/spec_change/` 配下なら `spec-change`
- `docs/design_analysis/new_feature/` 配下なら `new-feature`
- `docs/design_analysis/fix_issues/` 配下なら `bugfix`
- `docs/design_analysis/issue_resolution/` 配下なら `issue-resolution`
- `docs/design_analysis/refactoring/` 配下なら `refactoring`
- 判定不能時は現在進行中の workflow skill（`spec-change-workflow` / `new-feature-workflow` / `bugfix-workflow` / `issue-resolution-workflow` / `refactoring-workflow`）に合わせる
- それでも判定できない時はエラーにして、ユーザへ確認する

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

## Claude セッション管理

1. tmux セッション名は topic 単位で固定する
- 例: `{{PROJECT_NAME_LOWER}}-claude-<topic>`
- 同じ issue の再レビューでは同じセッションを再利用する

2. Claude はインタラクティブモードで起動する
```bash
SESSION_NAME="{{PROJECT_NAME_LOWER}}-claude-${TOPIC}"
python scripts/agent_cli_tmux.py ensure \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --cwd "${MAIN_PROJECT_DIR}" \
  --agent claude
```

3. 既存セッションがある場合は再利用し、Claude プロセスが落ちている時だけ再起動する

4. 必要に応じてユーザへ `tmux attach -t <session_name>` を案内してよいが、通常の監視と承認処理は Codex が担当する

## 監視ポリシー

1. レビュー依頼直後の監視間隔は `15s` を基本とする
2. 2 分経過後は `30s`、5 分経過後は `60s` に伸ばしてよい
3. `thinking` 表示、経過時間更新、token 増減、Read/Bash/Write の追加、review ファイル更新、reviewer commit 作成のいずれかが見える間は「進行中」とみなす
4. 5 分未満の無変化は通常範囲として扱い、停止扱いしない
5. 10 分程度、意味のある進捗が見えない場合は、`/exit` やセッション再作成の前にユーザへ対応方針を確認する
6. ただし Claude プロセス終了、tmux セッション消失、明示エラーなど concrete failure が確認できる場合は、ユーザ確認前でも再起動してよい

## レビュー依頼の基本手順

1. 現在の workflow / phase / issue-dir / topic / 最新コミット hash を確定する
2. review 文書の出力先を決める
3. Claude 用プロンプトファイルを作る
- 一時ファイル例: `/tmp/{{PROJECT_NAME_LOWER}}_claude_review_prompt.txt`
- 長文は `scripts/agent_cli_tmux.py send-prompt` で送る

4. Claude にレビューを依頼する
```bash
PROMPT_FILE="/tmp/{{PROJECT_NAME_LOWER}}_claude_review_prompt.txt"
python scripts/agent_cli_tmux.py send-prompt \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --file "${PROMPT_FILE}"
```

5. `sleep` を挟みながら `tmux capture-pane` で Claude の出力を監視する
```bash
python scripts/agent_cli_tmux.py capture \
  --session "${SESSION_NAME}" \
  --pane 0.0 \
  --sleep-before 15 \
  --lines 120
```
 - 監視中は `15s -> 30s -> 60s` の backoff を使ってよい
 - 5 分程度の長い `thinking` は通常範囲とみなし、安易に中断しない
 - 10 分程度進捗が見えない場合のみ、ユーザへ相談して対応方針を決める

6. Claude が承認ダイアログで停止したら、コマンド内容を確認する
- 危険なコマンドはユーザ確認
- それ以外は Codex が承認

7. Claude が review 文書を更新してコミットしたことを確認し、そのコミット hash を Codex 側で取得する

## 初回レビュー依頼テンプレート

1. Claude へのプロンプトには対象 workflow skill を先頭で渡す
- `spec-change`: `/spec-change-workflow`
- `new-feature`: `/new-feature-workflow`
- `bugfix`: `/bugfix-workflow`
- `issue-resolution`: `/issue-resolution-workflow`
- `refactoring`: `/refactoring-workflow`

```text
/<workflow skill>
あなたはレビュー担当 Agent です。
<issue file>
<issue id>. <issue title>
の Phase <plan|design|impl|docs> レビューをお願いします。
下記コミットから必要なファイルを取得して確認してください。
<commit hash>

レビュー結果は <review document path> に反映し、コミットまで実施してください。
レビュー観点は docs/procedure/review_checkpoints.md と現在の workflow 文書に従ってください。
```

## 指摘対応確認テンプレート

```text
レビュー指摘の対応が完了しました。
下記コミットから差分を取得して再確認してください。
<fix commit hash>

未解決指摘があれば <review document path> に追記してコミットしてください。
問題なければ、承認したことが分かる形で出力してください。
```

## 反復ルール

1. Claude が未承認なら、最新 review commit hash を Codex の作業コンテキストへ取り込み、`ai-review-response-workflow` に従って対応する
2. 対応後は fix commit hash を使って Claude に再確認を依頼する
3. Claude の再確認で未解決指摘が 0 になるまで繰り返す
4. 同じ Phase で 3 回連続で未承認になったら、論点を整理してユーザへエスカレーションする

## 最低限の必須チェック

1. レビュー対象ファイルが保存済みであることを確認する
2. Claude セッション起動後は `sleep` を挟むポーリングで状態監視する
3. 生成された review 文書が空でないことを確認する
4. Claude が review 文書をコミットした hash を取得してから次の処理に進む
5. Follow-up 時は未解決指摘ゼロ、または Claude の明示承認を確認する
6. Phase 5 の review 文書名が workflow ごとの命名規則に一致していることを確認する
7. レビュー指摘反映後は必ず Claude に follow-up を送って確認結果を取得する
8. review 完了確認後は停滞せず、そのまま指摘対応を開始する
9. review ループが 1 Phase 分完了したら、次 Phase へ進む前に短い状態要約を残し、利用可能なら `/compact` でコンテキストを整理する

## 終了処理

1. 同一 issue の後続レビューが残っている間は tmux セッションを維持してよい
2. ワークフロー完了後、またはユーザが終了を指示した時は Claude を閉じて tmux セッションを削除する
```bash
tmux send-keys -t "${SESSION_NAME}:0.0" "/exit" Enter 2>/dev/null || true
sleep 2
tmux kill-session -t "${SESSION_NAME}" 2>/dev/null || true
```

## トラブルシューティング

- `tmux capture-pane` が空になる: Claude が alt-screen で動作している可能性が高い。`TERM=dumb claude` で再起動する
- 5 分以上 `thinking` が続く: 直ちに停止扱いせず、`15s -> 30s -> 60s` の backoff 監視へ切り替える。10 分程度進捗が見えなければユーザへ相談する
- プロンプト投入が崩れる: `tmux send-keys` の直打ちではなく `scripts/agent_cli_tmux.py send-prompt` を使う
- Claude が review 文書をコミットしない: 「レビュー文書の更新とコミットまでお願いします」と追送する
- 承認ダイアログで停止する: まず Codex がコマンド内容を確認し、安全なら承認、危険ならユーザへ確認する
