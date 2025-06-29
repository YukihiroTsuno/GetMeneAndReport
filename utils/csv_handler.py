"""
CSVファイル処理機能
食事履歴データをCSVファイルに保存
"""

import pandas as pd
import os
import logging

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