import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from toolkit.models import ToolCategory, Tool, ToolParameter

def create_initial_data():
    """创建初始化数据"""
    print("开始创建工具包初始化数据...")
    
    # 创建分类
    categories = [
        {'name': '文件处理', 'slug': 'file', 'description': '处理各种文件的工具集合'},
        {'name': '数据处理', 'slug': 'data', 'description': '数据分析和处理工具'},
        {'name': '图片处理', 'slug': 'image', 'description': '图片编辑和优化工具'},
        {'name': '文本处理', 'slug': 'text', 'description': '文本分析和转换工具'},
    ]
    
    category_map = {}
    for cat_data in categories:
        category, created = ToolCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': cat_data['slug'],
                'description': cat_data['description']
            }
        )
        category_map[cat_data['slug']] = category
        print(f"{'创建' if created else '更新'} 分类: {cat_data['name']}")
    
    # 创建工具
    tools = [
        # 文件处理工具
        {
            'category': 'file',
            'name': '批量重命名文件',
            'slug': 'file-rename',
            'description': '批量重命名文件夹中的文件',
            'icon': 'file-text',
            'implementation_class': 'file_tools.FileRenameTool',
            'parameters': [
                {
                    'name': 'folderPath',
                    'label': '文件夹路径',
                    'type': 'text',
                    'required': True,
                    'description': '包含需要重命名文件的文件夹路径',
                    'placeholder': '例如: C:\\Users\\Documents\\Files'
                },
                {
                    'name': 'namingPattern',
                    'label': '命名模式',
                    'type': 'text',
                    'required': True,
                    'description': '文件命名模式，使用{index}作为序号占位符',
                    'placeholder': '例如: File_{index}.txt',
                    'default_value': 'File_{index}'
                },
                {
                    'name': 'fileType',
                    'label': '文件类型筛选',
                    'type': 'text',
                    'required': False,
                    'description': '筛选特定类型的文件，如.txt,.jpg等，留空表示所有文件',
                    'placeholder': '例如: .txt,.pdf'
                }
            ]
        },
        {
            'category': 'file',
            'name': 'Excel表格合并',
            'slug': 'excel-merge',
            'description': '合并多个Excel文件到一个工作簿',
            'icon': 'table',
            'implementation_class': 'file_tools.ExcelMergeTool',
            'parameters': [
                {
                    'name': 'folderPath',
                    'label': '文件夹路径',
                    'type': 'text',
                    'required': True,
                    'description': '包含Excel文件的文件夹路径',
                    'placeholder': '例如: C:\\Users\\Documents\\ExcelFiles'
                },
                {
                    'name': 'outputFileName',
                    'label': '输出文件名',
                    'type': 'text',
                    'required': True,
                    'description': '合并后的Excel文件名',
                    'placeholder': '例如: merged_data.xlsx',
                    'default_value': 'merged_data.xlsx'
                },
                {
                    'name': 'includeHeaders',
                    'label': '包含表头',
                    'type': 'boolean',
                    'required': False,
                    'description': '是否在每个工作表中包含表头',
                    'default_value': True
                }
            ]
        },
        # 数据处理工具
        {
            'category': 'data',
            'name': '数据统计分析',
            'slug': 'data-analysis',
            'description': '分析Excel或CSV文件中的数据',
            'icon': 'bar-chart',
            'implementation_class': 'data_tools.DataAnalysisTool',
            'parameters': [
                {
                    'name': 'filePath',
                    'label': '文件路径',
                    'type': 'text',
                    'required': True,
                    'description': 'Excel或CSV文件路径',
                    'placeholder': '例如: C:\\Users\\Documents\\data.xlsx'
                },
                {
                    'name': 'sheetName',
                    'label': '工作表名称',
                    'type': 'text',
                    'required': False,
                    'description': 'Excel文件中的工作表名称，CSV文件不需要',
                    'placeholder': '例如: Sheet1'
                },
                {
                    'name': 'analysisColumn',
                    'label': '分析列',
                    'type': 'text',
                    'required': True,
                    'description': '要分析的数据列名',
                    'placeholder': '例如: sales'
                }
            ]
        },
        # 图片处理工具
        {
            'category': 'image',
            'name': '图片批量压缩',
            'slug': 'image-compress',
            'description': '批量压缩文件夹中的图片文件',
            'icon': 'image',
            'implementation_class': 'image_tools.ImageCompressTool',
            'parameters': [
                {
                    'name': 'folderPath',
                    'label': '文件夹路径',
                    'type': 'text',
                    'required': True,
                    'description': '包含图片文件的文件夹路径',
                    'placeholder': '例如: C:\\Users\\Documents\\Images'
                },
                {
                    'name': 'quality',
                    'label': '压缩质量',
                    'type': 'number',
                    'required': False,
                    'description': '压缩质量(1-100)，数值越低压缩率越高',
                    'min_value': 1,
                    'max_value': 100,
                    'default_value': 80
                },
                {
                    'name': 'maxWidth',
                    'label': '最大宽度',
                    'type': 'number',
                    'required': False,
                    'description': '图片最大宽度(像素)，0表示保持原尺寸',
                    'min_value': 0,
                    'default_value': 1920
                }
            ]
        },
        # 文本处理工具
        {
            'category': 'text',
            'name': '文本内容提取',
            'slug': 'text-extract',
            'description': '从各种文件中提取文本内容',
            'icon': 'align-left',
            'implementation_class': 'text_tools.TextExtractTool',
            'parameters': [
                {
                    'name': 'filePath',
                    'label': '文件路径',
                    'type': 'text',
                    'required': True,
                    'description': '要提取文本的文件路径',
                    'placeholder': '例如: C:\\Users\\Documents\\sample.pdf'
                },
                {
                    'name': 'outputFormat',
                    'label': '输出格式',
                    'type': 'select',
                    'required': False,
                    'description': '文本输出格式',
                    'options': ['txt', 'json', 'markdown'],
                    'default_value': 'txt'
                }
            ]
        },
        {
            'category': 'text',
            'name': 'JSON格式化',
            'slug': 'json-format',
            'description': '格式化和美化JSON字符串',
            'icon': 'code',
            'implementation_class': 'text_tools.JsonFormatTool',
            'parameters': [
                {
                    'name': 'jsonContent',
                    'label': 'JSON内容',
                    'type': 'textarea',
                    'required': True,
                    'description': '要格式化的JSON字符串',
                    'placeholder': '例如: {"name":"value"}'
                },
                {
                    'name': 'indentSize',
                    'label': '缩进大小',
                    'type': 'number',
                    'required': False,
                    'description': 'JSON缩进空格数',
                    'min_value': 1,
                    'max_value': 8,
                    'default_value': 2
                }
            ]
        }
    ]
    
    for tool_data in tools:
        category = category_map.get(tool_data['category'])
        if not category:
            print(f"警告: 未找到分类 {tool_data['category']}")
            continue
        
        tool, created = Tool.objects.get_or_create(
            name=tool_data['name'],
            defaults={
                'slug': tool_data['slug'],
                'description': tool_data['description'],
                'icon': tool_data['icon'],
                'category': category,
                'implementation_class': tool_data['implementation_class'],
                'is_active': True
            }
        )
        
        if created:
            print(f"创建工具: {tool_data['name']}")
        else:
            print(f"更新工具: {tool_data['name']}")
        
        # 创建或更新参数
        for param_data in tool_data['parameters']:
            # 准备参数数据，只包含模型中存在的字段
            defaults = {
                'label': param_data['label'],
                'type': param_data['type'],
                'placeholder': param_data.get('placeholder', ''),
                'default_value': param_data.get('default_value', ''),
                'is_required': param_data.get('required', True),
                'options': param_data.get('options', [])
            }
            
            param, param_created = ToolParameter.objects.get_or_create(
                tool=tool,
                name=param_data['name'],
                defaults=defaults
            )
            
            # 如果参数已存在，更新字段
            if not param_created:
                for key, value in defaults.items():
                    setattr(param, key, value)
                param.save()
    
    print("初始化数据创建完成！")

if __name__ == '__main__':
    create_initial_data()