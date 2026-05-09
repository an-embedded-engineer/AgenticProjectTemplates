# user-level skills 改善メモ

## 目的

今回の `project-doc-bootstrap` と `copilot-review-automation` の実地検証で詰まった点と、設計上の改善余地を user-level skills 開発プロジェクトへ横展開するためのメモを残す。

## 対象 skill

- `project-doc-bootstrap`
- `copilot-review-automation`
- 関連 workflow: `new-feature-workflow`

## 検証サマリ

- 対象プロジェクト: 新規の最小 Python サンプルプロジェクト
- 実施内容: docs / instructions bootstrap、CLI TODO アプリ実装、Copilot CLI review、自動 follow-up review
- 結果: 主要フローは成立したが、新規プロジェクト前提では skill 側に不足する preflight と bootstrap 補助が多かった

## 詰まったところ

### 1. review automation の前提条件が新規プロジェクトで満たされていなかった

- `git` repository 未初期化
- review 対象の issue directory 未作成
- `meta.md`、`plan.md`、`design.md`、`impl.md` など phase 用文書が未作成
- 結果として、review 依頼前に実装 Agent 側で前提を補う必要があった

### 2. skill 参照先の文書パスに揺れがあった

- `copilot-review-automation` から期待される workflow 文書の参照先を、そのままでは解決できない場面があった
- skill 間参照の命名や配置規約が厳密に揃っていないと、自律実行時に探索コストが増える

### 3. Copilot CLI への初回 prompt 投入が安定しなかった

- `ensure` 直後の `send-prompt` で、起動直後すぎて実質空振りするケースがあった
- 同一 session に対して prompt を再送して初めて review が開始された

### 4. review 中の権限ダイアログが多かった

- ディレクトリアクセス許可
- `git show`、`git ls-tree` など read-only git command の許可
- review 文書編集許可
- `git add` / `git commit` 許可
- 完全自律で回すには確認回数が多く、監視側の介入コストが高かった

### 5. 検証コマンド前提と実環境がずれていた

- review 指摘で必須だった `pyright` 実行時に、実行環境へ `pyright` が未導入だった
- docs / skill は「実行可能」を前提にしていたが、bootstrap 後の環境準備には含まれていなかった

### 6. template 残骸の扱いが運用とずれた

- `project-doc-bootstrap` 実行後、`_example_component` を実コンポーネントへ置換したあとも、dry-run では再配置候補として見え続けた
- 実運用では「example を実体化済み」であり、ノイズになった

## 想定と異なり自律的に変えたところ

### 1. workflow Phase を実態に合わせて補正した

- 本来は Phase 0 から順に進めるべきだが、既に実装と docs が存在していたため、実質的に Phase 4 impl review 相当から処理を開始した

### 2. review 開始前に最小限の workflow 文書を自動生成した

- `meta.md`
- `plan.md`
- `design.md`
- `impl.md`
- skill 側の前提を満たすため、実装 Agent が不足成果物を補完した

### 3. review automation を成立させるために git repository を初期化した

- 新規プロジェクトだったため、`git init` とレビュー依頼前コミット作成を実施した
- skill の前提に repository 存在が暗黙で含まれていた

### 4. review 指摘対応で追加の型安全化を入れた

- `TodoRecord` の導入
- `_parse_records` による JSON I/O 境界の構造検証追加
- 単なる review 指摘消化ではなく、将来の再利用に寄与する補強を行った

### 5. サンプル用途より repo ルール準拠を優先した

- CLI 文言は当初日本語でも成立したが、`language_rules.md` に合わせて英語へ変更した

## skill 改善提案

### A. preflight を標準化する

review automation 実行前に、少なくとも以下を自動確認するべき。

- `git` repository か
- 現在の branch / commit が存在するか
- issue directory が存在するか
- `meta.md` と対象 phase 文書が存在するか
- review 依頼前コミットが存在するか
- 必須コマンド (`tmux`, `copilot`, `git`) が利用可能か

不足時は「不足一覧を返して停止」または「補助 bootstrap 手順へ誘導」のどちらかに統一する。

### B. 新規プロジェクト向け bootstrap 支援を追加する

新規プロジェクトでは、review automation 単体では前提が足りない。次の補助機能があるとよい。

- 最小 issue directory の自動生成
- `meta.md` / `plan.md` / `design.md` / `impl.md` の雛形作成
- 必要なら `git init` から初回コミットまで誘導する pre-review bootstrap

### C. skill 間参照の解決性を強化する

- workflow 文書や関連 skill の参照先は、存在チェックを前提にする
- 参照不能時は、候補探索または「明示不足」として扱う
- path 規約を user-level skills 全体で固定する

### D. Copilot CLI 起動直後の handshaking を入れる

- `ensure` 後すぐ `send-prompt` するのではなく、prompt 受け付け状態の確認を挟む
- たとえば `status` または `capture` で待機状態を確認してから投入する
- 初回投入失敗時の再送ルールを skill 側へ明記する

### E. 権限ダイアログ前提の運用を見直す

- read-only git command は repo 単位で包括許可しやすくする
- review 文書の更新と review commit も、review session の正規操作として扱いやすくする
- 「安全な承認」と「要ユーザ確認」の境界を skill 側でより明示する

### F. bootstrap 後の依存準備を docs へ反映する

- `pyright` のような完了条件に必須のツールは bootstrap 時点で明示する
- 可能なら `development_workflow.md` のセットアップ欄に検証依存も含める
- 依存未導入時の自動案内を skill に持たせる

### G. `_example_component` の扱いを改善する

- missing mode でも「実コンポーネントへ置換済み」の場合は warning のみとする
- あるいは example component を残す前提か、削除して置換する前提かを skill で選べるようにする

### H. review agent の tool error 復帰方針を明文化する

- 今回は review 文書更新時に tool error が一度発生したが、その後自力復帰できた
- `edit` 失敗時の代替手段、再試行回数、エスカレーション条件を skill に書いておくと安定する

## 優先度

### 高

- preflight 導入
- 新規プロジェクト向け bootstrap 補助
- skill 間参照パスの正規化
- Copilot CLI handshaking 導入

### 中

- 権限ダイアログ運用の改善
- bootstrap 後の検証依存準備の明示
- tool error 復帰ルールの明文化

### 低

- `_example_component` の再配置ノイズ低減

## user-level skills 開発プロジェクトへの反映案

### 短期

- `copilot-review-automation` に preflight checklist を追加する
- workflow 文書参照先の存在確認を追加する
- initial review prompt 送信前に session readiness 確認を追加する

### 中期

- `new-feature` / `spec-change` / `bugfix` 共通の pre-review bootstrap skill を用意する
- review session で許可すべき安全操作の定義を整理する

### 長期

- 新規 project bootstrap から review 完了までを通す end-to-end workflow を user-level skills 側で一貫提供する
- phase 成果物の生成と review 依頼の接続を、より強い契約で自動化する

## 結論

今回の検証で、user-level skills は中核フロー自体は成立する一方、新規プロジェクトのような前提未整備ケースでは「前提を自動で整える層」が不足していることが分かった。
改善の中心は、skill の判断能力を増やすことよりも、preflight、bootstrap、参照解決、session handshaking を標準化して、止まりどころを前段で潰すことにある。