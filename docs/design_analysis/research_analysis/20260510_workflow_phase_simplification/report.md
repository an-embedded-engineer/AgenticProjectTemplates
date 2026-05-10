# workflow skill Phase 簡略化 実現性調査レポート

## 1. 調査目的

`user-agent-assets/skills` にある workflow 系 skill は、現在 `plan -> design -> impl -> docs反映` を個別 Phase として扱う。各 Phase ごとに成果物作成、レビュー、指摘対応、コミット、ユーザ承認が発生するため、実行時の読み直しとレビュー依頼が多く、トークン消費が大きい。

本調査では、次の 2 点の実現性と実現案を整理する。

1. `plan` と `design` を 1 Phase に統合できるか
2. docs 反映を独立 Phase ではなく `design` または `impl` と同時に扱えるか

## 2. 調査対象

主対象:

- `user-agent-assets/skills/spec-change-workflow`
- `user-agent-assets/skills/new-feature-workflow`
- `user-agent-assets/skills/bugfix-workflow`
- `user-agent-assets/skills/issue-resolution-workflow`
- `user-agent-assets/skills/refactoring-workflow`
- `user-agent-assets/shared/references/procedure/workflow_phase_library/common`

周辺影響:

- `user-agent-assets/skills/ai-review-response-workflow`
- `user-agent-assets/skills/claude-review-automation`
- `user-agent-assets/skills/copilot-review-automation`
- `user-agent-assets/skills/autonomous-workflow-orchestrator`
- `user-agent-assets/skills/copilot-cli-workflow-orchestrator`
- `docs/design_analysis/README.md`

非対象:

