# workflow skill phase simplification feasibility research レビュー

- レビュー日: 2026-05-10
- 対象 commit: `8643970`
- 対象ファイル:
  - `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/report.md`
  - `docs/design_analysis/research_analysis/20260510_workflow_phase_simplification/meta.md`
- レビュー観点:
  - plan/design 統合推奨と実運用サンプルの整合
  - WBS 分解 skill 分離が core workflow 簡略化方針として妥当か
  - docs 反映を impl と completion に分ける案の漏れ・副作用
  - `user-agent-assets/shared/.../workflow_phase_library/common` を source 正本とし install/sync で hydrate される前提の取り扱い
  - `related_commits` を completion でまとめる案と review automation / research workflow の証跡要件の整合
  - 次の spec-change workflow へ渡せる粒度

## 1. 総評

- 簡略化方向（plan を design へ統合、Phase 5 docs review を impl と completion に分割、WBS 大規模 planning は別 skill へ逃がす、`related_commits` を completion でまとめる）の大枠は、shared common phase library と review automation / orchestrator skill 群の現状契約を踏まえて妥当に組み立てられている。
- shared common 正本の hydrate 前提は `install_user_agent_assets.sh` の `hydrate_workflow_phase_library_common` 関数で確認でき、Section 3 と Section 7.2 の記述は一次情報と一致する。
- 一方で、後段の spec-change workflow が判断材料としてそのまま使うには、実運用サンプルの読み取り精度、影響範囲列挙、未解決事項の closeable 化に重大度 Major / Moderate の不足がある。下記指摘の Major を解消した上で再レビューしたい。
- 現時点の判定: **条件付き未承認**。Major M1〜M5 の解消後に承認とする。Moderate / Minor は同一ラウンドで対応するのが望ましい。

## 2. 重大指摘 (Major)

### M1. Lanelet refactoring サンプルの「Phase 5 文書同期」セクションを過大解釈している

**箇所**: `report.md` §4.4「`20260426_tmux_agent_cli_script_commonization` では、`impl` 文書内に「Phase 5 文書同期」セクションがあり、実装記録の時点で反映対象と反映内容が整理されている」/「これは、恒久ドキュメント反映を実装 Phase に同梱し」 と続く部分、および §6.2 の「実装差分と一緒に恒久ドキュメントを更新する」推奨。

**事実**: `reference/LaneletMapViewPy/docs/design_analysis/refactoring/20260426_tmux_agent_cli_script_commonization/impl/tmux_agent_cli_script_commonization_refactoring_impl.md` §8 の「Phase 5 文書同期」は、`docs/rules/skill_catalog.md` 等の「反映対象」と「反映内容」を **事前列挙する planning 表** であり、impl Phase 時点で恒久ドキュメントを実体更新した記録ではない。Lanelet 運用は依然として Phase 5 で恒久 docs を更新している。

**何が問題か**: §6.2 の推奨「Phase 3（新）= 実装差分と恒久ドキュメントを同時更新」は、Lanelet サンプルが体現しているより一歩踏み込んだ提案である。サンプルは「impl 時点で反映先を確定」しているだけで、「impl 時点で実体を更新」はしていない。サンプル根拠と推奨案の差分を曖昧にしたまま「相性がよい」と書くと、後段 workflow が「Lanelet がやっている運用そのもの」と誤認しやすい。

**修正案**:
- §4.4 の該当段落を「impl 文書時点で反映先と反映内容が確定しており、Phase 5 の docs 更新が機械的作業に近づいている。これは impl Phase で『反映先確定 + 設計書更新』、Phase 5 でユーザ動作確認後に恒久 docs 反映、という派生案とも親和的」のように事実と推奨案を分けて書く。
- §6.2 の推奨を「Phase 3 で `docs/components/...` 等の恒久 docs を更新する」と「Phase 3 で更新先を impl 文書に確定し、ユーザ動作確認結果を踏まえて Phase 4 で同時 commit する」の 2 案に分けて、どちらを採るか次 workflow で意思決定対象にする旨を明記する。

### M2. 新 Phase 4（動作確認＋完了処理）が現行 Phase 5/6 の独立ゲートを 1 段に圧縮しており、副作用が記述されていない

