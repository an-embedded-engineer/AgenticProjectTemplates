# 自律ワークフローオーケストレーター手順

## 概要

Copilot が指揮者となり、Codex CLI（実装 Agent）と Claude Code CLI（レビュー Agent）を
協調させて 5 種類の workflow を全 Phase 自律的に完了させる。

---

## 登場人物と使用コマンド

| 役割 | ツール | モード | コマンド |
|------|--------|--------|---------|
| 指揮者 | Copilot CLI (本スキル) | — | — |
| 実装 Agent | Codex CLI | **インタラクティブ（tmux 監視）** | `codex --no-alt-screen -C <DIR> -s workspace-write -a on-request` |
| レビュー Agent | Claude Code CLI | **インタラクティブ（tmux 監視）** | `TERM=dumb claude` |

---

## コマンド承認方針（監視モード）

### Codex（実装 Agent）

- tmux 専用ペインでインタラクティブ起動する
- `--no-alt-screen` で TUI のインラインモードを有効化する（tmux `capture-pane` でスクロールバック履歴を取得するために必須）
- `-C ${MAIN_PROJECT_DIR}` で作業ディレクトリを明示指定する（`cd <DIR> &&` による前置より確実）
- `-s workspace-write` でワークスペース外への書き込みをサンドボックス制限する
- `-a on-request` でモデルが危険と判断したコマンドのみユーザへ確認する
- **ユーザは tmux ペインを別ウィンドウで監視し、確認ダイアログに随時応答する**

> **注意**: `--full-auto` は `-a on-request -s workspace-write` のエイリアスだが、
> 本ワークフローでは明示的にオプションを指定することを推奨する。

### Claude（レビュー Agent）

- tmux 専用ペインでインタラクティブ起動する
- `TERM=dumb` 環境変数を設定してインラインモードで起動する（tmux `capture-pane` でスクロールバック履歴を取得するために必須。`--no-alt-screen` オプションは Claude Code CLI に存在しないため、`TERM=dumb` で代替する）
- **ユーザは tmux ペインを別ウィンドウで監視し、承認ダイアログに随時応答する**
- Agent CLI の起動、prompt 投入、出力取得、終了は `scripts/agent_cli_tmux.py` を使う

---

## Step 0: 追跡項目判定・ワークフロー選択・作業ディレクトリ確定

**実行者: Copilot**

1. `docs/procedure/workflow_selection.md` を参照し、対象が `docs/issues/` か `docs/todo/` かを判定する
2. 以下の基準でワークフロー種別を判定する

   | 判定基準 | ワークフロー | 起票先 | 使用スキル |
   |----------|-------------|--------|-----------|
   | 既存仕様の変更 | spec-change | `docs/todo/todo.md` | `spec-change-workflow` |
   | 新機能追加 | new-feature | `docs/todo/todo.md` | `new-feature-workflow` |
   | 既存機能のバグ・不具合修正 | bugfix | `docs/issues/` | `bugfix-workflow` |
   | bug 以外の既知課題解決 | issue-resolution | `docs/issues/` | `issue-resolution-workflow` |
   | 外部仕様を変えない構造改善 | refactoring | `docs/todo/todo.md` | `refactoring-workflow` |

3. 曖昧な場合は ID 接頭辞（`TODO-`, `C-`, `F-`, `B-` 等）と本文を精読して判断する
4. **メインプロジェクトディレクトリを特定する**

   ```bash
   # git worktree list の先頭行がメインのワークツリー
   MAIN_PROJECT_DIR=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
   echo "Main project dir: ${MAIN_PROJECT_DIR}"
   ```

   > **重要**: Codex は必ずこのディレクトリで作業させる。
   > Copilot 自身が worktree 上で動作している場合でも、Codex の作業先はメインプロジェクトディレクトリとする。

5. 判断結果とメインプロジェクトディレクトリをユーザへ報告する

---

## Step 1: tmux セッション構築と Agent 起動

**実行者: Copilot**

```bash
# 1. Codex をペイン 0（左）で起動
python scripts/agent_cli_tmux.py ensure \
  --session workflow-orchestrator \
  --pane 0.0 \
  --cwd "${MAIN_PROJECT_DIR}" \
  --agent codex

# 2. Claude をペイン 1（右）で起動
python scripts/agent_cli_tmux.py ensure \
  --session workflow-orchestrator \
  --pane 0.1 \
  --cwd "${MAIN_PROJECT_DIR}" \
  --agent claude
```

