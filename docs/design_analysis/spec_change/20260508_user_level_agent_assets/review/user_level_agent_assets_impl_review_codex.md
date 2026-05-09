# ユーザレベル Agent 資産化 実装レビュー（Codex）

## レビュー対象

- 調査: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
- 設計: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md`
- 実装差分:
  - `.gitignore`
  - `scripts/rebuild_user_agent_skills.py`
  - `user-agent-assets/**`
  - `reference/**`（未追跡）

## 結論

現状の実装は、workflow skill の user-level 正本化と `references/` 化の土台はできているが、移行先構成としては未完了である。
特に installer の default 挙動、tmux wrapper の実行権限、Windows runtime、`project-doc-bootstrap` 欠落は、実際の user-level 利用で破綻する可能性が高い。

2026-05-09 commit `c233403` の再確認では、既存の追加指摘は概ね解消済みである。
High-2 相当の repo 直下 / 既存 template ripple は current phase の即時変更ではなく、`project-doc-bootstrap` を起点に target project へ project-level files と `sync_agent_instructions.*` を配る staged migration へ設計更新したうえで、移行完了後の follow-up に移した。
一方で、bootstrap の placeholder scan 範囲不足と PowerShell sync script の `param` 位置について追加指摘が残る。

## 対応状況（2026-05-09 更新）

| 指摘 | 状況 | 対応メモ |
|---|---|---|
| 1. existing skill への missing install 不備 | 対応済み | installer の file 単位 merge は維持しつつ、`missing` では既存 `SKILL.md` を更新しないため移行時は `--mode overwrite` 必須であることを install README へ明記した |
| 2. macOS / Linux tmux wrapper 実行権限 | 対応済み | source 側の実行ビット付与と install 時 `chmod 755` を追加した |
| 3. Windows runtime placeholder | 対応済み | `.ps1` wrapper を exe 優先 + Python fallback に変更し、placeholder 単体で即失敗しない契約へ寄せた |
| 4. `project-doc-bootstrap` 未実装 | 対応済み | skill 本体と wrapper に加え、template から `skill_catalog.md` を削除し、target docs reference も user-level skill 前提へ整理した |
| 5. suite skill payload 方針の設計未反映 | 対応済み | 設計書 Section 6.1 / 7.2 / 7.3 / 7.4 を現実装の slim payload 方針へ更新した |
| 6. 不正 `--targets` でも helper 先書き込み | 対応済み | target validation を runtime/helper copy より前へ移動した |
| 7. `reference/` 混入 | 対応済み | `.gitignore` へ `reference/` を追加し、作業用 clone 混入を避けた |
| 追加1. Claude 側 High-2 対応状況の実態不一致 | 方針更新で current phase 対象外 | repo 直下 / 既存 template は移行完了まで無変更とし、`project-doc-bootstrap` から target project へ docs、project-level `agent_common_master.md`、`agent_sync_guide.md`、`sync_agent_instructions.*` をコピーする staged migration に設計更新した |
| 追加2. bootstrap の placeholder scan 範囲不足 | 未対応 | docs だけを scan しており、同時にコピーする `instructions/agent_common_master.md` の `{{PROJECT_NAME}}` が一覧に出ない |
| 追加3. PowerShell sync script の `param` 位置 | 未対応 | `Set-StrictMode` が `param(...)` より前にあり、PowerShell script としての起動に失敗する可能性が高い |

備考:

- `pwsh` がローカル環境に無いため、PowerShell wrapper / installer の実行検証だけは未実施

## 指摘対応確認（commit c233403）

対象コミット: `c2334032f693d9221463c1cc1175713643e6749f`

### 対応済み確認

- `project-doc-bootstrap/templates/*/docs/rules/skill_catalog.md` は削除済み
- `references/*-target-docs.md` から `instructions/skills/**/*.md` の置換案内は削除済み
- 設計は、repo 直下 / 既存 template を current phase で直接変更せず、`project-doc-bootstrap` から target project へ docs / project-level instructions / sync script を配る staged migration 方針へ更新済み
- 隔離した Python target project で `copy_doc_templates.sh` を実行し、docs 雛形、`instructions/agent_common_master.md`、`instructions/agent_sync_guide.md`、`scripts/sync_agent_instructions.*` が配置されることを確認済み
- 同 target project で `scripts/sync_agent_instructions.sh --help` と `scripts/sync_agent_instructions.sh` の直接実行が成功し、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` が再生成されることを確認済み
- `rg` 上、bootstrap 生成先には旧 `skill_catalog` / `instructions/skills` / `scripts/agent_cli_tmux.py` / `tools/AgentCliTmux` / `SKILL.master` / template-doc-filler / `docs/procedure` 参照は残っていない
- `python3 -m py_compile scripts/rebuild_user_agent_skills.py user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py` は成功
- `bash -n user-agent-assets/install/install_user_agent_assets.sh user-agent-assets/bin/agentic-agent-cli-tmux.sh user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.sh user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.sh` は成功

