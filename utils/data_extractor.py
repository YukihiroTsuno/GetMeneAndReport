"""
データ抽出機能
Webページから食事履歴データを抽出する
"""

import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import Dict, Any, List, Optional
from .webdriver_manager import WebDriverManager
from .selector_manager import SelectorManager
from .navigation_manager import NavigationManager

logger = logging.getLogger(__name__)

class DataExtractor:
    """データ抽出クラス"""
    
    def __init__(self, webdriver_manager: WebDriverManager, selector_manager: SelectorManager, navigation_manager: NavigationManager):
        self.webdriver_manager = webdriver_manager
        self.selector_manager = selector_manager
        self.navigation_manager = navigation_manager
    
    def extract_meal_data(self) -> List[Dict[str, Any]]:
        """食事履歴データを抽出"""
        try:
            logger.info("食事履歴データの抽出を開始します")
            
            if not self.webdriver_manager.is_ready():
                logger.error("WebDriverが初期化されていません")
                return []
            
            driver = self.webdriver_manager.get_driver()
            
            if not driver:
                logger.error("WebDriverが初期化されていません")
                return []
            
            # 「もっと見る」ボタンをクリック
            self.navigation_manager.click_more_button()
            
            # 食事履歴記事を取得
            selectors = self.selector_manager.get_data_extraction_selectors()
            history_articles = driver.find_elements(By.CSS_SELECTOR, selectors["history_articles"])
            logger.info(f"発見された食事履歴記事数: {len(history_articles)}")
            
            structured_data = []
            
            for article in history_articles:
                try:
                    # 日付情報を取得
                    date_element = article.find_element(By.CSS_SELECTOR, selectors["date_element"])
                    month = date_element.find_element(By.CSS_SELECTOR, selectors["month_span"]).text.strip()
                    date = date_element.find_element(By.CSS_SELECTOR, selectors["date_span"]).text.strip()
                    day = date_element.find_element(By.CSS_SELECTOR, selectors["day_span"]).text.strip()
                    date_str = f"{month}月{date}日({day})"
                    
                    # 詳細要素を取得
                    detail_elements = article.find_elements(By.CSS_SELECTOR, selectors["detail_elements"])
                    
                    for detail_element in detail_elements:
                        try:
                            # 時刻、メニュー、金額を取得
                            hour = detail_element.find_element(By.CSS_SELECTOR, selectors["hour_element"]).text.strip()
                            
                            menu_elements = detail_element.find_elements(By.CSS_SELECTOR, selectors["menu_elements"])
                            menus = [menu.text.strip() for menu in menu_elements if menu.text.strip()]
                            
                            amount_element = detail_element.find_element(By.CSS_SELECTOR, selectors["amount_element"])
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
    
    def validate_extracted_data(self, data: List[Dict[str, Any]]) -> bool:
        """抽出されたデータの妥当性をチェック"""
        if not data:
            logger.warning("抽出されたデータがありません")
            return False
        
        # 必須フィールドのチェック
        required_fields = ['date', 'hour', 'menus', 'amount']
        for item in data:
            for field in required_fields:
                if field not in item:
                    logger.error(f"必須フィールドが不足しています: {field}")
                    return False
                if not item[field]:
                    logger.warning(f"フィールドが空です: {field}")
        
        logger.info(f"データ妥当性チェック完了: {len(data)}件")
        return True
    
    def get_data_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """抽出されたデータのサマリーを取得"""
        if not data:
            return {"count": 0, "date_range": None, "total_amount": 0}
        
        # 日付範囲を取得
        dates = [item['date'] for item in data]
        date_range = f"{min(dates)} 〜 {max(dates)}" if dates else None
        
        # 合計金額を計算（数値部分のみ抽出）
        total_amount = 0
        for item in data:
            try:
                amount_str = item['amount'].replace('¥', '').replace(',', '')
                total_amount += int(amount_str)
            except (ValueError, AttributeError):
                continue
        
        return {
            "count": len(data),
            "date_range": date_range,
            "total_amount": total_amount
        } 