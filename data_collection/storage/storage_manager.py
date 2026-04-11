import os
import json
import hashlib
from datetime import datetime
from data_collection.config.config import STORAGE_CONFIG

class StorageManager:
    """存储管理器"""
    
    def __init__(self):
        self.base_path = STORAGE_CONFIG['base_path']
        self.formats = STORAGE_CONFIG['formats']
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保存储目录存在"""
        os.makedirs(os.path.join(self.base_path, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'processed'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'final'), exist_ok=True)
    
    def _get_file_path(self, source, data_type, filename):
        """获取文件路径"""
        return os.path.join(self.base_path, data_type, f"{source}_{filename}.{self.formats[data_type]}")
    
    def save_raw_data(self, source, filename, data):
        """保存原始数据"""
        file_path = self._get_file_path(source, 'raw', filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    def save_processed_data(self, source, filename, data):
        """保存处理后的数据"""
        file_path = self._get_file_path(source, 'processed', filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    def save_final_data(self, source, filename, data):
        """保存最终数据"""
        file_path = self._get_file_path(source, 'final', filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    def load_data(self, source, data_type, filename):
        """加载数据"""
        file_path = self._get_file_path(source, data_type, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_files(self, data_type=None):
        """列出所有文件"""
        files = []
        if data_type:
            target_path = os.path.join(self.base_path, data_type)
            if os.path.exists(target_path):
                files = os.listdir(target_path)
        else:
            for dtype in ['raw', 'processed', 'final']:
                target_path = os.path.join(self.base_path, dtype)
                if os.path.exists(target_path):
                    for file in os.listdir(target_path):
                        files.append(f"{dtype}/{file}")
        return files
    
    def generate_filename(self, content):
        """根据内容生成唯一文件名"""
        hash_obj = hashlib.md5(str(content).encode('utf-8'))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{hash_obj.hexdigest()}_{timestamp}"
    
    def get_file_size(self, file_path):
        """获取文件大小"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0