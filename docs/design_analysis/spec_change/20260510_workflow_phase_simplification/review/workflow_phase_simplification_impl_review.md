# workflow Phase 簡略化 実装レビュー

**レビュー日**: 2026-05-10
**対象 commit**: `262e7e0838fe2c7d60c46d0499fe9ad1f5127df7`
**対象 issue-dir**: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/`
**対象 TODO**: `docs/todo/todo.md` TODO-2026-001
**対象 ADR**: `docs/adr/0001_workflow_phase_simplification.md`
**レビュー範囲**: shared common phase library / 5 種 core workflow / wbs-planning-workflow / review automation 系 skill / orchestrator 系 skill / project-level `docs/design_analysis/README.md` / Python・C# bootstrap template `docs/design_analysis/README.md` / ADR-0001
**チェックリスト**: `ai-review-response-workflow` skill 同梱 `references/procedure/review_checkpoints.md`

---

## 概要

`TODO-2026-001` に基づき、core workflow 5 種を従来の 7 Phase（plan / design / impl / docs 反映 / completion）から 4 ゲート構成（Phase 0 / 1 / 2 設計 / 3 実装+恒久 docs / 4 動作確認+完了処理）へ簡略化する仕様変更の実装レビューを行った。

shared common phase library、5 種 core workflow procedure と focus 文書、`wbs-planning-workflow` 新設、review automation / orchestrator 系 skill、ADR-0001 起票、project-level / bootstrap template の `docs/design_analysis/README.md` がいずれも 4 ゲート構成へ更新されており、過去方式（plan 文書、`plan_status`、Phase 5/6、`docs_review` 命名など）を知らずに現行 workflow 文書だけで運用できる状態に整理されている。

未解決指摘は 2 件（いずれも軽微）。重大・中程度の指摘はなし。指摘 2 件は本レビューで指摘するに留め、対応は本 spec-change の Phase 4-b で行うか、別 follow-up として切り出すかは承認者判断に委ねる。

---

## 1. 齟齬・不整合

### 1.1 bootstrap template の `diff.zip` 記載が project-level / SKILL.md / shared common と不整合

**場所**:

- `user-agent-assets/skills/project-doc-bootstrap/templates/python/docs/design_analysis/README.md:78`
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/docs/design_analysis/README.md:78`

**bootstrap template の記載**:

> 4. ソース差分レポートは `diff.zip` と `report.md` を課題ディレクトリ直下に配置する

**project-level / SKILL.md / shared common の当時の記載**:

- `docs/design_analysis/README.md:78`: `report.md` を配置し、`diff.zip` は必要に応じて追加する表記
- `user-agent-assets/skills/spec-change-workflow/SKILL.md:38` ほか 5 種 SKILL.md 第 10 項: `report.md` と必要時の `diff.zip` を生成する表記
- `user-agent-assets/shared/references/procedure/workflow_phase_library/common/phase_4_verification_and_completion.md:32`: `report.md` を作成し、`diff.zip` の追加条件が未明確な表記

**差異**: project-level / SKILL.md / shared common phase library は `diff.zip` の必要条件が曖昧で、bootstrap template の Python / C# 双方の README は `diff.zip` を `report.md` と並列に記載しており、常に両方必須に読める。実際の方針は、core workflow の差分・変更レポートを `change_report.md` として常に作成し、ソース変更を含む場合は `diff.zip` も必須、ドキュメント更新や調査のみなどソース以外の変更だけの場合は `diff.zip` を省略可である。

**推奨対応**: project-level / Python / C# 双方の README 第 4 項を、core workflow の差分・変更レポートは `change_report.md` として配置し、ソース変更を含む場合は `diff.zip` も必須、ソース以外の変更だけの場合は `diff.zip` を省略可、と分かる表記へ変更する。あわせて標準ファイル構成ブロックでも `change_report.md` と `diff.zip` の条件を明示する。

**対応**: Python / C# 双方の bootstrap template README と project-level README を、core workflow の差分・変更レポートは `change_report.md` として配置し、ソース変更を含む場合は `diff.zip` も必須、ソース以外の変更だけの場合は `diff.zip` を省略可、という表記へ統一した。

**重要度**: 軽微（ファイル数 2、文言 1 行）。

---

### 1.2 `meta.md` テンプレートに `status` フィールドが欠落

**場所**:

