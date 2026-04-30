# CLI command auto approval settings survey

## 調査目的

GitHub Copilot Chat/CLI、Codex、Claude Code について、主に次のような非破壊寄りコマンドの承認を不要化する設定方法を調査する。

- `agent_cli_tmux`
- `extract_git_diff`
- `grep`
- `rg`
- `cd`
- `cat`
- `find`
- `git status`

合わせて、このリポジトリで現在採用している orchestration 前提と各 CLI の実仕様が一致しているかを確認する。

## 調査対象

- Root / template 側の既存手順書と実装
- ローカルにインストール済みの `copilot` / `codex` / `claude` CLI help
- VS Code 同梱 Copilot 拡張の公開設定・文言定義
- Claude Code 公式ドキュメント

## 根拠ソース

### リポジトリ内

- `scripts/agent_cli_tmux.py`
- `python-project-template/scripts/agent_cli_tmux.py`
- `python-project-template/tools/extract_git_diff.py`
- `docs/procedure/autonomous_workflow_orchestrator.md`
- `docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md`

### ローカル CLI help / 設定

- `copilot --help`
- `copilot help permissions`
- `copilot help config`
- `codex --help`
- `claude --help`
- `~/.codex/config.toml`
- `~/.claude/settings.json`

### 外部ドキュメント

- `https://code.claude.com/docs/en/settings.md`
- `https://code.claude.com/docs/en/headless.md`
- `https://code.claude.com/docs/en/iam.md`

## 現状整理

### 1. この repo の現行前提

`scripts/agent_cli_tmux.py` と `python-project-template/scripts/agent_cli_tmux.py` の `AgentCommandBuilder` は、各 CLI を次のように起動している。

- Codex: `codex --no-alt-screen -C <cwd> -s workspace-write -a on-request`
- Claude Code: `TERM=dumb claude`
- Copilot CLI: `copilot --model <model> --no-ask-user` または `copilot --continue --model <model> --no-ask-user`

また、`docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md` では、`--no-ask-user` を「ツール承認を自動化する」前提として説明している。

### 2. 既存前提と実仕様のズレ

調査の結果、最も重要な差異は次の 2 点だった。

1. Copilot CLI の `--no-ask-user` は、`ask_user` ツールを無効化するフラグであり、シェル実行やファイル編集などのツール承認そのものを auto approve するフラグではない。
2. Codex は approval policy と sandbox policy は持つが、Claude Code や Copilot CLI のようなユーザー定義のコマンド allowlist は help から確認できなかった。

このため、現在の手順書にある「Copilot CLI は `--no-ask-user` で承認自動化できる」という書き方は、少なくともローカル help に基づく限り不正確である。

## 各ツールの調査結果

### GitHub Copilot CLI

#### 結論

Copilot CLI は 3 ツールの中で最も細かい allowlist を持っている。コマンド単位の自動承認は可能。

#### 確認できた仕組み

- `--allow-tool`
- `--deny-tool`
- `--allow-all-tools`
- `--available-tools`
- `--excluded-tools`
- `--allow-all`
- `--yolo`

`copilot help permissions` によると、`--allow-tool` と `--deny-tool` は permission pattern を受け取り、`shell(command:*?)` 形式で shell command 単位に許可できる。例として help 自体に次が載っている。

- `shell(git:*)`
- `shell(git push)`
- `write`
- `url(https://github.com)`

また `copilot --help` の説明では、次が明記されている。

- `--allow-all-tools`: 全ツールを確認なしで自動実行
- `--allow-tool`: 指定ツールは permission prompt を出さない
- `--deny-tool`: 指定ツールは permission prompt を出さないまま拒否
- `--no-ask-user`: ask_user ツールのみ無効化

#### 設定方法

セッション起動時の CLI 引数として渡すのが確認できた方法である。`copilot help config` で列挙される永続設定項目には URL / trusted folder / hooks はあるが、tool allowlist に相当する設定項目は確認できなかった。

そのため、現時点で確実なのは起動コマンドへ埋め込む方式である。

#### 非破壊寄りコマンドへの適用例

