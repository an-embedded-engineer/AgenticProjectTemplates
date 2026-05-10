# workflow skill Phase 簡略化 差分・変更レポート

## 概要

TODO-2026-001 に基づき、core workflow skill を 4 ゲート構成へ更新した。

## 主な変更

- Phase 2: 要求、範囲、採否理由、リスク、テスト観点を含む方針・設計レビュー
- Phase 3: 実装と恒久ドキュメント反映を同時に扱う impl review
- Phase 4: 動作確認、完了処理、merge 承認
- review 文書: `design_review` / `impl_review` を標準化し、`completion_review` は optional 化
- `related_commits`: core workflow では completion 集約
- 大規模変更: `wbs-planning-workflow` で work package へ分解

## 検証結果

| コマンド | 結果 |
|---|---|
| `./scripts/sync_agent_instructions.sh --help` | OK |
| `./scripts/sync_agent_instructions.sh` | OK |
| `python3 -m py_compile scripts/agent_cli_tmux.py` | OK |
| `bash user-agent-assets/install/install_user_agent_assets.sh --help` | OK |
| `bash user-agent-assets/install/install_user_agent_assets.sh --dry-run --mode overwrite --targets codex` | OK |
| `python3 -m pytest tests/test_agent_cli_tmux.py` | 14 passed |
| `python3 -m pytest tests/test_extract_git_diff.py` | 2 passed |
| `dotnet build user-agent-assets/runtime/agent-cli-tmux/csharp/AgentCliTmux/AgentCliTmux.csproj` | OK |
| `dotnet run --project tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj` | 13/13 passed |
| `dotnet build user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff/ExtractGitDiff.csproj` | OK |

追加確認:

- 新規運用に不要な status、review 命名、履歴前提の記述が、現行 skill / shared phase library / 新規運用 docs から消えていることを確認した
- installer dry-run で `wbs-planning-workflow` が user-level skill 配布対象に含まれることを確認した

残存参照チェックでは、現行 skill / shared phase library の手順が新しい workflow 契約だけで読めることを確認した。
`research-analysis-workflow` の Phase 5 表記は同 workflow 固有の現行手順として残している。