- `docs/design_analysis/README.md:61-71`
- `user-agent-assets/skills/project-doc-bootstrap/templates/python/docs/design_analysis/README.md:61-71`
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/docs/design_analysis/README.md:61-71`

**現状の README テンプレート**:

```yaml
---
title: "<課題タイトル>"
category: "<spec_change|new_feature|fix_issues|issue_resolution|refactoring|wbs|research_analysis>"
created: "<YYYY-MM-DD>"
design_status: "<draft|in_review|done>"
impl_status: "<not_started|draft|in_review|done>"
completion_status: "<not_started|in_progress|done>"
related_commits: []
---
```

**参照側の要求**:

- `user-agent-assets/shared/references/procedure/workflow_phase_library/common/phase_1_branch_and_meta.md:7-16`: 最低限記録すべき項目として `title` / `created_date` / `category` / `components` / **`status`** / `design_status` / `impl_status` / `completion_status` / `related_commits` を列挙
- `phase_3_impl_and_docs_review.md:23`: 「`meta.md` の `status` を `implemented` に更新し、反映結果をコミットする」
- `phase_4_verification_and_completion.md:48`: 「マージ後に `meta.md` の `status` を `merged` に更新」
- 実装結果の例: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/meta.md:9` で `status: "implemented"` を持つ

**差異**: shared common phase library と実装結果の `meta.md` は `status` フィールド（`<draft|implemented|merged>` 等の topic ライフサイクル状態）を持つ運用前提だが、project-level / bootstrap の README テンプレートには `status` 行が無く、`components` も欠けている。新規 topic 立ち上げ時にテンプレートだけを参照すると `status` を入れ忘れて、Phase 3 / 4 の status 更新 step が機能しない可能性がある。

**推奨対応**: project-level / Python / C# 3 か所の README の meta.md テンプレートに以下を追加する。

```yaml
components: []
status: "<draft|implemented|merged>"
```

`status` の値域は shared phase library の使用実績（`draft` -> `implemented` -> `merged`）に合わせ、必要なら README 末尾に値域の説明を 1 行追加する。

**対応**: project-level / Python / C# の 3 か所の README の `meta.md` テンプレートへ `components: []` と `status: "<draft|implemented|merged>"` を追加した。

**重要度**: 軽微（テンプレート 3 か所、各 2 行追加）。

---

## 2. ドキュメント不足

該当なし。本コミットで以下が網羅されている:

- ADR-0001 の Status / Context / Decision / Consequences / References
- `docs/adr/README.md` の ADR 索引（topic / component / keywords）
- shared common phase library の `phase_1` / `phase_2_design_review` / `phase_3_impl_and_docs_review` / `phase_4_verification_and_completion` 4 文書
- 5 種 core workflow の `phase_2_design_focus` / `phase_3_impl_and_docs_focus` / `phase_4_completion_focus`
- `wbs-planning-workflow` の SKILL.md と `wbs_planning_workflow.md`（Phase 0-4、`wbs.md` 表構造、依存・推奨 workflow・docs 更新先・検証観点を含む）
- `ai-review-response-workflow` の工程分類 `design / impl / completion`、出力ファイル命名 `<topic>_design_review.md` / `<topic>_impl_review.md` / `<topic>_completion_review.md`（optional）
- review automation 系 skill（`claude-review-automation` / `copilot-review-automation`）の review 文書命名と Phase 4-a STOP / Phase 4-c merge 承認
- orchestrator 系 skill（`autonomous-workflow-orchestrator` / `copilot-cli-workflow-orchestrator`）の禁止事項に「Phase 4-a のユーザ動作確認 STOP をスキップしてはならない」、Step 4 の Phase 4-a ゲート、Step 5 の Phase 4-c マージ承認
- bootstrap template `docs/design_analysis/README.md` の 4 ゲート構成・wbs/ ディレクトリ・新 status 体系

---

## 3. 改善提案

### 3.1 spec-change の `phase_4_completion_focus.md` レビュー観点が古い前提を内包しないかの再点検

**場所**: `user-agent-assets/skills/spec-change-workflow/references/procedure/workflow_phase_library/spec_change/phase_4_completion_focus.md:18-20`

**現状の記載**:

> ## レビュー観点
>
> - `todo` から archive へ移すのに必要な情報が揃っているか
> - 完了証跡と恒久ドキュメント更新の対応が追跡できるか

