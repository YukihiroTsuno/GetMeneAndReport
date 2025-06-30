"""
ログイン管理機能
Webサイトへのログイン処理を担当
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Dict, Any, Optional, Tuple
from .webdriver_manager import WebDriverManager
from .selector_manager import SelectorManager

logger = logging.getLogger(__name__)

class LoginManager:
    """ログイン管理クラス"""
    
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
                logger.error("WebDriverが初期化されていません")
                return False
            
            driver = self.webdriver_manager.get_driver()
            wait = self.webdriver_manager.get_wait()
            
            if not driver or not wait:
                logger.error("WebDriverまたはWebDriverWaitが初期化されていません")
                return False
            
            # ページにアクセス
            if not self.webdriver_manager.navigate_to(login_url):
                return False
            
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"アクセス後のURL: {current_url}")
            
            # デバッグ用にHTMLを保存
            self.webdriver_manager.save_debug_html("debug/login_page_debug.html")
            
            # ログインフォームが表示されているかチェック
            if not self._check_login_form_exists(wait):
                logger.info("ログインフォームが見つかりません。既にログイン済みの可能性があります")
                return True
            
            # ログイン情報を入力
            if not self._input_credentials(driver, wait):
                return False
            
            # ログインボタンをクリック
            if not self._click_login_button(driver, wait):
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
                logger.error("WebDriverが初期化されていません")
                return False
            
            driver = self.webdriver_manager.get_driver()
            wait = self.webdriver_manager.get_wait()
            
            if not driver or not wait:
                logger.error("WebDriverまたはWebDriverWaitが初期化されていません")
                return False
            
            # ログインフォームを探す
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]')))
            password_field = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
            
            # ログイン情報を入力
            if self.email and self.password:
                email_field.clear()
                email_field.send_keys(self.email)
                password_field.clear()
                password_field.send_keys(self.password)
            else:
                logger.error("認証情報が設定されていません")
                return False
            
            # ログインボタンをクリック
            login_button = driver.find_element(By.CSS_SELECTOR, 'button#next')
            login_button.click()
            
            time.sleep(self.config.get("after_login", 5))
            
            current_url = self.webdriver_manager.get_current_url()
            logger.info(f"2回目ログイン後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"2回目ログイン処理エラー: {e}")
            return False
    
    def _check_login_form_exists(self, wait: WebDriverWait) -> bool:
        """ログインフォームが存在するかチェック"""
        try:
            selectors = self.selector_manager.get_login_selectors()
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["email_field"])))
            logger.info("ログインフォームが表示されています")
            return True
        except TimeoutException:
            return False
    
    def _input_credentials(self, driver, wait: WebDriverWait) -> bool:
        """認証情報を入力"""
        try:
            selectors = self.selector_manager.get_login_selectors()
            email_field = driver.find_element(By.CSS_SELECTOR, selectors["email_field"])
            password_field = driver.find_element(By.CSS_SELECTOR, selectors["password_field"])

            if self.email and self.password:
                email_field.clear()
                email_field.send_keys(self.email)
                password_field.clear()
                password_field.send_keys(self.password)
            else:
                logger.error("認証情報が設定されていません")
                return False
            
            # 入力されたパスワード値をログ出力（デバッグ用）
            try:
                actual_pw = password_field.get_attribute('value')
                logger.info(f"パスワード欄の値（デバッグ用）: {actual_pw}")
            except Exception as e:
                logger.warning(f"パスワード値取得エラー: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"認証情報入力エラー: {e}")
            return False
    
    def _click_login_button(self, driver, wait: WebDriverWait) -> bool:
        """ログインボタンをクリック"""
        try:
            selectors = self.selector_manager.get_login_selectors()
            
            # ログインボタンを探す（複数のセレクターを試す）
            login_button = None
            login_button_selectors = [
                selectors["login_button"],
                "input[type='submit']",
                "button:contains('ログイン')",
                "button:contains('Login')",
                "input[value*='ログイン']",
                "input[value*='Login']"
            ]
            
            for selector in login_button_selectors:
                try:
                    if ":contains(" in selector:
                        # XPathに変換
                        text = selector.split("'")[1]
                        xpath_selector = f"//button[contains(text(), '{text}')]"
                        login_button = driver.find_element(By.XPATH, xpath_selector)
                    else:
                        login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if login_button:
                        logger.info(f"ログインボタン発見: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if not login_button:
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
            current_url = self.webdriver_manager.get_current_url()
            # URLにloginが含まれていない場合はログイン済みと判断
            return "login" not in current_url.lower()
        except Exception:
            return False 