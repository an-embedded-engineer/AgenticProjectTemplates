# Phase 2 計画 - ユーザレベル Agent 資産化

## 1. 背景

`SC-20260508-001` は、root / Python / C# テンプレートへ重複配置されている Agent instructions、workflow skills、`docs/procedure/` 系の運用文書を見直し、共通部分の正本を user-level Agent assets へ寄せる仕様変更である。

2026-05-07 の調査と 2026-05-08 のレビューで、次が確認された。

- workflow / orchestration skills は project 固有知識ではなく、共通の作業手順である
- `instructions/agent_common_master.md` には共通原則と project 固有ルールが混在している
- `docs/procedure/` と `docs/rules/skill_catalog.md` は project 固有 docs ではなく、Agent 運用基盤としての性格が強い
- Python / C# 間には `agent_cli_tmux.py` と `AgentCliTmux`、検証コマンド、docs 雛形に言語差があり、共通化と project-level 残置の切り分けが必要である

この変更は新機能追加ではなく、テンプレートの配布構造、同期元、workflow skill 参照経路を変更するため `spec-change` で進める。

## 2. 目的

1. workflow / orchestration skills の正本を user-level Agent assets へ移し、テンプレートごとの重複コピーを減らす。
2. 共通 Agent instructions を user-level 側へ寄せつつ、project-level には固有ルール、検証コマンド、成果物置き場の索引だけを残す。
3. docs 雛形は user-level skill から bootstrap 可能にし、対象 project には実体化済み docs だけを残す。
4. `docs/procedure/` の project-level 依存を外し、workflow skill が self-contained に動ける構成へ変更する。

## 3. 対象

### 3.1 正本構成

- root の `instructions/skills/`
- root の `instructions/agent_common_master.md` と `instructions/*.draft.md`
- root の `docs/procedure/`
- root の `docs/rules/skill_catalog.md`
- root の `scripts/sync_agent_skills.*`

### 3.2 テンプレート構成

- `python-project-template/instructions/`
- `python-project-template/docs/`
- `python-project-template/scripts/sync_agent_skills.*`
- `csharp-project-template/instructions/`
- `csharp-project-template/docs/`
- `csharp-project-template/scripts/sync_agent_skills.*`

### 3.3 新規追加候補

- user-level asset 正本ディレクトリ
- install script と README
- workflow skill 同梱 `references/`
- docs bootstrap skill と docs template 配布導線
- `agent_cli_tmux` / `AgentCliTmux` 用 OS 別 wrapper または publish 済み executable 配布導線

## 4. 非対象

- Copilot / Claude / Codex 以外の Agent runtime への対応
- user-level install 後の個人設定ファイルの強制上書き
- この Phase での大規模ファイル移動や template 削除
- 調査で未解決だった smoke test の結果確定前に、project-level skill を一括削除すること

## 5. 現行仕様からの変更差分

### 5.1 instructions

- 現行: 共通原則と project 固有ルールが `agent_common_master.md` 系に混在する
- 変更後: 共通原則は user-level instructions へ、project-level は薄い index と固有ルールへ分離する

### 5.2 skills

- 現行: workflow skills が root / Python / C# テンプレートへ重複配置され、`SKILL.master.md` から生成される
- 変更後: user-level 正本 `SKILL.md` を中心にし、project-level には共有が必要なものだけを残す

### 5.3 docs

- 現行: `docs/procedure/` と docs 雛形が template ごとに同梱される
- 変更後: workflow 手順書は skill 同梱 `references/` に移し、docs 雛形は bootstrap skill の `templates/` から project へ実体コピーする

### 5.4 sync / install

- 現行: `scripts/sync_agent_skills.*` が project-level 生成物中心で動く
- 変更後: user-level install と project-level 生成物の責務を分離し、同期対象を最小化する

## 6. 受け入れ条件ごとの対応方針

