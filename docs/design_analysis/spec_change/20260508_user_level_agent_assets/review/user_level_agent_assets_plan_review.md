---
title: "ユーザレベル Agent 資産化 Phase 2 計画レビュー"
created_date: "2026-05-08"
category: spec_change_plan_review
target_plan: docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md
target_meta: docs/design_analysis/spec_change/20260508_user_level_agent_assets/meta.md
target_commit: 4bc2fec5cc1f2273c32e4002c164f82ef96d86c7
status: approved
---

# レビュー文書: ユーザレベル Agent 資産化 Phase 2 計画

## 1. レビュー概要

- 観点
  - 調査レポートの推奨方針・結論と計画の整合
  - 受け入れ条件ごとの対応方針に漏れがないか
  - user-level assets と project-level の責務境界が曖昧でないか
  - `docs/procedure/` の references 化、`skill_catalog.md` 削除方向、wrapper 方針、Copilot smoke test が計画へ十分落ちているか
  - Phase 3 へ渡す未解決事項の粒度が妥当か
- 参照文書
  - 調査レポート: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
  - 調査レビュー: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/user_level_agent_assets_report_review.md`（承認済み）
  - 計画書: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md`
  - 追跡項目: `docs/todo/todo.md` SC-20260508-001
- 結果サマリ
  - 7 つの受け入れ条件はすべて計画の Section 6 表に対応方針が記載されており、抜け漏れなし
  - 5 ワークストリーム（7.1〜7.5）と研究レポートの推奨方針 7 項目の整合は概ね良好
  - リスク対策・実装順序・テスト方針は研究レポートの未解決事項処理結果を正しく引き継いでいる
  - ただし、以下の 2 点で Phase 3 設計者が研究レポートまで遡ることを余儀なくされる情報不足がある
- 総合判定: Medium 2 / Low 2

## 2. 調査レポート結論 vs 計画の整合確認

### 2.1 推奨方針 7 項目の計画への反映状況

| 研究レポート推奨方針 | 計画内対応箇所 | 判定 |
|---|---|---|
| #1 skills ユーザレベル正本化 | Section 5.2, 7.1 | ✅ |
| #2 instructions 共通原則分離 | Section 5.1, 7.4 | ✅ |
| #3 docs 雛形を bootstrap skill で配布 | Section 5.3, 7.3 | ✅ |
| #4 `docs/procedure/` → references 化 | Section 7.2, 受け入れ条件表 row 2 | ✅ |
| #5 Copilot も user-level 正本化対象に含める | Section 6 row 1, 10.2 item 1 | ✅ |
| #6 `skill_catalog.md` 削除方向 | Section 7.4, 6 row 5 | ✅（※後述 Medium-2）|
| #7 OS 別 wrapper / executable allowlist | Section 7.5, 6 row 6 | ✅（※後述 Low-1）|

### 2.2 研究レポートの「未解決事項」（方針確定 6 件・動作確認待ち 2 件）との整合

- 方針確定 6 件: `SKILL.master.md` → `SKILL.md` 変換、`skill_catalog.md` 削除、install script 安全要件、docs bootstrap スクリプト言語（wrapper 優先）、OS 別 wrapper 方針（sh/ps1/executable）、Copilot 向け install パス候補
  - 計画は Section 7.1〜7.5 / Section 6 表 / Section 8 リスクに対応を記載しており、いずれも適切に引き継いでいる ✅
- 動作確認待ち 2 件: Copilot smoke test（#2）、`docs/procedure/` references 化後動作確認（#6）
  - Copilot smoke test は Section 6 row 1 / Section 10.2 item 1 / Section 11 item 1 で Phase 5 に位置づけられている ✅
  - `docs/procedure/` 動作確認は Section 8.4（リスク対策）と Section 9 item 5 に暗黙的に記載されているが、後述 Medium-1 の問題を含む

