"""
メール送信機能
食事履歴データをHTMLメールで送信（iPhone最適化）
"""

import logging
from typing import List, Dict, Any, Optional
from .data_processor import DataProcessor
from .html_template import HTMLTemplateGenerator
from .smtp_sender import SMTPSender
from .email_config import EmailConfigManager

logger = logging.getLogger(__name__)

class EmailSender:
    """メール送信クラス（統合インターフェース）"""
    
    def __init__(self, email_width: Optional[int] = None):
        # config.pyの設定を優先使用
        try:
            from config import EMAIL_CONFIG
            self.email_config = EMAIL_CONFIG
            # 引数で指定された幅があれば使用、なければ設定ファイルの値を使用
            self.email_width = email_width if email_width is not None else self.email_config.get("email_width", 240)
        except ImportError:
            # config.pyが利用できない場合はデフォルト値を使用
            self.email_width = email_width if email_width is not None else 240
            self.email_config = {}
        
        self.config_manager = EmailConfigManager()
        self.smtp_sender = SMTPSender(self.config_manager)
        self.html_generator = HTMLTemplateGenerator(self.email_width)
    
    def send_notification(self, structured_data: List[Dict[str, Any]]) -> bool:
        """食事履歴データの通知メールを送信（HTML形式）"""
        try:
            # 最新の1週間分のデータのみをフィルタリング
            recent_data = DataProcessor.filter_recent_week_data(structured_data)
            
            # HTMLメール本文を作成
            html_body = self.html_generator.create_email_body(recent_data, len(structured_data))
            
            # メールを送信
            return self.smtp_sender.send_email(html_body)
            
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            return False
    
    def test_connection(self) -> bool:
        """SMTP接続をテスト"""
        return self.smtp_sender.test_connection()
    
    def update_config(self, **kwargs) -> None:
        """設定を更新"""
        self.config_manager.update_config(**kwargs)
        # 設定変更後、関連オブジェクトを再初期化
        if 'email_width' in kwargs:
            self.html_generator = HTMLTemplateGenerator(kwargs['email_width'])
    
    def get_config(self):
        """設定を取得"""
        return self.config_manager.get_config() 