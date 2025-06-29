# 食事履歴スクレイピング

広島大学生協の食事履歴を自動取得し、CSVファイルに保存するスクレイピングツールです。

## 機能

- 広島大学生協サイトへの自動ログイン
- 食事履歴データの自動取得
- CSVファイルへの保存
- メール通知機能
- ログ機能

## ファイル構成

```
GetMeneAndReport/
├── config.py                 # 設定ファイル
├── meal_scraper.py           # メインスクレイピングクラス
├── requirements.txt          # 依存関係
├── .env                      # 環境変数（要作成）
├── utils/                    # ユーティリティ
│   ├── __init__.py
│   ├── logger.py             # ログ機能
│   ├── email_sender.py       # メール送信機能
│   └── csv_handler.py        # CSV処理機能
├── tests/                    # テストファイル
├── logs/                     # ログファイル
└── debug/                    # デバッグファイル
```

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の内容を設定してください：

```env
EMAIL=your_email@example.com
PASSWORD=your_password
SENDER_EMAIL=your_sender_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
```

### 3. 実行

```bash
python meal_scraper.py
```

## 設定

`config.py`で以下の設定を変更できます：

- Selenium設定（ヘッドレスモード、タイムアウト等）
- セレクター設定
- ファイルパス設定
- メール設定
- ログ設定
- 待機時間設定

## 出力

- `meal_history.csv`: 食事履歴データ
- `logs/scraper.log`: ログファイル

## メール通知

メール設定が正しく設定されている場合、スクレイピング完了時にメール通知が送信されます。

## ログ

ログは`logs/scraper.log`に保存され、コンソールにも表示されます。

## トラブルシューティング

### ChromeDriverのエラー

ChromeDriverManagerが自動的に適切なバージョンをダウンロードします。

### ログインエラー

- メールアドレスとパスワードが正しいことを確認
- 2段階認証が有効な場合はアプリパスワードを使用

### セレクターエラー

サイトの構造が変更された場合は、`config.py`の`SELECTORS`を更新してください。

## 開発

### テスト

```bash
cd tests
python test_*.py
```

### 新しい機能の追加

1. `utils/`ディレクトリに新しいユーティリティを追加
2. `config.py`に設定を追加
3. `meal_scraper.py`に機能を統合

## ライセンス

MIT License 