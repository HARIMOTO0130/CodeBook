import re
import json
from typing import List, Dict, Any

class ContentConverter:
    """内容格式转换器，支持.docx内容转换为Markdown和Jupyter格式"""
    
    def __init__(self):
        """初始化转换器"""
        self.markdown_tables = []  # 存储提取的表格
        self.markdown_images = []  # 存储提取的图片
    
    def docx_to_markdown(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """将.docx章节内容转换为Markdown格式
        
        Args:
            chapters: 章节内容列表
            
        Returns:
            转换后的Markdown内容，包含目录和章节内容
        """
        markdown_chapters = []
        toc_markdown = []
        
        # 转换每个章节
        for i, chapter in enumerate(chapters):
            # 转换标题（根据级别添加#）
            title_level = chapter['level']
            # 确保级别在1-6之间
            if title_level < 1:
                title_level = 1
            elif title_level > 9:
                title_level = 6
            else:
                title_level = min(6, title_level)
            
            # 创建Markdown标题
            title_md = f"{'#' * title_level} {chapter['title']}"
            
            # 转换正文内容
            content_md = self._convert_text_to_markdown(chapter['content'])
            
            # 组合章节内容
            chapter_md = f"{title_md}\n\n{content_md}\n"
            
            # 添加到TOC
            toc_md = f"{'  ' * (title_level - 1)}* [{chapter['title']}](#{'#'.join(title_md.split('#')[1:]).strip()})"
            toc_markdown.append(toc_md)
            
            # 添加到章节列表
            markdown_chapters.append({
                'title': chapter['title'],
                'level': title_level,
                'content': chapter_md
            })
        
        # 组合完整的Markdown内容
        full_markdown = "\n".join(toc_markdown) + "\n\n" + "\n\n".join(chap['content'] for chap in markdown_chapters)
        
        return {
            'toc': toc_markdown,
            'chapters': markdown_chapters,
            'full_content': full_markdown
        }
    
    def _convert_text_to_markdown(self, text: str) -> str:
        """将纯文本转换为Markdown格式
        
        Args:
            text: 纯文本内容
            
        Returns:
            Markdown格式的文本
        """
        if not text:
            return ""
        
        # 处理空行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 处理代码块（增强检测）
        # 检测可能的代码块，包括：
        # 1. 以 | #例X.X: 开头的代码示例
        # 2. 包含常见代码关键词或缩进的代码
        # 3. 输入-处理-输出结构的代码
        lines = text.split('\n')
        
        # 检测特殊的代码示例格式：| #例4.2: 输入-处理-输出（IPO）模式
        example_start_pattern = re.compile(r'^\s*\|\s*#例\s*\d+\.\d+\s*[:：].*$')  # 支持中英文冒号
        example_end_pattern = re.compile(r'^\s*\|\s*---\s*\|$')
        
        # 处理普通代码块的状态
        in_code_block = False
        code_lines = []
        
        processed_lines = []
        i = 0
        n = len(lines)
        
        while i < n:
            line = lines[i]
            stripped = line.strip()
            
            # 检测特殊代码示例的开始
            if example_start_pattern.match(line):
                # 先保存当前可能的代码块
                if in_code_block:
                    processed_lines.append('```python')
                    processed_lines.extend(code_lines)
                    processed_lines.append('```')
                    in_code_block = False
                    code_lines = []
                
                # 收集整个代码示例块
                example_content = []
                i += 1
                
                # 继续收集直到遇到结束标记
                while i < n:
                    current_line = lines[i]
                    current_stripped = current_line.strip()
                    
                    # 检查是否结束
                    if example_end_pattern.match(current_line) or current_stripped == '| --- |':
                        i += 1
                        break
                    
                    # 清理行首的 | 符号
                    clean_line = re.sub(r'^\s*\|\s*', '', current_line)
                    example_content.append(clean_line.strip())  # 清理多余空格
                    i += 1
                
                # 将整个代码示例块作为一个代码块添加
                processed_lines.append('```python')
                processed_lines.extend(example_content)
                processed_lines.append('```')
            else:
                # 处理普通代码块
                stripped_line = line.strip()
                
                # 简单的代码块检测规则
                is_code_line = (
                    stripped_line.startswith(('def ', 'class ', 'import ', 'from ', 'for ', 'while ', 'if ', 'else:', 'elif ', 'print(')) or
                    re.search(r'\b(print|return|try|except|finally|with|lambda|input)\b', stripped_line) or
                    re.match(r'^\s{4,}', line)  # 缩进4个或更多空格
                )
                
                if is_code_line and not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    code_lines = [line]
                elif is_code_line and in_code_block:
                    # 继续代码块
                    code_lines.append(line)
                elif not is_code_line and in_code_block:
                    # 结束代码块
                    in_code_block = False
                    processed_lines.append('```python')
                    processed_lines.extend(code_lines)
                    processed_lines.append('```')
                    processed_lines.append(line)
                    code_lines = []
                else:
                    # 普通文本
                    processed_lines.append(line)
                
                i += 1
        
        # 处理剩余的代码块
        if in_code_block:
            processed_lines.append('```python')
            processed_lines.extend(code_lines)
            processed_lines.append('```')
        
        text = '\n'.join(processed_lines)
        
        # 处理列表（简单检测）
        text = re.sub(r'^\s*[1-9]\d*\s*[、.。，]\s*(.*)$', r'1. \1', text, flags=re.MULTILINE)  # 数字列表
        text = re.sub(r'^\s*[一二三四五六七八九十百千]+[、.。，]\s*(.*)$', r'- \1', text, flags=re.MULTILINE)  # 中文数字列表
        text = re.sub(r'^\s*[①②③④⑤⑥⑦⑧⑨⑩]\s*(.*)$', r'- \1', text, flags=re.MULTILINE)  # 特殊编号
        text = re.sub(r'^\s*[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽]\s*(.*)$', r'- \1', text, flags=re.MULTILINE)  # 括号数字
        
        # 处理粗体和斜体（简单检测）
        text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)  # 粗体
        text = re.sub(r'\*(.*?)\*', r'*\1*', text)  # 斜体
        
        return text
    
    def markdown_to_jupyter(self, markdown_content: str, language: str = 'python') -> Dict[str, Any]:
        """将Markdown内容转换为Jupyter Notebook格式
        
        Args:
            markdown_content: Markdown格式的内容
            language: 代码语言，默认为Python
            
        Returns:
            Jupyter Notebook格式的JSON数据
        """
        # 简单直接的实现：使用正则表达式匹配代码块
        import re
        
        # 匹配所有代码块
        code_block_pattern = re.compile(r'```python\n(.*?)```', re.DOTALL)
        
        # 将Markdown内容分割为代码块和非代码块
        parts = []
        last_end = 0
        
        for match in code_block_pattern.finditer(markdown_content):
            # 添加代码块前面的普通内容
            if match.start() > last_end:
                parts.append({
                    'type': 'markdown',
                    'content': markdown_content[last_end:match.start()]
                })
            
            # 添加代码块
            parts.append({
                'type': 'code',
                'content': match.group(1)
            })
            
            last_end = match.end()
        
        # 添加最后一个代码块后面的普通内容
        if last_end < len(markdown_content):
            parts.append({
                'type': 'markdown',
                'content': markdown_content[last_end:]
            })
        
        # 构建Jupyter单元格
        cells = []
        
        for part in parts:
            if part['type'] == 'code':
                # 创建代码单元格
                cells.append({
                    'cell_type': 'code',
                    'source': part['content'].split('\n'),
                    'metadata': {},
                    'execution_count': None,
                    'outputs': []
                })
            else:
                # 创建Markdown单元格
                cells.append({
                    'cell_type': 'markdown',
                    'source': part['content'].split('\n'),
                    'metadata': {}
                })
        
        # 创建完整的Jupyter Notebook结构
        jupyter_notebook = {
            'cells': cells,
            'metadata': {
                'kernelspec': {
                    'display_name': f'{language.capitalize()}',
                    'language': language,
                    'name': language
                },
                'language_info': {
                    'name': language,
                    'version': '3.9.0'
                }
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }
        
        return jupyter_notebook
    
    def convert_to_jupyter(self, chapters: List[Dict[str, Any]], language: str = 'python') -> Dict[str, Any]:
        """直接将.docx章节内容转换为Jupyter Notebook格式
        
        Args:
            chapters: 章节内容列表
            language: 代码语言
            
        Returns:
            Jupyter Notebook格式的JSON数据
        """
        # 先转换为Markdown
        md_result = self.docx_to_markdown(chapters)
        
        # 再转换为Jupyter格式
        jupyter_content = self.markdown_to_jupyter(md_result['full_content'], language)
        
        return {
            'jupyter_content': jupyter_content,
            'markdown_content': md_result
        }
    
    def _detect_code_language(self, code: str) -> str:
        """检测代码语言
        
        Args:
            code: 代码内容
            
        Returns:
            检测到的编程语言
        """
        # Python特征
        python_features = ['def ', 'import ', 'from ', 'print(', 'class ', 'self.', ':']
        # JavaScript特征
        js_features = ['function', 'var ', 'let ', 'const ', 'console.log', '=>', 'require(', 'module.exports']
        # Java特征
        java_features = ['public class', 'public static void main', 'System.out.println', 'import java.', 'private ', 'protected ']
        
        # 计算每种语言的特征匹配数
        python_score = sum(1 for feature in python_features if feature in code)
        js_score = sum(1 for feature in js_features if feature in code)
        java_score = sum(1 for feature in java_features if feature in code)
        
        # 选择得分最高的语言
        scores = {'python': python_score, 'javascript': js_score, 'java': java_score}
        detected_language = max(scores, key=scores.get)
        
        # 如果没有明显特征，默认返回Python
        if scores[detected_language] == 0:
            detected_language = 'python'
        
        return detected_language


def convert_content(content: Dict[str, Any], output_format: str = 'markdown', language: str = 'python') -> Dict[str, Any]:
    """转换内容格式的主函数
    
    Args:
        content: 输入内容，包含章节信息
        output_format: 输出格式，可选'markdown'或'jupyter'
        language: 代码语言
        
    Returns:
        转换后的内容
    """
    converter = ContentConverter()
    
    if output_format == 'jupyter':
        return converter.convert_to_jupyter(content['chapters'], language)
    else:
        return converter.docx_to_markdown(content['chapters'])
