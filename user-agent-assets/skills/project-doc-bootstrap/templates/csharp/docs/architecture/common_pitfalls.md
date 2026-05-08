# よくある落とし穴

<!-- TODO: プロジェクト固有の落とし穴を番号付きで追加する -->

## 1. Nullable 参照型

- プロジェクト全体で `<Nullable>enable</Nullable>` を有効にする
- `T?` を返すメソッドの呼び出し元で必ず null チェックを行う
- `!`（null 許容演算子）の安易な使用は実行時エラーの原因になる
- `string` と `string?` を混同しない

## 2. 非同期処理

- `async void` は使わない（イベントハンドラを除く）
- `Task.Result` / `Task.Wait()` によるデッドロックに注意する
- `ConfigureAwait(false)` の適用方針をプロジェクトで統一する

## 3. 例外処理

- `catch (Exception) { }` は絶対に書かない
- 例外を catch したら必ずログに原因情報を残す
- 上位に re-throw するか、明示的にハンドリングする
- `throw ex;` ではなく `throw;` でスタックトレースを保持する

## 4. IDisposable

- `IDisposable` を実装するオブジェクトは `using` で確実に破棄する
- `IAsyncDisposable` の場合は `await using` を使用する

<!-- TODO: 以下にプロジェクト固有の落とし穴を追加する -->
<!--
## 5. (例: パフォーマンス関連)

## 6. (例: DI コンテナ関連)

## 7. (例: Entity Framework 関連)
-->
