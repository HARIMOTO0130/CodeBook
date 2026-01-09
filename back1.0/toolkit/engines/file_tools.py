import os
import re
from typing import Dict, Any, List
from datetime import datetime
from .base_engine import BaseToolEngine


class FileRenameTool(BaseToolEngine):
    """批量重命名文件工具"""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            folder_path = params.get('folderPath')
            pattern = params.get('pattern')
            file_type = params.get('fileType', 'all')
            
            # 验证参数
            validation = self.validate_params(params)
            if not validation['valid']:
                return {
                    "success": False,
                    "result": None,
                    "error": "；".join(validation['errors'])
                }
            
            # 获取文件列表
            files = self._get_files(folder_path, file_type)
            if not files:
                return {
                    "success": False,
                    "result": None,
                    "error": "未找到符合条件的文件"
                }
            
            # 执行重命名
            renamed_files = []
            for i, file in enumerate(files):
                old_path = os.path.join(folder_path, file)
                file_ext = os.path.splitext(file)[1]
                
                # 格式化新文件名
                new_name = self._format_filename(pattern, i, file_ext)
                new_path = os.path.join(folder_path, new_name)
                
                # 避免文件名冲突
                counter = 1
                base_new_path = new_path
                while os.path.exists(new_path):
                    name_without_ext, ext = os.path.splitext(base_new_path)
                    new_path = f"{name_without_ext}_{counter}{ext}"
                    counter += 1
                
                # 重命名文件
                os.rename(old_path, new_path)
                renamed_files.append({
                    "old_name": file,
                    "new_name": os.path.basename(new_path)
                })
            
            return {
                "success": True,
                "result": {
                    "message": f"成功处理 {len(renamed_files)} 个文件",
                    "renamed_files": renamed_files
                },
                "error": None
            }
            
        except Exception as e:
            return self.handle_error(e)
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        
        if not params.get('folderPath'):
            errors.append("请输入文件夹路径")
        
        if not params.get('pattern'):
            errors.append("请输入命名模式")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _get_files(self, folder_path: str, file_type: str) -> List[str]:
        """获取符合条件的文件列表"""
        files = []
        
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    # 根据文件类型过滤
                    if file_type == 'all' or any(item.endswith(ext) for ext in file_type.split(',')):
                        files.append(item)
        except Exception:
            pass
        
        return files
    
    def _format_filename(self, pattern: str, index: int, file_ext: str) -> str:
        """格式化文件名"""
        # 替换数字占位符
        formatted = pattern
        
        # 处理 {num} 或 {num:03d} 格式的占位符
        if '{num' in pattern:
            # 查找所有可能的数字格式
            for match in re.finditer(r'\{num(?::(.*?))?\}', pattern):
                format_spec = match.group(1) or 'd'
                replacement = f"{{:{format_spec}}}".format(index + 1)
                formatted = formatted.replace(match.group(0), replacement)
        
        # 添加文件扩展名
        if not formatted.endswith(file_ext):
            formatted += file_ext
        
        return formatted


class ExcelMergeTool(BaseToolEngine):
    """Excel表格合并工具"""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            folder_path = params.get('folderPath')
            output_file_name = params.get('outputFileName', '合并结果.xlsx')
            has_same_header = params.get('hasSameHeader', 'true').lower() == 'true'
            
            # 验证参数
            validation = self.validate_params(params)
            if not validation['valid']:
                return {
                    "success": False,
                    "result": None,
                    "error": "；".join(validation['errors'])
                }
            
            # 获取Excel文件列表
            excel_files = self._get_excel_files(folder_path)
            if not excel_files:
                return {
                    "success": False,
                    "result": None,
                    "error": "未找到Excel文件"
                }
            
            # 实际合并操作，使用pandas实现
            import pandas as pd
            all_data = []
            
            for i, file in enumerate(excel_files):
                file_path = os.path.join(folder_path, file)
                df = pd.read_excel(file_path)
                
                # 只保留第一个文件的表头
                if i > 0 and has_same_header:
                    all_data.append(df)
                else:
                    all_data.append(df)
            
            # 合并所有数据
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 保存结果
            output_path = os.path.join(folder_path, output_file_name)
            combined_df.to_excel(output_path, index=False)
            
            return {
                "success": True,
                "result": {
                    "message": f"成功合并 {len(excel_files)} 个Excel文件",
                    "output_file": output_file_name,
                    "merged_files": excel_files
                },
                "error": None
            }
            
        except Exception as e:
            return self.handle_error(e)
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        
        if not params.get('folderPath'):
            errors.append("请输入Excel文件所在文件夹")
        
        if not params.get('outputFileName'):
            errors.append("请输入输出文件名")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _get_excel_files(self, folder_path: str) -> List[str]:
        """获取Excel文件列表"""
        excel_extensions = ['.xlsx', '.xls', '.xlsm']
        excel_files = []
        
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    _, ext = os.path.splitext(item)
                    if ext.lower() in excel_extensions:
                        excel_files.append(item)
        except Exception:
            pass
        
        return excel_files