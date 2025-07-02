"""
データ抽出機能（Playwright版）
Webページから食事履歴データを抽出する
"""

import logging
from playwright.sync_api import Page
from typing import Dict, Any, List, Optional
from .webdriver_manager import WebDriverManager
from .selector_manager import SelectorManager
from .navigation_manager import NavigationManager

logger = logging.getLogger(__name__)

class DataExtractor:
    """データ抽出クラス（Playwright版）"""
    
    def __init__(self, webdriver_manager: WebDriverManager, selector_manager: SelectorManager, navigation_manager: NavigationManager):
        self.webdriver_manager = webdriver_manager
        self.selector_manager = selector_manager
        self.navigation_manager = navigation_manager
    
    def extract_meal_data(self) -> List[Dict[str, Any]]:
        """食事履歴データを抽出"""
        try:
            logger.info("食事履歴データの抽出を開始します")
            
            if not self.webdriver_manager.is_ready():
                logger.error("Playwrightブラウザが初期化されていません")
                return []
            
            page = self.webdriver_manager.get_page()
            
            if not page:
                logger.error("Pageオブジェクトが初期化されていません")
                return []
            
            # 「もっと見る」ボタンをクリック
            self.navigation_manager.click_more_button()
            
            # 食事履歴記事を取得
            selectors = self.selector_manager.get_data_extraction_selectors()
            history_articles = page.locator(selectors["history_articles"]).all()
            logger.info(f"発見された食事履歴記事数: {len(history_articles)}")
            
            structured_data = []
            
            for article in history_articles:
                try:
                    # 日付情報を取得
                    date_element = article.locator(selectors["date_element"])
                    month = date_element.locator(selectors["month_span"]).text_content() or ""
                    date = date_element.locator(selectors["date_span"]).text_content() or ""
                    day = date_element.locator(selectors["day_span"]).text_content() or ""
                    date_str = f"{month.strip()}月{date.strip()}日({day.strip()})"
                    
                    # 詳細要素を取得
                    detail_elements = article.locator(selectors["detail_elements"]).all()
                    
                    for detail_element in detail_elements:
                        try:
                            # 時刻、メニュー、金額を取得
                            hour = detail_element.locator(selectors["hour_element"]).text_content() or ""
                            
                            menu_elements = detail_element.locator(selectors["menu_elements"]).all()
                            menus = []
                            for menu in menu_elements:
                                text = menu.text_content()
                                if text and text.strip():
                                    menus.append(text.strip())
                            
                            amount_element = detail_element.locator(selectors["amount_element"])
                            amount = amount_element.text_content() or ""
                            
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