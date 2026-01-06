import os
import json
from typing import Dict, Any
from .base_engine import BaseToolEngine


class TextExtractTool(BaseToolEngine):
    """文本内容提取工具"""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            file_path = params.get('filePath')
            output_format = params.get('outputFormat', 'txt')
            
            # 验证参数
            validation = self.validate_params(params)
            if not validation['valid']:
                return {
                    "success": False,
                    "result": None,
                    "error": "；".join(validation['errors'])
                }
            
            # 获取文件类型
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 模拟文本提取操作（实际环境中需要根据文件类型使用不同的库）
            # text_content = ""
            # 
            # if file_ext == '.pdf':
            #     # 使用PyPDF2或pdfplumber提取PDF文本
            #     import PyPDF2
            #     with open(file_path, 'rb') as file:
            #         reader = PyPDF2.PdfReader(file)
            #         for page_num in range(len(reader.pages)):
            #             page = reader.pages[page_num]
            #             text_content += page.extract_text() + '\n'
            # elif file_ext in ['.doc', '.docx']:
            #     # 使用python-docx提取Word文本
            #     from docx import Document
            #     doc = Document(file_path)
            #     for para in doc.paragraphs:
            #         text_content += para.text + '\n'
            # else:
            #     # 直接读取文本文件
            #     try:
            #         with open(file_path, 'r', encoding='utf-8') as file:
            #             text_content = file.read()
            #     except UnicodeDecodeError:
            #         # 尝试其他编码
            #         with open(file_path, 'r', encoding='gbk') as file:
            #             text_content = file.read()
            
            # 模拟结果
            text_content = "这是从文档中提取的示例文本内容。\n\n在实际应用中，这里将包含从PDF、Word等文档中提取的真实文本。\n\n提取的文本可以保存为纯文本或Markdown格式，便于进一步编辑和使用。"
            
            # 根据输出格式处理内容
            if output_format == 'md':
                # 添加简单的Markdown格式
                processed_content = f"# 从 {os.path.basename(file_path)} 提取的内容\n\n{text_content}"
            else:
                processed_content = text_content
            
            # 模拟保存结果（实际环境中需要实现文件保存）
            # output_file = os.path.splitext(os.path.basename(file_path))[0]
            # output_path = os.path.join(os.path.dirname(file_path), f"{output_file}_extracted.{output_format}")
            # with open(output_path, 'w', encoding='utf-8') as file:
            #     file.write(processed_content)
            
            return {
                "success": True,
                "result": {
                    "message": "成功提取文本内容",
                    "file": os.path.basename(file_path),
                    "output_format": output_format,
                    "content_preview": processed_content[:200] + "..." if len(processed_content) > 200 else processed_content,
                    "content_length": len(processed_content),
                    "word_count": len(processed_content.split()),
                    "line_count": processed_content.count('\n') + 1
                },
                "error": None
            }
            
        except Exception as e:
            return self.handle_error(e)
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        
        if not params.get('filePath'):
            errors.append("请输入文件路径")
        elif not os.path.exists(params['filePath']):
            errors.append("文件不存在")
        
        supported_formats = ['txt', 'md']
        output_format = params.get('outputFormat', 'txt')
        if output_format not in supported_formats:
            errors.append(f"不支持的输出格式，支持的格式：{', '.join(supported_formats)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


class JsonFormatTool(BaseToolEngine):
    """JSON格式化工具"""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            json_content = params.get('jsonContent', '').strip()
            
            # 处理缩进大小
            indent_size_str = params.get('indentSize', 2)
            try:
                if indent_size_str == '' or indent_size_str is None:
                    indent_size = 2
                else:
                    indent_size = int(indent_size_str)
            except (ValueError, TypeError):
                indent_size = 2  # 使用默认值
            
            # 验证参数
            validation = self.validate_params(params)
            if not validation['valid']:
                return {
                    "success": False,
                    "result": None,
                    "error": "；".join(validation['errors']),
                    "details": validation['errors']
                }
            
            # 解析并格式化JSON
            try:
                # 尝试解析JSON
                parsed_json = json.loads(json_content)
                
                # 格式化JSON
                formatted_json = json.dumps(
                    parsed_json, 
                    ensure_ascii=False, 
                    indent=indent_size,
                    sort_keys=False  # 保持原有键的顺序
                )
                
                # 计算统计信息
                original_size = len(json_content)
                formatted_size = len(formatted_json)
                
                return {
                    "success": True,
                    "result": {
                        "message": "JSON格式化成功",
                        "formatted_json": formatted_json,
                        "statistics": {
                            "original_size": original_size,
                            "formatted_size": formatted_size,
                            "size_difference": formatted_size - original_size,
                            "indent_size": indent_size,
                            "line_count": formatted_json.count('\n') + 1
                        }
                    },
                    "error": None
                }
                
            except json.JSONDecodeError as e:
                error_msg = str(e)
                # 提供更友好的错误信息
                if "Expecting" in error_msg:
                    error_msg = f"JSON格式错误：{error_msg}"
                elif "Unterminated" in error_msg:
                    error_msg = f"JSON格式错误：字符串未正确结束"
                else:
                    error_msg = f"JSON格式错误：{error_msg}"
                
                return {
                    "success": False,
                    "result": None,
                    "error": error_msg,
                    "details": [error_msg]
                }
            
        except Exception as e:
            return self.handle_error(e)
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        
        json_content = params.get('jsonContent', '')
        if not json_content:
            errors.append("请输入JSON内容")
        elif isinstance(json_content, str) and json_content.strip() == '':
            errors.append("JSON内容不能为空")
        
        indent_size_str = params.get('indentSize', 2)
        try:
            if indent_size_str == '' or indent_size_str is None:
                indent_size = 2  # 使用默认值
            else:
                indent_size = int(indent_size_str)
            
            if indent_size < 1 or indent_size > 8:
                errors.append("缩进空格数必须在1-8之间")
        except (ValueError, TypeError):
            errors.append("缩进空格数必须是1-8之间的整数")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }