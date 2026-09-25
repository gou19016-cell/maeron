# Current State

## 目的

Minecraft MOD 構成の確認・診断・可逆的な有効/無効切替を行う Windows 向けツールを開発する。

## 現在の作業

ブランチ: `feature/minecraft-mod-tool-mvp`

Issue #2 の MVP 実装を進行中。Python 3.10+ / Tkinter の初期実装を追加した。

- mods フォルダ直下の `.jar` と `.jar.disabled` を走査
- Forge / NeoForge TOML、Fabric / Quilt JSON の代表的メタデータを抽出
- 重複 MOD ID、不足依存、メタデータなし、破損 JAR の候補を表示
- 検索、状態・ローダーフィルタ、確認付きの可逆リネーム、Markdown / JSON 出力
- 自作の最小 JAR fixture を使ったユニットテスト 4 件が成功

## 残作業・制限

Issue #2 の完了条件はまだ満たしていない。

- 選択した Minecraft バージョンやインスタンスのローダーとの互換性判定
- スキャンをバックグラウンドで行う応答性改善（現在は同期処理）
- Minecraft / ローダー依存メタデータのバージョン範囲を正確に解釈する診断
- Windows 上での GUI 起動確認
- 上記を含む最終レビュー後の PR 作成

## 起動・テスト

```powershell
$env:PYTHONPATH = "src"
python -m maeron
python -m unittest discover -s tests -v
```

実 MOD JAR はリポジトリへ追加しない。fixture はテスト時に一時生成する。
