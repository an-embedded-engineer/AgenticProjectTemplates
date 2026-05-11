# AgenticProjectTemplates

AI コーディングエージェント（Claude Code / GitHub Copilot / Codex）向けの user-level assets と project bootstrap 資産を管理するリポジトリです。

## 概要

新規プロジェクトを立ち上げる際に、user-level workflow skills を install し、`project-doc-bootstrap` で言語別 docs / instructions / sync script を初期配置するための正本を提供します。

### 特徴

- **user-level assets 正本化** — workflow / review / orchestration skill は `user-agent-assets/` を正本として管理
- **project bootstrap 対応** — `project-doc-bootstrap` で target project に docs / instructions / sync script を配布
- **型安全性重視** — 静的解析ゼロエラーを完了条件とするコーディングルール（Python: Pyright / C#: dotnet build --warnaserrors）
- **ドキュメント駆動** — アーキテクチャ・設計・テスト戦略のテンプレートと、workflow 手順を同梱した user-level skill を提供

## 提供資産

| 資産 | 対象 | 説明 |
|---|---|---|
| `user-agent-assets/skills/` | user-level skills | workflow / review / orchestration skill の正本 |
| `user-agent-assets/skills/project-doc-bootstrap/` | project bootstrap | Python / C# 向け docs / instructions / sync script template |
| `user-agent-assets/runtime/` | shared runtime | Agent CLI tmux wrapper 用の runtime helper と native payload |
| `project-skills/` | project-local skills | このリポジトリ自身の保守専用 skill。user-level install 対象外 |
| `instructions/` | project-level instruction source | `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の同期元 |
| `tests/` | repo validation | Python pytest と C# test runner |

## 使い方

### 1. user-level assets を install

```bash
bash user-agent-assets/install/install_user_agent_assets.sh --mode overwrite
```

PowerShell を使う場合:

```powershell
pwsh -File user-agent-assets/install/install_user_agent_assets.ps1 -Mode overwrite
```

### 2. target project を bootstrap

- install 済みの `project-doc-bootstrap` を使って、target project に docs / project-level instructions / `scripts/sync_agent_instructions.*` を配置する
- Python / C# の言語差分は `user-agent-assets/skills/project-doc-bootstrap/templates/` 配下の template で吸収する

### 3. プレースホルダを埋める

- `instructions/agent_common_master.md` 内の `{{PROJECT_NAME}}` をプロジェクト名に置換
- `docs/rules/project_overview.md` にプロジェクト概要を記述
- `docs/architecture/overview.md` にアーキテクチャを記述
- 各 `docs/` 配下の `<!-- TODO: ... -->` を埋める

### 4. project-level instructions を同期

```bash
./scripts/sync_agent_instructions.sh
```

この sync は target project の `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` 再生成だけを扱います。

### 5. 開発開始

```bash
# Python の場合
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# C# の場合
dotnet restore
```

## ディレクトリ構成（共通）

この repo は user-level assets と bootstrap templates を正本として保持します。

```
AgenticProjectTemplates/
├── user-agent-assets/
│   ├── install/
│   ├── skills/
│   │   └── project-doc-bootstrap/
│   │       └── templates/
│   │           ├── python/
│   │           └── csharp/
│   ├── runtime/
│   └── bin/
├── project-skills/
├── instructions/
│   ├── agent_common_master.md
│   └── agent_sync_guide.md
├── docs/
├── scripts/
│   └── sync_agent_instructions.*
└── tests/
```

## ワークフロー skills

workflow 手順の正本は各 skill 配下の `references/procedure/` に同梱されます。

| Skill | トリガー |
|---|---|
| `spec-change-workflow` | 仕様変更の要求を受けた時 |
| `new-feature-workflow` | 新機能追加の要求を受けた時 |
| `bugfix-workflow` | 既存機能の不具合修正を行う時 |
| `issue-resolution-workflow` | bug ではない既知課題を解決する時 |
| `refactoring-workflow` | 外部仕様を変えない構造改善を行う時 |
| `documentation-workflow` | docs だけを作成・更新・整理する時 |
| `ai-review-response-workflow` | 設計/コードレビューの結果を反映する時 |

## Project-local maintenance skills

このリポジトリ自身の保守だけで使う skill は `project-skills/` 配下に置き、`user-agent-assets/` の install 対象には含めません。

| Skill | トリガー |
|---|---|
| `user-agent-assets-update-workflow` | user-agent-assets の skill / runtime / installer / template を更新する時 |

project-local skill は次のコマンドで Agent ごとの discovery path へ同期します。同期先の `.github/skills/`、`.claude/skills/`、`.codex/skills/` は生成物です。

```bash
./scripts/sync_project_skills.sh --all
```

PowerShell / Windows cmd を使う場合:

```powershell
pwsh -File scripts/sync_project_skills.ps1 -All
```

```bat
scripts\sync_project_skills.bat --all
```

## ツール

### extract_git_diff

git コミット履歴から指定範囲の差分を抽出し、before/after ソース・unified diff・レポートを出力します。Python / C# project へ配る正本は `project-doc-bootstrap` の language template 配下で管理します。

```bash
# Python project template
python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01
python tools/extract_git_diff.py --commit-from abc1234 --commit-to def5678
python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01 -d src -e .py

# C# project template
dotnet run --project tools/ExtractGitDiff -- --date-from 2024-01-01 --date-to 2024-02-01
dotnet run --project tools/ExtractGitDiff -- --commit-from abc1234 --commit-to def5678
dotnet run --project tools/ExtractGitDiff -- --date-from 2024-01-01 --date-to 2024-02-01 -d src -e .cs
```

## ライセンス

MIT
