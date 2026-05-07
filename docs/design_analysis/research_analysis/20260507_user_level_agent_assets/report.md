# ユーザレベル Agent 資産化の妥当性調査

## 調査目的

Python / C# プロジェクトテンプレートに同梱している `instructions`、`skills`、`docs` 基盤を、ユーザレベルの Agent 資産として定義する案について、妥当性と実現方法を整理する。

結論として、案は概ね妥当である。ただし、すべてをユーザレベルへ移すのではなく、共通 workflow / orchestration / docs 雛形の正本をユーザレベル skill に寄せ、プロジェクトには薄い索引、プロジェクト固有ルール、実体化済み docs だけを残す構成がよい。

## 調査対象

- Root 側 Agent 運用文書
  - `instructions/agent_common_master.md`
  - `instructions/agent_sync_guide.md`
  - `instructions/skills/`
  - `docs/procedure/`
  - `docs/rules/`
  - `docs/architecture/`
- Python / C# テンプレート側 Agent 運用文書
  - `python-project-template/instructions/`
  - `csharp-project-template/instructions/`
  - `python-project-template/docs/`
  - `csharp-project-template/docs/`
  - `python-project-template/scripts/sync_agent_skills.*`
  - `csharp-project-template/scripts/sync_agent_skills.*`
- テンプレート適用後の docs 補完 skill
  - `python-project-template/instructions/skills/python-template-doc-filler/`
  - `csharp-project-template/instructions/skills/csharp-template-doc-filler/`
- 外部仕様確認
  - Claude Code skills / memory docs
  - GitHub Copilot repository custom instructions docs
  - OpenAI Codex `AGENTS.md` 記述

## 根拠ソース

### リポジトリ内

- `docs/rules/project_overview.md`
- `docs/architecture/overview.md`
- `docs/architecture/code_patterns.md`
- `docs/architecture/common_pitfalls.md`
- `docs/rules/skill_catalog.md`
- `instructions/README.md`
- `instructions/agent_sync_guide.md`
- `python-project-template/instructions/agent_common_master.md`
- `csharp-project-template/instructions/agent_common_master.md`
- `python-project-template/instructions/skills/python-template-doc-filler/SKILL.md`
- `csharp-project-template/instructions/skills/csharp-template-doc-filler/SKILL.md`

### ローカル環境

- `~/.codex/skills/` に workflow skills が配置済みであること
- `~/.claude/settings.json` が存在すること
- `~/.copilot/settings.json` が存在すること

### 外部ドキュメント

- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Claude Code memory: <https://code.claude.com/docs/en/memory>
- GitHub Copilot repository custom instructions: <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions>
- OpenAI Codex / `AGENTS.md`: <https://openai.com/index/introducing-codex/>

## 現状整理

### 1. 現行テンプレートは共通資産をテンプレートごとに持っている

`docs/rules/project_overview.md` は、このリポジトリを「Python / C# の各テンプレートに Agent instructions、workflow skills、設計・レビュー文書運用、検証用ツールを同梱する」ものとして定義している。

その結果、次の資産が root、Python テンプレート、C# テンプレートの複数箇所に存在している。

- workflow 手順書: `docs/procedure/`
- workflow skills: `instructions/skills/*-workflow/`
- Agent 同期スクリプト: `scripts/sync_agent_skills.*`
- Agent 共通 instructions: `instructions/agent_common_master.md`
- `.github/skills` / `.claude/skills` への生成物

`diff -qr` で確認すると、Python / C# 間の `docs/procedure` には多数の差分があり、差分の多くは Python / C# の言語差やツール差である。例として、Python 側は `scripts/agent_cli_tmux.py`、C# 側は `tools/AgentCliTmux` を参照する。

### 2. instructions は共通原則とプロジェクト固有ルールが混在している

`python-project-template/instructions/agent_common_master.md` と `csharp-project-template/instructions/agent_common_master.md` には、次のような共通ルールが含まれている。

- 内部思考は英語、チャット応答は日本語
- コメントは日本語、ログ/UI/エラー文字列は英語
- 類似ロジックは重複実装より抽象化・共通化を優先する
- 不要な後方互換レイヤーやフォールバックを追加しない
- 関連 ADR を計画前・実装前・レビュー時に参照する

一方で、同じファイルには Python 固有の `pyright` 完了条件、C# 固有の `dotnet build --warnaserrors` 完了条件も含まれる。

したがって、ユーザレベルへ移すべきなのは共通原則であり、プロジェクトごとの実行コマンド、ビルドコマンド、静的解析コマンド、プロジェクト固有の責務境界は project-level instructions / docs に残すべきである。

### 3. skills はほぼ workflow / orchestration 系であり、ユーザレベル化に向いている

