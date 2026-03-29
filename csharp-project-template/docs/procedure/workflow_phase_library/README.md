# workflow_phase_library

## 目的

- workflow 本体を短く保ち、Phase ごとの詳細作業を分離する。
- `spec-change` と `bugfix` をはじめ、共通部分を `common/` へ集約して保守性を上げる。

## 構成

- `common/`: 複数 workflow で共通の Phase 手順
- `spec_change/`: 仕様変更の固有観点
- `new_feature/`: 新機能追加の固有観点
- `bugfix/`: 不具合修正の固有観点
- `issue_resolution/`: 課題解決の固有観点
- `refactoring/`: リファクタリングの固有観点

## 読み方

1. まず対象 workflow の `*_workflow.md` を開く
2. 各 Phase の「共通手順」と「固有観点」を対応するファイルで確認する
3. レビュー観点の詳細は `docs/procedure/review_checkpoints.md` を参照する
