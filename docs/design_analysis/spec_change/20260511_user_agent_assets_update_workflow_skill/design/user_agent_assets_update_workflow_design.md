# user-agent-assets-update-workflow skill 設計

## 背景

`user-agent-assets/` は user-level skills、review/orchestration workflow、installer、runtime、project-doc-bootstrap templates を配布する正本である。更新後は dry-run だけでなく、`tmp/` への仮インストールと実 user home へのインストール確認が必要になる。

既存の `documentation-workflow` は docs-only 変更専用で、実インストールや installer / runtime / script 変更を扱わない。そのため、user-agent-assets 更新専用の project-local workflow を追加する。

この workflow は AgenticProjectTemplates だけで使う保守手順であり、bootstrap 先プロジェクトへ配布する必要はない。正本は `project-skills/user-agent-assets-update-workflow/` に置き、`user-agent-assets/install/` の配布対象には含めない。

通常の project-local skill discovery に合わせるため、`project-skills/` から `.github/skills/`、`.claude/skills/`、`.codex/skills/` へ同期する `scripts/sync_project_skills.*` を追加する。同期先は生成物として `.gitignore` で除外し、正本は `project-skills/` に限定する。

## 方針

- 作業は専用 branch から開始する
- 変更方針と影響範囲を整理し、実装前に Claude または Copilot CLI のレビューを受ける
- skill / installer / runtime / template / docs を更新し、実装後にもレビューを受ける
- installer dry-run と `tmp/` 仮インストールを実施する
- 実インストールはユーザ確認後にだけ実行する
- merge はユーザ承認後にだけ実行する

## 仮インストール検証

`project-skills/user-agent-assets-update-workflow/scripts/validate_temp_install.py` を同梱し、`HOME` を repo 内の `tmp/user-agent-assets-install-check/home` に差し替えて installer を実行する。

検証 script は次を確認する。

- source の skill set と各 target の skill set が一致する
- source skill のファイルが target に展開されている
- `--exact-skill` 指定された skill は source と完全一致する
- project-local skill が user-level install 対象に含まれていない
- `.agentic-project-templates/` の helper runtime が展開されている
- shell wrapper に実行権限がある

## STOP ゲート

| ゲート | 承認者 | 条件 |
|---|---|---|
| 実インストール前 | ユーザ | dry-run と tmp 仮インストールが成功している |
| merge 前 | ユーザ | 実インストール結果と change_report が完了している |

## WBS 連携

user-level の `wbs-planning-workflow` には `user-agent-assets-update` を追加しない。この workflow は AgenticProjectTemplates project-local 専用であり、配布先プロジェクトの WBS 候補に出すと不要な選択肢になるためである。
