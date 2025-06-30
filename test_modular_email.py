"""
新しいモジュール構造のテスト
各機能が独立して動作することを確認
"""

import logging
from utils import (
    DataProcessor, 
    HTMLTemplateGenerator, 
    EmailConfigManager, 
    SMTPSender, 
    EmailSender
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_processor():
    """データ処理機能のテスト"""
    logger.info("=== データ処理機能テスト ===")
    
    # テストデータ
    test_data = [
        {
            'date': '12月19日(木[4])',
            'hour': '昼食',
            'menus': ['*ﾗｲｽL', '*国産さばの生姜煮', '*ﾀｲ風豚肉野菜炒め', '*蒸鶏いんげんごま和'],
            'amount': '¥580'
        },
        {
            'date': '12月18日(水[3])',
            'hour': '朝食',
            'menus': ['*パン', '*コーヒー'],
            'amount': '¥280'
        }
    ]
    
    # 日付解析テスト
    date_obj = DataProcessor.parse_date_from_string('12月19日(木[4])')
    logger.info(f"日付解析結果: {date_obj}")
    
    # 日付フォーマットテスト
    formatted_date = DataProcessor.format_date_with_weekday('12月19日(木[4])')
    logger.info(f"日付フォーマット結果: {formatted_date}")
    
    # メニューフォーマットテスト
    menu_html = DataProcessor.format_menu_items(['*ﾗｲｽL', '*国産さばの生姜煮'])
    logger.info(f"メニューフォーマット結果: {menu_html}")
    
    # 時間帯アイコンテスト
    icon = DataProcessor.get_time_icon('昼食')
    logger.info(f"時間帯アイコン結果: {icon}")
    
    # フィルタリングテスト
    filtered_data = DataProcessor.filter_recent_week_data(test_data)
    logger.info(f"フィルタリング結果: {len(filtered_data)}件")

def test_html_template():
    """HTMLテンプレート機能のテスト"""
    logger.info("=== HTMLテンプレート機能テスト ===")
    
    # テストデータ
    test_data = [
        {
            'date': '12月19日(木[4])',
            'hour': '昼食',
            'menus': ['*ﾗｲｽL', '*国産さばの生姜煮'],
            'amount': '¥580'
        }
    ]
    
    # 300px幅のテンプレート生成
    generator_300 = HTMLTemplateGenerator(email_width=300)
    html_300 = generator_300.create_email_body(test_data)
    logger.info(f"300px幅テンプレート生成: {len(html_300)}文字")
    
    # 600px幅のテンプレート生成
    generator_600 = HTMLTemplateGenerator(email_width=600)
    html_600 = generator_600.create_email_body(test_data)
    logger.info(f"600px幅テンプレート生成: {len(html_600)}文字")
    
    # 空データ用テンプレート
    html_empty = generator_300.create_email_body([])
    logger.info(f"空データテンプレート生成: {len(html_empty)}文字")

def test_email_config():
    """メール設定機能のテスト"""
    logger.info("=== メール設定機能テスト ===")
    
    config_manager = EmailConfigManager()
    config = config_manager.get_config()
    
    logger.info(f"SMTP Server: {config.smtp_server}")
    logger.info(f"SMTP Port: {config.smtp_port}")
    logger.info(f"Email Width: {config.email_width}")
    logger.info(f"Subject Template: {config.subject_template}")
    
    # 設定更新テスト
    config_manager.update_config(email_width=400)
    updated_config = config_manager.get_config()
    logger.info(f"更新後のEmail Width: {updated_config.email_width}")
    
    # 設定妥当性チェック
    is_valid = config_manager.validate_config()
    logger.info(f"設定妥当性: {is_valid}")

def test_smtp_sender():
    """SMTP送信機能のテスト"""
    logger.info("=== SMTP送信機能テスト ===")
    
    smtp_sender = SMTPSender()
    
    # 接続テスト（設定が不完全な場合はスキップ）
    if smtp_sender.config_manager.validate_config():
        connection_test = smtp_sender.test_connection()
        logger.info(f"SMTP接続テスト: {connection_test}")
    else:
        logger.info("SMTP設定が不完全なため、接続テストをスキップ")

def test_integrated_email_sender():
    """統合メール送信機能のテスト"""
    logger.info("=== 統合メール送信機能テスト ===")
    
    # テストデータ
    test_data = [
        {
            'date': '12月19日(木[4])',
            'hour': '昼食',
            'menus': ['*ﾗｲｽL', '*国産さばの生姜煮'],
            'amount': '¥580'
        }
    ]
    
    # 300px幅のメール送信機能
    email_sender_300 = EmailSender(email_width=300)
    logger.info(f"300px幅EmailSender初期化完了")
    
    # 設定取得テスト
    config = email_sender_300.get_config()
    logger.info(f"設定取得: Email Width = {config.email_width}")
    
    # 設定更新テスト
    email_sender_300.update_config(email_width=500)
    updated_config = email_sender_300.get_config()
    logger.info(f"設定更新後: Email Width = {updated_config.email_width}")
    
    # メール送信テスト（設定が不完全な場合はスキップ）
    if email_sender_300.config_manager.validate_config():
        send_result = email_sender_300.send_notification(test_data)
        logger.info(f"メール送信テスト: {send_result}")
    else:
        logger.info("メール設定が不完全なため、送信テストをスキップ")

def main():
    """メイン実行関数"""
    logger.info("新しいモジュール構造のテストを開始します")
    
    try:
        test_data_processor()
        test_html_template()
        test_email_config()
        test_smtp_sender()
        test_integrated_email_sender()
        
        logger.info("すべてのテストが完了しました")
        
    except Exception as e:
        logger.error(f"テスト実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main() 