### 追加指摘

#### D. [Medium] bootstrap の placeholder scan が `docs/` だけを対象にしており、コピー済み instructions の `{{PROJECT_NAME}}` を見落とす

`project-doc-bootstrap` は docs だけでなく `instructions/agent_common_master.md` も target project へコピーする。
しかし `copy_doc_templates.sh` / `.ps1` の placeholder scan は `docs/` 配下だけを対象にしている。

- `user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.sh:59-69`
- `user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.ps1:59-68`
- `user-agent-assets/skills/project-doc-bootstrap/templates/python/instructions/agent_common_master.md:1`
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/instructions/agent_common_master.md:1`

隔離 target project で bootstrap 後に `sync_agent_instructions.sh` を実行すると、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` に `# {{PROJECT_NAME}} Agent Project Instructions` がそのまま同期された。
`references/python-target-docs.md` / `csharp-target-docs.md` では `instructions/agent_common_master.md` の `{{PROJECT_NAME}}` 置換を高優先度で案内しているが、wrapper の一覧に出ないため見落としやすい。

対応案:

- placeholder scan 対象を `docs/` だけでなく、少なくとも `instructions/` と生成済み `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` まで広げる
- `project-doc-bootstrap/SKILL.md` の「copy 後に placeholder 一覧を確認」を「docs / instructions の placeholder 一覧」と明記する
- `sync_agent_instructions.*` 実行前に `instructions/agent_common_master.md` の placeholder が解消済みであることを check する

#### E. [Medium] `sync_agent_instructions.ps1` の `param` block が先頭にない

PowerShell の script parameter block は、コメント等を除いて script の先頭に置く必要がある。
現在の `sync_agent_instructions.ps1` は `Set-StrictMode` と `$ErrorActionPreference` の後に `param(...)` がある。

- `user-agent-assets/skills/project-doc-bootstrap/templates/common/scripts/sync_agent_instructions.ps1:5-14`

この配置では `pwsh -File scripts/sync_agent_instructions.ps1 -Help` 等が PowerShell script として正常に parameter binding されない可能性が高い。
ローカル環境には `pwsh` が無いため実行検証は未実施だが、同じ `project-doc-bootstrap/bin/copy_doc_templates.ps1` や install script は `param(...)` を先頭に置いており、こちらへ揃えるべきである。

対応案:

- `param(...)` を shebang / コメント直後へ移動し、その後に `Set-StrictMode` と `$ErrorActionPreference` を置く
- `pwsh -File scripts/sync_agent_instructions.ps1 -Help` と `pwsh -File scripts/sync_agent_instructions.ps1 -All` を Phase 5 検証項目に追加する

## 追加指摘対応後の確認（2026-05-09）

- A は `user-agent-assets/install/README.md` に移行時の `--mode overwrite` 必須を追記して解消した
- B は repo 直下 / 既存 template を先に変えず、`project-doc-bootstrap` が target project へ project-level files と `sync_agent_instructions.*` を供給する staged migration を設計へ反映して current phase の blocking から外した
- C は `project-doc-bootstrap` template から `skill_catalog.md` を削除し、target docs reference から `instructions/skills/**/*.md` 置換案内を除去して解消した

## 指摘対応確認（commit 5d200dc）

対象コミット: `5d200dcac387f9b58b192cb20935d90f17b6c49b`

### 未解決 / 追加指摘（対応前記録）

#### A. [High] 既存 `SKILL.md` は default `missing` install では更新されない

`install_user_agent_assets.sh` / `.ps1` は directory については file 単位 merge するよう修正された。
ただし、既存 file は `missing` mode で skip されるため、既存 user-level skill の `SKILL.md` は更新されない。

- `user-agent-assets/install/install_user_agent_assets.sh:66-73`
- `user-agent-assets/install/install_user_agent_assets.ps1:45-52`

隔離した `HOME` に古い `~/.codex/skills/spec-change-workflow/SKILL.md` を置いて install したところ、`old docs/procedure/spec_change_workflow.md scripts/agent_cli_tmux.py` が残り続けた。
したがって、既存環境の移行には `--mode overwrite` が必須である。

