"""
SMTP送信機能
メールのSMTP送信を担当する
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
from .email_config import EmailConfigManager

logger = logging.getLogger(__name__)

class SMTPSender:
    """SMTP送信クラス"""
    
    def __init__(self, config_manager: Optional[EmailConfigManager] = None):
        self.config_manager = config_manager or EmailConfigManager()
    
    def send_email(self, html_body: str, subject: Optional[str] = None) -> bool:
        """HTMLメールを送信"""
        if not self.config_manager.validate_config():
            logger.warning("メール設定が不完全なため、メール送信をスキップします")
            return False
        
        try:
            config = self.config_manager.get_config()
            smtp_config = self.config_manager.get_smtp_config()
            email_config = self.config_manager.get_email_config()
            
            # 件名を生成
            if subject is None:
                current_date = datetime.now().strftime('%Y年%m月%d日')
                subject = email_config["subject_template"].format(date=current_date)
            
            # メールオブジェクトを作成
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_config["sender_email"]
            msg['To'] = email_config["recipient_email"]
            msg['Subject'] = subject or "食事履歴データ"
            
            # HTML本文を追加
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # メールを送信
            with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
                server.starttls()
                server.login(smtp_config["sender_email"], smtp_config["sender_password"])
                server.send_message(msg)
            
            logger.info("HTMLメール通知を送信しました")
            return True
            
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            return False
    
    def test_connection(self) -> bool:
        """SMTP接続をテスト"""
        if not self.config_manager.validate_config():
            return False
        
        try:
            smtp_config = self.config_manager.get_smtp_config()
            
            with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
                server.starttls()
                server.login(smtp_config["sender_email"], smtp_config["sender_password"])
            
            logger.info("SMTP接続テストが成功しました")
            return True
            
        except Exception as e:
            logger.error(f"SMTP接続テストエラー: {e}")
            return False 