**指摘**: 新方式では恒久ドキュメント更新は Phase 3 で実施され、Phase 4-b では archive / history / merge 前確認が中心になる。Phase 4 の focus が「恒久ドキュメント更新の対応」を含むと、Phase 4 で恒久 docs を再度更新するのではないかという誤読を生む可能性がある。「恒久ドキュメント更新の **追跡可能性**」（Phase 3 結果との整合確認）であることが明確になる文言に整理すると親切。

**推奨対応（任意）**: 例えば「Phase 3 で更新した恒久ドキュメントと、archive / history / report の追跡が一貫しているか」のように Phase 境界が読み取れる文言にする。

**対応**: spec-change の `phase_4_completion_focus.md` のレビュー観点を、Phase 3 で更新した恒久ドキュメントと archive / history / report の追跡整合を確認する文言へ変更した。

**重要度**: 軽微（文言調整、機能影響なし）。本レビューでは指摘するに留め、必須対応とはしない。

---

### 3.2 `meta.md` の `related_commits` 集約タイミングの実例不在

**場所**: `docs/design_analysis/spec_change/20260510_workflow_phase_simplification/meta.md:13`

**現状**: `related_commits: []` で空のまま。本 topic 自身が「core workflow の `related_commits` を completion で集約する」設計の最初の適用例だが、`completion_status: in_progress` のまま空配列のため、completion 集約方針を読み手が体感しにくい。Phase 4-b で `262e7e0` を含む主要 commit が記録されれば本指摘は自然解消する。

**推奨対応（任意）**: Phase 4-b で `meta.md` の `related_commits` に主要 commit（Phase 1 ブランチ・meta、Phase 2 design / design_review、Phase 3 impl / impl_review、Phase 4-b 完了処理 / report）を集約する際、`Phase <N> <要約>` 形式の範例として残ることを意識する。

**重要度**: 情報提供（実装の指摘ではなく Phase 4-b への申し送り）。

---

## 4. 整合性確認済み項目

