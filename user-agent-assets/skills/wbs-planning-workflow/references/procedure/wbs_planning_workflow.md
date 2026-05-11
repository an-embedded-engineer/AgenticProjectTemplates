# WBS planning workflow

## 適用条件

- 大規模変更を複数の work package へ分解するタスク
- 実装や恒久修正そのものは対象外。分解後に通常 workflow へ引き継ぐ

## 成果物

- 成果物ディレクトリ: `docs/design_analysis/wbs/<yyyymmdd>_<topic>/`
- 必須ファイル: `meta.md`, `wbs.md`, `report.md`
- ブランチ例: `wbs/<topic>-<yyyymmdd>`

## Phase 一覧

| Phase | 目的 | 主な出力 |
|---|---|---|
| 0 | 依頼整理 | 背景、目的、完了条件、非対象 |
| 1 | ブランチ・meta 初期化 | WBS 専用ブランチ、`meta.md` |
| 2 | 影響範囲と依存整理 | コンポーネント、依存関係、リスク |
| 3 | work package 分解 | `wbs.md` |
| 4 | 完了処理 | `report.md`、次 workflow 提案 |

## Phase 詳細

### Phase 0: 依頼整理

- 変更の背景、目的、完了条件、非対象を固定する
- 既存 todo / issue / research report / ADR との関係を整理する
- 分解後に実装へ進む前提か、調査継続が必要かを明確にする

### Phase 1: ブランチ・meta 初期化

- WBS 専用ブランチを作成する
- `docs/design_analysis/wbs/<yyyymmdd>_<topic>/` を作成する
- `meta.md` には最低限次を記載する
  - `title`
  - `created_date`
  - `category: wbs`
  - `components`
  - `status`
  - `related_commits`
  - `source_refs`

### Phase 2: 影響範囲と依存整理

- 影響コンポーネント、外部境界、データ、UI、docs、test を列挙する
- cross-cutting な設計判断、ADR 候補、共通制約を整理する
- 実施順序に影響する依存関係を明確にする
- 1 workflow に収まらない範囲を分割候補として記録する

### Phase 3: work package 分解

`wbs.md` には最低限、次の列を持つ表を置く。

| 列 | 内容 |
|---|---|
| `work_package_id` | `WP-001` 形式 |
| `source_id` | 元の todo / issue / report があれば記載 |
| `recommended_workflow` | `spec-change` / `new-feature` / `bugfix` / `issue-resolution` / `refactoring` / `documentation` |
| `depends_on` | 先行 work package |
| `purpose` | この work package の目的 |
| `completion_criteria` | 完了条件 |
| `main_targets` | 主な変更対象 |
| `docs_targets` | docs 更新先 |
| `verification_points` | 検証観点 |
| `deferred_or_follow_up` | 後続へ送る範囲 |

分解時の基準:

- 1 work package は、通常 workflow 1 回で設計、実装、検証、文書反映、完了処理まで終えられる粒度にする
- workflow 種別が混ざる場合は work package を分ける
- 依存がある場合は、先行 package の完了条件を後続 package の前提条件として明記する
- 共通設計判断は個別 package に埋め込まず、WBS topic の上位判断として残す
- `recommended_workflow` が `documentation` の work package では、動作確認を必須にせず、`diff.zip` を作成しない。完了条件と検証観点には、リンク、索引、archive、history、重複記述の整合確認を含める

### Phase 4: 完了処理

- `report.md` に次をまとめる
  - 分解結果の要約
  - 推奨実施順序
  - 最初に着手すべき work package
  - 別 todo / issue として起票すべき項目
  - ADR 候補
  - 残リスク
- `meta.md` の `status` と `related_commits` を更新する
- ユーザへ分解結果を報告し、次に着手する work package の承認を待つ

## 完了条件

- `wbs.md` の各 work package が通常 workflow へ引き継げる粒度になっている
- 依存順序と最初に着手する work package が明確である
- docs 更新先と検証観点が work package ごとに定義されている
- 実装に進む前の未解決判断が `report.md` に残っている
