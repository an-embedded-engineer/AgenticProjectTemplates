---
name: user-agent-assets-update-workflow
description: AgenticProjectTemplates project-local 専用。user-agent-assets 配下にある user-level skills、review/orchestration workflow、runtime、installer、project-doc-bootstrap templates を更新し、レビュー、dry-run、tmp 仮インストール、実インストール、merge 承認まで進める手順。
---

# user-agent-assets-update-workflow

## いつ使う

- `user-agent-assets/skills/` 配下の workflow / review / orchestration / bootstrap skill を追加・更新する時
- `user-agent-assets/install/`、`user-agent-assets/bin/`、`user-agent-assets/runtime/`、`user-agent-assets/shared/` を変更する時
- user-level assets の配布結果を `tmp/` 仮インストールと実インストールで確認する必要がある時
- AgenticProjectTemplates 自身の project-local 作業として user-agent-assets 更新を branch から merge まで管理する時

## 使わない時

- docs だけを更新する時は `documentation-workflow` を使う
- bootstrap 先プロジェクトのアプリ機能を変更する時は通常の core workflow を使う
- 大規模変更を先に分解するだけなら `wbs-planning-workflow` を使う

## 実行ルール（索引）

- 手順本体: `references/procedure/user_agent_assets_update_workflow.md`
- 仮インストール検証: `scripts/validate_temp_install.py`
- skill 作成・更新: `skill-creator`
- レビュー委任: `claude-review-automation` または `copilot-review-automation`

## 禁止事項

- ユーザ承認なしに実インストールしてはならない
- ユーザ承認なしに branch merge してはならない
- 仮インストール確認を省略して実インストールへ進んではならない
- user home 配下へ手作業で個別コピーしてはならない。必ず `user-agent-assets/install/` の installer を使う
- review 文書（`*_review.md`）を自分で作成してはならない

## 最低限の必須チェック

1. 専用 branch を作成する
2. 変更内容、対象 runtime、配布影響範囲を整理する
3. 実装前に Claude または Copilot CLI へ方針レビューを依頼する
4. user-agent-assets、関連 docs、検証 script を更新する
5. 実装後に Claude または Copilot CLI へ実装レビューを依頼し、未解決指摘 0 件まで回す
6. installer の dry-run を実行する
7. `tmp/` へ仮インストールし、展開結果を検証する
8. ユーザ確認後に実インストールする
9. ユーザ承認後に既定ブランチへ merge する
