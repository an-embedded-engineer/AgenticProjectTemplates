# Python Template Target Docs

## 先に確認する信号

- 依存関係と実行基盤: `pyproject.toml`, `requirements*.txt`, `setup.cfg`, `tox.ini`, `Dockerfile*`
- 実行コマンド: `README*`, `Makefile`, `justfile`, `scripts/`, `.github/workflows/`
- テスト構成: `tests/`, `pytest.ini`, `conftest.py`, CI 設定
- アーキテクチャ: `src/`, エントリポイント, 主要パッケージ, 設定モジュール
- 既存文書: ルート `README.md`, `docs/`, ADR, 運用メモ

## 優先度: 高

- `instructions/agent_common_master.md`
  - 根拠: プロジェクト名, 実際の docs パス, 開発ルール
  - 作業: `{{PROJECT_NAME}}` を正式名称へ置換する。`instructions/skills/**/*.md` 内の `{{PROJECT_NAME}}` / `{{PROJECT_NAME_LOWER}}` も同時に置換する

- `docs/rules/project_overview.md`
  - 根拠: ルート `README.md`, `src/` 配下, 主要ディレクトリ構成
  - 作業: 目的、主要ディレクトリ、コンポーネント文書リンクを書く

- `docs/architecture/overview.md`
  - 根拠: エントリポイント, 主要パッケージ, 処理フロー
  - 作業: 主要コンポーネント 2 から 3 件、基本フロー、主要ファイルを具体名で書く

- `docs/rules/development_workflow.md`
  - 根拠: 実行コマンド, テストコマンド, CI, 補助スクリプト
  - 作業: アプリ起動と統合テストの例を実プロジェクトのコマンドへ差し替える

- `docs/tests/README.md`
  - 根拠: `tests/` 配下, pytest マーカー, `conftest.py`
  - 作業: テスト構成、カテゴリ、代表的な実行方法を実体に合わせて書く

- `docs/tests/strategy.md`
  - 根拠: 既存テスト, CI, カバレッジ設定, 品質基準
  - 作業: テスト原則、テストレベル、カバレッジ目標、テストデータ戦略を書く

## 優先度: 中

- `docs/architecture/code_patterns.md`
  - 根拠: import スタイル, データモデル実装, 例外クラス, テストコード
  - 作業: 現在のコードベースで繰り返し出てくるパターンだけを残す

- `docs/architecture/common_pitfalls.md`
  - 根拠: 起動手順, 設定ファイル, import path, 既存バグ傾向
  - 作業: プロジェクト固有の落とし穴を 2 から 5 件追加する

- `docs/components/<component>/README.md`
  - 根拠: 責務境界が明確な主要パッケージ, サービス, サブシステム
  - 作業: `_example_component` を複製または改名し、目的、主要要素、依存関係、設計パターンを書く

- `docs/components/<component>/basic_design.md`
  - 根拠: 主要クラス, 依存関係, 責務分担
  - 作業: クラス構成と依存方向を簡潔に書く

- `docs/components/<component>/detail_design.md`
  - 根拠: 状態遷移, 呼び出し順, 例外処理, イベント処理
  - 作業: 実装詳細をコード構造に沿って書く

- `docs/components/<component>/interface_spec.md`
  - 根拠: 公開 API, 主要メソッド, CLI 引数, ハンドラ境界
  - 作業: 外部から見えるインターフェースだけを書く

- `docs/components/<component>/issues.md`
  - 根拠: TODO コメント, 既存 issue, FIXME, テスト不足箇所
  - 作業: 事実ベースの既知課題のみを書く。根拠が弱いなら未整理である旨を書く

## 優先度: 低

- `docs/history/README.md`
  - 根拠: `git log`, 既存リリースノート, 実装履歴文書
  - 作業: 履歴文書が未整備なら運用方針だけ書き、架空の履歴は追加しない

## 通常はそのままでよいファイル

- `docs/design_analysis/README.md`
- `docs/todo/README.md`
- `docs/issues/README.md`
- `docs/procedure/*`
- `docs/rules/language_rules.md`
- `docs/rules/coding_rules.md`

上記はプロジェクトごとの差分が少ない。ID 命名や workflow の運用が明確に異なる場合だけ更新する。

## 注意事項

- `instructions/skills/**/*.md` を置換対象に含めてよい
- `instructions/symlink_migration_guide.md` の `{{SKILL_NAME}}` は skill 名の利用例なので置換しない
- `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` が symlink の場合、実体は `instructions/` 側にある。重複して個別編集しない

## プロジェクト形状ごとの補助観点

- Web API
  - ルータ, サービス, リポジトリ, 設定, DB 接続の流れを書く
- CLI / バッチ
  - エントリポイント, サブコマンド, 入出力ファイル, ジョブ実行順を書く
- ライブラリ
  - 公開 API, extension point, 利用例, 互換性制約を書く