| 受け入れ条件 | 計画上の対応方針 |
|---|---|
| Copilot user-level skill smoke test | 最小 skill を `~/.copilot/skills` または `~/.agents/skills` に配置し、Copilot Chat / Copilot CLI で検出確認する手順を Phase 5 へ入れる |
| workflow skill の `docs/procedure/` 非依存化 | skill ごとに `references/procedure/` を持つ self-contained 構成を Phase 3 で定義する |
| install script の安全要件 | `dry-run`、missing-only default、既存 skill 保護、未作成ディレクトリ作成を install 設計に含める |
| `SKILL.master.md` 由来の一般 skill 化 | placeholder を除去した user-level `SKILL.md` 生成方針を固定する |
| `skill_catalog.md` 削除方向整理 | 参照元更新を含めた ripple を Phase 3 / 4 の設計対象に含める |
| wrapper / executable allowlist 化 | Python / dotnet 直許可ではなく、用途別 wrapper / executable 配布を設計対象に含める |
| project-level instructions の薄化 | sync source 側で project 固有情報だけを残す方針を設計で確定する |

## 7. 変更ワークストリーム

### 7.1 User-Level Asset 正本化

- user-level asset 用の正本ディレクトリを新設する
- workflow / orchestration skill を project 非依存の `SKILL.md` へ変換する
- install 先として `~/.copilot/skills`、`~/.claude/skills`、`~/.agents/skills`、`~/.codex/skills` を扱う

### 7.2 Workflow Skill Self-Contained 化

- `docs/procedure/` 参照を skill 同梱 `references/` へ移す
- review checkpoints、workflow selection、phase library の参照経路を user-level skill 内へ閉じる
- 対象 project に必要な最小 docs ディレクトリがなければ bootstrap skill を案内する

### 7.3 Docs Bootstrap 導線

- Python / C# の doc filler を統合または共通化する
- `templates/common` と `templates/python|csharp` の分割を設計する
- 既存 docs を上書きしない default 挙動と placeholder 検出を定義する

### 7.4 Project-Level 縮小

- `instructions/agent_common_master.md` と `instructions/*.draft.md` を薄い index と固有ルール中心へ整理する
- template 同梱 workflow skills と `docs/procedure/` を段階的に削減する
- `docs/rules/skill_catalog.md` の参照元を更新し、削除方向で整理する
	- ripple 対象には `root/CLAUDE.md`、`root/AGENTS.md`、`.github/copilot-instructions.md`、各 template の `instructions/skills/*/SKILL.master.md` を含める

### 7.5 Sync / Wrapper 再設計

- user-level install script と project-level sync script の責務を分ける
- `agent_cli_tmux` / `AgentCliTmux` を呼ぶ OS 別 wrapper または publish 済み executable の配置方針を定める
	- macOS / Linux は `.sh`、Windows は `.ps1` を優先し、必要に応じて `.cmd` または publish 済み executable を併用する
- allowlist は wrapper / executable 単位で設計する

## 8. リスクと段階的移行方針

### 8.1 user-level 依存による再現性低下

- リスク: clone だけでは workflow skill が揃わない
- 対策: repo に user-level 正本と install script を残し、project-level index から前提を明記する

### 8.2 instructions の優先順位衝突

- リスク: user-level と project-level の指示が競合する
- 対策: user-level は原則と workflow に限定し、project-level に具体コマンドと例外ルールを集約する

### 8.3 Copilot user-level skill 検出の環境差

- リスク: `~/.copilot/skills` または `~/.agents/skills` の検出結果が実環境に依存する
- 対策: Phase 5 の smoke test で最小 skill を使って検証し、不合格時は `.github/skills/` を project-level fallback として維持する範囲と削除条件を Phase 3 で設計確定する

### 8.4 `docs/procedure/` の早期除去による workflow 破綻

- リスク: self-contained 化前に template から外すと skill が参照不能になる
- 対策: `references/` 化と smoke test 完了までは削除ではなく移行順序を固定する

### 8.5 言語差の吸収不足

