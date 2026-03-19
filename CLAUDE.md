# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## リポジトリ概要

AI エージェント（Claude Code / GitHub Copilot / Codex）向けの**プロジェクトテンプレート集**。
各サブディレクトリ（例: `python-project-template/`）は、新規プロジェクトにコピーして使う自己完結型テンプレート。

## 構成

各テンプレートは同一のディレクトリ構成を持つ。言語固有の内容（ビルド・静的解析・テスト・落とし穴など）のみが異なる。

```
AgenticProjectTemplates/
├── python-project-template/   # Python 3.10+ 向け
└── csharp-project-template/   # C# / .NET 8.0+ 向け
```

### 共通テンプレート構成

```
<template>/
├── AGENTS.md → instructions/agent_common_master.md (symlink)
├── CLAUDE.md → instructions/agent_common_master.md (symlink)
├── .github/copilot-instructions.md → 同上 (symlink)
├── instructions/
│   ├── agent_common_master.md    # 全エージェント共通の単一マスターファイル
│   ├── skills/                   # ワークフロー skill 定義 (SKILL.master.md)
│   └── symlink_migration_guide.md
├── docs/
│   ├── rules/          # 開発ルール（コーディング・言語・ワークフロー）
│   ├── architecture/   # アーキテクチャ概要・コードパターン・落とし穴
│   ├── procedure/      # ワークフロー手順書
│   ├── tests/          # テスト戦略
│   ├── components/     # コンポーネント別設計文書
│   ├── design_analysis/# 設計/レビュー追跡
│   ├── todo/           # 追跡: spec-change / new-feature / refactoring
│   ├── issues/         # 追跡: bugfix / issue-resolution
│   └── history/        # 実装履歴
├── scripts/
│   └── sync_agent_skills.sh  # SKILL.master.md を .claude/ .github/ ~/.codex/ へ配布
└── tools/
    └── extract_git_diff.py   # git差分抽出ツール（ワークフローで使用）
```

## 設計上の重要な判断

### symlink ベースのマスターファイル戦略
全エージェント向けファイル（`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`）は単一マスター（`instructions/agent_common_master.md`）への symlink。GitHub Copilot・Claude Code・Codex 間の一貫性を保証する。skills も `SKILL.master.md` で同様のパターンを使用。

### マスターファイルは索引のみ
`agent_common_master.md` は `docs/` 配下への参照のみを記載。詳細ルールは `docs/rules/`・`docs/architecture/`・`docs/procedure/` に分離し、個別に保守可能にしている。

### skills 同期メカニズム
`scripts/sync_agent_skills.sh` が skill 定義を配布する:
- `.claude/skills/` と `.github/skills/` → `SKILL.master.md` への **symlink**
- `~/.codex/skills/` → **実体コピー**（Codex は symlink 非対応）
- 旧コピーは `~/.codex/skills/_obsoleted/` にバックアップ

### tools ディレクトリ
`tools/extract_git_diff.py` はワークフローで使用する git 差分抽出ツール。日付範囲またはコミット ID 範囲を指定し、変更ファイルの before/after ソースと unified diff、レポート（`report.md`）を出力する。

```bash
# 日付範囲指定
python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01

# コミットID範囲指定
python tools/extract_git_diff.py --commit-from abc1234 --commit-to def5678

# ディレクトリ・拡張子フィルタ付き
python tools/extract_git_diff.py --date-from 2024-01-01 --date-to 2024-02-01 -d src tests -e .py

# 出力先指定（デフォルト: output/git_diff）
python tools/extract_git_diff.py --commit-from abc1234 --commit-to def5678 -o output/my_diff
```

## テンプレート別ルール

### 共通ルール（全テンプレート共通）

#### 言語規約
- 内部思考: 英語
- チャット応答: 日本語
- コメント / ドキュメントコメント: 日本語
- ログ / UI / エラー文字列: 英語
- `docs/` 配下ドキュメント: 日本語

#### 必須コーディングルール（共通）
- 例外握りつぶし禁止 — 必ず原因をログに残し、re-raise か明示的にハンドリング
- 不要なフォールバック禁止 — 早期失敗を優先
- 型付きデータモデル必須 — 汎用的な辞書/マップでのデータ受け渡し禁止
- リフレクション・動的アクセス制限

#### ワークフロー skills
タスク種別に応じた構造化ワークフローを提供:
- `spec-change-workflow` — 仕様変更
- `new-feature-workflow` — 新機能追加
- `bugfix-workflow` — 不具合修正
- `issue-resolution-workflow` — bug 以外の既知課題
- `refactoring-workflow` — 外部仕様を変えない構造改善
- `ai-review-response-workflow` — AI レビュー結果の反映

ワークフロー詳細は `docs/procedure/` を参照。追跡項目は `docs/todo/`（spec-change / new-feature / refactoring）または `docs/issues/`（bugfix / issue-resolution）で管理。

### Python テンプレート固有

```bash
# セットアップ
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 実行（PYTHONPATH=src は必須）
PYTHONPATH=src .venv/bin/python -m main

# テスト
PYTHONPATH=src .venv/bin/pytest                                # 全テスト
PYTHONPATH=src .venv/bin/pytest tests/test_foo.py::test_bar -v # 単一テスト
PYTHONPATH=src .venv/bin/pytest -x                             # 最初の失敗で停止

# 型チェック（完了条件: エラー 0 件）
.venv/bin/pyright --outputjson > pylance_error.json
```

- 型ヒント必須（`Optional` は `None` ガードとセット、`Any` は I/O 境界のみ）
- `getattr` / `setattr` / `__dict__` 禁止
- `dataclass` / `TypedDict` / Pydantic を使用（生 `dict` 禁止）
- Pyright エラー 0 件を完了条件とする

### C# テンプレート固有

```bash
# セットアップ
dotnet restore

# ビルド（完了条件: 警告・エラー 0 件）
dotnet build --warnaserrors

# テスト
dotnet test                                                    # 全テスト
dotnet test --filter "FullyQualifiedName~TestClass.TestMethod" # 単一テスト
dotnet test tests/App.Tests                                    # 特定プロジェクト

# フォーマット
dotnet format --verify-no-changes
```

- Nullable 参照型有効（`<Nullable>enable</Nullable>`、`T?` は null チェックとセット）
- `reflection` / `dynamic` / `ExpandoObject` 制限
- `record` / DTO クラスを使用（`Dictionary<string, object>` 禁止）
- `dotnet build --warnaserrors` エラー 0 件を完了条件とする