> **ユーザへの案内**: 別ターミナルウィンドウで `tmux attach -t workflow-orchestrator` を
> 実行し、両 Agent ペインを監視してください。承認ダイアログが出たら随時応答してください。

**Codex への初期プロンプト送信:**

```bash
TRACKING_FILE="<docs/todo/todo.md | docs/issues/XXX/issues.md>"   # Copilot が Step 0 で特定
ITEM_ID="<TODO-2026-XXX | C-2026-XXX>"
ITEM_TITLE="<項目タイトル>"
SKILL="<spec-change-workflow|new-feature-workflow|bugfix-workflow|issue-resolution-workflow|refactoring-workflow>"

PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
cat > "${PROMPT_FILE}" <<EOF
\$${SKILL}
${TRACKING_FILE}
${ITEM_ID}. ${ITEM_TITLE}
の対応を開始してください。
EOF
python scripts/agent_cli_tmux.py send-prompt \
  --session workflow-orchestrator \
  --pane 0.0 \
  --file "${PROMPT_FILE}"
```

> **PHASE_COMPLETE 誤検知について**: プロンプトに `[PHASE_COMPLETE:]` 等のシグナル文字列を含めると、Codex がその文字列を即座に出力して Copilot が誤検知する原因になる。また複数 Phase の実行を一度に指示すると連続実行の原因になる。これらは選択した workflow skill が規定しているため、Copilot からのプロンプトには含めないこと。

---

## Step 2: Phase 完了検知

**実行者: Copilot**

Copilot は `tmux capture-pane` で Codex の出力テキストを定期取得し、内容を読んで待機状態か否かを判断する。

### 検知の優先順位

1. **構造化シグナル（一次判定）**: Codex へ各 Phase 完了時に出力するよう指示する。確実に出力される場合はこちらを使う。

   ```
   [PHASE_COMPLETE: N]         … Phase N 完了、次 Phase 進行の承認待ち
   [NEED_USER_VERIFICATION]    … Phase 5 ユーザ動作確認の依頼待ち
   [ALL_PHASES_COMPLETE]       … 全 Phase 完了
   ```

2. **自然言語パターン（フォールバック判定）**: Codex が構造化シグナルを出力しない場合、Copilot が出力テキストを読んで以下のパターンで待機状態を判断する。

   | Codex の出力例 | Copilot の判断 |
   |---------------|---------------|
   | 「～完了です。Phase N に進めてよければ着手します」 | Phase N-1 完了、Phase N 開始の承認待ち |
   | 「承認をいただければ次の Phase に進みます」 | 現 Phase 完了、次 Phase 進行の承認待ち |
   | 「動作確認をお願いします」「アプリを起動して確認してください」 | Phase 5 ユーザ動作確認の依頼待ち |
   | 「マージしてよいですか」「master へのマージ承認をお願いします」 | Phase 6 最終マージの承認待ち |
   | 「レビューを依頼してください」「レビュー担当 Agent を起動してください」 | レビュー依頼準備完了、Claude への依頼タイミング |

```bash
# Copilot による定期読み取りのイメージ（実際は Copilot の判断ロジック）
while true; do
  OUTPUT=$(python scripts/agent_cli_tmux.py capture --session workflow-orchestrator --pane 0.0 --lines 100 2>/dev/null)

  # 一次判定: 構造化シグナル
  if echo "$OUTPUT" | grep -q '\[PHASE_COMPLETE:'; then
    PHASE=$(echo "$OUTPUT" | grep -oE '\[PHASE_COMPLETE: [0-9]+' | grep -oE '[0-9]+$' | tail -1)
    break
  fi
  if echo "$OUTPUT" | grep -q '\[NEED_USER_VERIFICATION\]'; then
    STATE="user_verification"; break
  fi

  # フォールバック判定: Copilot が自然言語を解釈して判断
  # （tmux capture-pane の出力全体を Copilot が読んで判断する）

  sleep 15
done

# 最新コミット hash の取得
COMMIT_HASH=$(git --no-pager log --oneline -1 --format="%H")
```

