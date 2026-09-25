# Maeron

Minecraft MOD の構成確認・診断・有効/無効切替を行う Windows 向けデスクトップ MVP です。Python 3.10 以上と Tkinter（通常の Windows Python インストーラーに含まれます）を使います。外部ライブラリや自動ダウンロード機能はありません。

## 起動

リポジトリのルートで実行します。

```powershell
python -m maeron
```

開発時は src レイアウトのため、次のどちらかを使います。

```powershell
$env:PYTHONPATH = "src"
python -m maeron
```

または `pip install -e .` の後に `maeron` を起動します。

## 使い方

1. 「modsフォルダを選択」で Minecraft インスタンスの `mods` フォルダを選びます。
2. 検索、状態、ローダーで一覧を絞り込みます。
3. MOD を選んで「有効/無効を切替」を押すと、対象名を確認してから `.jar` と `.jar.disabled` の間でリネームします。ファイルは削除しません。
4. 「エクスポート」で Markdown または JSON に保存します。

Forge / NeoForge の TOML と Fabric / Quilt の JSON メタデータを読み取ります。問題候補として重複 ID、不足依存関係、メタデータなし、読み取り不能を表示します。何百個もの JAR を扱うため、一覧には対象拡張子だけを読み込みます。

## テスト

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

テストは実 MOD を含めず、一時ディレクトリ内で最小の JAR fixture を作成します。

## MVP の制限

- バージョン範囲の完全な意味解析、ローダー/ゲームバージョン自動推定、ランタイム環境との互換性検査は行いません。
- 選択したフォルダ直下だけをスキャンします。
- UI は同期スキャンです。一般的な数百件の利用を想定しますが、非常に大きな JAR が混在する場合は応答性改善が必要です。
- 有効/無効切替はファイル名変更なので、ゲーム起動中には実行しないでください。
