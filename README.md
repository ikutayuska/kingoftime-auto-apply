# kot_auto_apply

KING OF TIME の勤務表を読み取り、今週平日分の申請を自動化する Playwright スクリプトです。

## 概要
- 勤務表の行テキストから勤務場所を判定します。
- `出社` 判定時: 日割り通勤費の申請を実行します。
- `在宅` 判定時: スマートワーキング手当の申請を実行します。

## 動作要件
- Python 3.10+
- Google Chrome または Playwright Chromium
- KING OF TIME にアクセスできる環境

## セットアップ
1. 依存パッケージをインストール
```bash
pip install python-dotenv playwright
python -m playwright install
```

2. `.env` を作成
```bash
cp .env.example .env
```

3. `.env` に値を設定
- `KOT_USERNAME`, `KOT_PASSWORD` は必須です。
- `KOT_OFFICE_KEYWORDS`, `KOT_REMOTE_KEYWORDS` は少なくともどちらか必須です。

## 環境変数
| 変数名 | 必須 | 説明 |
|---|---|---|
| `KOT_USERNAME` | Yes | KING OF TIME ログインID |
| `KOT_PASSWORD` | Yes | KING OF TIME パスワード |
| `KOT_URL` | No | ログインURL（既定: `https://login.ta.kingoftime.jp/admin`） |
| `KOT_TIMEZONE` | No | 日付判定タイムゾーン（既定: `Asia/Tokyo`） |
| `KOT_HEADLESS` | No | `true` でヘッドレス実行（既定: `false`） |
| `KOT_BROWSER_CHANNEL` | No | `chrome` など。空なら Playwright 同梱 Chromium |
| `KOT_OFFICE_KEYWORDS` | Conditionally | 出社判定用キーワード（カンマ区切り） |
| `KOT_REMOTE_KEYWORDS` | Conditionally | 在宅判定用キーワード（カンマ区切り） |
| `KOT_TRANSIT_REMARK` | No | 出社申請時の備考 |
| `KOT_REMOTE_REMARK` | No | 在宅申請時の備考 |

## 実行方法
```bash
python kot_auto_apply.py
```

## セキュリティと公開時の注意
- `.env` は機密情報を含むため Git 管理しないでください（`.gitignore` 設定済み）。
- 社内固有の住所・拠点名はコードに直書きせず、必ず `.env` で管理してください。
- 本スクリプトは実際に申請操作を行うため、テスト環境または少量データで動作確認してから利用してください。

## 既知の前提
- KING OF TIME の画面構造（ラベル名、ボタン名、ロール）が変更されると動作しない場合があります。
- 申請対象は「今週の月〜金」のみです。