**箇所**: `report.md` §6.1 推奨案 4 ゲート構成、§6.2 「Phase 4 では、ユーザ動作確認結果、検証結果、todo / issue 正本の完了証跡、archive 用リンク、`report.md` を扱う。docs review という独立レビューは原則廃止」、§7.3 `[NEED_USER_VERIFICATION]` 位置づけ更新。

**事実**: 現行 `phase_5_verification_and_docs.md` と `phase_6_completion.md` を読むと、ユーザ動作確認 STOP、Phase 5 docs 反映、docs review STOP、Phase 6 マージ承認 STOP、`status=merged` 更新、todo/issue archive、`docs/history/` 更新がそれぞれ独立ゲートになっている。`spec_change_workflow.md` の「ユーザ承認が必要なタイミング」は 7 箇所あるが、§6.1 推奨案では 4 箇所まで減る。

**何が問題か**:
- ユーザ動作確認 NG の差し戻し導線は §8 リスク表に書かれているが、merge / archive / history 更新の各 STOP が同 Phase 4 内で順序付けされる前提なのか、Phase 4 を更に内部 step で区切る前提なのか不明瞭。
- 動作確認 OK 直後にすぐ archive と merge を進められると、`docs/history/` 反映の見落としや、未確定の todo archive 移動が起きやすい。
- 現行 `phase_6_completion.md` で要求している「ソース差分レポート（`report.md`、必要に応じて `diff.zip`）」生成は、推奨案では Phase 4 のどこに位置するのか不明。

**修正案**:
- §6.1 の Phase 4 を内部 step に分けて記載する。例: `4-a 動作確認 STOP`, `4-b 完了処理（report.md / diff / archive / history）`, `4-c マージ承認 STOP`。
- §6.2 に「Phase 4 完了内 step の順序」表を追加し、動作確認 OK が出る前に archive / history / merge を進めない旨を明記する。
- 削除されるユーザ承認ゲート（Phase 2 の plan 後、Phase 5 docs review 完了後、Phase 6 マージ前など現行 7 箇所→新 4 箇所）の対比表を §6.1 末尾に追加する。

### M3. 実運用 review automation で Phase 名が直接命名規則に出現する箇所への影響範囲が網羅されていない

**箇所**: `report.md` §5.1 「review automation は Phase 名と review 文書名に依存しているが、コードではなく skill 文書上の契約であり、契約更新で対応できる」/ §7.3 review / orchestration skill 更新リスト。

**事実**:
- `claude-review-automation/SKILL.md` 94〜103 行目に「Phase 5 は workflow ごとの suffix を使う」として `<topic>_docs_review.md`, `<topic>_feature_docs_review.md`, `<topic>_bugfix_docs_review.md`, `<topic>_issue_resolution_docs_review.md`, `<topic>_refactoring_docs_review.md` を直接定義している。
- `copilot-review-automation/SKILL.md` も同等の Phase 5 命名規則を持つ前提（同 skill が現状未読のため §7.3 で要件記載必須）。
- `ai-review-response-workflow/references/procedure/ai_review_response_workflow.md` §「出力ファイルの配置」にも同じ 5 種命名が直接列挙されている。
- `autonomous-workflow-orchestrator/SKILL.md` と `copilot-cli-workflow-orchestrator/SKILL.md` の禁止事項に「Phase 5 のユーザ動作確認ゲートをスキップしてはならない」が直接書かれている。

**何が問題か**: §7.3 では「prompt の `Phase <plan|design|impl|docs>` を `Phase <design|impl|completion>` へ変更」など簡潔な記述に留まり、実際の更新対象ファイルとセクション名が示されていない。ai-review-response-workflow に至っては §7.3 で「工程分類」「review 文書名テンプレート」と書かれるだけで、命名 5 種すべてが対象であることが伝わらない。次 workflow で「どのファイルのどの章を更新するか」を再調査する必要が出てしまう。

