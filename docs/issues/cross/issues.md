# Cross Issues

AgenticProjectTemplates 全体に関わる `bugfix` / `issue-resolution` の追跡項目を管理する。

## Open

### C-2026-001: review automation preflight 標準化

- status: `open`
- priority: `high`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `copilot-review-automation`
	- 関連 workflow 全般
- summary:
	- review automation 実行前に `git` repository、branch / commit、issue directory、phase 文書、レビュー依頼前コミット、必須コマンドの存在を自動確認する
	- 不足時は不足一覧を返して停止するか、補助 bootstrap 手順へ統一的に誘導する

### C-2026-002: 新規プロジェクト向け pre-review bootstrap 支援

- status: `open`
- priority: `high`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `project-doc-bootstrap`
	- `copilot-review-automation`
	- `new-feature-workflow`
- summary:
	- 新規プロジェクト向けに最小 issue directory、`meta.md`、`plan.md`、`design.md`、`impl.md` の雛形作成と `git init` / 初回コミット誘導を補助する
	- review automation 単体では満たせない前提条件を事前に整備できるようにする

### C-2026-003: skill 間参照パスの正規化と存在確認

- status: `open`
- priority: `high`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- user-level workflow skills 全般
- summary:
	- workflow 文書や関連 skill の参照先 path 規約を固定し、参照前の存在確認を標準化する
	- 参照不能時は候補探索か明示不足のどちらへ倒すかを user-level skills 全体で統一する

### C-2026-004: Copilot CLI 初回 prompt 投入の handshaking 導入

- status: `open`
- priority: `high`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `copilot-review-automation`
- summary:
	- `ensure` 直後の `send-prompt` 空振りを避けるため、session readiness を `status` または `capture` で確認してから初回 prompt を投入する
	- 初回投入失敗時の再送ルールも skill 側へ明記する

### C-2026-005: review session の権限ダイアログ運用改善

- status: `open`
- priority: `medium`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `copilot-review-automation`
	- review automation 系 skill 全般
- summary:
	- read-only git command、review 文書更新、review commit のうち安全に包括許可しやすい操作と要ユーザ確認操作の境界を整理する
	- review session の介入回数を減らすための運用ルールを文書化する

### C-2026-006: bootstrap 後の検証依存準備を明示

- status: `open`
- priority: `medium`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `project-doc-bootstrap`
	- `new-feature-workflow`
- summary:
	- `pyright` のような完了条件に必要な検証依存を bootstrap 時点で明示し、`development_workflow.md` の setup 欄と自動案内へ反映する
	- 依存未導入時の案内手順を skill 側で統一する

### C-2026-007: `_example_component` 再配置ノイズの低減

- status: `open`
- priority: `low`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `project-doc-bootstrap`
- summary:
	- missing mode でも実コンポーネントへ置換済みのケースでは warning 中心に扱うなど、`_example_component` の再配置ノイズを下げる
	- example を残す前提か削除して置換する前提かを選べる運用も検討する

### C-2026-008: review agent の tool error 復帰方針明文化

- status: `open`
- priority: `medium`
- source_memo: `docs/design_analysis/spec_change/20260508_user_level_agent_assets/skill_improvement_memo.md`
- scope:
	- `copilot-review-automation`
	- review automation 系 skill 全般
- summary:
	- review 文書更新時の tool error を想定し、edit 失敗時の代替手段、再試行回数、エスカレーション条件を skill に明文化する
	- review session の自己復帰性を高める

### C-2026-009: bootstrap 後の agent instructions へ project 固有説明を補助

- status: `open`
- priority: `medium`
- source_memo: `user request 2026-05-09`
- scope:
	- `project-doc-bootstrap`
	- `templates/python/instructions/agent_common_master.md`
	- `templates/csharp/instructions/agent_common_master.md`
- summary:
	- bootstrap 後の `instructions/agent_common_master.md` 冒頭が sync source 自体の説明ではなく、対象プロジェクトの目的・主要コンポーネント・運用前提をすぐ埋められる形になるよう改善する
	- project-doc-bootstrap 実行時の placeholder scan、post-bootstrap guidance、または対話的補助で project 固有説明の追記漏れを減らす
