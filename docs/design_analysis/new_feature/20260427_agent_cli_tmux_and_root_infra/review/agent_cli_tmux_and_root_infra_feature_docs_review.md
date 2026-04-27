# Agent CLI tmux ツール・Root インフラ 実装レビュー

**レビュー日**: 2026-04-27
**対象コミット**:
- `c349f8f` — Add ADR index and shared Agent CLI tmux tooling
- `8caa3c9` — Add root workflow infrastructure
- `6f178d3` — Sync root agent skills for Copilot and Claude

**対象実装**:
- `scripts/agent_cli_tmux.py` (root)
- `python-project-template/scripts/agent_cli_tmux.py`
- `csharp-project-template/tools/AgentCliTmux/Program.cs`
- `python-project-template/tests/test_agent_cli_tmux_python_template.py`
- `csharp-project-template/tests/AgentCliTmux.Tests/Program.cs`
- `scripts/sync_agent_skills.sh|.ps1|.bat`
- `docs/`, `instructions/`, `docs/adr/`, `docs/procedure/`

---

## 概要

本レビューは 3 コミットにまたがる新機能追加（ADR 駆動インフラ、tmux Agent CLI 操作ツール、root instructions/skills 同期機構）を対象とする。
主要観点は設計品質・仕様整合・保守性・テスト網羅性の 4 軸。

---

## 1. 齟齬・不整合

### 1.1 `docs/architecture/overview.md` に root scripts/agent_cli_tmux.py の記載がない

**ドキュメント記載**:
> Python Agent CLI tmux tool: `python-project-template/scripts/agent_cli_tmux.py`

**実装**: `scripts/agent_cli_tmux.py`（root）と `python-project-template/scripts/agent_cli_tmux.py` の 2 ファイルが完全同一（diff 0）で存在する。

**差異**: root レベルのスクリプトが `overview.md` に記載されていない。`development_workflow.md` には両ファイルの `py_compile` が記載されているため、文書間で記載粒度が不一致。

**推奨対応**: `docs/architecture/overview.md` の「主要ファイルリファレンス」に `Root Agent CLI tmux tool: scripts/agent_cli_tmux.py` を追記する。

**対応**: 対応済み。`docs/architecture/overview.md` の「主要ファイルリファレンス」に `Root Agent CLI tmux tool: scripts/agent_cli_tmux.py` を追記した。

---

### 1.2 root scripts/agent_cli_tmux.py のテスト戦略が未定義

**ドキュメント記載** (`development_workflow.md`):
```
python3 -m py_compile scripts/agent_cli_tmux.py
```

**実装**: python-project-template/tests には `test_agent_cli_tmux_python_template.py` が存在するが、root の `scripts/agent_cli_tmux.py` を直接対象とするテストは存在しない（reference/ 配下に同一構成のテストがあるが未追跡）。

**差異**: root スクリプトの構文チェックしか行われない。pytest レベルの動作検証はテンプレート側テストで間接的に担保されている状態。

**推奨対応**: `development_workflow.md` に「root の agent_cli_tmux.py は python-project-template/tests/ で間接的に検証される（ファイルが完全同一のため）」旨を明記するか、root に向けたテスト実行コマンドを追加する。

**対応**: 対応済み。`docs/rules/development_workflow.md` に、root `scripts/agent_cli_tmux.py` は `py_compile` で確認し、動作検証は同一内容の `python-project-template/scripts/agent_cli_tmux.py` を対象にした pytest で間接検証する方針を追記した。

---

## 2. ドキュメント不足

### 2.1 `~/.codex/skills` グローバルインストールの影響範囲が未記載

**不足**: `scripts/sync_agent_skills.sh` の `sync_codex` 関数は `~/.codex/skills` へ直接書き込む。これは他プロジェクトの codex スキルを上書きする可能性がある。`instructions/agent_sync_guide.md` にこのリスクへの言及がない。

**推奨対応**: `agent_sync_guide.md` の「運用ルール」に「`--codex` または `--all` を指定すると `~/.codex/skills` がグローバルに上書きされる。複数プロジェクトで codex を利用する場合はバックアップを先に取るか `--copilot --claude` のみ同期する」旨を追記する。

**対応**: 対応済み。`instructions/agent_sync_guide.md` の運用ルールに、`--codex` / `--all` が `~/.codex/skills` をグローバルに上書きすることと、複数プロジェクト利用時は退避または同期対象の方針確認が必要である旨を追記した。

---

### 2.2 root/python-template 間のスクリプト同期運用が未規定

**不足**: `scripts/agent_cli_tmux.py` と `python-project-template/scripts/agent_cli_tmux.py` が現在 diff 0 で存在するが、どちらが正本でどのように同期するかのルールが文書化されていない。`coding_rules.md` の「テンプレート境界」節は C# 向けの制約のみ明示しており、root/template 間の Python スクリプト重複に関する方針が欠けている。

**推奨対応**: `docs/architecture/overview.md` または `docs/rules/coding_rules.md` に「`scripts/agent_cli_tmux.py` (root) と `python-project-template/scripts/agent_cli_tmux.py` は意図的に同一内容を保持する。変更時は両ファイルを同時に更新し、`development_workflow.md` の両 py_compile を通過させる」旨を記載する。

**対応**: 対応済み。`docs/architecture/overview.md` と `docs/rules/coding_rules.md` に、root `scripts/agent_cli_tmux.py` と Python テンプレート側スクリプトを意図的な重複として同一内容に保つ方針を追記した。

---

## 3. 改善提案

### 3.1 引数なしで全同期（~/.codex 含む）が実行されるデフォルト動作

