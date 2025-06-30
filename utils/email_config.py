"""
メール設定管理機能
メール送信に関する設定を一元管理する
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """メール設定データクラス"""
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    recipient_email: str
    email_width: int = 300
    subject_template: str = "ミールカード　食べたもの {date}"
    
    def is_valid(self) -> bool:
        """設定が有効かどうかをチェック"""
        return all([
            self.smtp_server,
            self.smtp_port > 0,
            self.sender_email,
            self.sender_password,
            self.recipient_email
        ])

class EmailConfigManager:
    """メール設定管理クラス"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> EmailConfig:
        """環境変数から設定を読み込み"""
        return EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            sender_email=os.getenv("SENDER_EMAIL", os.getenv("EMAIL", "")),
            sender_password=os.getenv("SENDER_PASSWORD", os.getenv("PASSWORD", "")),
            recipient_email=os.getenv("RECIPIENT_EMAIL", ""),
            email_width=int(os.getenv("EMAIL_WIDTH", "300")),
            subject_template=os.getenv("EMAIL_SUBJECT_TEMPLATE", "ミールカード　食べたもの {date}")
        )
    
    def get_config(self) -> EmailConfig:
        """設定を取得"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"設定を更新しました: {key} = {value}")
            else:
                logger.warning(f"無効な設定キー: {key}")
    
    def validate_config(self) -> bool:
        """設定の妥当性をチェック"""
        if not self.config.is_valid():
            logger.error("メール設定が不完全です")
            logger.error(f"SMTP Server: {self.config.smtp_server}")
            logger.error(f"SMTP Port: {self.config.smtp_port}")
            logger.error(f"Sender Email: {'設定済み' if self.config.sender_email else '未設定'}")
            logger.error(f"Sender Password: {'設定済み' if self.config.sender_password else '未設定'}")
            logger.error(f"Recipient Email: {'設定済み' if self.config.recipient_email else '未設定'}")
            return False
        return True
    
    def get_smtp_config(self) -> Dict[str, Any]:
        """SMTP設定を取得"""
        return {
            "smtp_server": self.config.smtp_server,
            "smtp_port": self.config.smtp_port,
            "sender_email": self.config.sender_email,
            "sender_password": self.config.sender_password
        }
    
    def get_email_config(self) -> Dict[str, Any]:
        """メール設定を取得"""
        return {
            "recipient_email": self.config.recipient_email,
            "email_width": self.config.email_width,
            "subject_template": self.config.subject_template
        } 