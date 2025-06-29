"""
メール送信機能
食事履歴データをHTMLメールで送信（iPhone最適化）
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
import os
import re

# EMAIL_CONFIGを直接定義
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "sender_email": os.getenv("SENDER_EMAIL", os.getenv("EMAIL", "")),
    "sender_password": os.getenv("SENDER_PASSWORD", os.getenv("PASSWORD", "")),
    "recipient_email": os.getenv("RECIPIENT_EMAIL", "")
}

logger = logging.getLogger(__name__)

class EmailSender:
    """メール送信クラス"""
    
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG["smtp_server"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.sender_email = EMAIL_CONFIG["sender_email"]
        self.sender_password = EMAIL_CONFIG["sender_password"]
        self.recipient_email = EMAIL_CONFIG["recipient_email"]
    
    def _parse_date_from_string(self, date_str):
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
    
    def _filter_recent_week_data(self, structured_data):
        """最新の1週間分のデータのみをフィルタリング"""
        if not structured_data:
            return structured_data
        
        # 現在の日付から1週間前の日付を計算
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # データを日付でソート（新しい順）- Noneの場合は最小値として扱う
        def sort_key(data):
            date_obj = self._parse_date_from_string(data['date'])
            return date_obj if date_obj else datetime.min
        
        sorted_data = sorted(structured_data, key=sort_key, reverse=True)
        
        # 1週間以内のデータのみをフィルタリング
        recent_data = []
        for data in sorted_data:
            date_obj = self._parse_date_from_string(data['date'])
            if date_obj and date_obj >= one_week_ago:
                recent_data.append(data)
        
        logger.info(f"全データ: {len(structured_data)}件, 1週間分データ: {len(recent_data)}件")
        return recent_data
    
    def send_notification(self, structured_data):
        """食事履歴データの通知メールを送信（HTML形式）"""
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.warning("メール設定が不完全なため、メール送信をスキップします")
            return False
        
        try:
            # 最新の1週間分のデータのみをフィルタリング
            recent_data = self._filter_recent_week_data(structured_data)
            
            # HTMLメール本文を作成
            html_body = self._create_html_email_body(recent_data, len(structured_data))
            
            # メールオブジェクトを作成
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"ミールカード　食べたもの {datetime.now().strftime('%Y年%m月%d日')}"
            
            # HTML本文を追加
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # メールを送信
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info("HTMLメール通知を送信しました")
            return True
            
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            return False
    
    def _clean_date_string(self, date_str):
        """日付文字列から曜日の部分を削除"""
        # "(月火水木金土日[0-6])" のパターンを削除
        cleaned_date = re.sub(r'\([月火水木金土日]\[[0-6]\]\)', '', date_str)
        return cleaned_date.strip()
    
    def _format_date_with_weekday(self, date_str):
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
    
    def _create_html_email_body(self, structured_data, total_data_count=None):
        """iPhone最適化されたHTMLメール本文を作成（インラインCSS + テーブルレイアウト）"""
        # 現在の日時を取得
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        # データを日付ごとにグループ化（元の日付文字列を保持）
        grouped_data = {}
        for data in structured_data:
            original_date = data['date']  # 元の日付文字列を保持
            clean_date = self._clean_date_string(original_date)  # グループ化用にクリーンアップ
            if clean_date not in grouped_data:
                grouped_data[clean_date] = []
            grouped_data[clean_date].append(data)
        
        # 日付を降順でソート
        sorted_dates = sorted(grouped_data.keys(), reverse=True)
        
        # サマリー情報を作成
        if total_data_count and total_data_count > len(structured_data):
            summary_text = f"取得件数: <strong>{len(structured_data)}件</strong> (全{total_data_count}件のうち最新1週間分)"
        else:
            summary_text = f"取得件数: <strong>{len(structured_data)}件</strong>"
        
        html = f"""
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
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    
                    <!-- ヘッダー -->
                    <tr>
                        <td style="background-color: #007AFF; color: #ffffff; padding: 20px; text-align: center;">
                            <h1 style="margin: 0; font-size: 20px; font-weight: 600; font-family: Arial, sans-serif;">🍽️ 食事履歴データ</h1>
                            <div style="margin: 8px 0 0 0; font-size: 12px; opacity: 0.9; font-family: Arial, sans-serif;">取得完了: {current_time}</div>
                        </td>
                    </tr>
                    
                    <!-- コンテンツエリア -->
                    <tr>
                        <td style="padding: 16px;">
                            
                            <!-- サマリー情報 -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f2f2f7; border-radius: 6px; margin-bottom: 16px; border-left: 3px solid #007AFF;">
                                <tr>
                                    <td style="padding: 12px;">
                                        <h3 style="margin: 0 0 8px 0; color: #007AFF; font-size: 14px; font-family: Arial, sans-serif;">📊 取得サマリー</h3>
                                        <p style="margin: 0; font-size: 12px; color: #666666; font-family: Arial, sans-serif;">{summary_text}</p>
                                        <p style="margin: 4px 0 0 0; font-size: 12px; color: #666666; font-family: Arial, sans-serif;">取得期間: <strong>{self._format_date_with_weekday(structured_data[-1]['date']) if structured_data else 'N/A'} 〜 {self._format_date_with_weekday(structured_data[0]['date']) if structured_data else 'N/A'}</strong></p>
                                    </td>
                                </tr>
                            </table>
        """
        
        # 日付ごとにデータを表示
        for date in sorted_dates:
            meals = grouped_data[date]
            # 最初の食事データから元の日付文字列を取得
            original_date = meals[0]['date'] if meals else date
            formatted_date = self._format_date_with_weekday(original_date)
            
            html += f"""
                            <!-- 日付セクション -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px; border: 1px solid #e5e5ea; border-radius: 6px; overflow: hidden;">
                                <!-- 日付ヘッダー -->
                                <tr>
                                    <td style="background-color: #8e8e93; color: #ffffff; padding: 12px 16px; font-weight: 600; font-size: 14px; text-align: center; font-family: Arial, sans-serif;">📅 {formatted_date}</td>
                                </tr>
            """
            
            for i, meal in enumerate(meals):
                # 時間帯に応じてアイコンを設定
                hour = meal['hour']
                if '朝' in hour or 'breakfast' in hour.lower():
                    time_icon = "🌅"
                elif '昼' in hour or 'lunch' in hour.lower():
                    time_icon = "☀️"
                elif '夜' in hour or 'dinner' in hour.lower():
                    time_icon = "🌙"
                else:
                    time_icon = "🍽️"
                
                # 偶数行の背景色を変更
                bg_color = "#f9f9f9" if i % 2 == 1 else "#ffffff"
                
                html += f"""
                                <!-- 食事アイテム -->
                                <tr>
                                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e5ea; background-color: {bg_color};">
                                        <div style="background-color: #007AFF; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; display: inline-block; margin-bottom: 4px; font-family: Arial, sans-serif;">{time_icon} {meal['hour']}</div>
                                        <div style="font-weight: 500; color: #1d1d1f; margin-bottom: 4px; font-size: 13px; font-family: Arial, sans-serif;">{meal['title'] if 'title' in meal else '食事'}</div>
                                        <div style="color: #666666; font-size: 12px; margin-bottom: 4px; font-family: Arial, sans-serif;">{', '.join(meal['menus'])}</div>
                                        <div style="color: #34c759; font-weight: 500; font-size: 12px; font-family: Arial, sans-serif;">💰 {meal['amount']}</div>
                                    </td>
                                </tr>
                """
            
            html += """
                            </table>
            """
        
        html += """
                        </td>
                    </tr>
                    
                    <!-- フッター -->
                    <tr>
                        <td style="background-color: #f2f2f7; padding: 12px 16px; text-align: center; border-top: 1px solid #e5e5ea;">
                            <div style="font-size: 10px; color: #666666; font-family: Arial, sans-serif;">このメールは自動生成されました</div>
                            <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #d1d1d6; font-size: 10px; color: #666666; font-family: Arial, sans-serif;">
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
        
        return html 