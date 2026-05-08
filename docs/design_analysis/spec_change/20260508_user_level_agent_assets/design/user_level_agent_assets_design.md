# ユーザレベル Agent 資産化（SC-20260508-001）設計書

## レビュー反映履歴

| 日時 | 対応内容 |
|------|---------|
| 2026-05-08 | 初版作成（Phase 3 pre-review） |
| 2026-05-09 | root 正本の `instructions/skills` / `docs/procedure` 棚卸し結果を反映し、reference 移行ルールと shared common hydrate 方針を再定義 |

---

## 1. 目的

Python / C# テンプレートと root に重複している workflow skills、Agent instructions、`docs/procedure/` 系資産を、user-level Agent assets を正本とする構成へ移行する。

本設計では、次を実装可能な粒度で確定する。

- user-level 正本ディレクトリの配置と中身
- project-level の薄い index / 固有ルールとの責務分離
- install script と sync script の責務分担
- workflow skill の self-contained 化と `references/` 参照方式
- docs bootstrap skill の構造と OS 別 wrapper 方針
- Copilot user-level skill の検証方針

## 2. 設計入力

### 2.1 承認済み入力

- 調査レポート: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/report.md`
- 調査レビュー: `docs/design_analysis/research_analysis/20260507_user_level_agent_assets/user_level_agent_assets_report_review.md`
- Phase 2 計画書: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/plan/user_level_agent_assets_plan.md`
- Phase 2 計画レビュー: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/review/user_level_agent_assets_plan_review.md`

### 2.2 設計で解消する論点

1. Copilot 向け install 先の優先順位と互換方針
2. user-level install と repo 内 sync の分離境界
3. docs bootstrap skill の template / references / wrapper 構成
4. `skill_catalog.md` 削除 ripple の具体対象
5. Copilot user-level skill の検証方針

## 3. before / after 仕様差分

| 観点 | Before | After |
|---|---|---|
| workflow skill 正本 | root / Python / C# template に重複配置された `instructions/skills/*/SKILL.master.md` | `user-agent-assets/skills/*/SKILL.md` を正本とし、install script で user-level へ配布 |
| workflow 手順参照 | skill 本文から project-level `docs/procedure/*` を前提参照 | 各 skill の `references/procedure/` を参照する self-contained 構成 |
| Agent instructions | `agent_common_master.md` に共通原則と project 固有ルールが混在 | 共通原則は user-level、project-level は index / コマンド / 固有制約へ分離 |
| docs 雛形 | template ごとに docs 雛形や doc filler が分散 | `project-doc-bootstrap` skill の `templates/` と `references/` へ集約 |
| sync script | project-level 生成物と skill 同期を一体で扱う | install script は user-level 配布、sync script は repo 内生成物更新に限定 |
| Copilot skill 配布 | workspace skill と template 同梱が混在 | user-level skill を正本とし、workspace fallback は持たない |

本件は UI 変更を伴わない。変更対象は配布構成、Agent の参照導線、テンプレートの docs / instructions 契約である。

## 4. ターゲット構成

### 4.1 新しい正本ディレクトリ

root 直下に user-level 正本を配置する。

```text
user-agent-assets/
├── bin/
│   ├── agentic-agent-cli-tmux.sh
│   └── agentic-agent-cli-tmux.ps1
├── runtime/
│   └── agent-cli-tmux/
│       ├── python/
│       │   └── agent_cli_tmux.py
│       └── win-x64/
│           └── AgentCliTmux.exe
├── instructions/
│   ├── common_agent_principles.md
│   └── language_policy.md
├── skills/
│   ├── spec-change-workflow/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── procedure/
│   ├── new-feature-workflow/
│   ├── bugfix-workflow/
│   ├── issue-resolution-workflow/
│   ├── refactoring-workflow/
│   ├── research-analysis-workflow/
│   ├── autonomous-workflow-orchestrator/
│   ├── copilot-cli-workflow-orchestrator/
│   ├── ai-review-response-workflow/
│   ├── copilot-review-automation/
│   ├── claude-review-automation/
│   └── project-doc-bootstrap/
│       ├── SKILL.md
│       ├── templates/
│       │   ├── common/
│       │   ├── python/
│       │   │   └── docs/
│       │   └── csharp/
│       │       └── docs/
│       ├── references/
│       └── bin/
├── shared/
│   └── references/
│       └── procedure/
│           └── workflow_phase_library/
│               └── common/
└── install/
    ├── install_user_agent_assets.sh
    ├── install_user_agent_assets.ps1
    └── README.md
```

設計判断:

- user-level 正本は `instructions/` と `skills/` を同じトップレベルに置き、repo 内で version 管理する
- 実行時に使う skill は placeholder を持たない `SKILL.md` を正本とする
- 既存 `SKILL.master.md` は Phase 4 で user-level 正本へ移した後、project-level 生成用途が残る場合だけ限定維持する
- orchestration skill (`autonomous-workflow-orchestrator`, `copilot-cli-workflow-orchestrator`) も user-level 正本化対象に含める

### 4.2 project-level に残すもの

各 template と root project-level に残すのは、対象 project の固有情報だけとする。

- `instructions/agent_common_master.md` と `instructions/*.draft.md`
  - 役割: 薄い index、実行コマンド、project 固有制約、成果物置き場案内
- `docs/rules/project_overview.md`, `docs/rules/development_workflow.md`, `docs/rules/coding_rules.md`
  - 役割: project 固有ルールと検証コマンド
- `docs/architecture/*`, `docs/tests/*`, `docs/issues/*`, `docs/todo/*`, `docs/history/*`
  - 役割: project 実体 docs

project-level から削減対象にするもの:

- template 同梱 workflow skills
- template 同梱 `docs/procedure/`
- `docs/rules/skill_catalog.md`

### 4.3 `agent_common_master.md` の After 構成

root / Python / C# の `instructions/agent_common_master.md` は、次の共通セクション骨格へ揃える。

1. 目的
  - 対象 project の範囲と template / root の役割
2. 必須参照
  - project 固有 docs 索引
3. project 固有ルール
  - 実行コマンド、検証コマンド、言語固有制約、責務境界
4. 生成物運用
  - `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の編集規則
5. user-level assets 利用前提
  - user-level skill を前提にすること、install 済み資産の参照先

削除対象:

- 内部思考 / コメント / ログ言語方針のような共通原則
- ADR 参照の一般ルール
- 不要フォールバック禁止の一般原則
- `docs/rules/skill_catalog.md` への横断参照

設計判断:

- 削除範囲は root / Python / C# で統一する
- retained section の本文は project 固有情報だけ差し替える

## 5. コンポーネント責務と依存方向

### 5.1 user-agent-assets

- 責務
  - 共通 instructions の正本管理
  - workflow / orchestration skill の正本管理
  - workflow 手順書 `references/` の同梱
  - docs bootstrap 用 templates / references / wrapper 配布
- 依存
  - repo 内 docs を直接参照しない
  - skill 内で必要な資料は `references/` に閉じ込める

### 5.2 project-level instructions

- 責務
  - project 名、目的、主要ディレクトリ案内
  - ビルド / テスト / 静的解析コマンド
  - project 固有設計制約と docs 索引
- 依存
  - user-level 共通原則を再掲しない
  - 必要に応じて user-level assets の利用前提だけを短く案内する

### 5.3 sync scripts

- 責務
  - repo 内の生成物再生成に限定する
  - 対象は `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` のみ
- 非責務
  - user home 配下への install
  - workflow skill 本体の正本管理

### 5.4 install scripts

- 責務
  - `user-agent-assets/` 配下の正本を user-level 配置先へコピーする
  - `dry-run`、missing-only default、既存 file 保護、未作成 directory 作成を提供する
- 非責務
  - repo 内生成物の再生成
  - template 固有 docs の補完

依存方向は常に `project-level -> user-agent-assets` の参照案内のみ許可し、逆方向の依存を禁止する。

## 6. install / sync 設計

### 6.1 install 先方針

Copilot の install 先は、実行環境差を吸収するため単一優先ではなく複数 install を default とする。

- Copilot: `~/.copilot/skills/` と `~/.agents/skills/` の両方へ install
- Claude: `~/.claude/skills/`
- Codex: `~/.codex/skills/`

設計判断:

- `~/.copilot/skills` を first-class target とする
- `~/.agents/skills` は互換ミラーとして同時 install する
- install script は `--targets copilot,claude,codex` のような絞り込みを許可するが、default は利用可能 runtime 全部に配布する
- `--targets` は配布先 runtime の絞り込みだけを行い、選択した runtime には user-level skill 一式をまとめて配布する
- suite skill は他 workflow skill の同時 install を前提にするため、runtime ごとの部分 install は許可しても skill 単位の selective install は提供しない

### 6.2 install script の I/F

`install/install_user_agent_assets.sh` と `install/install_user_agent_assets.ps1` は同じ意味論を持つ。

- `--dry-run`: コピー・作成予定のみ表示
- `--mode missing|overwrite`: default は `missing`
- `--targets <list>`: `copilot`, `claude`, `codex`
- `--source-root <path>`: テスト用。default は repo 配下 `user-agent-assets/`

install script は file ごとに次の判定を行う。

1. 配置先 directory がなければ作成候補に追加する
2. 同名 file がなければコピーする
3. 同名 file がある場合、default は skip する
4. `overwrite` 指定時のみ上書きする

### 6.3 sync script の再定義

既存 `scripts/sync_agent_skills.*` と template 側 `scripts/sync_agent_skills.*` は Phase 4 で以下へ責務縮小する。

- `instructions/*.draft.md` から `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` を再生成する
- user home 配下には一切書き込まない

install と sync を 1 コマンドに統合しない。理由は、repo 内生成物更新と user 環境更新で failure domain が異なるためである。

### 6.4 shared helper 配布

review / orchestration skill が共有利用する helper は `user-agent-assets/bin/` と `user-agent-assets/runtime/` に置く。

- install 先
  - 共通 wrapper: `~/.agentic-project-templates/bin/`
  - 共通 runtime payload: `~/.agentic-project-templates/runtime/agent-cli-tmux/`
- macOS / Linux
  - `agentic-agent-cli-tmux.sh` が `~/.agentic-project-templates/runtime/agent-cli-tmux/python/agent_cli_tmux.py` を呼ぶ
- Windows
  - `agentic-agent-cli-tmux.ps1` は `~/.agentic-project-templates/runtime/agent-cli-tmux/win-x64/AgentCliTmux.exe` を優先し、未配置時は Python runtime へ fallback する

`SKILL.md` からは wrapper だけを呼び、`python` / `dotnet` を直接 allowlist 対象にしない。

設計判断:

- multi-skill で共有する helper は skill 個別 `bin/` ではなく shared `user-agent-assets/bin/` に寄せる
- skill 個別 `bin/` は `project-doc-bootstrap` のような単独 skill 専用 wrapper に限定する
- install script は PATH 追加を前提にせず、`$HOME/.agentic-project-templates/bin/...` を直接参照できる配置にする

### 6.5 shared reference hydrate

`workflow_phase_library/common` は root 正本の棚卸し結果から、phase library を使う全 skill の共通依存であると確定した。そのため、user-level 正本では各 skill 配下へ重複保持せず、次を正本とする。

- shared 正本: `user-agent-assets/shared/references/procedure/workflow_phase_library/common/*.md`

`review_checkpoints.md` は `ai-review-response-workflow` からのみ参照するため、shared 配布対象にはせず、最初から `ai-review-response-workflow/references/procedure/` に同梱する。

install script と repo 内 sync script は、phase library を必要とする skill をコピーした直後に shared common 6 ファイルを各 skill の `references/procedure/workflow_phase_library/common/` へ hydrate する。`review_checkpoints.md` は common と同様の shared hydrate 対象には含めない。

設計判断:

- source 正本では common を 1 箇所だけに置く
- hydrate 対象は、`workflow_phase_library/<type>/` を参照する skill に限定する
- `research-analysis-workflow` と `ai-review-response-workflow` には common を配布しない
- `review_checkpoints.md` は `ai-review-response-workflow` の reference に最初から同梱する
- `workflow_selection.md` は user-level skill の初期移行対象から外す。将来必要なら standalone skill として別定義する

## 7. workflow skill reference migration 設計

### 7.1 棚卸し範囲と設計原則

2026-05-09 に、root 正本の次を棚卸しした。

- `instructions/skills/**/SKILL.master.md`
- `docs/procedure/*.md`
- `docs/procedure/workflow_phase_library/**`

この棚卸し結果に基づき、user-level skill の `references/` は次の原則で再構築する。

1. 各 skill へコピーする起点文書は、root 正本の `SKILL.master.md` で参照される `docs/procedure` 配下のファイルを基準にする
2. ただし `workflow_selection.md` は、skill が読み込まれた時点で役割を終えているため user-level skill ごとの `references/` には移さない
3. `review_checkpoints.md` は各 workflow skill から直接読ませず、`ai_review_response_workflow.md` からのみ参照する `ai-review-response-workflow` 専用文書として正規化する
4. 起点となる workflow 本体文書が `workflow_phase_library` を参照している場合は、その下流依存を追加でコピーする
5. `docs/procedure/README.md` のような索引文書や、直接・間接に参照されない別 workflow 文書はコピーしない
6. `workflow_phase_library/common` だけは shared 正本に寄せ、install / sync 時に必要 skill へ hydrate する

補足:

- `workflow_selection.md` は original skill では直接参照されているが、skill 選択済みの user-level 実行時には不要なので移行対象から外す
- `review_checkpoints.md` は original skill では複数 skill から直接参照されているが、用途上は review response の補助文書なので `ai-review-response-workflow` 配下へ寄せる

### 7.2 skill 別 dependency map

| skill | user-level で保持する起点文書 | 追加で必要な下流依存 | user-level `references/` へ置くもの |
|---|---|---|---|
| `spec-change-workflow` | `spec_change_workflow.md` | `workflow_phase_library/spec_change/*`、shared common 6 files | 起点文書 1 件 + `workflow_phase_library/spec_change/` + hydrate された common |
| `new-feature-workflow` | `new_feature_workflow.md` | `workflow_phase_library/new_feature/*`、shared common 6 files | 起点文書 1 件 + `workflow_phase_library/new_feature/` + hydrate された common |
| `bugfix-workflow` | `bugfix_workflow.md` | `workflow_phase_library/bugfix/*`、shared common 6 files | 起点文書 1 件 + `workflow_phase_library/bugfix/` + hydrate された common |
| `issue-resolution-workflow` | `issue_resolution_workflow.md` | `workflow_phase_library/issue_resolution/*`、shared common 6 files | 起点文書 1 件 + `workflow_phase_library/issue_resolution/` + hydrate された common |
| `refactoring-workflow` | `refactoring_workflow.md` | `workflow_phase_library/refactoring/*`、shared common 6 files | 起点文書 1 件 + `workflow_phase_library/refactoring/` + hydrate された common |
| `research-analysis-workflow` | `research_analysis_workflow.md` | なし | 起点文書 1 件のみ |
| `ai-review-response-workflow` | `ai_review_response_workflow.md` | `review_checkpoints.md` | 起点文書 1 件 + `review_checkpoints.md` |
| `copilot-review-automation` | なし（`SKILL.md` から 6 skill 名を索引） | 同時 install された workflow / review skill | `references/` 追加なし |
| `claude-review-automation` | `autonomous_workflow_orchestrator.md` | 同時 install された workflow / review skill | 起点文書 1 件のみ |
| `autonomous-workflow-orchestrator` | `autonomous_workflow_orchestrator.md` | 同時 install された workflow / review skill | 起点文書 1 件のみ |
| `copilot-cli-workflow-orchestrator` | `autonomous_workflow_orchestrator_copilot_cli.md` | 同時 install された workflow / review skill | 起点文書 1 件のみ |

### 7.3 shared common の対象と hydrate 条件

shared 正本に置くのは次の 6 ファイルだけとする。

- `phase_1_branch_and_meta.md`
- `phase_2_plan_review.md`
- `phase_3_design_review.md`
- `phase_4_impl_review.md`
- `phase_5_verification_and_docs.md`
- `phase_6_completion.md`

これらは root 正本の `docs/procedure/workflow_phase_library/common/` から移す。

hydrate 対象 skill:

- `spec-change-workflow`
- `new-feature-workflow`
- `bugfix-workflow`
- `issue-resolution-workflow`
- `refactoring-workflow`

hydrate 不要 skill:

- `research-analysis-workflow`
- `ai-review-response-workflow`
- `copilot-review-automation`
- `claude-review-automation`
- `autonomous-workflow-orchestrator`
- `copilot-cli-workflow-orchestrator`
- `project-doc-bootstrap`

`review_checkpoints.md` は shared 正本へは置かず、`ai-review-response-workflow/references/procedure/review_checkpoints.md` に同梱する。

### 7.4 移行ルール

- 各 skill の reference payload は、root 正本 `SKILL.master.md` を出発点にするが、`workflow_selection.md` 除外と `review_checkpoints.md` の `ai-review-response-workflow` への集約を明示例外として適用する
- review automation / orchestrator 群は「複数 workflow を束ねる suite」とみなすが、procedure を重複コピーせず、同時 install 済みの他 skill を `SKILL.md` から skill 名で索引する
- core workflow skill と `research-analysis-workflow` には `workflow_selection.md` と `review_checkpoints.md` を持たせない
- `review_checkpoints.md` は `ai-review-response-workflow` にのみ同梱し、その skill 内から参照する
- `workflow_selection.md` は user-level skill の `references/` へ移さない。必要になった場合だけ standalone skill として再定義する
- `workflow_phase_library/README.md` は root 正本で直接参照される `copilot-review-automation` にだけ置く
- shared common 以外の `workflow_phase_library` は core workflow skill ごとに個別配置し、suite skill へは install 時にも追加コピーしない
- `docs/procedure/README.md` や未参照の別 workflow 文書は user-level skill の `references/` に持ち込まない

### 7.5 `SKILL.master.md` からの移行

- user-level 正本は placeholder を持たない `SKILL.md` に統一する
- reference payload の選定根拠は template 側ではなく root 正本 `instructions/skills/` を優先する
- project-level 生成用途が残る skill だけ、移行期間中は `SKILL.master.md` を温存してもよい
- 移行完了後に template 側 `SKILL.master.md` を削除する対象は、Phase 4 実装で一覧化する

## 8. docs bootstrap skill 設計

### 8.1 skill 構成

`project-doc-bootstrap` skill は docs 雛形のコピー元と補完手順の両方を持つ。

```text
project-doc-bootstrap/
├── SKILL.md
├── templates/
│   ├── common/
│   ├── python/
│   │   └── docs/
│   └── csharp/
│       └── docs/
├── references/
│   ├── python-target-docs.md
│   └── csharp-target-docs.md
└── bin/
    ├── copy_doc_templates.sh
    └── copy_doc_templates.ps1
```

### 8.2 wrapper 方針

- macOS / Linux: `.sh`
- Windows: `.ps1`
- 追加で quoting 問題が解消しない場合のみ `.cmd` または publish 済み executable を追加する

設計判断:

- docs bootstrap の補助処理は Python に依存させない
- まず shell / PowerShell wrapper で必要十分な機能を提供する
- wrapper は docs コピー、dry-run、placeholder 列挙に責務を限定する

### 8.3 docs コピー契約

- default は missing-only
- `templates/common` を先にコピーし、その後 `templates/python|csharp` を追加適用する
- コピー後に placeholder / TODO 残存一覧を出力する
- `templates/common` は shared docs を抽出できた時だけ使い、Phase 4 時点では空ディレクトリのままでもよい
- 既存 docs を上書きするのは明示 `overwrite` 時のみ

## 9. project-level fallback 設計

### 9.1 fallback を持たない方針

workspace fallback は持たず、Copilot でも user-level skill を正本とする。

設計判断:

- 対象 skill の利用者が限定されているため、workspace fallback を維持するより実運用で user-level skill を直接検証して都度修正する方が単純である
- `.github/skills/`、`.claude/skills/`、`.agents/skills/` への暫定 skill 再生成は行わない
- user-level skill の smoke test と `references/` の self-contained 動作確認を優先し、問題があれば user-level 正本を修正する

### 9.2 検証と不具合時の扱い

Copilot user-level skill の smoke test は Phase 5 までに実施する。

1. `~/.copilot/skills` または `~/.agents/skills` の最小 skill 検出を確認する
2. workflow skill が `references/` だけで動作し、project-level `docs/procedure/` 非依存であることを確認する

不具合が見つかった場合は、workspace fallback を足すのではなく user-level 正本を修正して再検証する。

## 10. `skill_catalog.md` 削除 ripple 設計

`docs/rules/skill_catalog.md` の削除に伴い、少なくとも次を同一変更系列で更新する。

- root `CLAUDE.md`
- root `AGENTS.md`
- root `.github/copilot-instructions.md`
- root `instructions/agent_common_master.md`
- `python-project-template/instructions/agent_common_master.md`
- `csharp-project-template/instructions/agent_common_master.md`
- 各 template の `instructions/skills/*/SKILL.master.md` の skill catalog 参照

設計判断:

- `skill_catalog.md` を user-level 側の薄い索引として残さない
- user-level skill 名は `user-agent-assets/skills/` の実体名を唯一の正とする
- project-level index は必要な workflow だけ明示し、catalog への横断参照をやめる

## 11. 実装単位と変更順序

### 11.1 実装単位

1. `user-agent-assets/` 正本追加
2. install script 追加
3. workflow skill の `references/` 化
4. `project-doc-bootstrap` 追加
5. root / template sync source 薄化
6. `skill_catalog.md` 参照除去と削除
7. user-level smoke test と移行後クリーンアップ

### 11.2 順序制約

- `references/` 化完了前に `docs/procedure/` を削除しない
- install script の dry-run 実装前に template から workflow skill を外さない
- root 側の sync source 薄化前に template 側の参照除去を始めない
- 旧 instructions/skills や `docs/procedure/` の削除は smoke test と self-contained 動作確認後にしか行わない

## 12. 影響ファイルと新規関数配置方針

### 12.1 新規ファイル群

- `user-agent-assets/**`
- 必要に応じて `scripts/` 配下の補助 generator / sync 更新

### 12.2 既存更新対象

- root `instructions/agent_common_master.md`
- root `instructions/*.draft.md`
- root `scripts/sync_agent_skills.*`
- `python-project-template/instructions/**`
- `python-project-template/scripts/sync_agent_skills.*`
- `csharp-project-template/instructions/**`
- `csharp-project-template/scripts/sync_agent_skills.*`
- root / template `docs/procedure/**`
- root / template `docs/rules/skill_catalog.md`

### 12.3 配置原則

- install 処理は `user-agent-assets/install/` に閉じ、project-level sync へ混ぜない
- docs bootstrap の wrapper は `project-doc-bootstrap/bin/` に置き、汎用的な root helper へ逃がさない
- install/sync の責務から外れる暫定 workspace skill 生成は追加しない

## 13. テスト設計

### 13.1 Phase 4/5 で必須の検証

1. `install_user_agent_assets.sh --dry-run`
2. `install_user_agent_assets.ps1 -DryRun`
3. root `scripts/sync_agent_skills.sh --help`
4. Python template の既存 py_compile / pytest
5. C# template の既存 `dotnet build` / test
6. Copilot user-level skill smoke test
7. workflow skill の `references/` 参照 smoke test
8. docs bootstrap missing-only / overwrite / placeholder listing 確認

### 13.2 実装時の完了判断

- project-level `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` が薄い index として再生成できる
- workflow skill は project-level `docs/procedure/` がなくても自己完結する
- install script は既存 user-level skill を破壊しない
- workspace fallback を追加せず、user-level skill の smoke test と self-contained 動作確認が完了している

## 14. 設計上の受け入れ条件

1. user-level 正本ディレクトリ、install script、workflow skill `references/` の構造が明示されている。
2. project-level instructions と sync source の責務縮小方針が明示されている。
3. docs bootstrap skill の templates / references / wrapper 構造が明示されている。
4. shared common と `ai-review-response-workflow` 専用 reference の配置方針、および user-level skill の検証方針が定義されている。
5. `skill_catalog.md` 削除 ripple の具体対象が列挙されている。

## 15. 実装へ渡す判断メモ

- user-level install は `~/.copilot/skills` と `~/.agents/skills` の両方を default 対象にする
- docs bootstrap 補助処理は shell / PowerShell wrapper で開始し、Python 前提を導入しない
- workspace fallback は持たず、user-level 正本の修正と再検証で問題を解決する
- `skill_catalog.md` は削除方向で確定し、参照元更新を同一系列で行う