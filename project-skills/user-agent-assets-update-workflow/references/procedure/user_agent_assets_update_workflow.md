# User agent assets update workflow

## 適用条件

- AgenticProjectTemplates の `user-agent-assets/` 配下を更新する
- user-level skill、review/orchestration workflow、runtime、installer、bootstrap template の配布結果に影響する
- 更新後に `~/.codex` / `~/.claude` / `~/.copilot` / `~/.agents` / `~/.agentic-project-templates` へ実インストールする可能性がある

## 成果物

- 作業 branch: `user-agent-assets/<topic>-<yyyymmdd>` など
- design analysis: `docs/design_analysis/spec_change/<yyyymmdd>_<topic>/`
- 必須ファイル: `meta.md`, `design/<topic>_design.md`, `impl/<topic>_impl.md`, `change_report.md`
- review 文書: Claude または Copilot CLI が `review/` 配下へ作成・更新する

## Phase 一覧

| Phase | 目的 | 主な出力 |
|---|---|---|
| 0 | 依頼整理 | 変更目的、対象 asset、非対象、STOP ゲート |
| 1 | branch・meta 初期化 | 専用 branch、design analysis topic |
| 2 | 変更方針・影響範囲レビュー | design、影響範囲表、方針レビュー |
| 3 | 実装・実装レビュー | user-agent-assets 変更、docs 更新、実装レビュー |
| 4 | dry-run・仮インストール | dry-run log、tmp 仮インストール検証結果 |
| 5 | 実インストール | ユーザ承認、実インストール結果、post-check |
| 6 | 完了処理・merge | change_report、history、merge 承認 |

## Phase 詳細

### Phase 0: 依頼整理

- 変更目的、期待する利用者、対象 asset を固定する
- 影響対象を分類する
  - `skills`
  - `install`
  - `bin`
  - `runtime`
  - `shared`
  - `project-doc-bootstrap/templates`
- 変更しない範囲を明記する
- 実インストールと merge は STOP ゲートとしてユーザ承認を必須にする

### Phase 1: branch・meta 初期化

- 対象プロジェクトの既定ブランチを最新化する
- 専用 branch を作成する
- `docs/design_analysis/spec_change/<yyyymmdd>_<topic>/` を作成する
- `meta.md` には最低限次を記載する
  - `title`
  - `created_date`
  - `category: spec_change`
  - `components`
  - `status`
  - `design_status`
  - `impl_status`
  - `verification_status`
  - `completion_status`
  - `related_commits`

Phase 完了時は `[PHASE_COMPLETE: 1]` を出力する。

### Phase 2: 変更方針・影響範囲レビュー

- 既存 skill、installer、runtime、template の構成を確認する
- 次の影響範囲表を design に残す

| 項目 | 記載内容 |
|---|---|
| changed_assets | 変更する `user-agent-assets/` 配下 |
| install_targets | `codex` / `claude` / `copilot` / `.agents` / helper runtime |
| compatibility | 既存 installed assets への上書き影響 |
| validation | dry-run、tmp install、quick validate、script syntax check |
| user_gates | 実インストール前、merge 前 |

- skill を新規作成する場合は `skill-creator` を使う
- 方針がまとまったら Claude または Copilot CLI へレビューを依頼する
- レビュー指摘は `ai-review-response-workflow` に従って反映し、未解決指摘 0 件まで回す

Phase 完了時は `[PHASE_COMPLETE: 2]` を出力する。

### Phase 3: 実装・実装レビュー

- 変更内容に応じて user-agent-assets、関連 docs、検証 script を更新する
- `project-skills/` 配下の project-local skill を更新した場合は、discovery path へ同期する

```bash
./scripts/sync_project_skills.sh --all
```

- skill 更新時は次を確認する
  - `SKILL.md` frontmatter の `name` / `description`
  - `references/` の参照が `SKILL.md` から辿れること
  - `scripts/` を追加した場合は実行確認
  - `quick_validate.py <skill-dir>`
- installer / shell script 更新時は `bash -n` を実行する
- Python script 更新時は `python3 -m py_compile` を実行する
- 実装後に Claude または Copilot CLI へ実装レビューを依頼し、未解決指摘 0 件まで回す

Phase 完了時は `[PHASE_COMPLETE: 3]` を出力する。

### Phase 4: dry-run・仮インストール

1. installer dry-run を実行する

```bash
bash user-agent-assets/install/install_user_agent_assets.sh \
  --dry-run \
  --mode overwrite \
  --targets copilot,claude,codex \
  --source-root user-agent-assets
```

2. `tmp/` へ仮インストールする

```bash
python3 project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py \
  --source-root user-agent-assets \
  --temp-root tmp/user-agent-assets-install-check \
  --targets copilot,claude,codex \
  --mode overwrite \
  --clean \
  --forbid-skill user-agent-assets-update-workflow
```

3. 実行結果で最低限次を確認する
   - install script が成功している
   - 各 target の skill 数が source と一致している
   - 更新対象 skill が source と一致している
   - project-local skill が user-level install 対象に含まれていない
   - `project-doc-bootstrap/templates` の更新が target に展開されている
   - helper runtime が `.agentic-project-templates/` に展開されている

仮インストール結果をユーザへ報告し、実インストール可否を確認する。承認待ちでは `[NEED_USER_VERIFICATION]` を出力する。

### Phase 5: 実インストール

- ユーザが承認した場合だけ実インストールする

```bash
bash user-agent-assets/install/install_user_agent_assets.sh \
  --mode overwrite \
  --targets copilot,claude,codex \
  --source-root user-agent-assets
```

- 実インストール後は、更新対象 skill / helper runtime / template の存在と差分を確認する
- 実インストール結果を `change_report.md` に記録する

Phase 完了時は `[PHASE_COMPLETE: 5]` を出力する。

### Phase 6: 完了処理・merge

- `change_report.md` に次を記録する
  - 変更ファイル
  - レビュー結果
  - dry-run 結果
  - tmp 仮インストール結果
  - 実インストール結果
  - 未実施項目と理由
- `docs/history/change_history_<year>.md` を更新する
- 必要に応じて `docs/todo/todo.md` を archive する
- 最終 commit を作成する
- merge 前にユーザへ「マージしてよいですか」と確認する
- ユーザ承認後、既定ブランチへ merge する

merge 完了時は `[ALL_PHASES_COMPLETE]` を出力する。

## 完了条件

- user-agent-assets の変更が source と実インストール先で一致している
- review 指摘が未解決 0 件である
- dry-run と tmp 仮インストールが成功している
- 実インストールはユーザ承認後に実施され、結果が記録されている
- merge はユーザ承認後に実施されている