> **重要**: フォールバック判定は bash スクリプトではなく **Copilot 自身が出力テキストを読んで自然言語として解釈**する。
> 「着手します」「承認をお願い」のような待機意図が読み取れれば、それを Phase 完了シグナルと同等に扱う。

---

## Step 3: Phase ループ（Phase 2 以降）

**実行者: Copilot** が以下のループを全 Phase 完了まで繰り返す。

```
for each Phase N in [2, 3, 4, ...]:
  1. Codex の Phase N 完了・待機を検知 → 最新 commit hash を取得
  2. Claude に Phase N レビューを依頼（短文 + commit hash） → レビューコミット hash を取得
  3. Codex にレビュー結果を通知（短文 + review commit hash） → 対応完了を待機
  4. 対応後の fix commit hash を取得
  5. Claude に対応確認を依頼（短文 + fix commit hash）
  6. Claude が承認 → **ask_user でユーザに Phase N+1 への進行承認を求める**
  7. ユーザが承認 → Codex に "OKです。Phase N+1 へ進めてください。" と指示
  8. Claude が未承認 → step 3 に戻る（最大 3 回。超えた場合はエスカレーション）
  9. [NEED_USER_VERIFICATION] を検知したら Step 4 へ（動作確認ゲート）
```

> **承認方針**: Phase 完了後の次 Phase への移行判断はユーザ承認必須（`ask_user`）。

### 3-1. Codex への指示

**Phase 承認・開始指示（Claude が承認後）:**
```bash
NEXT_PHASE=<N>
PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
echo "OKです。Phase ${NEXT_PHASE} へ進めてください。" > "${PROMPT_FILE}"
python scripts/agent_cli_tmux.py send-prompt --session workflow-orchestrator --pane 0.0 --file "${PROMPT_FILE}"
```

**レビュー結果の通知（Claude のレビューコミット後）:**
```bash
# Claude がレビュー文書をコミットした後の最新 hash を取得
REVIEW_COMMIT_HASH=$(git -C "${MAIN_PROJECT_DIR}" --no-pager log --oneline -1 --format="%H")

PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
cat > "${PROMPT_FILE}" <<EOF
レビュー完了しました。
下記コミットから指摘内容を確認して対応をお願いします。
${REVIEW_COMMIT_HASH}
EOF
python scripts/agent_cli_tmux.py send-prompt --session workflow-orchestrator --pane 0.0 --file "${PROMPT_FILE}"
```

### 3-2. Claude への Phase レビュー依頼

**共通セットアップ:**
```bash
mkdir -p "${MAIN_PROJECT_DIR}/tmp/orchestrator"
REVIEW_PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/claude_review_prompt.txt"
```

**初回レビュー（Phase N の成果物を確認）:**
```bash
COMMIT_HASH=$(git -C "${MAIN_PROJECT_DIR}" --no-pager log --oneline -1 --format="%H")

cat > "${REVIEW_PROMPT_FILE}" << REVIEW_EOF
/${SKILL}
あなたはレビュー担当 Agent です。
${TRACKING_FILE}
${ITEM_ID}. ${ITEM_TITLE}
のレビューをお願いします。
下記コミットからドキュメントを取得してレビューをお願いします。
${COMMIT_HASH}
REVIEW_EOF

python scripts/agent_cli_tmux.py send-prompt \
  --session workflow-orchestrator \
  --pane 0.1 \
  --file "${REVIEW_PROMPT_FILE}"
```

> **注意**: Claude がレビュー文書をコミットしない場合は「コミットまでお願いします」と追加で依頼する（同じ `REVIEW_PROMPT_FILE` に内容を変えて再送する）。

**対応確認（Codex が指摘対応後）:**
```bash
# Codex の対応コミット後の最新 hash を取得
FIX_COMMIT_HASH=$(git -C "${MAIN_PROJECT_DIR}" --no-pager log --oneline -1 --format="%H")

cat > "${REVIEW_PROMPT_FILE}" << CHECK_EOF
レビュー指摘対応完了しました。
下記コミットから差分を取得して確認をお願いします。
${FIX_COMMIT_HASH}
CHECK_EOF

python scripts/agent_cli_tmux.py send-prompt \
  --session workflow-orchestrator \
  --pane 0.1 \
  --file "${REVIEW_PROMPT_FILE}"
```

