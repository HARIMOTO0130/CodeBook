import re
import numpy as np
from typing import List, Dict, Tuple, Optional
import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer, AutoModel, AutoTokenizer
import cv2
from PIL import Image
import io
import base64
from sklearn.svm import SVC
from sklearn.cluster import AgglomerativeClustering
import math
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AdvancedPDFProcessor:
    """高级PDF处理类，集成NLP和计算机视觉技术"""
    
    def __init__(self):
        """初始化高级处理器，加载必要的模型"""
        self._initialize_models()
        
    def _initialize_models(self):
        """初始化NLP和计算机视觉模型"""
        try:
            # 加载BERT模型用于文本特征提取
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
            self.bert_model = BertModel.from_pretrained('bert-base-chinese')
            
            # 初始化分类器
            self.content_classifier = SVC(kernel='rbf', probability=True)
            self.chapter_boundary_model = self._create_bilstm_crf_model()
            
            # 预训练布局分析模型（模拟）
            self.layout_analyzer = self._create_layout_analyzer()
            
            logger.info("高级处理模型初始化成功")
        except Exception as e:
            logger.error(f"模型初始化失败: {str(e)}")
            # 使用轻量级备选方案
            self.using_fallback = True
            logger.info("使用轻量级备选方案")
    
    def _create_bilstm_crf_model(self):
        """创建BiLSTM-CRF模型用于章节边界检测"""
        # 这里简化实现，实际项目中应该使用完整的BiLSTM-CRF模型
        class BiLSTMCRF(nn.Module):
            def __init__(self, input_dim=768, hidden_dim=256, num_tags=2):
                super().__init__()
                self.lstm = nn.LSTM(input_dim, hidden_dim, bidirectional=True, batch_first=True)
                self.hidden2tag = nn.Linear(hidden_dim * 2, num_tags)
                self.transitions = nn.Parameter(torch.randn(num_tags, num_tags))
            
            def forward(self, x):
                # 简化实现，返回预测的标签概率
                lstm_out, _ = self.lstm(x)
                tag_scores = self.hidden2tag(lstm_out)
                return torch.softmax(tag_scores, dim=2)
        
        return BiLSTMCRF()
    
    def _create_layout_analyzer(self):
        """创建布局分析器"""
        # 这里使用简化的布局分析器，实际项目中可以集成Faster R-CNN或YOLO
        class LayoutAnalyzer:
            def analyze(self, image):
                # 简化的布局分析，检测文本块、代码块、图表区域
                regions = []
                # 实际项目中应该使用计算机视觉技术检测区域
                return regions
        
        return LayoutAnalyzer()
    
    def extract_text_features(self, text: str) -> np.ndarray:
        """使用BERT提取文本特征
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        try:
            inputs = self.bert_tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            # 使用[CLS]标记的输出作为文本表示
            return outputs.last_hidden_state[:, 0, :].numpy()[0]
        except Exception:
            # 回退到简单的TF-IDF类特征
            return self._fallback_feature_extraction(text)
    
    def _fallback_feature_extraction(self, text: str) -> np.ndarray:
        """回退的特征提取方法"""
        # 基于规则的简单特征
        features = []
        # 文本长度特征
        features.append(len(text))
        # 大写字母比例
        features.append(sum(1 for c in text if c.isupper()) / max(1, len(text)))
        # 数字比例
        features.append(sum(1 for c in text if c.isdigit()) / max(1, len(text)))
        # 特殊字符比例
        special_chars = '{}[]()=;:,./\|!@#$%^&*'
        features.append(sum(1 for c in text if c in special_chars) / max(1, len(text)))
        # 章节关键词特征
        chapter_keywords = ['章', '节', 'Chapter', 'SECTION']
        features.append(sum(1 for keyword in chapter_keywords if keyword in text))
        
        return np.array(features)
    
    def classify_content_type(self, text: str, features: Optional[np.ndarray] = None) -> Dict[str, float]:
        """使用NLP技术分类内容类型
        
        Args:
            text: 输入文本
            features: 预计算的特征向量（可选）
            
        Returns:
            各内容类型的概率分布
        """
        if features is None:
            features = self.extract_text_features(text)
        
        try:
            # 这里简化实现，实际应该使用训练好的分类器
            # 计算内容类型概率
            probabilities = {
                'title': 0.0,
                'paragraph': 0.0,
                'code': 0.0,
                'table': 0.0,
                'figure': 0.0,
                'list': 0.0
            }
            
            # 基于文本特征计算概率
            if len(text) < 100 and any(keyword in text for keyword in ['章', '节', 'Chapter', 'SECTION']):
                probabilities['title'] = 0.8
            elif re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*.*$', text) or 'function' in text or 'def ' in text:
                probabilities['code'] = 0.7
            elif re.search(r'^\s*[1-9]\d*[、.)]|^\s*[一二三四五六七八九十][、.]', text):
                probabilities['list'] = 0.6
            elif '|' in text and any(ch.isdigit() for ch in text):
                probabilities['table'] = 0.5
            else:
                probabilities['paragraph'] = 0.7
            
            # 归一化概率
            total = sum(probabilities.values())
            if total > 0:
                for key in probabilities:
                    probabilities[key] /= total
            
            return probabilities
        except Exception as e:
            logger.error(f"内容分类失败: {str(e)}")
            return {'paragraph': 1.0}
    
    def detect_chapter_boundaries(self, text_blocks: List[str], positions: List[Tuple[int, int]]) -> List[int]:
        """使用序列标注模型检测章节边界
        
        Args:
            text_blocks: 文本块列表
            positions: 每个块的位置信息
            
        Returns:
            章节边界的索引列表
        """
        try:
            boundaries = []
            
            # 提取每个块的特征
            features = []
            for block, (page_idx, line_idx) in zip(text_blocks, positions):
                block_features = self.extract_text_features(block)
                # 添加位置特征
                position_features = np.array([page_idx, line_idx, line_idx / 100])
                combined_features = np.concatenate([block_features[:5], position_features])
                features.append(combined_features)
            
            # 转换为PyTorch张量并进行预测
            features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
            
            # 使用BiLSTM-CRF模型预测
            with torch.no_grad():
                predictions = self.chapter_boundary_model(features_tensor)
            
            # 提取边界位置
            for i, pred in enumerate(predictions[0]):
                if pred[1] > 0.5:  # 假设索引1表示章节边界
                    boundaries.append(i)
            
            # 补充规则检测
            for i, block in enumerate(text_blocks):
                if re.match(r'^第[一二三四五六七八九十百千]+章[：:].+$|^第\d+章[：:].+$|^Chapter\s+\d+', block):
                    if i not in boundaries:
                        boundaries.append(i)
            
            return sorted(boundaries)
        except Exception as e:
            logger.error(f"章节边界检测失败: {str(e)}")
            # 回退到规则方法
            return self._fallback_chapter_boundaries(text_blocks)
    
    def _fallback_chapter_boundaries(self, text_blocks: List[str]) -> List[int]:
        """回退的章节边界检测方法"""
        boundaries = []
        chapter_patterns = [
            r'^第[一二三四五六七八九十百千]+章[：:].+$',
            r'^第\d+章[：:].+$',
            r'^Chapter\s+\d+',
            r'^SECTION\s+[A-Z]',
            r'^\d+\.\s+[A-Z]',
        ]
        
        for i, block in enumerate(text_blocks):
            for pattern in chapter_patterns:
                if re.match(pattern, block.strip()):
                    boundaries.append(i)
                    break
        
        return boundaries
    
    def analyze_document_layout(self, image: np.ndarray) -> List[Dict]:
        """使用计算机视觉技术分析文档布局
        
        Args:
            image: 页面图像
            
        Returns:
            内容区域列表，每个区域包含类型、坐标和特征
        """
        try:
            # 使用布局分析器分析图像
            regions = self.layout_analyzer.analyze(image)
            
            # 如果没有检测到区域，使用OCR后处理
            if not regions:
                regions = self._post_process_ocr_layout(image)
            
            return regions
        except Exception as e:
            logger.error(f"布局分析失败: {str(e)}")
            return []
    
    def _post_process_ocr_layout(self, image: np.ndarray) -> List[Dict]:
        """基于OCR结果的布局后处理"""
        # 简化实现，实际应该使用OCR结果进行布局分析
        regions = []
        
        # 模拟检测页面顶部的标题区域
        height, width = image.shape[:2]
        title_region = {
            'type': 'title',
            'coordinates': [0, 0, width, height // 4],
            'confidence': 0.7
        }
        regions.append(title_region)
        
        # 模拟检测正文区域
        content_region = {
            'type': 'content',
            'coordinates': [0, height // 4, width, height * 3 // 4],
            'confidence': 0.8
        }
        regions.append(content_region)
        
        return regions
    
    def detect_code_blocks(self, text: str) -> List[Tuple[int, int]]:
        """使用语言模型和熵分析检测代码块
        
        Args:
            text: 输入文本
            
        Returns:
            代码块的起始和结束行索引列表
        """
        try:
            code_blocks = []
            lines = text.splitlines()
            in_code_block = False
            start_line = -1
            
            # 计算每行的熵值（简化版）
            entropies = []
            for line in lines:
                entropy = self._calculate_text_entropy(line)
                entropies.append(entropy)
            
            # 检测代码块
            for i, (line, entropy) in enumerate(zip(lines, entropies)):
                # 代码行通常有特定的语法特征
                is_code_line = (
                    # 低熵值
                    entropy < 3.5 and 
                    # 包含代码特征
                    (re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=', line) or 
                     'function' in line or 
                     'def ' in line or 
                     'class ' in line or 
                     'import ' in line or 
                     re.search(r'^\s*[{}[\];:]', line))
                )
                
                if is_code_line and not in_code_block:
                    start_line = i
                    in_code_block = True
                elif not is_code_line and in_code_block:
                    code_blocks.append((start_line, i-1))
                    in_code_block = False
            
            # 处理最后一个代码块
            if in_code_block:
                code_blocks.append((start_line, len(lines)-1))
            
            return code_blocks
        except Exception as e:
            logger.error(f"代码块检测失败: {str(e)}")
            return []
    
    def _calculate_text_entropy(self, text: str) -> float:
        """计算文本的熵值"""
        if not text:
            return 0.0
        
        # 计算字符频率
        freq_dict = defaultdict(int)
        for char in text:
            freq_dict[char] += 1
        
        # 计算熵
        entropy = 0.0
        total_chars = len(text)
        for count in freq_dict.values():
            p = count / total_chars
            entropy -= p * math.log2(p)
        
        return entropy
    
    def extract_chapter_hierarchy(self, chapters: List[Dict]) -> List[Dict]:
        """使用层次聚类构建章节层次结构
        
        Args:
            chapters: 检测到的章节列表
            
        Returns:
            带有层次关系的章节列表
        """
        try:
            if len(chapters) <= 1:
                return chapters
            
            # 提取章节特征
            features = []
            for chapter in chapters:
                # 提取标题和内容特征
                title_features = self.extract_text_features(chapter['title'])
                features.append(title_features[:10])  # 简化特征
            
            # 执行层次聚类
            clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.5)
            cluster_labels = clustering.fit_predict(features)
            
            # 构建层次结构
            chapter_hierarchy = []
            parent_chapters = []
            
            for i, (chapter, label) in enumerate(zip(chapters, cluster_labels)):
                # 基于章节编号和聚类结果确定层次
                if re.match(r'^第\d+章', chapter['title']) or label not in [c['cluster'] for c in parent_chapters]:
                    # 主章节
                    chapter['level'] = 1
                    chapter['cluster'] = label
                    chapter_hierarchy.append(chapter)
                    parent_chapters.append(chapter)
                else:
                    # 子章节
                    chapter['level'] = 2
                    # 找到最近的父章节
                    for parent in reversed(parent_chapters):
                        if parent['cluster'] == label:
                            if 'children' not in parent:
                                parent['children'] = []
                            parent['children'].append(chapter)
                            break
                    chapter_hierarchy.append(chapter)
            
            return chapter_hierarchy
        except Exception as e:
            logger.error(f"章节层次结构构建失败: {str(e)}")
            return chapters
    
    def identify_formulas(self, image: np.ndarray) -> List[Dict]:
        """识别数学公式
        
        Args:
            image: 页面图像
            
        Returns:
            公式区域列表
        """
        try:
            formulas = []
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用边缘检测和形态学操作检测公式
            edges = cv2.Canny(gray, 50, 150)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(edges, kernel, iterations=1)
            
            # 查找轮廓
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 计算轮廓边界
                x, y, w, h = cv2.boundingRect(contour)
                
                # 筛选可能是公式的区域
                if h > 20 and h < 200 and w > 10 and w < 500:
                    # 计算区域特征
                    aspect_ratio = w / float(h)
                    if 0.5 < aspect_ratio < 10:  # 合理的宽高比
                        formulas.append({
                            'coordinates': [x, y, x + w, y + h],
                            'confidence': 0.6  # 简化的置信度
                        })
            
            return formulas
        except Exception as e:
            logger.error(f"公式识别失败: {str(e)}")
            return []
    
    def integrate_visual_text_features(self, text: str, image: np.ndarray) -> np.ndarray:
        """融合视觉和文本特征
        
        Args:
            text: 文本内容
            image: 页面图像
            
        Returns:
            融合后的特征向量
        """
        try:
            # 提取文本特征
            text_features = self.extract_text_features(text)
            
            # 提取视觉特征（简化版）
            # 计算图像的基本统计特征
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            visual_features = np.array([
                np.mean(gray),
                np.std(gray),
                np.max(gray),
                np.min(gray),
                np.sum(gray > 200) / gray.size,  # 高亮像素比例
                np.sum(gray < 50) / gray.size    # 暗像素比例
            ])
            
            # 融合特征
            # 这里使用简单的拼接，实际应该使用注意力机制
            combined_features = np.concatenate([text_features[:10], visual_features])
            
            return combined_features
        except Exception as e:
            logger.error(f"特征融合失败: {str(e)}")
            return self.extract_text_features(text)
    
    def align_toc_with_content(self, toc_items: List[Dict], content_chapters: List[Dict]) -> List[Dict]:
        """使用序列比对算法对齐目录和正文
        
        Args:
            toc_items: 目录项列表
            content_chapters: 正文章节列表
            
        Returns:
            对齐后的章节列表
        """
        try:
            aligned_chapters = []
            
            # 为每个目录项找到最匹配的正文章节
            for toc in toc_items:
                best_match = None
                best_score = 0
                
                for content in content_chapters:
                    # 计算编辑距离相似度
                    similarity = self._calculate_title_similarity(toc['title'], content['title'])
                    
                    # 结合位置信息改进匹配
                    pos_factor = 1.0
                    if 'page' in toc and 'start_page' in content:
                        page_diff = abs(toc['page'] - content['start_page'])
                        pos_factor = max(0.1, 1.0 - page_diff * 0.05)
                    
                    total_score = similarity * pos_factor
                    
                    if total_score > best_score:
                        best_score = total_score
                        best_match = content
                
                if best_match and best_score > 0.3:
                    # 合并目录和正文信息
                    aligned_chapter = {
                        'title': best_match['title'],
                        'start_page': best_match['start_page'],
                        'end_page': best_match['end_page'],
                        'content': best_match['content'],
                        'toc_info': toc,
                        'alignment_score': best_score
                    }
                    aligned_chapters.append(aligned_chapter)
            
            return aligned_chapters
        except Exception as e:
            logger.error(f"目录正文对齐失败: {str(e)}")
            return content_chapters
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """计算标题相似度"""
        # 移除数字和特殊字符
        clean1 = re.sub(r'\d+|[\s\p{P}]+', '', title1)
        clean2 = re.sub(r'\d+|[\s\p{P}]+', '', title2)
        
        # 计算最长公共子序列
        lcs_length = self._longest_common_subsequence(clean1, clean2)
        
        # 计算相似度
        if not clean1 or not clean2:
            return 0.0
        
        similarity = lcs_length / max(len(clean1), len(clean2))
        return similarity
    
    def _longest_common_subsequence(self, s1: str, s2: str) -> int:
        """计算最长公共子序列长度"""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def enhance_chapter_detection(self, pages_data: List[Dict], images: List[np.ndarray] = None) -> List[Dict]:
        """增强的章节检测，集成NLP和计算机视觉技术
        
        Args:
            pages_data: 页面数据列表
            images: 页面图像列表（可选）
            
        Returns:
            检测到的章节列表
        """
        try:
            # 收集所有文本块和位置信息
            text_blocks = []
            positions = []
            
            for page_idx, page in enumerate(pages_data):
                lines = page['text'].splitlines()
                for line_idx, line in enumerate(lines):
                    if line.strip():
                        text_blocks.append(line.strip())
                        positions.append((page_idx, line_idx))
            
            # 检测章节边界
            boundaries = self.detect_chapter_boundaries(text_blocks, positions)
            
            # 构建章节
            chapters = []
            start_idx = 0
            
            for boundary_idx in sorted(boundaries + [len(text_blocks)]):
                if boundary_idx > start_idx:
                    # 提取章节内容
                    chapter_blocks = text_blocks[start_idx:boundary_idx]
                    chapter_text = '\n'.join(chapter_blocks)
                    
                    # 获取章节标题（第一个非空行）
                    title = next((block for block in chapter_blocks if block.strip()), f'章节{len(chapters)+1}')
                    
                    # 获取起始和结束页码
                    start_page = positions[start_idx][0]
                    end_page = positions[boundary_idx-1][0] if boundary_idx-1 < len(positions) else start_page
                    
                    # 分类章节类型
                    content_type = self.classify_content_type(chapter_text)
                    chapter_type = max(content_type.items(), key=lambda x: x[1])[0]
                    
                    chapter = {
                        'title': title[:100],
                        'start_page': start_page,
                        'end_page': end_page,
                        'content': chapter_text,
                        'type': chapter_type,
                        'content_scores': content_type
                    }
                    
                    chapters.append(chapter)
                    start_idx = boundary_idx
            
            # 构建章节层次结构
            enhanced_chapters = self.extract_chapter_hierarchy(chapters)
            
            return enhanced_chapters
        except Exception as e:
            logger.error(f"增强章节检测失败: {str(e)}")
            # 回退到简单方法
            return self._fallback_chapter_detection(pages_data)
    
    def _fallback_chapter_detection(self, pages_data: List[Dict]) -> List[Dict]:
        """回退的章节检测方法"""
        chapters = []
        current_chapter = None
        
        chapter_pattern = re.compile(r'^第[一二三四五六七八九十百千]+章[：:].+$|^第\d+章[：:].+$|^Chapter\s+\d+')
        
        for page_idx, page in enumerate(pages_data):
            lines = page['text'].splitlines()
            
            for line in lines:
                line = line.strip()
                
                # 检测章节标题
                if chapter_pattern.match(line):
                    # 保存当前章节
                    if current_chapter:
                        current_chapter['end_page'] = page_idx
                        chapters.append(current_chapter)
                    
                    # 开始新章节
                    current_chapter = {
                        'title': line,
                        'start_page': page_idx,
                        'end_page': page_idx,
                        'content': line + '\n',
                        'type': 'main'
                    }
                elif current_chapter:
                    # 添加内容到当前章节
                    current_chapter['content'] += line + '\n'
                    current_chapter['end_page'] = page_idx
        
        # 添加最后一个章节
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters