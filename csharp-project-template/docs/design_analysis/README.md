# 設計分析・レビュー文書 運用ガイド

## 目的

設計/実装/レビュー文書の配置・命名・更新ルールを統一する。

## ディレクトリ構成

```
docs/design_analysis/
├── spec_change/           — 仕様変更
├── new_feature/           — 新機能追加
├── fix_issues/            — 不具合修正
├── issue_resolution/      — 課題解決
├── refactoring/           — リファクタリング
└── research_analysis/     — 調査・分析
```

## 課題ディレクトリ命名

```
<category>/<YYYYMMDD>_<slug>/
```

例: `spec_change/20260315_update_api_contract/`

## 標準ファイル構成

```
<YYYYMMDD>_<slug>/
├── plan/
│   └── <topic>_plan.md
├── design/
│   └── <topic>_design.md
├── impl/
│   └── <topic>_impl.md
├── review/
│   ├── <topic>_plan_review.md
│   ├── <topic>_design_review.md
│   └── <topic>_impl_review.md
├── diff/
│   └── report.md
└── meta.md
```

## meta.md テンプレート

```yaml
---
title: "<課題タイトル>"
category: "<spec_change|new_feature|fix_issues|issue_resolution|refactoring|research_analysis>"
created: "<YYYY-MM-DD>"
plan_status: "<draft|in_review|approved|N/A>"
design_status: "<draft|in_review|approved|N/A>"
impl_status: "<not_started|in_progress|done|N/A>"
related_commits: []
---
```

## 運用ルール

1. 課題ディレクトリは日付プレフィックスで一意に識別する
2. `meta.md` のステータスは各 Phase 完了時に必ず更新する
3. レビュー文書は `review/` ディレクトリに配置する
4. ソース差分レポートは `diff/` ディレクトリに配置する
5. 調査・分析は `research_analysis/` に配置する（workflow Phase を伴わない）
