"""
新しいモジュール構造のWebスクレイピング機能テスト
各機能が独立して動作することを確認
"""

import logging
from utils import (
    WebDriverManager,
    SelectorManager,
    LoginManager,
    NavigationManager,
    DataExtractor
)
from meal_scraper import MealHistoryScraper

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_webdriver_manager():
    """WebDriver管理機能のテスト"""
    logger.info("=== WebDriver管理機能テスト ===")
    
    # 設定
    config = {
        "headless": True,  # テスト時はヘッドレスモード
        "timeout": 10,
        "page_load": 3
    }
    
    # WebDriverManagerをテスト
    with WebDriverManager(config) as wdm:
        # 基本的な機能をテスト
        assert wdm.is_ready() == True
        assert wdm.get_driver() is not None
        assert wdm.get_wait() is not None
        
        # URL遷移テスト
        success = wdm.navigate_to("https://www.google.com")
        assert success == True
        
        # 現在のURL取得テスト
        current_url = wdm.get_current_url()
        assert "google" in current_url.lower()
        
        # デバッグHTML保存テスト
        success = wdm.save_debug_html("debug/test_page.html")
        assert success == True
        
        logger.info("WebDriver管理機能テスト完了")

def test_selector_manager():
    """セレクター管理機能のテスト"""
    logger.info("=== セレクター管理機能テスト ===")
    
    # デフォルトセレクターでテスト
    sm = SelectorManager()
    
    # セレクター取得テスト
    login_selectors = sm.get_login_selectors()
    assert "email_field" in login_selectors
    assert "password_field" in login_selectors
    assert "login_button" in login_selectors
    
    navigation_selectors = sm.get_navigation_selectors()
    assert "meal_history_link" in navigation_selectors
    assert "usage_detail_link" in navigation_selectors
    
    data_selectors = sm.get_data_extraction_selectors()
    assert "history_articles" in data_selectors
    assert "date_element" in data_selectors
    
    # セレクター更新テスト
    new_selectors = {"email_field": "input#new_email"}
    sm.update_selectors(new_selectors)
    
    updated_login_selectors = sm.get_login_selectors()
    assert updated_login_selectors["email_field"] == "input#new_email"
    
    # 妥当性チェックテスト
    is_valid = sm.validate_selectors()
    assert is_valid == True
    
    logger.info("セレクター管理機能テスト完了")

def test_login_manager():
    """ログイン管理機能のテスト"""
    logger.info("=== ログイン管理機能テスト ===")
    
    # 設定
    config = {
        "headless": True,
        "timeout": 10,
        "page_load": 3,
        "after_login": 2
    }
    
    # テスト用の認証情報（実際には使用されない）
    credentials = ("test@example.com", "testpassword")
    
    # 各マネージャーを初期化
    wdm = WebDriverManager(config)
    sm = SelectorManager()
    lm = LoginManager(wdm, sm, credentials, config)
    
    # WebDriverをセットアップ
    wdm.setup_driver()
    
    # ログイン状態チェックテスト
    is_logged_in = lm.is_logged_in()
    logger.info(f"ログイン状態: {is_logged_in}")
    
    # クリーンアップ
    wdm.cleanup()
    
    logger.info("ログイン管理機能テスト完了")

def test_navigation_manager():
    """ナビゲーション管理機能のテスト"""
    logger.info("=== ナビゲーション管理機能テスト ===")
    
    # 設定
    config = {
        "headless": True,
        "timeout": 10,
        "page_load": 3,
        "after_click": 2,
        "element_load": 2
    }
    
    # テスト用の認証情報
    credentials = ("test@example.com", "testpassword")
    
    # 各マネージャーを初期化
    wdm = WebDriverManager(config)
    sm = SelectorManager()
    lm = LoginManager(wdm, sm, credentials, config)
    nm = NavigationManager(wdm, sm, lm, config)
    
    # WebDriverをセットアップ
    wdm.setup_driver()
    
    # もっと見るボタンクリックテスト（実際のページがないためスキップ）
    # success = nm.click_more_button()
    # logger.info(f"もっと見るボタンクリック: {success}")
    
    # クリーンアップ
    wdm.cleanup()
    
    logger.info("ナビゲーション管理機能テスト完了")

def test_data_extractor():
    """データ抽出機能のテスト"""
    logger.info("=== データ抽出機能テスト ===")
    
    # 設定
    config = {
        "headless": True,
        "timeout": 10,
        "page_load": 3,
        "after_click": 2,
        "element_load": 2
    }
    
    # テスト用の認証情報
    credentials = ("test@example.com", "testpassword")
    
    # 各マネージャーを初期化
    wdm = WebDriverManager(config)
    sm = SelectorManager()
    lm = LoginManager(wdm, sm, credentials, config)
    nm = NavigationManager(wdm, sm, lm, config)
    de = DataExtractor(wdm, sm, nm)
    
    # テストデータ
    test_data = [
        {
            'date': '12月19日(木)',
            'hour': '昼食',
            'menus': ['*ﾗｲｽL', '*国産さばの生姜煮'],
            'amount': '¥580'
        }
    ]
    
    # データ妥当性チェックテスト
    is_valid = de.validate_extracted_data(test_data)
    assert is_valid == True
    
    # データサマリーテスト
    summary = de.get_data_summary(test_data)
    assert summary["count"] == 1
    assert summary["date_range"] is not None
    assert summary["total_amount"] == 580
    
    logger.info("データ抽出機能テスト完了")

def test_integrated_scraper():
    """統合スクレイパーのテスト"""
    logger.info("=== 統合スクレイパーテスト ===")
    
    # 統合スクレイパーを初期化
    scraper = MealHistoryScraper()
    
    # データサマリー取得テスト（実際のログインは行わない）
    # summary = scraper.get_data_summary()
    # logger.info(f"データサマリー: {summary}")
    
    logger.info("統合スクレイパーテスト完了")

def main():
    """メイン実行関数"""
    logger.info("新しいモジュール構造のWebスクレイピング機能テストを開始します")
    
    try:
        test_webdriver_manager()
        test_selector_manager()
        test_login_manager()
        test_navigation_manager()
        test_data_extractor()
        test_integrated_scraper()
        
        logger.info("すべてのテストが完了しました")
        
    except Exception as e:
        logger.error(f"テスト実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main() 