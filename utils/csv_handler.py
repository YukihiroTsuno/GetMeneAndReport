"""
CSVファイル処理機能
食事履歴データをCSVファイルに保存
"""

import pandas as pd
import os
import logging
import ast
import re

# FILE_PATHSを直接定義
FILE_PATHS = {
    "csv_output": "meal_history.csv",
    "debug_dir": "debug",
    "logs_dir": "logs"
}

logger = logging.getLogger(__name__)

class CSVHandler:
    """CSVファイル処理クラス"""
    
    def __init__(self):
        self.output_path = FILE_PATHS["csv_output"]
    
    def _parse_menus_string(self, menus_str):
        """メニュー文字列をリストに変換"""
        try:
            if not menus_str or menus_str == 'nan':
                return []
            
            # 文字列をクリーンアップ
            menus_str = str(menus_str).strip()
            
            # リスト形式の文字列を安全に評価
            if menus_str.startswith('[') and menus_str.endswith(']'):
                try:
                    # ast.literal_evalを使用して安全に評価
                    menus_list = ast.literal_eval(menus_str)
                    if isinstance(menus_list, list):
                        return menus_list
                except (ValueError, SyntaxError):
                    pass
            
            # 単一のメニュー項目の場合
            if menus_str.startswith("'") and menus_str.endswith("'"):
                return [menus_str[1:-1]]  # クォートを除去
            
            # その他の場合は単一項目として扱う
            return [menus_str]
            
        except Exception as e:
            logger.warning(f"メニュー文字列の解析エラー: {e}, 文字列: {menus_str}")
            return [menus_str] if menus_str else []
    
    def save_data(self, structured_data):
        """構造化データをCSVファイルに保存"""
        try:
            if not structured_data:
                logger.warning("保存するデータがありません")
                return None
            
            # DataFrameを作成
            df = pd.DataFrame(structured_data)
            
            # CSVファイルに保存
            df.to_csv(self.output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSVファイルに保存しました: {self.output_path}")
            return self.output_path
            
        except Exception as e:
            logger.error(f"CSVファイル保存エラー: {e}")
            return None
    
    def load_data(self, file_path=None):
        """CSVファイルからデータを読み込み"""
        try:
            path = file_path or self.output_path
            
            if not os.path.exists(path):
                logger.warning(f"ファイルが存在しません: {path}")
                return None
            
            df = pd.read_csv(path, encoding='utf-8-sig')
            data = df.to_dict('records')
            
            # メニューデータを正しく変換
            for record in data:
                if 'menus' in record:
                    record['menus'] = self._parse_menus_string(record['menus'])
            
            logger.info(f"CSVファイルから読み込みました: {path}")
            return data
            
        except Exception as e:
            logger.error(f"CSVファイル読み込みエラー: {e}")
            return None
    
    def get_file_info(self, file_path=None):
        """CSVファイルの情報を取得"""
        try:
            path = file_path or self.output_path
            
            if not os.path.exists(path):
                return None
            
            file_size = os.path.getsize(path)
            file_stats = os.stat(path)
            
            return {
                'path': path,
                'size': file_size,
                'created': file_stats.st_ctime,
                'modified': file_stats.st_mtime
            }
            
        except Exception as e:
            logger.error(f"ファイル情報取得エラー: {e}")
            return None 