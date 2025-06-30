"""
設定ファイル
食事履歴スクレイピングの設定を管理
"""

import os
from dotenv import load_dotenv
from utils.encryption import CredentialManager

# 環境変数を読み込み
load_dotenv()

# 基本設定
MEAL_PAGE_URL = "https://hiroshima.meal.univ-coop.net/mypage"

# 認証情報の取得（暗号化ファイルのみ）
def get_credentials():
    """暗号化された認証情報を取得（.credentialsのみ）"""
    credential_manager = CredentialManager()
    email, password = credential_manager.load_encrypted_credentials()
    return email, password

EMAIL, PASSWORD = get_credentials()

# Selenium設定
SELENIUM_CONFIG = {
    "headless": False,  # ヘッドレスモード（Trueで非表示）
    "window_size": (1920, 1080),
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "script_timeout": 30
}

# セレクター設定
SELECTORS = {
    # ログインフォーム
    "email_field": "input#form_email",
    "password_field": "input#form_password",
    "login_button": "input[type='submit'][value='ログインする']",
    
    # ミール利用履歴リンク
    "meal_history_link": "a[href*='cn-univ.coop']",
    "meal_history_xpath": "//a[contains(text(), 'ミール利用履歴')]",
    
    # ご利用明細
    "usage_detail_link": "a[href*='detail']",
    
    # 食事履歴データ
    "history_articles": "article.history-contents",
    "date_element": ".history-contents-date",
    "month_span": ".month",
    "date_span": ".date",
    "day_span": ".day",
    "detail_elements": ".history-contents-detail",
    "hour_element": ".hour",
    "menu_elements": ".item li",
    "amount_element": ".total .amount",
    
    # もっと見るボタン
    "more_button": ".btn-more"
}

# ファイルパス設定
FILE_PATHS = {
    "csv_output": "meal_history.csv",
    "debug_dir": "debug",
    "logs_dir": "logs"
}

# メール設定
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": os.getenv("SENDER_EMAIL", ""),
    "sender_password": os.getenv("SENDER_PASSWORD", ""),
    "recipient_email": os.getenv("RECIPIENT_EMAIL", ""),
    "email_width": 240,  # HTMLメールの幅（px）
    "subject_template": "ミールカード　食べたもの {date}"
}

# ログ設定
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/scraper.log"
}

# 待機時間設定
WAIT_TIMES = {
    "timeout": 30,
    "page_load": 5,
    "element_load": 3,
    "after_click": 8,
    "after_login": 5,
    "before_close": 15
} 