```bash
copilot \
  --model gpt-5.4 \
  --allow-tool='shell(rg)' \
  --allow-tool='shell(grep)' \
  --allow-tool='shell(find)' \
  --allow-tool='shell(cat)' \
  --allow-tool='shell(cd)' \
  --allow-tool='shell(git status)'
```

#### `agent_cli_tmux` / `extract_git_diff` への適用上の注意

Copilot CLI の shell permission pattern は基本的に command 名ベースで評価される。`python scripts/agent_cli_tmux.py` のような呼び方だと、許可単位が `python` になりやすく、script 単位に絞れない可能性が高い。

そのため、Copilot CLI で script 単位に細かく許可したい場合は、次のどちらかが必要になる。

1. shebang 付き executable として直接呼ぶ
2. 専用 wrapper command 名を作って、その command 名を allowlist する

repo 既存の `python scripts/agent_cli_tmux.py` 形式のままでは、`python` 全体を緩めることになりやすい。

#### VS Code Copilot Chat との関係

VS Code 同梱 Copilot 拡張の公開文字列には `github.copilot.resetAutomaticCommandExecutionPrompt` という command が存在した。一方で、公開 configuration key として command auto approval の allowlist を定義する項目は確認できなかった。

このため、VS Code の Copilot Chat は「自動実行確認の内部状態を持ち、リセット command はある」が、「repo に commit できる declarative な allowlist 設定は今回の調査範囲では確認できない」と整理するのが妥当である。

補足として、VS Code Copilot 拡張には `github.copilot.config.claudeAgent.allowDangerouslySkipPermissions` が存在するが、これは Claude Agent provider 向けの bypass 許可であり、Copilot Chat 全般の per-command allowlist ではない。

### Codex CLI

#### 結論

Codex は approval policy と sandbox policy を持つが、ユーザー定義の command allowlist は確認できなかった。今回の要件には最も不向き。

#### 確認できた仕組み

- `-a, --ask-for-approval <untrusted|on-failure|on-request|never>`
- `-s, --sandbox <read-only|workspace-write|danger-full-access>`
- `--full-auto`
- `--dangerously-bypass-approvals-and-sandbox`

`codex --help` では approval policy の意味が次のように説明されている。

- `untrusted`: built-in の trusted command だけ無確認で実行
- `on-request`: モデル判断で承認を求める
- `never`: ユーザー承認を一切求めない

#### 制約

help と `~/.codex/config.toml` の確認範囲では、Claude Code の `permissions.allow` や Copilot CLI の `--allow-tool='shell(...)'` に相当する、ユーザーが任意コマンドを allowlist する機構は確認できなかった。

したがって、次のような要件は満たしにくい。

- `rg`, `grep`, `find`, `git status` だけ自動承認
- `python scripts/agent_cli_tmux.py` だけ自動承認
- それ以外は都度承認

実現できるのは、概ね次の 3 択になる。

1. `-a untrusted` にして組み込み trusted set に任せる
2. `-a on-request` にしてモデル判断に任せる
3. `-a never` または `--dangerously-bypass-approvals-and-sandbox` で全体を無確認化する

#### 評価

今回の「非破壊寄りコマンドだけ無承認化したい」という要件には、Codex は粒度が粗すぎる。

### Claude Code

#### 結論

Claude Code は settings.json と CLI flag の両方で、最も明示的に command allowlist を管理できる。今回の要件に最も適合する。

#### 確認できた仕組み

CLI help と公式 docs の両方から、次を確認できた。

- `--allowed-tools`
- `--disallowed-tools`
- `--permission-mode`
- `--settings <file-or-json>`
- `permissions.allow`
- `permissions.ask`
- `permissions.deny`
- `permissions.defaultMode`

公式 docs の `settings.md` では、`~/.claude/settings.json`、`.claude/settings.json`、`.claude/settings.local.json` の階層化設定が明記されている。また permission rule syntax も公開されており、`Bash(git diff *)`、`Read(./.env)` などの prefix / path ベース指定が可能である。

#### 設定方法

共有設定にしたい場合は project scope の `.claude/settings.json`、個人だけで試すなら `.claude/settings.local.json` が適切。

例:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(rg *)",
      "Bash(grep *)",
      "Bash(find *)",
      "Bash(cat *)",
      "Bash(cd *)",
      "Bash(git status *)",
      "Bash(python scripts/agent_cli_tmux.py *)",
      "Bash(python python-project-template/tools/extract_git_diff.py *)"
    ]
  }
}
```

headless / CI 的に 1 回限り渡す場合は次でもよい。

```bash
claude -p "Run the read-only inspection workflow" \
  --allowedTools "Bash(rg *),Bash(grep *),Bash(find *),Bash(cat *),Bash(git status *)"
```

#### permission mode の使い分け

- `default`: 通常の permission 挙動
- `acceptEdits`: file edit と一部 filesystem command を auto approve
- `dontAsk`: `permissions.allow` と read-only command set 以外は prompt ではなく abort
- `bypassPermissions`: 全 permission check を飛ばす

今回の要件では、通常運用なら `default` のまま `permissions.allow` を積み増すのが最も安全。CI 的に hard fail が欲しい場合だけ `dontAsk` を併用するのがよい。

#### sandbox を使う代替案

公式 docs では `sandbox.autoAllowBashIfSandboxed` の既定値が `true` とされている。つまり sandbox を有効化した Bash command は、sandbox 内で auto approve されやすい。

ただしこの方式は「sandbox に通る Bash 全体」が対象になりやすく、今回のような read-only command のみ細かく許可したい要件には、`permissions.allow` の明示 allowlist の方が制御しやすい。

## 比較

| 観点 | Copilot CLI | Codex CLI | Claude Code |
|------|-------------|-----------|-------------|
| command 単位 allowlist | 可能 | help からは確認不可 | 可能 |
| 永続設定 | tool allowlist は未確認 | 粒度粗い trust / config はある | 可能 |
| script 単位の細粒度化 | 呼び出し方に工夫が必要 | 実質不可 | Bash prefix で比較的やりやすい |
| VS Code Chat との整合 | Chat 側は reset command はあるが declarative 設定未確認 | N/A | VS Code 拡張でも同じ settings 階層を利用 |
| 今回要件への適合度 | 中 | 低 | 高 |

## 推奨方針

### 推奨 1: Claude Code は `.claude/settings.json` の `permissions.allow` を使う

最も再現性が高く、repo 共有もしやすい。`agent_cli_tmux` と `extract_git_diff` も command prefix で許可しやすい。

### 推奨 2: Copilot CLI は `--allow-tool` を使うが、script は wrapper 化を前提にする

`grep` / `rg` / `find` / `cat` / `git status` は直接 allowlist できる。一方で Python script を `python <script>` で呼ぶ構成は粒度が荒いので、wrapper command へ寄せた方がよい。

### 推奨 3: Codex は現状の `-a on-request` 維持が妥当

今回の要件に合う細粒度 allowlist が確認できない以上、無理に `never` 側へ倒さない方がよい。

## リスクと未解決事項

### リスク

1. Copilot CLI の `--no-ask-user` を tool auto approval と誤認したまま運用すると、想定より多くの承認待ちが残る。
2. Copilot CLI で Python wrapper を使わず `python ...` 形式を残すと、`python` 全体を許可しがちで許可粒度が粗くなる。
3. Claude Code の `bypassPermissions` や Copilot CLI の `--allow-all-tools` を安易に使うと、read-only command だけを緩める意図を超えてしまう。

### 未解決事項

1. VS Code Copilot Chat に、公開されていない内部設定以外で declarative な command allowlist が存在するかは未確認。
2. Copilot CLI の tool allowlist を設定ファイルへ永続化する公式キーは、今回の `help config` 範囲では確認できなかった。
3. Copilot CLI の `shell(...)` が script path をどの粒度で match するかは、live session での挙動確認までは実施していない。

## 推奨する次 workflow

`spec-change-workflow` を推奨する。

理由:

- `docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md` の承認説明を実仕様へ合わせて修正する必要がある。
- `scripts/agent_cli_tmux.py` の Copilot 起動オプションを `--no-ask-user` 中心から `--allow-tool` ベースへ再設計する余地がある。
- Claude Code / Copilot CLI 向けの shared settings / wrapper command 方針を、instructions と procedure に同期する必要がある。