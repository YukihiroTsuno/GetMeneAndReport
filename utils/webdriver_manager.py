"""
WebDriver管理機能
Selenium WebDriverの設定、管理、クリーンアップを担当
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WebDriverManager:
    """WebDriver管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    def setup_driver(self) -> bool:
        """Chromeドライバーをセットアップ"""
        try:
            logger.info("Chromeドライバーをセットアップ中...")
            
            # Chromeオプションを設定
            chrome_options = Options()
            
            if self.config.get("headless", False):
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # ChromeDriverManagerでドライバーを自動管理
            service = Service(ChromeDriverManager().install())
            
            # WebDriverを作成
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.config.get("timeout", 30))
            
            logger.info("Chromeドライバーのセットアップが完了しました")
            return True
            
        except Exception as e:
            logger.error(f"Chromeドライバーセットアップエラー: {e}")
            return False
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """WebDriverを取得"""
        return self.driver
    
    def get_wait(self) -> Optional[WebDriverWait]:
        """WebDriverWaitを取得"""
        return self.wait
    
    def is_ready(self) -> bool:
        """WebDriverが準備完了しているかチェック"""
        return self.driver is not None and self.wait is not None
    
    def save_debug_html(self, file_path: str = "debug/page_debug.html") -> bool:
        """デバッグ用にHTMLを保存"""
        try:
            if not self.driver:
                return False
            
            html = self.driver.page_source
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"デバッグ用HTMLを保存しました: {file_path}")
            return True
            
        except Exception as e:
            logger.warning(f"HTML保存エラー: {e}")
            return False
    
    def get_current_url(self) -> str:
        """現在のURLを取得"""
        if self.driver:
            return self.driver.current_url
        return ""
    
    def navigate_to(self, url: str) -> bool:
        """指定されたURLに遷移"""
        try:
            if not self.driver:
                return False
            
            self.driver.get(url)
            time.sleep(self.config.get("page_load", 5))
            logger.info(f"URLに遷移しました: {url}")
            return True
            
        except Exception as e:
            logger.error(f"URL遷移エラー: {e}")
            return False
    
    def cleanup(self, wait_time: int = 15) -> None:
        """リソースをクリーンアップ"""
        try:
            if self.driver:
                time.sleep(wait_time)
                self.driver.quit()
                self.driver = None
                self.wait = None
                logger.info("ブラウザを閉じました")
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")
    
    def __enter__(self):
        """コンテキストマネージャー用"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー用"""
        self.cleanup() 