**修正案**:
- §7.3 を表形式に整理し、対象ファイル × 影響セクション × 変更内容を列挙する。例:
  - `claude-review-automation/SKILL.md` §「review 文書命名」: Phase 5 suffix 5 種を `<topic>_completion_review.md` 単一に集約 / または impl review に統合。
  - `copilot-review-automation/SKILL.md` 50 行目「Phase 4 review 完了とユーザ動作確認完了前に、Phase 5 の恒久ドキュメント同期を始めてはならない」: 文言ごと差替え / 削除。
  - `ai-review-response-workflow/references/procedure/ai_review_response_workflow.md` §「概要フロー」「出力ファイルの配置」: 工程分類 (`plan`/`design`/`impl`) と命名 5 種を更新。
  - `autonomous-workflow-orchestrator/SKILL.md` / `copilot-cli-workflow-orchestrator/SKILL.md`: 禁止事項「Phase 5 のユーザ動作確認ゲートをスキップしてはならない」を新 Phase 4 内 step（4-a 動作確認）へ書き換え。
- 該当行番号またはセクション名を「7.3 変更対象 一覧」に最低限残す。

### M4. `related_commits` を completion でまとめる方針が、研究 workflow / 多段レビュー文書での運用慣行と矛盾している

**箇所**: `report.md` §6.5、§8 リスク表「`related_commits` 更新 commit が増える」、§11 未解決事項 7。

**事実**:
- 現在の本 research の `meta.md` 自身が、Phase 1 / Phase 2 / Phase 2 補足 2 件の commit を逐次追記している（research_analysis_workflow の Phase 1〜Phase 4 ループで `meta.md` の `status` と `related_commits` を更新する手順が `research_analysis_workflow.md` §Phase 5 / コミット運用に明記）。
- Lanelet `20260506_scenario_v2_poc_round1_design/meta.md` は Round 1〜Round 3 のレビュー、Phase 5 完了処理、scope 補正など、12 commit を時系列に積んで運用上の証跡として機能させている。
- Lanelet 同 review 文書 m10 では、Phase 1 と Phase 2 が 1 commit にまとまったことを「次回以降の Phase 4 対応では各ラウンドを独立 commit で残す」「次ラウンド以降は Phase 単位で記録する」と是正している。

**何が問題か**:
- §6.5 の推奨「Phase 1 から Phase 3 の途中では `related_commits` を更新しない、または `pending` のままにする」は、研究 workflow の正本 procedure（各ラウンドコミット必須、`status` と `related_commits` の継続更新）と直接矛盾する。
- 多段レビュー（Round 1/2/3）を持つトピックでは、Round 単位の commit hash が `meta.md` から消えると、後続レビュアと指揮者が `git log` だけで対応関係を再構築する必要があり、コスト削減と相反する。
- `report.md` 自体が「core workflow 簡略化方針」の論点であって、研究 / レビュー多段運用に手を入れるかは別判断。論点を切り分けないまま「completion でまとめる」を全 workflow 共通推奨にすると影響範囲が拡大する。

**修正案**:
- §6.5 の適用範囲を「core workflow（spec-change / new-feature / bugfix / issue-resolution / refactoring）に限定」と明記する。
- 研究 / 多段レビュー topic では `related_commits` をラウンドごとに追記する従来運用を維持する旨を §6.5 末尾と §11 未解決事項に明示する。
- §11 未解決事項 7 を「core workflow では Phase 境界 + review/follow-up 主要 commit に絞る案、研究 / 多段レビュー topic では Round 単位記録を維持する案、を分けて確定する」に書き換える。
- §8 リスク表に「`related_commits` 省略により多段レビュー証跡が `meta.md` から欠落する」リスクと対策を追加する。

### M5. WBS 分解 skill の位置づけと既存 `research-analysis-workflow` の責務境界が確定していない

**箇所**: `report.md` §5.3、§7.4 WBS 分解 topic 推奨構成、§9 推奨実装順 8、§11 未解決事項 1。

**事実**:
- §7.4 の WBS 分解 topic は `docs/design_analysis/research_analysis/<YYYYMMDD>_<topic>_wbs/` 配下に置く想定で、`meta.md` / `report.md` / `wbs.md` を成果物にする。これは research_analysis category と同階層・同テンプレ。
- 既存 `research-analysis-workflow.md` の Phase 一覧は調査と report が中心で、WBS 分解（work package 化、依存関係、推奨 workflow 割当）に必要な成果物（`wbs.md`）と review ループ条件が定義されていない。
- §9 推奨実装順 8 は「WBS 分解用 skill を追加するか、少なくとも次フェーズの設計対象として起票する」と並列記述で、新 skill か派生かが未定。

