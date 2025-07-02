"""
ログイン管理機能（Playwright版）
Webサイトへのログイン処理を担当
"""

import time
import logging
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from typing import Dict, Any, Optional, Tuple
from .webdriver_manager import WebDriverManager
from .selector_manager import SelectorManager

logger = logging.getLogger(__name__)

class LoginManager:
    """ログイン管理クラス（Playwright版）"""
    
    def __init__(self, webdriver_manager: WebDriverManager, selector_manager: SelectorManager, credentials: Tuple[str, str], config: Dict[str, Any]):
        self.webdriver_manager = webdriver_manager
        self.selector_manager = selector_manager
        self.email, self.password = credentials
        self.config = config
    
    def login(self, login_url: str) -> bool:
        """ログイン処理を実行"""
        try:
            logger.info("ログイン処理を開始します")
            
            if not self.webdriver_manager.is_ready():
                logger.error("Playwrightブラウザが初期化されていません")
                return False
            
            page = self.webdriver_manager.get_page()
            
            if not page:
                logger.error("Pageオブジェクトが初期化されていません")
                return False
            
            # ページにアクセス
            if not self.webdriver_manager.navigate_to(login_url):
                return False
            
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"アクセス後のURL: {current_url}")
            
            # デバッグ用にHTMLを保存
            self.webdriver_manager.save_debug_html("debug/login_page_debug.html")
            
            # ログインフォームが表示されているかチェック
            if not self._check_login_form_exists(page):
                logger.info("ログインフォームが見つかりません。既にログイン済みの可能性があります")
                return True
            
            # ログイン情報を入力
            if not self._input_credentials(page):
                return False
            
            # ログインボタンをクリック
            if not self._click_login_button(page):
                return False
            
            # ログイン後の処理を待機
            time.sleep(self.config.get("after_login", 5))
            
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"ログイン後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"ログイン処理エラー: {e}")
            return False
    
    def perform_second_login(self) -> bool:
        """2回目のログイン処理"""
        try:
            logger.info("2回目のログイン処理を開始します")
            
            if not self.webdriver_manager.is_ready():
                logger.error("Playwrightブラウザが初期化されていません")
                return False
            
            page = self.webdriver_manager.get_page()
            
            if not page:
                logger.error("Pageオブジェクトが初期化されていません")
                return False
            
            # ログインフォームを探す
            email_field = page.wait_for_selector('input[name="email"]', timeout=self.config.get("timeout", 30) * 1000)
            password_field = page.locator('input[name="password"]')
            
            # ログイン情報を入力
            if self.email and self.password and email_field:
                email_field.fill(self.email)
                password_field.fill(self.password)
            else:
                logger.error("認証情報が設定されていません")
                return False
            
            # ログインボタンをクリック
            login_button = page.locator('button#next')
            login_button.click()
            
            time.sleep(self.config.get("after_login", 5))
            
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"2回目ログイン後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"2回目ログイン処理エラー: {e}")
            return False
    
    def _check_login_form_exists(self, page: Page) -> bool:
        """ログインフォームが存在するかチェック"""
        try:
            selectors = self.selector_manager.get_login_selectors()
            email_field = page.wait_for_selector(selectors["email_field"], timeout=self.config.get("timeout", 30) * 1000)
            logger.info("ログインフォームが表示されています")
            return True
        except PlaywrightTimeoutError:
            return False
    
    def _input_credentials(self, page: Page) -> bool:
        """認証情報を入力"""
        try:
            selectors = self.selector_manager.get_login_selectors()
            email_field = page.locator(selectors["email_field"])
            password_field = page.locator(selectors["password_field"])

            if self.email and self.password:
                email_field.fill(self.email)
                password_field.fill(self.password)
            else:
                logger.error("認証情報が設定されていません")
                return False
            
            # 入力されたパスワード値をログ出力（デバッグ用）
            try:
                actual_pw = password_field.input_value()
                logger.info(f"パスワード欄の値（デバッグ用）: {actual_pw}")
            except Exception as e:
                logger.warning(f"パスワード値取得エラー: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"認証情報入力エラー: {e}")
            return False
    
    def _click_login_button(self, page: Page) -> bool:
        """ログインボタンをクリック"""
        try:
            selectors = self.selector_manager.get_login_selectors()
            
            # ログインボタンを探す（複数のセレクターを試す）
            login_button = None
            login_button_selectors = [
                selectors["login_button"],
                "input[type='submit']",
                "button:has-text('ログイン')",
                "button:has-text('Login')",
                "input[value*='ログイン']",
                "input[value*='Login']"
            ]
            
            for selector in login_button_selectors:
                try:
                    if ":has-text(" in selector:
                        # Playwrightのテキストセレクターに変換
                        text = selector.split("'")[1]
                        text_selector = f"button:has-text('{text}')"
                        login_button = page.locator(text_selector)
                    else:
                        login_button = page.locator(selector)
                    
                    if login_button.count() > 0:
                        logger.info(f"ログインボタン発見: {selector}")
                        break
                except Exception:
                    continue
            
            if not login_button or login_button.count() == 0:
                logger.error("ログインボタンが見つかりませんでした")
                return False
            
            # ログインボタンをクリック
            login_button.click()
            logger.info("ログインボタンをクリックしました")
            return True
            
        except Exception as e:
            logger.error(f"ログインボタンクリックエラー: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """ログイン状態をチェック"""
        try:
            if not self.webdriver_manager.is_ready():
                return False
            
            page = self.webdriver_manager.get_page()
            if not page:
                return False
            
            # ログインフォームが存在しない場合はログイン済みと判断
            selectors = self.selector_manager.get_login_selectors()
            try:
                page.wait_for_selector(selectors["email_field"], timeout=5000)
                return False  # ログインフォームが存在する
            except PlaywrightTimeoutError:
                return True  # ログインフォームが存在しない
            
        except Exception as e:
            logger.warning(f"ログイン状態チェックエラー: {e}")
            return False 