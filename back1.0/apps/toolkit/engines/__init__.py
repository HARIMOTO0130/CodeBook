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
    """根据实现类名获取工具实现"""
    return TOOL_IMPLEMENTATIONS.get(implementation_class)