## 3. 受け入れ条件ごとの対応方針チェック

`docs/todo/todo.md` の受け入れ条件 7 項目 vs 計画 Section 6 表の対応：

| # | 受け入れ条件 | 計画 Section 6 対応方針 | 判定 |
|---|---|---|---|
| 1 | Copilot smoke test | Phase 5 で検出確認手順を実施 | ✅ |
| 2 | workflow skill が `docs/procedure/` 非依存化 | Phase 3 で self-contained 構成定義 | ✅ |
| 3 | install script の安全要件（dry-run / missing-only / 保護） | install 設計に含める | ✅ |
| 4 | `SKILL.master.md` → placeholder 除去 user-level `SKILL.md` | 生成方針を固定 | ✅ |
| 5 | `skill_catalog.md` 削除方向と参照元更新 | Phase 3/4 設計対象に含める | ✅（※Medium-2）|
| 6 | wrapper / executable allowlist 化 | 用途別 wrapper / executable 配布を設計対象 | ✅（※Low-1）|
| 7 | project-level instructions 薄化 | sync source 側で固有ルール中心化 | ✅ |

**全 7 条件の対応方針は計画に記載されており、原則として抜け漏れなし。**
ただし、条件 #3 と #4 は Section 6 表には記載されているが Section 14（受け入れ条件）には集約済みで可視性が低い（後述 Low-2）。

## 4. user-level / project-level 責務境界の明確性

計画 Section 5 の変更差分 3 点（instructions / skills / docs）は、研究レポートと一致した分離方針を簡潔に記述しており境界は概ね明確である。

- Section 5.1: 共通原則 → user-level、固有ルール・検証コマンド → project-level ✅
- Section 5.2: workflow skill の正本 → user-level、共有が必要なものだけ project-level に残す ✅
- Section 5.3: workflow 手順書 → references、docs 雛形 → bootstrap skill の templates、実体化済み docs → project-level ✅

**境界の詳細（どのファイルをどちらに置くか）は Section 7 ワークストリームと Section 12 影響コンポーネント別変更範囲に分散しており、Phase 3 で確定する設計として正しく扱われている。**

## 5. 指摘一覧

### [Medium-1] Copilot smoke test 不合格時の project-level fallback 構成が未定義

- 対象箇所
  - plan.md Section 8.3「対策: Phase 5 の smoke test で最小 skill を使って検証し、必要なら project-level fallback を明示する」
  - plan.md Section 13（未解決事項）に対応する記載なし
- 理由
  - smoke test が不合格だった場合、Copilot 向けに何を project-level（`.github/skills/` や `.github/copilot-instructions.md`）に残すかは、Phase 3 のディレクトリ構造設計と install script 設計に直結する。
  - 現行の "必要なら project-level fallback を明示する" はタイミングと内容両方が曖昧であり、Phase 3 設計者が前提を決められない。
  - 研究レポートのリスク 3 対策には「project-level `.github/skills/` / `.claude/skills/` / `.agents/skills/` をチーム共有が必要な skill だけを置く fallback / workspace 共有経路として整理する」と方向が示されていたが、plan にはこの内容が引き継がれていない。
- 推奨対応
  - Section 13 に「Copilot smoke test が失敗した場合、project-level fallback として `.github/skills/` に workflow skills を残す範囲とその解消条件を Phase 3 設計で明確化する」を追加する。
  - または Section 8.3 の対策を「smoke test 不合格時は `.github/skills/` を project-level fallback として維持し、smoke test 合格確認後に削除する」等、条件と内容を明記する形に書き換える。

### [Medium-2] `skill_catalog.md` 削除 ripple の具体ファイル名が計画本文に不在

- 対象箇所
  - plan.md Section 6 表 row 5「参照元更新を含めた ripple を Phase 3 / 4 の設計対象に含める」
  - plan.md Section 7.4「`docs/rules/skill_catalog.md` の参照元を更新し、削除方向で整理する」
  - plan.md Section 12「`docs/rules/skill_catalog.md`: 参照元更新を伴う削除方向整理」