- 本調査内で workflow skill 本体は変更しない
- install / sync script の実装変更は行わない
- project-level `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の再生成は行わない

## 3. 根拠ソース

- `user-agent-assets/skills/*-workflow/references/procedure/*_workflow.md`
  - 5 種の core workflow は共通して Phase 0 から Phase 6 を持つ
  - Phase 2 は計画、Phase 3 は設計、Phase 4 は実装、Phase 5 は動作確認・文書反映
- `user-agent-assets/shared/references/procedure/workflow_phase_library/common/phase_2_plan_review.md`
  - `plan/` 文書作成、`plan_status` 更新、レビュー、指摘反映、ユーザ承認を個別 Phase として要求する
- `user-agent-assets/shared/references/procedure/workflow_phase_library/common/phase_3_design_review.md`
  - `design/` 文書作成、`design_status` 更新、レビュー、指摘反映、ユーザ承認を個別 Phase として要求する
- `user-agent-assets/shared/references/procedure/workflow_phase_library/common/phase_4_impl_review.md`
  - 実装と `impl/` 文書更新、検証、レビュー、指摘反映、`status=implemented` 更新を要求する
- `user-agent-assets/shared/references/procedure/workflow_phase_library/common/phase_5_verification_and_docs.md`
  - ユーザ動作確認後に恒久ドキュメントを更新し、docs review を個別に要求する
- `user-agent-assets/install/install_user_agent_assets.sh` / `install_user_agent_assets.ps1`
  - `user-agent-assets/shared/references/procedure/workflow_phase_library/common` を source 正本とし、install 時に phase library を必要とする各 workflow skill の `references/procedure/workflow_phase_library/common/` へ hydrate する
- `user-agent-assets/skills/*-workflow/references/procedure/workflow_phase_library/*/phase_2_plan_focus.md`
  - 受け入れ条件、影響範囲、リスク、テスト観点、完了条件など、設計前の判断材料を要求する
- `user-agent-assets/skills/*-workflow/references/procedure/workflow_phase_library/*/phase_3_design_focus.md`
  - 実装差分、責務分割、依存方向、例外・互換方針、関連ドキュメント更新先など、実装直前の判断材料を要求する
- `user-agent-assets/skills/*-workflow/references/procedure/workflow_phase_library/*/phase_5_sync_focus.md`
  - 恒久ドキュメントと `todo` / `issue` 正本への反映先を workflow 別に定義する
- `user-agent-assets/skills/claude-review-automation/SKILL.md`
  - Phase 2/3/4/5 の review 文書名を固定している
- `user-agent-assets/skills/copilot-review-automation/SKILL.md`
  - Phase 2 review 完了前に Phase 3 を始めない、Phase 4 review とユーザ動作確認前に Phase 5 docs 同期を始めない、というゲートを固定している
- `docs/design_analysis/README.md`
  - 標準構成として `plan/`, `design/`, `impl/`, `review/`, `report.md`, `meta.md` を示す
- `reference/LaneletMapViewPy/docs/design_analysis/spec_change/20260429_deleted_state_field_unification/`
  - 実運用例として `plan` / `design` / `impl` / docs review が分離され、`report.md` に 28 commit の Phase 運用履歴が残っている
- `reference/LaneletMapViewPy/docs/design_analysis/refactoring/20260426_tmux_agent_cli_script_commonization/`
  - 実運用例として計画・設計・実装・docs review が分離され、`impl` 文書内にも Phase 5 文書同期内容が先に整理されている
- `reference/LaneletMapViewPy/docs/design_analysis/research_analysis/20260506_scenario_v2_poc_round1_design/`
  - research workflow の実運用例として、Phase 1+2 が 1 commit にまとまったことが review 指摘になっており、Phase 粒度と commit 粒度の厳密運用が実コストを生むことを確認できる

関連 ADR:

- `docs/adr/README.md` を確認したが、2026-05-10 時点で ADR 一覧は空であり、本件に該当する採用済み ADR はない。

## 4. 現状整理

### 4.1 現行 Phase 構成

5 種の core workflow は、概ね次の構成で揃っている。

| Phase | 現行目的 | 主な成果物 |
|---|---|---|
| 0 | 要求・課題・事象の固定 | todo / issue 正本、スコープ |
| 1 | ブランチ・meta 初期化 | `meta.md` |
| 2 | 計画・計画レビュー | `plan/<topic>_*_plan.md`, `<topic>_plan_review.md` |
| 3 | 設計・設計レビュー | `design/<topic>_*_design.md`, `<topic>_design_review.md` |
| 4 | 実装・実装レビュー | code, `impl/<topic>_*_impl.md`, `<topic>_impl_review.md` |
| 5 | 動作確認・文書反映 | 恒久ドキュメント、docs review |
| 6 | 完了処理 | `report.md`, archive / merge 前処理 |

トークン消費が大きい主因は、Phase 2/3/4/5 がそれぞれ次を要求する点である。

- 対象文書の作成
- `meta.md` status 更新
- レビュー依頼前コミット
- レビュー Agent による review 文書作成
- 指摘対応
- follow-up review
- 次 Phase 進行承認

### 4.2 plan と design の重複

`phase_2_plan_focus.md` は、変更理由、受け入れ条件、影響範囲、リスク、テスト観点、完了条件を扱う。一方で `phase_3_design_focus.md` は、before / after 差分、責務分割、依存方向、移行方針、例外方針、回帰テスト設計、関連ドキュメント更新先を扱う。

重複している、または同じ文書内に置いたほうが自然な項目:

- 受け入れ条件と設計差分
- 影響範囲とコンポーネント責務
- リスクと失敗時動作
- テスト観点と回帰テスト設計
- 完了条件と確認証跡
- 移行要否と旧経路削除方針

現行の分割は、巨大案件で「まず実施範囲を承認し、後で詳細設計を承認する」には有効である。一方、通常サイズの修正や文書中心の変更では、Phase 2 で書いた判断を Phase 3 でより具体化して再掲する形になりやすい。

### 4.3 docs 反映 Phase の分離コスト

Phase 5 は、ユーザ動作確認が OK になった後に恒久ドキュメントへ反映する前提である。これは「実装が確定してから docs を更新する」安全さがあるが、次のコストがある。

- Phase 4 実装後に設計・実装文書を再読して docs 更新先を洗い直す
- docs review のために Phase 5 専用 review 文書を作る
- 実装差分と恒久ドキュメントの対応が時間的に離れ、文書漏れが起きやすい
- 軽微な修正でも Phase 5 の review / follow-up / 承認が追加で発生する

docs 反映先自体は workflow 別 `phase_5_sync_focus.md` に明確化されているため、設計時に「更新予定先」を決め、実装時に実際の恒久ドキュメントを同時更新する運用へ移せる。

### 4.4 Lanelet 実運用サンプルからの補強

`reference/LaneletMapViewPy/docs` の最近の実運用文書を確認した結果、現行 Phase 分割の品質上の利点とコストがどちらも見えた。

`20260429_deleted_state_field_unification` では、`plan` 214 行、`design` 450 行、`impl` 216 行、review 文書合計 745 行、`report.md` 123 行の規模になっている。`report.md` の commit 一覧では、Phase 2 plan review、Phase 3 design review、Phase 4 impl review、Phase 5 docs review それぞれに reviewer commit / follow-up / approval / status sync が発生し、全体で 28 commit が記録されている。特に Phase 5 docs review は docs review、指摘対応、follow-up、残指摘対応、承認の 5 commit を消費している。

この実例は、Phase 分割によりレビュー観点を細かく閉じられる一方、通常の実装案件でも review loop と meta/status sync の固定費が大きくなることを示す。

`20260429_deleted_state_field_unification` の plan review では、影響ファイル列挙、Phase 3 で確定する API、命名方針などが指摘され、Phase 3 design review では、それらの follow-up が設計に落ちているか確認されている。これは plan/design 分離が有効だった例である。ただし、計画書の多くの内容は背景、対象/非対象、到達点、変更方針、実装ステップ、リスク、テスト方針、受け入れ条件であり、推奨案の統合 design 文書の必須章として保持できる。

`20260426_tmux_agent_cli_script_commonization` では、`impl` 文書内に「Phase 5 文書同期」セクションがあり、実装記録の時点で反映対象と反映内容が整理されている。その後の docs review は主に `meta.md` の status、`impl_status`、旧コマンド残存、history / todo / skill catalog 整合を確認している。これは、恒久ドキュメント反映を実装 Phase に同梱し、completion 側では status / archive / 最終証跡を確認する案と相性がよい。

`20260506_scenario_v2_poc_round1_design` の review では、`meta.md` の `related_commits` で Phase 1 と Phase 2 が 1 commit にまとまっていることが形式差分として指摘されている。これは研究 workflow の例だが、Phase と commit を細かく一致させる規定が実運用ではレビュー論点になり、トークンと対応コストを増やすことを示している。

実運用サンプルを踏まえると、簡略化方針は次のように補正するのがよい。

- plan/design 統合を標準にするが、`20260429_deleted_state_field_unification` のように影響範囲が広く、API 未確定事項が多い案件は `plan_required` として分離を許可する
- 実装 Phase の `impl` 文書に恒久ドキュメント反映対象と反映内容を含め、impl review で code / docs 整合をまとめて見る
- completion Phase は、恒久 docs の詳細 review ではなく、`meta.md`、todo / issue / history、archive、最終 report の整合確認に寄せる
- Phase ごとの commit 粒度は標準推奨に留め、やむを得ず複数 Phase が 1 commit にまとまった場合は `Phase 1+2` のような記録形式を許容するかを設計で決める

## 5. 実現性評価

### 5.1 plan/design 統合

実現性は高い。

理由:

- Phase 2 と Phase 3 の成果物はどちらも実装前の判断を扱う
- review automation は Phase 名と review 文書名に依存しているが、コードではなく skill 文書上の契約であり、契約更新で対応できる
- `docs/design_analysis/README.md` の標準構成は `plan/` と `design/` を示しているが、調査・分析では例外構成をすでに許容しているため、運用ガイド側も拡張可能である

注意点:

- plan を完全削除すると「実施すべきか」を判断するゲートが薄くなる
- 大規模・高リスク案件では plan と design を分ける選択肢を残すべきである
- `meta.md` の `plan_status` / `design_status` をそのまま残すか、統合 status へ移すかを決める必要がある

### 5.2 docs 反映の前倒し

実現性は中から高である。

実装と同時に恒久ドキュメントを更新する案は妥当である。特に次の文書は、実装差分と同じ Phase で更新したほうが整合しやすい。

- `docs/components/<component>/README.md`
- `docs/components/<component>/basic_design.md`
- `docs/components/<component>/detail_design.md`
- `docs/components/<component>/interface_spec.md`

一方、`docs/todo/todo.md` や `docs/issues/<component>/issues.md` の archive 準備は、動作確認や最終検証結果が必要になるため、完了処理側へ残すほうがよい。

したがって docs 反映は 2 種類に分けるのが現実的である。

| 種類 | 推奨タイミング | 理由 |
|---|---|---|
| 恒久仕様・設計 docs | 実装 Phase と同時 | 実装差分と対応付けやすい |
| todo / issue の完了証跡・archive 準備 | 完了処理 Phase | 検証結果と完了判断が必要 |

## 6. 実現案

### 6.1 推奨案: 4 ゲート構成へ再編する

現行 Phase 0/1 は維持し、Phase 2 以降を再編する。

| 新 Phase | 目的 | 旧 Phase 対応 | 主な成果物 |
|---|---|---|---|
| 0 | 要求・課題・事象の固定 | 旧 0 | todo / issue 正本、スコープ |
| 1 | ブランチ・meta 初期化 | 旧 1 | `meta.md` |
| 2 | 方針・設計 | 旧 2 + 旧 3 | `design/<topic>_*_design.md`, `<topic>_design_review.md` |
| 3 | 実装・恒久ドキュメント反映 | 旧 4 + 旧 5 docs の一部 | code, `impl/<topic>_*_impl.md`, 恒久 docs, `<topic>_impl_review.md` |
| 4 | 動作確認・完了処理 | 旧 5 verification + 旧 6 | ユーザ確認結果、`report.md`, todo / issue archive 準備 |

この案では、plan 文書を独立成果物にしない。Phase 2 の design 文書へ次の章を必須化する。

- 背景・要求・完了条件
- 対象範囲と非対象
- before / after
- 影響範囲
- 設計方針
- 互換性・移行方針
- 恒久ドキュメント更新予定先
- テスト・ユーザ確認観点
- リスクと follow-up

これにより、plan の判断材料を失わずに review loop を 1 回削減できる。

### 6.2 docs 反映の扱い

Phase 2 では「どの恒久ドキュメントを更新するか」を設計書へ明記する。

Phase 3 では、実装差分と一緒に恒久ドキュメントを更新する。実装レビューは code / impl 文書 / 恒久ドキュメントをまとめて確認する。

Phase 4 では、ユーザ動作確認結果、検証結果、todo / issue 正本の完了証跡、archive 用リンク、`report.md` を扱う。docs review という独立レビューは原則廃止し、必要な場合だけ completion review として扱う。

### 6.3 `meta.md` の status 方針

後方互換をなるべく増やさない方針に合わせ、長期的には `plan_status` / `design_status` / `impl_status` の 3 分割をやめ、Phase 単位の status へ寄せるほうが自然である。

推奨:

```yaml
status: draft | in_review | implemented | verification_pending | completed | merged
phase_status:
  intake: done
  setup: done
  design: draft | in_review | done
  implementation: not_started | draft | in_review | done
  completion: not_started | in_progress | done
