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
  - GitHub Copilot agent skills / repository custom instructions docs
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
- GitHub Copilot agent skills: <https://learn.microsoft.com/ja-jp/visualstudio/ide/copilot-agent-skills?view=visualstudio>
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

`diff -qr` で確認すると、Python / C# 間の `docs/procedure` には多数の差分があり、差分の多くは Python / C# の言語差やツール差である。代表例は次の通りである。

- `python-project-template/instructions/skills/claude-review-automation/SKILL.master.md` は `scripts/agent_cli_tmux.py` を参照するが、C# 側は `tools/AgentCliTmux` と `dotnet run --project tools/AgentCliTmux -- ...` を参照する。
- `python-project-template/docs/procedure/workflow_phase_library/new_feature/phase_4_impl_focus.md` は `getattr` / `setattr` / `Any` / `Dict` を制限対象にしているが、C# 側は `reflection` / `dynamic` / `object` / `Dictionary<string, object?>` を制限対象にしている。
- `python-project-template/docs/rules/coding_rules.md` は完了条件を `./.venv/bin/pyright --outputjson > pylance_error.json` としているが、C# 側は `dotnet build --warnaserrors` としている。

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

これらはプロジェクト固有のドメイン知識というより、Agent 作業の進め方そのものである。Claude Code 公式 docs では、個人 skill を `~/.claude/skills/<skill-name>/SKILL.md` に置けるとされる。Microsoft Learn の GitHub Copilot agent skills docs でも、個人 skill の場所として `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` が明記され、workspace skill の場所として `.github/skills/`、`.claude/skills/`、`.agents/skills/` が明記されている。ローカルにも `~/.codex/skills/` に同種の workflow skills が配置済みである。

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