- 理由
  - 研究レポートおよびそのレビュー（Round 4）では、ripple 対象ファイルとして `CLAUDE.md`、`AGENTS.md`、`.github/copilot-instructions.md`、各 `SKILL.master.md` が明示されていた。
  - 計画のどのセクションにも具体ファイル名の列挙がなく、"ripple を設計対象に含める" という表現にとどまっている。
  - Phase 3 設計者が影響ファイルを確認するには研究レポートまで遡る必要があり、設計漏れのリスクが生じる。
- 推奨対応
  - Section 7.4 または Section 12 の `docs/rules/skill_catalog.md` 行に「参照元: `root/CLAUDE.md`、`root/AGENTS.md`、`.github/copilot-instructions.md`、各テンプレートの `SKILL.master.md`」を具体的に追記する。

### [Low-1] OS 別 wrapper の具体方針（sh / ps1 / executable）が計画に転記されていない

- 対象箇所
  - plan.md Section 7.5「OS 別 wrapper または publish 済み executable の配置方針を定める」
  - plan.md Section 13 item なし
- 理由
  - 研究レポートの未解決事項 #8 は「macOS / Linux は `.sh`、Windows は `.ps1`、必要なら `.cmd` または publish 済み executable」と具体的な方針まで確定していた。
  - 計画 Section 7.5 はこれを抽象化した記述になっており、Phase 3 設計者が OS 別方針を研究レポートから参照し直す必要が生じる。
  - Section 13 の未解決事項にも未掲載のため、Phase 3 設計チェックリストから抜け落ちる恐れがある。
- 推奨対応
  - Section 7.5 に「macOS / Linux: `.sh`、Windows: `.ps1`（必要なら `.cmd` または publish 済み executable）」を追記する。または Section 13 に「OS 別 wrapper 具体方針（研究レポート未解決事項 #8）を Phase 3 で設計に落とすこと」を明示する。

### [Low-2] Section 14 受け入れ条件の集約によりインストールスクリプト安全要件の可視性が低い

- 対象箇所
  - plan.md Section 14「4. `skill_catalog.md` 削除方向に伴う参照更新、wrapper allowlist、Copilot smoke test を含む検証計画が定義されている」
  - todo.md 受け入れ条件 #3「install script は `dry-run`、`missing-only default`、既存 user skill の上書き保護、未作成 skill directory の作成に対応する」
- 理由
  - Section 14 は todo.md の 7 条件を 4 件に集約しており、install script の安全要件（dry-run / missing-only / 保護）が Section 14 の文面から直接確認できない。
  - Section 6 の表には記載されているが、Section 14 を最終受け入れチェックリストとして参照する場合に追跡コストが増える。
  - 計画 Section 14 は "この Phase で完了を確認するための基準" として機能することが期待されるため、原則として todo.md の全受け入れ条件を参照できるよう対応しておくほうがよい。
- 推奨対応
  - Section 14 に注記として「詳細な受け入れ条件は Section 6 の表および `docs/todo/todo.md` SC-20260508-001 を参照」を追加する。または install script 安全要件を項目として追記する。

## 6. 確認内容と残リスク（指摘なし部分）

