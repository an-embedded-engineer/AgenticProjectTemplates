# 自律ワークフローオーケストレーター手順（Copilot CLI 統一版）

## 概要

Copilot（VS Code Copilot Chat または Copilot CLI）が指揮者となり、
**Copilot CLI の別セッション**を実装 Agent・レビュー Agent として起動し、
モデル選択で役割を分担させて 5 種類の workflow を全 Phase 自律的に完了させる。

> **従来版との違い**: Codex CLI + Claude Code CLI の 2 ツール構成を、
> Copilot CLI 単一に統一する。GitHub Copilot のサブスクリプションのみで完結する。

---

## 実現可能性の評価

### 結論: **実現可能**

Copilot CLI（`gh copilot` / `copilot`）v1.0.3+ は、従来の Codex CLI・Claude Code CLI の
必要機能をすべてカバーしている。

### 機能対応表

| 必要機能 | Codex CLI | Claude Code CLI | Copilot CLI | 対応状況 |
|----------|-----------|-----------------|-------------|---------|
| インタラクティブモード | デフォルト | N/A | デフォルト / `-i` | ✅ 完全対応 |
| 非インタラクティブモード | N/A | `-p` | `-p` / `--prompt` | ✅ 完全対応 |
| モデル選択 | 暗黙（Codex モデル） | 暗黙（Claude） | `--model <model>` | ✅ 明示選択可能 |
| alt-screen 無効化 | `--no-alt-screen` | N/A | `--no-alt-screen` | ✅ 完全対応 |
| 作業ディレクトリ指定 | `-C <DIR>` | `cd <DIR> &&` | tmux ペインの CWD | ⚠️ `-C` なし（後述） |
| ツール制限（サンドボックス） | `-s workspace-write` | `--allowed-tools` | `--available-tools` / `--allow-tool` / `--deny-tool` | ✅ より細粒度 |
| 承認ポリシー | `-a on-request` | 自動（ツール制限） | デフォルト（per-tool）/ `--allow-all-tools` | ✅ 対応 |
| セッション継続 | tmux ペイン維持 | `--resume <id>` / `-c` | `--resume [id]` / `--continue` | ✅ 完全対応 |
| JSON 出力 | N/A | `--output-format json` | `--output-format json` | ✅ 完全対応 |
| カスタム指示（AGENTS.md） | 対応 | CLAUDE.md | AGENTS.md（デフォルト読込） | ✅ 対応 |
| オートパイロット | N/A | N/A | `--autopilot` | ✅ 追加機能 |
| ask_user 無効化 | N/A | N/A | `--no-ask-user` | ✅ 追加機能 |

### 複数セッション同時実行

- Copilot CLI は独立プロセスとして起動するため、**複数ターミナルでの同時実行が可能**
- 各セッションは独立した認証トークンを使用（GitHub 認証は共有）
- 手動検証済み（ユーザ確認）

### 利用可能なモデル（2026-03 時点）

```
claude-sonnet-4.6, claude-sonnet-4.5, claude-haiku-4.5,
claude-opus-4.6, claude-opus-4.6-fast, claude-opus-4.5,
claude-sonnet-4, gemini-3-pro-preview,
gpt-5.4, gpt-5.3-codex, gpt-5.2-codex, gpt-5.2,
gpt-5.1-codex-max, gpt-5.1-codex, gpt-5.1, gpt-5.1-codex-mini,
gpt-5-mini, gpt-4.1
```

---

## 主な差異と対処方針

### 1. 作業ディレクトリ指定（`-C` オプション非対応）

**現行**: Codex CLI は `-C ${MAIN_PROJECT_DIR}` で明示指定。

**Copilot CLI 版**: `-C` オプションがないため、tmux ペインの CWD で制御する。

```bash
# tmux ペイン作成時に -c で CWD を指定（従来と同じ）
tmux new-session -d -s workflow-orchestrator -x 220 -y 60 -c "${MAIN_PROJECT_DIR}"
```

加えて `--add-dir` でアクセス許可ディレクトリを明示できる。

### 2. ツール制限（サンドボックス）

**現行 Codex**: `-s workspace-write`（ワークスペース外書込み禁止）
**現行 Claude**: `--allowed-tools "Bash(git:*),Read,Write,Edit,MultiEdit"`

**Copilot CLI 版**:

- **実装 Agent**: デフォルト（per-tool 承認）で十分。`--no-ask-user` でツール承認を自動化する。
- **レビュー Agent**: インタラクティブモードで起動するため、ツール制限は不要。
  `--no-ask-user` でツール承認を自動化する。

### 3. スキル呼び出し記法

