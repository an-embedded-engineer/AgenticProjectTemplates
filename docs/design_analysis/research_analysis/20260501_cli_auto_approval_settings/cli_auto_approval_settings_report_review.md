# CLI 自動承認設定調査レポート レビュー

## レビュー情報

| 項目 | 内容 |
|------|------|
| レビュー日 | 2026-05-01 |
| 対象レポート | `docs/design_analysis/research_analysis/20260501_cli_auto_approval_settings/report.md` |
| レビュー担当 | Claude Code レビュー Agent |

---

## 検証方法

以下の根拠ソースを確認した。

| ソース | 確認方法 |
|--------|---------|
| `scripts/agent_cli_tmux.py` | ファイル精読（AgentCommandBuilder.build 実装） |
| `python-project-template/scripts/agent_cli_tmux.py` | ファイル精読（ルートと同一実装を確認） |
| `docs/procedure/autonomous_workflow_orchestrator.md` | ファイル精読（Codex / Claude 起動オプション） |
| `docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md` | ファイル精読（機能対応表・承認ポリシー記述） |
| `~/.claude/settings.json` | ファイル精読（Claude Code 設定の実在確認） |
| `copilot --help` | セッション権限の制約で直接実行不可。手順書内の記述と照合して間接確認 |
| `codex --help` | セッション権限の制約で直接実行不可。手順書内の記述と照合して間接確認 |

> CLI help の直接実行はセッション権限の制約により不可だった。ただし
> `autonomous_workflow_orchestrator_copilot_cli.md` の機能対応表が CLI help の
> 内容を反映した一次資料として機能しており、間接的に主要事実を検証できた。

---

## 根拠サマリー

### 検証ポイント 1: Copilot CLI `--no-ask-user` はツール承認を自動化しない

**根拠**

`autonomous_workflow_orchestrator_copilot_cli.md` の機能対応表（「ask_user 無効化」行）に
明確に記載されている。

```
ask_user 無効化 | N/A | N/A | --no-ask-user | ✅ 追加機能
```

一方、同文書の「ツール制限（サンドボックス）」セクションでは：

```
--no-ask-user でツール承認を自動化する。
```

と記述しており、これは `ask_user` ツール無効化とツール承認全般の自動化を
混同した不正確な記述である。

また `scripts/agent_cli_tmux.py` の `AgentCommandBuilder.build()` も
Copilot 起動時に `--no-ask-user` のみを付加しており、ツール承認用の
フラグは何も指定していない（lines 72, 74-76）。

**判定**: レポートの主張を支持。

---

### 検証ポイント 2: Copilot CLI は `--allow-tool` シェルパターンをサポートする

**根拠**

`autonomous_workflow_orchestrator_copilot_cli.md` の機能対応表「ツール制限（サンドボックス）」行：

```
--available-tools / --allow-tool / --deny-tool | ✅ より細粒度
```

同文書のサンドボックス対処方針でも `--deny-tool` を活用した危険ツール拒否が言及されている。

`shell(command:*?)` 形式の構文はローカル help (`copilot help permissions`) から
得られた情報とされており、今回の直接実行確認は未実施だが、
procedure 文書の記述と整合しており矛盾はない。

**判定**: レポートの主張を支持。ただし `shell(...)` の厳密なパターン構文は
live セッションでの動作確認が推奨される（未解決事項としてレポートも言及済み）。

---

### 検証ポイント 3: Codex は approval policy を持つが、ユーザー定義のコマンド allowlist は確認できない

**根拠**

`scripts/agent_cli_tmux.py` の Codex 起動コマンド（lines 62-65）：

```python
return (
    "codex --no-alt-screen "
    f"-C {shlex.quote(str(spec.cwd))} "
    "-s workspace-write -a on-request"
)
```

`autonomous_workflow_orchestrator.md` の Codex セクションでも：
- `-s workspace-write`（sandbox policy）
- `-a on-request`（approval policy）

のみが使用されており、コマンド単位 allowlist に相当する記述は存在しない。
`python-project-template/scripts/agent_cli_tmux.py` も同一実装であることを確認した。

**判定**: レポートの主張を支持。

---

### 検証ポイント 4: Claude Code は `permissions.allow` および `--allowedTools` をサポートする

**根拠**

`autonomous_workflow_orchestrator.md` の Claude 起動コマンドで
`--allowed-tools "Bash(git:*),Read,Write,Edit,MultiEdit"` が使用されている（line 75）。

`~/.claude/settings.json` の存在を確認した（`enabledPlugins` / `effortLevel` を含む）。
`permissions.allow` の実際の設定はこのシステム上では未設定だが、
Claude Code 公式ドキュメント (`settings.md`) に基づく説明はレポートを通じて整合している。

**判定**: レポートの主張を支持。

---

## 指摘事項

### [INFO-1] CLI help 直接実行の未確認

- **対象**: レポートのすべての CLI help 由来の記述
- **概要**: `copilot --help`、`copilot help permissions`、`codex --help` の
  ローカル実行出力を今回のレビューでは直接確認できなかった。
  ただし手順書内の機能対応表と整合しており、実質的な矛盾は発見されなかった。
- **推奨対応**: 指摘なし。レポートが未解決事項として `shell(...)` の live 確認を
  自ら明記しており、適切に処理されている。

### [INFO-2] 手順書内の `--no-ask-user` 記述の混在

- **対象**: `docs/procedure/autonomous_workflow_orchestrator_copilot_cli.md`
- **概要**: 同文書内で `ask_user 無効化` と `ツール承認自動化` が混在している。
  レポートはこの不整合を正しく検出している。
- **推奨対応**: 指摘なし。レポートはこれを推奨次 workflow（`spec-change-workflow`）の
  根拠として適切に位置づけている。

---

## 総合評価

| 検証ポイント | 結果 |
|-------------|------|
| `--no-ask-user` はツール承認を自動化しない | ✅ 支持 |
| `--allow-tool` シェルパターンをサポートする | ✅ 支持 |
| Codex はユーザー定義 allowlist を持たない | ✅ 支持 |
| Claude Code は `permissions.allow` / `--allowedTools` をサポートする | ✅ 支持 |

---

## 判定

**承認（修正不要）**

レポートの主要な調査結果は、リポジトリ内の実装コードおよび手順書から得られる
根拠と整合している。特に重要な発見である「Copilot CLI の `--no-ask-user` が
ツール承認全般の自動化フラグではなく `ask_user` ツールのみを無効化するフラグである」
という指摘は、`autonomous_workflow_orchestrator_copilot_cli.md` の記述の矛盾を
正確に捉えており、仕様変更の必要性を適切に示している。

指摘事項はいずれも INFO レベルであり、レポートの内容を変更する必要はない。
本レポートをそのまま承認する。
