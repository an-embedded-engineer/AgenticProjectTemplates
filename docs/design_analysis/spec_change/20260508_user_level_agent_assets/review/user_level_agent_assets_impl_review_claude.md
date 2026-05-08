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
  - `project-doc-bootstrap` skill と project-level ripple（`agent_common_master.md` 薄化、`skill_catalog.md` 削除、sync script 縮小）が未着手
  - `bin/` ディレクトリが既存 `.gitignore` の `bin/` ルールに巻き込まれており、コミット時に wrapper が消失する致命的な問題がある
- 総合判定: Critical 1 / High 3 / Medium 5 / Low 4 / Design-Doc Update 1（旧 High-3 を分離）

  ## 1.1 対応状況（2026-05-09 更新）

  | finding | 状況 | 対応メモ |
  |---|---|---|
  | Critical-1 | 対応済み | `.gitignore` へ `user-agent-assets/bin/**` と `user-agent-assets/skills/*/bin/**` の negation を追加し、wrapper を commit 対象へ戻した |
  | High-1 | 対応済み | `project-doc-bootstrap` を実装し、`workflow_selection.md` は削除して `common_agent_principles.md` の参照も整理済み |
  | High-2 | 対応済み | root / Python / C# の `agent_common_master.md` を薄い index 化し、sync script を instruction output 再生成専用へ縮小した |
  | Design-Doc-Update-1 | 対応済み | 設計書 Section 6.1 / 7.2 / 7.3 / 7.4 を suite skill slim payload 方針へ更新した |
  | High-3 | 対応済み | shared shell wrapper の source 実行ビット付与と install 時 `chmod 755` を追加した |
  | Medium-1 | 対応済み | `workflow_selection.md` 残置をやめ、standalone skill 化もしない方針に合わせた |
  | Medium-2 | 対応済み | generated `SKILL.md` の project-level docs 直接参照を一般化し、project 固有 rules path を除去した |
  | Medium-3 | 対応済み | Windows wrapper を exe 優先 + Python fallback に変更し、現 payload と整合させた |
  | Medium-4 | 対応済み | generator 側で project 固有 wording と固定検証文言を汎化した |
  | Medium-5 | 対応済み | `scripts/rebuild_user_agent_skills.py` に runtime helper 同期処理を追加した |

  備考:

  - `pwsh` がローカルに無いため、PowerShell 実行系の実検証は未了

## 2. 実装と設計の対応評価

| 設計章 | 実装対応箇所 | 評価 | 備考 |
|---|---|---|---|
| 4.1 user-level 正本ディレクトリ | `user-agent-assets/` | ⚠️ | `project-doc-bootstrap/` 欠落、`instructions/workflow_selection.md` が設計外で追加されている（Critical-1 / High-1 / Medium-1） |
| 4.2 project-level に残すもの | 未着手 | ❌ | root / template の薄化に未着手（High-2） |
| 4.3 `agent_common_master.md` After 構成 | 未着手 | ❌ | root / Python / C# とも未編集（High-2） |
| 5 コンポーネント責務と依存方向 | install / runtime / skills の配置 | ⚠️ | 一部 `SKILL.md` が `docs/rules/coding_rules.md` 等の project-level docs を直接索引しており、依存方向の禁止規定（Section 5.2）に抵触する余地がある（Medium-2） |
| 6.1-6.2 install 先・I/F | `install/install_user_agent_assets.{sh,ps1}` | ✅ | `--dry-run`、`missing` default、`--targets`、`--source-root` を実装済み |
| 6.3 sync script の責務縮小 | `scripts/sync_agent_skills.*` | ❌ | 未着手（High-2） |
| 6.4 shared helper 配布 | `bin/` と `runtime/` | ⚠️ | 配置は設計通りだが gitignore と実行権限の問題あり（Critical-1 / Medium-3） |
| 6.5 / 7.3 shared common hydrate | `install_user_agent_assets.{sh,ps1}` の hydrate ロジック | ✅ | core workflow skill では設計通りに動作。suite skill 群は新方針（procedure 非同梱）に伴い hydrate 対象外として扱う（Design-Doc-Update-1） |
| 7.2 skill 別 dependency map | `scripts/rebuild_user_agent_skills.py` の `WORKFLOW_SKILLS` | ⚠️ | 4 つの suite skill（review automation × 2 + orchestrator × 2）の payload は意図的に縮小されており、設計書 Section 7.2 / 7.3 / 7.4 を新方針に合わせて更新する必要がある（Design-Doc-Update-1） |
| 7.4 `workflow_selection.md` 除外 | `user-agent-assets/instructions/workflow_selection.md` | ❌ | 「user-level skill の `references/` には移さない」は守られているが、`instructions/` 直下に追加されており `common_agent_principles.md` から相対参照されている（High-1） |
| 7.5 `SKILL.master.md` からの一般化 | `rebuild_user_agent_skills.py:rewrite_text` | ⚠️ | `docs/procedure/` → `references/procedure/` 等のパス書換は実施しているが、`AgenticProjectTemplatesの` のような project 名や `Python pytest と .NET build/test` のような project 固有チェックが残置（Medium-4） |
| 8 docs bootstrap skill | （未実装） | ❌ | `project-doc-bootstrap/` skill 自体が存在しない（High-1） |
| 9 fallback を持たない方針 | （実装スコープ的には何もしない） | ✅ | `.github/skills/` 等への workspace fallback 生成は行っていない |
| 10 `skill_catalog.md` ripple | 未着手 | ❌ | `instructions/agent_common_master.md` 等から `skill_catalog.md` / `docs/procedure/` 参照が残置（High-2） |
| 11.1 実装単位の進捗 | 1〜3 のみ部分着手 | ⚠️ | 4 (project-doc-bootstrap) / 5 (sync 薄化) / 6 (skill_catalog ripple) / 7 (smoke test) は未着手 |
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

