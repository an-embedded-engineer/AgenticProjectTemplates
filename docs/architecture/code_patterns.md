# コードパターン

## 横展開パターン

- 片方のテンプレートに追加した概念は、もう片方のテンプレートへも必要性を評価する
- 実装言語はテンプレートに合わせる
  - Python bootstrap template: Python docs / rules
  - C# bootstrap template: .NET docs / rules
- 文書構造と workflow 名は、意図的な差異がない限り両テンプレートで揃える

## ツール配置

- root review 補助: `scripts/`
- shared runtime helper / native payload: `user-agent-assets/runtime/`
- project へ配布する language-specific tool: `user-agent-assets/skills/project-doc-bootstrap/templates/<language>/tools/`

## エラーハンドリング

- CLI tool は失敗理由を stderr に出し、非 0 exit code を返す
- dry-run は外部副作用を起こさず、実行予定コマンドを stdout に出す
- 仕様不一致は暗黙フォールバックではなく明示エラーにする

## テストパターン

- dry-run 可能な CLI は、外部プロセスや tmux session を作らず stdout / stderr / exit code を検証する
- C# test runner は外部 NuGet 依存を増やさず、`dotnet run --project tests/...` で実行できる形を優先する
- Python pytest は repo root からの相対パスで実行できることを確認する