ただし、これらのファイルは直接編集対象ではない。現行テンプレートでは `instructions/agent_common_master.md` や `instructions/*.draft.md` が sync source であり、`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は `scripts/sync_agent_skills.*` による生成物である。したがって「薄くする」とは、生成物ではなく sync source と同期スクリプトの責務を薄くすることを意味する。

### skills

妥当。むしろ最も移行効果が大きい。

理由:

- 現行 skill は workflow / orchestration であり、対象プロジェクトのコードやドメインへ強く依存しない
- テンプレートごとにコピーすると、root / Python / C# の差分管理が増える
- Claude Code は personal skills を公式にサポートしている
- Codex でもローカル `~/.codex/skills/` に同種 skill が配置されている

注意点:

- Copilot の user-level skill ディレクトリは `~/.copilot/skills/` として Microsoft Learn に明記されている。加えて、Copilot agent skills は `~/.claude/skills/` と `~/.agents/skills/` も個人 skill として検出対象にする。したがって Copilot についても、workflow / orchestration skills をユーザレベル正本化する方針に含めてよい。ただし同 docs の前提は Visual Studio 2026 version 18.5 以降であるため、VS Code Copilot Chat / Copilot CLI まで同じ検出挙動を前提にするかは、実装前に対象環境ごとに確認する。
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

現行の skill 正本は多くが `SKILL.master.md` であり、同期先では `SKILL.md` として生成される。user-level 正本化では、`{{PROJECT_NAME}}` / `{{PROJECT_NAME_LOWER}}` などの placeholder を残さない一般 skill へ変換するか、install 時に対象プロジェクト名を解決して `SKILL.md` を生成するかを決める必要がある。単に `SKILL.master.md` を `~/.codex/skills` や `~/.claude/skills` へコピーするだけでは不十分である。

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

ここでの `SKILL.md` は user-level の実行時正本である。既存 `SKILL.master.md` を継続する場合は、install script が `SKILL.master.md` から placeholder を除去または解決して `SKILL.md` を生成する。

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

スクリプトを Python で実装する場合、C# テンプレート利用者にも Python 実行環境を要求する点が残る。ユーザレベル skill の補助スクリプトとしてなら、project-template 内の「C# には .NET tool を優先する」ルールの直接対象外と整理できる。ただし、その前提は明文化する必要がある。C# テンプレート内へ同梱する、または C# プロジェクトの通常運用コマンドとして要求する場合は .NET tool 版も検討すべきである。

### 4. プロジェクトテンプレートは薄くする

Python / C# テンプレートから削減候補:

- `instructions/skills/*-workflow/`
- `.claude/skills/`
- `.github/skills/`
- 汎用 workflow 手順書としての `docs/procedure/`
- `docs/rules/skill_catalog.md`
- `scripts/sync_agent_skills.*` のうち、ユーザレベル install と重複する機能

`docs/rules/skill_catalog.md` は root / template の `agent_common_master.md` から参照されているため、削除する場合は `CLAUDE.md`、`AGENTS.md`、`.github/copilot-instructions.md`、各 `SKILL.master.md` の索引参照も同時に更新する必要がある。削除ではなく「user-level skills の薄い索引」として残す案も比較対象にする。

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
3. Copilot agent skills の対象環境を確認する
   - Microsoft Learn で確認済み: Visual Studio 2026 version 18.5 以降
   - 実装前確認対象: VS Code Copilot Chat / Copilot CLI で同じ skill 検出が使えるか

### Phase B: user-level skill 正本の作成

1. workflow skills を user-level 正本ディレクトリへ移す
2. `SKILL.master.md` を user-level の `SKILL.md` へ変換する方針を決める
   - placeholder を持たない一般 skill へ書き換える
   - または install 時に placeholder を解決して `SKILL.md` を生成する
3. `docs/procedure/` 参照を skill 内 `references/procedure/` 参照へ変更する
4. Python / C# の Agent CLI 実行差分を target language 検出または設定で吸収する
5. `install_user_agent_assets.*` を作り、少なくとも Copilot / Claude / Codex へ install できるようにする
6. install script は `~/.copilot/skills`、`~/.claude/skills`、`~/.agents/skills`、`~/.codex/skills` が未作成でも作成でき、既存 user-level skill を不用意に上書きしない冪等な挙動にする

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
4. sync source である `instructions/agent_common_master.md` と `instructions/*.draft.md` を project index 化する
5. `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` は直接編集せず、同期スクリプト経由で再生成する
6. `scripts/sync_agent_skills.*` の責務を再定義する
   - user-level install を担うのか
   - project-level 生成物だけを担うのか
   - 暫定的に project-level skills を維持する mode を持つのか
7. `docs/rules/skill_catalog.md` を削除、縮小、または user-level skills 参照の薄い索引として残すかを決め、参照元を同時に更新する

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

### リスク 3: Copilot の user-level skill 対応環境が限定される可能性

Microsoft Learn の GitHub Copilot agent skills docs では、個人 skill の場所として `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` が正式に示されている。workspace skill も `.github/skills/`、`.claude/skills/`、`.agents/skills/` が対象である。

一方で、同 docs の prerequisites は Visual Studio 2026 version 18.5 以降と GitHub Copilot subscription である。VS Code Copilot Chat や Copilot CLI が同じ user-level skill 検出を行うかは、この調査時点では未確認である。

対策:

- Copilot も user-level skills 正本化の対象に含める
- install script は `~/.copilot/skills/` と `~/.agents/skills/` をサポート対象に含める
- project-level `.github/skills/` / `.claude/skills/` / `.agents/skills/` は、チーム共有したい skill だけを置く fallback / workspace 共有経路として整理する
- VS Code Copilot Chat / Copilot CLI で同じ検出が使えない場合だけ、`.github/copilot-instructions.md` / `AGENTS.md` で user-level skill 利用を案内する

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
- user-level skill 内の補助スクリプトは project-template 内の同梱ツールではないため、Python / .NET の重複実装ルールを直接適用しない。ただし、C# プロジェクト利用者に Python を必須要件として押し付ける設計にする場合は、.NET tool 版または PowerShell 版の提供を比較する。

## 未解決事項

次 workflow へ渡す前提として、少なくとも次を未解決事項として扱う。

1. project-level sync source の範囲
   - `instructions/agent_common_master.md`
   - `instructions/AGENTS.draft.md`
   - `instructions/CLAUDE.draft.md`
   - `instructions/copilot-instructions.draft.md`
   - `scripts/sync_agent_skills.*`
2. Copilot の対象環境
   - Visual Studio 2026 version 18.5 以降は `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` を前提にできる
   - VS Code Copilot Chat / Copilot CLI で同じ skill 検出が使えるか
   - 未対応環境向けに `.github/copilot-instructions.md` / `AGENTS.md` で user-level 資産への索引を残すか
3. `SKILL.master.md` から user-level `SKILL.md` への変換方針
   - placeholder を除去した一般 skill にするか
   - install 時に placeholder を解決するか
4. `docs/rules/skill_catalog.md` の扱い
   - 削除
   - 縮小
   - user-level skills の薄い索引として維持
5. user-level install script の安全要件
   - dry-run
   - missing-only default
   - 既存 user skill の上書き保護
   - `~/.copilot/skills` / `~/.claude/skills` / `~/.agents/skills` / `~/.codex/skills` 未作成時の作成
6. `docs/procedure/` を project-level から外す時期
   - workflow skill の `references/` 化完了まで暫定保持するか
   - bootstrap skill で必要時だけコピーするか
7. user-level skill 補助スクリプトの言語
   - Python 単体でよいか
   - C# 利用者向けに .NET / PowerShell 版も持つか

## 推奨方針

1. `skills` はユーザレベル正本化する。
2. `instructions` は共通原則だけユーザレベルへ移し、プロジェクト固有の索引と検証コマンドは project-level に残す。
3. `docs` は雛形を user-level skill の `templates/` へ移し、対象プロジェクトには bootstrap skill で実体コピーする。
4. `docs/procedure` は対象プロジェクトから外す候補にする。ただし、workflow skill の `references/` 化が完了するまでは削除しない。
5. Copilot も user-level skill 正本化の対象に含める。`~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` を install 対象にし、project-level `.github/skills/` はチーム共有が必要な skill のみ残す。

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
