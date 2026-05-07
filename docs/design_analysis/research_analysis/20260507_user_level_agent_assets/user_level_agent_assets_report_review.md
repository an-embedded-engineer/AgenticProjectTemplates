---
title: "ユーザレベル Agent 資産化の妥当性調査 レビュー"
created_date: "2026-05-07"
category: research_analysis_review
target_report: docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md
target_meta: docs/design_analysis/research_analysis/20260507_user_level_agent_assets/meta.md
review_target_commit: 51cc2b1
fix_commit: e96aa40
status: approved
---

# レビュー文書: ユーザレベル Agent 資産化の妥当性調査

## 1. レビュー概要

- 観点
  - ユーザレベル instructions / skills / docs template 化の妥当性に飛躍がないか
  - repo 内の現行構成への根拠が十分か
  - Claude / Codex / Copilot の user-level 配置に関する前提が過剰でないか
  - Python / C# テンプレート間同期ルール、および C# に Python 前提を持ち込まない CLAUDE.md ルールとの整合
  - 次 workflow へ渡す粒度で未解決事項が明確か
- 結果サマリ
  - 主要な現状認識（重複、混在、外部仕様）は repo の実態と整合している
  - 推奨アーキテクチャは概ね妥当だが、生成物と同期元の関係、Copilot の取り扱い、語彙（`SKILL.master.md` 対 `SKILL.md`、project-level/user-level 境界）の精度に改善余地がある
  - スコープ全体としては次 workflow を `spec-change-workflow` へ渡せるが、未解決事項を明示化しておく必要がある
- 総合判定: Round 1 で Major 0 / Medium 3 / Low 4。Round 2 で fix commit `e96aa40` により全指摘解消、承認済み

## 2. 確認した repo 実態

レビューにあたって以下を確認した。レポートの根拠は概ね一致した。

- root / Python / C# 3 箇所に workflow skills が存在
  - root: `instructions/skills/{ai-review-response,autonomous-workflow-orchestrator,bugfix,claude-review-automation,copilot-cli-workflow-orchestrator,copilot-review-automation,issue-resolution,new-feature,refactoring,research-analysis,spec-change}-workflow/`
  - Python / C# テンプレート: 上記に加え `python-template-doc-filler` / `csharp-template-doc-filler`
- skill ファイル名は実際には `SKILL.master.md` であり、`SKILL.md` は同期スクリプトで生成される
- `docs/procedure/` は root / Python / C# の 3 箇所に存在
  - `diff -qr` で Python と C# 間に 17 ファイルの差分（多くは `workflow_phase_library/*/phase_*_*.md`）
- `agent_common_master.md` の言語別完了条件: Python 33 行目 `pyright`、C# 33 行目 `dotnet build --warnaserrors`
- ローカル環境
  - `~/.codex/skills/` に workflow / orchestrator 系 skill が配置済み
  - `~/.claude/settings.json` 存在（`~/.claude/skills/` は未存在）
  - `~/.copilot/settings.json` 存在、`~/.copilot/skills/` は未存在
- 同期スクリプト: root, Python, C# それぞれに `scripts/sync_agent_skills.{sh,ps1,bat}` が存在
- Python / C# の workflow 系 skill 本文（`autonomous-workflow-orchestrator`, `claude-review-automation`, `copilot-review-automation`, `copilot-cli-workflow-orchestrator`）は `agent_cli_tmux.py` / `AgentCliTmux` を参照しており、言語差が skill 本文に埋め込まれていることを確認

## 3. 指摘一覧

### [Medium-1] sync source と生成物の関係を recommendation に明示する

- 対象箇所
  - report.md L140「テンプレート内 `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` を厚く生成するのではなく、薄い project index にするのがよい」
  - report.md L294-302 「残す候補」一覧
  - 「変更手順案 Phase D」L329-336
- 理由
  - `python-project-template/instructions/agent_common_master.md` 等の 1 行目に「Sync Source」と明記されており、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は `scripts/sync_agent_skills.*` による生成物である
  - root `CLAUDE.md` 自体に「テンプレート内の生成物は直接編集せず、`instructions/` 側の同期元を編集する」というルールがある
  - レポートは「薄くする」と表現しているが、実際に編集対象になる正本は `instructions/agent_common_master.md`（および `AGENTS.draft.md` 等の draft）であり、生成物の薄化は同期スクリプトの再設計と一体である点が読み手に伝わりにくい
- 推奨対応
  - 推奨アーキテクチャまたは Phase D に「project-level 正本は `instructions/agent_common_master.md`（および draft）であり、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は同期スクリプト経由で生成される。薄化は sync source 側で行う」と明記する
  - `scripts/sync_agent_skills.*` の責務再定義（user-level 資産が正本になった場合に何を残すか）を未解決事項に追加する