### 3-3. Copilot によるレビュー結果の評価と Codex への通知

**原則: Claude が「指摘なし」または「全件対応済み」と回答するまで次の Phase に進まない。**

Copilot は Claude のペイン出力を取得して読み、承認を判断する：

```bash
REVIEW_TEXT=$(python scripts/agent_cli_tmux.py capture --session workflow-orchestrator --pane 0.1 --lines 100 2>/dev/null)
```

**Claude が承認（指摘なし・全件対応済み）の場合:**

まず `ask_user` でユーザに Phase 移行の承認を求める：

```
Phase ${CURRENT_PHASE} のレビューが完了しました（指摘: 全件対応済み）。
Phase ${NEXT_PHASE} へ進行してよろしいですか？
```

選択肢: `["Phase ${NEXT_PHASE} へ進行する", "保留する（手動で確認後に再開）"]`

ユーザが承認した場合のみ Codex に次 Phase を指示する：
```bash
NEXT_PHASE=<N+1>
PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
echo "OKです。Phase ${NEXT_PHASE} へ進めてください。" > "${PROMPT_FILE}"
python scripts/agent_cli_tmux.py send-prompt --session workflow-orchestrator --pane 0.0 --file "${PROMPT_FILE}"
```

ユーザが保留した場合は、自動進行せずそのまま待機する。
再開時はユーザが Copilot に「Phase ${NEXT_PHASE} へ進める」と明示してから、上記コマンドを送る。

**Claude が未承認（未解決指摘あり）の場合:**
```bash
# Step 3-1 の「レビュー結果の通知」でレビューコミット hash を Codex に渡す
# 最大 3 回ループ。超えた場合はエスカレーション
LOOP_COUNT=$((LOOP_COUNT + 1))
if [ "$LOOP_COUNT" -ge 3 ]; then
  echo "ESCALATION: 3 回のループでも指摘が解消されませんでした"
fi
```

> **重要**: Copilot が `REVIEW_TEXT` を自然言語として読んで承認を判断する。指摘なしと読み取れれば次 Phase へ進める。ループ回数が 3 回を超えた場合はユーザへエスカレーションし、方針を確認する。
> 保留が選択された場合は、現在の tmux セッションを維持したまま待機し、次 Phase を自動送信してはならない。

---

## Step 4: Phase 5 ユーザ動作確認ゲート（必須）

**実行者: Copilot**

`[NEED_USER_VERIFICATION]` を検知したタイミングで以下を実行する。

### 4-1. Codex から動作確認観点を取得

```bash
# Codex の最新出力から動作確認観点セクションを抽出
VERIFICATION_GUIDE=$(python scripts/agent_cli_tmux.py capture --session workflow-orchestrator --pane 0.0 --lines 200 \
  | sed -n '/動作確認観点/,/\[NEED_USER_VERIFICATION\]/p')
```

### 4-2. ユーザへ通知（ask_user ツール使用）

Copilot は以下の内容で `ask_user` を呼び出す：

```
【Phase 5: アプリ動作確認のお願い】

Codex が実装を完了しました。アプリを起動して以下の観点で動作確認してください。

<VERIFICATION_GUIDE の内容>

確認完了後、結果を選択してください。
```

選択肢: `["OK（正常動作を確認）", "NG（問題あり）"]`

### 4-3. ユーザ応答に基づく処理

**OK の場合:**
```bash
PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
echo "動作確認し、問題なさそうです。文書反映へ進めてください。" > "${PROMPT_FILE}"
python scripts/agent_cli_tmux.py send-prompt --session workflow-orchestrator --pane 0.0 --file "${PROMPT_FILE}"
```

**NG の場合:**
```bash
# NG 理由の詳細を ask_user で追加取得（freeform）
# その後 Codex に Phase 4 差し戻しを指示
PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
cat > "${PROMPT_FILE}" <<EOF
動作確認でNGでした。原因: <NG 詳細>
修正をお願いします。
EOF
python scripts/agent_cli_tmux.py send-prompt --session workflow-orchestrator --pane 0.0 --file "${PROMPT_FILE}"
# Step 3 のループに戻る
```