対応案:

- README とレビュー対応状況に「既存 `SKILL.md` の移行は `--mode overwrite` 必須」と明記する
- もしくは `--mode merge` / `--mode migrate` のような移行用 mode を追加し、managed file は更新、ユーザ追加 file は維持する

#### B. [High] Claude 側レビューの `High-2` は対応済み表示だが、実装は未対応

Claude レビュー文書では `High-2` が「root / Python / C# の `agent_common_master.md` を薄い index 化し、sync script を instruction output 再生成専用へ縮小した」として対応済みになっている。
しかし、対象コミットには `instructions/`、`python-project-template/instructions/`、`csharp-project-template/instructions/`、`scripts/sync_agent_skills.*` の変更が含まれていない。

- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_impl_review_claude.md:43-46`
- `instructions/agent_common_master.md:18-19`
- `python-project-template/instructions/agent_common_master.md:18-19`
- `csharp-project-template/instructions/agent_common_master.md:18-19`

現状でも `skill_catalog.md` / `docs/procedure/README.md` / `docs/procedure/` 参照が残っているため、project-level 薄化と sync script 縮小は未完了として扱う必要がある。

対応案:

- 実装側で root / template の薄化と sync script 縮小を行う
- まだ Phase 4 の後続作業として残すなら、Claude レビュー文書の対応状況を「未対応 / 後続対応」に戻す

#### C. [Medium] `project-doc-bootstrap` が削除方針の `skill_catalog.md` と旧参照を再導入している

`project-doc-bootstrap` は追加されたが、テンプレート配下に `docs/rules/skill_catalog.md` が含まれている。
さらに、その内容には旧 workspace skill / repo-local helper 前提の参照が残っている。

- `user-agent-assets/skills/project-doc-bootstrap/templates/python/docs/rules/skill_catalog.md:43-67`
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/docs/rules/skill_catalog.md:43-67`
- `user-agent-assets/skills/project-doc-bootstrap/references/python-target-docs.md:13-15`
- `user-agent-assets/skills/project-doc-bootstrap/references/python-target-docs.md:85-88`
- `user-agent-assets/skills/project-doc-bootstrap/references/csharp-target-docs.md:13-16`

特に `scripts/agent_cli_tmux.py`、`tools/AgentCliTmux`、`instructions/skills/*/SKILL.master.md`、`python-template-doc-filler` / `csharp-template-doc-filler` は、user-level assets 正本化後の導線と矛盾する。
また、設計書では `skill_catalog.md` は削除方向であり、project docs 雛形として再配布すると削除 ripple を打ち消す。

対応案:

