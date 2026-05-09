# project-level instruction 整理 変更要約

## 背景

project-level instructions の再初期化後、生成物である `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の冒頭に、同期元ファイル自体の説明が残っていた。あわせて、workflow skills が user-level 正本へ格上げされた後も root に `docs/procedure/` と `instructions/skills` 系の重複資産が残っており、保守対象の境界が曖昧だった。

## 今回の変更

### 1. root agent instructions の導入文を project 説明へ修正

- `instructions/agent_common_master.md` の冒頭を、sync source 自体の説明から project 概要説明へ置き換えた
- `bash ./scripts/sync_agent_instructions.sh` により `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` を再同期した

### 2. root の重複 workflow 資産を削除

- root `docs/procedure/` 一式を削除した
- root `instructions/skills/` は削除済みとし、再導入しない方針へ整理した
- 旧再生成経路 `scripts/rebuild_user_agent_skills.py` を削除した

### 3. root docs を user-level 正本前提へ修正

- `README.md`
- `docs/rules/project_overview.md`
- `docs/architecture/overview.md`
- `docs/rules/development_workflow.md`
- `docs/rules/README.md`

上記を更新し、workflow 手順の正本を `user-agent-assets/skills/*/references/procedure/` として扱う前提へ揃えた。

### 4. template 側改善は follow-up へ分離

- `C-2026-009` を追加し、bootstrap 後の `instructions/agent_common_master.md` に project 固有説明を補助する改善を追跡対象にした
- template 側 `agent_common_master.md` の文面変更はロールバックし、今回の commit には含めていない

## 主な変更ファイル

- `instructions/agent_common_master.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `README.md`
- `docs/architecture/overview.md`
- `docs/rules/project_overview.md`
- `docs/rules/development_workflow.md`
- `docs/rules/README.md`
- `docs/issues/cross/issues.md`
- 削除: `docs/procedure/**`
- 削除: `scripts/rebuild_user_agent_skills.py`

## 検証

- `bash ./scripts/sync_agent_instructions.sh`
- active docs / generated instructions に対する grep で、`docs/procedure/`、`instructions/skills/`、`rebuild_user_agent_skills.py` の参照が残っていないことを確認
- root / template の更新対象に対して Problems 0 件を確認

## レビュー後の追加修正

- `scripts/sync_agent_instructions.sh` に実行権限を付与し、README / sync guide の直接実行導線と一致させた
- shell 版 `--help` のオプション行インデントを他 OS 向け script と揃えた
- `instructions/agent_sync_guide.md` に `--all` / `-All` の実行例とオプション説明を追加した
- `instructions/agent_common_master.md` の Python / C# 同期方針を双方向の表現へ揃えた
- 追加検証として `./scripts/sync_agent_instructions.sh --help` と `./scripts/sync_agent_instructions.sh` の直接実行を確認する
- follow-up review の指摘に対応し、`user-agent-assets/skills/project-doc-bootstrap/templates/common/` 配下の `scripts/sync_agent_instructions.sh` と `instructions/agent_sync_guide.md` へ同じ修正を横展開した
- root と template common の対応ファイルに対して `diff` を実行し、差分が空であることを確認する

## レビュー観点

1. root `agent_common_master.md` の導入文が、生成物として読まれた時にノイズなく project 概要になっているか
2. `docs/procedure/` と旧再生成 script の削除後、active docs / instructions / review 導線に root 依存が残っていないか
3. template 側改善を `C-2026-009` へ分離した判断が妥当か
4. user-level skill 正本と root docs の責務境界が、今回の修正で明確になっているか

## 補足

履歴文書や過去レビュー文書には、当時の文脈を保持するため `docs/procedure/` などの旧 path が残っている。今回は active docs / active instructions / 実運用導線の整理を対象とし、履歴文書の全面書換は行っていない。