---

## Step 5: master マージと最終承認

**実行者: Copilot → ユーザ（最終承認） → Codex**

### 5-1. ユーザへ最終マージ承認を要求

全 Phase レビュー完了後、Copilot は `ask_user` で確認する：

```
全 Phase が完了しました。master へのマージを承認しますか？

- ブランチ: <branch名>
- 実装レビュー: 完了（open 指摘: N 件）
- ドキュメントレビュー: 完了（open 指摘: M 件）
- ユーザ動作確認: OK
```

選択肢: `["マージを承認する", "マージを保留する（手動で後日対応）"]`

### 5-2. 承認時 – Codex に完了処理を指示

```bash
PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/codex_prompt.txt"
cat > "${PROMPT_FILE}" <<EOF
ユーザがマージを承認しました。以下を実行してください:
 1. meta.md の related_commits を確定させる
 2. master へ --no-ff でマージする
 3. meta.md の status を merged に更新して最終コミットしてください
EOF
python scripts/agent_cli_tmux.py send-prompt --session workflow-orchestrator --pane 0.0 --file "${PROMPT_FILE}"
```

### 5-3. Copilot による最終確認

```bash
git --no-pager log --oneline master -5
git --no-pager branch -a | grep -v "HEAD"
```

---

## Step 6: ユーザへの結果サマリー報告

Copilot は以下の内容をユーザに報告する：

```
## ワークフロー完了サマリー

- 項目: <item ID> - <タイトル>
- ワークフロー種別: <spec-change / new-feature / bugfix / issue-resolution / refactoring>
- ブランチ: <branch名>（master にマージ済み）
- 完了 Phase: Phase 0 〜 Phase 6
- 最終コミット: <hash>
- レビュー指摘件数（合計）: <N> 件（うち critical: <M> 件）
- ユーザ動作確認: OK（<確認日時>）
- 残存 follow-up: <なし / あり（詳細）>
- 設計文書パス: docs/design_analysis/<category>/<yyyymmdd>_<topic>/
```

---

## Step 7: セッションクリーンアップ

**実行者: Copilot**

ワークフロー完了後（またはユーザが中断した場合）、tmux セッションを明示的に終了する。

```bash
# Codex を終了（q キーで終了; すでに終了している場合は無視）
python scripts/agent_cli_tmux.py stop --session workflow-orchestrator --pane 0.0 --agent codex
# Claude を終了
python scripts/agent_cli_tmux.py stop --session workflow-orchestrator --pane 0.1 --agent claude --kill-session
sleep 3

# セッションを削除
if tmux has-session -t workflow-orchestrator 2>/dev/null; then
  tmux kill-session -t workflow-orchestrator
  echo "Session workflow-orchestrator killed"
fi

# 一時ファイルのクリーンアップ
rm -f "${MAIN_PROJECT_DIR}/tmp/orchestrator/claude_review_prompt.txt"
echo "Cleanup complete"
```

> **注意**: 中断時も必ずこの手順を実行し、セッションを残留させないこと。

---

## エスカレーション条件

以下の場合は処理を中断し、`ask_user` ツールでユーザに判断を求める：

| 条件 | エスカレーション内容 |
|------|---------------------|
| open 指摘の修正ループが **3 回**超え | 指摘内容・severity・試行履歴を提示し、方針をユーザに委任 |
| Phase 5 ユーザ動作確認が **NG** | NG 詳細を共有し、Phase 4 差し戻しを報告 |
| 項目の要件が曖昧で種別判定不能 | 5 workflow のどれで扱うかをユーザに確認 |
| Codex ペインが無応答（10 分超え） | セッション再起動の要否をユーザに確認 |
| master マージでコンフリクト発生 | コンフリクト箇所を提示し、解消方法をユーザに確認 |
| Pyright エラーが 2 Phase 連続で 0 件にならない | 原因と影響範囲を提示し、方針をユーザに確認 |

---

## セッション管理まとめ

| Agent | セッション継続方法 | セッション ID 保存先 |
|-------|------------------|---------------------|
| Codex | tmux ペイン継続（インタラクティブ） | `workflow-orchestrator:0.0` ペインが存在する限り維持 |
| Claude | tmux ペイン継続（インタラクティブ） | `workflow-orchestrator:0.1` ペインが存在する限り維持 |

