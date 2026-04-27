# テスト戦略

## テスト原則

- テンプレート利用者へ配布される tool / script は dry-run で副作用なしに検証できるようにする
- 言語テンプレートごとの標準ツールチェーンを使う
- 外部 CLI (`tmux`, `codex`, `claude`) が必要な処理は、dry-run でコマンド構築を検証する

## テストレベル

- 文書変更: リンク、プレースホルダ、テンプレート間整合を確認する
- CLI unit 相当: dry-run の stdout / stderr / exit code を確認する
- build: C# tool は `dotnet build`、Python script は `py_compile` を実行する

## テストデータ管理

- 一時ファイルは OS の temporary directory に作成し、テスト終了時に削除する
- テンプレート内へ生成物を残さない

## モック/フィクスチャ戦略

- tmux session は作らず、dry-run 出力で tmux コマンド列を検証する
- 外部 package 依存を増やさず、テンプレート適用直後でも検証できる構成を優先する
