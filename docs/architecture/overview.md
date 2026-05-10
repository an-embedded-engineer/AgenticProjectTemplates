# アーキテクチャ概要

## コアコンポーネント

### Python bootstrap template

`user-agent-assets/skills/project-doc-bootstrap/templates/python/` に Python project 向け docs / rules / instructions template を保持する。

### C# bootstrap template

`user-agent-assets/skills/project-doc-bootstrap/templates/csharp/` に C# / .NET project 向け docs / rules / instructions template を保持する。

### Root infra (`docs/`, `instructions/`, `user-agent-assets/`, `scripts/`)

AgenticProjectTemplates 自体の保守ルール、レビュー運用、ADR、project-level instruction sync source、user-level assets、bootstrap templates を保持する。テンプレート内 infra の横展開前に root infra で方針を固定する。

### Reference (`reference/`)

横展開元プロジェクトなどの参照用ディレクトリ。通常は未追跡のまま扱い、コミット対象へ含めない。

## 基本フロー

1. `reference/` または既存テンプレートから変更候補を調査する
2. root `docs/` / `user-agent-assets/` で方針と workflow を整理する
3. root `instructions/` を同期元として Agent 向け生成物を再生成する
4. `project-doc-bootstrap` の Python / C# template へ言語特性に合わせて横展開する
5. 各 language variant と repo toolchain の検証を実行する
6. design analysis / history / tracking docs を同期する

## 主要ファイルリファレンス

- user-level skill 正本: `user-agent-assets/skills/`
- user-level install / bootstrap: `user-agent-assets/install/`, `user-agent-assets/skills/project-doc-bootstrap/`
- shared Agent CLI tmux runtime: `user-agent-assets/runtime/agent-cli-tmux/`
- Root instruction sync source: `instructions/agent_common_master.md`
- Root instruction sync guide: `instructions/agent_sync_guide.md`
- Root instruction sync script: `scripts/sync_agent_instructions.sh`
- Root Agent CLI tmux tool: `scripts/agent_cli_tmux.py`
- Python / pytest tests: `tests/`
- Python bootstrap tools: `user-agent-assets/skills/project-doc-bootstrap/templates/python/tools/`
- C# bootstrap tools: `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/`
- C# tests: `tests/AgentCliTmux.Tests/`

`scripts/agent_cli_tmux.py` は root のレビュー運用向け正本であり、Python 側の検証は `tests/test_agent_cli_tmux.py` で直接行う。workflow 手順の実行時参照は `user-agent-assets/skills/*/references/procedure/` を正とする。

## ドキュメント構成

```
docs/
├── adr/              — 横断判断の索引
├── architecture/     — アーキテクチャ概要・パターン・注意点
├── design_analysis/  — 設計分析・レビュー文書
├── rules/            — 開発ルール
├── tests/            — テスト方針・構成
├── todo/             — 追跡項目（spec-change / new-feature / refactoring / documentation）
├── issues/           — 追跡項目（bugfix / issue-resolution）
└── history/          — 実装履歴
```

## 設計文書リファレンス

- 設計/レビュー文書運用: `docs/design_analysis/README.md`
- 追跡項目: `docs/todo/todo.md`, `docs/issues/cross/issues.md`
- ADR: `docs/adr/README.md`
