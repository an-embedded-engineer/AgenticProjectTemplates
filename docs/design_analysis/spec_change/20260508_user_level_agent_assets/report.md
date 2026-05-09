# SC-20260508-001 Phase 6 差分レポート

## 対象

- issue: `SC-20260508-001`
- topic: `ユーザレベル Agent 資産化`
- branch: `feature/spec-user-level-agent-assets-20260508`
- compare_base_branch: `main`
- merge_base: `61c9863801734cef6dd4893129e8d1683aca4390`
- target_head: `working tree (HEAD=8259889)`

## 収集方法

Phase 6 の完了処理に向けて、以下のコマンドで main との差分を working tree 基準で収集した。

```bash
git merge-base main HEAD
git diff --stat $(git merge-base main HEAD)
git diff --name-only $(git merge-base main HEAD)
```

`phase_6_completion.md` では `master` 基準の記載になっているが、この repository の default branch は `main` のため、比較基準は `main` に読み替えた。

## 差分サマリ

- 変更ファイル数: `298`
- 追加行数: `4986`
- 削除行数: `8273`

## 主な変更グループ

### 1. 仕様変更の計画・設計・レビュー成果物

- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/` に plan、design、meta、review 群、improvement memo を追加・更新した
- Phase 2 / 3 / 4 / 5 のレビュー文書と、PowerShell 検証・follow-up issue 化、Phase 6 cleanup までの記録を揃えた

### 2. 追跡管理文書

- `docs/todo/todo.md` を Phase 5 完了状態へ更新した
- `docs/issues/cross/issues.md` に `C-2026-001` 〜 `C-2026-008` の follow-up issue を追加した
- `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md` を staged migration 方針に合わせて更新した

### 3. user-level assets の導入基盤

- `user-agent-assets/install/` に shell / PowerShell installer と README を追加した
- `user-agent-assets/bin/` に Agent CLI tmux wrapper を追加した
- `user-agent-assets/runtime/agent-cli-tmux/` に Python runtime と Windows 向け runtime placeholder README を追加した
- `scripts/rebuild_user_agent_skills.py` を追加し、skills 再生成と manual skill 保全の仕組みを整備した

### 4. 旧 project-level assets と template ディレクトリの撤去

- root / template の旧 `instructions/`、`scripts/sync_agent_skills.*`、`docs/rules/skill_catalog.md`、repo-local `.github/skills/` / `.claude/skills/` を削除した
- `python-project-template/` と `csharp-project-template/` を撤去し、repo の責務を user-level assets と bootstrap 資産の保守へ揃えた
- 旧 template にあった共通保守ツールを `user-agent-assets/runtime/` と `project-doc-bootstrap/templates/*/tools/` へ再配置し、test runner は root `tests/` へ集約した
- 追加実装記録として `impl/user_level_agent_assets_impl.md` を作成し、最終配置判断と system-dotnet-only validation の前提を整理した

### 5. workflow / review skills の user-level 正本化

- `user-agent-assets/skills/` に workflow / review / orchestrator skills を追加した
- 各 skill で `references/procedure/` を同梱し、project-level `docs/procedure/` 依存を外す方向へ整理した
- `copilot-review-automation`、`claude-review-automation`、`ai-review-response-workflow` などの review 系 skill を user-level assets 側へ集約した
- `copilot-review-automation/SKILL.md` の frontmatter `description` は YAML block scalar へ修正し、Copilot CLI 起動時の skill load error を解消した

### 6. project-doc-bootstrap と project-level docs 雛形

- `user-agent-assets/skills/project-doc-bootstrap/` に shell / PowerShell wrapper、reference、Python / C# 向け template 群を追加した
- `instructions/agent_common_master.md`、`agent_sync_guide.md`、`scripts/sync_agent_instructions.*` を target project へ配布する staged migration 契約を実装した
- placeholder scan を docs だけでなく instructions と生成済み Agent 文書まで拡張した

## 変更ファイルの代表例

- `.gitignore`
- `scripts/rebuild_user_agent_skills.py`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/meta.md`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/report.md`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_claude.md`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_codex.md`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_docs_review.md`
- `docs/issues/cross/issues.md`
- `docs/todo/todo.md`
- `user-agent-assets/runtime/agent-cli-tmux/csharp/AgentCliTmux/`
- `user-agent-assets/skills/project-doc-bootstrap/templates/python/tools/extract_git_diff.py`
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff/`
- `tests/test_agent_cli_tmux.py`
- `tests/test_extract_git_diff.py`
- `tests/AgentCliTmux.Tests/`
- `user-agent-assets/install/install_user_agent_assets.sh`
- `user-agent-assets/install/install_user_agent_assets.ps1`
- `user-agent-assets/skills/project-doc-bootstrap/SKILL.md`
- `user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.sh`
- `user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.ps1`
- `user-agent-assets/skills/copilot-review-automation/SKILL.md`

## 検証の要約

本 branch では Phase 5 までに以下を確認済みである。

- shell / PowerShell の bootstrap、sync、installer dry-run
- 実ユーザールートへの install と wrapper 実行権限
- fake HOME への clean install で runtime 直下に不要な `win-x64` が再生成されないことと、実ユーザールートでも `--mode overwrite` により stale な `win-x64` を除去できること
- 新規 Python サンプルプロジェクトでの `project-doc-bootstrap`、`copilot-review-automation`、`new-feature-workflow` 実地検証
- Phase 5 docs review と follow-up review の承認
- repo root へ移設した Python files の `py_compile`
- repo root へ移設した C# tool / test runner の `dotnet build`
- system `dotnet` による `dotnet run --project tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj` の成功
- repo-local `.dotnet9` 削除後も同 test runner が成功すること
- `copilot-review-automation` の source / install 済み `SKILL.md` frontmatter が YAML parse できることと、ユーザ確認で Copilot CLI 起動時の skill load error が消えたこと

## 補足

- 本レポートは merge 前の working tree 状態を記録するものであり、merge commit、archive、history 更新は含まない
- merge 後は Phase 6 手順に従い、`meta.md` の `status=merged` 更新、todo archive、history 反映を別途実施する