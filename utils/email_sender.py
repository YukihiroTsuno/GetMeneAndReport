"""
メール送信機能
食事履歴データをメールで送信
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import EMAIL_CONFIG
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """メール送信クラス"""
    
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG["smtp_server"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.sender_email = EMAIL_CONFIG["sender_email"]
        self.sender_password = EMAIL_CONFIG["sender_password"]
        self.recipient_email = EMAIL_CONFIG["recipient_email"]
    
    def send_notification(self, structured_data, csv_file_path=None):
        """食事履歴データの通知メールを送信"""
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.warning("メール設定が不完全なため、メール送信をスキップします")
            return False
        
        try:
            # メール本文を作成
            body = self._create_email_body(structured_data)
            
            # メールオブジェクトを作成
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = "食事履歴データ取得完了"
            
            # 本文を追加
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # CSVファイルを添付
            if csv_file_path:
                self._attach_csv_file(msg, csv_file_path)
            
            # メールを送信
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info("メール通知を送信しました")
            return True
            
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            return False
    
    def _create_email_body(self, structured_data):
        """メール本文を作成"""
        body = "食事履歴データの取得が完了しました。\n\n"
        body += f"取得件数: {len(structured_data)}件\n\n"
        
        # 最新の5件を表示
        body += "最新の食事履歴:\n"
        for i, data in enumerate(structured_data[:5]):
            body += f"{i+1}. {data['date']} {data['hour']} - {', '.join(data['menus'])} - {data['amount']}\n"
        
        if len(structured_data) > 5:
            body += f"... 他 {len(structured_data) - 5}件\n"
        
        body += "\n詳細は添付のCSVファイルをご確認ください。"
        return body
    
    def _attach_csv_file(self, msg, csv_file_path):
        """CSVファイルを添付"""
        try:
            with open(csv_file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {csv_file_path}'
            )
            msg.attach(part)
            logger.info(f"CSVファイルを添付しました: {csv_file_path}")
            
        except Exception as e:
            logger.error(f"CSVファイル添付エラー: {e}") 