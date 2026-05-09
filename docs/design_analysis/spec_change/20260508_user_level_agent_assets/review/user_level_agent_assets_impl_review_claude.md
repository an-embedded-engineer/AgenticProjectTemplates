---
title: "ユーザレベル Agent 資産化 Phase 4 実装レビュー（Claude）"
created_date: "2026-05-09"
category: spec_change_impl_review
target_design: docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md
target_plan: docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md
target_meta: docs/design_analysis/spec_change/20260508_user_level_agent_assets/meta.md
target_branch: feature/spec-user-level-agent-assets-20260508
target_worktree_state: untracked working tree（commit 8522b8f 時点 + 未コミットの user-agent-assets/ と scripts/rebuild_user_agent_skills.py）
status: review_findings
---

# レビュー文書: ユーザレベル Agent 資産化 Phase 4 実装

## 1. レビュー概要

- 観点
  - 移行先 `user-agent-assets/` のディレクトリ構造・正本配置が承認済み設計に整合しているか
  - workflow skill `references/` の payload が設計 Section 7 の dependency map に一致しているか
  - install / sync スクリプトの I/F と shared common hydrate の挙動が設計通りか
  - 既存の `instructions/`、`skills/`、`docs/` から user-agent-assets への参照経路に破壊がないか
  - 配布資産そのものが正しく git 管理 / インストールされる状態になっているか
- 参照文書
  - 設計書: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md`
  - 設計レビュー: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_design_review.md`
  - 計画書: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md`
  - 調査レポート: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
- 対象ツリーの状況
  - `user-agent-assets/` は丸ごと untracked。`scripts/rebuild_user_agent_skills.py` も untracked
  - `meta.md` の `impl_status` は `not_started`。実装作業途中の中間レビューと位置付ける
  - root / template の `instructions/`、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`、`docs/procedure/`、`docs/rules/skill_catalog.md` には未着手
- 結果サマリ
  - 正本ディレクトリ・install スクリプト・core workflow skill の `references/` 化と shared common hydrate は設計通りに成立している
  - 設計に記載されたままの suite skill payload（5 workflow 一括同梱）は、ユーザ指示で「他 skill との同時 install を前提に procedure コピーを廃し、SKILL.md から同名 skill を案内する」方針へ転換された。実装はその新方針に追従済みだが、設計書（Section 7.2 / 7.3 / 7.4）が旧方針のままであり、設計と実装の乖離は **設計書の未反映** として扱う必要がある（Design-Doc-Update-1 で詳述）
  - current phase の project-level 導線は `project-doc-bootstrap` が target project へ docs 雛形、`agent_common_master.md`、`agent_sync_guide.md`、project-level sync script をコピーする方式へ更新した。repo 直下 / 既存 template の ripple は移行完了後の follow-up とする
  - `bin/` ディレクトリが既存 `.gitignore` の `bin/` ルールに巻き込まれており、コミット時に wrapper が消失する致命的な問題がある
