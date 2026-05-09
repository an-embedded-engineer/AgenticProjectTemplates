# project-level instruction 整理 レビュー（Codex）

## 対象

- commit: `ac93c7ee9fec794654fe840d0c65414648f4806a`
- summary: `Clean up project-level agent instruction assets`
- review date: 2026-05-09
- reviewer: Codex

## Findings

## 対応状況（2026-05-09）

- [Medium] macOS / Linux 向けの案内どおりに sync script を直接実行できない
  - status: `resolved`
  - 対応: `scripts/sync_agent_instructions.sh` に実行権限を付与し、`./scripts/sync_agent_instructions.sh --help` と `./scripts/sync_agent_instructions.sh` の直接実行を確認した
  - 追加対応: `docs/rules/development_workflow.md` の検証コマンドを直接実行ベースへ更新し、`instructions/agent_sync_guide.md` に `--all` / `-All` を追記した

## 追加レビュー（2026-05-10）

## 追加レビュー対応状況（2026-05-10）

- [Low] root の sync guide / shell help 修正が bootstrap template 側へ反映されていない
  - status: `resolved`
  - 対応: `templates/common/scripts/sync_agent_instructions.sh` の help インデントと `templates/common/instructions/agent_sync_guide.md` の `--all` / `-All` 案内を root と同一内容へ更新した
  - 検証: root と template common の対象ファイルに対する `diff` が空であることを確認した

## 追加レビュー（2026-05-10, `9b248112` 確認）

### [Low] review 文書の結論が解消済み指摘を未解消として残している

- 対象:
  - `docs/design_analysis/issue_resolution/20260509_project_level_instruction_cleanup/review_codex.md:81`
  - `docs/design_analysis/issue_resolution/20260509_project_level_instruction_cleanup/review_claude.md:172`
- 内容:
  - `9b2481126a18ab16ed342fd8d6f55eceb697a381` で root / template common の `sync_agent_instructions.sh` と `agent_sync_guide.md` は内容一致し、`review_codex.md` と `review_claude.md` の対応状況も `resolved` に更新されている。
  - しかし、`review_codex.md` の総評は root shell script の file mode 不整合を未解消として読める文のまま残っている。
  - 同様に、`review_claude.md` の結論も bootstrap template 側が同期から外れているとして Medium 指摘の対応を推奨する文のまま残っている。
- 影響:
  - 対応状況では resolved、結論では未解消という状態になり、後続レビューや完了判定時に現在の残課題を誤読しやすい。
- 推奨対応:
  - 対応済みの結論へ更新するか、元の結論は「初回レビュー時点の結論」であることが分かる見出しへ分離する。

### [Low] root の sync guide / shell help 修正が bootstrap template 側へ反映されていない

- 対象:
  - `instructions/agent_sync_guide.md:25-54`
  - `user-agent-assets/skills/project-doc-bootstrap/templates/common/instructions/agent_sync_guide.md:25-51`
  - `scripts/sync_agent_instructions.sh:20-24`
  - `user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh:20-24`
- 内容:
  - 対応コミット `5809f487aa305a7d30f02af74ad4fdd961071570` では、root の `instructions/agent_sync_guide.md` に `--all` / `-All` の実行例とオプション説明が追加され、root の shell script help も 2-space インデントへ整形された。
  - しかし、project bootstrap で target project へ配布される `user-agent-assets/skills/project-doc-bootstrap/templates/common/instructions/agent_sync_guide.md` と `templates/common/scripts/sync_agent_instructions.sh` は旧記述のままである。
  - そのため root では解消済みの guide / help 表示の不整合が、bootstrap 後の target project には残る。
- 影響:
  - 実行機能には影響しないが、`project-doc-bootstrap` が配布する sync guide / script と root の正本運用が乖離する。
  - README は `project-doc-bootstrap` で docs / instructions / sync script を配布すると説明しているため、共通 sync 資産の説明差分は利用者に見える。
- 推奨対応:
  - root の `instructions/agent_sync_guide.md` と `scripts/sync_agent_instructions.sh` の今回修正分を、`user-agent-assets/skills/project-doc-bootstrap/templates/common/` 側の対応ファイルにも横展開する。
  - もしくは root 専用差分として残す理由があるなら、今回の report へ意図的差異として明記する。

### [Medium] macOS / Linux 向けの案内どおりに sync script を直接実行できない

- 対象:
  - `scripts/sync_agent_instructions.sh`
  - `README.md:55`
  - `instructions/agent_sync_guide.md:25`
- 内容:
  - `README.md` と `instructions/agent_sync_guide.md` は macOS / Linux の実行方法として `./scripts/sync_agent_instructions.sh` を案内している。
  - しかし、対象コミットで追加された root script の git mode は `100644` であり、実行権限が付いていない。
  - 実測でも `./scripts/sync_agent_instructions.sh --help` は `permission denied` で失敗した。
  - 一方、同一内容の bootstrap template 側 `user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh` は `100755` で、root 側だけ mode が落ちている。
- 影響:
  - README / sync guide の主要導線どおりに project-level instruction sync を実行できない。
  - root `development_workflow.md` は `bash ./scripts/sync_agent_instructions.sh` を案内しているため検証では見落としやすいが、ユーザー向け手順と実ファイル状態が不整合になっている。
- 推奨対応:
  - `scripts/sync_agent_instructions.sh` に実行権限を付け、git mode を `100755` に揃える。
  - 併せて `./scripts/sync_agent_instructions.sh --help` を検証に追加する。

## 確認済み事項

- `instructions/agent_common_master.md`、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` は `cmp` で一致を確認した。
- `bash ./scripts/sync_agent_instructions.sh --help` は成功した。
- `./scripts/sync_agent_instructions.sh --help` は成功した。
- `./scripts/sync_agent_instructions.sh` は成功し、git diff は発生しなかった。
- `bash ./scripts/sync_agent_instructions.sh` は成功し、git diff は発生しなかった。
- `pwsh -File scripts/sync_agent_instructions.ps1 -Help` は成功した。
- active docs / instructions / user-level skill 導線に対する `docs/procedure`、`instructions/skills`、`rebuild_user_agent_skills.py`、`sync_agent_skills` の検索では、削除済み経路への実運用依存は確認されなかった。
- `docs/design_analysis/` 配下の過去文書には旧 path が残っているが、今回の report の補足どおり履歴文脈として扱える範囲と判断した。
- `diff scripts/sync_agent_instructions.sh user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh`: 差分なし。
- `diff instructions/agent_sync_guide.md user-agent-assets/skills/project-doc-bootstrap/templates/common/instructions/agent_sync_guide.md`: 差分なし。

## 総評

責務境界の整理自体は、`user-agent-assets/skills/*/references/procedure/` を正本とする方針に沿っている。root docs / generated instructions / sync source の関係も概ね一貫している。

ただし、追加された root shell script の file mode だけが template 側および README / sync guide の実行例と食い違っているため、修正後に再確認するのがよい。
