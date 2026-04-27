# 調査・分析ワークフロー

## 適用条件

- 実装・仕様変更・不具合修正に入る前に、現状把握、論点整理、根拠収集、選択肢比較を行うタスク
- 既存コード、既存文書、既存レビューの整合性を調査し、次に取るべき workflow を判断したいタスク
- 実装や恒久修正自体が目的になった場合は、対応する workflow へ切り替える

## 起票・成果物

- 成果物ディレクトリ: `docs/design_analysis/research_analysis/<yyyymmdd>_<topic>/`
- 必須ファイル: `meta.md`, `report.md`
- 標準レビュー文書: `<topic>_report_review.md`
- 必要に応じて `report_*.md` の分割や `review/` ディレクトリ利用を許容する
- ブランチ例: `research/<topic>-<yyyymmdd>`

## 役割

- 調査担当 Agent
  - ブランチを作成し、ソース/ドキュメント調査と `report.md` 更新を担当する
- レビュー担当 Agent
  - 調査結果の妥当性、根拠、考慮漏れ、実装整合性を確認し、レビュー文書を作成する
- 指揮者
  - ユーザまたは指揮担当 Agent とし、レビュー依頼、レビュー完了通知、次 workflow への移行判断を行う

## Phase 一覧

| Phase | 目的 | 主な出力 |
|------|------|----------|
| 0 | 依頼整理 | 調査目的、観点、非対象、期待成果物の固定 |
| 1 | ブランチ・meta 初期化 | 調査専用ブランチ、`meta.md` |
| 2 | 調査・分析・レポート作成 | `report.md` |
| 3 | レビュー依頼・レビュー実施 | `<topic>_report_review.md` |
| 4 | 指摘対応ループ | 更新済み `report.md` / `meta.md` |
| 5 | 完了処理 | 完了通知、次 workflow 提案 |

## Phase 詳細

### Phase 0: 依頼整理

- ユーザ依頼を、調査対象、確認観点、除外範囲、期待する意思決定に分解する
- 既存 issue / todo / 設計文書 / レビュー文書との関係を整理する
- 実装を開始しないこと、結論が暫定か最終かを明確にする

### Phase 1: ブランチ・meta 初期化

- 調査担当 Agent が専用ブランチを作成する
- `docs/design_analysis/research_analysis/<yyyymmdd>_<topic>/` を作成する
- `meta.md` を作成し、最低限次を記載する
  - `title`
  - `created_date`
  - `category: research_analysis`
  - `components`
  - `status: draft`
  - `related_commits`
  - `source_design_path: docs/design_analysis/research_analysis/<yyyymmdd>_<topic>/report.md`

### Phase 2: 調査・分析・レポート作成

- ソースコード、既存設計書、issue、review 文書、履歴を読み、根拠を収集する
- `report.md` には最低限次を含める
  - 調査目的
  - 調査対象
  - 根拠ソース
  - 現状整理
  - 論点と選択肢
  - 推奨方針
  - リスクと未解決事項
- 根拠なしの推測は「仮説」と明記する
- 調査担当 Agent はレビュー依頼前に 1 コミット残す

### Phase 3: レビュー依頼・レビュー実施

- 指揮者はレビュー担当 Agent に `report.md` のレビューを依頼する
- 調査担当 Agent は `meta.md` の `status` を `in_review` に更新する
- レビュー担当 Agent は同ディレクトリに `<topic>_report_review.md` を作成する
- レビュー観点は最低限次を含める
  - 実装との整合性
  - 根拠の十分性
  - 考慮漏れの有無
  - 結論の飛躍や過剰一般化の有無
  - 次 workflow へ渡せる粒度になっているか
- レビュー担当 Agent はレビュー成果を 1 コミットで残し、指揮者へ通知する

### Phase 4: 指摘対応ループ

- 指揮者はレビュー完了を調査担当 Agent に通知する
- 調査担当 Agent は指摘を分類し、`report.md` と必要に応じて `meta.md` を更新する
- レビュー指摘が残る間は Phase 3 と Phase 4 を繰り返す
- 再レビュー時は既存レビュー文書へ追記し、ラウンド履歴を残す
- 重大な前提変更が出た場合は、指揮者へ再度スコープ確認を求める

### Phase 5: 完了処理

- ブランチ上でレビュー指摘が解消したら、`meta.md` の `status` を `merged` に更新する
- `related_commits` に各ラウンドのコミットを記録する
- ユーザへ次を報告する
  - 調査結論
  - 主要根拠
  - 未解決事項
  - 次に推奨する workflow
- 調査で実装タスクが確定した場合は、別 workflow の Phase 0 へ引き継ぐ

## 主なレビュー観点

- 結論がソースコードや既存文書の事実に支えられているか
- 調査範囲と非対象が明確で、結論の適用範囲が過不足ないか
- 実装制約、依存関係、既存設計との衝突が見落とされていないか
- 次の仕様変更/実装/修正へ渡すための前提が十分に整理されているか

## ユーザ承認が必要なタイミング

- Phase 0 のスコープ整理後
- Phase 2 の初回 `report.md` 作成後
- 各レビューラウンドで重大指摘が出た時
- Phase 5 で次 workflow へ移行する前

## コミット運用

- Phase 1 はブランチ作成と `meta.md` 初期化を 1 コミットで残す
- Phase 2 は初回 `report.md` を 1 コミットで残す
- Phase 3 はレビュー担当 Agent がレビュー文書追加を 1 コミットで残す
- Phase 4 は各対応ラウンドを 1 コミットで残す
- `related_commits` の形式: `- <commit_hash> : Phase <番号> <要約>`