---

## ユーザ操作まとめ

| タイミング | ユーザが行うこと |
|------------|----------------|
| Step 1 直後 | 別ターミナルで `tmux attach -t workflow-orchestrator` を開いて両 Agent ペインを監視 |
| Codex の承認ダイアログ | tmux ペインで承認・却下を応答 |
| Phase 5 動作確認ゲート | Copilot からの通知に従いアプリを起動して確認し、OK / NG を回答 |
| Phase 6 最終マージ | Copilot からの承認確認に OK / 保留を回答 |

---

## トラブルシューティング

### Codex が tmux で起動できない / 出力が取得できない

| 症状 | 原因 | 対処 |
|------|------|------|
| `tmux capture-pane` で出力が空 | Codex がalt-screen モードで動作している | `--no-alt-screen` を付けて起動する |
| 日本語テキストが文字化け | tmux のエンコーディング問題 | プロンプトを英語テンプレートファイルにして `< file` で渡す |
| `codex` コマンドが見つからない | PATH にインストール先が含まれていない | `which codex` で確認。`npm install -g @openai/codex` で再インストール |
| Codex が worktree を作成してしまう | プロンプトの厳守事項が不足 | `-C <DIR>` で作業ディレクトリを明示指定し、プロンプトに worktree 禁止を明記 |

### Claude Code が起動できない / レビューが実行されない

| 症状 | 原因 | 対処 |
|------|------|------|
| `tmux capture-pane` で出力が空 | Claude が alt-screen モードで動作している | `TERM=dumb claude` で起動する（`--no-alt-screen` オプションは Claude Code CLI に存在しない） |
| プロンプトが正しく入力されない | tmux paste-buffer の改行処理問題 | `scripts/agent_cli_tmux.py send-prompt` を使い、必要なら `--submit-delay` を指定する |
| セッション継続が途切れる | ペインが閉じられた | `workflow-orchestrator:0.1` ペインの生存を確認し、必要に応じて Claude を再起動する |

### Codex の承認設定に関するトラブル

| 設定 | 効果 | 変更方法 |
|------|------|---------|
| `~/.codex/config.toml` の `trust_level = "trusted"` | プロジェクトを信頼済みとして扱い、承認ダイアログを減少させる | 後述の「Codex の自動許可設定の戻し方」を参照 |
| `-a on-request` | モデルが危険と判断したコマンドのみ承認を求める | `-a untrusted` にすると安全なコマンド以外すべて承認を求める |
| `-a never` | 承認を一切求めない（非インタラクティブ向け） | インタラクティブでは使用しない |

---

## Codex の自動許可設定の戻し方

### 現在の設定確認

```bash
cat ~/.codex/config.toml
```

### `trust_level` の削除（推奨）

`~/.codex/config.toml` のプロジェクト固有セクションを削除または変更する：

**変更前（自動許可が有効）:**
```toml
[projects."/path/to/your-project"]
trust_level = "trusted"
```

**変更後（削除する場合）:**
```toml
# [projects."/path/to/your-project"] セクションを削除
```

**変更後（明示的に制限する場合）:**
```toml
# trust_level 行を削除するだけで default に戻る
[projects."/path/to/your-project"]
# trust_level を指定しない = default 動作
```

### 承認ポリシーの比較

| `-a` オプション | 動作 | ユースケース |
|--------|------|-------------|
| `untrusted` | 安全なコマンド（ls, cat, sed 等）のみ自動実行。それ以外はすべてユーザに確認 | 最も安全。初回使用時や信頼性の低い環境向け |
| `on-request` | モデルが危険と判断したコマンドのみ確認（**本ワークフローのデフォルト**） | 通常運用向け |
| `never` | 承認を一切求めない | `codex exec`（非インタラクティブ）専用 |

### 即座に反映する方法

```bash
# config.toml を直接編集
vi ~/.codex/config.toml
# → trust_level = "trusted" の行を削除またはコメントアウト

# または CLI オプションで一時的に上書き
codex --no-alt-screen -C <DIR> -s workspace-write -a untrusted
```
