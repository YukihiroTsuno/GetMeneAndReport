# 広島大学生協 食事履歴自動取得システム

**Version: 1.4.0**  
**Last Updated: 2025-07-02**

広島大学生協の食事履歴を自動取得し、CSV保存・iPhone対応HTMLメール通知を行うPythonプロジェクトです。

## 機能

- **自動スクレイピング**: Seleniumを使用した広島大学生協サイトからの食事履歴自動取得
- **CSV保存**: 取得したデータをCSVファイルに自動保存
- **メール通知**: iPhone最適化されたHTMLメールでの自動通知（最新10日間分）
- **暗号化認証情報管理**: セキュアな認証情報の保存・管理
- **モジュラー設計**: 機能ごとの分離による保守性・拡張性の向上

## プロジェクト構造

```
GetMeneAndReport/
├── meal_scraper.py          # メインスクレイパー（統合インターフェース）
├── config.py               # 設定ファイル
├── setup_credentials.py    # 認証情報設定
├── requirements.txt        # 依存関係
├── README.md              # このファイル
├── debug/                 # デバッグ用ファイル
├── logs/                  # ログファイル
└── utils/                 # ユーティリティモジュール
    ├── __init__.py
    ├── logger.py          # ログ管理
    ├── csv_handler.py     # CSV処理
    ├── encryption.py      # 暗号化
    ├── webdriver_manager.py    # WebDriver管理
    ├── selector_manager.py     # セレクター管理
    ├── login_manager.py        # ログイン管理
    ├── navigation_manager.py   # ナビゲーション管理
    ├── data_extractor.py       # データ抽出
    ├── data_processor.py       # データ処理
    ├── html_template.py        # HTMLテンプレート生成
    ├── email_config.py         # メール設定管理
    ├── smtp_sender.py          # SMTP送信
    └── email_sender.py         # メール送信統合
```

## モジュラー設計の利点

### Webスクレイピング機能の分離

プロジェクトは以下の5つの主要なWebスクレイピングモジュールに分離されています：

1. **WebDriver管理** (`utils/webdriver_manager.py`)
   - Selenium WebDriverの設定・管理・クリーンアップ
   - ヘッドレスモード対応
   - デバッグ用HTML保存機能

2. **セレクター管理** (`utils/selector_manager.py`)
   - Web要素のセレクターを一元管理
   - サイト構造変更への対応
   - セレクターの妥当性チェック

3. **ログイン管理** (`utils/login_manager.py`)
   - Webサイトへのログイン処理
   - 複数回ログイン対応
   - ログイン状態チェック

4. **ナビゲーション管理** (`utils/navigation_manager.py`)
   - ページ遷移処理
   - リンククリック処理
   - 動的要素の操作

5. **データ抽出** (`utils/data_extractor.py`)
   - 食事履歴データの抽出
   - データ妥当性チェック
   - データサマリー生成

### メール機能の分離

メール機能も以下の5つのモジュールに分離されています：

1. **データ処理** (`utils/data_processor.py`)
2. **HTMLテンプレート生成** (`utils/html_template.py`)
3. **メール設定管理** (`utils/email_config.py`)
4. **SMTP送信** (`utils/smtp_sender.py`)
5. **メール送信統合** (`utils/email_sender.py`)

### 設計原則

- **単一責任の原則**: 各モジュールは1つの明確な責任を持つ
- **依存性注入**: モジュール間の依存関係を明確化
- **設定の外部化**: 設定をconfig.pyで一元管理
- **エラーハンドリング**: 各モジュールで適切なエラー処理
- **ログ出力**: 詳細なログによる動作追跡

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 認証情報の設定

```bash
python setup_credentials.py
```

### 3. 設定ファイルの確認

`config.py`で以下の設定を確認・調整してください：

- `EMAIL`, `PASSWORD`: 生協のログイン情報
- `SELECTORS`: Web要素のセレクター
- `WAIT_TIMES`: 待機時間設定
- `SELENIUM_CONFIG`: Selenium設定
- メール設定

## 使用方法

### 基本的な実行

```bash
python meal_scraper.py
```

### テスト実行

各モジュールの独立動作を確認：

```bash
# メール機能テスト
python test_modular_email.py

# Webスクレイピング機能テスト
python test_modular_scraper.py
```

### 個別モジュールの使用例

```python
from utils import WebDriverManager, SelectorManager, LoginManager

# WebDriver管理
config = {"headless": True, "timeout": 10}
with WebDriverManager(config) as wdm:
    wdm.navigate_to("https://example.com")

# セレクター管理
sm = SelectorManager()
selectors = sm.get_login_selectors()

# ログイン管理
credentials = ("email@example.com", "password")
lm = LoginManager(wdm, sm, credentials, config)
success = lm.login("https://login.example.com")
```

## 設定のカスタマイズ

### セレクターの変更

サイト構造が変更された場合、`config.py`の`SELECTORS`を更新：

```python
SELECTORS = {
    "email_field": "input#new_email_field",
    "password_field": "input#new_password_field",
    # その他のセレクター...
}
```

### 待機時間の調整

ネットワーク環境に応じて`WAIT_TIMES`を調整：

```python
WAIT_TIMES = {
    "timeout": 15,        # 要素待機時間
    "page_load": 8,       # ページ読み込み待機
    "after_login": 5,     # ログイン後待機
    "after_click": 8,     # クリック後待機
    "element_load": 3,    # 要素読み込み待機
    "before_close": 15    # ブラウザ閉じる前待機
}
```

### Selenium設定の調整

```python
SELENIUM_CONFIG = {
    "headless": True,     # ヘッドレスモード
    "timeout": 30         # タイムアウト時間
}
```

## トラブルシューティング

### よくある問題

1. **ログインエラー**
   - 認証情報を確認
   - セレクターが正しいか確認
   - デバッグHTMLを確認

2. **データ取得エラー**
   - サイト構造の変更を確認
   - セレクターの更新が必要か確認

3. **メール送信エラー**
   - SMTP設定を確認
   - 認証情報を確認

### デバッグ方法

1. **ログの確認**
   ```bash
   tail -f logs/scraper.log
   ```

2. **デバッグHTMLの確認**
   ```bash
   cat debug/login_page_debug.html
   ```

3. **個別モジュールのテスト**
   ```bash
   python test_modular_scraper.py
   ```

## 今後の拡張性

### ログイン方法の変更対応

新しいログイン方式が導入された場合：

1. `utils/login_manager.py`の`LoginManager`クラスを拡張
2. 新しいログイン方式用のメソッドを追加
3. 設定でログイン方式を選択可能に

### サイト構造変更への対応

サイト構造が変更された場合：

1. `utils/selector_manager.py`でセレクターを更新
2. 必要に応じて`utils/data_extractor.py`を調整
3. 設定ファイルでセレクターを管理

### 新しいデータ形式への対応

新しいデータ形式に対応する場合：

1. `utils/data_extractor.py`に新しい抽出ロジックを追加
2. `utils/data_processor.py`で新しいデータ処理を実装
3. `utils/html_template.py`で新しい表示形式を追加

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

- 本ツールは教育目的で作成されています
- 生協の利用規約を遵守してご利用ください
- 過度なアクセスは避けてください
- 取得したデータの取り扱いには十分ご注意ください 