"""
食事履歴スクレイピング
広島大学生協の食事履歴を取得してCSVファイルに保存

Version: 1.0.0
Author: AI Assistant
Date: 2024-12-19
"""

__version__ = "1.0.0"

import time
from typing import Optional, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    MEAL_PAGE_URL, EMAIL, PASSWORD, SELENIUM_CONFIG, 
    SELECTORS, WAIT_TIMES
)
from utils import setup_logger, EmailSender, CSVHandler

logger = setup_logger()

class MealHistoryScraper:
    """食事履歴スクレイピングクラス"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.email_sender = EmailSender()
        self.csv_handler = CSVHandler()
    
    def setup_driver(self):
        """Chromeドライバーをセットアップ"""
        try:
            logger.info("Chromeドライバーをセットアップ中...")
            
            # Chromeオプションを設定
            chrome_options = Options()
            if SELENIUM_CONFIG["headless"]:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument(f"--window-size={SELENIUM_CONFIG['window_size'][0]},{SELENIUM_CONFIG['window_size'][1]}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            # ChromeDriverManagerでドライバーをインストール
            service = Service(ChromeDriverManager().install())
            
            # WebDriverを初期化
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # タイムアウト設定
            self.driver.implicitly_wait(SELENIUM_CONFIG["implicit_wait"])
            self.driver.set_page_load_timeout(SELENIUM_CONFIG["page_load_timeout"])
            self.driver.set_script_timeout(SELENIUM_CONFIG["script_timeout"])
            
            # WebDriverWaitを設定
            self.wait = WebDriverWait(self.driver, SELENIUM_CONFIG["implicit_wait"])
            
            logger.info("Chromeドライバーのセットアップが完了しました")
            return True
            
        except Exception as e:
            logger.error(f"Chromeドライバーのセットアップエラー: {e}")
            return False
    
    def login(self):
        """ログイン処理"""
        try:
            logger.info("ログイン処理を開始します")
            
            if not self.driver or not self.wait:
                logger.error("ドライバーが初期化されていません")
                return False
            
            # ページにアクセス
            self.driver.get(MEAL_PAGE_URL)
            time.sleep(WAIT_TIMES["page_load"])
            
            current_url = self.driver.current_url
            logger.info(f"アクセス後のURL: {current_url}")
            
            # デバッグ用にHTMLを保存
            try:
                html = self.driver.page_source
                with open("debug/login_page_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("デバッグ用HTMLを保存しました: debug/login_page_debug.html")
            except Exception as e:
                logger.warning(f"HTML保存エラー: {e}")
            
            # ログインフォームが表示されているかチェック
            try:
                email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["email_field"])))
                logger.info("ログインフォームが表示されています")
            except TimeoutException:
                logger.info("ログインフォームが見つかりません。既にログイン済みの可能性があります")
                return True
            
            # ログイン情報を入力
            email_field = self.driver.find_element(By.CSS_SELECTOR, SELECTORS["email_field"])
            password_field = self.driver.find_element(By.CSS_SELECTOR, SELECTORS["password_field"])

            email_field.clear()
            email_field.send_keys(EMAIL)
            logger.info(f"メールアドレスを入力: {EMAIL}")

            password_field.clear()
            password_field.send_keys(PASSWORD)
            logger.info("パスワードを入力しました")
            # 入力されたパスワード値をログ出力（デバッグ用）
            try:
                actual_pw = password_field.get_attribute('value')
                logger.info(f"パスワード欄の値（デバッグ用）: {actual_pw}")
            except Exception as e:
                logger.warning(f"パスワード値取得エラー: {e}")
            
            # ログインボタンを探す（複数のセレクターを試す）
            login_button = None
            login_button_selectors = [
                SELECTORS["login_button"],
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
                        login_button = self.driver.find_element(By.XPATH, xpath_selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
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
            
            # ログイン後の処理を待機
            time.sleep(WAIT_TIMES["after_login"])
            
            current_url = self.driver.current_url
            logger.info(f"ログイン後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"ログイン処理エラー: {e}")
            return False
    
    def navigate_to_meal_history(self):
        """食事履歴ページに遷移"""
        try:
            logger.info("食事履歴ページに遷移中...")
            
            if not self.driver or not self.wait:
                logger.error("ドライバーが初期化されていません")
                return False
            
            # ミール利用履歴リンクを探してクリック
            meal_history_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["meal_history_link"]))
            )
            
            href = meal_history_link.get_attribute("href")
            link_text = meal_history_link.text
            logger.info(f"リンク先URL: {href}")
            logger.info(f"リンクテキスト: {link_text.strip() if link_text else 'N/A'}")
            
            meal_history_link.click()
            time.sleep(WAIT_TIMES["after_click"])
            
            # 遷移後の確認
            current_url = self.driver.current_url
            logger.info(f"遷移後のURL: {current_url}")
            
            # 2回目のログインが必要な場合
            if "login" in current_url.lower():
                logger.info("2回目のログインが必要です")
                return self.perform_second_login()
            
            return True
            
        except Exception as e:
            logger.error(f"食事履歴ページ遷移エラー: {e}")
            return False
    
    def perform_second_login(self):
        """2回目のログイン処理"""
        try:
            logger.info("2回目のログイン処理を開始します")
            
            if not self.driver or not self.wait:
                logger.error("ドライバーが初期化されていません")
                return False
            
            # ログインフォームを探す
            email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]')))
            password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
            
            # ログイン情報を入力
            email_field.clear()
            email_field.send_keys(EMAIL)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            # ログインボタンをクリック
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button#next')
            login_button.click()
            
            time.sleep(WAIT_TIMES["after_login"])
            
            current_url = self.driver.current_url
            logger.info(f"2回目ログイン後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"2回目ログイン処理エラー: {e}")
            return False
    
    def select_usage_detail(self):
        """ご利用明細を選択"""
        try:
            logger.info("ご利用明細を選択中...")
            
            if not self.driver or not self.wait:
                logger.error("ドライバーが初期化されていません")
                return False
            
            # ご利用明細リンクを探してクリック
            usage_detail_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["usage_detail_link"]))
            )
            
            usage_detail_link.click()
            time.sleep(WAIT_TIMES["after_click"])
            
            current_url = self.driver.current_url
            logger.info(f"ご利用明細遷移後のURL: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"ご利用明細選択エラー: {e}")
            return False
    
    def extract_meal_data(self):
        """食事履歴データを抽出"""
        try:
            logger.info("食事履歴データの抽出を開始します")
            
            if not self.driver:
                logger.error("ドライバーが初期化されていません")
                return []
            
            # 「もっと見る」ボタンがあればクリック
            try:
                more_button = self.driver.find_element(By.CSS_SELECTOR, SELECTORS["more_button"])
                if more_button.is_displayed():
                    logger.info("「もっと見る」ボタンをクリックします")
                    more_button.click()
                    time.sleep(WAIT_TIMES["element_load"])
            except NoSuchElementException:
                logger.info("「もっと見る」ボタンは見つかりませんでした")
            
            # 食事履歴記事を取得
            history_articles = self.driver.find_elements(By.CSS_SELECTOR, SELECTORS["history_articles"])
            logger.info(f"発見された食事履歴記事数: {len(history_articles)}")
            
            structured_data = []
            
            for article in history_articles:
                try:
                    # 日付情報を取得
                    date_element = article.find_element(By.CSS_SELECTOR, SELECTORS["date_element"])
                    month = date_element.find_element(By.CSS_SELECTOR, SELECTORS["month_span"]).text.strip()
                    date = date_element.find_element(By.CSS_SELECTOR, SELECTORS["date_span"]).text.strip()
                    day = date_element.find_element(By.CSS_SELECTOR, SELECTORS["day_span"]).text.strip()
                    date_str = f"{month}月{date}日({day})"
                    
                    # 詳細要素を取得
                    detail_elements = article.find_elements(By.CSS_SELECTOR, SELECTORS["detail_elements"])
                    
                    for detail_element in detail_elements:
                        try:
                            # 時刻、メニュー、金額を取得
                            hour = detail_element.find_element(By.CSS_SELECTOR, SELECTORS["hour_element"]).text.strip()
                            
                            menu_elements = detail_element.find_elements(By.CSS_SELECTOR, SELECTORS["menu_elements"])
                            menus = [menu.text.strip() for menu in menu_elements if menu.text.strip()]
                            
                            amount_element = detail_element.find_element(By.CSS_SELECTOR, SELECTORS["amount_element"])
                            amount = amount_element.text.strip()
                            
                            # 構造化データに追加
                            data = {
                                'date': date_str,
                                'hour': hour,
                                'menus': menus,
                                'amount': amount
                            }
                            structured_data.append(data)
                            
                        except Exception as e:
                            logger.warning(f"詳細要素の解析でエラー: {e}")
                            continue
                    
                except Exception as e:
                    logger.warning(f"記事の解析でエラー: {e}")
                    continue
            
            logger.info(f"食事履歴データの抽出が完了しました。取得件数: {len(structured_data)}")
            return structured_data
            
        except Exception as e:
            logger.error(f"食事履歴データ抽出エラー: {e}")
            return []
    
    def run(self):
        """スクレイピングを実行"""
        try:
            logger.info("食事履歴スクレイピングを開始します")
            
            # ドライバーをセットアップ
            if not self.setup_driver():
                return False
            
            # ログイン
            if not self.login():
                return False
            
            # 食事履歴ページに遷移
            if not self.navigate_to_meal_history():
                return False
            
            # ご利用明細を選択
            if not self.select_usage_detail():
                return False
            
            # 食事履歴データを抽出
            structured_data = self.extract_meal_data()
            
            if not structured_data:
                logger.error("食事履歴データの取得に失敗しました")
                return False
            
            # CSVファイルに保存
            csv_file_path = self.csv_handler.save_data(structured_data)
            
            # メール通知を送信
            self.email_sender.send_notification(structured_data, csv_file_path)
            
            logger.info("食事履歴スクレイピングが完了しました")
            return True
            
        except Exception as e:
            logger.error(f"スクレイピング実行エラー: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        try:
            if self.driver:
                time.sleep(WAIT_TIMES["before_close"])
                self.driver.quit()
                logger.info("ブラウザを閉じました")
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")

def main():
    """メイン実行関数"""
    scraper = MealHistoryScraper()
    success = scraper.run()
    
    if success:
        logger.info("スクレイピングが正常に完了しました")
    else:
        logger.error("スクレイピングが失敗しました")

if __name__ == "__main__":
    main() 