- 総合判定: Critical 1 / High 3 / Medium 5 / Low 4 / Design-Doc Update 1（旧 High-3 を分離）
- 再検証後の判定（2026-05-09 Claude 再検証・方針更新反映）: 当初 Critical 1 / High 3 / Medium 5 / Design-Doc-Update 1 のうち Critical-1 と High-1 / High-3 / Medium 1〜5 / Design-Doc-Update-1 を解消。High-2 は repo 直下 / 既存 template を即時変更する項目ではなく、`project-doc-bootstrap` を起点に target project へ project-level files を配る staged migration へ設計更新したため、current phase の blocking から外した。現時点の残課題は `pwsh` 不在による PowerShell 実行検証未了と、Low-1 / Low-2 / Low-4 の非 blocking 項目のみ。
- 再々検証後の判定（2026-05-09 Claude、コミット `c2334032f...`）: 当初指摘した Critical-2 と Low-5 をいずれも解消（REPLACEMENT_GUARDS による wrapper path 保護 + 境界付き session 名置換、設計書 Section 7.4 の残骸削除）。新規発見は Low-6 / Low-7 / Low-8（placeholder scan の scope、PowerShell 動作検証、sync 上書き告知）でいずれも non-blocking。**Phase 5 smoke test へ進める状態と判断する**

  ## 1.1 対応状況（2026-05-09 更新）

  | finding | 状況 | 対応メモ |
  |---|---|---|
  | Critical-1 | 対応済み | `.gitignore` へ `user-agent-assets/bin/**` と `user-agent-assets/skills/*/bin/**` の negation を追加し、wrapper を commit 対象へ戻した |
  | High-1 | 対応済み | `project-doc-bootstrap` を実装し、`workflow_selection.md` は削除して `common_agent_principles.md` の参照も整理済み |
  | High-2 | 方針更新で current phase 対象外 | repo 直下 / 既存 template は移行完了まで無変更とし、`project-doc-bootstrap` が target project へ docs、`agent_common_master.md`、`agent_sync_guide.md`、project-level sync script をコピーする staged migration へ設計を更新した |
  | Design-Doc-Update-1 | 対応済み | 設計書 Section 6.1 / 7.2 / 7.3 / 7.4 を suite skill slim payload 方針へ更新した |
  | High-3 | 対応済み | shared shell wrapper の source 実行ビット付与と install 時 `chmod 755` を追加した |
  | Medium-1 | 対応済み | `workflow_selection.md` 残置をやめ、standalone skill 化もしない方針に合わせた |
  | Medium-2 | 対応済み | generated `SKILL.md` の project-level docs 直接参照を一般化し、project 固有 rules path を除去した |
  | Medium-3 | 対応済み | Windows wrapper を exe 優先 + Python fallback に変更し、現 payload と整合させた |
  | Medium-4 | 対応済み | generator 側で project 固有 wording と固定検証文言を汎化した |
  | Medium-5 | 対応済み | `scripts/rebuild_user_agent_skills.py` に runtime helper 同期処理を追加した |

  備考:

  - `pwsh` がローカルに無いため、PowerShell 実行系の実検証は未了

  ## 1.1.1 追加指摘対応後の要約（2026-05-09 更新）

  - High-2: repo 直下 / 既存 template を先に触らず、`project-doc-bootstrap` を起点に target project へ project-level docs / instructions / sync script を配る staged migration へ設計更新した
  - Critical-2: `rebuild_user_agent_skills.py` の過大置換を廃止し、wrapper install path を保護したうえで session 名だけを短縮するよう修正した
  - Low-5: 設計書 Section 7.4 の `workflow_phase_library/README.md` 残骸を `suite skill には workflow_phase_library を追加配置しない` へ修正した
  - `project-doc-bootstrap` から `skill_catalog.md` と repo local skill 参照を除去し、target docs reference を user-level skill 前提へ整理した
  - 隔離した Python target project で `copy_doc_templates.sh` -> `sync_agent_instructions.sh --help` -> `sync_agent_instructions.sh` を通し、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の再生成まで確認した

  ## 1.2 対応状況の独立検証（2026-05-09 Claude 再検証）

  対象コミット: `5d200dcac387f9b58b192cb20935d90f17b6c49b`（"Finalize user-level agent assets hardening"） + `d115d62`（"Add user-level agent assets foundation"）。

  | finding | 申告 | 検証結果 | 検証根拠 |
  |---|---|---|---|
  | Critical-1 | 対応済み | ✅ 確認 | `.gitignore` に negation 4 行（`!user-agent-assets/bin/`、`!user-agent-assets/bin/**`、`!user-agent-assets/skills/*/bin/`、`!user-agent-assets/skills/*/bin/**`）が追加され、`git check-ignore -v user-agent-assets/bin/agentic-agent-cli-tmux.sh` は ignore せず。`git ls-files user-agent-assets/bin/` で `.sh` / `.ps1` が tracked。`project-doc-bootstrap/bin/` も tracked |
  | High-1 | 対応済み | ✅ 確認 | `user-agent-assets/skills/project-doc-bootstrap/{SKILL.md,bin/,references/,templates/}` 一式が追加。`templates/python/docs/` と `templates/csharp/docs/` の雛形も配置。`user-agent-assets/instructions/workflow_selection.md` は削除済み。`common_agent_principles.md` の参照は `インストール済み workflow skill の SKILL.md` に置換 |
  | High-2 | 方針更新 | ✅ 確認 | current phase は repo 直下 / 既存 template を変更せず、`project-doc-bootstrap` を起点に target project へ docs、`instructions/agent_common_master.md`、`instructions/agent_sync_guide.md`、project-level sync script をコピーする flow へ設計更新した |
  | Design-Doc-Update-1 | 対応済み | ✅ 確認 | Section 6.1 / 7.2 / 7.3 / 7.4 は新方針へ更新済みで、Section 7.4 の `workflow_phase_library/README.md` 残骸も削除済み |
  | High-3 | 対応済み | ✅ 確認 | `install_user_agent_assets.sh:88-99` に `ensure_shell_wrapper_executable` を追加し `chmod 755` を実行。`install_user_agent_assets.sh:174` で helper bin にも適用。source 側の `user-agent-assets/bin/agentic-agent-cli-tmux.sh` も `-rwxr-xr-x`。`bash install_user_agent_assets.sh --dry-run` 出力に `[dry-run] chmod 755 ...` を確認 |
  | Medium-1 | 対応済み | ✅ 確認 | `user-agent-assets/instructions/` は `common_agent_principles.md` と `language_policy.md` のみ。設計 Section 4.1 のディレクトリ規定と一致 |
  | Medium-2 | 対応済み | ✅ 確認 | `rebuild_user_agent_skills.py:rewrite_text` で `docs/rules/coding_rules.md` → `各プロジェクトのコーディング規約`、`docs/rules/development_workflow.md` → `各プロジェクトの開発・検証コマンド定義` に置換。生成 `SKILL.md` を grep しても旧 path は残っていない |
  | Medium-3 | 対応済み | ✅ 確認 | `bin/agentic-agent-cli-tmux.ps1` が `AgentCliTmux.exe` 優先 → `python/agent_cli_tmux.py` への fallback 構成へ変更。`py` / `python` / `python3` の auto-detect も含む。Windows runtime placeholder のままでも実 fallback は動作する見込み |
  | Medium-4 | 対応済み | ✅ 確認 | rewrite_text に `AgenticProjectTemplatesの` → `プロジェクトの`、`関連する Python pytest と .NET build/test を通す` → `対象プロジェクトで定義された検証コマンドを実行する` 等の置換が追加。生成 `SKILL.md` で project 固有 wording は残っていない |
  | Medium-5 | 対応済み | ✅ 確認 | `rebuild_user_agent_skills.py` に `sync_runtime_helper()` を追加し、`scripts/agent_cli_tmux.py` を `user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py` へ自動コピーする。`rebuild()` 内で先頭処理として呼ばれるため、再生成時の同期漏れを防げる |
  | Low-1 | 未対応 | ⚠️ 残置 | install script の `--source-root` dry-run 時 path resolve は未修正（実害は限定的） |
  | Low-2 | 未対応 | ⚠️ 残置 | overwrite mode の `rm -rf` 挙動は変わらず（一方で missing mode は `merge_missing_dir` / `Sync-MissingDirectory` で file 単位 merge へ改善され、Codex finding #1 と High-1 の install 動作は強化された） |
  | Low-3 | 対応済み | ✅ 確認 | tmux session 名は短縮しつつ、wrapper path は placeholder 保護 + 境界付き置換により `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh` を維持するよう修正済み |
  | Low-4 | 未対応 | ⚠️ 残置 | `common_agent_principles.md` を実際にどの runtime が consume するかは未明示（実害は限定的） |

  ## 1.4 再々検証（2026-05-09 Claude、コミット `c2334032f693d9221463c1cc1175713643e6749f`）

  対象コミット: `c2334032f693d9221463c1cc1175713643e6749f`（"Finalize review fixes for user-level agent assets"）。

  ### 1.4.1 検証コマンドと結果

  - **Critical-2 修正の確認**:
    - `grep -rn '~/.agentic[^-]' user-agent-assets/skills/` → **0 件**（regression 解消）
    - `grep -rn '~/.agentic-project-templates/bin' user-agent-assets/skills/` → 67 件すべて `~/.agentic-project-templates/` を維持
    - `python3 scripts/rebuild_user_agent_skills.py` 実行後も上記が維持されることを確認
  - **置換ガード実装の確認**:
    - `rebuild_user_agent_skills.py:24-26` に `REPLACEMENT_GUARDS = {"~/.agentic-project-templates/": "__AGENTIC_WRAPPER_ROOT__"}` を導入
    - `rewrite_text:95-97` と `122-124` で前後に placeholder へ退避 / 戻しを行い、`~/.agentic-project-templates/` を全置換から保護
    - session 名置換は境界付きへ書き換え (`agentic-project-templates-review-` → `agentic-review-`、`agentic-project-templates-claude-` → `agentic-claude-`、`agentic-project-templates-orchestrator` → `agentic-orchestrator`)
    - 結果: SKILL.md / procedure 内に `agentic-orchestrator` / `agentic-review-${TOPIC}` / `agentic-claude-${TOPIC}` の短縮 session 名と、`~/.agentic-project-templates/bin/...` の wrapper パスが共存。**Critical-2 は構造的に再発しない**
  - **Low-5 修正の確認**:
    - `grep -nE 'workflow_phase_library/README' docs/.../design.md` → 0 件（残骸削除済み）
    - 該当行は `suite skill には workflow_phase_library を追加配置しない` へ書き換え済み
  - **manual skill 保護機構の確認**:
    - `rebuild_user_agent_skills.py:141-167` に `preserve_manual_skills` / `restore_manual_skills` を追加
    - `rebuild()` 実行前に `WORKFLOW_SKILLS` に含まれない skill ディレクトリを `tempfile.mkdtemp` 配下へ退避し、再生成後に戻す
    - 検証: 再 build 前後の `user-agent-assets/skills/project-doc-bootstrap/SKILL.md` の md5 が一致 (`b95857b8bcd223a44335f0a4ff29c2ca`)。templates / bin / references すべて維持
    - 結果: 当初指摘した「rmtree が手動編集を消す」リスクは解消
  - **設計書 staged migration への更新**:
    - design.md Section 4.1 / 4.2 / 5.3 / 6.3 / 8.1 / 8.3 / 8.4 / 10 / 11.1 / 11.2 / 12.2 / 12.3 / 14 / 15 を `current phase` と `移行完了後 follow-up` に分けて再構成
    - 新 Section 8.4「想定ユーザフロー」が、ユーザ補足の 1〜4 ステップに沿って明文化されている
    - 結果: High-2 は方針変更により **本 phase の対象外**として閉じる根拠が設計書側で明示された

  ### 1.4.2 End-to-end smoke test 結果

  隔離した `mktemp -d` の target project で次を実行し、ユースケース全段（user 補足の 1〜5 ステップに対応）が通ることを確認:

  1. `bash user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.sh --language python --project-root <tmp>` で
     - `docs/{adr,architecture,components/_example_component,design_analysis/{spec_change,new_feature,fix_issues,issue_resolution,refactoring,research_analysis},history,issues,rules,tests,todo}/...` 一式
     - `instructions/agent_common_master.md`、`instructions/agent_sync_guide.md`
     - `scripts/sync_agent_instructions.{sh,ps1,bat}`
     が配置される
  2. placeholder scan が `<!-- TODO: -->` と `{{PROJECT_NAME}}` のいずれもヒット報告し、`docs/components/_example_component が残っています` を warn 表示する
  3. target project で `bash scripts/sync_agent_instructions.sh` を実行すると、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` が `instructions/agent_common_master.md` から再生成される
  4. 再 build (`python3 scripts/rebuild_user_agent_skills.py`) 後も `project-doc-bootstrap` skill が消失しない（manual preservation が機能）

  ### 1.4.3 再々検証で発見した残課題

  ### [Low-6] `copy_doc_templates.sh` の placeholder scan が `instructions/` 配下を見ない

  - 対象箇所
    - `user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.sh:60-75`
    - `templates/python/instructions/agent_common_master.md:1`、`templates/csharp/instructions/agent_common_master.md:1` の `# {{PROJECT_NAME}} Agent Project Instructions (Sync Source)`
  - 確認結果
    - `list_placeholders` は `${PROJECT_ROOT}/docs` のみを scan し、`${PROJECT_ROOT}/instructions/` を含めない
    - bootstrap で配置される `instructions/agent_common_master.md` 冒頭の `{{PROJECT_NAME}}` placeholder は scan 対象外
    - sync 後の `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` も同じ placeholder が残る
  - 影響
    - 設計 Section 8.4 step 4「Agent が copied docs / instructions の placeholder を記入する」を遂行する Agent が、`docs/` 以外の placeholder 残件を一覧で取得できない
    - 実害: Agent が能動的に instructions / sync 出力を確認しない限り、`{{PROJECT_NAME}}` が runtime 文書に残ったままになる
  - 推奨対応
    - `list_placeholders` の scan target を `docs` のみから `docs` + `instructions` + sync 出力 3 種へ拡張する。具体的には:
      - `${PROJECT_ROOT}/docs`
      - `${PROJECT_ROOT}/instructions`
      - `${PROJECT_ROOT}/AGENTS.md`、`${PROJECT_ROOT}/CLAUDE.md`、`${PROJECT_ROOT}/.github/copilot-instructions.md`（存在する場合のみ）
    - `bin/copy_doc_templates.ps1` 側にも同等の調整を入れる
    - 副次的に、placeholder scan の出力末尾に「sync 後に再 scan する」一行ガイドを足すと、Agent が sync を忘れにくくなる

  ### [Low-7] `bin/copy_doc_templates.ps1` の挙動が `.sh` 版と完全一致するかは未検証

  - 対象箇所
    - `user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.ps1`
  - 確認結果
    - `pwsh` がローカル環境にないため、PowerShell 版の dry-run / overwrite / placeholder 一覧は確認できていない
    - 設計上は `.sh` 版と equivalent semantics が要求されている（design.md Section 8.2）
  - 推奨対応
    - Phase 5 の smoke test に「macOS / Linux で `pwsh` を導入したうえで `bin/copy_doc_templates.ps1` の同一動作を確認する」を組み込む
    - 確認項目: `--language` 必須、`missing` default、placeholder scan 出力フォーマット、`_example_component` 警告

  ### [Low-8] sync スクリプト群がドキュメント更新時に静かに dest を上書きする

  - 対象箇所
    - `templates/common/scripts/sync_agent_instructions.sh:66-74`（`copy_instruction_file` が `rm -f` → `cp` する）
    - `templates/common/scripts/sync_agent_instructions.ps1` 同等処理
  - 確認結果
    - sync は `--mode` の概念を持たず、常に `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` を上書きする
    - target project で生成物 3 種を手書き編集している場合、sync 実行時に何の警告もなく上書きされる
  - 影響
    - 設計上、生成物 3 種は直接編集禁止（agent_common_master.md を sync source とする）になっているため期待通りの挙動。ただし誤って編集していたユーザは差分を失う
  - 推奨対応
    - SKILL.md または `agent_sync_guide.md` で「生成物 3 種を直接編集しない」契約を明記する（user 補足の step 5 に対応する文章）
    - 必要なら `sync_agent_instructions.sh --check` モード（差分があれば exit 1）を follow-up として検討

  ### 1.4.4 追加指摘対応後の補足（2026-05-09）

  - Low-6 は対応済み。`copy_doc_templates.sh` / `.ps1` の placeholder scan 対象を `docs` から `docs` + `instructions` + 既存生成物 3 種へ拡張し、wrapper 出力末尾に sync 後の再 scan ガイドを追加した
  - Low-8 は対応済み。`agent_sync_guide.md` に「sync 実行時は生成物 3 種を上書きする」契約を追加し、生成物 3 種の直接編集を避ける運用を明示した
  - Low-7 は継続。`pwsh` 不在のため PowerShell 実行検証は未実施

  ## 1.5 再々々検証（2026-05-09 Claude、コミット `986c735a620147eff2cf9e11f0308515cbc97f0d`）

  対象コミット: `986c735a620147eff2cf9e11f0308515cbc97f0d`（"Address latest user-level agent assets review findings"）。Low-6 / Low-7 / Low-8 の対応確認に絞って独立に再検証した。

  ### 1.5.1 検証結果

  | finding | 申告 | 検証結果 | 検証根拠 |
  |---|---|---|---|
  | Low-6 | 対応済み | ✅ 確認 | `bin/copy_doc_templates.sh:60-100` の `list_placeholders` を `${PROJECT_ROOT}/docs` から、`docs` + `instructions` + `AGENTS.md` + `CLAUDE.md` + `.github/copilot-instructions.md` を選択的に scan する `scan_targets` 配列ベースに書き換え。`rg` / `grep -R` どちらの分岐でも directory / file 双方を扱える。`[info] sync 実行後に本 wrapper を再実行すると、生成済み Agent 向けファイルも再 scan されます` の hint も末尾に追加。SKILL.md の進め方 #3 と最低限のチェック #4 も `docs / instructions の placeholder` へ更新済み |
  | Low-7 | 部分対応 | ✅ 構造確認 / ⚠️ 実行検証は未了 | `bin/copy_doc_templates.ps1:58-105` も `.sh` 版と同等の scan target 拡張へ書き換え（`Test-Path -PathType Container` で directory / file を分岐）。さらに **隠れた critical bug** として、`templates/common/scripts/sync_agent_instructions.ps1` の `param()` ブロックが `Set-StrictMode` / `$ErrorActionPreference` の後ろに置かれていた問題を修正。PowerShell では `param()` は先頭コメント直後にしか書けないため、修正前のスクリプトは parse error で起動できなかった可能性が高い。design.md Section 13.1 #4 に `pwsh -File scripts/sync_agent_instructions.ps1 -Help` を追加。実行検証は引き続き `pwsh` 不在のため未実施 |
  | Low-8 | 対応済み | ✅ 確認 | `templates/common/instructions/agent_sync_guide.md:56` に `sync 実行時は生成物 3 種を上書きするため、手編集した差分は保持されない` を追加。同 file 既存 line 5 / 55 にも「生成物は手編集しない」契約があり、ダブル念押しで明文化された |

  ### 1.5.2 End-to-end 再 smoke test 結果

  隔離 target project で `bash copy_doc_templates.sh --language python` → `bash sync_agent_instructions.sh` → 再 `copy_doc_templates.sh` を実行し、次を確認した:

  - **bootstrap 直後**: `instructions/agent_common_master.md:1` の `{{PROJECT_NAME}}` を scan が報告（旧 scan は docs だけだったため見落としていたもの）
  - **sync 後の再 scan**: 上記に加え `AGENTS.md:1` / `CLAUDE.md:1` / `.github/copilot-instructions.md:1` の `{{PROJECT_NAME}}` も新たに報告
  - `[info] sync 実行後に本 wrapper を再実行すると...` の案内が末尾に出力
  - `[warn] docs/components/_example_component が残っています` の警告は維持

  期待どおりの動作を確認した。

  ### 1.5.3 新規 finding

  なし。Low-6 / Low-7 / Low-8 の対応はいずれも趣旨に合致し、追加の構造的問題は発見されなかった。

  Phase 5 で残るオープン項目は次のみ:

  - `pwsh` 環境での `bin/copy_doc_templates.ps1` および `scripts/sync_agent_instructions.ps1 -Help` 実行確認
  - その際に param() 並び順修正が PowerShell parser を通過すること（Low-7 の hidden bug 修正の検証）

  ## 1.6 PowerShell 実行確認（2026-05-09 Claude、コミット `986c735a620147eff2cf9e11f0308515cbc97f0d` 後）

  `pwsh` 導入後に、未実施だった PowerShell 経路の実行確認を追加で行った。

  ### 1.6.1 実行コマンドと結果

  - `pwsh -NoLogo -NoProfile -File user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.ps1 -Language python -ProjectRoot <tmp>`
    - 成功。`instructions/agent_common_master.md`、`instructions/agent_sync_guide.md`、`scripts/sync_agent_instructions.ps1` を含む bootstrap 配置を確認
    - placeholder scan は `instructions/agent_common_master.md:1` の `{{PROJECT_NAME}}` を報告し、末尾の `[info] sync 実行後に本 wrapper を再実行すると...` ガイドも出力
  - `pwsh -NoLogo -NoProfile -File <tmp>/scripts/sync_agent_instructions.ps1 -Help`
    - 成功。usage と option 一覧を正常表示し、`param()` 位置修正後の parser 通過を確認
  - `pwsh -NoLogo -NoProfile -File <tmp>/scripts/sync_agent_instructions.ps1 -All`
    - 成功。`.github/copilot-instructions.md`、`CLAUDE.md`、`AGENTS.md` の 3 生成物が再生成されることを確認
  - `pwsh -NoLogo -NoProfile -File user-agent-assets/install/install_user_agent_assets.ps1 -DryRun`
    - 成功。既存 skill に対する `[skip]` と未配置資産への `[dry-run] copy` を出力し、install 完了まで到達

  ### 1.6.2 新規 finding

  なし。Low-7 の未実施項目は解消した。

  ### 1.6.3 Claude による独立 PowerShell 実行検証（2026-05-09、`pwsh 7.6.1`）

  ローカルに `pwsh 7.6.1` が導入されたため、設計・実装 Agent 側の成功報告と独立に検証を行った。

  | 検証項目 | 結果 | 検証根拠 |
  |---|---|---|
  | `pwsh -File user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.ps1 -Language python -ProjectRoot <tmp>` | ✅ 成功 | 27 file 配置、placeholder scan が docs / instructions の `{{PROJECT_NAME}}` と `<!-- TODO: -->` を出力。`[info] sync 実行後に...` hint と `[warn] docs/components/_example_component が残っています` warn も出力 |
  | `pwsh -File <tmp>/scripts/sync_agent_instructions.ps1 -Help` | ✅ 成功 | Usage / Options が正しく出力。`param()` を script 先頭へ移動した修正により、PowerShell parser を通過することを実証（修正前は parse error 必至だった） |
  | `pwsh -File <tmp>/scripts/sync_agent_instructions.ps1`（既定 = `-All` 相当） | ✅ 成功 | `=== Agent Sync Start ===` から `=== Agent Sync Complete ===` まで通り、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` がいずれも `instruction copied` で出力される |
  | sync 後の再 scan（Low-6 確認） | ✅ 成功 | bootstrap を再実行すると `instructions/agent_common_master.md`、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` の `{{PROJECT_NAME}}` がいずれも報告される |
  | `pwsh -File user-agent-assets/install/install_user_agent_assets.ps1 -DryRun` | ✅ 成功 | helper root 作成、wrapper / instructions / runtime の copy plan、3 target × 全 skill の copy plan、core workflow skill への shared common hydrate plan を計 101 行出力 |
  | `pwsh -File install_user_agent_assets.ps1 -DryRun -Targets claude`（target 絞り込み） | ✅ 成功 | `~/.claude/skills/` のみへの copy plan が出力され、`~/.copilot/skills` / `~/.agents/skills` / `~/.codex/skills` のいずれも触らない |
  | `pwsh -File install_user_agent_assets.ps1 -DryRun -Targets bogus`（不正 target validation） | ✅ 成功 | helper root への copy 前に `Validate-Targets` が `Unsupported target: bogus` を throw して終了。helper root を汚さない順序が保たれている |
  | `pwsh -File install_user_agent_assets.ps1 -DryRun -Targets 'copilot, claude'`（空白吸収） | ✅ 成功 | `Get-NormalizedTargets` の `.Trim()` により空白を吸収し、両 target の install plan を出力 |
  | `pwsh -File install_user_agent_assets.ps1 -Targets claude` の実 install（HOME を `mktemp -d` へ redirect） | ✅ 成功 | `install complete` を出力。配布された `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh` のモードが `-rwxr-xr-x`、つまり PowerShell の `Copy-Item` が source の +x bit を保持することを確認 |

  ### 1.6.4 観察事項（finding 化はしない）

  - **`install_user_agent_assets.ps1` には明示的な chmod 処理が無い**。一方 `install_user_agent_assets.sh` には `ensure_shell_wrapper_executable` で defensive に `chmod 755` を行うコードがある。POSIX 環境で `pwsh` 経由で実行した場合、PowerShell の `Copy-Item` が source の `-rwxr-xr-x` を保持するため、現状は実動作上問題ないことを実 install で確認した。ただし、source 側で何らかの理由で +x が外れた場合 `.sh` 版は復帰できるが `.ps1` 版は復帰できないという非対称が残る。**Phase 5 完了後の follow-up メモ**として記録するに留める
  - `param()` 位置修正により `Set-StrictMode` が `param()` の後に評価される動線が成立し、未定義変数の早期検出も期待どおり機能する
  - PowerShell の `throw` メッセージは色付きで stderr へ出力され、`Validate-Targets` の error path でも本文 (`Unsupported target: bogus`) は読みやすい

  ### 1.6.5 結論

  - Low-7 の構造修正は PowerShell parser を実通過し、Phase 5 持ち越し項目だった `.ps1` 系の動作検証が完了
  - bootstrap / sync / install の全 PowerShell スクリプトが期待どおり動作することを実機で確認
  - 構造的な追加指摘なし。`.ps1` installer に chmod が無い点は Phase 5 完了後の follow-up メモとして記録
  - **Phase 4 残オープン項目はゼロ**になり、Phase 5 へそのまま進める

  ## 1.3 再検証で発見した新規 finding（対応前記録）

  ### [Critical-2] generator の置換ルールが wrapper install path を破壊し、orchestrator/review skill から wrapper を呼べない（regression）

  - 対象箇所
    - `scripts/rebuild_user_agent_skills.py:97`（`text = text.replace("agentic-project-templates", "agentic")`）
    - 影響 file: `user-agent-assets/skills/{copilot-review-automation,claude-review-automation,autonomous-workflow-orchestrator,copilot-cli-workflow-orchestrator}/SKILL.md` と各 `references/procedure/*.md`
  - 確認結果
    - `grep -rn '~/.agentic' user-agent-assets/skills/` で `~/.agentic/bin/agentic-agent-cli-tmux.sh` 形式の参照を 30 箇所以上検出
    - 一方、wrapper の **実 install 先**は引き続き `$HOME/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh`
      - `install_user_agent_assets.sh:165` の `helper_root="${HOME}/.agentic-project-templates"`
      - `install_user_agent_assets.ps1:154` の `Join-Path $HOME '.agentic-project-templates'`
      - `bin/agentic-agent-cli-tmux.sh:4` / `bin/agentic-agent-cli-tmux.ps1:4` の `RUNTIME_ROOT` 既定値
      - `user-agent-assets/install/README.md:10-11` も `~/.agentic-project-templates/` を案内
      - `common_agent_principles.md:18` も `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh` を案内
  - 影響
    - install 後、orchestrator / review automation skill の手順をなぞって `~/.agentic/bin/agentic-agent-cli-tmux.sh ensure ...` を実行すると **`No such file or directory` で即失敗**する
    - Critical-1（gitignore）と High-3（chmod）が解消されても、wrapper への到達経路自体が壊れているため、Phase 4 の核となる orchestrator workflow が動かない
    - 設計 Section 6.4 の「`SKILL.md` からは wrapper だけを呼ぶ」契約は維持されているが、その wrapper のパスが SKILL.md 側と install 側で食い違う
  - 原因分析
    - Low-3 対応として tmux session 名短縮（`agentic-project-templates-orchestrator` → `agentic-orchestrator`）を狙った置換 `text.replace("agentic-project-templates", "agentic")` が、文字列マッチで `~/.agentic-project-templates/bin/...` も巻き込んだ
    - 対策時に「session 名」と「install path」を区別する境界が無かったため、過大置換が発生した
  - 推奨対応（いずれか）
    1. **置換ルールを境界付きに変更**（推奨）:
       - 例えば session 名のみマッチする `text.replace("agentic-project-templates-review-", "agentic-review-")` / `text.replace("agentic-project-templates-orchestrator", "agentic-orchestrator")` のように、後ろに識別子が続くケースに限定する
       - もしくは事前に `text.replace("~/.agentic-project-templates/", "~/.agentic-project-templates/")` という no-op を最後に挟むのではなく、**置換順を逆にして wrapper path を先に保護する placeholder で守ってから session 名置換 → placeholder 戻し** のパターンにする
    2. **install 先 path を skill 側に合わせる**:
       - install 先と wrapper の `RUNTIME_ROOT` を `$HOME/.agentic/` に変更し、`README.md` / `common_agent_principles.md` も追従する
       - 既に user-level に install 済みのユーザがいる場合は migration note が必要
    - いずれにせよ、`grep -rn '~/.agentic-project-templates\|~/.agentic/' user-agent-assets/` の結果が install 動線と完全に一致することを smoke test に組み込むべき

  ### [High-2 再開] root / template の薄化と `skill_catalog.md` ripple は依然として未着手

  ステータステーブルでは「対応済み」と申告されたが、実態として `instructions/agent_common_master.md` / 各 template の `agent_common_master.md` / root + template の `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` / `scripts/sync_agent_skills.*` / `docs/rules/skill_catalog.md` / `docs/procedure/` のいずれも修正されていない。

  影響:
  - 設計 Section 14（受け入れ条件）#2 と #5 が未達
  - `meta.md` の `impl_status` を切り替える前に、設計 Section 11.1 / 11.2 の順序制約に従ってこの ripple を片付ける必要がある
  - 仮にこのまま Phase 5 へ進むと、user-level skill は機能していても project-level の案内文が旧構造を指し続け、ユーザに「正本がどこか」を誤認させる

  推奨対応:
  - 設計 Section 4.3 のスケルトン（目的 / 必須参照 / project 固有ルール / 生成物運用 / user-level assets 利用前提）に従い、3 つの `agent_common_master.md` を書き換える
  - sync script `scripts/sync_agent_skills.{sh,ps1,bat}` を「`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の再生成のみ」へ縮小する
  - `docs/rules/skill_catalog.md` を削除し、参照元（master / template の各 `agent_common_master.md` と `SKILL.master.md`）から `skills カタログ` 行を除去する
  - `docs/procedure/` 一式は smoke test 通過後にまとめて削除する

  ### [Low-5] 設計書 Section 7.4 line 366 が新方針と矛盾している残骸

  - 対象: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:366`
  - 現状: `- workflow_phase_library/README.md は root 正本で直接参照される copilot-review-automation にだけ置く`
  - 矛盾: 同一文書 Section 7.2 の新 dependency map では `copilot-review-automation` の payload は「なし（SKILL.md から 6 skill 名を索引）」と明記されている。`workflow_phase_library/README.md` は実装上も配置されていない（`find user-agent-assets -name 'README.md' -path '*workflow_phase_library*'` が 0 件）
  - 推奨: 当該行を削除するか、「`copilot-review-automation` を含め、suite skill には `workflow_phase_library` 一切を持たせない」と書き換える