設計 Section 14 の受け入れ条件と現状の充足度:

1. user-level 正本ディレクトリ、install script、workflow skill `references/` の構造が明示されている
   - **部分達成**。ディレクトリ構造と install I/F は揃っている。一方で `project-doc-bootstrap` が欠落しているため、構造上は不完全。
2. project-level instructions と sync source の責務縮小方針が明示されている
   - **未達成**。root / template の `agent_common_master.md` と sync script は無修正。
3. docs bootstrap skill の templates / references / wrapper 構造が明示されている
   - **未達成**。`project-doc-bootstrap/` skill 自体が無い。
4. shared common と `ai-review-response-workflow` 専用 reference の配置方針、および user-level skill の検証方針が定義されている
   - **達成（設計書更新が前提）**。core workflow skill では shared common hydrate が成立。`ai-review-response-workflow` の `review_checkpoints.md` 同梱も実装済み。suite skill 群は新方針で hydrate 対象外として整合済みだが、設計書 Section 7.2 / 7.3 / 7.4 の更新が必要（Design-Doc-Update-1）。
5. `skill_catalog.md` 削除 ripple の具体対象が列挙されている
   - **設計には列挙されているが実装は未着手**（High-2）。

## 6. 推奨次アクション

1. Critical-1 を最優先で `.gitignore` に negation を追加し、`user-agent-assets/bin/` を git 追跡対象に戻す（30 分以内で可能）
2. Design-Doc-Update-1 として設計書 Section 7.2 / 7.3 / 7.4 を新方針（suite skill は他 skill の同時 install を前提にし、procedure をコピーしない）に書き換え、`meta.md` の `related_commits` に追記する
3. High-3 の `chmod +x` 対応を install script に追加し、wrapper の実行可否を smoke test
4. High-1 / High-2 を `meta.md` の `impl_status` を `in_progress` に更新したうえで Phase 4 のタスクとして再着手
5. 上記が完了した後で、設計 Section 13.1 の検証 1〜8 を Phase 5 として実施

## 7. 総合判定

- **Critical 1**（`.gitignore` 衝突）はコミット時点で配布物が欠落するため即修正が必須
- **High 3** は設計受け入れ条件の達成可否に直結するため、Phase 4 完了前に解決必須
- **Design-Doc-Update 1** は実装変更ではなく設計書の追従更新。Phase 5 検証前に確定させ、後続レビューで再指摘されないようにする
- **Medium 5** / **Low 4** は Phase 4 〜 Phase 5 で順次解消可能
- 現状は Phase 4 実装の中盤段階であり、設計と実装の差分を `meta.md` および本 review に反映したうえで段階的に閉じれば、Phase 5 の smoke test に進める見通し
