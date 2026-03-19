# アーキテクチャ概要

## コアコンポーネント

<!-- TODO: 各コンポーネントの概要と責務を記述する -->

### コンポーネント1 (`src/Xxx/`)

<!-- TODO: 概要、主要クラス、責務を記述する -->

### コンポーネント2 (`src/Yyy/`)

<!-- TODO: 概要、主要クラス、責務を記述する -->

## 基本フロー

<!-- TODO: システムの主要なデータフロー/処理フローを記述する -->
<!-- 例:
1. リクエスト受信
2. DI によるサービス解決
3. ビジネスロジック実行
4. レスポンス返却
-->

## 主要ファイルリファレンス

<!-- TODO: エントリポイントや主要ファイルをリストする -->
<!-- 例:
- エントリポイント: `src/App/Program.cs`
- 設定: `src/App/appsettings.json`
- DI 構成: `src/App/Startup.cs` or `Program.cs`
-->

## ソリューション構成

<!-- TODO: ソリューション内のプロジェクト構成を記述する -->
<!-- 例:
```
Solution.sln
├── src/
│   ├── App/            — エントリポイント・DI構成
│   ├── App.Core/       — ドメインモデル・ビジネスロジック
│   └── App.Infra/      — インフラ層（DB・外部API）
└── tests/
    ├── App.Tests/      — ユニットテスト
    └── App.IntegrationTests/ — 統合テスト
```
-->

## ドキュメント構成

```
docs/
├── architecture/     — アーキテクチャ概要・パターン・注意点
├── components/       — コンポーネント別の設計文書
├── design_analysis/  — 設計分析・レビュー文書
├── procedure/        — ワークフロー手順書
├── rules/            — 開発ルール
├── tests/            — テスト方針・構成
├── todo/             — 追跡項目（spec-change / new-feature / refactoring）
├── issues/           — 追跡項目（bugfix / issue-resolution）
└── history/          — 実装履歴
```

## 設計文書リファレンス

<!-- TODO: docs/components/ の各コンポーネントへのリンクを記述する -->
<!-- 例:
- コンポーネントA: `docs/components/component_a/README.md`
- コンポーネントB: `docs/components/component_b/README.md`
-->