## 2. 実装と設計の対応評価

| 設計章 | 実装対応箇所 | 評価 | 備考 |
|---|---|---|---|
| 4.1 user-level 正本ディレクトリ | `user-agent-assets/` | ✅ | `project-doc-bootstrap/` を含む current phase の正本構造を満たし、`workflow_selection.md` の設計外追加も解消済み |
| 4.2 project-level に残すもの | `project-doc-bootstrap/templates/**` | ✅ | current phase は target project へ docs / instructions / sync script を初期配置する導線を採り、repo 直下 / template 側の薄化は follow-up とした |
| 4.3 `agent_common_master.md` After 構成 | `project-doc-bootstrap/templates/{python,csharp}/instructions/agent_common_master.md` | ✅ | target project bootstrap 用の project-level instruction として After 構成を定義し、repo 直下 / template 側反映は移行完了後に分離した |
| 5 コンポーネント責務と依存方向 | install / runtime / skills の配置 | ⚠️ | 一部 `SKILL.md` が `docs/rules/coding_rules.md` 等の project-level docs を直接索引しており、依存方向の禁止規定（Section 5.2）に抵触する余地がある（Medium-2） |
| 6.1-6.2 install 先・I/F | `install/install_user_agent_assets.{sh,ps1}` | ✅ | `--dry-run`、`missing` default、`--targets`、`--source-root` を実装済み |
| 6.3 sync script の責務縮小 | `project-doc-bootstrap` が配る `sync_agent_instructions.*` | ✅ | current phase では target project 上の生成物 3 種再生成に責務を限定し、repo 直下 / template 側変更は follow-up とした |
| 6.4 shared helper 配布 | `bin/` と `runtime/` | ⚠️ | 配置は設計通りだが gitignore と実行権限の問題あり（Critical-1 / Medium-3） |
| 6.5 / 7.3 shared common hydrate | `install_user_agent_assets.{sh,ps1}` の hydrate ロジック | ✅ | core workflow skill では設計通りに動作。suite skill 群は新方針（procedure 非同梱）に伴い hydrate 対象外として扱う（Design-Doc-Update-1） |
| 7.2 skill 別 dependency map | `scripts/rebuild_user_agent_skills.py` の `WORKFLOW_SKILLS` | ✅ | suite skill slim payload 方針と設計書 Section 7.2 / 7.3 / 7.4 の更新が一致した |
| 7.4 `workflow_selection.md` 除外 | `user-agent-assets/` | ✅ | `workflow_selection.md` は user-level 配布対象から外れ、design の例外規則と整合した |
| 7.5 `SKILL.master.md` からの一般化 | `rebuild_user_agent_skills.py:rewrite_text` | ⚠️ | `docs/procedure/` → `references/procedure/` 等のパス書換は実施しているが、`AgenticProjectTemplatesの` のような project 名や `Python pytest と .NET build/test` のような project 固有チェックが残置（Medium-4） |
| 8 docs bootstrap skill | `project-doc-bootstrap/` | ✅ | docs 雛形に加え、project-level `agent_common_master.md`、`agent_sync_guide.md`、sync script を target project へ初期配置する current phase の導線を定義した |
| 9 fallback を持たない方針 | （実装スコープ的には何もしない） | ✅ | `.github/skills/` 等への workspace fallback 生成は行っていない |
| 10 `skill_catalog.md` ripple | 設計更新 | ⚠️ | repo 直下 / template 側 ripple は移行完了後の follow-up と明示。current phase では bootstrap templates が `skill_catalog.md` を再導入しないことを要件化 |
| 11.1 実装単位の進捗 | 1〜5 着手、6 は follow-up | ⚠️ | 4 (`project-doc-bootstrap`) と 5（target project への project-level 導線）は current phase に含め、repo 直下 / template の ripple は移行完了後へ分離 |
| 13 テスト設計 | 未実施 | — | impl 中であり判断保留 |

