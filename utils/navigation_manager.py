"""
ナビゲーション管理機能（Playwright版）
Webサイト内のページ遷移を担当
"""

import time
import logging
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from typing import Dict, Any, Optional
from .webdriver_manager import WebDriverManager
from .selector_manager import SelectorManager
from .login_manager import LoginManager

logger = logging.getLogger(__name__)

class NavigationManager:
    """ナビゲーション管理クラス（Playwright版）"""
    
    def __init__(self, webdriver_manager: WebDriverManager, selector_manager: SelectorManager, login_manager: LoginManager, config: Dict[str, Any]):
        self.webdriver_manager = webdriver_manager
        self.selector_manager = selector_manager
        self.login_manager = login_manager
        self.config = config
    
    def navigate_to_meal_history(self) -> bool:
        """食事履歴ページに遷移"""
        try:
            logger.info("食事履歴ページに遷移中...")
            
            if not self.webdriver_manager.is_ready():
                logger.error("Playwrightブラウザが初期化されていません")
                return False
            
            page = self.webdriver_manager.get_page()
            
            if not page:
                logger.error("Pageオブジェクトが初期化されていません")
                return False
            
            # ミール利用履歴リンクを探してクリック
            selectors = self.selector_manager.get_navigation_selectors()
            meal_history_link = page.wait_for_selector(
                selectors["meal_history_link"], 
                state="visible",
                timeout=self.config.get("timeout", 30) * 1000
            )
            
            if meal_history_link:
                href = meal_history_link.get_attribute("href")
                link_text = meal_history_link.text_content()
                logger.info(f"リンク先URL: {href}")
                logger.info(f"リンクテキスト: {link_text.strip() if link_text else 'N/A'}")
                
                meal_history_link.click()
            else:
                logger.error("ミール利用履歴リンクが見つかりませんでした")
                return False
            time.sleep(self.config.get("after_click", 8))
            
            # 遷移後の確認
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"遷移後のURL: {current_url}")
            
            # 2回目のログインが必要な場合
            if "login" in current_url.lower():
                logger.info("2回目のログインが必要です")
                return self.login_manager.perform_second_login()
            
            return True
            
        except Exception as e:
            logger.error(f"食事履歴ページ遷移エラー: {e}")
            return False
    
    def select_usage_detail(self) -> bool:
        """ご利用明細を選択"""
        try:
            logger.info("ご利用明細を選択中...")
            
            if not self.webdriver_manager.is_ready():
                logger.error("Playwrightブラウザが初期化されていません")
                return False
            
            page = self.webdriver_manager.get_page()
            
            if not page:
                logger.error("Pageオブジェクトが初期化されていません")
                return False
            
            # ご利用明細リンクを探してクリック
            selectors = self.selector_manager.get_navigation_selectors()
            usage_detail_link = page.wait_for_selector(
                selectors["usage_detail_link"],
                state="visible",
                timeout=self.config.get("timeout", 30) * 1000
            )
            
            if usage_detail_link:
                usage_detail_link.click()
            else:
                logger.error("ご利用明細リンクが見つかりませんでした")
                return False
            time.sleep(self.config.get("after_click", 8))
            
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"ご利用明細遷移後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"ご利用明細選択エラー: {e}")
            return False
    
    def click_more_button(self) -> bool:
        """「もっと見る」ボタンをクリック"""
        try:
            if not self.webdriver_manager.is_ready():
                return False
            
            page = self.webdriver_manager.get_page()
            
            if not page:
                return False
            
            # 「もっと見る」ボタンがあればクリック
            try:
                selectors = self.selector_manager.get_data_extraction_selectors()
                more_button = page.locator(selectors["more_button"])
                if more_button.count() > 0 and more_button.is_visible():
                    logger.info("「もっと見る」ボタンをクリックします")
                    more_button.click()
                    time.sleep(self.config.get("element_load", 3))
                    return True
            except Exception:
                logger.info("「もっと見る」ボタンは見つかりませんでした")
                return True  # ボタンがない場合は正常として扱う
            
            return True
            
        except Exception as e:
            logger.warning(f"「もっと見る」ボタンクリックエラー: {e}")
            return False 