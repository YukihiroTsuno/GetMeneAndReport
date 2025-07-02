"""
食事履歴スクレイピング
広島大学生協の食事履歴を自動取得

Version: 1.4.0
Author: AI Assistant
Date: 2025-07-02
"""

__version__ = "1.4.0"

import logging
from typing import Dict, Any, List, Optional
from utils.logger import setup_logger
from utils.email_sender import EmailSender
from utils.webdriver_manager import WebDriverManager
from utils.selector_manager import SelectorManager
from utils.login_manager import LoginManager
from utils.navigation_manager import NavigationManager
from utils.data_extractor import DataExtractor
from utils.csv_handler import CSVHandler

# 設定をインポート
from config import EMAIL, PASSWORD, SELECTORS, WAIT_TIMES, SELENIUM_CONFIG, MEAL_PAGE_URL

logger = setup_logger()

class MealHistoryScraper:
    """食事履歴スクレイピングクラス（統合インターフェース）"""
    
    def __init__(self):
        # 設定を準備
        self.selenium_config = SELENIUM_CONFIG
        self.wait_times = WAIT_TIMES
        self.credentials = (EMAIL or "", PASSWORD or "")
        self.login_url = MEAL_PAGE_URL
        
        # 各マネージャーを初期化
        self.webdriver_manager = WebDriverManager(self.selenium_config)
        self.selector_manager = SelectorManager(SELECTORS)
        self.login_manager = LoginManager(
            self.webdriver_manager, 
            self.selector_manager, 
            self.credentials, 
            self.wait_times
        )
        self.navigation_manager = NavigationManager(
            self.webdriver_manager,
            self.selector_manager,
            self.login_manager,
            self.wait_times
        )
        self.data_extractor = DataExtractor(
            self.webdriver_manager,
            self.selector_manager,
            self.navigation_manager
        )
        
        # その他のコンポーネント
        self.email_sender = EmailSender()
        self.csv_handler = CSVHandler()
    
    def run(self) -> bool:
        """スクレイピングを実行"""
        try:
            logger.info("食事履歴スクレイピングを開始します")
            
            # WebDriverをセットアップ
            if not self.webdriver_manager.setup_driver():
                logger.error("WebDriverのセットアップに失敗しました")
                return False
            
            # ログイン
            if not self.login_manager.login(self.login_url):
                logger.error("ログインに失敗しました")
                return False
            
            # 食事履歴ページに遷移
            if not self.navigation_manager.navigate_to_meal_history():
                logger.error("食事履歴ページへの遷移に失敗しました")
                return False
            
            # ご利用明細を選択
            if not self.navigation_manager.select_usage_detail():
                logger.error("ご利用明細の選択に失敗しました")
                return False
            
            # 食事履歴データを抽出
            structured_data = self.data_extractor.extract_meal_data()
            
            if not structured_data:
                logger.error("食事履歴データの取得に失敗しました")
                return False
            
            # データの妥当性をチェック
            if not self.data_extractor.validate_extracted_data(structured_data):
                logger.warning("抽出されたデータに問題があります")
            
            # データサマリーを取得
            summary = self.data_extractor.get_data_summary(structured_data)
            logger.info(f"データ抽出完了: {summary}")
            
            # CSVファイルに保存
            csv_path = self.csv_handler.save_data(structured_data)
            if csv_path:
                logger.info(f"CSVファイルに保存しました: {csv_path}")
            
            # メール通知を送信
            self.email_sender.send_notification(structured_data)
            
            logger.info("食事履歴スクレイピングが完了しました")
            return True
            
        except Exception as e:
            logger.error(f"スクレイピング実行エラー: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        self.webdriver_manager.cleanup()
    
    def get_data_summary(self) -> Optional[Dict[str, Any]]:
        """データサマリーを取得（テスト用）"""
        try:
            # WebDriverをセットアップ
            if not self.webdriver_manager.setup_driver():
                return None
            
            # ログイン
            if not self.login_manager.login(self.login_url):
                return None
            
            # 食事履歴ページに遷移
            if not self.navigation_manager.navigate_to_meal_history():
                return None
            
            # ご利用明細を選択
            if not self.navigation_manager.select_usage_detail():
                return None
            
            # 食事履歴データを抽出
            structured_data = self.data_extractor.extract_meal_data()
            
            if not structured_data:
                return None
            
            # データサマリーを取得
            return self.data_extractor.get_data_summary(structured_data)
            
        except Exception as e:
            logger.error(f"データサマリー取得エラー: {e}")
            return None
        
        finally:
            self.cleanup()

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