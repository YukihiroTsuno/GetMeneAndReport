"""
セレクター管理機能
Web要素のセレクターを一元管理し、サイト構造変更に対応
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SelectorConfig:
    """セレクター設定データクラス"""
    # ログインフォーム
    email_field: str
    password_field: str
    login_button: str
    
    # ナビゲーション
    meal_history_link: str
    meal_history_xpath: str
    usage_detail_link: str
    
    # データ抽出
    history_articles: str
    date_element: str
    month_span: str
    date_span: str
    day_span: str
    detail_elements: str
    hour_element: str
    menu_elements: str
    amount_element: str
    
    # その他
    more_button: str

class SelectorManager:
    """セレクター管理クラス"""
    
    def __init__(self, selectors: Optional[Dict[str, str]] = None):
        self.selectors = selectors or self._get_default_selectors()
        self.selector_config = self._create_selector_config()
    
    def _get_default_selectors(self) -> Dict[str, str]:
        """デフォルトのセレクターを取得"""
        return {
            # ログインフォーム
            "email_field": "input#form_email",
            "password_field": "input#form_password",
            "login_button": "input[type='submit'][value='ログインする']",
            
            # ミール利用履歴リンク
            "meal_history_link": "a[href*='cn-univ.coop']",
            "meal_history_xpath": "//a[contains(text(), 'ミール利用履歴')]",
            
            # ご利用明細
            "usage_detail_link": "a[href*='detail']",
            
            # 食事履歴データ
            "history_articles": "article.history-contents",
            "date_element": ".history-contents-date",
            "month_span": ".month",
            "date_span": ".date",
            "day_span": ".day",
            "detail_elements": ".history-contents-detail",
            "hour_element": ".hour",
            "menu_elements": ".item li",
            "amount_element": ".total .amount",
            
            # もっと見るボタン
            "more_button": ".btn-more"
        }
    
    def _create_selector_config(self) -> SelectorConfig:
        """セレクター設定オブジェクトを作成"""
        return SelectorConfig(
            email_field=self.selectors["email_field"],
            password_field=self.selectors["password_field"],
            login_button=self.selectors["login_button"],
            meal_history_link=self.selectors["meal_history_link"],
            meal_history_xpath=self.selectors["meal_history_xpath"],
            usage_detail_link=self.selectors["usage_detail_link"],
            history_articles=self.selectors["history_articles"],
            date_element=self.selectors["date_element"],
            month_span=self.selectors["month_span"],
            date_span=self.selectors["date_span"],
            day_span=self.selectors["day_span"],
            detail_elements=self.selectors["detail_elements"],
            hour_element=self.selectors["hour_element"],
            menu_elements=self.selectors["menu_elements"],
            amount_element=self.selectors["amount_element"],
            more_button=self.selectors["more_button"]
        )
    
    def get_selector(self, key: str) -> str:
        """指定されたキーのセレクターを取得"""
        return self.selectors.get(key, "")
    
    def get_login_selectors(self) -> Dict[str, str]:
        """ログイン関連のセレクターを取得"""
        return {
            "email_field": self.selectors["email_field"],
            "password_field": self.selectors["password_field"],
            "login_button": self.selectors["login_button"]
        }
    
    def get_navigation_selectors(self) -> Dict[str, str]:
        """ナビゲーション関連のセレクターを取得"""
        return {
            "meal_history_link": self.selectors["meal_history_link"],
            "meal_history_xpath": self.selectors["meal_history_xpath"],
            "usage_detail_link": self.selectors["usage_detail_link"]
        }
    
    def get_data_extraction_selectors(self) -> Dict[str, str]:
        """データ抽出関連のセレクターを取得"""
        return {
            "history_articles": self.selectors["history_articles"],
            "date_element": self.selectors["date_element"],
            "month_span": self.selectors["month_span"],
            "date_span": self.selectors["date_span"],
            "day_span": self.selectors["day_span"],
            "detail_elements": self.selectors["detail_elements"],
            "hour_element": self.selectors["hour_element"],
            "menu_elements": self.selectors["menu_elements"],
            "amount_element": self.selectors["amount_element"],
            "more_button": self.selectors["more_button"]
        }
    
    def update_selectors(self, new_selectors: Dict[str, str]) -> None:
        """セレクターを更新"""
        self.selectors.update(new_selectors)
        self.selector_config = self._create_selector_config()
        logger.info(f"セレクターを更新しました: {list(new_selectors.keys())}")
    
    def get_all_selectors(self) -> Dict[str, str]:
        """すべてのセレクターを取得"""
        return self.selectors.copy()
    
    def validate_selectors(self) -> bool:
        """セレクターの妥当性をチェック"""
        required_keys = [
            "email_field", "password_field", "login_button",
            "meal_history_link", "usage_detail_link",
            "history_articles", "date_element", "detail_elements"
        ]
        
        missing_keys = [key for key in required_keys if key not in self.selectors]
        
        if missing_keys:
            logger.error(f"必須セレクターが不足しています: {missing_keys}")
            return False
        
        return True 