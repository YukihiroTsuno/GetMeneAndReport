"""
暗号化機能
ログイン情報を暗号化・復号化
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    """認証情報管理クラス"""
    
    def __init__(self, master_password=None):
        self.master_password = master_password or self._get_default_master_password()
        self.fernet = self._create_fernet()
    
    def _get_default_master_password(self):
        """デフォルトのマスターパスワードを取得"""
        # 環境変数から取得、なければデフォルト値を使用
        return os.getenv('MASTER_PASSWORD', 'GetMeneAndReport2024')
    
    def _create_fernet(self):
        """Fernet暗号化オブジェクトを作成"""
        try:
            # マスターパスワードからキーを生成
            salt = b'GetMeneAndReport_Salt_2024'  # 固定のソルト（本番では環境変数から取得）
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
            return Fernet(key)
        except Exception as e:
            logger.error(f"Fernet作成エラー: {e}")
            return None
    
    def encrypt_credentials(self, email, password):
        """認証情報を暗号化"""
        try:
            if not self.fernet:
                logger.error("暗号化オブジェクトが初期化されていません")
                return None, None
            
            # 認証情報を暗号化
            encrypted_email = self.fernet.encrypt(email.encode())
            encrypted_password = self.fernet.encrypt(password.encode())
            
            # Base64エンコードして文字列に変換
            encrypted_email_str = base64.urlsafe_b64encode(encrypted_email).decode()
            encrypted_password_str = base64.urlsafe_b64encode(encrypted_password).decode()
            
            logger.info("認証情報の暗号化が完了しました")
            return encrypted_email_str, encrypted_password_str
            
        except Exception as e:
            logger.error(f"認証情報暗号化エラー: {e}")
            return None, None
    
    def decrypt_credentials(self, encrypted_email, encrypted_password):
        """認証情報を復号化"""
        try:
            if not self.fernet:
                logger.error("暗号化オブジェクトが初期化されていません")
                return None, None
            
            # Base64デコード
            encrypted_email_bytes = base64.urlsafe_b64decode(encrypted_email.encode())
            encrypted_password_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            
            # 復号化
            email = self.fernet.decrypt(encrypted_email_bytes).decode()
            password = self.fernet.decrypt(encrypted_password_bytes).decode()
            
            logger.info("認証情報の復号化が完了しました")
            return email, password
            
        except Exception as e:
            logger.error(f"認証情報復号化エラー: {e}")
            return None, None
    
    def save_encrypted_credentials(self, email, password, file_path='.credentials'):
        """暗号化された認証情報をファイルに保存"""
        try:
            encrypted_email, encrypted_password = self.encrypt_credentials(email, password)
            
            if not encrypted_email or not encrypted_password:
                return False
            
            # 暗号化された認証情報をファイルに保存
            with open(file_path, 'w') as f:
                f.write(f"EMAIL={encrypted_email}\n")
                f.write(f"PASSWORD={encrypted_password}\n")
            
            logger.info(f"暗号化された認証情報を保存しました: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"認証情報保存エラー: {e}")
            return False
    
    def load_encrypted_credentials(self, file_path='.credentials'):
        """暗号化された認証情報をファイルから読み込み"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"認証情報ファイルが存在しません: {file_path}")
                return None, None
            
            # ファイルから暗号化された認証情報を読み込み
            credentials = {}
            with open(file_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        credentials[key] = value
            
            if 'EMAIL' not in credentials or 'PASSWORD' not in credentials:
                logger.error("認証情報ファイルの形式が正しくありません")
                return None, None
            
            # 復号化
            email, password = self.decrypt_credentials(
                credentials['EMAIL'], 
                credentials['PASSWORD']
            )
            
            return email, password
            
        except Exception as e:
            logger.error(f"認証情報読み込みエラー: {e}")
            return None, None 