**何が問題か**:
- §5.3 で「core workflow から大規模 planning を外す」を推奨しているのに、移し先の skill 仕様が未確定なため、次 spec-change workflow の Phase 0 が「core 簡略化」と「WBS skill 仕様確定」の二重スコープを抱えることになる。
- WBS 成果物が `research_analysis/...` 配下なら、調査 workflow の review/round 運用を流用できるか、独立の WBS workflow にするかで `meta.md` schema と review 文書命名が変わる。

**修正案**:
- §5.3 末尾に「2 案いずれかを次 spec-change workflow の Phase 0 で確定する」と明示する選択肢を 2 案で書き分ける。
  - 案 A: 新 skill `wbs-planning-workflow` を追加し、`docs/design_analysis/wbs/<YYYYMMDD>_<topic>/` を成果物配置先とする。
  - 案 B: 既存 `research-analysis-workflow` の派生として扱い、研究調査 topic と同じ `research_analysis/...` 配下で `wbs.md` を成果物に追加する Phase バリエーションを定義する。
- §7.4 の WBS 配置例を、案 A / 案 B 2 通り提示し、依存 schema を明示する。
- §9 推奨実装順 8 を「次 spec-change workflow の Phase 0 で 案 A / 案 B を確定する」「確定後の skill 仕様作成は別 spec-change workflow に分割する」と明確化する。

## 3. 中重大度指摘 (Moderate)

### Mod1. plan/design の重複項目主張が、5 種 workflow すべてで成立する根拠が示されていない

**箇所**: `report.md` §4.2 の「重複している、または同じ文書内に置いたほうが自然な項目」リスト。

**事実**: 確認できる範囲では `spec-change` の `phase_2_plan_focus.md`（受け入れ条件 / 影響範囲 / リスク等）と `phase_3_design_focus.md`（before/after / 責務分割 / 互換方針等）に部分的な重複は確認できた。一方で `bugfix` / `issue-resolution` / `refactoring` / `new-feature` の各 focus 文書については本 report 内で個別比較がない。

**何が問題か**: 5 種共通で plan/design 統合可と読める文体だが、根拠は spec-change 1 例のみ。bugfix の「再現条件・原因」と refactoring の「振る舞い不変確認」は plan と design の重複構造が異なる可能性がある。

**修正案**:
- §4.2 末尾に「5 種すべての focus 比較は次 spec-change workflow の Phase 0 で確認対象」と明記する、または各 workflow の `phase_2_plan_focus.md` / `phase_3_design_focus.md` を 1 行サマリで対比した表を追加する。

### Mod2. `meta.md` の status 分割（plan_status / design_status / impl_status）の移行戦略が両論併記で終わっている

**箇所**: `report.md` §6.3。

**事実**: §6.3 は「長期的には Phase 単位 status へ寄せる」と「移行期は `plan_status: N/A` で互換」を併記しており、判断基準が示されていない。`spec_change_workflow.md` のコミット運用、`phase_2_plan_review.md`〜`phase_5_verification_and_docs.md` の各 STOP では `plan_status` / `design_status` / `impl_status` を直接更新する step が手順に組み込まれている。

**何が問題か**: 次 spec-change workflow の Phase 2 設計時に、新 schema 一気切替か互換移行かで作業量が大きく変わる。判断基準が示されないと Phase 0 で何度も確認が必要。

**修正案**:
- §6.3 に判断基準（例: 過去 design_analysis 文書の数、review automation prompt 内 status 参照箇所、orchestrator が status を機械参照する箇所の有無）を列挙する。
- 推奨を 1 案に絞る（例: 「移行期 `plan_status: N/A` 互換、半年後または ADR 起票後に Phase 単位 status へ切替」）。

### Mod3. 推奨実装順 §9 の項目間依存が暗黙

**箇所**: `report.md` §9 1〜10。

**事実**: §9 は番号付きだが、各項目間の依存関係（先行必須 / 並列可 / 検証順）が明示されていない。例えば項目 3（shared common phase library 更新）は項目 4（core workflow 更新）の前提だが、項目 5（ai-review-response-workflow 更新）と項目 6（review automation / orchestrator 更新）は項目 4 完了に依存する。