| 項目 | 確認結果 |
|------|----------|
| 4 ゲート構成（Phase 0/1/2/3/4）が shared common phase library に実装されている | ✓ 整合 |
| Phase 4-a 動作確認 STOP / 4-b 完了処理 / 4-c merge 承認の内部 step が `phase_4_verification_and_completion.md` に明記されている | ✓ 整合 |
| Phase 4-a で `[NEED_USER_VERIFICATION]` を停止シグナルとして使う旨が明記されている | ✓ 整合 |
| 5 種 core workflow procedure が新 common 手順と新 focus 文書を参照している | ✓ 整合（`spec_change_workflow.md:21-23` ほか） |
| 5 種 SKILL.md の禁止事項・必須チェックが新 status 体系（`design_status` / `impl_status` / `completion_status`）に揃っている | ✓ 整合 |
| review 文書命名 `<topic>_design_review.md` / `<topic>_impl_review.md` / optional `<topic>_completion_review.md` が `ai-review-response-workflow` / `claude-review-automation` / `copilot-review-automation` で一致 | ✓ 整合 |
| `claude-review-automation` SKILL.md の description / 適用 Phase が「Phase 2/3 + optional completion」へ更新されている | ✓ 整合（行 3, 11, 70-77） |
| `copilot-review-automation` SKILL.md の description / 適用 Phase が「Phase 2/3 + optional completion」へ更新されている | ✓ 整合（行 4, 91-98, 220, 228） |
| orchestrator 系 SKILL.md の禁止事項が「Phase 4-a のユーザ動作確認 STOP をスキップしてはならない」に揃っている | ✓ 整合（`autonomous-workflow-orchestrator/SKILL.md:47`、`copilot-cli-workflow-orchestrator/SKILL.md:41`） |
| orchestrator 手順本体の Step 3 / Step 4 / Step 5 が Phase 2/3 review、Phase 4-a 動作確認、Phase 4-c merge 承認に再構成されている | ✓ 整合（`autonomous_workflow_orchestrator.md:177-405`） |
| `ai-review-response-workflow` の工程分類が `design` / `impl` / `completion` に揃っている | ✓ 整合（行 12, 36-43, 128, 130） |
| `wbs-planning-workflow` SKILL.md と `wbs_planning_workflow.md` が大規模変更の work package 分解 skill として独立 | ✓ 整合（成果物配置 `docs/design_analysis/wbs/<yyyymmdd>_<topic>/`、`wbs.md` の表構造、推奨 workflow / 依存 / 完了条件 / docs_targets / verification_points を必須化） |
| `wbs-planning-workflow` が install 対象 skill 群に含まれる（installer の `for skill_dir in "${skill_root}"/*` 経由） | ✓ 整合（`install_user_agent_assets.sh:155-161, 182-187, 192-198`、`change_report.md:34` で installer dry-run 確認済み） |
| `docs/design_analysis/README.md` が 4 ゲート構成・wbs/ 区分・completion_review optional・`related_commits` の completion 集約方針を説明している | ✓ 整合（行 28-58, 73-82） |
| Python / C# bootstrap template の `docs/design_analysis/README.md` が project-level と同一方針へ同期している | ✓ 整合（4 ゲート構成・wbs 区分・status 体系は揃っている） |
| ADR-0001 が `docs/adr/README.md` の索引へ追加されている（topic / component / keywords が一致） | ✓ 整合（`docs/adr/README.md:55`） |
| ADR-0001 が Phase 構成・design 文書必須章・恒久 docs 更新タイミング・`related_commits` 集約方針・wbs 分離を記述している | ✓ 整合 |
| shared common phase library の hydrate 経路が installer に維持されている | ✓ 整合（`hydrate_workflow_phase_library_common` 関数が target skill の `workflow_phase_library` 配下へ shared common を copy） |
| `plan_status: N/A` 等の移行期互換 status が core workflow / shared phase library / SKILL.md / README / meta.md template から完全に削除されている | ✓ 整合（残存は historical research_analysis 文書 2 種のみ。`docs/todo/todo.md:37` の `phase0_decisions` は判断選択肢の記録で、運用に再導入されてはいない） |
| `phase_2_plan_review.md` / `phase_5_verification_and_docs.md` / `phase_6_completion.md` / `phase_2_plan_focus.md` / `phase_3_design_focus.md` / `phase_4_impl_focus.md` / `phase_5_sync_focus.md` の旧 common / focus 文書が 5 種すべてで削除されている | ✓ 整合（差分 stat で 6 ファイル × 5 workflow = 30 文書相当が削除または rename） |
| 過去方式（plan 文書、`plan_status`、Phase 5/6 user approval gate、`docs_review` 命名）の前提知識なしに現行 workflow 文書だけで実行可能 | ✓ 整合（残存参照は historical 文書と `research-analysis-workflow` 内 Phase 5 のみ。後者は `change_report.md:37` で意図的非移行が明記） |
| `research-analysis-workflow` の Phase 5 表記が同 workflow 固有の現行手順として残されている | ✓ 整合（`research_analysis_workflow.md:93, 116`、`spec_change/.../change_report.md:37` の宣言と一致） |
| 設計書（`design/<topic>_design.md`）が要求・採用方針・非対象・影響範囲・恒久ドキュメント更新先・検証観点を網羅 | ✓ 整合 |
| 実装記録（`impl/<topic>_impl.md`）が実装内容・決定事項・検証コマンドを記録 | ✓ 整合 |
| `change_report.md` が変更概要・検証結果（installer dry-run / Python pytest / .NET build / ExtractGitDiff build）・残存参照チェック結果をまとめている | ✓ 整合 |
| `meta.md` フロントマターが新 status 体系（`design_status: done` / `impl_status: done` / `completion_status: in_progress`）と `adr` フィールドを含む | ✓ 整合 |

---

## 5. 対応優先度

| 優先度 | 項目 | 理由 |
|--------|------|------|
| 軽微（要対応推奨） | §1.1 `diff.zip` の条件付き必須表記への修正 | 本コミットで bootstrap template の README は更新されており、同じ更新範囲で project-level と揃えるのが自然 |
| 軽微（要対応推奨） | §1.2 meta.md テンプレートへの `status` / `components` 追加 | `phase_1_branch_and_meta.md` が要求し、Phase 3 / 4 で更新する `status` がテンプレートに無いと運用ミスを誘発しやすい |
| 任意 | §3.1 `phase_4_completion_focus.md` のレビュー観点文言 | 機能影響なし。新方式の Phase 境界をより明確にする文言整理 |
| 情報提供 | §3.2 `related_commits` の completion 集約実例 | Phase 4-b で自然解消。指摘ではなく申し送り |

---

## 6. 結論

`workflow Phase 簡略化` 仕様変更の実装は、shared common phase library から ADR、bootstrap template、review automation / orchestrator 系 skill、`wbs-planning-workflow` 新設まで一貫しており、過去方式の前提知識なしに新 workflow 文書だけで運用できる状態に達している。`plan_status: N/A` などの移行期互換 status は core workflow から完全に取り除かれており、残存は historical research_analysis 文書のみで意図的非移行と整合している。4 ゲート構成・review 文書命名・Phase 4-a/4-b/4-c の STOP 条件・`wbs-planning-workflow` の独立性も観点通り。

未解決指摘 2 件（§1.1 `diff.zip` の条件表記、§1.2 meta.md テンプレートの `status` 欠落）はいずれも軽微で、文言・テンプレート整備の範囲。重大・中程度の指摘はなく、本実装は **Phase 4 ゲート進行可** と判定する。

軽微指摘 2 件への対応は、本 spec-change の Phase 4-b で同時整理するか、別 follow-up todo として切り出すかは承認者判断に委ねる。

---

## 8. 指摘対応再確認（commit `aebc053`）

**確認日**: 2026-05-10
**初回対応 commit**: `aebc053dd2fbe080a26ea4891bee388a0fb16c4e`（`docs: address workflow phase review comments`）
**方針補正**: 2026-05-11 にユーザ指摘を受け、core workflow の差分・変更レポートは `change_report.md` とし、`diff.zip` は単純な optional ではなく、ソース変更を含む場合は必須、ドキュメント更新や調査のみなどソース以外の変更だけの場合は省略可、として再整理した。

| 指摘 | 確認結果 |
|------|----------|
| §1.1 `change_report.md` と `diff.zip` の条件付き必須表記への統一 | ✓ 解消（project-level / Python / C# の README 第 4 項が、core workflow の差分・変更レポートは `change_report.md` として配置し、ソース変更を含む場合は `diff.zip` も必須、ソース以外の変更だけの場合は `diff.zip` を省略可とする表記へ更新された。標準ファイル構成も `change_report.md` と「ソース変更がある場合は必須」の `diff.zip` へ揃った） |
| §1.2 meta.md テンプレートの `status` / `components` 追加 | ✓ 解消（project-level / Python / C# の 3 か所すべての meta.md テンプレートに `components: []` と `status: "<draft|implemented|merged>"` が追加された） |
| §3.1 `phase_4_completion_focus.md` レビュー観点の文言整理 | ✓ 解消（spec-change の `phase_4_completion_focus.md:19` が「Phase 3 で更新した恒久ドキュメントと、archive / history / report の追跡が一貫しているか」へ更新され、Phase 境界の誤読リスクが解消した） |
| §3.2 `related_commits` 集約実例 | 申し送り維持（Phase 4-b で自然解消する情報提供） |

未解決指摘なし。本実装レビューは **承認** とする。

> **APPROVED**: 全要対応指摘（§1.1 / §1.2 / §3.1）が解消済み。本 spec-change は Phase 4-a 動作確認 STOP へ進んでよい。

---

## 7. 参考: 確認に用いたコマンド・チェック

- `git show --stat 262e7e0838fe2c7d60c46d0499fe9ad1f5127df7`（変更 62 ファイル / +836 / -648）
- `grep -rn "plan_status" --include="*.md"`（残存は historical research_analysis 内のみ）
- `grep -rn "phase_5\|Phase 5\|phase_6\|Phase 6\|phase_2_plan\|phase_3_design\|phase_4_impl\|phase_5_sync\|phase_5_verification\|phase_6_completion\|docs_review\|plan_review" user-agent-assets docs/adr docs/design_analysis/README.md docs/design_analysis/spec_change/20260510_workflow_phase_simplification --include="*.md"`（残存は `research-analysis-workflow` の Phase 5 のみ、`change_report.md:37` の宣言と整合）
- `grep -rn "wbs-planning\|wbs_planning\|wbs/" user-agent-assets --include="*.md"`（bootstrap template / wbs-planning-workflow 自身に存在、整合）
- installer の hydrate 関数（`install_user_agent_assets.sh:102-124, 155-161, 182-187, 192-198`）と shared common phase library のディレクトリ存在確認
