"""书籍视图函数"""
from rest_framework import viewsets, status, decorators
from rest_framework.exceptions import PermissionDenied
import threading
import tempfile
import os
import cv2
import numpy as np
from PIL import Image
import re
import json

# 为了兼容性，定义action装饰器
action = decorators.action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Max, Avg
from .models import Book, Chapter
from .serializers import BookListSerializer, BookDetailSerializer, ChapterSerializer, ChapterDetailSerializer
from apps.learning.models import LearningRecord
from .advanced_processor import AdvancedPDFProcessor


class BookViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete']  # 只允许GET、POST和DELETE操作
    """书籍视图集"""
    queryset = Book.objects.all()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化高级PDF处理器
        self.advanced_processor = AdvancedPDFProcessor()
    
    def get_permissions(self):
        # GET操作不需要认证，其他操作（包括DELETE）需要认证
        if self.action in ['list', 'retrieve']:
            return []
        return [IsAuthenticated()]
    
    def get_queryset(self):
        # 重写方法以避免冲突
        # 第一个get_queryset已经被上面的list方法使用
        return Book.objects.all()
    
    def perform_destroy(self, instance):
        # 确保只有书籍所有者可以删除
        if instance.owner != self.request.user and not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied("您没有权限删除这本教材")
        # 调用模型的delete方法，这将同时删除数据库记录和相关的PDF文件
        instance.delete()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookDetailSerializer
    
    def get_queryset(self):
        # 对于列表视图，我们需要预先加载相关数据
        queryset = Book.objects.all()
        
        # 如果用户已登录，我们可以在序列化器中计算进度
        if self.request.user.is_authenticated:
            # 这里可以添加逻辑来获取用户的学习进度
            pass
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """获取书籍列表，包含用户学习进度信息"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # 确保所有书籍都有进度和最后学习时间字段
        for item in serializer.data:
            # 设置默认值
            item['progress'] = 0
            item['last_learn_time'] = None
        
        # 如果用户已登录，添加进度信息
        if request.user.is_authenticated:
            book_ids = [b.id for b in queryset]
            if book_ids:
                aggregates = (
                    LearningRecord.objects
                    .filter(user=request.user, book_id__in=book_ids)
                    .values('book_id')
                    .annotate(
                        avg_progress=Avg('progress'),
                        last_time=Max('last_learn_time')
                    )
                )
                book_id_to_stats = {a['book_id']: a for a in aggregates}
                for item in serializer.data:
                    stats = book_id_to_stats.get(item['id'])
                    if stats:
                        item['progress'] = int(stats['avg_progress']) if stats['avg_progress'] is not None else 0
                        item['last_learn_time'] = stats['last_time'].isoformat() if stats['last_time'] else None
        
        return Response(serializer.data)

    def _extract_pdf_to_images(self, pdf_path):
        """将PDF转换为图像列表"""
        try:
            from pdf2image import convert_from_path
            # 转换PDF到图像列表，使用300dpi以获得较好的质量
            images = convert_from_path(pdf_path, dpi=300)
            return images
        except Exception as e:
            print(f"PDF转图像失败: {e}")
            return []
    
    def _extract_text_with_ocr(self, image):
        """使用OCR从图像中提取文本"""
        try:
            import pytesseract
            # 转换PIL图像到OpenCV格式
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            # 灰度转换
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # 二值化处理
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            # 使用Tesseract OCR提取文本
            text = pytesseract.image_to_string(binary, lang='chi_sim+eng')
            return text
        except Exception as e:
            print(f"OCR提取失败: {e}")
            return ""
    
    def _detect_content_regions(self, image):
        """检测图像中的内容区域和类型"""
        try:
            # 加载预训练的布局检测模型
            model = lp.Detectron2LayoutModel(
                config_path="lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
            )
            
            # 转换PIL图像到OpenCV格式
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 进行布局检测
            layout = model.detect(img_cv)
            
            # 提取不同类型的区域
            regions = []
            for block in layout:
                regions.append({
                    'type': block.type,
                    'coordinates': block.coordinates,
                    'confidence': block.score
                })
            
            return regions
        except Exception as e:
            print(f"内容区域检测失败: {e}")
            return []
    
    def _classify_content_type(self, text):
        """使用文本特征分类内容类型"""
        try:
            # 简单的内容类型分类
            # 代码块特征：包含大量特殊字符、缩进、关键词
            code_patterns = [
                r'def\s+\w+\s*\(', r'function\s+\w+', r'class\s+\w+',
                r'if\s*\(', r'for\s*\(', r'while\s*\(',
                r'\{[^}]*\}', r'\[[^\]]*\]', r'\([^)]*\)',
                r'\s*=\s*['+'"'+'\''+'].*['+'"'+'\''+']', r'import\s+\w+'
            ]
            
            # 检查是否为代码块
            code_score = sum(1 for pattern in code_patterns if re.search(pattern, text))
            
            # 表格特征：包含|或,分隔的数据
            table_pattern = r'^\s*\|.*\|\s*$|^\s*\w+,\s*\w+'
            is_table = bool(re.search(table_pattern, text, re.MULTILINE))
            
            # 标题特征：较短，可能全大写或包含数字+点
            title_pattern = r'^\s*([0-9]+\.|[一二三四五六七八九十]、)\s*\w+.*$|^\s*[A-Z\s]+$'
            is_title = bool(re.search(title_pattern, text, re.MULTILINE))
            
            if code_score > 3 or 'print(' in text or 'console.log(' in text:
                return 'code'
            elif is_table:
                return 'table'
            elif is_title and len(text.split()) < 10:
                return 'title'
            else:
                return 'text'
        except Exception:
            return 'text'
    
    def _is_figure_or_table_title(self, line):
        """快速判断是否为图表或表格标题"""
        # 全面的图表标题模式
        figure_patterns = [
            r'^\s*图\s*\d+[-.]?\d*\s*[：:].*$',      # 图1.1：
            r'^\s*图\s*\d+[-.]?\d*\s+.*$',          # 图1.1 
            r'^\s*图\s*[一二三四五六七八九十百千]+\s*[：:].*$',  # 图一：
            r'^\s*图\s*[一二三四五六七八九十百千]+\s+.*$',      # 图一 
            r'^\s*图示\s*\d*[：:].*$',              # 图示：
            r'^\s*图表\s*\d*[：:].*$',              # 图表：
            r'^\s*Figure\s*\d+[-.]?\d*\s*[：:].*$', # Figure 1.1:
            r'^\s*Fig\.?\s*\d+[-.]?\d*\s*[：:].*$',  # Fig. 1.1:
            # 捕获类似"图1 Oracle主页"这种格式
            r'^\s*图\s*(\d+[-.]?\d*)\s+(.+)$',
            # 捕获更宽松的图表标题格式
            r'^\s*图(\d+[-.]?\d*)[：:].*$',         # 图1.1:（无空格）
            r'^\s*图\s*(\d+[-.]?\d*)\s*[^：:]*$',   # 图1.1（无冒号）
        ]
        
        # 全面的表格标题模式
        table_patterns = [
            r'^\s*表\s*\d+[-.]?\d*\s*[：:].*$',      # 表1.1：
            r'^\s*表\s*\d+[-.]?\d*\s+.*$',          # 表1.1 
            r'^\s*表格\s*\d*[：:].*$',              # 表格：
            r'^\s*Table\s*\d+[-.]?\d*\s*[：:].*$', # Table 1.1:
            r'^\s*Tab\.?\s*\d+[-.]?\d*\s*[：:].*$',  # Tab. 1.1:
            # 捕获更宽松的表格标题格式
            r'^\s*表(\d+[-.]?\d*)[：:].*$',         # 表1.1:（无空格）
            r'^\s*表\s*(\d+[-.]?\d*)\s*[^：:]*$',   # 表1.1（无冒号）
        ]
        
        # 检查是否匹配任何图表标题模式
        for pattern in figure_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # 检查是否匹配任何表格标题模式
        for pattern in table_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _direct_chapter_detection(self, pages_data):
        """直接使用_is_true_chapter_title方法进行章节检测，包括主章节和二级标题"""
        print("执行直接章节检测...")
        chapters = []
        current_chapter = None
        current_subsection = None
        full_text = '\n'.join([page['text'] for page in pages_data])
        
        # 逐页逐行扫描查找章节标题和二级标题
        for page_idx, page in enumerate(pages_data):
            lines = page['text'].splitlines()
            
            for line_idx, line in enumerate(lines):
                # 清理行文本
                line = line.strip()
                
                # 检查是否为章标题
                if self._is_true_chapter_title(line, line_idx, full_text, page.get('regions', []), False):
                    print(f"检测到章节标题: {line} (第{page_idx+1}页)")
                    
                    # 结束当前章节（如果有）
                    if current_chapter:
                        current_chapter['end_page'] = page_idx
                        chapters.append(current_chapter)
                    
                    # 开始新章节
                    current_chapter = {
                        'title': line,
                        'content': line + '\n\n',
                        'start_page': page_idx,
                        'end_page': page_idx,
                        'subsections': []  # 为每个主章节创建子章节列表
                    }
                    current_subsection = None
                # 检查是否为二级标题
                elif self._is_true_chapter_title(line, line_idx, full_text, page.get('regions', []), True):
                    print(f"检测到二级标题: {line} (第{page_idx+1}页)")
                    
                    # 只有在存在当前章节的情况下才添加二级标题
                    if current_chapter:
                        # 结束当前二级标题（如果有）
                        if current_subsection:
                            current_subsection['end_page'] = page_idx
                            current_chapter['subsections'].append(current_subsection)
                        
                        # 开始新二级标题
                        current_subsection = {
                            'title': line,
                            'content': line + '\n\n',
                            'start_page': page_idx,
                            'end_page': page_idx
                        }
                elif current_subsection:
                    # 添加内容到当前二级标题
                    current_subsection['content'] += line + '\n'
                    current_subsection['end_page'] = page_idx
                elif current_chapter:
                    # 添加内容到当前章节
                    current_chapter['content'] += line + '\n'
                    current_chapter['end_page'] = page_idx
        
        # 添加最后一个二级标题（如果有）
        if current_subsection and current_chapter:
            current_subsection['end_page'] = len(pages_data) - 1
            current_chapter['subsections'].append(current_subsection)
        
        # 添加最后一个章节
        if current_chapter:
            current_chapter['end_page'] = len(pages_data) - 1
            chapters.append(current_chapter)
        
        print(f"直接检测到{len(chapters)}个章节")
        # 统计二级标题数量
        total_subsections = sum(len(chapter.get('subsections', [])) for chapter in chapters)
        print(f"检测到{total_subsections}个二级标题")
        return chapters
    
    def _advanced_chapter_detection(self, pages_data, images):
        """高级章节检测算法，集成NLP、计算机视觉技术和文档结构分析"""
        try:
            print("执行增强的高级章节检测...")
            
            # 首先使用直接检测方法，确保能识别基本的章节格式
            direct_chapters = self._direct_chapter_detection(pages_data)
            
            # 如果直接检测到章节，优先使用
            if direct_chapters:
                print(f"直接检测成功，找到{len(direct_chapters)}个章节")
                # 优化章节边界
                optimized_chapters = self._optimize_chapter_boundaries(direct_chapters, pages_data)
                return optimized_chapters
            
            # 从BookViewSet获取document_structure（如果可用）
            document_structure = getattr(self, '_document_structure', None)
            
            # 如果有文档结构信息，优先使用它进行章节检测
            if document_structure and 'content_blocks' in document_structure:
                print("使用文档结构分析结果进行章节检测...")
                
                content_blocks = document_structure['content_blocks']
                chapters = []
                current_chapter = None
                
                # 基于内容块重建章节
                for block_idx, block in enumerate(content_blocks):
                    block_type = block.get('type', 'text')
                    block_content = block.get('content', '')
                    page_num = block.get('page_number', 0)
                    
                    # 检查是否为章节标题格式
                    is_chapter_title = self._is_true_chapter_title(block_content, 0, '', [], False)
                    
                    # 如果是标题块或符合章节标题格式，开始新章节
                    if (block_type == 'title' or is_chapter_title) and block_content.strip():
                        # 结束当前章节（如果有）
                        if current_chapter:
                            current_chapter['end_page'] = page_num - 1
                            chapters.append(current_chapter)
                        
                        # 开始新章节
                        current_chapter = {
                            'title': block_content.strip(),
                            'content': block_content + '\n\n',
                            'start_page': page_num,
                            'end_page': page_num
                        }
                    elif current_chapter:
                        # 添加内容到当前章节
                        current_chapter['content'] += block_content + '\n\n'
                        current_chapter['end_page'] = max(current_chapter['end_page'], page_num)
                
                # 添加最后一个章节
                if current_chapter:
                    chapters.append(current_chapter)
                
                # 如果通过文档结构检测到章节，进行处理
                if chapters:
                    print(f"通过文档结构检测到{len(chapters)}个章节")
                    
                    # 如果有目录对齐信息，使用它优化章节标题
                    if document_structure.get('toc_alignments'):
                        toc_alignments = document_structure['toc_alignments']
                        print(f"应用目录对齐信息优化章节标题，找到{len(toc_alignments)}个对齐项")
                        
                        # 映射章节到目录项
                        for alignment in toc_alignments:
                            for chapter in chapters:
                                # 基于相似度匹配章节
                                if self._calculate_text_similarity(
                                    chapter['title'].lower(), 
                                    alignment['content_heading']['title'].lower()
                                ) > 0.7:
                                    # 使用目录项标题（通常更规范）
                                    if len(alignment['toc_item']['title']) > len(chapter['title']):
                                        chapter['title'] = alignment['toc_item']['title']
                                    chapter['toc_verified'] = True
                                    break
                    
                    # 优化章节边界
                    optimized_chapters = self._optimize_chapter_boundaries(chapters, pages_data)
                    return optimized_chapters
            
            # 使用高级处理器进行章节检测
            try:
                chapters = self.advanced_processor.enhance_chapter_detection(pages_data, images)
                
                # 如果检测到章节，进行优化
                if chapters:
                    print(f"高级处理器检测到{len(chapters)}个章节")
                    # 优化章节边界
                    optimized_chapters = self._optimize_chapter_boundaries(chapters, pages_data)
                    return optimized_chapters
            except Exception as proc_error:
                print(f"高级处理器错误: {str(proc_error)}")
            
            # 如果所有方法都失败，使用基于章节标题格式的直接扫描
            print("所有其他方法失败，使用基于行的直接扫描")
            direct_scan_chapters = []
            current_chapter = None
            
            # 逐页逐行扫描查找章节标题
            for page_idx, page in enumerate(pages_data):
                lines = page['text'].splitlines()
                
                for line_idx, line in enumerate(lines):
                    # 清理行文本
                    line = line.strip()
                    
                    # 检查是否符合章节标题格式
                    if re.match(r'^第\s*[一二三四五六七八九十百千\d]+\s*章', line) or \
                       (re.match(r'^\d+\.\s+', line) and not re.search(r'\d+\.\d+', line)):
                        print(f"直接扫描检测到章节标题: {line} (第{page_idx+1}页)")
                        
                        # 结束当前章节（如果有）
                        if current_chapter:
                            current_chapter['end_page'] = page_idx
                            direct_scan_chapters.append(current_chapter)
                        
                        # 开始新章节
                        current_chapter = {
                            'title': line,
                            'content': line + '\n\n',
                            'start_page': page_idx,
                            'end_page': page_idx
                        }
                    elif current_chapter:
                        # 添加内容到当前章节
                        current_chapter['content'] += line + '\n'
                        current_chapter['end_page'] = page_idx
            
            # 添加最后一个章节
            if current_chapter:
                direct_scan_chapters.append(current_chapter)
            
            if direct_scan_chapters:
                print(f"直接扫描检测到{len(direct_scan_chapters)}个章节")
                optimized_chapters = self._optimize_chapter_boundaries(direct_scan_chapters, pages_data)
                return optimized_chapters
            else:
                # 如果真的没有检测到章节，使用回退方法
                print("无法检测到章节，使用回退方法")
                return self._fallback_chapter_splitting(pages_data)
                
        except Exception as e:
            print(f"高级章节检测错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 发生错误时，使用直接扫描作为最后的回退
            try:
                print("发生异常，使用直接扫描作为最后的回退")
                return self._direct_chapter_detection(pages_data)
            except:
                # 如果直接扫描也失败，使用简单回退
                return self._fallback_chapter_splitting(pages_data)
    
    def _calculate_text_similarity(self, text1, text2):
        """计算文本相似度（简化版本）"""
        # 移除空格并转换为集合
        set1 = set(text1.replace(' ', ''))
        set2 = set(text2.replace(' ', ''))
        
        # 计算Jaccard相似度
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union
    
    def _is_true_chapter_title(self, line, line_idx, full_text, regions, is_subsection=False):
        """判断一行文本是否为真正的章节标题（识别章标题和二级标题）
        
        Args:
            line: 要判断的文本行
            line_idx: 行在文本中的索引
            full_text: 完整文本
            regions: 内容区域信息
            is_subsection: 是否为子章节（支持二级标题检测）
        """
        # 清理行文本
        line = line.strip()
        
        # 快速排除明显不是标题的情况
        # 图表相关内容
        figure_patterns = [
            r'^图\s*\d+[-.]?\d*\s*[：:].*$',
            r'^图\s*[一二三四五六七八九十百千]+\s*[：:].*$',
            r'^图示|图表\s*\d*[：:].*$',
            r'^图\s+\d+[-.]?\d*\s+.+$'
        ]
        for pattern in figure_patterns:
            if re.match(pattern, line):
                return False
        
        # 表格相关内容
        table_patterns = [
            r'^(表|表格)\s*\d*[：:].*$',
            r'^表\s*\d+[-.]?\d*\s+[^：:].*$'
        ]
        for pattern in table_patterns:
            if re.match(pattern, line):
                return False
        
        # 排除三级及以上层级序号（如 1.1.1、1.2.3 等）
        if re.match(r'^\d+\.\d+\.\d+', line):
            return False
        
        # 识别章标题格式
        # 1. 中文数字序号格式：第一章...、第1章...或第 1 章...（以"第"字开头、"章"字结尾，支持中间有空格）
        if re.match(r'^第\s*[一二三四五六七八九十百千\d]+\s*章', line):
            return True
        
        # 2. 单层阿拉伯数字序号格式：1. ...（仅包含一位阿拉伯数字加英文句点）
        if re.match(r'^\d+\.\s+', line) and not re.search(r'\d+\.\d+', line):
            return True
        
        # 3. 如果是子章节，识别二级标题格式：1.1、1.2 等
        if is_subsection:
            # 二级标题格式：X.Y 或 X.Y 标题，X和Y都是数字
            if re.match(r'^\d+\.\d+(\s+.*)?$', line):
                # 确保不是三级或更深层级的标题
                if not re.search(r'\d+\.\d+\.\d+', line):
                    return True
        
        # 其他格式不再识别
        return False
    
    def _is_non_chapter_content(self, line):
        """快速判断是否为非章节内容（额外的过滤层）"""
        # 首先检查是否为章标题格式，如果是则直接返回False
        if self._is_true_chapter_title(line, 0, '', [], False):
            return False
        
        # 明显的列表项格式
        list_patterns = [
            r'^[1-9]\d*\s*[、.。，].*$',         # 数字+标点
            r'^[一二三四五六七八九十百千万]+[、.]\s*.*$', # 中文数字+标点
            r'^[①②③④⑤⑥⑦⑧⑨⑩].*$',               # 特殊编号
            r'^[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽].*$',             # 括号数字
        ]
        
        # 列表项格式
        for pattern in list_patterns:
            if re.match(pattern, line):
                return True
        
        # 包含等号、引号等特殊字符的行，可能是代码或配置
        if any(char in line for char in ['=', '"', "'", '{', '}', '[', ']']):
            return True
        
        # 以标点符号结尾的行，通常不是标题（但章标题可能以句号结尾，所以需要谨慎）
        if line.rstrip().endswith(('。', '，', '.', ',', '！', '？', '!', '?', '；', ';')) and not re.search(r'章[。.]$', line):
            return True
        
        return False
    
    def _optimize_chapter_boundaries(self, chapters, pages_data):
        """优化章节边界，识别章标题和二级标题"""
        if len(chapters) <= 1:
            return chapters
            
        # 首先识别章节类型（处理主章节和二级标题）
        for chapter in chapters:
            title = chapter['title'].strip()
            chapter['type'] = 'content'  # 默认类型
            chapter['number'] = None
            chapter['parent_number'] = None
            chapter['full_number'] = None
            
            # 严格的章标题识别规则
            
            # 1. 中文数字序号格式：第一章...、第1章...或第 1 章...（以"第"字开头、"章"字结尾，支持中间有空格）
            if re.match(r'^(第\s*[一二三四五六七八九十百千\d]+\s*章)', title):
                chapter['type'] = 'main'
                chapter['number'] = re.search(r'第\s*[一二三四五六七八九十百千\d]+\s*章', title).group(0)
                chapter['full_number'] = chapter['number']
            # 2. 单层阿拉伯数字序号格式：1. ...（仅包含一位阿拉伯数字加英文句点）
            elif re.match(r'^(\d+)\.\s+(.+)$', title) and not re.search(r'\d+\.\d+', title):
                chapter['type'] = 'main'
                chapter['number'] = re.match(r'^(\d+)\.\s+(.+)$', title).group(1)
                chapter['full_number'] = chapter['number']
                chapter['title'] = f"{chapter['full_number']}. {re.match(r'^(\d+)\.\s+(.+)$', title).group(2)}"
            # 3. 二级标题格式：1.1、1.2 等
            elif re.match(r'^(\d+)\.(\d+)(\s+.*)?$', title) and not re.search(r'\d+\.\d+\.\d+', title):
                chapter['type'] = 'subsection'
                match = re.match(r'^(\d+)\.(\d+)(\s+.*)?$', title)
                chapter['parent_number'] = match.group(1)
                chapter['number'] = match.group(2)
                chapter['full_number'] = f"{match.group(1)}.{match.group(2)}"
                # 确保格式统一
                content_part = match.group(3).strip() if match.group(3) else ''
                chapter['title'] = f"{chapter['full_number']} {content_part}"
        
        # 按起始页排序章节
        sorted_chapters = sorted(chapters, key=lambda x: x['start_page'])
        
        # 收集主章节和二级标题
        main_chapters = []
        subsections = []
        
        for chapter in sorted_chapters:
            # 获取章节的实际内容
            chapter_pages = pages_data[chapter['start_page']:chapter['end_page']+1]
            chapter_text = '\n'.join([page['text'] for page in chapter_pages])
            chapter['content'] = chapter_text  # 使用完整内容
            
            # 处理主章节
            if chapter['type'] == 'main':
                # 确保主章节标题格式统一为 "数字. 标题"
                title = chapter['title'].strip()
                match = re.match(r'^(\d+)\.\s+(.+)$', title)
                if not match and chapter.get('number') and chapter['number'].isdigit():
                    # 提取内容部分
                    content_part = re.sub(r'^第[一二三四五六七八九十百千]+章[：:\s]*', '', title)
                    content_part = re.sub(r'^Chapter\s+\d+\.?\s*', '', content_part, flags=re.IGNORECASE)
                    chapter['title'] = f"{chapter['number']}. {content_part}"
                
                # 添加到主章节列表
                main_chapters.append(chapter)
                # 为每个主章节添加子章节列表
                chapter['subsections'] = []
            
            # 处理二级标题
            elif chapter['type'] == 'subsection':
                subsections.append(chapter)
        
        # 将二级标题关联到对应的主章节
        for subsection in subsections:
            parent_number = subsection['parent_number']
            for chapter in main_chapters:
                if chapter.get('number') == parent_number:
                    chapter['subsections'].append(subsection)
                    break
        
        # 最后进行章节标题标准化
        return self._standardize_chapter_titles(main_chapters)
    
    def _calculate_chapter_importance(self, chapter):
        """计算章节的重要性分数"""
        importance = 0.5  # 基础分数
        
        # 基于标题的重要性（重点关注主章节标识）
        title = chapter['title']
        
        # 检查是否为二级标题
        if re.match(r'^\d+\.\d+\s+', title):
            importance += 0.15  # 二级标题权重
        else:
            # 更新正则表达式，支持中文数字、阿拉伯数字和带空格的格式
            if re.match(r'^(第\s*[一二三四五六七八九十百千\d]+\s*章.*)$', title):
                importance += 0.3
            elif re.match(r'^(Chapter\s+\d+\.?\s+.*)$', title, re.IGNORECASE):
                importance += 0.3
            elif re.match(r'^\d+\.\s+', title):
                # 对一级数字编号给予较高权重
                importance += 0.2
        
        # 基于内容长度的重要性
        content_len = len(chapter['content'])
        if content_len > 2000:
            importance += 0.2
        elif content_len > 500:
            importance += 0.1
        
        # 标准化到0-1范围
        return min(1.0, importance)
    
    def _standardize_chapter_titles(self, chapters):
        """标准化章节标题格式，处理章标题和二级标题"""
        # 首先确定实际的章节编号，不使用计数方式
        # 而是根据内容中提取的编号进行标准化
        main_chapter_numbers = []
        
        # 收集所有主章节的编号
        for chapter in chapters:
            if chapter.get('number'):
                if chapter['number'].isdigit():
                    main_chapter_numbers.append(int(chapter['number']))
        
        # 排序编号
        main_chapter_numbers.sort()
        
        # 构建编号映射
        number_map = {}
        for i, num in enumerate(main_chapter_numbers, 1):
            number_map[num] = i
        
        # 标准化每个章节
        for chapter in chapters:
            title = chapter['title'].strip()
            
            # 主章节处理 - 格式：1. 标题
            # 使用数字编号格式 "1. 标题" 作为标准
            if re.match(r'^\d+\.\s+.+$', title):
                # 已经是标准格式，确保格式一致
                match = re.match(r'^(\d+)\.\s+(.+)$', title)
                chapter_num = int(match.group(1))
                # 使用原始编号或映射的编号
                final_num = number_map.get(chapter_num, chapter_num)
                chapter['title'] = f"{final_num}. {match.group(2)}"
            else:
                # 不是标准格式，提取内容并添加标准编号
                content_part = title
                # 移除可能的章节标识
                content_part = re.sub(r'^第[一二三四五六七八九十百千]+章[：:\s]*', '', content_part)
                content_part = re.sub(r'^Chapter\s+\d+\.?\s*', '', content_part, flags=re.IGNORECASE)
                
                # 分配标准编号
                if chapter.get('number') and chapter['number'].isdigit():
                    chapter_num = int(chapter['number'])
                    final_num = number_map.get(chapter_num, len(number_map) + 1)
                    chapter['title'] = f"{final_num}. {content_part}"
                else:
                    # 如果没有编号，按顺序分配
                    chapter['title'] = f"{len(number_map) + 1}. {content_part}"
                    number_map[len(number_map) + 1] = len(number_map) + 1
            
            # 更新编号信息
            match = re.match(r'^(\d+)\.', chapter['title'])
            if match:
                chapter['number'] = match.group(1)
                chapter['full_number'] = match.group(1)
            
            # 清理标题中的多余空格
            chapter['title'] = re.sub(r'\s+', ' ', chapter['title']).strip()
            
            # 标准化子章节（二级标题）
            if 'subsections' in chapter and chapter['subsections']:
                # 为每个主章节创建子章节编号映射
                subsection_map = {}
                subsection_numbers = []
                
                # 收集子章节编号
                for sub in chapter['subsections']:
                    if sub.get('number') and sub['number'].isdigit():
                        subsection_numbers.append(int(sub['number']))
                
                # 排序子章节编号
                subsection_numbers.sort()
                
                # 构建子章节编号映射
                for i, num in enumerate(subsection_numbers, 1):
                    subsection_map[num] = i
                
                # 标准化每个子章节
                for sub in chapter['subsections']:
                    sub_title = sub['title'].strip()
                    
                    # 确保二级标题格式为 "X.Y 标题"
                    match = re.match(r'^(\d+)\.(\d+)(\s+.*)?$', sub_title)
                    if match:
                        # 获取标准化后的父编号
                        parent_num = chapter['number']
                        # 获取子编号
                        sub_num = int(match.group(2))
                        # 使用映射的编号
                        final_sub_num = subsection_map.get(sub_num, sub_num)
                        # 获取标题内容
                        content_part = match.group(3).strip() if match.group(3) else ''
                        # 更新标题和编号信息
                        sub['title'] = f"{parent_num}.{final_sub_num} {content_part}"
                        sub['full_number'] = f"{parent_num}.{final_sub_num}"
                        sub['number'] = str(final_sub_num)
                        sub['parent_number'] = parent_num
                    
                    # 清理标题中的多余空格
                    sub['title'] = re.sub(r'\s+', ' ', sub['title']).strip()
                
                # 按子章节编号排序
                chapter['subsections'].sort(key=lambda x: int(x['number']) if x.get('number') and x['number'].isdigit() else 0)
        
        # 最终按主章节编号排序
        chapters.sort(key=lambda x: int(x['number']) if x.get('number') and x['number'].isdigit() else 0)
        
        return chapters
    
    def _fallback_chapter_splitting(self, pages_data):
        """基于内容密度的回退章节分割"""
        chapters = []
        total_pages = len(pages_data)
        # 计算理想的章节数量（每章8-15页）
        ideal_chapters = max(1, min(10, total_pages // 10))
        chunk_size = max(1, total_pages // ideal_chapters)
        
        for i in range(0, total_pages, chunk_size):
            end = min(i + chunk_size, total_pages)
            chapter_pages = pages_data[i:end]
            chapter_content = '\n'.join([page['text'] for page in chapter_pages])
            
            # 尝试提取标题
            title = f'第{len(chapters)+1}章'
            if chapter_content.strip():
                first_line = chapter_content.strip().splitlines()[0].strip()
                if len(first_line) > 0:
                    title = first_line[:80]  # 限制标题长度
            
            chapters.append({
                'start_page': i,
                'end_page': end - 1,
                'content': chapter_content,
                'title': title
            })
        
        return chapters
    
    def _detect_programming_language(self, content, title):
        """使用高级PDF处理器检测编程代码的语言"""
        try:
            # 使用高级处理器进行语言检测，结合内容和标题
            return self.advanced_processor.detect_programming_language(content, title)
        except Exception as e:
            print(f"高级代码语言检测错误: {str(e)}")
            # 发生错误时使用回退方法
            try:
                # 基于关键词和代码模式检测语言
                js_patterns = [r'function\s+\w+', r'console\.log', r'\{[^}]*\}', r'const\s+', r'let\s+', r'var\s+', r'require\(', r'import\s+.*from']
                python_patterns = [r'def\s+\w+\s*\(', r'print\(', r'import\s+\w+', r'from\s+\w+\s+import', r'class\s+\w+', r':\s*$', r'\bself\b']
                
                text = (content + ' ' + title).lower()
                js_score = sum(1 for pattern in js_patterns if re.search(pattern, text))
                python_score = sum(1 for pattern in python_patterns if re.search(pattern, text))
                
                # 检查文件名或标题中的线索
                if any(kw in text for kw in ['javascript', 'js', '前端', 'web']):
                    js_score += 3
                if any(kw in text for kw in ['python', '爬虫', '数据分析', 'ai', '机器学习']):
                    python_score += 3
                
                if js_score > python_score:
                    return 'javascript'
                else:
                    return 'python'
            except Exception:
                return 'python'
    
    def _enhanced_content_processing(self, content):
        """使用高级PDF处理器进行增强内容处理"""
        try:
            # 使用高级处理器进行内容处理
            return self.advanced_processor.enhanced_content_processing(content)
        except Exception as e:
            print(f"高级内容处理错误: {str(e)}")
            # 发生错误时使用回退方法
            try:
                # 分离内容为不同类型的块
                blocks = []
                lines = content.splitlines()
                current_block = []
                current_type = 'text'
                
                for line in lines:
                    line_type = self._classify_content_type(line)
                    
                    # 如果类型变化，保存当前块并开始新块
                    if line_type != current_type and current_block:
                        blocks.append({
                            'type': current_type,
                            'content': '\n'.join(current_block)
                        })
                        current_block = [line]
                        current_type = line_type
                    else:
                        current_block.append(line)
                
                # 添加最后一个块
                if current_block:
                    blocks.append({
                        'type': current_type,
                        'content': '\n'.join(current_block)
                    })
                
                # 重新组装内容，添加类型标记
                enhanced_content = []
                for block in blocks:
                    if block['type'] == 'code':
                        enhanced_content.append(f"```python\n{block['content']}\n```")
                    elif block['type'] == 'table':
                        enhanced_content.append(f"[TABLE]\n{block['content']}\n[/TABLE]")
                    elif block['type'] == 'title':
                        enhanced_content.append(f"# {block['content']}")
                    else:
                        enhanced_content.append(block['content'])
                
                return '\n\n'.join(enhanced_content)
            except Exception:
                return content
    
    @action(detail=False, methods=['post'], url_path='import-pdf', permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    def import_pdf(self, request):
        """上传PDF并使用计算机视觉技术解析为教材与章节"""
        # 详细日志记录请求参数
        print("=== PDF导入请求开始 ===")
        print(f"用户: {request.user.username}")
        print(f"请求数据: {list(request.data.keys())}")
        print(f"文件字段: {list(request.FILES.keys())}")
        
        # 获取并验证参数
        title = (request.data.get('title') or '').strip()
        author = (request.data.get('author') or '').strip() or '未知作者'
        file_obj = request.FILES.get('file') or request.FILES.get('pdf')
        
        print(f"验证参数:")
        print(f"- title: {'存在' if title else '不存在'}")
        print(f"- author: {author}")
        print(f"- file_obj: {'存在' if file_obj else '不存在'}")
        
        if not file_obj:
            print("错误: 缺少PDF文件")
            return Response({'error': '缺少PDF文件(file)'}, status=status.HTTP_400_BAD_REQUEST)
        if not title:
            print("错误: 缺少教材标题")
            return Response({'error': '缺少教材标题(title)'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建书籍并保存PDF
        book = Book.objects.create(title=title, author=author, description=request.data.get('description') or '', owner=request.user)
        book.pdf_file = file_obj
        book.save()
        
        # 创建临时文件用于处理
        temp_pdf = None
        try:
            # 创建临时PDF文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                for chunk in book.pdf_file.chunks():
                    temp_pdf.write(chunk)
                temp_pdf_path = temp_pdf.name
            
            # 将PDF转换为图像
            images = self._extract_pdf_to_images(temp_pdf_path)
            
            # 使用高级PDF处理器处理PDF
            try:
                print("使用增强的高级PDF处理器进行全功能分析...")
                # 让高级处理器处理PDF提取和分析（包含并行处理、引用检测、文档结构重建等）
                processed_result = self.advanced_processor.process_pdf(temp_pdf_path, images)
                pages_data = processed_result.get('pages_data', [])
                document_structure = processed_result.get('document_structure', None)
                
                # 将文档结构保存到实例属性，供_advanced_chapter_detection方法使用
                self._document_structure = document_structure
                
                # 记录处理结果统计信息
                if 'metadata' in processed_result:
                    print(f"高级处理统计: 页码数={processed_result['metadata'].get('total_pages', 0)}, "
                          f"处理时间={processed_result['metadata'].get('processing_time', 0):.2f}秒, "
                          f"方法={processed_result['metadata'].get('processing_method', 'unknown')}")
                
                if document_structure:
                    # 记录文档结构分析结果
                    print(f"文档结构分析: 估计章节数={document_structure.get('estimated_chapters', 0)}, "
                          f"引用分析={bool(document_structure.get('citation_graph'))}, "
                          f"目录对齐={bool(document_structure.get('toc_alignments'))}")
                
                # 如果高级处理失败，回退到基本方法
                if not pages_data:
                    if not images:
                        # 如果无法转换为图像，回退到基本的PyPDF2文本提取
                        from PyPDF2 import PdfReader
                        reader = PdfReader(book.pdf_file)
                        pages_data = []
                        for page in reader.pages:
                            try:
                                text = page.extract_text() or ''
                                pages_data.append({'text': text, 'regions': []})
                            except Exception:
                                pages_data.append({'text': '', 'regions': []})
                    else:
                        # 使用OCR和布局分析处理每一页
                        pages_data = []
                        for image in images:
                            # 提取文本
                            text = self._extract_text_with_ocr(image)
                            # 检测内容区域
                            regions = self._detect_content_regions(image)
                            pages_data.append({'text': text, 'regions': regions})
            except Exception as e:
                print(f"高级PDF处理错误: {str(e)}")
                # 完全回退到原始方法
                if not images:
                    # 如果无法转换为图像，回退到基本的PyPDF2文本提取
                    from PyPDF2 import PdfReader
                    reader = PdfReader(book.pdf_file)
                    pages_data = []
                    for page in reader.pages:
                        try:
                            text = page.extract_text() or ''
                            pages_data.append({'text': text, 'regions': []})
                        except Exception:
                            pages_data.append({'text': '', 'regions': []})
                else:
                    # 使用OCR和布局分析处理每一页
                    pages_data = []
                    for image in images:
                        # 提取文本
                        text = self._extract_text_with_ocr(image)
                        # 检测内容区域
                        regions = self._detect_content_regions(image)
                        pages_data.append({'text': text, 'regions': regions})
            
            # 高级章节检测（已集成高级处理器）
            chapters = self._advanced_chapter_detection(pages_data, images)
            
            # 检测编程语言（已集成高级处理器）
            combined_content = '\n'.join([page['text'] for page in pages_data])
            language = self._detect_programming_language(combined_content, title)
            
            # 创建章节
            created_count = 0
            chapter_order = 1
            
            # 定义二级标题格式的正则表达式
            subsection_pattern = re.compile(r'^\d+\.\d+')
            # 定义三级及以上标题格式的正则表达式（需要排除）
            deeper_level_pattern = re.compile(r'^\d+\.\d+\.\d+')
            
            for main_chapter in chapters:
                # 增强内容处理
                enhanced_content = self._enhanced_content_processing(main_chapter['content'])
                
                # 生成适当的代码示例
                if language == 'javascript':
                    code_example = f"// {main_chapter['title'][:30]}\nconsole.log('学习{main_chapter['title']}');\n// 在此处添加您的代码"
                else:
                    code_example = f"# {main_chapter['title'][:30]}\nprint('学习{main_chapter['title']}')\n# 在此处添加您的代码"
                
                # 创建主章节
                created_main_chapter = Chapter.objects.create(
                    book=book,
                    title=main_chapter['title'][:100],  # 限制标题长度
                    type='reading',
                    duration=30 + len(main_chapter['content']) // 1000,  # 基于内容长度估计时长
                    description=f'由PDF自动生成，包含第{main_chapter['start_page']+1}-{main_chapter['end_page']+1}页内容',
                    content=enhanced_content,
                    code=code_example,
                    language=language,
                    order=chapter_order,
                    level=1,  # 明确设置为主章节级别
                    is_main_chapter=True
                )
                created_count += 1
                chapter_order += 1
                
                # 如果有子章节，创建子章节记录
                if 'subsections' in main_chapter and main_chapter['subsections']:
                    for subsection in main_chapter['subsections']:
                        # 检查是否为二级标题（格式为1.1、1.2等）且不是三级及以上标题
                        title = subsection.get('title', '').strip()
                        is_valid_subsection = subsection_pattern.match(title) and not deeper_level_pattern.match(title)
                        
                        if is_valid_subsection:
                            # 增强子章节内容处理
                            subsection_enhanced_content = self._enhanced_content_processing(subsection.get('content', ''))
                            
                            # 生成子章节代码示例
                            if language == 'javascript':
                                subsection_code_example = f"// {subsection['title'][:30]}\nconsole.log('学习{subsection['title']}');\n// 在此处添加您的代码"
                            else:
                                subsection_code_example = f"# {subsection['title'][:30]}\nprint('学习{subsection['title']}')\n# 在此处添加您的代码"
                            
                            # 创建子章节，关联到主章节
                            Chapter.objects.create(
                                book=book,
                                title=title[:100],  # 限制标题长度
                                type='reading',
                                duration=20 + len(subsection.get('content', '')) // 1000,  # 基于内容长度估计时长
                                description=f'由PDF自动生成的二级标题',
                                content=subsection_enhanced_content,
                                code=subsection_code_example,
                                language=language,
                                order=chapter_order,
                                level=2,  # 明确设置为二级章节级别
                                is_main_chapter=False,
                                parent_chapter=created_main_chapter  # 关联到主章节
                            )
                            created_count += 1
                            chapter_order += 1
                            print(f"已创建二级标题: {title}")
                        else:
                            print(f"跳过不符合二级标题格式的子章节: {title}")
            
            # 刷新章节数
            book.save()
            
            # 异步处理图像和图表提取（后续可以实现）
            # threading.Thread(target=self._extract_images_and_charts, args=(book.id, temp_pdf_path)).start()
            
            return Response({
                'success': True, 
                'book_id': book.id, 
                'chapters': created_count,
                'language': language,
                'message': 'PDF解析成功，已创建章节并进行内容类型识别'
            })
            
        except Exception as e:
            # 详细记录异常
            import traceback
            print(f"=== PDF处理异常 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误消息: {str(e)}")
            print(f"堆栈跟踪:")
            traceback.print_exc()
            
            # 清理
            if temp_pdf and hasattr(temp_pdf, 'name') and os.path.exists(temp_pdf.name):
                try:
                    os.unlink(temp_pdf.name)
                    print("临时文件已清理")
                except:
                    print("清理临时文件失败")
            
            return Response({'error': f'PDF处理失败: {str(e)}', 'error_type': type(e).__name__}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            # 确保临时文件被删除
            if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
                try:
                    os.unlink(temp_pdf_path)
                    print(f"临时文件 {temp_pdf_path} 已删除")
                except Exception as e:
                    print(f"删除临时文件失败: {str(e)}")
            print("=== PDF导入请求结束 ===")
    
    def retrieve(self, request, *args, **kwargs):
        """获取书籍详情，包含所有章节"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    """章节视图集"""
    queryset = Chapter.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChapterDetailSerializer
        return ChapterSerializer
    
    @action(detail=False, methods=['get'], url_path='book/(?P<book_id>[^/.]+)')
    def by_book(self, request, book_id=None):
        """获取指定书籍的所有章节"""
        try:
            chapters = Chapter.objects.filter(book_id=book_id).order_by('order')
            serializer = self.get_serializer(chapters, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """获取章节详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # 如果用户已登录，可以记录学习行为
        if request.user.is_authenticated:
            # 这里应该调用learning应用的API来记录学习行为
            pass
        
        return Response(serializer.data)