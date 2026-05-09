# project-level instruction 整理 レビュー（Claude）

## 対象

- commit: `ac93c7ee9fec794654fe840d0c65414648f4806a`
- summary: `Clean up project-level agent instruction assets`
- review date: 2026-05-09
- reviewer: Claude (Opus 4.7)

## 総評

`docs/procedure/` と旧再生成 script (`rebuild_user_agent_skills.py`) を削除し、root の責務を「project-level instruction sync source + 検証」に絞り、workflow 手順の正本を `user-agent-assets/skills/*/references/procedure/` 側へ寄せる方向性は妥当である。`README.md` / `docs/rules/` / `docs/architecture/` の更新も同方針と整合しており、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は `instructions/agent_common_master.md` と byte 単位で一致している（`cmp` 確認済み）。

ただし、追加された `scripts/sync_agent_instructions.sh` の file mode が周辺ドキュメントの想定と食い違っているため、後追い修正が必要である。Codex レビューと同一の指摘を独立に確認した。

## Findings

## 対応状況（2026-05-09）

- [Medium] `scripts/sync_agent_instructions.sh` の実行 bit が落ちている
	- status: `resolved`
	- 対応: `chmod +x scripts/sync_agent_instructions.sh` で実行権限を付与し、直接実行の検証を追加した
- [Low] `scripts/sync_agent_instructions.sh` の `usage()` 出力にインデント不整合
	- status: `resolved`
	- 対応: shell script の help ブロックを再整形し、オプション行を 2-space 始まりに統一した
- [Low] `instructions/agent_sync_guide.md` が `--all` / `-All` を案内していない
	- status: `resolved`
	- 対応: macOS / Linux、PowerShell、Command Prompt の実行例とオプション節へ `--all` / `-All` を追記した
- [Low] `instructions/agent_common_master.md` に末尾改行がない
	- status: `resolved`
	- 対応: `instructions/agent_common_master.md` を更新して再同期し、生成物 3 種も含めて末尾改行ありの状態へ揃えた
- [Info] root agent instructions の文面と「メタプロジェクト」表現について
	- status: `noted`
	- 対応: 任意改善として扱いつつ、片方向だった Python / C# の asset / tool 検討方針を双方向表現へ更新した

### [Medium] `scripts/sync_agent_instructions.sh` の実行 bit が落ちている（Codex 指摘と同件）

- 対象:
	- `scripts/sync_agent_instructions.sh`
	- `README.md:55`
	- `instructions/agent_sync_guide.md:25-28`
- 観測:
	- `git ls-tree ac93c7e scripts/` で確認した mode は `100644`。
	- 同一内容の bootstrap template 側 `user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh` は `100755` で、root 側だけ落ちている（blob hash は同一なので、内容自体には差異なし）。
	- 実機でも `./scripts/sync_agent_instructions.sh --help` は `permission denied` で失敗した。
- 影響:
	- `README.md` は手順 4 で `./scripts/sync_agent_instructions.sh` の直接実行を案内しており、`instructions/agent_sync_guide.md` も macOS / Linux 用の実行例として `./scripts/sync_agent_instructions.sh` を提示している。これら主要導線がそのままでは動作しない。
	- `docs/rules/development_workflow.md` 側は `bash ./scripts/sync_agent_instructions.sh --help` を案内しているため検証では拾われづらく、利用者向けと検証導線の食い違いを増やす要因にもなる。
- 推奨対応:
	- `git update-index --chmod=+x scripts/sync_agent_instructions.sh` 等で mode を `100755` に揃えてコミットする。
	- 検証コマンドに `./scripts/sync_agent_instructions.sh --help`（`bash` を前置きしない形）を加えると、今回のような mode 落ちを早期検知できる。

### [Low] `scripts/sync_agent_instructions.sh` の `usage()` 出力にインデント不整合

- 対象: `scripts/sync_agent_instructions.sh:14-27`
- 内容:
	- ヒアドキュメント内の `Options:` 配下で、`--copilot` / `--claude` / `--codex` の 3 行は 4-space 始まり、`--all` / `-h, --help` の 2 行は 2-space 始まりになっており、help 表示で列が揃わない。
	- `.bat` / `.ps1` 側はいずれも 2-space 列で揃っており、shell 版だけ列ズレが発生する。
- 影響:
	- 機能差はないが、`--help` を眺めた時の見栄えが OS 間で揃わない。
- 推奨対応:
	- `--copilot` / `--claude` / `--codex` の 3 行を 2-space 始まりに揃える。

### [Low] `instructions/agent_sync_guide.md` が `--all` / `-All` を案内していない

