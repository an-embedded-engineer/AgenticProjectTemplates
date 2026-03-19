# 開発・実行ルール

## 環境

- .NET 8.0+
- IDE: Visual Studio / Visual Studio Code / Rider

## セットアップ

```bash
dotnet restore
```

## ビルド

```bash
# 通常ビルド
dotnet build

# 警告をエラーとして扱う（完了条件）
dotnet build --warnaserrors

# Release ビルド
dotnet build -c Release
```

## アプリケーション実行

<!-- TODO: プロジェクト固有の実行コマンドを記述する -->
```bash
# 例: メインアプリケーション起動
dotnet run --project src/App

# 例: Release モードで実行
dotnet run --project src/App -c Release
```

## テスト

```bash
# 全テスト実行
dotnet test

# 詳細出力で全テスト実行
dotnet test -v normal

# 特定のテストプロジェクトを実行
dotnet test tests/App.Tests

# 特定のテストケースを実行
dotnet test --filter "FullyQualifiedName~TestClassName.TestMethodName"

# 特定カテゴリのテストを実行
dotnet test --filter "Category=Unit"

# 失敗したテストのみ表示
dotnet test --logger "console;verbosity=detailed" -- RunConfiguration.TreatNoTestsAsError=true

# 最初の失敗で停止
dotnet test -- RunConfiguration.MaxCpuCount=1
```

## 統合テスト

<!-- TODO: プロジェクト固有の統合テストコマンドを記述する -->
```bash
# 例: 統合テストプロジェクト実行
dotnet test tests/App.IntegrationTests
```

## 静的解析（必須）

```bash
# ビルド時警告チェック — 完了条件: 警告・エラー 0 件
dotnet build --warnaserrors

# .NET Analyzer（コード品質・スタイル）
dotnet format --verify-no-changes

# フォーマット適用
dotnet format
```
