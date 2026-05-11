---
title: "user-agent-assets-update-workflow skill 実装レビュー"
phase: "impl"
reviewer: "Claude Opus 4.7"
reviewed_at: "2026-05-12"
approved_at: "2026-05-12"
review_target_commit: "9c40c1d Add project-local user agent assets workflow"
response_target_commit: "b66a35e Address user agent assets workflow review"
status: "approved"
unresolved_major: 0
unresolved_moderate: 0
unresolved_minor: 0
response_status: "complete"
---

# user-agent-assets-update-workflow skill 実装レビュー

## 1. レビュー範囲

- 対象コミット: `9c40c1d Add project-local user agent assets workflow`
- 対象 topic: `docs/design_analysis/spec_change/20260511_user_agent_assets_update_workflow_skill/`
- 主要対象:
  - `project-skills/user-agent-assets-update-workflow/{SKILL.md, references/procedure/user_agent_assets_update_workflow.md, scripts/validate_temp_install.py}`
  - `scripts/sync_project_skills.{sh,ps1,bat}`
  - `.gitignore`
  - `README.md`
  - `docs/history/change_history_2026.md`
  - topic 配下の `meta.md` / `design/` / `impl/` / `change_report.md`

## 2. 観点別判定

### 2.1 配置の妥当性（観点 1）

- `project-skills/user-agent-assets-update-workflow/` は `user-agent-assets/skills/` とは別の正本ツリーに収められている。
- `user-agent-assets/install/install_user_agent_assets.sh` は `${SOURCE_ROOT}/skills` だけを参照し、`project-skills/` を読み取らない構造であることを確認した。`--source-root user-agent-assets` でドライランしても `user-agent-assets-update-workflow` が install 対象に含まれない設計と整合する。
- SKILL.md / 手順本体・README いずれも「project-local 専用」「user-level install 対象外」を明示しており、設計意図は文書化されている。
- 判定: 妥当。

### 2.2 sync スクリプトの責務分離（観点 2）

- `scripts/sync_project_skills.{sh,ps1,bat}` は `project-skills/` → `.github/skills` / `.claude/skills` / `.codex/skills` のみを扱う。`scripts/sync_agent_instructions.*` は skill ディレクトリを一切操作しない（`grep` 確認済み）。責務分離は守られている。
- shell 版は `set -euo pipefail`、ps1 版は `Set-StrictMode -Version Latest` と `$ErrorActionPreference="Stop"`、bat 版は各 `errorlevel` チェックで早期失敗するよう書かれている。
- target ディレクトリは毎回 `rm -rf` してから再生成する破壊的同期で、未知のファイルが残らない設計。`.gitignore` で同期先を ignore しているため、誤って手書き編集を残しても黙って消えるリスクが避けられている。
- 判定: 妥当。ただし「README が bash 版だけ案内している」点は 2.4 Minor で指摘。

### 2.3 `validate_temp_install.py` の検証強度（観点 3）

- `TARGET_SKILL_ROOTS` で copilot=`{.copilot/skills, .agents/skills}`、claude=`{.claude/skills}`、codex=`{.codex/skills}` を網羅し、installer の出力先と一致している。
- 各 target につき (a) skill set 完全一致、(b) source ファイル存在＋内容一致（`filecmp.cmp(... shallow=False)`）、(c) `--forbid-skill` の混入チェック、(d) `--exact-skill` 指定 skill のみ余剰検出を実施。
- helper runtime は `.agentic-project-templates/{bin,instructions,runtime/agent-cli-tmux}` の存在と shell wrapper の実行ビット、source との byte 一致を確認しており、必要十分。
- `resolve_paths` で `temp_root.is_relative_to(repo_root)` を `--clean` 時に強制し、リポジトリ外を誤消去しない安全策がある。
- `--forbid-skill user-agent-assets-update-workflow` は混入検知に有効。なお、set 一致チェックでも `extra=[...]` に出るため二重防衛だが、専用フラグの方がエラー文が明示的で運用上有用。
- 判定: 仮インストール検証として十分。

### 2.4 ドキュメント整合（観点 4）

- README は `project-skills/` を directory 表・directory tree・専用セクションに追加し、生成物 (`.github/skills/`、`.claude/skills/`、`.codex/skills/`) と正本の境界を明示している。
- `docs/history/change_history_2026.md` は配布対象外である旨を含めて記述しており、ドキュメント整合は概ね良好。
- 残課題は `meta.md` の `components` 記載（Moderate 1 を参照）と Minor 指摘群。