`docs/rules/skill_catalog.md` に列挙されている主要 skill は、仕様変更、新機能、不具合修正、課題解決、リファクタリング、調査分析、レビュー反映、Agent orchestration である。

これらはプロジェクト固有のドメイン知識というより、Agent 作業の進め方そのものである。Claude Code 公式 docs でも、個人 skill は `~/.claude/skills/<skill-name>/SKILL.md` に置けるとされ、skill は必要時だけ本文がロードされる。ローカルにも `~/.codex/skills/` に同種の workflow skills が配置済みである。

したがって、workflow / orchestration skills はユーザレベルを正本にする方が、テンプレートごとのコピーより保守しやすい。

ただし、現行 skill は `docs/procedure/...` を対象プロジェクト内に存在する前提で参照している。ユーザレベル skill 化するなら、workflow 手順書を skill の `references/` に同梱するか、参照先を「対象プロジェクト docs」から「skill バンドル内の参照文書」へ変更する必要がある。

### 4. docs テンプレートはプロジェクトへ実体化する必要がある

`docs/architecture/overview.md` と `docs/architecture/common_pitfalls.md` は、root infra とテンプレート docs の混同を落とし穴として明記している。プロジェクト適用後の docs は、対象プロジェクトの設計、テスト、ADR、追跡項目、履歴を置く場所であり、最終的にはリポジトリに実体として存在する必要がある。

一方で、`docs/procedure/` の workflow 手順書や `docs/rules/skill_catalog.md` は、個々の対象プロジェクトの固有設計というより Agent 運用基盤である。これらは user-level skill の参照資料へ移してもよい。

docs については次の分離が妥当である。

| 種別 | 推奨配置 | 理由 |
|---|---|---|
| workflow 手順書 / review checkpoints | ユーザレベル skill の `references/` | Agent の作業手順であり、全プロジェクト共通 |
| docs 雛形 | ユーザレベル skill の `templates/` | コピー元を一元管理できる |
| 実体化済み project docs | 対象プロジェクトの `docs/` | プロジェクト固有の設計・履歴・追跡情報 |
| project-specific rules | 対象プロジェクトの `docs/rules/` | ビルド、テスト、命名、責務境界はプロジェクト依存 |

## 案の妥当性評価

### instructions

妥当。ただし、ユーザレベルとプロジェクトレベルを明確に分ける必要がある。

ユーザレベルに置くべきもの:

- Agent との協働方針
- 共通の設計原則
- コメント / ログ / UI 言語方針
- workflow skill の選択規則
- ADR / design_analysis を使う一般ルール
- 不要な後方互換やフォールバックを避ける方針

プロジェクトレベルに残すべきもの:

- プロジェクト名、目的、主要ディレクトリ
- 実行 / ビルド / テスト / 静的解析コマンド
- 言語・フレームワーク固有ルール
- プロジェクト固有の責務境界、命名、設計制約
- そのプロジェクトでだけ有効な ADR / docs 索引

実装上は、テンプレート内 `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` を厚く生成するのではなく、薄い project index にするのがよい。

### skills

妥当。むしろ最も移行効果が大きい。

理由:

- 現行 skill は workflow / orchestration であり、対象プロジェクトのコードやドメインへ強く依存しない
- テンプレートごとにコピーすると、root / Python / C# の差分管理が増える
- Claude Code は personal skills を公式にサポートしている
- Codex でもローカル `~/.codex/skills/` に同種 skill が配置されている

注意点:

- Copilot の user-level skill ディレクトリは、今回確認した GitHub Docs では明示確認できなかった。Copilot については当面、repo-level `.github/copilot-instructions.md` / `.github/instructions/*.instructions.md` / `AGENTS.md` を残す方が安全である。
- C# 向けの workflow skill には `tools/AgentCliTmux` 参照、Python 向けには `scripts/agent_cli_tmux.py` 参照があり、完全共通化には `$PROJECT_LANGUAGE` またはターゲット検出が必要である。
- skill 本文が対象プロジェクトの `docs/procedure` を参照する設計のままだと、docs 手順書をプロジェクトから外した瞬間に壊れる。

### docs テンプレート

妥当。ただし、「docs をユーザレベルに置く」のではなく、「docs 雛形をユーザレベル skill に同梱し、必要時に対象プロジェクトへコピーして編集する」と整理するべきである。

既存の `python-template-doc-filler` / `csharp-template-doc-filler` は、すでに次の流れを持っている。

1. docs / instructions 内の placeholder を検出する
2. 対象プロジェクトの README、依存関係、src、tests、CI を根拠として調査する
3. `docs/rules/project_overview.md`、`docs/architecture/overview.md`、`docs/tests/*` を優先して埋める
4. `docs/components/_example_component` を実コンポーネントへ置き換える

