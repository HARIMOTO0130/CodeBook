import os
from typing import Dict, Any, List
from .base_engine import BaseToolEngine


class DataAnalysisTool(BaseToolEngine):
    """数据统计分析工具"""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            file_path = params.get('filePath')
            sheet_name = params.get('sheetName', 'Sheet1')
            columns = params.get('columns', '')
            
            # 验证参数
            validation = self.validate_params(params)
            if not validation['valid']:
                return {
                    "success": False,
                    "result": None,
                    "error": "；".join(validation['errors'])
                }
            
            # 解析需要分析的列
            target_columns = [col.strip() for col in columns.split(',')] if columns else []
            
            # 实际数据分析操作，使用pandas实现
            import pandas as pd
            
            # 读取Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 如果指定了列，只分析这些列
            if target_columns:
                # 验证列是否存在
                missing_columns = [col for col in target_columns if col not in df.columns]
                if missing_columns:
                    return {
                        "success": False,
                        "result": None,
                        "error": f"未找到以下列: {', '.join(missing_columns)}"
                    }
                analysis_df = df[target_columns]
            else:
                # 自动选择数值列进行分析
                analysis_df = df.select_dtypes(include=['number'])
            
            # 生成统计信息
            statistics = analysis_df.describe().to_dict()
            
            # 计算额外的统计信息
            total_rows = statistics.get(list(statistics.keys())[0], {}).get("count", 0)
            analyzed_columns = list(statistics.keys())
            
            return {
                "success": True,
                "result": {
                    "message": f"成功分析 {len(analyzed_columns)} 列数据，共 {total_rows} 行",
                    "file": os.path.basename(file_path),
                    "sheet": sheet_name,
                    "statistics": statistics,
                    "summary": {
                        "total_rows": total_rows,
                        "analyzed_columns": analyzed_columns,
                        "total_columns": len(analyzed_columns)
                    }
                },
                "error": None
            }
            
        except Exception as e:
            return self.handle_error(e)
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        
        if not params.get('filePath'):
            errors.append("请输入Excel文件路径")
        elif not os.path.exists(params['filePath']):
            errors.append("文件不存在")
        elif not params['filePath'].lower().endswith(('.xlsx', '.xls')):
            errors.append("请输入有效的Excel文件")
        
        if not params.get('sheetName'):
            errors.append("请输入工作表名称")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }