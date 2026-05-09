---
title: "project-level instruction 整理と root workflow docs 削減"
created_date: "2026-05-09"
category: issue_resolution
components:
  - instructions
  - docs
  - scripts
  - user-agent-assets
status: in_review
plan_status: N/A
design_status: N/A
impl_status: done
related_issues:
  - docs/issues/cross/issues.md#c-2026-009-bootstrap-後の-agent-instructions-へ-project-固有説明を補助
related_commits: []
---

# メタ情報

## 目的

project-level `agent_common_master.md` の導入文から sync source 自体の説明ノイズを除去し、root に残っていた workflow 手順書と skill source の重複配置を削減する。

## スコープ

- root `instructions/agent_common_master.md` の導入文見直し
- root `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` の再同期
- root `docs/procedure/` と `scripts/rebuild_user_agent_skills.py` の削除
- root docs の参照先を user-level skill / `references/procedure/` 前提へ更新
- template 側改善は `C-2026-009` へ分離

## レビュー依頼時の前提

- template 側 `user-agent-assets/skills/project-doc-bootstrap/templates/*/instructions/agent_common_master.md` は、この変更では意図的に変更していない
- template 側の project 固有説明補助は follow-up issue `C-2026-009` で扱う