## 3. 指摘一覧

### [Critical-1] `user-agent-assets/bin/` が `.gitignore` の `bin/` ルールに巻き込まれてコミット対象から除外される

- 対象箇所
  - `.gitignore:26` の `bin/`（C# / .NET の build artifact 除外）
  - `user-agent-assets/bin/agentic-agent-cli-tmux.sh`
  - `user-agent-assets/bin/agentic-agent-cli-tmux.ps1`
- 確認結果
  - `git check-ignore -v user-agent-assets/bin/agentic-agent-cli-tmux.sh` の出力は `.gitignore:26: bin/`
  - `git status --ignored user-agent-assets` でも `Ignored files: user-agent-assets/bin/` と表示される
- 影響
  - 現状はまだ working tree のみで、`git add user-agent-assets/` を行っても `bin/` 配下が一切コミットされない
  - 結果として、配布物の中核である `agentic-agent-cli-tmux.sh` / `.ps1` がリポジトリに残らず、設計 Section 6.4 と orchestrator skill 群（`autonomous_workflow_orchestrator.md` 内の `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh ensure ...`）が成立しなくなる
  - 設計 Section 8.1 の `project-doc-bootstrap/bin/` も追加実装した時点で同じ問題に遭遇する
- 推奨対応
  - `.gitignore` に明示的な negation を追加する（例: `!user-agent-assets/bin/`、`!user-agent-assets/bin/**`、`!user-agent-assets/skills/*/bin/`、`!user-agent-assets/skills/*/bin/**`）
  - 併せて `git check-ignore` で `user-agent-assets/bin/agentic-agent-cli-tmux.sh` が無視されないことを確認するスモークステップを Phase 5 のチェックリストに追加する
  - 可能ならば C# 用の `bin/` ルールを `**/csharp-project-template/**/bin/` 等のスコープへ絞り、ユーザレベル資産との衝突を恒久的に避ける

