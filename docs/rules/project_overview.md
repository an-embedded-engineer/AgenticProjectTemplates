# プロジェクト概要

## 目的

AgenticProjectTemplates は、AI コーディングエージェントと協働するための user-level assets と、言語別 project bootstrap 資産を管理するメタプロジェクトである。workflow / review / orchestration skill の正本は `user-agent-assets/` に集約し、Python / C# の言語差分は bootstrap template、shared runtime、root tests で保持する。

## 主要コンポーネント

- `user-agent-assets/`: workflow skills、installer、project bootstrap templates の正本
- `user-agent-assets/skills/project-doc-bootstrap/templates/python/`: Python 向け bootstrap template
- `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/`: C# / .NET 向け bootstrap template
- `user-agent-assets/runtime/`: Agent CLI tmux helper と native payload の配布元
- `docs/`: AgenticProjectTemplates 自体の運用ルール、workflow、ADR、設計分析
- `tests/`: repo 共通の検証コード
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
