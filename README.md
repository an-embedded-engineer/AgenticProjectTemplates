# AgenticProjectTemplates

AI コーディングエージェント（Claude Code / GitHub Copilot / Codex）と協働するためのプロジェクトテンプレート集です。

## 概要

新規プロジェクトを立ち上げる際に、AI エージェント向けのインストラクション・ワークフロー・ドキュメント構成を一式コピーしてすぐに使い始められるテンプレートを提供します。

### 特徴

- **マルチエージェント対応** — `AGENTS.md`（Codex）・`CLAUDE.md`（Claude Code）・`copilot-instructions.md`（GitHub Copilot）を単一マスターファイルからの symlink で一元管理
- **構造化ワークフロー** — 仕様変更・新機能追加・不具合修正・リファクタリングなど、タスク種別ごとの skill を定義済み
- **型安全性重視** — 静的解析ゼロエラーを完了条件とするコーディングルール（Python: Pyright / C#: dotnet build --warnaserrors）
- **ドキュメント駆動** — アーキテクチャ・設計・手順書・テスト戦略のテンプレートを同梱

## テンプレート一覧

| テンプレート | 対象 | 説明 |
|---|---|---|
| [python-project-template](python-project-template/) | Python 3.10+ | Pyright 型チェック・pytest・構造化ワークフローを備えた Python プロジェクトテンプレート |
| [csharp-project-template](csharp-project-template/) | C# / .NET 8.0+ | dotnet build 警告ゼロ・dotnet test・構造化ワークフローを備えた C# プロジェクトテンプレート |

## 使い方

### 1. テンプレートをコピー

```bash
# Python プロジェクトの場合
cp -r python-project-template/ /path/to/your-new-project/

# C# プロジェクトの場合
cp -r csharp-project-template/ /path/to/your-new-project/

cd /path/to/your-new-project/
```

### 2. プレースホルダを埋める

- `instructions/agent_common_master.md` 内の `{{PROJECT_NAME}}` をプロジェクト名に置換
- `docs/rules/project_overview.md` にプロジェクト概要を記述
- `docs/architecture/overview.md` にアーキテクチャを記述
- 各 `docs/` 配下の `<!-- TODO: ... -->` を埋める

### 3. skills を同期

```bash
./scripts/sync_agent_skills.sh
```

`.claude/skills/`・`.github/skills/` に symlink、`~/.codex/skills/` に実体コピーが配布されます。

### 4. 開発開始

```bash
# Python の場合
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# C# の場合
dotnet restore
```

## ディレクトリ構成（共通）

各テンプレートは同一のディレクトリ構成を持ちます。言語固有の内容（ビルド・静的解析・テスト・落とし穴など）のみが異なります。

```
<template>/
├── instructions/           # エージェント共通インストラクション（マスター）
│   ├── agent_common_master.md
│   └── skills/             # ワークフロー skill 定義
├── docs/
│   ├── rules/              # 開発ルール（コーディング・言語・ワークフロー）
│   ├── architecture/       # アーキテクチャ・コードパターン・落とし穴
│   ├── procedure/          # ワークフロー手順書
│   ├── components/         # コンポーネント別設計文書
│   ├── design_analysis/    # 設計/レビュー追跡
│   └── tests/              # テスト戦略
├── scripts/
│   └── sync_agent_skills.sh
└── tools/
    └── extract_git_diff.py # git 差分抽出・レポート生成ツール
```

## ワークフロー skills

| Skill | トリガー |
|---|---|
| `spec-change-workflow` | 仕様変更の要求を受けた時 |
| `new-feature-workflow` | 新機能追加の要求を受けた時 |
| `bugfix-workflow` | 既存機能の不具合修正を行う時 |
| `issue-resolution-workflow` | bug ではない既知課題を解決する時 |
| `refactoring-workflow` | 外部仕様を変えない構造改善を行う時 |
| `ai-review-response-workflow` | 設計/コードレビューの結果を反映する時 |

## ツール

### extract_git_diff.py

git コミット履歴から指定範囲の差分を抽出し、before/after ソース・unified diff・レポートを出力します。

```bash
# 日付範囲指定
python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01

# コミットID範囲指定
python tools/extract_git_diff.py --commit-from abc1234 --commit-to def5678

# フィルタ付き
python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01 -d src -e .py
```

## ライセンス

MIT
