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

## 対応状況（2026-05-09 更新）

| 指摘 | 状況 | 対応メモ |
|---|---|---|
| 1. existing skill への missing install 不備 | 対応済み | installer を file 単位 merge へ修正し、既存 skill dir 配下の未配置 `SKILL.md` / references を補完できるようにした |
| 2. macOS / Linux tmux wrapper 実行権限 | 対応済み | source 側の実行ビット付与と install 時 `chmod 755` を追加した |
| 3. Windows runtime placeholder | 対応済み | `.ps1` wrapper を exe 優先 + Python fallback に変更し、placeholder 単体で即失敗しない契約へ寄せた |
| 4. `project-doc-bootstrap` 未実装 | 対応済み | `user-agent-assets/skills/project-doc-bootstrap/` を追加し、templates / references / shell / PowerShell wrapper を実装した |
| 5. suite skill payload 方針の設計未反映 | 対応済み | 設計書 Section 6.1 / 7.2 / 7.3 / 7.4 を現実装の slim payload 方針へ更新した |
| 6. 不正 `--targets` でも helper 先書き込み | 対応済み | target validation を runtime/helper copy より前へ移動した |
| 7. `reference/` 混入 | 対応済み | `.gitignore` へ `reference/` を追加し、作業用 clone 混入を避けた |

備考:

- `pwsh` がローカル環境に無いため、PowerShell wrapper / installer の実行検証だけは未実施

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
