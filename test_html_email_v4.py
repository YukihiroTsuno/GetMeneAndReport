#!/usr/bin/env python3
"""
HTMLメールテンプレートテストスクリプト v4
iPhone対応の新しいテーブルレイアウトHTMLメールをテスト
"""

import sys
import os
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.email_sender import EmailSender
from utils.logger import setup_logger

def create_sample_data():
    """テスト用のサンプルデータを作成"""
    sample_data = [
        {
            'date': '12月19日(木[4])',
            'hour': '朝食',
            'title': '学生食堂',
            'menus': ['ご飯', '味噌汁', '焼き魚', '納豆'],
            'amount': '350円'
        },
        {
            'date': '12月19日(木[4])',
            'hour': '昼食',
            'title': 'カフェテリア',
            'menus': ['カレーライス', 'サラダ', 'コーヒー'],
            'amount': '480円'
        },
        {
            'date': '12月19日(木[4])',
            'hour': '夕食',
            'title': '学生食堂',
            'menus': ['うどん', '天ぷら', 'おにぎり'],
            'amount': '420円'
        },
        {
            'date': '12月18日(水[3])',
            'hour': '朝食',
            'title': 'カフェテリア',
            'menus': ['トースト', 'スクランブルエッグ', 'オレンジジュース'],
            'amount': '380円'
        },
        {
            'date': '12月18日(水[3])',
            'hour': '昼食',
            'title': '学生食堂',
            'menus': ['ラーメン', '餃子', 'チャーハン'],
            'amount': '520円'
        },
        {
            'date': '12月17日(火[2])',
            'hour': '朝食',
            'title': '学生食堂',
            'menus': ['パン', 'スープ', 'フルーツ'],
            'amount': '320円'
        },
        {
            'date': '12月17日(火[2])',
            'hour': '昼食',
            'title': 'カフェテリア',
            'menus': ['ハンバーガー', 'ポテト', 'コーラ'],
            'amount': '450円'
        },
        {
            'date': '12月17日(火[2])',
            'hour': '夕食',
            'title': '学生食堂',
            'menus': ['丼物', '味噌汁', '漬物'],
            'amount': '380円'
        }
    ]
    return sample_data

def test_html_generation():
    """HTMLメール生成のテスト"""
    logger = setup_logger()
    logger.info("HTMLメールテンプレートテスト開始")
    
    # サンプルデータを作成
    sample_data = create_sample_data()
    logger.info(f"サンプルデータ作成完了: {len(sample_data)}件")
    
    # EmailSenderインスタンスを作成
    email_sender = EmailSender()
    
    try:
        # HTMLメール本文を生成
        html_body = email_sender._create_html_email_body(sample_data, len(sample_data))
        
        # HTMLファイルとして保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"test_email_v4_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_body)
        
        logger.info(f"HTMLファイル保存完了: {html_filename}")
        
        # HTMLファイルのサイズを確認
        file_size = os.path.getsize(html_filename)
        logger.info(f"HTMLファイルサイズ: {file_size:,} bytes")
        
        # HTML内容の一部を表示
        logger.info("HTML内容の一部:")
        lines = html_body.split('\n')
        for i, line in enumerate(lines[:20]):
            logger.info(f"  {i+1:2d}: {line}")
        
        if len(lines) > 20:
            logger.info(f"  ... (残り {len(lines) - 20} 行)")
        
        return html_filename, html_body
        
    except Exception as e:
        logger.error(f"HTML生成エラー: {e}")
        return None, None

def test_email_sending():
    """メール送信のテスト（設定がある場合のみ）"""
    logger = setup_logger()
    
    # 環境変数をチェック
    required_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"メール送信に必要な環境変数が設定されていません: {missing_vars}")
        logger.info("HTMLファイル生成のみ実行します")
        return False
    
    logger.info("メール送信テスト開始")
    
    # サンプルデータを作成
    sample_data = create_sample_data()
    
    # EmailSenderインスタンスを作成
    email_sender = EmailSender()
    
    try:
        # メール送信テスト
        success = email_sender.send_notification(sample_data)
        
        if success:
            logger.info("メール送信テスト成功")
            return True
        else:
            logger.error("メール送信テスト失敗")
            return False
            
    except Exception as e:
        logger.error(f"メール送信エラー: {e}")
        return False

def main():
    """メイン処理"""
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("HTMLメールテンプレートテスト v4 開始")
    logger.info("=" * 50)
    
    # HTML生成テスト
    html_filename, html_body = test_html_generation()
    
    if html_filename:
        logger.info(f"✅ HTML生成テスト成功: {html_filename}")
        
        # ブラウザでHTMLファイルを開く
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(html_filename)}")
            logger.info("ブラウザでHTMLファイルを開きました")
        except Exception as e:
            logger.warning(f"ブラウザ起動エラー: {e}")
            logger.info(f"手動でHTMLファイルを開いてください: {os.path.abspath(html_filename)}")
    else:
        logger.error("❌ HTML生成テスト失敗")
        return
    
    # メール送信テスト（設定がある場合のみ）
    if test_email_sending():
        logger.info("✅ メール送信テスト成功")
    else:
        logger.info("⚠️ メール送信テストはスキップされました（設定不足）")
    
    logger.info("=" * 50)
    logger.info("テスト完了")
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 