---
title: "ユーザレベル Agent 資産化 Phase 3 設計レビュー"
created_date: "2026-05-08"
category: spec_change_design_review
target_design: docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md
target_meta: docs/design_analysis/spec_change/20260508_user_level_agent_assets/meta.md
target_commit: fb34c225bdd21d470d6c9ab99d96157487a03750
status: approved
---

# レビュー文書: ユーザレベル Agent 資産化 Phase 3 設計

## 1. レビュー概要

- 観点
  - user-agent-assets 正本構造・install/sync 分離・references 化の設計が実装可能な粒度か
  - project-level fallback の範囲と削除条件が曖昧でないか
  - skill_catalog 削除 ripple・wrapper 方針・project-level instructions 薄化の責務境界が明確か
  - before/after 差分・依存方向・変更順序・検証方針が Phase 4 実装に十分か
  - 不要な後方互換レイヤーや曖昧なフォールバック前提になっていないか
- 参照文書
  - 承認済み計画書: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md`
  - 承認済み計画レビュー: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_plan_review.md`
  - 設計書: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md`
- 結果サマリ
  - before/after 仕様差分、install/sync 責務分離、fallback 削除条件、`skill_catalog.md` ripple は実装可能な粒度で設計されており良好
  - ただし、現行 root に存在する 2 つの orchestration skill と、それらが依存する `agent_cli_tmux.py` / `AgentCliTmux` の user-level 配布方針が設計書に不在であり、Phase 4 実装に支障が生じる
  - `agent_common_master.md` の After 構成も "薄い index" という方向のみ示されており、root / Python / C# 間で実装差が生じるリスクがある
- 総合判定: Medium 3 / Low 2

## 2. 設計全体の構造評価

| 項目 | 評価 | 備考 |
|---|---|---|
| before/after 仕様差分（Section 3） | ✅ | 6 観点で Before/After を表形式で整理。実装者が差分を把握できる |
| user-agent-assets 正本構造（Section 4.1） | ⚠️ | ツリーに 2 skill 漏れ（Medium-1 参照） |
| project-level 残置方針（Section 4.2） | ⚠️ | 役割の記述はあるが After 構成が不明（Medium-3 参照） |
| コンポーネント責務と依存方向（Section 5） | ✅ | 4 コンポーネントの責務・非責務が明示されており境界明確 |
| install/sync 分離（Section 6） | ✅ | I/F 定義・failure domain 分離の理由が記載されている |
| references 化ルール（Section 7） | ⚠️ | 振り分け基準が "必要な分だけ" で曖昧（Low-2 参照） |
| docs bootstrap 設計（Section 8） | ✅ | wrapper 方針・コピー契約が明示されている |
| fallback 設計（Section 9） | ⚠️ | 除外 3 skill の根拠が薄い（Low-1 参照） |
| skill_catalog 削除 ripple（Section 10） | ✅ | 具体ファイル名が列挙されている |
| 変更順序制約（Section 11） | ✅ | 主要な依存制約をカバーしている |
| テスト設計（Section 13） | ✅ | 8 項目の検証が測定可能な形で定義されている |
| 後方互換レイヤーの有無 | ✅ | Section 9.2 と Section 15 で "恒久運用にしない" が明言されている |

## 3. 指摘一覧

### [Medium-1] `autonomous-workflow-orchestrator` と `copilot-cli-workflow-orchestrator` の user-level 扱いが未定義

- 対象箇所
  - design.md Section 4.1（user-agent-assets/skills/ ツリー）
  - design.md Section 9.1（fallback 対象リスト）
- 理由
  - 現行 root `instructions/skills/` には、設計書に記載されていない 2 つの orchestration skill が存在する。
    - `autonomous-workflow-orchestrator`（Copilot が Codex / Claude を tmux 監視で指揮する手順）
    - `copilot-cli-workflow-orchestrator`（Copilot CLI 単体でモデル切り替えしながら指揮する手順）
  - Section 4.1 の skill ツリーはこれら 2 skill を含まず、Section 9.1 の fallback リストにも記載がない。
  - "user-level 正本化する" / "project-level に残す" / "削除対象にする" のいずれの方針も設計書に明示されていない。
  - Phase 4 実装者がこれら 2 skill を見落とすか、任意の判断で移行先を決めることになり、設計の齟齬が生じる。
- 推奨対応
  - Section 4.1 のスキルツリーに `autonomous-workflow-orchestrator` と `copilot-cli-workflow-orchestrator` を追加し、user-level 正本として移行する方針を明示する。
  - または、これらを user-level 移行の対象外とする場合は、その理由と残置先（root project-level など）を Section 4.1 の設計判断に記載する。

### [Medium-2] `agent_cli_tmux.py` / `AgentCliTmux` の user-level skill 配布方針が欠落

- 対象箇所
  - design.md Section 7.1（references 同梱ルール・bin/ 定義）
  - design.md Section 8.2（wrapper 方針）
  - plan.md Section 7.5（Phase 3 で定めるとされていた wrapper 方針）
- 理由
  - 承認済み計画（plan.md Section 7.5）では、`agent_cli_tmux` / `AgentCliTmux` を呼ぶ OS 別 wrapper または publish 済み executable の配置方針を Phase 3 設計で確定することが明示されていた。
  - `claude-review-automation` の `SKILL.master.md` は `scripts/agent_cli_tmux.py` を参照しており、`copilot-review-automation` も同様である。user-level skill 化後にこの参照先をどこに置くかが未決定のままである。
  - Section 7.1 の `bin/` の説明は "runtime 補助 wrapper が必要な場合のみ" と記述されるにとどまり、orchestration / review skill 向けの helper 配置が明示されていない。
  - Section 8.2 は docs bootstrap skill 専用の wrapper 方針であり、orchestration skill に転用可能なものかどうかが不明である。
  - この欠落があると、Phase 4 実装者は `claude-review-automation` / `copilot-review-automation` の user-level `SKILL.md` から何を呼べばよいかを自己判断するしかなく、skill 本文の参照先が不整合になるリスクがある。
- 推奨対応
  - Section 7.1 または新規 Section として、`agent_cli_tmux` / `AgentCliTmux` の user-level 配布方針を以下の観点で明示する。
    - wrapper の配置場所（各 skill の `bin/` に個別配置 vs `user-agent-assets/bin/` に共通配置）
    - macOS/Linux 向け `.sh`、Windows 向け `.ps1` の提供形式
    - install script が wrapper を user 環境のどこに配置するか（`~/.local/bin/` や PATH に通す場所など）
    - `SKILL.md` からの wrapper 呼び出し記述方針（パス絶対指定 / PATH 前提 / 環境変数）

### [Medium-3] `agent_common_master.md` の After 状態の具体構成が未定義

- 対象箇所
  - design.md Section 4.2（project-level に残すもの）
  - design.md Section 5.2（project-level instructions の責務）
- 理由
  - 現行の `agent_common_master.md`（root / Python / C# の 3 ファイル）は、共通原則（内部思考言語・コメント言語・フォールバック禁止・ADR 参照ルール等）と project 固有ルール（検証コマンド・責務境界・docs 索引）が混在している。
  - 設計書は After の役割を "薄い index、実行コマンド、project 固有制約、成果物置き場案内" と表現しているが、現行ファイルのどのセクションを保持してどのセクションを削除するかが定義されていない。
  - Section 5.2 は「user-level 共通原則を再掲しない」と明言しているが、何が "再掲" に該当するかは実装者の判断に委ねられている。
  - root / Python / C# の 3 つの `agent_common_master.md` は元々言語差があり、共通原則の削除範囲が揃わないと、実装後に 3 ファイル間で一貫性が崩れる。
- 推奨対応
  - Section 4.2 または新規 Section として、After 状態の `agent_common_master.md` が持つべき最小構成（セクション名レベル）を記載する。例えば:
    - 保持: project 名・目的、ビルド/テスト/静的解析コマンド、project 固有 docs 索引、user-level assets 利用前提の案内
    - 削除: 共通設計原則、コメント/ログ言語方針、ADR 参照の一般ルール
  - root / Python / C# 間で削除範囲を統一する方針を明示する。

### [Low-1] fallback 除外 3 skill の根拠が不明確

- 対象箇所
  - design.md Section 9.1（fallback を残す条件・設計判断）
- 理由
  - Section 9.1 は `research-analysis-workflow`、`ai-review-response-workflow`、`claude-review-automation` を fallback 必須対象から除外し、「user-level install 後運用へ寄せ、Phase 4 初期段階では fallback 必須対象に含めない」と記述している。
  - しかし、Copilot smoke test が不合格だった場合、この 3 skill は Copilot から一切呼べなくなる。これらは実用上重要な skill であり（特に `ai-review-response-workflow` と `claude-review-automation` はレビュープロセスの中核）、Copilot から利用不能になる影響の説明がない。
  - "fallback 必須対象に含めない" という判断が、"Copilot 利用者はこれら 3 skill を smoke test 完了まで使わない前提" なのか、"smoke test 不合格でも Claude / Codex 経由で代替できるため問題ない" なのかが不明確である。
- 推奨対応
  - Section 9.1 の設計判断に、除外根拠として以下を追記する。
    - 「これら 3 skill は Claude Code CLI / Codex から直接呼び出す用途が主であり、Copilot Chat からの直接起動頻度が低いため、`.github/skills/` fallback がなくても実運用上の支障が小さい」等
  - または、smoke test 不合格時にユーザへ案内する代替手順（Claude/Codex 経由で呼ぶ等）を Section 9.2 か Section 15 に補足する。

### [Low-2] skill ごとの `references/procedure/` 振り分け基準がない

- 対象箇所
  - design.md Section 7.1（references 同梱ルール）
- 理由
  - Section 7.1 は各 skill が持つべき最小構成を示しているが、"必要な分だけ `references/procedure/` へ複製する" という方針にとどまっており、具体的な振り分け対応表がない。
  - 現行 `docs/procedure/` は `workflow_phase_library/common/` と `workflow_phase_library/<workflow_type>/` 以下に多数のサブファイルを持つ。`spec-change-workflow` skill には `spec_change_workflow.md` と `workflow_phase_library/spec_change/phase_*.md` が必要だが、`workflow_phase_library/common/phase_*.md` は全 skill に共通で必要であり、これが "duplicate を許容する" の対象に当たる。
  - Phase 4 実装者が振り分けを自己判断すると、特定 skill の `references/` に必要なファイルが漏れるリスクがある。
- 推奨対応
  - Section 7.1 または付録として、代表 skill（例: `spec-change-workflow`）を例示した `references/procedure/` の最小ファイルリストを記載する。
  - 全 skill 共通で必要なファイル（`review_checkpoints.md`、`workflow_selection.md`、`workflow_phase_library/common/phase_*.md`）を "共通コピー対象" として明示し、skill 固有ファイル（`spec_change_workflow.md`、`workflow_phase_library/spec_change/phase_*.md` 等）との分類を示す。

## 4. 確認内容と問題なし部分

- **before/after 仕様差分（Section 3）**: 6 観点の表形式による整理は明快であり、実装者が現状と目標差分を把握できる ✅
- **install/sync 分離（Section 6）**: install script の I/F 設計（`--dry-run`、`--mode`、`--targets`、`--source-root`）が具体的であり実装可能。failure domain 分離の理由も明示されている ✅
- **fallback 削除条件（Section 9.2）**: 2 条件（smoke test 合格 + references 動作確認）が具体的で、削除タイミングも Phase 5 完了後と明示されている。"恒久運用にしない" が Section 15 でも確認でき、不要な後方互換レイヤーの固着を防ぐ設計になっている ✅
- **`skill_catalog.md` 削除 ripple（Section 10）**: 具体的な 7 ファイル（root CLAUDE.md、AGENTS.md、.github/copilot-instructions.md、root instructions/agent_common_master.md、Python/C# 各 agent_common_master.md、各 SKILL.master.md）が列挙されており、計画レビューの Medium-2 指摘に適切に対応している ✅
- **docs bootstrap 設計（Section 8）**: wrapper 方針（sh/ps1 優先、Python 非依存）、コピー契約（missing-only default、common 先行、placeholder 列挙）が明示されている ✅
- **依存方向の禁止（Section 5.1）**: user-agent-assets から project-level を参照しない一方向制約が明記されている ✅
- **変更順序制約（Section 11.2）**: 4 制約が主要なリスクケース（references 化前の docs/procedure 削除禁止 / dry-run 前の skill 除去禁止）をカバーしている ✅
- **テスト設計（Section 13）**: 8 項目が測定可能であり、計画の受け入れ条件に対応している ✅

## 5. Phase 4 へ渡す事項の評価

Phase 4 実装に支障をきたす未解決事項（Medium 指摘）:
1. `autonomous-workflow-orchestrator` / `copilot-cli-workflow-orchestrator` の移行方針（Medium-1）
2. `agent_cli_tmux.py` / `AgentCliTmux` の user-level 配布方針（Medium-2）
3. `agent_common_master.md` の After セクション構成（Medium-3）

これら 3 点は Phase 4 実装開始前に設計書で解消する必要がある。特に Medium-2 は複数の skill（`claude-review-automation`、`copilot-review-automation`、`autonomous-workflow-orchestrator`）の `SKILL.md` 本文の記述に直結するため、未解消のまま実装を開始すると skill 本文と helper 配置が不整合になる。

## 6. レビューラウンド履歴

- Round 1 (2026-05-08)
  - レビュー担当: Claude Sonnet 4.6 (GitHub Copilot CLI)
  - 対象コミット: fb34c22
  - 指摘: Medium 3 / Low 2
  - 状態: 指摘対応待ち → Round 2 で対応完了
- Round 2 (2026-05-08)
  - レビュー担当: Claude Sonnet 4.6 (GitHub Copilot CLI)
  - 対象コミット: c4171ce
  - 確認内容
    - Medium-1: Section 4.1 ツリーに `autonomous-workflow-orchestrator` / `copilot-cli-workflow-orchestrator` を追加。設計判断に "orchestration skill も user-level 正本化対象" を明記。Section 9.1 に両 skill の fallback 非対象根拠も追記。OK
    - Medium-2: `user-agent-assets/bin/` と `runtime/` をツリーに追加（`agentic-agent-cli-tmux.sh`、`.ps1`、`agent_cli_tmux.py`、`AgentCliTmux.exe`）。Section 6.4 として shared helper 配布設計（install 先 `~/.agentic-project-templates/`・macOS/Linux と Windows の wrapper 呼び出し方針・SKILL.md からは wrapper 経由のみ・`python`/`dotnet` 直 allowlist 禁止）を追加。skill 個別 `bin/` と shared `bin/` の分離方針も明記。OK
    - Medium-3: Section 4.3 として `agent_common_master.md` の After 構成（5 保持セクション: 目的・必須参照・project 固有ルール・生成物運用・user-level assets 利用前提 / 4 削除カテゴリ: 共通原則・ADR 参照一般ルール・フォールバック禁止一般原則・skill_catalog 横断参照）を追加。root / Python / C# 統一方針も明記。OK
    - Low-1: Section 9.1 設計判断に除外 5 skill の根拠（"Copilot Chat 日常導線より Claude/Codex/明示起動用途が主"）を追記。smoke test 不合格時の代替案内（Claude/Codex 側 user-level skill から起動・明示参照 advanced operation として扱う）も追記。OK
    - Low-2: Section 7.2 に共通コピー対象 10 ファイルを列挙。Section 7.3 に `spec-change-workflow` および `copilot-review-automation` / orchestration skill の固有ファイル例を追記。OK
  - 新規指摘: なし
  - 状態: 承認済み（Phase 4 実装への移行可）
- Round 3 (2026-05-09)
  - レビュー担当: Claude Sonnet 4.6 (GitHub Copilot CLI)
  - 対象コミット: cf4045b（docs: refine user-level agent asset migration policy）
  - 変更概要
    - 設計書: `workflow_selection.md` を `instructions/` ツリーから削除。`shared/references/procedure/` サブツリー（review_checkpoints.md + workflow_phase_library/common）を追加。Section 6.5（shared reference hydrate）新設。Section 7 を全面再構築（7.1 棚卸し原則 / 7.2 skill 別 dependency map / 7.3 shared common hydrate 条件 / 7.4 移行ルール 8 箇条）。
    - 調査レポート: "original 正本棚卸し結果（2026-05-09 追補）" セクション追加。同内容の skill 別最小コピー集合表と移行方針補正 8 箇条を追記。
  - 確認内容
    - `workflow_selection.md` 除外の一貫性: Section 6.5 設計判断・Section 7.1 原則 2・Section 7.4 移行ルール・補足すべてで "user-level skill の references/ へ移さない / 必要なら standalone skill として再定義" が統一されている。調査レポート補足・移行方針補正 rule 4 も一致。**OK**
    - `review_checkpoints.md` の ai-review-response-workflow 帰属: Section 6.5・7.1 原則 3・7.3・7.4 で "ai-review-response-workflow にだけ配置" が貫徹。調査レポート棚卸し結論 4・移行方針補正 rule 5 も一致。shared 正本パス（`user-agent-assets/shared/references/procedure/review_checkpoints.md`）が 6.5・7.3 で明示されトレース可能。**OK**
    - dependency map と shared hydrate 方針の整合: Section 7.2 の skill 別 12 行テーブルと調査レポート追補の同テーブルが完全に一致。Section 7.3 の hydrate 対象 9 skill / 不要 3 skill の分類が 7.2 の dependency map と矛盾なし。`workflow_phase_library/README.md` を `copilot-review-automation` にのみ個別保持する規則が 7.2・7.4・レポート rule 6 で一致。**OK**
    - Round 2 解消済み指摘の再発確認: Medium-1（orchestration skill 2 件）、Medium-2（agent_cli_tmux 配布方針）、Medium-3（agent_common_master After 構成）、Low-1（fallback 除外根拠）、Low-2（references 振り分け基準）—いずれも今回の変更で削除・上書きされた箇所はなく、Round 2 対応内容が維持されている。**OK**
  - 新規指摘: なし
  - 状態: **承認済み（Round 3 承認・Phase 4 実装への移行可）**
- Round 4 (2026-05-09)
  - レビュー担当: Claude Sonnet 4.6 (GitHub Copilot CLI)
  - 対象コミット: 6d96e46（docs: simplify skill payload distribution）
  - 変更概要
    - 設計書: workspace fallback 設計を "no fallback・user-level 正本修正で対応" へ全面転換（Section 9 再構築、Section 3/11/12/13/14/15 関連箇所を一括更新）。`review_checkpoints.md` を shared 配布ではなく `ai-review-response-workflow` への直接同梱へ変更（Section 4.1 ツリー・6.5・7.1/7.2/7.3/7.4 を一貫更新）。sync script から fallback 再生成責務を削除。
    - 調査レポート: `shared/` ツリーから `review_checkpoints.md` を削除。参照構造例を簡素化。補足・棚卸し結論 4・移行方針 rule 5・リスク 1 対策を一貫更新。
  - 確認内容
    - `review_checkpoints.md` の直接同梱方針（shared 経由なし）: 設計書 4.1 ツリー・6.5・7.1 原則 3・7.2 テーブル・7.3・7.4 移行ルール、レポート補足・棚卸し結論 4・移行方針 rule 5 すべてで "ai-review-response-workflow の references/procedure/ に最初から同梱する" に統一。`shared/` ツリーに `review_checkpoints.md` は残存しない。**OK**
    - `shared` = common 6 files の hydrate のみ: 設計書・レポート両ツリーで `shared/references/procedure/` 配下が `workflow_phase_library/common/` のみになった。Section 6.5 設計判断・7.3 の shared 正本 6 ファイルリスト変更なし。`review_checkpoints.md` は "common と同様の shared hydrate 対象には含めない" と明記。**OK**
    - workspace fallback なし・問題は user-level 正本修正で解決: Section 3 before/after・9.1・9.2・11.1 step 7・11.2 順序制約・12・13・14・15、レポートのリスク 1 対策すべてで "workspace fallback は持たず user-level 正本を修正して再検証する" が貫徹。sync script の fallback 再生成行も削除済み。**OK**
    - Round 2〜3 指摘の再発確認: Medium-1（orchestration skill ツリー・設計判断）・Medium-2（Section 6.4 shared helper 配布）・Medium-3（Section 4.3 After 構成）は今回の diff に触れておらず維持。Low-1 は "fallback なし" 方針への転換により懸案自体が解消（fallback 除外根拠が不要になった）。Low-2（Section 7 dependency map）は変更なし。Section 4.3 item 5 の "fallback がある場合の参照先" → "install 済み資産の参照先" は fallback 廃止と整合した改善。**再発なし**
  - 新規指摘: なし
  - 状態: **承認済み（Round 4 承認・Phase 4 実装への移行可）**
