# コーディングルール

## 基本方針

- このリポジトリはテンプレート本体と運用文書を管理するため、変更対象がどのテンプレートへ属するかを先に明確にする
- Python テンプレートと C# テンプレートに同等の機能を入れる場合、言語ごとの自然な実装形に合わせる
- 類似ロジックや同等手順を見つけた場合は、重複した文書・コードを増やす前に共通化または差異の明文化を検討する
- テンプレート利用者へコピーされる文書には、生のプレースホルダや未整理 TODO を残さない

## 必須ルール

1. テンプレート境界
   - `python-project-template/` と `csharp-project-template/` の片方だけを変更する場合、差異が意図的かを文書または実装記録に残す
   - C# テンプレートに Python 実行前提の保守ツールを追加しない。必要な場合は .NET tool として実装する
   - root `scripts/agent_cli_tmux.py` と `python-project-template/scripts/agent_cli_tmux.py` は意図的な重複として同一内容を保持し、変更時は両方を同期する
2. Agent instructions
   - Agent 向け同期元は `instructions/agent_common_master.md` と `instructions/skills/` を正本とする
   - テンプレート内の生成物は直接編集しない
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

1. 変更対象テンプレートの検証コマンドを実行する
2. root 側 docs とテンプレート側 docs の整合を確認する
3. `reference/` や生成物を誤って commit 対象に含めていないか確認する
