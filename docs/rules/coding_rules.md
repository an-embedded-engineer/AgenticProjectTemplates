# コーディングルール

## 基本方針

- このリポジトリはテンプレート本体と運用文書を管理するため、変更対象がどのテンプレートへ属するかを先に明確にする
- Python テンプレートと C# テンプレートに同等の機能を入れる場合、言語ごとの自然な実装形に合わせる
- 類似ロジックや同等手順を見つけた場合は、重複した文書・コードを増やす前に共通化または差異の明文化を検討する
- テンプレート利用者へコピーされる文書には、生のプレースホルダや未整理 TODO を残さない

## 必須ルール

1. テンプレート境界
   - `user-agent-assets/skills/project-doc-bootstrap/templates/python/` と `templates/csharp/` の片方だけを変更する場合、差異が意図的かを文書または実装記録に残す
   - C# 向け bootstrap asset に Python 実行前提の保守ツールを追加しない。必要な場合は .NET tool として実装する
   - repo 共通の review 補助と検証コードは root `scripts/` と `tests/` を正本とし、shared runtime / bootstrap template へ不要な重複を持ち込まない
2. Agent instructions
   - workflow / review / orchestration skill の正本は `user-agent-assets/skills/` とする
   - root `.github/copilot-instructions.md`、`AGENTS.md`、`CLAUDE.md` と template 側 `AGENTS.md` / `CLAUDE.md` は checked-in canonical docs として扱う
   - 削除済みの root / template `instructions/`、`scripts/sync_agent_skills.*`、repo-local `.github/skills` / `.claude/skills` を再導入しない
3. 型安全性
   - Python コードは型注釈を付け、`Any` / `dict[str, Any]` / `getattr` / `setattr` の使用は局所化する
   - C# コードは nullable reference types を前提にし、`dynamic` / reflection / `Dictionary<string, object?>` の乱用を避ける
4. 例外処理
   - 例外は握りつぶさない
   - 失敗時は原因が追跡できる情報を残す
5. 後方互換
   - 明示的に指示されない限り、旧経路/旧 API/旧データ解釈を残す後方互換レイヤーは追加しない
6. フォールバック
   - 不必要なフォールバックを実装しない
   - リポジトリ内で閉じる仕様不一致は、例外や明示的エラーとして顕在化する

## 完了前チェック

1. 変更対象の bootstrap template / toolchain の検証コマンドを実行する
2. root 側 docs と `user-agent-assets/` 配下 template の整合を確認する
3. `reference/` や生成物を誤って commit 対象に含めていないか確認する