**現行 Codex**: `$<workflow-skill>` で呼び出し。
**Copilot CLI**: AGENTS.md / skills を自動読込するため、プロンプト内で自然言語で指示する。

```
<workflow-skill> スキルに従って、
<tracking-file>
<item-id>. <タイトル>
の対応を開始してください。
```

### 4. 承認ポリシーの対応

| 現行 | Copilot CLI |
|------|-------------|
| `-a on-request`（Codex） | デフォルト動作（初回承認 → 以降自動） |
| `-a never` | `--no-ask-user`（両 Agent 共通） |
| ツール制限による自動実行（Claude） | `--no-ask-user` + インタラクティブモード |

---

## 登場人物と使用コマンド

| 役割 | ツール | モード | コマンド |
|------|--------|--------|---------|
| 指揮者 | Copilot Chat / Copilot CLI (本スキル) | — | — |
| 実装 Agent | Copilot CLI | **インタラクティブ（tmux 監視）** | `gh copilot -- --no-alt-screen --model <IMPL_MODEL> --no-ask-user` |
| レビュー Agent | Copilot CLI | **インタラクティブ（tmux 監視）** | `gh copilot -- --no-alt-screen --model <REVIEW_MODEL> --no-ask-user` |

### 推奨モデル構成

| 役割 | 推奨モデル | 理由 |
|------|-----------|------|
| 実装 Agent | `gpt-5.3-codex` または `gpt-5.2-codex` | コード生成に最適化された Codex 系モデル |
| レビュー Agent | `claude-opus-4.6` | 長文理解・レビュー品質に優れた Opus |

> **モデルは状況に応じて変更可能**。例えば実装 Agent に `claude-opus-4.6` を使うことも、
> レビュー Agent に `gpt-5.4` を使うことも自由。

---

## Step 0: 追跡項目判定・ワークフロー選択・作業ディレクトリ確定

（現行版と同一。変更なし。）

**実行者: Copilot**

1. `docs/procedure/workflow_selection.md` を参照し、対象が `docs/issues/` か `docs/todo/` かを判定する
2. `spec-change` / `new-feature` / `bugfix` / `issue-resolution` / `refactoring` を判定する
3. メインプロジェクトディレクトリを特定する

   ```bash
   MAIN_PROJECT_DIR=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
   echo "Main project dir: ${MAIN_PROJECT_DIR}"
   ```

4. モデル構成を確定する

   ```bash
   # デフォルト推奨。ユーザ指定があればそちらを優先
   IMPL_MODEL="gpt-5.3-codex"
   REVIEW_MODEL="claude-opus-4.6"
   ```

5. 判断結果をユーザへ報告する

---

## Step 1: tmux セッション構築と Agent 起動

**実行者: Copilot**

```bash
# 0. 既存セッションのクリーンアップ
if tmux has-session -t workflow-orchestrator 2>/dev/null; then
  tmux kill-session -t workflow-orchestrator
  echo "Previous session killed"
fi

# 1. tmux セッション作成（メインプロジェクトディレクトリで起動）
tmux new-session -d -s workflow-orchestrator -x 220 -y 60 -c "${MAIN_PROJECT_DIR}"

# 2. ペイン分割（左: 実装 Agent / 右: レビュー Agent 用）
tmux split-window -h -t workflow-orchestrator -c "${MAIN_PROJECT_DIR}"

# 3. 実装 Agent をペイン 0（左）で起動
tmux send-keys -t workflow-orchestrator:0.0 \
  "gh copilot -- --no-alt-screen --model ${IMPL_MODEL} --no-ask-user" \
  Enter

# 4. レビュー Agent をペイン 1（右）で起動
tmux send-keys -t workflow-orchestrator:0.1 \
  "gh copilot -- --no-alt-screen --model ${REVIEW_MODEL} --no-ask-user" \
  Enter
```

> **ユーザへの案内**: 別ターミナルウィンドウで `tmux attach -t workflow-orchestrator` を
> 実行し、両 Agent ペインを監視してください。承認ダイアログが出たら随時応答してください。

**実装 Agent への初期プロンプト送信:**

```bash
TRACKING_FILE="<docs/todo/todo.md | docs/issues/XXX/issues.md>"
ITEM_ID="<TODO-2026-XXX | C-2026-XXX>"
ITEM_TITLE="<項目タイトル>"
SKILL="<spec-change-workflow|new-feature-workflow|bugfix-workflow|issue-resolution-workflow|refactoring-workflow>"

tmux send-keys -t workflow-orchestrator:0.0 \
"${SKILL} スキルに従って、
${TRACKING_FILE}
${ITEM_ID}. ${ITEM_TITLE}
の対応を開始してください。" \
Enter
```

---

## Step 2: Phase 完了検知