**現状**: `parse_args` に引数ゼロの場合 `SYNC_COPILOT=SYNC_CLAUDE=SYNC_CODEX=1` になる。`~/.codex` は他プロジェクトへの影響があるため、明示的な `--all` 指定がない限りグローバル展開を避けるデフォルトに変更することを検討する。

**推奨対応**: デフォルト動作を `--copilot --claude` に絞り、`--all` を明示的なオプションとして維持する変更を検討する。または現状維持でドキュメントに警告を加える（最小変更案）。

**対応**: 対応済み（最小変更案）。`instructions/agent_sync_guide.md` に `--codex` / `--all` のグローバル上書きリスクを明記した。デフォルト動作は既存テンプレートとの同期スクリプト互換を優先して現状維持とする。

---

### 3.2 C# ParseOptions が文字列辞書ベースの独自パーサー

**現状**: Python 側は `argparse` で型安全（`type=int/float`）だが、C# 側は `Dictionary<string, string?>` 経由で `ParseInt`/`ParseSleepSeconds` による遅延バリデーションになっている。

**評価**: C# で標準 CLIライブラリへの依存を避け、外部アセンブリゼロで実装した合理的な選択と判断できる。動作は Python と等価でありバグの可能性も低い。重大な問題ではない。

**推奨対応**: `docs/architecture/code_patterns.md` または C# `Program.cs` の先頭コメントに「標準 CLIライブラリ非依存のため独自パーサーを使用」と理由を記録することで、将来の読者が疑問を持たないようにする。

**対応**: 対応済み。`csharp-project-template/tools/AgentCliTmux/Program.cs` に、外部 CLI パーサー依存を避けてテンプレート単体で build/run できるよう最小パーサーを使う旨のコメントを追記した。

---

### 3.3 capture/status サブコマンドに --dry-run オプションなし

**現状**: `start/ensure/send-prompt/stop/sleep` は `--dry-run` をサポートするが、`capture/status` にはない。これは「tmux から取得する」という操作の性質上 dry-run が無意味なため合理的。

**評価**: 問題なし。`capture`/`status` は tmux の現在状態を読み取るだけで副作用がないため dry-run 対象外とする設計は適切。

**推奨対応**: なし（現状維持で可）。

---

## 4. 整合性確認済み項目

| 項目 | 確認結果 |
|------|----------|
| `CLAUDE.md` ↔ `instructions/agent_common_master.md` | ✓ 完全一致（diff 0） |
| `.claude/skills/` ↔ `.github/skills/` | ✓ 完全一致（全 skill diff 0） |
| `scripts/agent_cli_tmux.py` ↔ `python-project-template/scripts/agent_cli_tmux.py` | ✓ 完全一致（diff 0） |
| Python/C# の同等コマンド動作 | ✓ 同等（start/ensure/send-prompt/capture/status/stop/sleep） |
| ADR インデックスが root・両テンプレートに配置 | ✓ 3 箇所に同一構成で配置 |
| `docs/adr/README.md` の起票条件・索引規則 | ✓ 明確に定義されている |
| workflow phase library による共通フェーズ共有 | ✓ DRY 原則を順守 |
| coding_rules.md の型安全性ルールがコードに反映されている | ✓ dataclass/record/型注釈が一貫して使われている |
| 例外を握りつぶしていない | ✓ RuntimeError/ValueError/CliException が適切に伝播する |
| 不要なフォールバックなし | ✓ 仕様外入力は即 ValueError/CliException |
| `reference/` が未追跡 | ✓ git status で `??` のみ（コミット対象外） |
| `scripts/__pycache__/` が未追跡 | ✓ git ls-files で未追跡 |
| Python テスト網羅性（dry-run パス中心） | ✓ 主要コマンド・エラー系が網羅されている |
| C# テスト網羅性（Python と同等ケース） | ✓ Python と対称的なケースが揃っている |
| `docs/design_analysis/` 階層構造が定義されている | ✓ README.md で category/yyyymmdd_topic/review/ を明示 |
| sync スクリプトが 3 プラットフォーム対応 | ✓ bash/ps1/bat が存在 |
| SKILL.master.md (legacy) / SKILL.md (structured) の両形式対応 | ✓ copy_skill_dir で分岐処理 |

---

## 5. 対応優先度

| 優先度 | 項目 | 理由 |
|--------|------|------|
| 高 | 2.1: ~/.codex グローバルインストールの警告未記載 | 対応済み |
| 中 | 1.1: overview.md に root scripts パス未記載 | 対応済み |
| 中 | 1.2: root スクリプトのテスト戦略未定義 | 対応済み |
| 中 | 2.2: root/template 間スクリプト重複の方針未文書 | 対応済み |
| 低 | 3.1: 引数なし全同期デフォルト | 対応済み（ドキュメント警告、動作は現状維持） |
| 低 | 3.2: C# 独自パーサーの設計理由未記録 | 対応済み |

---

## 6. 結論

3 コミットで追加された機能は全体として設計品質が高く、以下の観点が優れている。

- **責務分離**: `AgentCommandBuilder` / `TmuxRunner` の分離、workflow phase library による共通フェーズ共有
- **型安全性**: Python/C# 両方で値オブジェクトを使い、動的な辞書アクセスを最小化
- **対称性**: Python/C# の同等ツールが機能・テスト・dry-run の各軸で対称的に実装
- **文書整合**: CLAUDE.md / agent_common_master.md、.claude/skills / .github/skills がいずれも同期済み

**残課題**:
なし。レビュー指摘はすべて対応済み。
