from .base_engine import BaseToolEngine
from .file_tools import FileRenameTool, ExcelMergeTool
from .data_tools import DataAnalysisTool
from .image_tools import ImageCompressTool
from .text_tools import TextExtractTool, JsonFormatTool

# 工具实现映射表
TOOL_IMPLEMENTATIONS = {
    'FileRenameTool': FileRenameTool,
    'ExcelMergeTool': ExcelMergeTool,
    'DataAnalysisTool': DataAnalysisTool,
    'ImageCompressTool': ImageCompressTool,
    'TextExtractTool': TextExtractTool,
    'JsonFormatTool': JsonFormatTool
}

def get_tool_implementation(implementation_class):
    """根据实现类名获取工具实现，支持完整类路径"""
    # 如果包含完整类路径，提取类名部分
    if '.' in implementation_class:
        class_name = implementation_class.split('.')[-1]
    else:
        class_name = implementation_class
    return TOOL_IMPLEMENTATIONS.get(class_name)