- **計画の構造**: 背景 → 目的 → 対象 → 変更差分 → 受け入れ条件表 → ワークストリーム → リスク → 実装順序 → テスト方針 → ユーザ確認シナリオ → 影響コンポーネント → 未解決事項 → 受け入れ条件 の流れは論理的で過不足なし ✅
- **5 ワークストリーム（7.1〜7.5）**: 研究レポートの Phase A〜E に対応しており、設計フェーズでのカバレッジが見通せる ✅
- **リスク 8.1〜8.5**: 研究レポートのリスク 1〜5 を全て引き継ぎ、対策方針も整合している。特に 8.4（`docs/procedure/` 早期除去リスク）と 8.5（言語差の吸収不足）は適切 ✅
- **実装順序 Section 9**: "恒久的な二重正本は残さない" という方針が明記されており、段階移行の意図が明確 ✅
- **テスト方針 Section 10.2**: 5 つの本件固有確認項目が研究レポートの Phase E と整合 ✅
- **Section 13 未解決事項**: 4 項目は Phase 3 設計に必要な決定事項であり、Phase 2 計画の阻害要因でない項目として適切に切り分けられている（Medium-1 の追加を除く）

- **残リスク（情報として記録）**
  - Section 8.2（instructions 優先順位衝突）のリスクは計画で "user-level は原則 workflow、project-level は具体コマンドと例外ルール" と対策が示されているが、現行の runtime（Copilot / Claude / Codex）で user-level と project-level の競合解決順序が一致しているかは、Phase 5 smoke test で初めて確認できる性質のものである。実装 Phase では動作確認対象として明示することを推奨する。
  - Section 7.3（docs bootstrap 導線）の "既存 docs を上書きしない default" と "placeholder 検出" は Section 10.2 item 3 に検証項目として挙げられているが、docs bootstrap の補助スクリプト言語が Section 13 item 3 の未解決事項として残っており、Phase 3 設計前に言語選定方針を確定する必要がある。

## 7. Phase 3 へ渡す未解決事項の粒度評価

計画 Section 13 の 4 項目の粒度は概ね適切。ただし Medium-1 で指摘のとおり、Copilot smoke test 不合格時の fallback 構成を追加すべきである。

推奨追加後の Section 13 未解決事項:

| # | 項目 | Phase 3 での判断内容 |
|---|---|---|
| 1 | Copilot install 先優先順位 | `~/.copilot/skills` vs `~/.agents/skills` のどちらを正規先とするか |
| 2 | install / sync script 共通化スコープ | root / template の共通化範囲と暫定 project-level skills 維持 mode |
| 3 | docs bootstrap スクリプト言語 | shell / PowerShell / publish 済み executable の選定 |
| 4 | project-level fallback 期間 | smoke test と references 化確認後の削除条件（時期の明示） |
| *5（追加推奨）* | *Copilot smoke test 不合格時の fallback 構成* | *`.github/skills/` に残す workflow skills の範囲と解消条件* |

## 8. レビューラウンド履歴

- Round 1 (2026-05-08)
  - レビュー担当: Claude Sonnet 4.6 (GitHub Copilot CLI)
  - 対象コミット: 4bc2fec
  - 指摘: Medium 2 / Low 2
  - 状態: 指摘対応待ち → Round 2 で対応完了
- Round 2 (2026-05-08)
  - レビュー担当: Claude Sonnet 4.6 (GitHub Copilot CLI)
  - 対象コミット: cea5833
  - 確認内容
    - Medium-1: Section 8.3 の対策を "不合格時は `.github/skills/` を project-level fallback として維持する範囲と削除条件を Phase 3 で設計確定する" に書き換え。Section 13 item 5 として fallback 構成の設計確定を追加。OK
    - Medium-2: Section 7.4 に ripple 対象ファイル（`root/CLAUDE.md`、`root/AGENTS.md`、`.github/copilot-instructions.md`、各 template の `instructions/skills/*/SKILL.master.md`）を追記。Section 12 にも同内容を追記。OK
    - Low-1: Section 7.5 に macOS/Linux → `.sh`、Windows → `.ps1`、必要時 `.cmd` または publish 済み executable を明記。OK
    - Low-2: Section 14 item 5 に install script 安全要件（dry-run / missing-only default / 保護 / directory 作成）を追記。Section 6 と `docs/todo/todo.md` への参照注記を追加。OK
  - 新規指摘: なし
  - 状態: 承認済み（Phase 3 設計への移行可）
