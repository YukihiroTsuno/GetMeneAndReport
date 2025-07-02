"""
Webブラウザ管理機能（Playwright版）
Playwrightの設定、管理、クリーンアップを担当
"""

import time
import logging
from playwright.sync_api import sync_playwright, Browser, Page
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WebDriverManager:
    """Playwrightブラウザ管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def setup_driver(self) -> bool:
        """Playwrightブラウザをセットアップ"""
        try:
            logger.info("Playwrightブラウザをセットアップ中...")
            
            # 既存のリソースをクリーンアップ
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            
            # Playwrightを初期化
            self.playwright = sync_playwright().start()
            headless = self.config.get("headless", False)
            
            # シンプルなブラウザ起動
            self.browser = self.playwright.chromium.launch(headless=headless)
            
            # 新しいページを作成
            self.page = self.browser.new_page()
            
            # ウィンドウサイズやUAなども必要に応じて設定
            self.page.set_viewport_size({"width": 1920, "height": 1080})
            self.page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            logger.info("Playwrightブラウザのセットアップが完了しました")
            return True
            
        except Exception as e:
            logger.error(f"Playwrightセットアップエラー: {e}")
            # エラー時はリソースをクリーンアップ
            self.cleanup()
            return False
    
    def get_page(self) -> Optional[Page]:
        """Pageオブジェクトを取得"""
        return self.page
    
    def is_ready(self) -> bool:
        """ブラウザが準備完了しているかチェック"""
        return self.browser is not None and self.page is not None
    
    def save_debug_html(self, file_path: str = "debug/page_debug.html") -> bool:
        """デバッグ用にHTMLを保存"""
        try:
            if not self.page:
                return False
            html = self.page.content()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"デバッグ用HTMLを保存しました: {file_path}")
            return True
        except Exception as e:
            logger.warning(f"HTML保存エラー: {e}")
            return False
    
    def get_current_url(self) -> str:
        """現在のURLを取得"""
        if self.page:
            return self.page.url
        return ""
    
    def navigate_to(self, url: str) -> bool:
        """指定されたURLに遷移"""
        try:
            if not self.page:
                return False
            
            # Playwrightの最適化されたナビゲーション
            self.page.goto(
                url, 
                timeout=self.config.get("navigation_timeout", 30000),
                wait_until="networkidle"  # ネットワークが安定するまで待機
            )
            
            logger.info(f"URLに遷移しました: {url}")
            return True
        except Exception as e:
            logger.error(f"URL遷移エラー: {e}")
            return False
    
    def cleanup(self, wait_time: int = 3) -> None:
        """リソースをクリーンアップ"""
        try:
            if self.browser:
                time.sleep(wait_time)
                self.browser.close()
                self.browser = None
                self.page = None
                logger.info("ブラウザを閉じました")
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")
    
    def __enter__(self):
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup() 