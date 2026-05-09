# ユーザレベル Agent 資産化 実装記録

## 目的

SC-20260508-001 の追加実装として、repo 内に残っていた旧 project-template / project-level skill 構成を撤去し、shared runtime と bootstrap template への責務再配置を完了させる。あわせて、C# 検証が repo-local workaround に依存せず system の `dotnet` のみで実行できる状態を確認し、その前提を恒久ドキュメントへ反映する。

## 今回の実装スコープ

- 旧 root / template `instructions/`、`scripts/sync_agent_skills.*`、repo-local `.github/skills/` / `.claude/skills/` の削除
- `python-project-template/` と `csharp-project-template/` の repo からの撤去
- AgentCliTmux の shared runtime への再配置
- ExtractGitDiff の Python / C# bootstrap template `tools/` への再配置
- C# test runner が system の `.NET 9` SDK / runtime で動作することの確認
- repo-local `.dotnet9` workaround の撤去
- C# 実行前提を `docs/tests/README.md` と `docs/rules/development_workflow.md` に反映

## 設計差分との対応

### 1. repo の責務整理

設計では、repo を project-template 配布元ではなく user-level assets、bootstrap template、shared runtime の保守 repo へ寄せる方針を採っていた。今回の追加実装では、旧 template ディレクトリと旧 project-level skill 配布経路を削除し、その方針を実ファイル構成へ反映した。

### 2. tool 配置原則の確定

- AgentCliTmux は install 後も user-level wrapper から参照される shared runtime であるため、`user-agent-assets/runtime/agent-cli-tmux/csharp/AgentCliTmux/` を正本にした
- ExtractGitDiff は bootstrap 後の target project に同梱される project-local tool であるため、`user-agent-assets/skills/project-doc-bootstrap/templates/python/tools/` と `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff/` を正本にした

この分離により、review 運用で共有される runtime と、生成先 project にコピーされる language-specific tool の責務境界を一致させた。

### 3. C# 検証前提の固定

`net9.0` の test runner は、SDK の存在だけではなく system の `dotnet` が `Microsoft.NETCore.App 9.x` runtime を列挙できることを前提とする。今回の追加実装では、repo-local workaround を残さず system `dotnet` に一本化し、その prerequisites を恒久ドキュメントへ明記した。

## 実装内容

### 1. obsolete asset の削除

- root / template `instructions/` を削除した
- root / template `scripts/sync_agent_skills.*` を削除した
- repo-local `.github/skills/` / `.claude/skills/` を削除した
- `python-project-template/` と `csharp-project-template/` を削除した

これにより、user-level skill 正本と bootstrap template 正本の二重管理を解消した。

### 2. runtime / bootstrap への再配置

- AgentCliTmux C# source を `user-agent-assets/runtime/agent-cli-tmux/csharp/AgentCliTmux/` へ移した
- macOS native payload を `user-agent-assets/runtime/agent-cli-tmux/csharp/osx-arm64/AgentCliTmux` として保持した
- Python ExtractGitDiff を `user-agent-assets/skills/project-doc-bootstrap/templates/python/tools/extract_git_diff.py` へ移した
- C# ExtractGitDiff を `user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff/` へ移した
- wrapper、tests、docs からの参照先を新配置へ更新した

### 3. C# test 実行基盤の整理

- 公式 installer により system `dotnet` に `.NET 9` SDK / runtime が見える状態を確認した
- `dotnet run --project tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj` が system `dotnet` のみで成功することを確認した
- 一時対応として使っていた repo-local `.dotnet9` を削除した
- 以後の repo validation は system `dotnet` を前提とする方針に揃えた

## 互換性と影響

- 旧 `python-project-template/` / `csharp-project-template/` パスを前提にした repo 内参照は無効になった
- C# validation は `.NET 9` SDK / runtime を持つ system `dotnet` が必須になった
- runtime helper と bootstrap tool の参照先が固定されたため、今後は repo 内で同一ツールを別経路へ重複配置しない

今回の変更は repo の責務整理に伴う破壊的変更だが、意図した移行完了状態であり、旧経路の後方互換レイヤーは追加していない。

## 検証結果

### 実行確認

- `python3 -m pytest tests/test_agent_cli_tmux.py tests/test_extract_git_diff.py`
  - 16 tests passed
- `dotnet run --project tests/AgentCliTmux.Tests/AgentCliTmux.Tests.csproj`
  - 13/13 tests passed
- `dotnet build user-agent-assets/skills/project-doc-bootstrap/templates/csharp/tools/ExtractGitDiff/ExtractGitDiff.csproj`
  - succeeded
- repo-local `.dotnet9` 削除後に同じ C# test runner が再度成功

### 文書反映確認

- `docs/tests/README.md` に system `dotnet` + `.NET 9` prerequisite を追記した
- `docs/rules/development_workflow.md` に C# validation の前提と確認コマンドを追記した

## 未解決事項

- Windows 向け native payload の恒久運用は follow-up issue で継続管理する
- Phase 6 の archive / history / merged status 反映は別途完了処理で実施する