### [Medium-2] Copilot 取り扱いの推奨に未解決の前提が混在

- 対象箇所
  - report.md L154-156「Copilot の user-level skill ディレクトリは…明示確認できなかった」
  - report.md L368-376 「リスク 3」と対策
  - 推奨方針 #5 「Copilot は user-level skill 依存を避け、当面 repo-level instructions を残す」
- 理由
  - 推奨方針 #1 で「skills はユーザレベル正本化する」と言いつつ、#5 で Copilot は repo-level を残すため、Copilot 利用環境では結局 project-level に workflow skills 相当の何かを残す必要があるのか、`AGENTS.md` 経由で user-level の参照に置き換えるのかが曖昧
  - また、`AGENTS.md` は Copilot / Codex 双方が読み得るとされるが、レポートは Codex 文脈でのみ言及しており、Copilot 側の `AGENTS.md` 読み込みを user-level 配置の代替手段として検討した形跡がない
- 推奨対応
  - 「Copilot 利用時に何を読ませるか」を明示する分岐を追記する
    - 案 A: project-level `.github/copilot-instructions.md` / `.github/instructions/*` を従来どおり厚めに残す
    - 案 B: `AGENTS.md` を介して user-level docs を間接参照する
  - 案 A / B のどちらを採るかは spec-change 側で決める旨を未解決事項に明記する

### [Medium-3] `instructions/skills/` の正本ファイル名と sync 経路の整合

- 対象箇所
  - report.md L213-221「推奨 skill 構成（SKILL.md）」
  - report.md 「変更手順案 Phase B」L317-321
- 理由
  - 現行リポジトリの skill 正本は `SKILL.master.md`（プレースホルダ含む）であり、`SKILL.md` は同期生成物として `.claude/skills` 等に配置される
  - ユーザレベルへ移す際は、`SKILL.master.md` を「placeholder を解決した skill」または「placeholder を持たない一般 skill」へ転換する作業が必要だが、レポートは `SKILL.md` 直書き相当の構成を前提にしており、変換工程が暗黙化している
- 推奨対応
  - Phase B に「`SKILL.master.md` → `SKILL.md` への正本変換（placeholder 除去、project 名解決の不要化）」を明示する
  - user-level 正本にプレースホルダを残すか否かを未解決事項に追加する

### [Low-1] 「差分の多くは言語差・ツール差」根拠の薄さ

- 対象箇所
  - report.md L75-77「差分の多くは Python / C# の言語差やツール差である」
- 理由
  - `diff -qr` で 17 ファイルが異なることは確認できるが、差分内容（例: `dotnet build` 対 `pyright`、`tools/AgentCliTmux` 対 `scripts/agent_cli_tmux.py`）の実例がレポート本文に提示されておらず、結論の根拠としてはやや弱い
- 推奨対応
  - 代表例を 1〜2 ファイル分、具体的な差分行で引用する（例: `workflow_phase_library/common/phase_4_impl_review.md` の検証コマンド差分）

### [Low-2] `~/.claude/skills` の現状と install script の関係

- 対象箇所
  - report.md L52-53 「ローカル環境」
  - 「変更手順案 Phase B 4」L320 「`install_user_agent_assets.*` を作り、…」
- 理由
  - 実環境では `~/.claude/skills` は未作成。レポートは Claude Code 公式 docs を引用して「置ける」とは記載しているが、現状は未配置である事実が明示されていない
  - install script の設計時、ディレクトリ作成、既存 user 設定の保護、上書き方針などを明文化しておかないと spec-change フェーズで揺らぐ
- 推奨対応
  - 現状整理または「未解決事項」に「`~/.claude/skills` は未作成であり、install script 側で作成・冪等性・既存ファイル保護を扱う必要がある」と追記

### [Low-3] `docs/rules/skill_catalog.md` 削除/縮小の波及

- 対象箇所
  - report.md L284-286 「テンプレート削減候補」に `docs/rules/skill_catalog.md`
  - report.md L335 「`docs/rules/skill_catalog.md` を削除または user-level skills 参照の薄い索引へ変更する」
- 理由
  - 当該ファイルは root `CLAUDE.md` の「必須参照（索引）」および各テンプレートの `agent_common_master.md` から参照されている
  - 削除/縮小すると CLAUDE.md / agent_common_master.md / 関連 skill の索引も同時に更新する必要があり、ripple が大きい