（現行版と同一ロジック。実装 Agent の出力を tmux capture-pane で取得して判断する。）

```bash
OUTPUT=$(tmux capture-pane -t workflow-orchestrator:0.0 -p -S -100 2>/dev/null)
```

検知の優先順位:
1. **構造化シグナル**: `[PHASE_COMPLETE: N]`, `[NEED_USER_VERIFICATION]`, `[ALL_PHASES_COMPLETE]`
2. **自然言語パターン**: Copilot が出力テキストを読んで待機意図を判断

---

## Step 3: Phase ループ（Phase 2 以降）

### 3-1. 実装 Agent への指示

Phase 完了後の次 Phase への移行判断は `ask_user` でユーザ承認必須。

**Phase 承認・開始指示（ユーザ承認後）:**
```bash
# ask_user でユーザが承認した後に実行する
tmux send-keys -t workflow-orchestrator:0.0 \
"OKです。Phase ${NEXT_PHASE} へ進めてください。" \
Enter
```

```bash
# レビュー結果の通知
REVIEW_COMMIT_HASH=$(git -C "${MAIN_PROJECT_DIR}" --no-pager log --oneline -1 --format="%H")

tmux send-keys -t workflow-orchestrator:0.0 \
"レビュー完了しました。
下記コミットから指摘内容を確認して対応をお願いします。
${REVIEW_COMMIT_HASH}" \
Enter
```

### 3-2. レビュー Agent への Phase レビュー依頼

**共通セットアップ:**
```bash
mkdir -p "${MAIN_PROJECT_DIR}/tmp/orchestrator"
REVIEW_PROMPT_FILE="${MAIN_PROJECT_DIR}/tmp/orchestrator/copilot_review_prompt.txt"
```

**初回レビュー:**
```bash
COMMIT_HASH=$(git -C "${MAIN_PROJECT_DIR}" --no-pager log --oneline -1 --format="%H")

cat > "${REVIEW_PROMPT_FILE}" << REVIEW_EOF
${SKILL} スキルのレビュー手順に従ってください。
あなたはレビュー担当 Agent です。
${TRACKING_FILE}
${ITEM_ID}. ${ITEM_TITLE}
のレビューをお願いします。
下記コミットからドキュメントを取得してレビューをお願いします。
${COMMIT_HASH}
REVIEW_EOF

tmux load-buffer "${REVIEW_PROMPT_FILE}"
tmux paste-buffer -t workflow-orchestrator:0.1
tmux send-keys -t workflow-orchestrator:0.1 "" Enter
```

**対応確認（実装 Agent が指摘対応後）:**
```bash
FIX_COMMIT_HASH=$(git -C "${MAIN_PROJECT_DIR}" --no-pager log --oneline -1 --format="%H")

cat > "${REVIEW_PROMPT_FILE}" << CHECK_EOF
レビュー指摘対応完了しました。
下記コミットから差分を取得して確認をお願いします。
${FIX_COMMIT_HASH}
CHECK_EOF

tmux load-buffer "${REVIEW_PROMPT_FILE}"
tmux paste-buffer -t workflow-orchestrator:0.1
tmux send-keys -t workflow-orchestrator:0.1 "" Enter
```

### 3-3. レビュー結果の評価と Phase 移行承認

レビュー Agent のペイン出力を取得して Copilot が解釈し、承認判断する。

```bash
REVIEW_TEXT=$(tmux capture-pane -t workflow-orchestrator:0.1 -p -S -100 2>/dev/null)
```

**レビュー Agent が承認（指摘なし・全件対応済み）の場合:**

`ask_user` でユーザに Phase 移行の承認を求める：

```
Phase ${CURRENT_PHASE} のレビューが完了しました（指摘: 全件対応済み）。
Phase ${NEXT_PHASE} へ進行してよろしいですか？
```

選択肢: `["Phase ${NEXT_PHASE} へ進行する", "保留する（手動で確認後に再開）"]`

ユーザが承認した場合のみ、Step 3-1 の「Phase 承認・開始指示」で実装 Agent に次 Phase を指示する。

ユーザが保留した場合は、自動進行せずそのまま待機する。
再開時はユーザが Copilot に「Phase ${NEXT_PHASE} へ進める」と明示してから、Step 3-1 の指示を送る。

**レビュー Agent が未承認（未解決指摘あり）の場合:**

Step 3-1 の「レビュー結果の通知」でレビューコミット hash を実装 Agent に渡す。
最大 3 回ループ。超えた場合はユーザへエスカレーション。

---

## Step 4〜7

Step 4（ユーザ動作確認ゲート）、Step 5（master マージ）、Step 6（結果サマリー）、
Step 7（セッションクリーンアップ）は現行版と同一手順。

