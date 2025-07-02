"""
HTMLテンプレート機能
iPhone最適化されたHTMLメールテンプレートを生成する
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from .data_processor import DataProcessor

logger = logging.getLogger(__name__)

class HTMLTemplateGenerator:
    """HTMLテンプレート生成クラス"""
    
    def __init__(self, email_width: int = 400):
        self.email_width = email_width
    
    def create_email_body(self, structured_data: List[Dict[str, Any]], total_data_count: Optional[int] = None) -> str:
        """iPhone最適化されたHTMLメール本文を作成"""
        if not structured_data:
            return self._create_empty_template()
        
        # データを日付ごとにグループ化
        grouped_data = DataProcessor.group_data_by_date(structured_data)
        sorted_dates = sorted(grouped_data.keys(), reverse=True)
        
        # 現在の日時を取得
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        # サマリー情報を作成
        summary_text = self._create_summary_text(structured_data, total_data_count)
        
        # HTMLテンプレートを生成
        html = self._create_header(current_time)
        html += self._create_summary_section(summary_text, structured_data)
        html += self._create_meal_sections(grouped_data, sorted_dates)
        html += self._create_footer()
        
        return html
    
    def _create_empty_template(self) -> str:
        """空のデータ用テンプレート"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        html = self._create_header(current_time)
        html += f"""
                        <td style="padding: 12px;">
                            <div style="text-align: center; padding: 40px 20px; color: #666666; font-family: Arial, sans-serif;">
                                <div style="font-size: 19px; margin-bottom: 8px;">📭</div>
                                <div style="font-size: 17px;">データがありません</div>
                                <div style="font-size: 13px; margin-top: 8px;">取得期間内に食事履歴が見つかりませんでした</div>
                            </div>
                        </td>
                    </tr>
                    {self._create_footer()}
        """
        return html
    
    def _create_header(self, current_time: str) -> str:
        """ヘッダー部分を生成"""
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>食事履歴データ</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f0f0f0; color: #333333; line-height: 1.5;">
    <!-- メインコンテナテーブル -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0f0f0;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <!-- メールコンテンツテーブル -->
                <table width="{self.email_width}" cellpadding="0" cellspacing="0" style="max-width: {self.email_width}px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    
                    <!-- ヘッダー -->
                    <tr>
                        <td style="background-color: #007AFF; color: #ffffff; padding: 16px; text-align: center;">
                            <h1 style="margin: 0; font-size: 22px; font-weight: 600; font-family: Arial, sans-serif;">🍽️ 食事履歴データ</h1>
                            <div style="margin: 6px 0 0 0; font-size: 13px; opacity: 0.9; font-family: Arial, sans-serif;">取得完了: {current_time}</div>
                        </td>
                    </tr>
                    
                    <!-- コンテンツエリア -->
                    <tr>
        """
    
    def _create_summary_text(self, structured_data: List[Dict[str, Any]], total_data_count: Optional[int]) -> str:
        """サマリーテキストを生成"""
        if total_data_count and total_data_count > len(structured_data):
            return f"取得件数: <strong>{len(structured_data)}件</strong> (全{total_data_count}件のうち最新10日間分)"
        else:
            return f"取得件数: <strong>{len(structured_data)}件</strong>"
    
    def _create_summary_section(self, summary_text: str, structured_data: List[Dict[str, Any]]) -> str:
        """サマリー情報セクションを生成"""
        period_text = f"取得期間: <strong>{DataProcessor.format_date_with_weekday(structured_data[-1]['date']) if structured_data else 'N/A'} 〜 {DataProcessor.format_date_with_weekday(structured_data[0]['date']) if structured_data else 'N/A'}</strong>"
        
        return f"""
                        <td style="padding: 12px;">
                            
                            <!-- サマリー情報 -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f2f2f7; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #007AFF;">
                                <tr>
                                    <td style="padding: 10px;">
                                        <h3 style="margin: 0 0 6px 0; color: #007AFF; font-size: 16px; font-family: Arial, sans-serif;">📊 取得サマリー</h3>
                                        <p style="margin: 0; font-size: 13px; color: #666666; font-family: Arial, sans-serif;">{summary_text}</p>
                                        <p style="margin: 3px 0 0 0; font-size: 13px; color: #666666; font-family: Arial, sans-serif;">{period_text}</p>
                                    </td>
                                </tr>
                            </table>
        """
    
    def _create_meal_sections(self, grouped_data: Dict[str, List[Dict[str, Any]]], sorted_dates: List[str]) -> str:
        """食事セクションを生成"""
        html = ""
        
        for date in sorted_dates:
            meals = grouped_data[date]
            # 最初の食事データから元の日付文字列を取得
            original_date = meals[0]['date'] if meals else date
            formatted_date = DataProcessor.format_date_with_weekday(original_date)
            
            html += f"""
                            <!-- 日付セクション -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px; border: 1px solid #e5e5ea; border-radius: 6px; overflow: hidden;">
                                <!-- 日付ヘッダー -->
                                <tr>
                                    <td style="background-color: #8e8e93; color: #ffffff; padding: 10px 12px; font-weight: 600; font-size: 16px; text-align: center; font-family: Arial, sans-serif;">📅 {formatted_date}</td>
                                </tr>
            """
            
            for i, meal in enumerate(meals):
                time_icon = DataProcessor.get_time_icon(meal['hour'])
                menu_html = DataProcessor.format_menu_items(meal['menus'])
                bg_color = "#f9f9f9" if i % 2 == 1 else "#ffffff"
                
                html += f"""
                                <!-- 食事アイテム -->
                                <tr>
                                    <td style="padding: 10px 12px; border-bottom: 1px solid #e5e5ea; background-color: {bg_color};">
                                        <div style="background-color: #007AFF; color: #ffffff; padding: 3px 6px; border-radius: 3px; font-size: 12px; font-weight: 500; display: inline-block; margin-bottom: 3px; font-family: Arial, sans-serif;">{time_icon} {meal['hour']}</div>
                                        <div style="color: #666666; font-size: 14px; margin-bottom: 3px; font-family: Arial, sans-serif;">{menu_html}</div>
                                        <div style="color: #34c759; font-weight: 500; font-size: 13px; font-family: Arial, sans-serif;">💰 {meal['amount']}</div>
                                    </td>
                                </tr>
                """
            
            html += """
                            </table>
            """
        
        return html
    
    def _create_footer(self) -> str:
        """フッター部分を生成"""
        return """
                        </td>
                    </tr>
                    
                    <!-- フッター -->
                    <tr>
                        <td style="background-color: #f2f2f7; padding: 10px 12px; text-align: center; border-top: 1px solid #e5e5ea;">
                            <div style="font-size: 11px; color: #666666; font-family: Arial, sans-serif;">このメールは自動生成されました</div>
                            <div style="margin-top: 4px; padding-top: 4px; border-top: 1px solid #d1d1d6; font-size: 11px; color: #666666; font-family: Arial, sans-serif;">
                                <strong>GetMeneAndReport</strong> v1.2.0
                            </div>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """ 