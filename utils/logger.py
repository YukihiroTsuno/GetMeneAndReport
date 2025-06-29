"""
ログ機能
スクレイピングのログを管理
"""

import logging
import os

# ログ設定を直接定義（循環インポート回避）
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/scraper.log"
}

FILE_PATHS = {
    "logs_dir": "logs"
}

def setup_logger(name="meal_scraper"):
    """ログ設定を初期化"""
    # ログディレクトリを作成
    os.makedirs(FILE_PATHS["logs_dir"], exist_ok=True)
    
    # ロガーを作成
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_CONFIG["level"]))
    
    # 既存のハンドラーをクリア
    logger.handlers.clear()
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(LOG_CONFIG["file"], encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッター
    formatter = logging.Formatter(LOG_CONFIG["format"])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラーを追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 