この設計は、ユーザレベル skill として自然に再利用できる。必要なのは、コピー処理を明示化し、Python / C# で重複している doc filler を統合または共通化することである。

## 推奨アーキテクチャ

### 1. ユーザレベル Agent assets を正本化する

リポジトリ内の正本候補:

```text
user-agent-assets/
├── instructions/
│   ├── common_agent_principles.md
│   ├── workflow_selection.md
│   └── language_policy.md
├── skills/
│   ├── spec-change-workflow/
│   ├── new-feature-workflow/
│   ├── bugfix-workflow/
│   ├── issue-resolution-workflow/
│   ├── refactoring-workflow/
│   ├── research-analysis-workflow/
│   ├── ai-review-response-workflow/
│   ├── claude-review-automation/
│   └── project-doc-bootstrap/
└── install/
    ├── install_user_agent_assets.sh
    ├── install_user_agent_assets.ps1
    └── README.md
```

既存の `instructions/skills/` をそのまま移動するか、新規 `user-agent-assets/skills/` を作るかは実装設計で決めればよい。重要なのは、Python / C# テンプレート内の `instructions/skills/` を正本にしないことである。

### 2. workflow skill は self-contained にする

現行:

```text
SKILL.md -> docs/procedure/*.md を参照
```

推奨:

```text
SKILL.md
references/
  procedure/
    spec_change_workflow.md
    workflow_phase_library/...
    review_checkpoints.md
scripts/
  resolve_project_context.py
```

これにより、対象プロジェクトに `docs/procedure/` がなくても workflow skill が動く。

### 3. docs テンプレート適用 skill を追加する

新規 skill 例:

```text
project-doc-bootstrap/
├── SKILL.md
├── templates/
│   ├── common/
│   │   ├── docs/design_analysis/README.md
│   │   ├── docs/adr/README.md
│   │   ├── docs/adr/_template.md
│   │   ├── docs/history/README.md
│   │   ├── docs/issues/README.md
│   │   └── docs/todo/README.md
│   ├── python/
│   │   ├── docs/rules/coding_rules.md
│   │   ├── docs/rules/development_workflow.md
│   │   └── docs/tests/strategy.md
│   └── csharp/
│       ├── docs/rules/coding_rules.md
│       ├── docs/rules/development_workflow.md
│       └── docs/tests/strategy.md
├── references/
│   ├── python-target-docs.md
│   └── csharp-target-docs.md
└── scripts/
    └── copy_doc_templates.py
```

`copy_doc_templates.py` の想定仕様:

```bash
python scripts/copy_doc_templates.py \
  --language python \
  --target /path/to/project \
  --mode missing \
  --dry-run
```

最低限の仕様:

- `--language python|csharp|auto`
- `--target <project-root>`
- `--mode missing|overwrite`
- default は `missing` とし、既存 docs を上書きしない
- `--dry-run` でコピー対象と衝突を表示する
- コピー後、placeholder / TODO の残存を一覧化する
- Agent はその一覧をもとに対象プロジェクトへ合わせて docs を編集する

スクリプトを Python で実装する場合、C# テンプレート利用者にも Python 実行環境を要求する点が残る。ユーザレベル skill の補助スクリプトとしてなら許容しやすいが、C# テンプレート内へ同梱する場合は .NET tool 版も検討すべきである。

### 4. プロジェクトテンプレートは薄くする

Python / C# テンプレートから削減候補:

- `instructions/skills/*-workflow/`
- `.claude/skills/`
- `.github/skills/`
- 汎用 workflow 手順書としての `docs/procedure/`
- `docs/rules/skill_catalog.md`
- `scripts/sync_agent_skills.*` のうち、ユーザレベル install と重複する機能

残す候補:

- 薄い `AGENTS.md`
- 薄い `CLAUDE.md`
- 薄い `.github/copilot-instructions.md`
- `docs/design_analysis/README.md`
- `docs/adr/README.md` / `_template.md`
- `docs/rules/project_overview.md`
- `docs/rules/development_workflow.md`
- `docs/rules/coding_rules.md`
- `docs/architecture/*`
- `docs/tests/*`
- `docs/components/_example_component/*`
- `docs/issues/README.md`
- `docs/todo/README.md`
- `docs/history/README.md`

薄い project-level instructions の役割は、ユーザレベル資産の再掲ではなく、プロジェクト固有 docs への索引に限定する。

## 変更手順案

### Phase A: 方針固定

1. `docs/design_analysis/...` で本調査結果を設計化する
2. 「ユーザレベルへ移すもの / project-level に残すもの」の分類表を承認する
3. Copilot の user-level skill 相当機能について、実運用で使う対象を確認する

### Phase B: user-level skill 正本の作成