**何が問題か**: 次 spec-change workflow の WBS 分解時に、依存関係を再構築する必要がある。`spec-change-workflow` の Phase 4 実装順で混乱を招く。

**修正案**:
- §9 を依存表に整形する。最低限「ステップ → 先行依存 → 検証手段」の 3 列を示す。
- 並列実行可能な項目（例: 7 と 9 など）と直列必須（例: 3 → 4 → 5,6）を明示する。

### Mod4. ユーザ承認ゲート削減後の代替検証手段が示されていない

**箇所**: `report.md` §6.1、§6.2、§7.3 ユーザ承認ゲート関連。

**事実**: 現行 `spec_change_workflow.md` のユーザ承認ゲートは 7 箇所、推奨案は 4 箇所。M2 の指摘で対比表追加を求めたが、削除される 3 箇所について「人間ゲートを失っても品質が保てる代替手段」（自動 review 通過、checklist 完了、status 検査など）が示されていない。

**何が問題か**: ゲート削減はトークン削減に直結する利点だが、「どの手段で品質が担保されるか」を示さないと、次 workflow で安易に承認ゲートを足し戻す逆行が起きやすい。

**修正案**:
- §6.1 末尾または §6.2 末尾に「削除する承認ゲート × 代替検証」表を追加する。例: Phase 5 docs review 完了承認 → impl review に集約された docs 整合チェック / completion checklist の項目化。

## 4. 軽微指摘 (Minor)

### m1. `meta.md` `related_commits` のフォーマットと procedure 規定の整合

**箇所**: `meta.md` `related_commits` 欄。

**事実**: 4 件すべて `<commit_hash> : Phase <番号> <要約>` の形式で記載されており、`research_analysis_workflow.md` §コミット運用の `- <commit_hash> : Phase <番号> <要約>` と整合している。Lanelet `20260506_scenario_v2_poc_round1_design` の m10 で問題になった `Phase 1+2` 並記の事例には該当しない。

**コメント**: 形式は適合。問題なし。記録としてのみ残す。

### m2. WBS 成果物 `wbs.md` のフィールド定義粒度

**箇所**: `report.md` §5.3 末尾の `wbs.md` 必須項目リスト。

**事実**: `work package ID` / `推奨 workflow` / `依存 work package` / `目的` / `完了条件` / `主な変更対象` / `docs 更新先` / `検証観点` / `follow-up / deferred 判断` が列挙されている。

**問題**: `推奨 workflow` の許容値（5 種 workflow + WBS 派生の有無）と、`work package ID` の命名規則（既存 todo / issue ID と独立か、紐付けるか）が未定義。

**修正案**: §5.3 末尾の項目リストに「許容値」「命名規則」「他 ID との関連」を追記する。

### m3. §7.4 推奨構成の `review/` ディレクトリの位置づけ

**箇所**: `report.md` §7.4 推奨構成例。

**事実**: 推奨構成では `review/<topic>_design_review.md` / `<topic>_impl_review.md` を提示しているが、`docs/design_analysis/README.md` の標準構成更新に反映するファイル名（`<topic>_completion_review.md` を含めるか optional か）が §6.4 と §7.4 で完全に揃っていない。

**修正案**: §6.4 と §7.4 を「completion_review は optional」「必要時のみ追加」で文言を一致させる。

### m4. ADR 索引参照の現状確認のみで活用方針がない

**箇所**: `report.md` §3 末尾「関連 ADR は空」。

**事実**: 2026-05-10 時点で `docs/adr/README.md` が空であることは事実。確認済み。

**問題**: 本 simplification は orchestrator / review automation を含む横断仕様変更で、本来 ADR 候補。「未起票」と書くだけで終わらず、`9 推奨実装順` のどこで ADR を起票するか提案するほうが次 workflow に渡しやすい。

**修正案**: §9 に「Phase 簡略化採用判断を ADR-X-001（仮）として起票する」step を追加する、または §11 未解決事項に追加する。

### m5. §4.4 の Lanelet 数値根拠の出典