```

ただし既存文書・レビュー automation への影響を抑える移行期は、`plan_status: N/A`、`design_status`、`impl_status` を残す案も可能である。

移行期の最小案:

```yaml
plan_status: N/A
design_status: draft | in_review | done
impl_status: not_started | draft | in_review | done
```

### 6.4 review 文書命名

推奨案では、標準 review 文書を次の 2 種に減らす。

- `<topic>_design_review.md`
- `<topic>_impl_review.md`

必要に応じて完了処理レビューを追加する。

- `<topic>_completion_review.md`

docs review の workflow 別 suffix は廃止候補にする。恒久ドキュメントの整合性は `impl_review` に含め、todo / issue archive の証跡は `completion_review` または completion checklist で見る。

## 7. 変更が必要な箇所

### 7.1 core workflow skill

5 種の `*_workflow.md` を更新する。

- Phase 一覧を新構成へ変更する
- Phase 2 の共通手順参照を `phase_2_design_review.md` 相当へ変更する
- Phase 3 の共通手順参照を `phase_3_impl_and_docs_review.md` 相当へ変更する
- Phase 4 を `verification_and_completion.md` 相当へ変更する
- ユーザ承認タイミングを Phase 2 review 後、Phase 3 review 後、ユーザ動作確認、完了前へ減らす

workflow 別 focus 文書は、次のように再編する。

- `phase_2_plan_focus.md` と `phase_3_design_focus.md` を統合する
- `phase_4_impl_focus.md` に `phase_5_sync_focus.md` の恒久 docs 反映先を取り込む
- todo / issue archive に必要な観点だけ completion focus へ残す

### 7.2 shared common phase library

`user-agent-assets/shared/references/procedure/workflow_phase_library/common` を更新する。
ここが source 正本であり、各 workflow skill 配下の `references/procedure/workflow_phase_library/common/` は install / sync 時に hydrate される配布結果として扱う。
したがって、簡略化時の正本変更は shared common に対して行い、hydrate 後の各 workflow で同じ common phase library が読めることを検証する。

現行:

- `phase_1_branch_and_meta.md`
- `phase_2_plan_review.md`
- `phase_3_design_review.md`
- `phase_4_impl_review.md`
- `phase_5_verification_and_docs.md`
- `phase_6_completion.md`

推奨:

- `phase_1_branch_and_meta.md`
- `phase_2_design_review.md`
- `phase_3_impl_and_docs_review.md`
- `phase_4_verification_and_completion.md`

### 7.3 review / orchestration skill

review automation と orchestrator は Phase 契約を強く参照しているため、同時更新が必要である。

更新対象:

- `claude-review-automation/SKILL.md`
  - Phase 2/3/4/5 review 対応を Phase 2/3/4 に変更
  - review 文書命名から plan/docs を削除または optional 化
  - prompt の `Phase <plan|design|impl|docs>` を `Phase <design|impl|completion>` へ変更
- `copilot-review-automation/SKILL.md`
  - Phase 進行ゲートを新構成へ変更
  - 「Phase 4 review とユーザ動作確認前に Phase 5 docs 同期を始めない」を削除し、実装 Phase 内 docs 更新へ変更
- `autonomous-workflow-orchestrator` / `copilot-cli-workflow-orchestrator`
  - Phase loop の範囲とユーザ確認ゲートを更新
  - `[NEED_USER_VERIFICATION]` の位置づけを completion Phase へ変更
- `ai-review-response-workflow`
  - 工程分類の `plan / design / impl` を `design / impl / completion` または `design / impl` へ更新
  - review 文書名テンプレートを更新

### 7.4 docs/design_analysis 運用

`docs/design_analysis/README.md` の標準構成を更新する必要がある。

推奨構成:

```text
<YYYYMMDD>_<slug>/
├── design/
│   └── <topic>_design.md
├── impl/
│   └── <topic>_impl.md
├── review/
│   ├── <topic>_design_review.md
│   └── <topic>_impl_review.md
├── report.md
└── meta.md
```

大規模案件向けに `plan/` を optional として残す場合は、明示条件を置く。

- 複数案比較が必要
- ユーザ判断なしに設計へ進めない
- 影響範囲が複数コンポーネントにまたがる
- 実装前に段階分割の承認が必要

## 8. リスクと対策

| リスク | 内容 | 対策 |
|---|---|---|
| 実施可否判断が薄くなる | plan を削ると「やるべきか」の判断が design に埋もれる | design 文書の先頭に要求・完了条件・非対象・採否理由を必須章として置く |
| 大規模案件で review 粒度が粗くなる | plan/design 統合によりレビュー対象が大きくなる | `plan_required` 条件を定義し、該当時だけ旧来に近い 2 段階を許可する |
| docs 更新が実装中に揺れる | 実装が変わるたび恒久ドキュメントも更新し直す必要がある | Phase 2 では更新予定先だけ決め、Phase 3 の最終差分で実体更新する |
| 動作確認前の docs が誤る | ユーザ確認前に恒久 docs を更新するため未確定内容が混ざる | impl review 後、ユーザ確認 NG なら code と docs を同時に Phase 3 へ差し戻す |
| automation が壊れる | Phase 番号、review 文書名、prompt template が固定されている | core workflow と review/orchestrator skill を同一仕様変更で更新し、smoke test を行う |
| 既存 design_analysis との混在 | 過去文書は plan/design/impl 分割のまま残る | 過去文書は移行しない。README に「新規案件から適用」と明記する |

## 9. 推奨移行手順

次 workflow としては `spec-change-workflow` が適切である。理由は、workflow skill の公開契約、review automation、design_analysis 運用を横断して変更するためである。

推奨する実装順:

1. Phase 簡略化の新契約を `docs/design_analysis/spec_change/<date>_workflow_phase_simplification/` に設計する
2. `docs/design_analysis/README.md` の標準構成を新規案件向けに更新する
3. shared common phase library を 4 ゲート構成へ更新する
4. 5 種の core workflow と workflow 別 focus 文書を更新する
5. `ai-review-response-workflow` の工程分類と review 文書名を更新する
6. `claude-review-automation` / `copilot-review-automation` / orchestrator 群の Phase 契約を更新する
7. user-level assets install / sync の hydrate 結果で common phase library が正しく配布されることを確認する
8. 小さな文書変更タスクで smoke test を行い、review 文書が design / impl の 2 本で回ることを確認する

## 10. 結論

plan/design 統合は実現可能であり、トークン削減効果も見込める。推奨は、plan を独立成果物として廃止し、Phase 2 の design 文書に「要求・完了条件・範囲・リスク・テスト観点」を必須章として統合する方式である。

docs 反映の前倒しも実現可能である。ただし、すべてを design 時に反映するのではなく、設計時は更新予定先の確定、実装時は code と恒久ドキュメントの同時更新、完了処理時は todo / issue の証跡整理に分けるのがよい。

最終的な推奨構成は次である。

- Phase 0: 要求・課題・事象の固定
- Phase 1: ブランチ・meta 初期化
- Phase 2: 方針・設計レビュー
- Phase 3: 実装・恒久ドキュメント反映レビュー
- Phase 4: 動作確認・完了処理

この変更は単独 workflow 文書だけでは完結しない。review automation と orchestrator が Phase 2/3/4/5、review 文書名、ユーザ承認ゲートを固定しているため、仕様変更として一括設計・一括更新する必要がある。

## 11. 未解決事項

1. 大規模案件で `plan/` を optional に残す条件をどこまで明文化するか
2. `meta.md` を新しい `phase_status` へ移行するか、当面 `plan_status: N/A` で互換運用するか
3. completion review を標準化するか、完了 checklist のみで済ませるか
4. 過去の design_analysis 文書を旧構成のまま扱うことを README にどう明記するか
5. review automation の prompt template で Phase 番号を残すか、`design` / `impl` / `completion` の名称ベースへ移すか
6. Phase と commit の対応を厳密必須にするか、実運用上の複数 Phase 混在 commit を `Phase 1+2` のような記録形式で許容するか