1. workflow skills を user-level 正本ディレクトリへ移す
2. `docs/procedure/` 参照を skill 内 `references/procedure/` 参照へ変更する
3. Python / C# の Agent CLI 実行差分を target language 検出または設定で吸収する
4. `install_user_agent_assets.*` を作り、少なくとも Claude / Codex へ install できるようにする

### Phase C: docs bootstrap skill の作成

1. 既存 `python-template-doc-filler` / `csharp-template-doc-filler` を統合する
2. `templates/common`、`templates/python`、`templates/csharp` を定義する
3. `copy_doc_templates.py` を追加する
4. placeholder 検出を言語共通化する
5. 既存 docs を上書きしない default にする

### Phase D: Python / C# テンプレートの縮小

1. テンプレート内 workflow skills の同梱を停止する
2. `.claude/skills` / `.github/skills` 生成物の同梱方針を見直す
3. `docs/procedure/` をテンプレートから外すか、暫定互換期間だけ残すかを決める
4. `agent_common_master.md` を project index 化する
5. `docs/rules/skill_catalog.md` を削除または user-level skills 参照の薄い索引へ変更する

### Phase E: 検証

1. user-level install の dry-run
2. 新規一時プロジェクトへ docs bootstrap を適用
3. Python / C# それぞれで placeholder 検出
4. workflow skill から `docs/design_analysis/...` を作れることを確認
5. Claude / Codex / Copilot それぞれで最低限の instructions が読まれることを確認

## リスクと対策

### リスク 1: ユーザレベル資産はチーム共有性が落ちる

ユーザホーム配下の設定は個人環境であり、リポジトリ clone だけでは再現されない。

対策:

- このリポジトリに user-level assets の正本と install script を残す
- skill に version を記録する
- project-level `AGENTS.md` に「このプロジェクトでは user-level workflow skills を前提にする」と明記する

### リスク 2: project-level と user-level の指示が衝突する

共通原則をユーザレベルへ移すほど、プロジェクト固有ルールとの優先順位が重要になる。

対策:

- user-level は原則と workflow のみにする
- project-level は具体コマンド、責務境界、例外ルールに限定する
- project-level が常に優先される前提で書く

### リスク 3: Copilot の user-level skill 配置が未確定

Claude は `~/.claude/skills` が公式に確認できる。Codex はローカルに `~/.codex/skills` が存在し、`AGENTS.md` は home 配置も可能という公開記述がある。一方、GitHub Copilot については今回確認した docs では repository custom instructions が中心で、`~/.copilot/skills` 相当は確認できなかった。

対策:

- Copilot は当面 repo-level `.github/copilot-instructions.md` / `.github/instructions/*.instructions.md` / `AGENTS.md` を維持する
- `~/.copilot` への依存は追加確認後に行う

### リスク 4: workflow skill が対象プロジェクト docs に依存して壊れる

現行 skill は `docs/procedure/...` を参照しているため、テンプレートから `docs/procedure` を外すと破綻する。

対策:

- workflow 手順書を skill の `references/` に同梱する
- 対象プロジェクトには `docs/design_analysis/` など成果物置き場だけを要求する
- skill 起動時に必須 docs ディレクトリを検査し、なければ bootstrap skill を案内する

### リスク 5: 言語別差分が user-level skill に混入する

Python と C# では検証コマンド、Agent CLI helper、コーディングルールが異なる。

対策:

- 共通 skill は target language を判定する
- 言語別 docs template は `templates/python` / `templates/csharp` に分ける
- 言語別の完了条件は project-level docs に残す

## 推奨方針

1. `skills` はユーザレベル正本化する。
2. `instructions` は共通原則だけユーザレベルへ移し、プロジェクト固有の索引と検証コマンドは project-level に残す。
3. `docs` は雛形を user-level skill の `templates/` へ移し、対象プロジェクトには bootstrap skill で実体コピーする。
4. `docs/procedure` は対象プロジェクトから外す候補にする。ただし、workflow skill の `references/` 化が完了するまでは削除しない。
5. Copilot は user-level skill 依存を避け、当面 repo-level instructions を残す。

## 次に推奨する workflow

次は `spec-change-workflow` が適切である。

理由:

- テンプレート構成、sync script、skill 配置、docs 配布方式を変更するため、仕様変更として扱うべきである
- 実装前に、どのファイルを削除 / 移動 / 新設するかの設計レビューが必要である
- 特に `docs/procedure` をテンプレートから外すかどうかは互換性と運用への影響が大きい

仕様変更の初期スコープは、次の 3 点に絞るのがよい。

1. user-level workflow skills の正本ディレクトリと install script を追加する
2. docs bootstrap skill を追加する
3. Python / C# テンプレートの project-level instructions を薄くする方針を設計する
