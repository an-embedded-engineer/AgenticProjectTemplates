# Phase 1 共通: ブランチ作成・meta 初期化

## 実施内容

1. `master` を最新化して、workflow 専用ブランチを作成する
2. 対応する `docs/design_analysis/<category>/<yyyymmdd>_<topic>/` を作成する
3. `meta.md` を作成し、以下を最低限記録する
   - `title`
   - `created_date`
   - `category`
   - `components`
   - `status`
   - `plan_status`
   - `design_status`
   - `impl_status`
   - `related_commits`
4. 作業ブランチ名を `meta.md` または `plan.md` に残す
5. Phase 1 の成果を 1 コミットで残す

## 完了条件

- 専用ブランチで作業している
- 課題ディレクトリと `meta.md` が作成済み
- Phase 1 成果がコミットされている

## 進行制約

- Phase 1 完了前に Phase 2 へ進まない