- リスク: Python / C# の検証コマンドや helper 差分を共通 skill に混ぜ込みすぎる
- 対策: project-level rules に残すものと user-level wrapper で吸収するものを Phase 3 で明示分離する

## 9. 実装順序の方針

1. user-level 正本ディレクトリ、install script、skill `references/` 構成を設計確定する
2. docs bootstrap skill と template 配布方式を設計確定する
3. sync source と project-level 生成物の縮小方針を確定する
4. root で最小実装を行い、続いて Python / C# テンプレートへ横展開する
5. smoke test と template 検証を行ったうえで、不要な project-level 同梱物を削減する

段階移行は採るが、恒久的な二重正本は残さない。移行期間中の project-level 同梱は smoke test と周辺更新のための暫定措置として扱う。

## 10. テスト方針

### 10.1 実装時の必須検証

- root `scripts/agent_cli_tmux.py` の `python3 -m py_compile`
- root `scripts/sync_agent_skills.sh --help`
- Python テンプレートの `python3 -m py_compile` と対象 pytest
- C# テンプレートの対象 `dotnet build` / test
- user-level install script の `dry-run`
- workflow skill が `references/` だけで起動できることの smoke test

### 10.2 本件固有の確認

1. Copilot Chat / Copilot CLI が user-level 最小 skill を検出できる
2. Claude / Codex への install で未作成ディレクトリが安全に作成される
3. docs bootstrap が既存 docs を上書きせず、未補完 placeholder を列挙できる
4. Python / C# テンプレートの project-level instructions が固有ルール中心へ縮小される
5. `skill_catalog.md` 参照削除後も sync 生成物の索引が破綻しない

## 11. ユーザ確認シナリオ

Phase 5 では少なくとも以下をユーザ確認対象とする。

1. user-level install 実行後、新規 project で workflow skill を project-level 同梱なしに呼び出せる
2. docs bootstrap skill で必要 docs がコピーされ、placeholder が一覧化される
3. project-level `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` が薄い index として成立する
4. Python / C# テンプレートの基本検証が通る

## 12. 影響コンポーネント別の変更範囲

- `instructions/`: sync source の再編、project-level index 化
- `instructions/skills/`: user-level 正本化、`references/` 同梱化
- `docs/procedure/`: user-level skill 側への移管
- `docs/rules/skill_catalog.md`: `root/CLAUDE.md`、`root/AGENTS.md`、`.github/copilot-instructions.md`、各 template の `instructions/skills/*/SKILL.master.md` の参照更新を伴う削除方向整理
- `scripts/`: sync / install / wrapper の責務再設計
- `python-project-template/`, `csharp-project-template/`: project-level instructions と docs の薄化、検証導線更新

## 13. 設計 Phase へ持ち込む未解決事項

1. Copilot では `~/.copilot/skills` と `~/.agents/skills` のどちらを正規 install 先として優先するか
2. install script と sync script の機能分割をどこまで root / template 共通化するか
3. docs bootstrap skill の補助スクリプトを shell / PowerShell / publish 済み executable のどれで提供するか
4. project-level fallback をどの期間まで残すか
5. Copilot smoke test が不合格だった場合、`.github/skills/` に残す workflow skills の範囲と解消条件をどう定義するか

## 14. 受け入れ条件

1. workflow / orchestration skills の正本と install 導線が user-level 前提で設計されている。
2. workflow skill が `docs/procedure/` を project-level に要求せず、skill 同梱 `references/` から必要手順を参照できる。
3. project-level instructions は共通原則の再掲ではなく、固有ルールと成果物索引へ縮小される。
4. `skill_catalog.md` 削除方向に伴う参照更新、wrapper allowlist、Copilot smoke test を含む検証計画が定義されている。
5. user-level install script は `dry-run`、`missing-only default`、既存 user skill 保護、未作成 skill directory 作成を満たす。

補足: 詳細な受け入れ条件の対応表は Section 6 と `docs/todo/todo.md` の `SC-20260508-001` を正とする。