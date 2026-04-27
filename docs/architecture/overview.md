# アーキテクチャ概要

## コアコンポーネント

### Python テンプレート (`python-project-template/`)

Python プロジェクト向けの Agent instructions、workflow docs、Python tool / pytest 構成を保持する。

### C# テンプレート (`csharp-project-template/`)

C# / .NET プロジェクト向けの Agent instructions、workflow docs、.NET tool / C# test runner 構成を保持する。

### Root infra (`docs/`, `instructions/`, `scripts/`)

AgenticProjectTemplates 自体の保守 workflow、レビュー運用、ADR、Claude review 自動化を保持する。テンプレート内 infra の横展開前に root infra で方針を固定する。

### Reference (`reference/`)

横展開元プロジェクトなどの参照用ディレクトリ。通常は未追跡のまま扱い、コミット対象へ含めない。

## 基本フロー

1. `reference/` または既存テンプレートから変更候補を調査する
2. root `docs/` / `instructions/` で方針と workflow を整理する
3. `python-project-template/` と `csharp-project-template/` へ言語特性に合わせて横展開する
4. 各テンプレート固有の検証を実行する
5. design analysis / history / tracking docs を同期する

## 主要ファイルリファレンス

- Root instructions: `instructions/agent_common_master.md`
- Root skills: `instructions/skills/`
- Root workflow docs: `docs/procedure/`
- Python template instructions: `python-project-template/instructions/`
- C# template instructions: `csharp-project-template/instructions/`
- Python Agent CLI tmux tool: `python-project-template/scripts/agent_cli_tmux.py`
- C# Agent CLI tmux tool: `csharp-project-template/tools/AgentCliTmux/`

## ドキュメント構成

```
docs/
├── adr/              — 横断判断の索引
├── architecture/     — アーキテクチャ概要・パターン・注意点
├── design_analysis/  — 設計分析・レビュー文書
├── procedure/        — ワークフロー手順書
├── rules/            — 開発ルール
├── tests/            — テスト方針・構成
├── todo/             — 追跡項目（spec-change / new-feature / refactoring）
├── issues/           — 追跡項目（bugfix / issue-resolution）
└── history/          — 実装履歴
```

## 設計文書リファレンス

- 設計/レビュー文書運用: `docs/design_analysis/README.md`
- 追跡項目: `docs/todo/todo.md`, `docs/issues/cross/issues.md`
- ADR: `docs/adr/README.md`
