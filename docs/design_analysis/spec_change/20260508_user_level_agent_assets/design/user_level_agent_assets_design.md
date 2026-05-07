# ユーザレベル Agent 資産化（SC-20260508-001）設計書

## レビュー反映履歴

| 日時 | 対応内容 |
|------|---------|
| 2026-05-08 | 初版作成（Phase 3 pre-review） |

---

## 1. 目的

Python / C# テンプレートと root に重複している workflow skills、Agent instructions、`docs/procedure/` 系資産を、user-level Agent assets を正本とする構成へ移行する。

本設計では、次を実装可能な粒度で確定する。

- user-level 正本ディレクトリの配置と中身
- project-level の薄い index / 固有ルールとの責務分離
- install script と sync script の責務分担
- workflow skill の self-contained 化と `references/` 参照方式
- docs bootstrap skill の構造と OS 別 wrapper 方針
- Copilot smoke test 不合格時の project-level fallback 条件

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
5. Copilot smoke test 不合格時の project-level fallback 範囲

## 3. before / after 仕様差分

| 観点 | Before | After |
|---|---|---|
| workflow skill 正本 | root / Python / C# template に重複配置された `instructions/skills/*/SKILL.master.md` | `user-agent-assets/skills/*/SKILL.md` を正本とし、install script で user-level へ配布 |
| workflow 手順参照 | skill 本文から project-level `docs/procedure/*` を前提参照 | 各 skill の `references/procedure/` を参照する self-contained 構成 |
| Agent instructions | `agent_common_master.md` に共通原則と project 固有ルールが混在 | 共通原則は user-level、project-level は index / コマンド / 固有制約へ分離 |
| docs 雛形 | template ごとに docs 雛形や doc filler が分散 | `project-doc-bootstrap` skill の `templates/` と `references/` へ集約 |
| sync script | project-level 生成物と skill 同期を一体で扱う | install script は user-level 配布、sync script は repo 内生成物更新に限定 |
| Copilot fallback | 明確な fallback 設計なし | smoke test 不合格時のみ `.github/skills/` に限定的 fallback を残す |

本件は UI 変更を伴わない。変更対象は配布構成、Agent の参照導線、テンプレートの docs / instructions 契約である。

## 4. ターゲット構成

### 4.1 新しい正本ディレクトリ

root 直下に user-level 正本を配置する。

```text
user-agent-assets/
├── instructions/
│   ├── common_agent_principles.md
│   ├── workflow_selection.md
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
│   ├── ai-review-response-workflow/
│   ├── copilot-review-automation/
│   ├── claude-review-automation/
│   └── project-doc-bootstrap/
│       ├── SKILL.md
│       ├── templates/
│       │   ├── common/
│       │   ├── python/
│       │   └── csharp/
│       ├── references/
│       └── bin/
└── install/
    ├── install_user_agent_assets.sh
    ├── install_user_agent_assets.ps1
    └── README.md
```

設計判断:

- user-level 正本は `instructions/` と `skills/` を同じトップレベルに置き、repo 内で version 管理する
- 実行時に使う skill は placeholder を持たない `SKILL.md` を正本とする
- 既存 `SKILL.master.md` は Phase 4 で user-level 正本へ移した後、project-level 生成用途が残る場合だけ限定維持する

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
  - 対象は `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`、必要な project-level skill fallback のみ
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
- fallback 運用中に限り `.github/skills/` / `.claude/skills/` / `.agents/skills/` の薄い project-level skill を再生成する
- user home 配下には一切書き込まない

install と sync を 1 コマンドに統合しない。理由は、repo 内生成物更新と user 環境更新で failure domain が異なるためである。

## 7. workflow skill self-contained 設計

### 7.1 references 同梱ルール

各 workflow skill は次の最小構成を持つ。

```text
<skill>/
├── SKILL.md
├── references/
│   ├── procedure/
│   │   ├── <workflow>.md
│   │   ├── workflow_selection.md
│   │   ├── review_checkpoints.md
│   │   └── workflow_phase_library/
│   └── rules/
│       └── 共通参照が必要な場合のみ
└── bin/
    └── runtime 補助 wrapper が必要な場合のみ
```

設計判断:

- `docs/procedure/` は skill 実行に必要な分だけ `references/procedure/` へ複製する
- `SKILL.md` から project-level `docs/procedure/` を直接読ませない
- workflow 間で共通の references は、install script 側で duplicate を許容する。Phase 4 では構造単純化を優先する

### 7.2 `SKILL.master.md` からの移行

- user-level 正本は placeholder を持たない `SKILL.md` に統一する
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
│   └── csharp/
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
- 既存 docs を上書きするのは明示 `overwrite` 時のみ

## 9. project-level fallback 設計

### 9.1 fallback を残す条件

Copilot smoke test が完了するまでは、workspace fallback を最小限で維持できる設計を残す。

- fallback 配置先: `.github/skills/`
- fallback 対象: workflow / orchestration のうち Copilot 実行で実害が出るものだけ
  - `spec-change-workflow`
  - `new-feature-workflow`
  - `bugfix-workflow`
  - `issue-resolution-workflow`
  - `refactoring-workflow`
  - `copilot-review-automation`

設計判断:

- `research-analysis-workflow`、`ai-review-response-workflow`、`claude-review-automation` は user-level install 後運用へ寄せ、Phase 4 初期段階では fallback 必須対象に含めない
- `.claude/skills/` と `.agents/skills/` の workspace fallback は新規増設しない
- fallback は team-shared workspace 互換経路としてのみ扱う

### 9.2 fallback の削除条件

次の 2 条件が揃ったら `.github/skills/` fallback を削除対象にする。

1. `~/.copilot/skills` または `~/.agents/skills` の smoke test が合格している
2. workflow skill が `references/` だけで動作し、project-level `docs/procedure/` 非依存を確認できている

削除タイミングは Phase 5 の検証完了後とし、Phase 4 実装中は削除ではなく「生成対象縮小」で段階移行する。

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
7. `.github/skills/` fallback 縮小

### 11.2 順序制約

- `references/` 化完了前に `docs/procedure/` を削除しない
- install script の dry-run 実装前に template から workflow skill を外さない
- root 側の sync source 薄化前に template 側の参照除去を始めない
- fallback 削除は smoke test 後にしか行わない

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
- fallback 判定ロジックが必要でも、`scripts/` 直下の汎用 executor を増やさず、install/sync の責務内へ閉じる

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
- `.github/skills/` fallback は設計した限定範囲に縮小されている

## 14. 設計上の受け入れ条件

1. user-level 正本ディレクトリ、install script、workflow skill `references/` の構造が明示されている。
2. project-level instructions と sync source の責務縮小方針が明示されている。
3. docs bootstrap skill の templates / references / wrapper 構造が明示されている。
4. Copilot fallback 条件と削除条件が定義されている。
5. `skill_catalog.md` 削除 ripple の具体対象が列挙されている。

## 15. 実装へ渡す判断メモ

- user-level install は `~/.copilot/skills` と `~/.agents/skills` の両方を default 対象にする
- docs bootstrap 補助処理は shell / PowerShell wrapper で開始し、Python 前提を導入しない
- fallback は `.github/skills/` の限定運用だけに留め、恒久運用にしない
- `skill_catalog.md` は削除方向で確定し、参照元更新を同一系列で行う