# AGENTS.md

## このリポジトリの運用方針

このリポジトリは Minecraft MOD 関連ツールの開発用です。

Codex は作業開始時に、まずこのファイルと `docs/CURRENT_STATE.md` を確認してください。

## 情報の保存先

### 短期・現在進行中 → GitHub

GitHub には、今の開発に直接必要な情報を置きます。

- ソースコード
- 設定ファイル、スクリプト
- 現在の TODO
- バグと再現条件
- 実装中の仕様
- 短期の検証結果
- 次にやること
- ブランチ単位の作業メモ

現在状態の要約は `docs/CURRENT_STATE.md` に書きます。

### 長期・あとから参照する情報 → Google Drive

長期的に残す情報は Google Drive 側へ整理します。

- プロジェクト全体の目的
- 設計判断とその理由
- 大きな環境構築の記録
- 重要なトラブルと解決経緯
- 方針転換の理由
- 将来も参照する重要事項

長期記録:
https://docs.google.com/document/d/1E67nRYuDWdySRcvqlI7xxkseWN0pEpThj7DLSvalhHQ/edit?usp=drivesdk

## Codex の確認順

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. 関連コード・設定・Issue・コミット
4. 過去の理由や長期情報が必要な場合のみ Google Drive の長期記録

## 更新ルール

- 作業中の情報は Git を優先する。
- `docs/CURRENT_STATE.md` は現在の状態だけを短く保つ。
- 作業が一区切りついたら、今後も必要な情報だけ Drive の長期記録へ移す。
- Git と Drive に同じ長文を重複保存しない。
- Git は「今」、Drive は「長期記憶」として使い分ける。
- パスワード、トークン、秘密鍵などの秘密情報はコミットしない。

## Git の基本

- 意味のある小さな単位でコミットする。
- 大きな変更は可能なら作業ブランチで行う。
- 既存コードを大きく変更する前に関連ファイルを確認する。
- 作業終了時に `docs/CURRENT_STATE.md` を更新する。
