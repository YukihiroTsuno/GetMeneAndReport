#!/usr/bin/env python3
"""
実際の食事履歴データでメール送信テスト
"""

import sys
import os
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.email_sender import EmailSender
from utils.logger import setup_logger

def create_sample_data():
    """テスト用のサンプルデータを作成"""
    sample_data = [
        {
            'date': '06月28日(土)',
            'hour': '13:55',
            'menus': ['*冷やしそば'],
            'amount': '308円'
        },
        {
            'date': '06月27日(金)',
            'hour': '18:21',
            'menus': ['*焼肉ビビンバ丼M', '*国産さばの生姜煮'],
            'amount': '946円'
        },
        {
            'date': '06月26日(木)',
            'hour': '15:46',
            'menus': ['紅茶バターパン'],
            'amount': '108円'
        },
        {
            'date': '06月26日(木)',
            'hour': '17:54',
            'menus': ['*ライスM', '*ジューシーチキン竜田', '*豆腐'],
            'amount': '628円'
        },
        {
            'date': '06月25日(水)',
            'hour': '12:26',
            'menus': ['*焼肉ビビンバ丼M', '*フルーツヨーグルト'],
            'amount': '847円'
        },
        {
            'date': '06月25日(水)',
            'hour': '14:35',
            'menus': ['紅茶バターパン'],
            'amount': '108円'
        },
        {
            'date': '06月25日(水)',
            'hour': '16:25',
            'menus': ['*広島中華そば醤油豚'],
            'amount': '451円'
        },
        {
            'date': '06月24日(火)',
            'hour': '13:58',
            'menus': ['チョコチャンク'],
            'amount': '148円'
        }
    ]
    return sample_data

def test_actual_email():
    """サンプルデータを使用してメール送信をテスト"""
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("サンプルデータでメール送信テスト開始")
    logger.info("=" * 50)
    
    # サンプルデータを作成
    sample_data = create_sample_data()
    logger.info(f"サンプルデータ作成完了: {len(sample_data)}件")
    
    # 最初の数件を表示
    logger.info("データサンプル:")
    for i, data in enumerate(sample_data[:3]):
        logger.info(f"  {i+1}: {data}")
    
    # EmailSenderインスタンスを作成
    email_sender = EmailSender()
    
    # 環境変数を確認
    logger.info("メール設定確認:")
    logger.info(f"  SENDER_EMAIL: {email_sender.sender_email}")
    logger.info(f"  RECIPIENT_EMAIL: {email_sender.recipient_email}")
    logger.info(f"  SMTP_SERVER: {email_sender.smtp_server}")
    logger.info(f"  SMTP_PORT: {email_sender.smtp_port}")
    
    # メール送信テスト
    logger.info("メール送信テスト開始...")
    success = email_sender.send_notification(sample_data)
    
    if success:
        logger.info("✅ メール送信テスト成功")
        return True
    else:
        logger.error("❌ メール送信テスト失敗")
        return False

def main():
    """メイン処理"""
    success = test_actual_email()
    
    if success:
        print("\n🎉 メール送信テストが成功しました！")
        print("受信メールボックスを確認してください。")
    else:
        print("\n❌ メール送信テストが失敗しました。")
        print("ログを確認してエラーの詳細を確認してください。")

if __name__ == "__main__":
    main() 