### 2.5 `.gitignore`（観点 5）

- root 直下 `/.claude/skills/`、`/.codex/skills/`、`/.github/skills/` を追加し、`sync_project_skills.*` の出力を ignore している。
- コメントも `sync_agent_instructions.* and sync_project_skills.*` に更新済み。
- 残課題は Minor 1 を参照（`*/.codex/skills/` パターンの欠落）。

## 3. 指摘事項

### Moderate

#### M-1: `meta.md` の `components` に未変更パスが残っている

- 場所: `docs/design_analysis/spec_change/20260511_user_agent_assets_update_workflow_skill/meta.md` L4-9
- 現状:
  ```yaml
  components:
    - project-skills/user-agent-assets-update-workflow
    - user-agent-assets/skills/wbs-planning-workflow
    - README.md
    - docs/history/change_history_2026.md
  ```
- 問題: コミット `9c40c1d` の `git show --stat` には `user-agent-assets/skills/wbs-planning-workflow` 配下の変更は存在しない。設計書 `design/user_agent_assets_update_workflow_design.md` の「WBS 連携」節も「`wbs-planning-workflow` には追加しない」という非追加の判断を述べているだけで、当該 skill を変更した記録ではない。`components` は実際に変更したコンポーネントの索引として読まれるため、未変更パスを残すと後続のレビューや archive 作業で誤読される。
- 修正案: `components` を実変更ファイルへ揃える。例:
  ```yaml
  components:
    - project-skills/user-agent-assets-update-workflow
    - scripts/sync_project_skills.sh
    - scripts/sync_project_skills.ps1
    - scripts/sync_project_skills.bat
    - .gitignore
    - README.md
    - docs/history/change_history_2026.md
  ```
  「wbs-planning-workflow に追加しない」決定は設計書側に既に記載済みのため、components から外しても情報は失われない。

### Minor

#### m-1: `.gitignore` で `*/.codex/skills/` パターンが欠落している

- 場所: `.gitignore` L57-66
- 状況: 既存パターン `*/.claude/skills/` と `*/.github/skills/` は subdirectory 配下の生成 skills を ignore するが、`*/.codex/skills/` は無い。今回 root 直下に `.codex/skills/` を追加したことで、target trio (`.github`/`.claude`/`.codex`) の扱いが root レベルでは揃ったが、`*/` 系の subdirectory 扱いだけ codex が抜けている。
- 影響: 現状の sync スクリプトは root 直下にしか書き込まないため即時バグは無いが、将来 bootstrap target や integration ディレクトリで `.codex/skills/` が生成された場合に追跡対象に混入する。
- 修正案: 既存パターン群と同列に `*/.codex/skills/` を追加するか、または subdir 用パターンを意図的に外している理由をコメントで残す。

#### m-2: `change_report.md` を Phase 3 コミットに含めるか Phase 6 まで保留するかの整合

- 場所: `docs/design_analysis/spec_change/20260511_user_agent_assets_update_workflow_skill/change_report.md`
- 状況: `references/procedure/user_agent_assets_update_workflow.md` の Phase 6 では `change_report.md` に「変更ファイル、レビュー結果、dry-run 結果、tmp 仮インストール結果、実インストール結果、未実施項目と理由」を記録すると定義しているが、本コミットでは Phase 3 段階で実インストール前の検証ログだけを書いた状態で `change_report.md` が作成・コミットされている。
- 影響: Phase 6 で再度上書きすることになり、commit 履歴上は「Phase 3 で完了したレポート」と誤読される可能性がある。
- 修正案: いずれかで揃える。
  - (a) Phase 3 では `change_report.md` を作成せず、検証ログは `impl/` 文書または `verification/` 等の作業文書に置き、Phase 6 で初めて `change_report.md` を作成する。
  - (b) 現状を維持する場合は `change_report.md` 冒頭に「Phase 3 時点の検証中間結果。実インストール結果と最終承認は Phase 6 で追記する」旨を明記する。

#### m-3: README が `sync_project_skills` を bash 版のみ案内している

- 場所: `README.md` の "Project-local maintenance skills" 節
- 状況: 既存 `instructions/agent_sync_guide.md` や `scripts/sync_agent_instructions.*` は Windows/PowerShell 版にも触れる体裁が多いが、新セクションは `./scripts/sync_project_skills.sh --all` のみ。
- 修正案: PowerShell (`scripts/sync_project_skills.ps1 -All`) と batch (`scripts\sync_project_skills.bat --all`) も併記する。または `instructions/agent_sync_guide.md` 側へリンクし sync 詳細は集約する。