**箇所**: `report.md` §4.4 の `plan` 214 行 / `design` 450 行 / `impl` 216 行 / review 文書合計 745 行 / `report.md` 123 行 / 28 commit。

**事実**: `report.md` の commit 一覧で 28 commit は確認できた。行数は本レビュー内で逐次確認していないが、`report.md` `Range From: 09435b38 To: cea780c2 / Commits: 28` の commit 数と一致する。

**問題**: 行数は将来の編集で揺れる可能性があるため、参照時点を明示するほうが再現性が上がる。

**修正案**: §4.4 冒頭に「(2026-05-10 時点)」と明記する。

### m6. recommendations と未解決事項の重複

**箇所**: `report.md` §6.3、§6.5、§11 未解決事項 2 / 6 / 7。

**事実**: §6.3 で示した移行案、§6.5 の `related_commits` 運用、§11 未解決事項 2 / 6 / 7 が同一論点を別言語で記述している。

**問題**: 次 workflow で「結論済み」「未確定」の境界が分かりにくい。

**修正案**: §11 を「§ から提示した推奨案のうち、確定 / 未確定 / 別 workflow へ持ち越し」の 3 列表で再整理する。

### m7. WBS 派生 commit 粒度許容（Phase 並記）の方針が未提示

**箇所**: `report.md` §11 未解決事項 6。

**事実**: Lanelet review m10 で「複数 Phase を含む commit は Phase 並記表記（`Phase 1+2:`）に統一」が推奨されている。本 report はこの先例を引用しつつ、推奨を出さず「未解決」のままにしている。

**修正案**: §6.5 または §11 に「実運用上、複数 Phase を含む commit が出た場合は `Phase X+Y` の並記許容」を推奨明記する。

### m8. リスク表 §8 の対策粒度のばらつき

**箇所**: `report.md` §8 リスク表。

**事実**: 行ごとに対策粒度が異なる。「design 文書の先頭に要求・完了条件・非対象・採否理由を必須章として置く」など具体的な行と、「core workflow と review/orchestrator skill を同一仕様変更で更新し、smoke test を行う」のように高粒度の行が混在。

**修正案**: 各行の対策に、対応 §（例: §6.1 / §7.3）への参照を追加して、変更必要箇所を辿りやすくする。

## 5. 観点別チェック結果

| 観点 | 評価 | 主要指摘 |
|---|---|---|
| plan/design 統合の推奨が、実運用サンプルと矛盾していないか | 部分的に矛盾 | M1 (Lanelet refactoring サンプル過大解釈), Mod1 (5 種共通根拠不足) |
| WBS 分解 skill 分離が core workflow 簡略化方針として妥当か | 方向は妥当だが未確定 | M5 (skill 位置づけ未確定), m2 (`wbs.md` 項目粒度) |
| docs 反映を impl と completion に分ける案の漏れ・副作用 | 漏れあり | M1, M2 (動作確認 NG / merge / archive / history 順序), Mod4 (削除ゲート代替) |
| `workflow_phase_library/common` を source 正本として install/sync で hydrate する前提の取り扱い | 整合 | (適合。`hydrate_workflow_phase_library_common` 関数で実装確認済み) |
| `related_commits` を completion でまとめる案と review automation / 研究 workflow 証跡要件の整合 | 矛盾あり | M4 (研究 workflow / 多段レビュー証跡との衝突) |
| 次の spec-change workflow へ渡せる粒度・実装順 | 不足 | M3 (影響範囲列挙不足), Mod3 (依存関係不明), m6 (推奨と未解決事項の重複) |

## 6. 次ラウンドへの依頼事項

- 本レビューの Major M1〜M5 に対応した `report.md` の更新と、レビュー対応状況を本ファイルに追記してほしい。
- Moderate / Minor は同一ラウンドでの解消を推奨する。次 spec-change workflow の Phase 0 までに片付けば許容する。
- 対応後、本ファイル末尾の「対応状況」表に項目ごとの結果を記録してから再レビュー依頼をお願いする。

## 7. 承認可否

**条件付き未承認**。Major M1〜M5 の解消後に再レビューを実施して承認可否を再判断する。Moderate Mod1〜Mod4、Minor m1〜m8 は、解消が次 spec-change workflow Phase 0 までに完了することを推奨する。
