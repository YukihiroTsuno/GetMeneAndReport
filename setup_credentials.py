"""
認証情報セットアップスクリプト
ログイン情報を暗号化して保存
"""

import os
import sys
from getpass import getpass

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.encryption import CredentialManager

def main():
    """メイン実行関数"""
    print("🔐 認証情報セットアップ")
    print("=" * 50)
    
    # メールアドレスを入力
    print("📧 メールアドレスを入力してください:")
    email = input("メールアドレス: ").strip()
    
    if not email:
        print("❌ メールアドレスが入力されていません")
        return False
    
    # パスワードを入力（非表示）
    print("🔑 パスワードを入力してください:")
    password = getpass("パスワード: ").strip()
    
    if not password:
        print("❌ パスワードが入力されていません")
        return False
    
    # マスターパスワードを入力（暗号化用）
    print("🔐 暗号化用のマスターパスワードを入力してください:")
    print("（Enterキーでデフォルト値を使用）")
    master_password = getpass("マスターパスワード: ").strip()
    
    if not master_password:
        master_password = None  # デフォルト値を使用
        print("ℹ️  デフォルトのマスターパスワードを使用します")
    
    # 認証情報を暗号化して保存
    credential_manager = CredentialManager(master_password)
    
    if credential_manager.save_encrypted_credentials(email, password):
        print("✅ 認証情報の暗号化・保存が完了しました")
        print("📁 保存先: .credentials")
        print("\n⚠️  注意事項:")
        print("   - .credentialsファイルは安全に保管してください")
        print("   - マスターパスワードを忘れないでください")
        print("   - .gitignoreに.credentialsが含まれていることを確認してください")
        return True
    else:
        print("❌ 認証情報の保存に失敗しました")
        return False

if __name__ == "__main__":
    main() 