#### m-4: `validate_temp_install.py` の冗長な検査の意図をコメントで残す

- 場所: `project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py` `validate_skill_targets`
- 状況: `installed_names != source_names` で extras が検出される一方、`--forbid-skill` 専用判定でも同じ skill を捕捉する。重複検査は意図的（明示的なエラー文）と判断したが、コード上は同一条件に二度落ちる可能性があるためレビュー時に「意図された冗長」と分かりにくい。
- 修正案: `--forbid-skill` 判定の前後に 1 行コメントで「set diff より先に forbid 専用判定で明示的に失敗させる」旨を書き添える、または `--forbid-skill` 判定でエラー後 `return` ではなく `fail` で確実に終わっている既存挙動を docstring に追記する。

## 4. その他の確認

- ワーキングツリーに `.gitignore` の追加変更（末尾 `__pycache__/`、行頭 `__pycache__/` と重複）が unstaged で残っている。これは本コミットの対象外だが、レビュー実行時には残置状態だったため留意点として記録する。レビュー時点ではコミットすべきかは未確定。
- `quick_validate.py` の合格、`bash -n`、PowerShell dry-run、`diff -qr`、tmp 仮インストール、installer dry-run など `change_report.md` 記載のチェックは網羅されている。
- shell / ps1 / bat いずれも `--all` 既定動作と target 引数組み合わせを揃えており、CRLF / 引用問題は見当たらない。

## 5. 結論

- Major 指摘なし。
- Moderate 指摘 1 件（M-1: `meta.md` `components` 修正）の反映を必須とする。
- Minor 4 件は反映を推奨するが、Phase 3 完了の阻害要因ではない。
- 上記 M-1 反映後、`impl_status=done` の維持と Phase 4-a 承認待ちへの遷移を推奨する。

## 6. 指摘対応状況

| ID | status | 対応 |
|---|---|---|
| M-1 | done | `meta.md` の `components` を実変更ファイルへ揃え、未変更の `user-agent-assets/skills/wbs-planning-workflow` を除外した |
| m-1 | done | `.gitignore` に `*/.codex/skills/` を追加し、subdirectory 配下の `.github` / `.claude` / `.codex` skill 生成物の扱いを揃えた |
| m-2 | done | `change_report.md` 冒頭に Phase 3 時点の検証中間結果であり、実インストール結果・最終承認・merge 結果は Phase 6 で追記する旨を明記した |
| m-3 | done | README の project-local skill sync 案内に PowerShell 版と Windows cmd 版を追記した |
| m-4 | done | `validate_temp_install.py` の `--forbid-skill` 判定に、generic set-diff より先に専用メッセージで失敗させる意図をコメントで残した |

補足: レビュー時点で記録された `.gitignore` の未ステージ差分は、重複した `__pycache__/` 行であり、対応前に削除して作業ツリーを clean に戻した。

## 7. 最終承認

- 承認者: Claude Opus 4.7（レビュー担当 Agent）
- 承認日: 2026-05-12
- 対応コミット: `b66a35e Address user agent assets workflow review`
- 確認内容:
  - M-1: `meta.md` の `components` から `user-agent-assets/skills/wbs-planning-workflow` が除外され、実変更ファイル（`scripts/sync_project_skills.{sh,ps1,bat}`、`.gitignore`）に揃っている。`related_commits` も初回実装・レビューの 2 件が追記されている。
  - m-1: `.gitignore` L63 に `*/.codex/skills/` が追加され、subdirectory 配下 3 target の対称性が回復している。
  - m-2: `change_report.md` 冒頭に「Phase 3 時点の検証中間結果。実インストール結果・最終承認・merge 結果は Phase 6 で追記」の注記が入っている。
  - m-3: README の project-local maintenance skills 節に PowerShell (`pwsh -File scripts/sync_project_skills.ps1 -All`) と Windows cmd (`scripts\sync_project_skills.bat --all`) の実行例が追記されている。
  - m-4: `validate_temp_install.py` `validate_skill_targets` の `--forbid-skill` 判定直前に「Fail with a dedicated message before the generic set-diff check.」コメントが入り、二重防衛の意図が明示されている。
- 判定: 未解決指摘 0 件で承認。`impl_status=done` を維持し、Phase 4-a のユーザ動作確認へ進める。
