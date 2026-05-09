# Change History 2026

## 2026-05-09

### ユーザレベル Agent 資産化を main へ統合

- design_analysis: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/`
- source_branch: `feature/spec-user-level-agent-assets-20260508`
- merge_commit: `55075be`

Python / C# project 向けに分散していた Agent instructions、workflow skills、docs bootstrap assets を user-level 配布前提の `user-agent-assets/` へ集約した。あわせて runtime / bootstrap tool の責務を再配置し、旧 template ディレクトリと repo-local skill 資産を撤去した。

追加で、Copilot CLI の skill load error を引き起こしていた `copilot-review-automation` の YAML frontmatter を修正し、user root への再 install と実起動確認まで完了した。