- `project-doc-bootstrap/templates/*/docs/rules/skill_catalog.md` を削除する
- bootstrap 後の workflow 案内は `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の薄い index と user-level skill 名に寄せる
- `references/*-target-docs.md` から `instructions/skills/**/*.md` の置換案内を削除し、user-level skill は置換対象外であることを明記する

### 対応済み確認

- `.gitignore` の `user-agent-assets/bin/**` / `user-agent-assets/skills/*/bin/**` unignore は有効で、`git check-ignore` でも wrapper は無視されない
- `user-agent-assets/bin/agentic-agent-cli-tmux.sh` と `project-doc-bootstrap/bin/copy_doc_templates.sh` は `100755` で commit されている
- invalid `--targets unknown` は helper / runtime 書き込み前に終了する
- `project-doc-bootstrap` skill、shell wrapper、PowerShell wrapper、templates / references は追加済み
- 隔離した Python target project で `copy_doc_templates.sh` を実行し、docs 雛形、`instructions/agent_common_master.md`、`instructions/agent_sync_guide.md`、`scripts/sync_agent_instructions.*` が配置されることを確認した
- 同 target project で `scripts/sync_agent_instructions.sh --help` と `scripts/sync_agent_instructions.sh` の直接実行が成功し、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` が再生成されることを確認した
- `reference/` は `.gitignore` 対象になっている
- `python3 -m py_compile scripts/rebuild_user_agent_skills.py user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py` は成功
- `bash -n user-agent-assets/install/install_user_agent_assets.sh user-agent-assets/bin/agentic-agent-cli-tmux.sh user-agent-assets/skills/project-doc-bootstrap/bin/copy_doc_templates.sh` は成功
- 隔離した `HOME` への `--targets codex` 実 install は成功し、shared common hydrate と shell wrapper 実行権限付与も確認済み

## 指摘

### 1. [High] 既存 user-level skill がある環境では、default install で新しい `SKILL.md` / references が配布されない

`install_user_agent_assets.sh` / `.ps1` は `missing` mode で対象パスが存在するとディレクトリ単位で skip する。
設計は file ごとの missing-only 判定を要求しているが、実装は skill directory が存在するだけで `SKILL.md` と通常 references の更新・追加を止める。

- `user-agent-assets/install/install_user_agent_assets.sh:39-45`
- `user-agent-assets/install/install_user_agent_assets.sh:90-91`
- `user-agent-assets/install/install_user_agent_assets.ps1:25-33`
- `user-agent-assets/install/install_user_agent_assets.ps1:77-78`

このため、既に `~/.codex/skills/spec-change-workflow` 等があるユーザ環境では、旧 skill が残り続ける。
今回の移行目的である `docs/procedure/` 非依存化や wrapper 参照への書き換えが適用されず、移行後に project-level `docs/procedure/` を削ると workflow が壊れる。

対応案:

- directory 単位ではなく file 単位で再帰コピーし、既存 file は skip、新規 file は追加する
- 既存 `SKILL.md` を保護したい場合でも、`--mode missing` の仕様として「既存 skill directory 内の未存在 references は補完する」ことを明示実装する
- 既存 skill をあえて更新しない運用なら、`missing` では移行できないことを README に明記し、移行用 `--mode overwrite` または `--mode merge` を用意する

### 2. [High] macOS / Linux の tmux wrapper が実行不可の権限で配布される

各 orchestration / review skill は `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh` を直接実行する前提になっている。
一方で、実ファイルは `-rw-r--r--` で、installer もコピー後に `chmod +x` していない。

- `user-agent-assets/skills/copilot-review-automation/SKILL.md:118`
- `user-agent-assets/bin/agentic-agent-cli-tmux.sh:1-13`
- `user-agent-assets/install/install_user_agent_assets.sh:118`
- `user-agent-assets/install/install_user_agent_assets.ps1:101`

この状態で skill の手順どおりに `~/.agentic-project-templates/bin/agentic-agent-cli-tmux.sh ensure ...` を実行すると、macOS / Linux では `Permission denied` になる。

対応案:

- repository 上で `agentic-agent-cli-tmux.sh` に executable bit を付ける
- install script 側でもコピー後に `chmod 755 "$helper_root/bin/agentic-agent-cli-tmux.sh"` を実行する
- PowerShell wrapper も Windows 実行ポリシーを考慮し、README に `pwsh -File ...` での呼び出し契約を明記する

### 3. [High] Windows runtime が placeholder のままで、PowerShell wrapper は必ず失敗する

設計では `runtime/agent-cli-tmux/win-x64/AgentCliTmux.exe` を配置する構成になっている。
しかし実装には `AgentCliTmux.exe` がなく、`win-x64/README.md` に placeholder と follow-up 予定だけがある。
PowerShell wrapper はこの exe の存在を必須としているため、Windows では常に `runtime helper not found` で終了する。

- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:70-71`
- `user-agent-assets/bin/agentic-agent-cli-tmux.ps1:1-11`
- `user-agent-assets/runtime/agent-cli-tmux/win-x64/README.md:1-4`

対応案:

- Phase 4 の完了対象に Windows を含めるなら、`AgentCliTmux.exe` を配置して wrapper を動作可能にする
- まだ Windows を非対応にするなら、install script / README / design の target から Windows runtime を明示的に外す
- 暫定的には `.ps1` wrapper から Python runtime を呼ぶ実装へ寄せる方が、現在の payload と整合する

### 4. [High] `project-doc-bootstrap` が未実装で、docs 移行の受け入れ条件を満たしていない

設計では `project-doc-bootstrap` を user-level assets の必須構成に含め、docs 雛形コピー、missing-only / overwrite、placeholder 一覧化を担わせるとしている。
現在の `user-agent-assets/skills/` には `project-doc-bootstrap` が存在しない。

- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:90-97`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:377-410`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:456-459`
- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:500-507`

これにより、docs 雛形を user-level skill から project へ実体化する導線がなく、調査レポートの「docs はユーザレベルに置くのではなく、雛形を user-level skill に同梱して必要時にコピーする」という結論も実装されていない。

対応案:

- `user-agent-assets/skills/project-doc-bootstrap/` を追加する
- `templates/common`, `templates/python`, `templates/csharp`, `references/`, `bin/copy_doc_templates.sh`, `bin/copy_doc_templates.ps1` を設計どおり配置する
- installer の skill 配布対象に含め、missing-only / overwrite / placeholder listing の検証を追加する

### 5. [Medium] orchestration / review automation 系 skill の reference payload 方針が設計ドキュメントへ未反映

補足確認により、`copilot-review-automation`、`claude-review-automation`、`autonomous-workflow-orchestrator`、`copilot-cli-workflow-orchestrator` が 5 workflow 本体・phase library・`ai_review_response_workflow.md` を全コピーしない構成は、メンテナンスコストを抑えるための明示方針であると確認した。
したがって実装不備ではない。

一方で、現行設計ドキュメントの dependency map は「5 workflow 本体とその phase library を丸ごと持つ」前提のままであり、実装済み方針と整合していない。

- `docs/design_analysis/spec_change/20260508_user_level_agent_assets/design/user_level_agent_assets_design.md:319-337`
- `scripts/rebuild_user_agent_skills.py:61-80`
- `user-agent-assets/skills/copilot-review-automation/SKILL.md:23-34`
- `user-agent-assets/skills/autonomous-workflow-orchestrator/SKILL.md:28-40`
- `user-agent-assets/skills/copilot-cli-workflow-orchestrator/SKILL.md:22-34`

現状の本文は「同時に install される他 skill を skill 名で参照する」形であり、default install で全 workflow skill が同時配布される運用とは整合する。
ただし設計書が古いままだと、後続レビューや実装者が「全 procedure コピーへ戻す」誤修正を行うリスクがある。

対応案:

- 設計の dependency map を「orchestration / review automation 系は procedure を重複コピーせず、同時 install される workflow skill 名を参照する」方針へ更新する
- `self-contained` の定義を「各 workflow skill は自身の procedure を持つ」「orchestration / review automation 系は install bundle 全体を前提に skill 間参照する」と分けて明記する
- selective install をサポートしない、または orchestration 系を選ぶ場合は依存 workflow skill も同時 install する、という install 契約を README に追記する

### 6. [Medium] 不正 `--targets` 指定でも helper / runtime が先に書き込まれる

shell installer は target validation より前に `install_single_runtime` を実行する。
そのため `--targets unknown` のような不正入力でも、エラー終了前に `~/.agentic-project-templates/` 配下へ書き込みが発生する。

- `user-agent-assets/install/install_user_agent_assets.sh:197`
- `user-agent-assets/install/install_user_agent_assets.sh:200-215`

install script は user home を変更するため、引数検証は書き込み前に完了しているべきである。

対応案:

- `parse_args` 後に target list を検証してから `install_single_runtime` を呼ぶ
- PowerShell 側も helper copy 前に `$Targets` の全要素を検証する構成へ揃える

### 7. [Medium] `reference/` 配下に別リポジトリと `.git` が未追跡で存在している

`git status --short` で `?? reference/` が出ており、配下には `reference/LaneletMapViewPy/.git/**` を含む別リポジトリ全体が存在する。
`.gitignore` の変更は `tmp/` 追加のみで、`reference/` は ignore されていない。

- `.gitignore:57-60`
- `reference/LaneletMapViewPy/.git/**`

このまま staging すると、調査用 clone や `.git` object を誤って取り込むリスクがある。

対応案:

- 実装に不要なら `reference/` を作業ツリー外へ移す
- 調査用に残すなら `.gitignore` に `reference/` を追加する
- レビュー/コミット前に `git status --short` で未追跡の混入を必ず確認する

## 補足確認

次は確認済み。

- `rg` 上、生成済み `user-agent-assets/skills` 本文には旧 `docs/procedure/` 直接参照は残っていない
- core workflow skill の個別 `workflow_phase_library/<type>/` は `references/` 配下へコピーされている
- `shared/references/procedure/workflow_phase_library/common/` には共通 Phase 6 ファイルが配置されている
- `bash user-agent-assets/install/install_user_agent_assets.sh --dry-run --targets codex` は終了コード 0
- `python3 -m py_compile scripts/rebuild_user_agent_skills.py user-agent-assets/runtime/agent-cli-tmux/python/agent_cli_tmux.py` は終了コード 0
- `bash -n user-agent-assets/install/install_user_agent_assets.sh user-agent-assets/bin/agentic-agent-cli-tmux.sh` は終了コード 0

ただし、上記は構文・ドライラン確認であり、Copilot / Claude / Codex の user-level skill 検出 smoke test、PowerShell dry-run、template 側検証、docs bootstrap 検証は未確認である。