### [High-1] `project-doc-bootstrap` skill が未実装、かつ `workflow_selection.md` が設計外で `instructions/` に追加されている

- 対象箇所
  - 設計書 Section 4.1 / 7.4 / 8 / 11.1
  - 実装: `user-agent-assets/skills/` には `project-doc-bootstrap/` が存在しない
  - 実装: `user-agent-assets/instructions/workflow_selection.md` が新規追加されている
- 確認結果
  - `find user-agent-assets -iname '*bootstrap*'` の結果 0 件
  - `python-project-template/instructions/skills/python-template-doc-filler/`、`csharp-project-template/instructions/skills/csharp-template-doc-filler/` は依然として template 内に存在
  - 設計 Section 4.1 のディレクトリツリーは `instructions/` を `common_agent_principles.md` と `language_policy.md` の 2 ファイルだけと定義しており、`workflow_selection.md` を含めていない
  - 設計 Section 7.4 は `workflow_selection.md` を「user-level skill の `references/` へ移さない。必要になった場合だけ standalone skill として再定義する」と明記
- 影響
  - 設計が `Phase 4 実装単位 4` として明示している `project-doc-bootstrap` 追加が未達
  - `common_agent_principles.md` Line 11 から相対パス `workflow_selection.md` で参照されているため、user-level instructions として配布する場合は配布先を `~/.agentic-project-templates/instructions/` に揃える必要があるが、Codex / Claude / Copilot のいずれも当該パスを自動 load しないため、ユーザが手動で確認しに行かない限り意味を持たない
  - 設計外の追加であるため、設計と実装の責務境界がぶれている
- 推奨対応
  - `project-doc-bootstrap/` skill を `templates/`、`references/`、`bin/` を含めて追加するか、本 Phase の対象から外す場合は設計 Section 4.1 / 8 / 11.1 を更新して根拠を残す
  - `workflow_selection.md` は「standalone skill 化するまで user-level に置かない」方針を採るのであれば削除し、`common_agent_principles.md` の参照を「workflow 選択ルール（各 workflow skill の SKILL.md を参照）」のような skill ベース参照に置換する
  - もし `instructions/` 直下配布を採用する場合は、設計 Section 4.1 / 6.5 / 7.4 を更新し、`common_agent_principles.md` から参照する正規パスを明示する

### [High-2] root / template 側の薄化と `skill_catalog.md` ripple が未着手

- 対象箇所
  - `instructions/agent_common_master.md`、`python-project-template/instructions/agent_common_master.md`、`csharp-project-template/instructions/agent_common_master.md`
  - root / template の `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`
  - root `instructions/skills/*/SKILL.master.md`、template 側 `.claude/skills/*/SKILL.md`
  - root / template の `docs/procedure/`、`docs/rules/skill_catalog.md`
  - `scripts/sync_agent_skills.{sh,ps1,bat}`
- 確認結果
  - `grep -nE 'docs/procedure|skill_catalog' instructions/agent_common_master.md` で 3 件、Python template / C# template の同名ファイルでも同件数の `skill_catalog` / `docs/procedure/README.md` / `docs/procedure/` 参照が残置
  - `git diff scripts/sync_agent_skills.sh` 等は無変化
- 影響
  - 設計 Section 4.2 / 4.3 / 6.3 / 10 / 11.1 の主要スコープが残っており、`SC-20260508-001` の完了条件（受け入れ条件 1〜5）を満たしていない
  - 現状の root / template から user-agent-assets への移行案内が `agent_common_master.md` 上に存在せず、ユーザが「正本がどこにあるのか」を読み解けない
  - sync script 未着手のため、薄化後の `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` 再生成パイプラインを実証できない
- 推奨対応
  - 設計 Section 11.1 に従い、次の順序でリップル更新を行う
    1. workflow skill の `references/` 化が動作することを smoke test で確認（後述 Medium-3 / High-3 の修正後）
    2. `instructions/agent_common_master.md` を Section 4.3 のスケルトンへ書き換え
    3. `skill_catalog.md` 参照を root / template / SKILL.master.md から削除
    4. `scripts/sync_agent_skills.*` の責務を Section 6.3 の通り、生成物 3 種のみへ縮小
    5. 上記が揃った後に `docs/procedure/` を root / template から削除
  - 移行期間中は `meta.md` の `impl_status` を `in_progress` に更新し、進捗トレースを取り直す

### [Design-Doc-Update-1] suite skill 群の payload は意図的縮小済み。設計書 Section 7.2 / 7.3 / 7.4 が旧方針のまま未反映

