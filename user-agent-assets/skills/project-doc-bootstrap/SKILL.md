---
name: project-doc-bootstrap
description: 既存プロジェクトへ docs 雛形を流し込み、missing-only または overwrite で project-level 文書を初期化する手順。Python / C# の既存テンプレート docs を user-level skill から配布する。
---

# project-doc-bootstrap

## いつ使う

- 既存プロジェクトへ project-level docs 雛形を初期導入する時
- `python-project-template` または `csharp-project-template` 相当の docs 構造を user-level skill から展開したい時

## 実行ルール（索引）

- Python 向け対象 docs: `references/python-target-docs.md`
- C# 向け対象 docs: `references/csharp-target-docs.md`
- macOS / Linux copy wrapper: `bin/copy_doc_templates.sh`
- Windows PowerShell copy wrapper: `bin/copy_doc_templates.ps1`

## 進め方

1. 対象言語を `python` または `csharp` で決める
2. 対象プロジェクト root で wrapper を実行し、docs 雛形をコピーする
3. copy 後に docs / instructions の placeholder 一覧を確認し、残件を整理する
4. language-specific reference を読み、優先度の高い文書から埋める

## wrapper の基本例

### macOS / Linux

```bash
bash bin/copy_doc_templates.sh --language python --project-root /path/to/project
bash bin/copy_doc_templates.sh --language csharp --project-root /path/to/project --mode overwrite
```

### Windows PowerShell

```powershell
pwsh -File bin/copy_doc_templates.ps1 -Language python -ProjectRoot C:\path\to\project
pwsh -File bin/copy_doc_templates.ps1 -Language csharp -ProjectRoot C:\path\to\project -Mode overwrite
```

## 最低限の必須チェック

1. `--language` を明示する
2. `missing` では既存 file を壊さず、未配置 file だけが入ることを確認する
3. `overwrite` の影響範囲を理解してから実行する
4. copy 後に docs / instructions の placeholder 一覧を確認する
5. `docs/components/_example_component` が残る場合は実コンポーネント化の要否を判断する