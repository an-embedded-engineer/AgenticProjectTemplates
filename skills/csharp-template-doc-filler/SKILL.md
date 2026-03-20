---
name: csharp-template-doc-filler
description: "既存の C# プロジェクトに `csharp-project-template` を適用した後、`instructions/agent_common_master.md` の `{{PROJECT_NAME}}` / `{{PROJECT_NAME_LOWER}}` 置換、`docs/` 配下の HTML TODO コメント解消、`docs/components/_example_component` の実コンポーネント化を行う skill。ソリューション構成、`.csproj`、実行環境、テスト構成、既存 README や CI 設定を根拠にして、プロジェクト固有ドキュメントを埋める時に使う。"
---

# CSharp Template Doc Filler

## Overview

`csharp-project-template` を既存 C# / .NET プロジェクトへコピーした直後に使う。ソリューション、プロジェクト、設定、テスト、既存文書から事実を抽出し、テンプレートのプレースホルダを運用可能な文書へ置き換える。

## 実行ルール（索引）

- 対象ファイルと根拠: `references/target-docs.md`
- プレースホルダ検出: `scripts/find_placeholder_docs.py`

## 前提

- 対象リポジトリに `csharp-project-template` のファイル群がすでに配置されている
- `.sln`、`*.csproj`、実行コマンド、依存関係、テスト構成の少なくとも一部が存在する
- 推測だけで埋めず、repo 内の根拠を優先する

## 進め方

1. バンドルされた `scripts/find_placeholder_docs.py <project-root>` を実行し、`{{PROJECT_NAME}}` 系マクロと `<!-- TODO: ... -->` を列挙する
2. `references/target-docs.md` を読み、優先度の高い文書から埋める
3. `.sln`、`*.csproj`、`Directory.Build.props`、`Directory.Build.targets`、`global.json`、`README*`、`src/`、`tests/`、`Program.cs`、`appsettings*.json`、`Properties/launchSettings.json`、`Dockerfile*`、`.github/workflows/` を確認し、事実をメモする
4. `instructions/agent_common_master.md` と `instructions/skills/**/*.md` の `{{PROJECT_NAME}}` / `{{PROJECT_NAME_LOWER}}` を置換する。ただし `instructions/symlink_migration_guide.md` の `{{SKILL_NAME}}` は利用例なので置換しないこと
5. `docs/rules/project_overview.md`、`docs/architecture/overview.md`、`docs/rules/development_workflow.md`、`docs/tests/README.md`、`docs/tests/strategy.md` を先に埋める
6. `docs/architecture/code_patterns.md` と `docs/architecture/common_pitfalls.md` を、実際に見つかった規約と事故りやすい点だけで埋める
7. `docs/components/_example_component/` を実コンポーネントへ置き換える。複数コンポーネントがあるなら `docs/components/<component>/` を追加し、例示用ディレクトリは削除する
8. 更新後に再度 `scripts/find_placeholder_docs.py <project-root>` を実行し、触れた対象に生のプレースホルダが残っていないこと、および `_example_component` 警告が出ていないことを確認する

## 記述ルール

- ドキュメント本文は日本語で簡潔に書く
- 実行コマンドは repo に存在する実コマンドをそのまま書く
- クラス名、名前空間、プロジェクト名、ディレクトリ名は実在識別子を使う
- 根拠がない項目は捏造しない
- 情報が不足する場合でも、生のテンプレート TODO は残さず `要確認:` 形式で不足情報と確認元を明記する
- テンプレートの見出し構造は維持する
- 大きいプロジェクトでも最初は主要コンポーネント 1 から 3 件に絞る

## コンポーネント文書の扱い

- `src/` 直下、主要プロジェクト、主要名前空間から責務境界が明確な単位を選ぶ
- `README.md` には目的、責務、依存関係を書く
- `basic_design.md` には責務、主要クラス、依存関係を書く
- `detail_design.md` には状態管理、処理フロー、例外処理を書く
- `interface_spec.md` には公開 API、主要サービス境界、または主要エンドポイントを書く
- `issues.md` には既知不具合が repo 内に見当たらなければ、未整理である旨を書く。架空の Issue ID は作らない

## 最低限の必須チェック

1. `{{PROJECT_NAME}}` と `{{PROJECT_NAME_LOWER}}` をすべて解消する
2. 高優先度文書を repo 根拠ベースで更新する
3. 実行コマンド、ビルドコマンド、テストコマンドを現行プロジェクトに合わせる
4. `docs/components/_example_component` を実体に置き換えるか、保留理由を明記する
5. 触れたファイルに生の `<!-- TODO:` を残さない
