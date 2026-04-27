# プロジェクト概要

## 目的

AgenticProjectTemplates は、AI コーディングエージェントと協働するためのプロジェクトテンプレート集である。Python / C# の各テンプレートに、Agent instructions、workflow skills、設計・レビュー文書運用、検証用ツールを同梱する。

## 主要コンポーネント

- `python-project-template/`: Python プロジェクト向けテンプレート
- `csharp-project-template/`: C# / .NET プロジェクト向けテンプレート
- `docs/`: AgenticProjectTemplates 自体の運用ルール、workflow、ADR、設計分析
- `instructions/`: AgenticProjectTemplates 自体を保守する Agent 用 instructions / skills
- `reference/`: 横展開元などの参照プロジェクト。通常はコミット対象外

## アーキテクチャ

- 概要: `docs/architecture/overview.md`
- コードパターン: `docs/architecture/code_patterns.md`
- よくある落とし穴: `docs/architecture/common_pitfalls.md`

## 基本設計リンク

- ルール索引: `docs/rules/README.md`
- 手順書索引: `docs/procedure/README.md`
- 設計/レビュー文書運用: `docs/design_analysis/README.md`
- テスト方針: `docs/tests/README.md`