- 対象箇所
  - 設計書 Section 7.2（dependency map）、Section 7.3（hydrate 対象）、Section 7.4（移行ルール）
  - 実装: `scripts/rebuild_user_agent_skills.py:WORKFLOW_SKILLS`（lines 61-80）
  - 配置: `user-agent-assets/skills/{copilot-review-automation,claude-review-automation,autonomous-workflow-orchestrator,copilot-cli-workflow-orchestrator}/references/`
- 経緯（ユーザ補足 2026-05-09）
  - 元の設計では orchestration / review automation 系 skill が 5 種 workflow の procedure を全コピーする構成だった
  - 全コピーは正本変更時の同期コストが高いため、ユーザ指示で「procedure をコピーせず、同時 install される他 skill の名前だけを SKILL.md に記載する」方針へ転換した
  - 実装（`rebuild_user_agent_skills.py:WORKFLOW_SKILLS` と各 `SKILL.md` の参照表現）は新方針に追従済み
  - 設計書本文には未反映であり、Section 7.2 / 7.3 / 7.4 が旧方針のままになっている
- 確認結果（実装実態）
  | skill | 設計書記載（旧方針） | 実装（新方針） |
  |---|---|---|
  | `copilot-review-automation` | `workflow_phase_library/README.md` + 5 workflow 本体 + `ai_review_response_workflow.md` + 5 workflow 分の phase library + hydrate された common | `SKILL.md` のみ。本文から `spec-change-workflow` / `new-feature-workflow` / `bugfix-workflow` / `issue-resolution-workflow` / `refactoring-workflow` / `ai-review-response-workflow` の各 skill を名前で索引 |
  | `claude-review-automation` | 5 workflow 本体 + `ai_review_response_workflow.md` + `autonomous_workflow_orchestrator.md` + 5 workflow 分の phase library + hydrate された common | `autonomous_workflow_orchestrator.md` のみ。SKILL.md から他 skill を名前で索引 |
  | `autonomous-workflow-orchestrator` | `autonomous_workflow_orchestrator.md` + 5 workflow 本体 + `ai_review_response_workflow.md` + 5 workflow 分の phase library + hydrate された common | `autonomous_workflow_orchestrator.md` のみ。SKILL.md から他 skill を名前で索引 |
  | `copilot-cli-workflow-orchestrator` | `autonomous_workflow_orchestrator_copilot_cli.md` + 5 workflow 本体 + `ai_review_response_workflow.md` + 5 workflow 分の phase library + hydrate された common | `autonomous_workflow_orchestrator_copilot_cli.md` のみ。SKILL.md から他 skill を名前で索引 |
  - install スクリプトの `hydrate_workflow_phase_library_common` は `references/procedure/workflow_phase_library/` の存在を前提に common を hydrate する。新方針では suite skill に phase library を持たせないため、これら 4 skill が hydrate 対象から外れる挙動と整合している
- 影響
  - 実装は新方針に従って動作しており、機能的な問題は無い
  - ただし設計書 Section 7.2 / 7.3 / 7.4 が旧方針のまま残っており、後続レビュー（codex review、Phase 5 検証、Phase 6 アーカイブ後の参照）で「設計と実装が食い違う」と再指摘される懸念がある
  - 設計上の `self-contained` 要件は、suite skill では「同 install bundle 内の他 skill が揃っている前提」へ緩和されるため、その前提も設計書に明記が必要
- 推奨対応（設計書側の更新）
  - Section 7.2 dependency map の suite skill 4 行を新方針に合わせて書き換える
    - `copilot-review-automation`: 起点文書なし（SKILL.md から他 skill を名前で索引）
    - `claude-review-automation`: `autonomous_workflow_orchestrator.md` のみ
    - `autonomous-workflow-orchestrator`: `autonomous_workflow_orchestrator.md` のみ
    - `copilot-cli-workflow-orchestrator`: `autonomous_workflow_orchestrator_copilot_cli.md` のみ
  - Section 7.3 の「hydrate 対象 skill」一覧から `copilot-review-automation` / `claude-review-automation` / `autonomous-workflow-orchestrator` / `copilot-cli-workflow-orchestrator` を外す
  - Section 7.4 の「review automation / orchestrator 群は『複数 workflow を束ねる suite』とみなし、5 workflow 本体とその phase library を丸ごと持つ」を「review automation / orchestrator 群は同時 install される他 user-level skill の存在を前提とし、`SKILL.md` から skill 名で索引する」へ書き換える
  - 併せて、install script は `--targets` 単位で常に skill 全件を配布する仕様であることを Section 6.1 に追記し、部分インストール時の制約（suite skill 単独使用不可）を README に明示する
  - 設計書改訂は Phase 3 設計の「post-review refine」追加コミットとして残し、`meta.md` の `related_commits` に追記する

### [High-3] install 後の wrapper に実行権限が付与されない（macOS / Linux）

- 対象箇所
  - `user-agent-assets/install/install_user_agent_assets.sh` の `copy_path`
  - `user-agent-assets/bin/agentic-agent-cli-tmux.sh`
- 確認結果
  - `ls -l user-agent-assets/bin/agentic-agent-cli-tmux.sh` のモードは `-rw-r--r--`
  - 配下の install script は `cp -R` / `cp` を呼ぶだけで、`chmod +x` は行っていない
  - skill 群の `SKILL.md`（`autonomous-workflow-orchestrator` など）は `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh ensure ...` を直接呼ぶ前提
- 影響
  - install を行った直後の `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh` も実行権限を持たないため、orchestrator / review skill から直接起動できない
  - ユーザが `chmod +x` を手動で当てる、もしくは `bash` 経由で起動する必要が生じ、Phase 5 smoke test の前提を満たさない
- 推奨対応
  - install 後に `.sh` wrapper へ `chmod +x` を当てるロジックを追加する（macOS / Linux のみ。PowerShell では実行権限の付与は不要）
  - source 側 (`user-agent-assets/bin/agentic-agent-cli-tmux.sh`) を最初から `+x` で commit するのも有効（git は実行ビットを保持する）
  - PowerShell 側 install script もコピー後に `git update-index` 等を呼ぶ必要は無いが、`cp` で `RemoveItem` を伴うため、再 install 時のモード保持を smoke test で確認する

### [Medium-1] `instructions/workflow_selection.md` を残すなら配布動線が片肺

- 対象箇所
  - `user-agent-assets/instructions/workflow_selection.md`
  - `install/install_user_agent_assets.{sh,ps1}` の `install_single_runtime`
  - 設計書 Section 4.1
- 確認結果
  - install script は `${source_root}/instructions` を `~/.agentic-project-templates/instructions/` にコピーする
  - 一方で Codex / Claude / Copilot のいずれも `~/.agentic-project-templates/instructions/` を自動 load しない
  - `common_agent_principles.md` から相対参照 (`workflow_selection.md`) されているため、ユーザが当該ファイルへ手動でアクセスしない限り存在意義が薄い
- 影響
  - 設計外配置のまま残す場合、文書的に置いてあるだけで配布の役に立たないファイルになる
  - 仮に standalone skill 化（Section 7.4）するなら、`user-agent-assets/skills/workflow-selection/` のような専用 skill にして CLI から `--skill workflow-selection` で参照できるようにすべき
- 推奨対応
  - High-1 と一括で扱う。残置するなら設計 Section 4.1 を更新し、`common_agent_principles.md` がどう活きるか（人間向け補助か、特定 agent への load か）を明示する

### [Medium-2] 一部の `SKILL.md` がプロジェクト固有 docs を直接索引しており、設計 Section 5.2 の依存方向に抵触する

- 対象箇所
  - `user-agent-assets/skills/spec-change-workflow/SKILL.md:18-19`（`docs/rules/coding_rules.md`、`docs/rules/development_workflow.md`）
  - 同様に `bugfix-workflow`、`new-feature-workflow`、`issue-resolution-workflow`、`refactoring-workflow`、`research-analysis-workflow`、`ai-review-response-workflow` の `SKILL.md`（`scripts/rebuild_user_agent_skills.py:rewrite_text` が `docs/rules/*` を書き換えていないため）
- 確認結果
  - `rebuild_user_agent_skills.py:84-104` の置換ルールは `docs/procedure/` のみを対象とし、`docs/rules/*` には触れていない
  - 設計 Section 4.2 では `docs/rules/coding_rules.md` 等を project-level に残すと宣言しているため、user-level skill が「プロジェクト側にこのファイルがある前提」で動くのは設計と衝突する
- 影響
  - user-level skill が任意プロジェクトで起動された際、当該 docs が無いと skill 内の「実行ルール」セクションが破綻する
  - 設計 Section 5.2 の依存方向（user-level → project-level の参照禁止）と矛盾
- 推奨対応
  - rewrite_text に「`docs/rules/coding_rules.md` 等の project-level docs は『プロジェクトのコーディング規約（プロジェクト docs を参照）』という抽象表現に置換する」ロジックを足す
  - もしくは、これらのリンクを削除し、`common_agent_principles.md` 経由で「各プロジェクトの規約に従う」と一段抽象化する

### [Medium-3] Windows ランタイム実体が placeholder のため `.ps1` wrapper が起動失敗する

- 対象箇所
  - `user-agent-assets/runtime/agent-cli-tmux/win-x64/README.md`
  - `user-agent-assets/bin/agentic-agent-cli-tmux.ps1`
