"""
データ処理機能
食事履歴データの解析、フィルタリング、変換を行う
"""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """データ処理クラス"""
    
    @staticmethod
    def parse_date_from_string(date_str: str) -> Optional[datetime]:
        """日付文字列から日付オブジェクトを解析"""
        try:
            # "12月19日(木[4])" のような形式から日付を抽出
            match = re.search(r'(\d+)月(\d+)日', date_str)
            if match:
                month = int(match.group(1))
                day = int(match.group(2))
                # 現在の年を取得
                current_year = datetime.now().year
                # 月が現在の月より大きい場合は前年
                if month > datetime.now().month:
                    year = current_year - 1
                else:
                    year = current_year
                return datetime(year, month, day)
        except Exception as e:
            logger.warning(f"日付解析エラー: {e}")
        return None
    
    @staticmethod
    def clean_date_string(date_str: str) -> str:
        """日付文字列から曜日の部分を削除"""
        # "(月火水木金土日[0-6])" のパターンを削除
        cleaned_date = re.sub(r'\([月火水木金土日]\[[0-6]\]\)', '', date_str)
        return cleaned_date.strip()
    
    @staticmethod
    def format_date_with_weekday(date_str: str) -> str:
        """日付文字列を曜日付きでフォーマット"""
        # 元の日付文字列から曜日を抽出
        weekday_match = re.search(r'\(([月火水木金土日])\[([0-6])\]\)', date_str)
        if weekday_match:
            weekday_jp = weekday_match.group(1)
            
            # 日付部分を取得
            date_part = re.sub(r'\([月火水木金土日]\[[0-6]\]\)', '', date_str).strip()
            
            return f"{date_part} ({weekday_jp})"
        else:
            # 曜日情報がない場合は元の文字列を返す
            return date_str
    
    @staticmethod
    def filter_recent_ten_days_data(structured_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """最新の10日間分のデータのみをフィルタリング"""
        if not structured_data:
            return structured_data
        
        # 現在の日付から10日前の日付を計算
        ten_days_ago = datetime.now() - timedelta(days=10)
        
        # データを日付でソート（新しい順）- Noneの場合は最小値として扱う
        def sort_key(data):
            date_obj = DataProcessor.parse_date_from_string(data['date'])
            return date_obj if date_obj else datetime.min
        
        sorted_data = sorted(structured_data, key=sort_key, reverse=True)
        
        # 10日間以内のデータのみをフィルタリング
        recent_data = []
        for data in sorted_data:
            date_obj = DataProcessor.parse_date_from_string(data['date'])
            if date_obj and date_obj >= ten_days_ago:
                recent_data.append(data)
        
        logger.info(f"全データ: {len(structured_data)}件, 10日間分データ: {len(recent_data)}件")
        return recent_data
    
    @staticmethod
    def group_data_by_date(structured_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """データを日付ごとにグループ化"""
        grouped_data = {}
        for data in structured_data:
            original_date = data['date']  # 元の日付文字列を保持
            clean_date = DataProcessor.clean_date_string(original_date)  # グループ化用にクリーンアップ
            if clean_date not in grouped_data:
                grouped_data[clean_date] = []
            grouped_data[clean_date].append(data)
        return grouped_data
    
    @staticmethod
    def format_menu_items(menu_items: Any) -> str:
        """メニューアイテムを改行付きHTMLに変換"""
        if isinstance(menu_items, list):
            # リストの場合は`, `で結合してから改行に変換
            menu_text = ', '.join(menu_items)
        else:
            # 文字列の場合はそのまま使用
            menu_text = str(menu_items)
        
        # `, `を改行に変換
        return menu_text.replace(', ', '<br>')
    
    @staticmethod
    def get_time_icon(hour: str) -> str:
        """時間帯に応じてアイコンを取得"""
        if '朝' in hour or 'breakfast' in hour.lower():
            return "🌅"
        elif '昼' in hour or 'lunch' in hour.lower():
            return "☀️"
        elif '夜' in hour or 'dinner' in hour.lower():
            return "🌙"
        else:
            return "🍽️" 