- 推奨対応
  - 「波及範囲（CLAUDE.md, agent_common_master.md, 各 SKILL.master.md の参照）」を Phase D に明記
  - もしくは「削除しない、`docs/rules/skill_catalog.md` を user-level skills の索引として残す」案を選択肢として併記

### [Low-4] C# 側へ Python 前提を持ち込まないルールとの整合確認

- 対象箇所
  - report.md L255-263 `copy_doc_templates.py`
  - report.md L274-275 「C# テンプレート利用者にも Python 実行環境を要求する点が残る」
- 理由
  - root `CLAUDE.md` は「Python テンプレートに Python ツールを追加した場合、C# テンプレートでは同等の .NET tool を優先して検討する」と定めている
  - レポートは user-level skill 補助スクリプトとしての Python を許容する立場を取っているが、これは「user-level は project-template ではないため CLAUDE.md ルールの対象外」という前提に立っている。この前提自体が明文化されていない
- 推奨対応
  - 推奨方針 or リスク 5 に「user-level skill 内のスクリプトは project-template 内ではないため、Python / .NET の重複実装ルールはユーザレベルでは適用しない」と前提を明示
  - そのうえで、C# テンプレートの project-level スクリプトを user-level 経由で代替するか否かは別問題として未解決事項に切り出す

## 4. 確認内容と残リスク（指摘なし部分）

- 主要結論「workflow / orchestration skill はユーザレベル化に最適、instructions は分割、docs は雛形を skill から配布」は repo 実態と外部仕様に整合している
- 次 workflow として `spec-change-workflow` を選んでいる点は妥当（テンプレート構成、sync 経路、skill 配置、docs 配布方式の同時変更を伴うため）
- リスク 1〜5 はそれぞれ実在するもので、対策の方向も妥当
- 残リスク（情報として記録）
  - root `instructions/skills/` には `python-template-doc-filler` / `csharp-template-doc-filler` が存在しない（テンプレート側にのみ存在）。user-level に統合する `project-doc-bootstrap` を新設する場合、root 側の skill 索引・skill 雛形運用も再設計が必要
  - 同期スクリプト `scripts/sync_agent_skills.*` が user-level 資産導入後にどう変化するかが未確定。少なくとも「user-level がある場合に skill 同期を停止するスイッチ」「project-level skill を維持する暫定モード」のいずれかの仕様が要る

## 5. 次 workflow への引き継ぎ提案（指摘対応後の追記候補）

`report.md` の「未解決事項」または `meta.md` の `next_workflow_inputs` 相当に、最低限以下を明示することを推奨する。

1. project-level 正本（`instructions/agent_common_master.md` 等）の薄化と sync スクリプト再設計の範囲
2. Copilot の参照経路（`.github/copilot-instructions.md` / `AGENTS.md` / user-level のいずれか）の決定
3. `SKILL.master.md` → `SKILL.md` への変換方針（placeholder 取り扱い）
4. `docs/rules/skill_catalog.md` の削除/縮小/移設のいずれを採るか
5. user-level install script の冪等性・既存 user 設定保護要件
6. user-level skill 内補助スクリプトの言語選定方針（C# 利用者への影響）
7. `docs/procedure/` を project-level から外すか暫定保持するかの判断軸（互換性・運用への影響）

## 6. レビューラウンド履歴

- Round 1 (2026-05-07)
  - レビュー担当: Claude (Opus 4.7)
  - 対象コミット: 51cc2b1
  - 指摘: Medium 3 / Low 4
  - 状態: 指摘対応待ち → Round 2 で対応完了
- Round 2 (2026-05-07)
  - レビュー担当: Claude (Opus 4.7)
  - 対象コミット: e96aa40
  - 確認内容
    - Medium-1: report.md L143 付近に sync source / 生成物の区別、Phase D に sync スクリプト責務再定義を追記。OK
    - Medium-2: 注意点・リスク 3・推奨方針 #5・未解決事項 #2 に Copilot 案 A/B の分岐を追記。OK
    - Medium-3: ユーザレベル正本セクションと Phase B、未解決事項 #3 に SKILL.master.md → SKILL.md 変換方針を追記。OK
    - Low-1: claude-review-automation skill / phase_4_impl_focus / coding_rules の 3 つの差分例を追記。OK
    - Low-2: Phase B step 6 と未解決事項 #5 に install script の冪等性要件を追記。OK
    - Low-3: 削減候補一覧下に波及範囲、Phase D step 7、未解決事項 #4 に維持/縮小/削除案を追記。OK
    - Low-4: リスク 5 と未解決事項 #7 に user-level 補助スクリプトの言語前提を追記。OK
  - 新規指摘: なし
  - 状態: 承認済み（次 workflow へ移行可）