- 確認結果
  - `win-x64/AgentCliTmux.exe` は未配置（README.md のみ）
  - `.ps1` wrapper は `Test-Path $ExePath` チェックの後 `Write-Error "runtime helper not found"` で終了する
- 影響
  - Windows 環境では orchestrator / review skill が事実上動作しない
  - placeholder の旨は README に記述されているため、設計 Section 13.1 #2 の「`install_user_agent_assets.ps1 -DryRun`」自体は通る
- 推奨対応
  - 当該 placeholder を follow-up todo として明示的に切り出し（例: `docs/todo/todo.md` に新 ID で起票）、Phase 4 のスコープから外すか後段で publish する責務を明確化する
  - `meta.md` の `impl_status` 移行と同時に「Windows runtime は follow-up」を明示

### [Medium-4] user-level `SKILL.md` に project 名 / 言語固定の文言が残っている

- 対象箇所
  - 各 `user-agent-assets/skills/*/SKILL.md`（特に description と「最低限の必須チェック」中の "関連する Python pytest と .NET build/test を通す"）
- 確認結果
  - `description: AgenticProjectTemplatesの仕様変更で...` のような project 固定 description が複数残置
  - `"関連する Python pytest と .NET build/test を通す"` は AgenticProjectTemplates 専用の検証コマンドであり、任意の Python 単独 / C# 単独 project では不適切
  - `rebuild_user_agent_skills.py:rewrite_text` には project 名の一般化や言語条件の調整ロジックがない
- 影響
  - 設計 Section 4.1 / 7.5 の「placeholder を持たない `SKILL.md` に統一」「user-level 正本は project 非依存」前提に対する実装ギャップ
  - 任意の Python / C# project に install したユーザが、自プロジェクトに関係ない検証コマンドを実行する誤導が起きる
- 推奨対応
  - description は `AgenticProjectTemplatesの` プレフィックスを削るか、`プロジェクトの` のような汎用表現に置換する
  - チェックリスト第 5/6 項は「対象プロジェクトの規定検証コマンドを通す」のような抽象表現にし、具体コマンドは project-level docs に委譲する

### [Medium-5] `agent_cli_tmux.py` が repo 内で 3 箇所に重複し、同期手段が無い

- 対象箇所
  - `scripts/agent_cli_tmux.py`
  - `python-project-template/scripts/agent_cli_tmux.py`
  - `user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py`（追加）
- 確認結果
  - `md5 scripts/agent_cli_tmux.py user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py` は完全一致
  - `rebuild_user_agent_skills.py` には agent_cli_tmux.py の sync 処理は無く、手動コピーで成立している
- 影響
  - 将来の機能追加時、3 箇所のうち 1 つだけ更新されると不整合が長期間放置される（CLAUDE.md 必須ルール「python-project-template/ と csharp-project-template/ の同等概念は意図的な差異を除き同期する」とも整合しない）
  - `__pycache__` が `user-agent-assets/runtime/agent-cli-tmux/python/__pycache__` に生成されている（`.gitignore` で `__pycache__/` は除外されているので git 上の問題は無いが、配布物に compiled file を発生させる場所であることは要注意）
- 推奨対応
  - `rebuild_user_agent_skills.py` に `scripts/agent_cli_tmux.py` を `user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py` へコピーする処理を追加する
  - もしくは user-agent-assets を正本とし、`scripts/agent_cli_tmux.py` を symlink もしくは生成物として位置付ける（CLAUDE.md の「生成物は直接編集しない」原則を踏襲）
  - 配布前に `__pycache__` を含めない清掃ステップを install / sync に組み込む

### [Low-1] install script の `--source-root` 解決が dry-run でも実 path を要求する

- 対象箇所
  - `install/install_user_agent_assets.sh:188` `resolved_root="$(cd "${SOURCE_ROOT}" && pwd)"`
  - `install/install_user_agent_assets.ps1:85` `Resolve-Path $SourceRoot`
- 確認結果
  - dry-run でも `cd` / `Resolve-Path` を先に実行しているため、存在しないパスを `--source-root` で渡した場合、dry-run 出力前に異常終了する
- 影響
  - 利用者影響は小さいが、CI 等で「絶対 path で計画だけ確認する」用途で躓く可能性がある
- 推奨対応
  - dry-run 時は path resolve を緩める（例: `realpath -m` を使う / `Resolve-Path -ErrorAction Stop` を `-ErrorAction SilentlyContinue` で扱う）か、ヘルプに「`--source-root` は実在する path であること」を明記する

### [Low-2] `copy_path` が overwrite mode で `rm -rf` するため、ユーザ手動カスタマイズが消える

- 対象箇所
  - `install/install_user_agent_assets.sh:53` `rm -rf "${target_path}"`
  - `install/install_user_agent_assets.ps1:42` `Remove-Item -Recurse -Force $TargetPath`
- 確認結果
  - overwrite mode 時、target skill ディレクトリ全体を削除してから `cp -R` で再構築する
- 影響
  - skill ディレクトリにユーザが追加したカスタムファイル（メモ書き、ローカル拡張等）も同時に削除される
  - 設計 Section 6.2 の「overwrite 指定時のみ上書き」と語義は合うが、実装は「ディレクトリ丸ごと置換」であり、ファイル単位 overwrite ではない
- 推奨対応
  - 現状の挙動を README に明示し、`overwrite` の副作用を利用者へ知らせる
  - もしくはファイル単位の `cp -f` ベースの上書きへ変更し、user-extension の保護を試みる（ただし削除されたソースファイルは残ったままになる難点あり、現実装が単純で良い可能性も高い）

### [Low-3] orchestrator skill 内の `tmux session 名` がプロジェクト固有

- 対象箇所
  - `user-agent-assets/skills/copilot-review-automation/SKILL.md:107` `agentic-project-templates-review-<topic>`
  - `user-agent-assets/skills/autonomous-workflow-orchestrator/.../autonomous_workflow_orchestrator.md` の `agentic-project-templates-orchestrator`
- 影響
  - 任意プロジェクトに install した際にも `agentic-project-templates-*` という session 名が使われ、ユーザに「この skill は AgenticProjectTemplates 専用？」と誤解させる
- 推奨対応
  - `agentic-project-templates-` プレフィックスを `agentic-` などプロジェクト不可知の名称に置換するか、可変化（環境変数 / SKILL 引数）する

### [Low-4] `common_agent_principles.md` 配布の意義整理

- 対象箇所
  - `user-agent-assets/instructions/common_agent_principles.md`
  - install 動線で `~/.agentic-project-templates/instructions/` へコピーされる
- 確認結果
  - Codex / Claude / Copilot のいずれも `~/.agentic-project-templates/instructions/` を自動 load する仕組みは無い
  - `common_agent_principles.md` の中身は user-level workflow を案内する内容で、実体は人間向け参考資料に近い
- 影響
  - 「user-level 共通原則を配布する」という設計意図に対して、配布先で誰がいつ読むのかが不明瞭
- 推奨対応
  - どの agent ランタイムが `common_agent_principles.md` を取り込むのかを設計 Section 4.1 / 5.1 / 6.4 のいずれかに明記する
  - もしくは Claude Code の memory（`~/.claude/CLAUDE.md`）等、各 agent の通常の memory パスへ追記する補助スクリプトを install へ追加する

## 4. 設計と実装の追加観察

- `rebuild_user_agent_skills.py` は `SKILL_OUTPUT_ROOT` を毎回 `shutil.rmtree` してから再生成するため、`user-agent-assets/skills/` に手動編集を加えると消失する。設計 Section 7.5 に従う「正本は user-level `SKILL.md`」と整合させるなら、当該スクリプト自体を「正本生成器」と位置付け直し、CLAUDE.md に同期手順を残す（root の `instructions/skills/` を編集 → `python scripts/rebuild_user_agent_skills.py` 実行）必要がある。
- `install/README.md` の使い方には `--targets copilot,claude` 等のサンプルがあるが、`--mode overwrite` の例示が無い。Low-2 と併せて、副作用を伴うオプションは README に明示するのが望ましい。
- `user-agent-assets/install/install_user_agent_assets.ps1` は `Copy-Item -Recurse -Force` を使うため、ディレクトリ目標が既存のときに上書きの副作用が `.sh` 版と完全一致するかは smoke test で確認する価値がある。
- `language_policy.md` は内容が非常に薄く、CLAUDE.md / agent_common_master.md と重複する文言を含む。設計 Section 5.1 が要求するのは「user-level 共通 instructions」だけなので、内容は最小で良いが、project-level との重複を解消するためのトーン調整は今後の検討余地あり。

## 5. 完了条件への影響評価

設計 Section 14 の受け入れ条件と現状の充足度（再検証後）:

1. user-level 正本ディレクトリ、install script、workflow skill `references/` の構造が明示されている
  - **達成**。`project-doc-bootstrap` skill が追加され、ディレクトリ構造と install I/F は揃った。
2. project-level instructions と sync source の責務縮小方針が明示されている
  - **達成（current phase）**。`project-doc-bootstrap` から target project へ `agent_common_master.md`、`agent_sync_guide.md`、sync script を初期配置する導線を明示し、repo 直下 / template 側は follow-up として分離した。
