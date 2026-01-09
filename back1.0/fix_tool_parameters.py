#!/usr/bin/env python
"""
修复工具参数关联问题的脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from toolkit.models import Tool, ToolParameter

def fix_tool_parameters():
    """修复工具参数关联"""
    print("开始修复工具参数关联...")
    
    # 删除所有现有参数
    ToolParameter.objects.all().delete()
    print("已删除所有现有参数")
    
    # 获取所有工具
    tools = Tool.objects.all()
    print(f"找到{tools.count()}个工具")
    
    # 为每个工具创建正确的参数
    tool_params_map = {
        1: [  # 批量重命名文件
            {
                "name": "folderPath",
                "label": "文件夹路径",
                "type": "text",
                "placeholder": "例如: C:\\Users\\Documents\\Files",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 0
            },
            {
                "name": "namingPattern",
                "label": "命名模式",
                "type": "text",
                "placeholder": "例如: File_{index}.txt",
                "default_value": "File_{index}",
                "is_required": True,
                "options": [],
                "order": 1
            },
            {
                "name": "fileType",
                "label": "文件类型筛选",
                "type": "text",
                "placeholder": "例如: .txt,.pdf",
                "default_value": "",
                "is_required": False,
                "options": [],
                "order": 2
            }
        ],
        2: [  # Excel表格合并
            {
                "name": "folderPath",
                "label": "文件夹路径",
                "type": "text",
                "placeholder": "例如: C:\\Users\\Documents\\ExcelFiles",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 0
            },
            {
                "name": "outputFileName",
                "label": "输出文件名",
                "type": "text",
                "placeholder": "例如: merged_data.xlsx",
                "default_value": "merged_data.xlsx",
                "is_required": True,
                "options": [],
                "order": 1
            },
            {
                "name": "includeHeaders",
                "label": "包含表头",
                "type": "boolean",
                "placeholder": "",
                "default_value": "True",
                "is_required": False,
                "options": [],
                "order": 2
            }
        ],
        3: [  # 数据统计分析
            {
                "name": "filePath",
                "label": "文件路径",
                "type": "text",
                "placeholder": "例如: C:\\Users\\Documents\\data.xlsx",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 0
            },
            {
                "name": "sheetName",
                "label": "工作表名称",
                "type": "text",
                "placeholder": "例如: Sheet1",
                "default_value": "",
                "is_required": False,
                "options": [],
                "order": 1
            },
            {
                "name": "analysisColumn",
                "label": "分析列",
                "type": "text",
                "placeholder": "例如: sales",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 2
            }
        ],
        4: [  # 图片批量压缩
            {
                "name": "folderPath",
                "label": "文件夹路径",
                "type": "text",
                "placeholder": "例如: C:\\Users\\Documents\\Images",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 0
            },
            {
                "name": "quality",
                "label": "压缩质量",
                "type": "number",
                "placeholder": "80",
                "default_value": "80",
                "is_required": False,
                "options": [],
                "order": 1
            },
            {
                "name": "maxWidth",
                "label": "最大宽度",
                "type": "number",
                "placeholder": "1920",
                "default_value": "1920",
                "is_required": False,
                "options": [],
                "order": 2
            }
        ],
        5: [  # 文本内容提取
            {
                "name": "filePath",
                "label": "文件路径",
                "type": "text",
                "placeholder": "例如: C:\\Users\\Documents\\sample.pdf",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 0
            },
            {
                "name": "outputFormat",
                "label": "输出格式",
                "type": "select",
                "placeholder": "",
                "default_value": "txt",
                "is_required": False,
                "options": ["txt", "json", "markdown"],
                "order": 1
            }
        ],
        6: [  # JSON格式化
            {
                "name": "jsonContent",
                "label": "JSON内容",
                "type": "textarea",
                "placeholder": "例如: {\"name\": \"value\"}",
                "default_value": "",
                "is_required": True,
                "options": [],
                "order": 0
            },
            {
                "name": "indentSize",
                "label": "缩进大小",
                "type": "number",
                "placeholder": "2",
                "default_value": "2",
                "is_required": False,
                "options": [],
                "order": 1
            }
        ]
    }
    
    # 创建新参数
    for tool_id, params in tool_params_map.items():
        try:
            tool = Tool.objects.get(id=tool_id)
            for param_data in params:
                ToolParameter.objects.create(
                    tool=tool,
                    **param_data
                )
            print(f"已为工具{tool.name}创建{len(params)}个参数")
        except Tool.DoesNotExist:
            print(f"警告：工具ID {tool_id} 不存在")
    
    print("\n修复完成！")
    print(f"总共有{Tool.objects.count()}个工具")
    print(f"总共有{ToolParameter.objects.count()}个参数")
    
    # 验证修复结果
    print("\n验证修复结果：")
    for tool in Tool.objects.all():
        param_count = tool.parameters.count()
        print(f"工具{tool.id} {tool.name}: {param_count}个参数")

if __name__ == "__main__":
    fix_tool_parameters()