唯一の違い:
- クリーンアップ時の一時ファイルパスは `${MAIN_PROJECT_DIR}/tmp/orchestrator/copilot_review_prompt.txt`

```bash
# Step 7: セッションクリーンアップ
tmux send-keys -t workflow-orchestrator:0.0 "/exit" Enter 2>/dev/null
tmux send-keys -t workflow-orchestrator:0.1 "/exit" Enter 2>/dev/null
sleep 3

if tmux has-session -t workflow-orchestrator 2>/dev/null; then
  tmux kill-session -t workflow-orchestrator
  echo "Session workflow-orchestrator killed"
fi

rm -f "${MAIN_PROJECT_DIR}/tmp/orchestrator/copilot_review_prompt.txt"
echo "Cleanup complete"
```

> **注意**: Copilot CLI の終了は `q` ではなく `/exit` コマンド。

---

## 現行版からの変更点サマリー

| 項目 | 現行版 | Copilot CLI 統一版 |
|------|--------|-------------------|
| 実装 Agent | Codex CLI | Copilot CLI (`--model gpt-5.3-codex`) |
| レビュー Agent | Claude Code CLI | Copilot CLI (`--model claude-opus-4.6`) |
| 必要サブスクリプション | GitHub Copilot + OpenAI (Codex) + Anthropic (Claude) | **GitHub Copilot のみ** |
| alt-screen 無効化 | `--no-alt-screen` | `--no-alt-screen`（同一） |
| 作業ディレクトリ指定 | `-C <DIR>` | tmux `-c <DIR>`（ペイン CWD） |
| ツール制限（実装） | `-s workspace-write` | デフォルト per-tool 承認 |
| ツール制限（レビュー） | `--allowed-tools "Bash(git:*),..."` | 不要（インタラクティブモード） |
| 全ツール自動承認 | `-a never` | `--no-ask-user`（両 Agent 共通） |
| 承認方式（実装） | `-a on-request` | デフォルト（初回承認 → 以降自動） |
| スキル呼び出し | `$skill-name` | 自然言語で指示 |
| セッション継続 | tmux ペイン維持 / `--resume <id>` | tmux ペイン維持（両 Agent 共通） |
| JSON 出力 | N/A / `--output-format json` | 不要（インタラクティブモード） |
| CLI 終了コマンド | `q` | `/exit` |
| セッション ID ファイル | `${MAIN_PROJECT_DIR}/tmp/orchestrator/claude_orchestrator_session.txt` | 不要（インタラクティブモードで継続） |
| ask_user 無効化 | N/A | `--no-ask-user`（実装・レビュー Agent 両方） |

---

## 検証が必要な項目

以下は手順策定段階では確認できておらず、実運用前に検証が必要。

### 1. 実装 Agent の承認 UX

Copilot CLI のデフォルト承認フロー（per-tool 確認）が、
Codex の `-a on-request` と同等の体験を提供するか。
`--allow-tool` で事前許可するツールの最適な組み合わせを検証する。

### 2. レート制限

同一 GitHub アカウントから Copilot CLI を 2 セッション同時実行した場合の
レート制限・スロットリングの有無。

---

## 想定される課題と対処

### 課題 1: `-C` オプションがない

**影響**: 実装 Agent が意図しないディレクトリで作業する可能性。

**対処**:
- tmux ペイン作成時に `-c "${MAIN_PROJECT_DIR}"` で CWD を設定（十分）
- プロンプトに「現在のディレクトリ `${MAIN_PROJECT_DIR}` で作業してください」を明記
- `--add-dir "${MAIN_PROJECT_DIR}"` でアクセス許可を明示

### 課題 2: スキル呼び出し記法の変更

**影響**: `$skill-name` 記法が使えない場合、スキル適用が不確実。

**対処**:
- Copilot CLI は AGENTS.md を自動読込するため、skills セクションのスキルは
  プロンプト内の自然言語指示で適用される
- 「`<workflow-skill> スキルに従って`」と明示的に指示する

### 課題 3: サンドボックスの粒度

**影響**: Codex の `-s workspace-write` ほど明確なサンドボックスがない。

**対処**:
- `--add-dir` でアクセス許可ディレクトリを限定（ワークスペース外を除外）
- `--deny-tool` で危険なツールを明示的に拒否
- tmux 監視でユーザが承認ダイアログに応答する運用は変わらない

---

## 推奨実装順序

1. **検証フェーズ**: 上記「検証が必要な項目」を実機で確認する
2. **SKILL.md 更新**: `autonomous-workflow-orchestrator` スキルを Copilot CLI 版に更新
3. **手順書更新**: 本文書を正式版に昇格させる
4. **試行運用**: 小規模 issue で一巡テストする