3. docs bootstrap skill の templates / references / wrapper 構造が明示されている
   - **達成**。`project-doc-bootstrap/{SKILL.md,bin/,references/,templates/}` が揃っている。
4. shared common と `ai-review-response-workflow` 専用 reference の配置方針、および user-level skill の検証方針が定義されている
   - **達成**。core workflow skill では shared common hydrate が成立。`ai-review-response-workflow` の `review_checkpoints.md` 同梱も実装済み。設計書 Section 7.2 / 7.3 / 7.4 の更新も完了。残り Low-5（Section 7.4 line 366 の残骸）のみ。
5. `skill_catalog.md` 削除 ripple の具体対象が列挙されている
  - **達成（設計）**。repo 直下 / template 側の ripple 対象を follow-up として列挙し、current phase では bootstrap templates が `skill_catalog.md` を再導入しないことを要件化した。

## 6. 推奨次アクション

### 当初リスト（履歴）

1. Critical-1 を最優先で `.gitignore` に negation を追加し、`user-agent-assets/bin/` を git 追跡対象に戻す（30 分以内で可能）
2. Design-Doc-Update-1 として設計書 Section 7.2 / 7.3 / 7.4 を新方針（suite skill は他 skill の同時 install を前提にし、procedure をコピーしない）に書き換え、`meta.md` の `related_commits` に追記する
3. High-3 の `chmod +x` 対応を install script に追加し、wrapper の実行可否を smoke test
4. High-1 / High-2 を `meta.md` の `impl_status` を `in_progress` に更新したうえで Phase 4 のタスクとして再着手
5. 上記が完了した後で、設計 Section 13.1 の検証 1〜8 を Phase 5 として実施

### 再検証後の追加アクション（2026-05-09 方針更新後）

1. Phase 5 検証として、`project-doc-bootstrap` を使って隔離した target project へ docs / instructions / `sync_agent_instructions.*` を配置し、`scripts/sync_agent_instructions.sh --help` と placeholder listing を確認する
2. `pwsh` が利用できる環境で `install_user_agent_assets.ps1 -DryRun`、`copy_doc_templates.ps1`、target project 側 sync script の PowerShell 実行を確認する
3. repo 直下 / 既存 template の薄化、`skill_catalog.md` ripple、script 名整理は、移行完了後の follow-up として別変更系列で扱う

1 は実施済み。残作業は 2 と 3。

## 7. 総合判定

### 当初判定（履歴）

- **Critical 1**（`.gitignore` 衝突）はコミット時点で配布物が欠落するため即修正が必須
- **High 3** は設計受け入れ条件の達成可否に直結するため、Phase 4 完了前に解決必須
- **Design-Doc-Update 1** は実装変更ではなく設計書の追従更新。Phase 5 検証前に確定させ、後続レビューで再指摘されないようにする
- **Medium 5** / **Low 4** は Phase 4 〜 Phase 5 で順次解消可能
- 現状は Phase 4 実装の中盤段階であり、設計と実装の差分を `meta.md` および本 review に反映したうえで段階的に閉じれば、Phase 5 の smoke test に進める見通し

### 再検証後の判定（2026-05-09 方針更新後）

- current phase は `project-doc-bootstrap` を起点に target project へ docs / instructions / sync script を初期配置する流れでまとまり、repo 直下 / 既存 template の ripple は follow-up に分離された
- user-level assets 側の blocking finding は解消済みで、残課題は `pwsh` 不在による PowerShell 実行検証未了と Low-1 / Low-2 / Low-4 の非 blocking 項目が中心である
- 結論: **Phase 5 では bootstrap 済み target project を用いた導線確認を優先する**。repo 直下 / template の薄化や script rename は、移行完了後に別変更系列で扱うのが妥当

### 再々検証後の判定（2026-05-09 Claude、コミット `c2334032f...`）

- **Critical-2 解消**: `rebuild_user_agent_skills.py` に `REPLACEMENT_GUARDS` placeholder 退避方式を導入し、`~/.agentic-project-templates/` を保護したまま session 名のみ短縮（`agentic-orchestrator` / `agentic-review-${TOPIC}` / `agentic-claude-${TOPIC}`）。再 build 後の `grep -rn '~/.agentic[^-]' user-agent-assets/skills/` も 0 件で、構造的に regression が再発しない設計
- **Low-5 解消**: 設計書 Section 7.4 line 366 の `workflow_phase_library/README.md` 残骸を `suite skill には workflow_phase_library を追加配置しない` へ書き換え
- **High-2 方針更新で閉じ**: design.md Section 4.1 / 4.2 / 5.3 / 6.3 / 8.1 / 8.3 / 8.4 / 10 / 11.1 / 11.2 / 12.2 / 12.3 / 14 / 15 を `current phase` と `移行完了後 follow-up` に分けて再構成。新 Section 8.4「想定ユーザフロー」がユーザ補足の 1〜5 ステップを明文化
- **新ユースケースの実証**: 隔離 target project に対する `bash copy_doc_templates.sh --language python` → `bash sync_agent_instructions.sh` のパイプラインが手動 smoke test で成立。docs / instructions / scripts の配布、placeholder scan 動作、sync 実行による生成物 3 種の再生成までを確認
- **rebuild 副作用の解消**: `preserve_manual_skills` / `restore_manual_skills` により、`project-doc-bootstrap` のような generator 対象外 skill が再 build で消えないことを md5 一致で検証
- **残 Low**:
  - Low-7: PowerShell 版 wrapper / installer の実検証が `pwsh` 不在のため未実施
- **結論**: blocking issue は解消済み。**Phase 5 smoke test に進める**。残 Low は Phase 5 / 6 の中で順次解消すれば足りる。Phase 5 の smoke test に下記の追加を推奨:
  - `grep -rn '~/.agentic[^-]' user-agent-assets/skills/` が 0 件であることを CI / local で確認
  - `pwsh` 環境での `bin/copy_doc_templates.ps1` 動作と `install_user_agent_assets.ps1 -DryRun` 動作確認
  - target project の bootstrap → sync 往復が `--mode missing` の前提下で idempotent であること（Low-2 の挙動明文化と併せる）

### 再々々検証後の判定（2026-05-09 Claude、コミット `986c735a...`）

- **Low-6 解消**: `copy_doc_templates.{sh,ps1}` の placeholder scan を `docs` のみから `docs` + `instructions` + 既存生成物 3 種へ拡張。`scan_targets` 配列ベースで存在する対象だけを走査し、末尾に sync 後の再 scan ガイドを出力。SKILL.md のチェック文言も `docs / instructions` へ更新済み
- **Low-7 構造解消（実行検証は Phase 5 へ持ち越し）**: PowerShell 版 placeholder scan を `.sh` 版と等価に書き換え。さらに `sync_agent_instructions.ps1` の `param()` が `Set-StrictMode` / `$ErrorActionPreference` の後ろに置かれていた **PowerShell parse error 必至の hidden bug** を修正（`param()` を script 先頭コメント直後へ移動）。design.md Section 13.1 #4 に `pwsh -File scripts/sync_agent_instructions.ps1 -Help` の検証項目も追加
- **Low-8 解消**: `agent_sync_guide.md:56` に `sync 実行時は生成物 3 種を上書きするため、手編集した差分は保持されない` を追加し、契約を明文化
- **End-to-end smoke test**: 隔離 target project で bootstrap → sync → 再 scan が期待どおり動作。bootstrap 直後に `instructions/agent_common_master.md` の placeholder が、sync 後に `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の placeholder がそれぞれ報告される
- **新規 finding**: なし
- **結論**: 当初の Critical 1 / High 3 / Medium 5 / Low 4 / Design-Doc-Update 1 と、再検証で発生した Critical-2 / Low-5 / Low-6 / Low-7 / Low-8 の **すべてが解消済み**。Phase 4 完了条件を満たした状態で Phase 5 smoke test に進める

### PowerShell 実行検証後の判定（2026-05-09 Claude、`pwsh 7.6.1` 導入後）

- Phase 5 持ち越しだった Low-7 の実行検証を、ローカル `pwsh 7.6.1` で独立実施した
- 検証項目（§ 1.6.3）の 9 件すべてが期待どおり成功:
  - bootstrap (`copy_doc_templates.ps1`)
  - sync (`sync_agent_instructions.ps1 -Help` / 既定 -All)
  - sync 後再 scan による Low-6 動作確認
  - install dry-run（既定 / target 絞り込み / 不正 target validation / whitespace tolerance）
  - 実 install での wrapper +x bit 保持確認
- 観察事項として、`install_user_agent_assets.ps1` には `.sh` 版にある defensive な `chmod 755` 相当が無く、source の mode に依存する点を記録（POSIX で source が +x を失った場合の復帰能力に非対称が残る）。Phase 5 完了後の follow-up メモとして残し、blocking finding にはしない
- **結論**: PowerShell 系もすべて実動作確認済み。**Phase 4 のオープン項目はゼロ**となり、Phase 5 smoke test 完了 → Phase 6 完了処理へ進める状態
