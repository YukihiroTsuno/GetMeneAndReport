"""
HTMLメール内容確認テスト
生成されるHTMLの内容を確認
"""

import os
import sys
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.email_sender import EmailSender

def create_test_data():
    """テスト用の食事履歴データを作成（曜日付き日付）"""
    test_data = []
    
    # 今日から7日前までのデータを作成
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        # 曜日の日本語表記
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        weekday_jp = weekdays[date.weekday()]
        weekday_num = date.weekday()
        
        # 元の形式の日付文字列（スクレイピングで取得される形式）
        date_str = f"{date.month}月{date.day}日({weekday_jp}[{weekday_num}])"
        
        # 朝食
        test_data.append({
            'date': date_str,
            'hour': '朝食',
            'menus': ['パン', 'サラダ', 'スープ'],
            'amount': '350円'
        })
        
        # 昼食
        test_data.append({
            'date': date_str,
            'hour': '昼食',
            'menus': ['カレーライス', '味噌汁', '小鉢'],
            'amount': '450円'
        })
        
        # 夕食
        test_data.append({
            'date': date_str,
            'hour': '夕食',
            'menus': ['ハンバーグ', 'ご飯', '味噌汁', 'サラダ'],
            'amount': '550円'
        })
    
    return test_data

def main():
    """メイン実行関数"""
    print("🔍 HTMLメール内容確認テストを開始します...")
    
    # テストデータを作成
    test_data = create_test_data()
    print(f"✅ テストデータ作成完了: {len(test_data)}件")
    
    # 日付の表示例を確認
    print("\n📋 元の日付形式:")
    for i, data in enumerate(test_data[:3]):
        print(f"   {i+1}. {data['date']}")
    
    # メール送信機能をテスト
    email_sender = EmailSender()
    
    # HTMLメール本文を生成
    html_content = email_sender._create_html_email_body(test_data)
    
    # HTMLファイルに保存
    with open('debug/test_email_content.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n✅ HTMLファイルを生成しました: debug/test_email_content.html")
    print("📄 ブラウザで開いて内容を確認してください")
    
    # 日付フォーマットのテスト
    print("\n🔍 日付フォーマットテスト:")
    for i, data in enumerate(test_data[:3]):
        original = data['date']
        formatted = email_sender._format_date_with_weekday(original)
        print(f"   {i+1}. 元: {original}")
        print(f"      変換後: {formatted}")
    
    return True

if __name__ == "__main__":
    main() 