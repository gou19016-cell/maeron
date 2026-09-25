# Current State

## 目的

Minecraft MOD 関連ツールをこのリポジトリで開発する。

## 現在の状態

- GitHub リポジトリ初期化済み
- デフォルトブランチ: `main`
- ChatGPT / Codex から GitHub の読み書きが可能
- GitHub 連携テスト済み
- 短期情報は GitHub、長期情報は Google Drive で管理
- Codex から ChatGPT へ確認が必要な事項は Google Drive の「GPT確認待ち」に報告する運用を追加
- Minecraft MOD管理・診断ツール MVP の実装タスクを GitHub Issue #2 に作成済み
- 作業ブランチ `feature/minecraft-mod-tool-mvp` を作成済み

## 現在の作業

Codex に Minecraft MOD 管理・診断ツール MVP の実装を依頼する段階。

依頼:
https://github.com/gou19016-cell/maeron/issues/2

作業ブランチ:
`feature/minecraft-mod-tool-mvp`

## MVPの中心機能

- mods フォルダ走査
- Forge / NeoForge / Fabric / Quilt のメタデータ解析
- MOD名、ID、バージョン、ローダー、依存関係などの一覧表示
- 重複MOD、複数バージョン、ローダー不一致、Minecraftバージョン不一致、不足依存関係などの検出
- MODの安全な有効/無効切替
- 検索・フィルタ
- Markdown / JSON レポート出力
- 数百MODでもUIを固めにくい構成
- 自動テストとREADME

詳細な完了条件は Issue #2 を参照。

## 管理先

長期記録:
https://docs.google.com/document/d/1E67nRYuDWdySRcvqlI7xxkseWN0pEpThj7DLSvalhHQ/edit?usp=drivesdk

GPT確認待ち:
https://docs.google.com/document/d/1tLaKA_91ZhXpwTGkYApVf3cnP33jbmmUxDLvj1L6BvA/edit?usp=drivesdk

## 次にやること

- Codex が `feature/minecraft-mod-tool-mvp` で実装開始
- 小さな単位でコミット
- テストを追加
- 迷いや重要判断があれば GPT確認待ちへ報告
- MVP完成時にPR作成

## 作業終了時

- 現在状態をこのファイルへ反映
- GPT確認が必要な内容があれば Drive の確認待ちへ報告
- 長期保存すべきと確定した重要事項だけ Drive の長期記録へ整理