- 対象: `instructions/agent_sync_guide.md:22-44`
- 内容:
	- 3 種類のスクリプト（`.sh` / `.ps1` / `.bat`）は `--all` / `-All` を実装しているが、`agent_sync_guide.md` の「実行方法」「オプション」節には記載がない。
	- 「オプション未指定時は全ターゲットを再生成する」とは書かれているため省略不可ではないが、`-All` を明示するスクリプトの help 表示と guide の記述が整合しない。
- 推奨対応:
	- 「オプション」節に `--all` / `-All` を明記し、help との整合を取る。任意。

### [Low] `instructions/agent_common_master.md` に末尾改行がない

- 対象: `instructions/agent_common_master.md:46`
- 内容:
	- `git show` 出力で `\ No newline at end of file` が表示される通り、master ファイルは末尾改行なしで保存されている。`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は単純コピーなので、生成物 3 種すべてに同じ状態が伝播している。
	- 動作上の支障はないが、POSIX 的には text file の末尾改行が望ましく、`pre-commit` の `end-of-file-fixer` 等を導入した際にノイズ差分の発生源になりやすい。
- 推奨対応:
	- master 側に末尾改行を 1 文字追加し、`bash ./scripts/sync_agent_instructions.sh` で 4 ファイル分まとめて再生成する。優先度は低い。

### [Info] root agent instructions の文面と「メタプロジェクト」表現について

- 対象: `instructions/agent_common_master.md:5-6`
- 内容:
	- 「本リポジトリはテンプレートを生成する単一アプリではなく、複数言語向け project bootstrap 資産、user-level skills、shared runtime、関連ドキュメントを保守するメタプロジェクトである。」という導入文は、`README.md` 冒頭の「user-level assets と project bootstrap 資産を管理するリポジトリ」と整合しており、生成物として読まれた際のノイズも目立たない。レビュー観点 1 は満たしていると判断する。
	- 一方で「Python 向け bootstrap asset や tool を追加した場合、C# 側でも同等の .NET asset / tool を優先して検討する」は片方向の記述で、C# 側に追加した場合の Python への横展開が暗黙になっている。Python / C# の同期方針自体は前段で「同等概念は、意図的な差異を除き同期する」と双方向で書かれているので致命的ではないが、後段だけ片方向なのが少し気になる程度。任意改善。
- 推奨対応:
	- 必要であれば、後段を「Python / C# のいずれかに asset / tool を追加した場合、もう一方でも同等の asset / tool を優先して検討する」と双方向化する。任意。

## 確認済み事項（レビュー観点別）

### 観点 1: root `agent_common_master.md` の導入文

- 「sync source 自体の説明」から「project 概要説明」への置き換えは適切に行われている。
- bootstrap template 側 `user-agent-assets/skills/project-doc-bootstrap/templates/{python,csharp}/instructions/agent_common_master.md` は `Sync Source` を冒頭に置いた文面のままで、root の文面とは意図通り分離されている（report の C-2026-009 切り出しと整合）。

### 観点 2: 削除後の参照残存

- active docs / instructions / 生成物 3 種 / `scripts/` を対象に `docs/procedure`、`instructions/skills`、`rebuild_user_agent_skills` を grep し、削除済み path への運用上の依存は確認されなかった。
- ヒットしたのは `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` / `instructions/agent_common_master.md` 内の「`docs/procedure/` を前提にしない」という否定形の記述のみで、削除方針を強める意図と矛盾しない。
- 過去 review / design analysis の履歴文書には旧 path の言及が残っているが、report の補足どおり履歴文脈として扱える範囲。

### 観点 3: template 側改善を `C-2026-009` へ分離した判断

- bootstrap 後の placeholder 化と project 固有説明の補助は、root 1 件の cleanup と論点が独立しており、template 側も Python / C# 両方を巻き込むため、issue として切り出した判断は妥当。
- `docs/issues/cross/issues.md:101-113` に追記された scope（`templates/python/instructions/agent_common_master.md` / `templates/csharp/instructions/agent_common_master.md`）が双方を含んでおり、横展開の前提も担保されている。

### 観点 4: user-level skill 正本と root docs の責務境界

- `README.md` / `docs/rules/project_overview.md` / `docs/rules/development_workflow.md` / `docs/rules/README.md` / `docs/architecture/overview.md` がいずれも、workflow 手順の正本を `user-agent-assets/skills/*/references/procedure/` と明記している。
- root の責務は「project-level instruction sync source + 共通検証」に縮小され、`scripts/sync_agent_instructions.*` は project-level 生成物 3 種のみを扱う、という説明が `instructions/agent_common_master.md:42-44` と `instructions/agent_sync_guide.md:55-58` で揃っている。
- 責務境界は今回の修正で明確になっている。

## 検証ログ

- `cmp -s instructions/agent_common_master.md AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`: いずれも一致。
- `bash ./scripts/sync_agent_instructions.sh --help`: 成功（usage 表示）。
- `./scripts/sync_agent_instructions.sh --help`: 成功。
- `./scripts/sync_agent_instructions.sh`: 成功。
- `cmp -s instructions/agent_common_master.md AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`: 修正後も一致。
- `python3 -c 'from pathlib import Path; print(Path("instructions/agent_common_master.md").read_bytes().endswith(b"\n"))'`: `True`。
- 削除 path / 旧スクリプトの参照 grep: 否定形の言及以外は無し。

## 追加指摘（2026-05-10、修正コミット `5809f48` 確認時）

5809f48 で root 側の指摘 5 件は解消されたことを確認した。一方、root と bootstrap template (`user-agent-assets/skills/project-doc-bootstrap/templates/common/`) の同期が今回の対応で崩れている。

### [Medium] root 修正が `templates/common/` へ伝播していない

- 対象:
	- `scripts/sync_agent_instructions.sh` ↔ `user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh`
	- `instructions/agent_sync_guide.md` ↔ `user-agent-assets/skills/project-doc-bootstrap/templates/common/instructions/agent_sync_guide.md`
- 観測:
	- `git ls-tree 5809f48 -- scripts/sync_agent_instructions.sh user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh` で確認:
		- root: `100755 6a577d3` (新版、indent 修正済み)
		- template: `100755 c2ed8bd` (旧版、indent 未修正)
	- `diff` 結果でも、template 側の `usage()` ブロックは依然として `--copilot` / `--claude` / `--codex` 行が 4-space 始まりのままになっている。
	- 同様に template 側 `agent_sync_guide.md` には `--all` / `-All` の実行例とオプション節が追記されておらず、root 側にだけ含まれている。
	- 元コミット `ac93c7e` 時点では root と template の `.sh` / `.bat` / `.ps1` / `agent_sync_guide.md` は blob hash が完全に一致していた（mode 差を除く）ため、両者を byte-identical に保つ意図が読み取れる。
- 影響:
	- `project-doc-bootstrap` で新規 project を立ち上げた際、bootstrap 後に作成される `scripts/sync_agent_instructions.sh` と `instructions/agent_sync_guide.md` には今回 root で潰した issue が再混入する。
	- root 側 CLAUDE.md (`instructions/agent_common_master.md:24`) で「Python / C# 向け bootstrap template の同等概念は、意図的な差異を除き同期する」と明示しているため、本リポジトリの保守ルールにも反する。
	- template の `--all` 文書欠落は、bootstrap 直後の利用者が `script --help` 出力と guide を見比べた際の整合性を欠く。
- 推奨対応:
	- `templates/common/scripts/sync_agent_instructions.sh` を root と同一内容に更新する（indent 修正の反映）。
	- `templates/common/instructions/agent_sync_guide.md` に `--all` / `-All` の実行例とオプション節を反映する。
	- 反映後、`diff scripts/sync_agent_instructions.{sh,bat,ps1} user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.{sh,bat,ps1}` と `diff instructions/agent_sync_guide.md user-agent-assets/skills/project-doc-bootstrap/templates/common/instructions/agent_sync_guide.md` がいずれも空であることを検証に追加すると、今後の root-only 修正の再発を防げる。

### 追加検証ログ

- `git ls-tree 5809f48 scripts/sync_agent_instructions.sh`: `100755 6a577d3`（実行 bit / indent 修正）。
- `./scripts/sync_agent_instructions.sh --help`: 成功（exit 0）。
- master の末尾改行: `tail -c 1` で `0a` を確認。
- `cmp` による master と生成物 3 種の一致: 修正後も維持。
- `diff scripts/sync_agent_instructions.bat templates/common/scripts/sync_agent_instructions.bat`: 差分なし。
- `diff scripts/sync_agent_instructions.ps1 templates/common/scripts/sync_agent_instructions.ps1`: 差分なし。
- `diff scripts/sync_agent_instructions.sh templates/common/scripts/sync_agent_instructions.sh`: 21〜23 行で差分あり（追加指摘の根拠）。
- `diff instructions/agent_sync_guide.md templates/common/instructions/agent_sync_guide.md`: 4 箇所で差分あり（追加指摘の根拠）。

## 結論

責務境界の整理と root docs / generated instructions / sync source の整合は達成されている。当初の Medium / Low / Info はいずれも 5809f48 で解消済み。

ただし root のみで修正したことで、bootstrap template 側 (`templates/common/scripts/sync_agent_instructions.sh` と `templates/common/instructions/agent_sync_guide.md`) が同期から外れている。Medium 1 件として template 側へ同じ修正を反映し、`diff` を検証に組み込むことを推奨する。
