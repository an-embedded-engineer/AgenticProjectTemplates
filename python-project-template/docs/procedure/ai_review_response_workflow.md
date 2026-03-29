# AIレビュー対応ワークフロー（改訂案）

## 適用条件

- 設計書/実装レビュー結果を反映して整合性を確保したい場合

## 概要フロー

1. 入力整理（対象文書、対象コード、レビュー結果）
2. 工程分類（`plan` / `design` / `impl`）
3. 指摘分類（重大度・優先度・根拠）
4. 反映（対象工程の文書 + レビュー文書）
5. 未解決事項の明確化
6. 全指摘のステータス確定

## 詳細観点

- 詳細チェックリストは `docs/procedure/review_checkpoints.md` を参照する
- `ai-review-response-workflow` の SKILL には索引のみを記載し、観点詳細はこのファイル群へ委譲する

## 設計・実装レビューで必ず確認する原則

- 類似ロジックがある場合は、重複追加ではなく抽象化・共通化を優先しているか確認する
- 新規関数の配置先が適切で、呼び出し箇所に近いだけの場当たり配置になっていないか確認する
- モジュール直下のグローバル関数を原則増やさず、責務に応じたクラス/メソッドへ配置されているか確認する
- フレームワーク契約や既存公開 API 等の明示要件で例外を採る場合、理由と境界が残っているか確認する
- `getattr` / `setattr` / `Any` / `Dict` は原則避け、抽象化・共通化・汎用化のための局所利用に限られているか確認する
- 明示指示または外部契約がない限り、後方互換レイヤーや旧経路を残していないか確認する
- プロジェクト内で閉じる仕様不一致を不要なフォールバックで吸収せず、例外や明示的エラーハンドリングで顕在化しているか確認する

## 出力ファイルの配置

- 原則: レビュー結果は `docs/design_analysis/<category>/<yyyymmdd>_<topic>/review/` 配下に配置する
- 例外: 特定コンポーネントの恒久ドキュメントレビューは、対象ディレクトリ直下の `review/` に配置してよい
- ファイル名:
  - `<topic>_plan_review.md`
  - `<topic>_design_review.md`
  - `<topic>_impl_review.md`
  - `<topic>_docs_review.md`（仕様変更 Phase 5 の文書レビュー）
  - `<topic>_feature_docs_review.md`（新機能追加 Phase 5 の文書レビュー）
  - `<topic>_bugfix_docs_review.md`（不具合修正 Phase 5 の文書レビュー）
  - `<topic>_issue_resolution_docs_review.md`（課題解決 Phase 5 の文書レビュー）
  - `<topic>_refactoring_docs_review.md`（リファクタリング Phase 5 の文書レビュー）
- 例:
  - `docs/design_analysis/spec_change/20260329_api_contract_update/review/api_contract_update_plan_review.md`
  - `docs/design_analysis/spec_change/20260329_api_contract_update/review/api_contract_update_design_review.md`
  - `docs/design_analysis/spec_change/20260329_api_contract_update/review/api_contract_update_impl_review.md`
  - `docs/design_analysis/new_feature/20260329_bulk_import/review/bulk_import_feature_docs_review.md`
  - `docs/components/example_component/review/component_interface_design_review.md`

## レビュー結果ドキュメント構成（テンプレート）

```markdown
# <対象>設計レビュー

**レビュー日**: YYYY-MM-DD
**対象ドキュメント**: <パス>
**対象実装**: <パス>

---

## 概要

<レビュー目的と対象の説明>

---

## 1. 齟齬・不整合

### 1.1 <項目名>

**ドキュメント記載**: ...
**実装**: ...
**差異**: ...
**推奨対応**: ...
**対応**: <対応内容/更新ファイル/追加説明>

---

## 2. ドキュメント不足

### 2.1 <項目名>

**不足**: ...
**推奨対応**: ...
**対応**: <対応内容>

---

## 3. 改善提案

### 3.1 <項目名>

**推奨対応**: ...
**対応**: <対応内容>（または未対応理由）

---

## 4. 整合性確認済み項目

| 項目 | 確認結果 |
|------|----------|
| ... | ✓ 整合 |

---

## 5. 対応優先度

| 優先度 | 項目 | 理由 |
|--------|------|------|
| 高 | ... | ... |
| 中 | ... | ... |
| 低 | ... | ... |

---

## 6. 結論

<総括と残課題>
```

## 対応記載テンプレート

レビュードキュメントへの追記例:

```
**対応**: <対応内容/更新ファイル/追加説明>
```

未対応の場合は理由と次アクションを記載する。

## 成果物

- 対象工程文書更新（`plan` / `design` / `impl`）
- レビュー文書更新（全指摘に `対応` または `未対応理由` を付与）
- 必要に応じて `meta.md` の `plan_status` / `design_status` / `impl_status` を更新

## 完了条件

- レビュー項目に未分類・未対応が残っていない
- 対象工程文書とレビュー書の記述が一致している
- 必要な追加タスク（別 issue / 別設計）が切り出されている
