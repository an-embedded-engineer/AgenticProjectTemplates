# シンボリックリンク移行ガイド（Draft）

## 目的

共通インストラクションと skills を master 一元管理し、Agent ごとの参照先を統一する。

## 対象

- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `.claude/skills/*/SKILL.md`
- `.github/skills/*/SKILL.md`
- `~/.codex/skills/*/SKILL.md`
- resources を持つ structured skill の `agents/` `references/` `scripts/` `assets/`

## 運用方針

- legacy workflow skill は `SKILL.master.md` を master として扱う。
- resources を持つ structured skill は `SKILL.md` を起点に skill ディレクトリ全体を同期する。
- プロジェクト内 Agent（`.claude` / `.github`）は symlink を使う。
- `~/.codex/skills` は symlink を使わず、skill 実体をコピーする。
- 標準運用は `scripts/sync_agent_skills.sh` を実行する。

## 事前準備

1. master ファイルを作成する
2. 既存ファイルをバックアップする
3. 新規 skill のディレクトリを作成する

```bash
# 新規 skill ディレクトリ作成（例: bugfix-workflow）
mkdir -p .github/skills/bugfix-workflow
mkdir -p .claude/skills/bugfix-workflow
mkdir -p ~/.codex/skills/bugfix-workflow
```

## 例: 共通インストラクション

```bash
mv AGENTS.md AGENTS.md.bak
mv CLAUDE.md CLAUDE.md.bak
mv .github/copilot-instructions.md .github/copilot-instructions.md.bak

ln -s instructions/agent_common_master.md AGENTS.md
ln -s instructions/agent_common_master.md CLAUDE.md
ln -s ../instructions/agent_common_master.md .github/copilot-instructions.md
```

## 例: skills 同期（推奨）

```bash
./scripts/sync_agent_skills.sh
```

## 例: skills 手動同期

```bash
# legacy workflow skill の例: .claude / .github は SKILL.master.md への symlink
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/SKILL.master.md .claude/skills/{{SKILL_NAME}}/SKILL.md
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/SKILL.master.md .github/skills/{{SKILL_NAME}}/SKILL.md

# structured skill の例: .claude / .github は SKILL.md と resource ディレクトリを同期
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/SKILL.md .claude/skills/{{SKILL_NAME}}/SKILL.md
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/references .claude/skills/{{SKILL_NAME}}/references
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/scripts .claude/skills/{{SKILL_NAME}}/scripts
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/agents .claude/skills/{{SKILL_NAME}}/agents

ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/SKILL.md .github/skills/{{SKILL_NAME}}/SKILL.md
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/references .github/skills/{{SKILL_NAME}}/references
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/scripts .github/skills/{{SKILL_NAME}}/scripts
ln -sfn ../../../instructions/skills/{{SKILL_NAME}}/agents .github/skills/{{SKILL_NAME}}/agents

# legacy workflow skill の例: ~/.codex/skills は SKILL.master.md をコピー
cp instructions/skills/{{SKILL_NAME}}/SKILL.master.md ~/.codex/skills/{{SKILL_NAME}}/SKILL.md

# structured skill の例: ~/.codex/skills は skill ディレクトリ全体をコピー
cp -R instructions/skills/{{SKILL_NAME}}/. ~/.codex/skills/{{SKILL_NAME}}/
```

## 検証

```bash
# 共通インストラクション
ls -l AGENTS.md CLAUDE.md .github/copilot-instructions.md

# .claude / .github skills は symlink
ls -l .claude/skills/{{SKILL_NAME}}/SKILL.md
ls -l .github/skills/{{SKILL_NAME}}/SKILL.md
ls -l .claude/skills/{{SKILL_NAME}}
ls -l .github/skills/{{SKILL_NAME}}

# ~/.codex/skills は symlink ではないことを確認
ls -l ~/.codex/skills/{{SKILL_NAME}}
test ! -L ~/.codex/skills/{{SKILL_NAME}}/SKILL.md
```

## ロールバック

```bash
# 共通インストラクションの復元
rm AGENTS.md CLAUDE.md .github/copilot-instructions.md
mv AGENTS.md.bak AGENTS.md
mv CLAUDE.md.bak CLAUDE.md
mv .github/copilot-instructions.md.bak .github/copilot-instructions.md

# .claude / .github の skill 復元
rm .claude/skills/{{SKILL_NAME}}/SKILL.md
rm .github/skills/{{SKILL_NAME}}/SKILL.md
mv .claude/skills/{{SKILL_NAME}}/SKILL.md.bak .claude/skills/{{SKILL_NAME}}/SKILL.md
mv .github/skills/{{SKILL_NAME}}/SKILL.md.bak .github/skills/{{SKILL_NAME}}/SKILL.md

# ~/.codex/skills は同期スクリプト退避先から復元
# 例: BACKUP_TAG=20260216_120000_skill_sync
BACKUP_TAG=<backup_tag>
cp -R ~/.codex/skills/_obsoleted/$BACKUP_TAG/{{SKILL_NAME}}/. ~/.codex/skills/{{SKILL_NAME}}/
```
