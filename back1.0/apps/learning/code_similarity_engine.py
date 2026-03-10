"""代码相似度检测引擎

该模块实现代码相似度检测功能，分析用户提交的代码与参考代码或其他用户代码的相似度，
帮助识别代码抄袭和重复，促进原创性编程。
"""

import json
import hashlib
import difflib
import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class CodeSimilarityEngine:
    """代码相似度检测引擎
    
    核心功能：
    1. 代码标准化处理
    2. 特征提取
    3. 相似度计算
    4. 结果分析
    """
    
    def __init__(self):
        """初始化代码相似度检测引擎"""
        pass
    
    def calculate_similarity(self, code1: str, code2: str, language: str = 'python') -> Dict[str, Any]:
        """计算两段代码的相似度
        
        Args:
            code1: 第一段代码
            code2: 第二段代码
            language: 代码语言
            
        Returns:
            包含相似度计算结果的字典
        """
        try:
            # 代码标准化
            normalized_code1 = self._normalize_code(code1, language)
            normalized_code2 = self._normalize_code(code2, language)
            
            # 提取特征
            features1 = self._extract_features(normalized_code1, language)
            features2 = self._extract_features(normalized_code2, language)
            
            # 计算多种相似度指标
            similarity_scores = {
                'token_similarity': self._calculate_token_similarity(normalized_code1, normalized_code2, language),
                'structure_similarity': self._calculate_structure_similarity(features1, features2),
                'ast_similarity': self._calculate_ast_similarity(code1, code2, language),
                'line_similarity': self._calculate_line_similarity(code1, code2)
            }
            
            # 综合相似度得分
            overall_similarity = self._calculate_overall_similarity(similarity_scores)
            
            # 分析相似代码片段
            similar_segments = self._identify_similar_segments(code1, code2)
            
            # 评估相似度级别
            similarity_level = self._evaluate_similarity_level(overall_similarity)
            
            return {
                'overall_similarity': overall_similarity,
                'similarity_scores': similarity_scores,
                'similarity_level': similarity_level,
                'similar_segments': similar_segments,
                'normalized_code1': normalized_code1,
                'normalized_code2': normalized_code2,
                'features1': features1,
                'features2': features2,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'计算相似度失败: {str(e)}',
                'overall_similarity': 0
            }
    
    def batch_compare(self, target_code: str, reference_codes: List[str], language: str = 'python') -> Dict[str, Any]:
        """批量比较代码相似度
        
        Args:
            target_code: 目标代码
            reference_codes: 参考代码列表
            language: 代码语言
            
        Returns:
            批量比较结果
        """
        try:
            results = []
            for i, reference_code in enumerate(reference_codes):
                similarity_result = self.calculate_similarity(target_code, reference_code, language)
                results.append({
                    'reference_index': i,
                    'similarity_result': similarity_result
                })
            
            # 按相似度排序
            results.sort(key=lambda x: x['similarity_result'].get('overall_similarity', 0), reverse=True)
            
            return {
                'batch_results': results,
                'total_references': len(reference_codes),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'批量比较失败: {str(e)}',
                'batch_results': []
            }
    
    def _normalize_code(self, code: str, language: str) -> str:
        """代码标准化处理
        
        Args:
            code: 原始代码
            language: 代码语言
            
        Returns:
            标准化后的代码
        """
        # 去除注释
        code = self._remove_comments(code, language)
        
        # 去除空白字符
        code = self._normalize_whitespace(code)
        
        # 标准化变量名（可选）
        # code = self._normalize_variable_names(code, language)
        
        return code
    
    def _remove_comments(self, code: str, language: str) -> str:
        """去除代码中的注释
        
        Args:
            code: 原始代码
            language: 代码语言
            
        Returns:
            去除注释后的代码
        """
        if language == 'python':
            # 去除Python注释
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        elif language == 'javascript':
            # 去除JavaScript注释
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        
        return code
    
    def _normalize_whitespace(self, code: str) -> str:
        """标准化空白字符
        
        Args:
            code: 原始代码
            
        Returns:
            标准化空白字符后的代码
        """
        # 替换多个空格为单个空格
        code = re.sub(r'\s+', ' ', code)
        # 去除行首行尾空白
        code = code.strip()
        return code
    
    def _extract_features(self, code: str, language: str) -> Dict[str, Any]:
        """提取代码特征
        
        Args:
            code: 标准化后的代码
            language: 代码语言
            
        Returns:
            代码特征
        """
        features = {
            'line_count': len(code.split('\n')),
            'token_count': len(code.split()),
            'function_count': self._count_functions(code, language),
            'class_count': self._count_classes(code, language),
            'imports': self._extract_imports(code, language),
            'keywords': self._extract_keywords(code, language)
        }
        
        return features
    
    def _count_functions(self, code: str, language: str) -> int:
        """统计函数数量
        
        Args:
            code: 代码
            language: 代码语言
            
        Returns:
            函数数量
        """
        if language == 'python':
            try:
                tree = ast.parse(code)
                return sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            except:
                return 0
        elif language == 'javascript':
            # 简单统计函数声明
            return len(re.findall(r'function\s+\w+\s*\(', code))
        return 0
    
    def _count_classes(self, code: str, language: str) -> int:
        """统计类数量
        
        Args:
            code: 代码
            language: 代码语言
            
        Returns:
            类数量
        """
        if language == 'python':
            try:
                tree = ast.parse(code)
                return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            except:
                return 0
        elif language == 'javascript':
            # 简单统计类声明
            return len(re.findall(r'class\s+\w+', code))
        return 0
    
    def _extract_imports(self, code: str, language: str) -> List[str]:
        """提取导入语句
        
        Args:
            code: 代码
            language: 代码语言
            
        Returns:
            导入语句列表
        """
        imports = []
        if language == 'python':
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(f'{node.module}.{node.names[0].name}')
            except:
                pass
        elif language == 'javascript':
            # 简单提取import语句
            matches = re.findall(r'import\s+.*?from\s+["\'](.*?)["\']', code)
            imports.extend(matches)
        return imports
    
    def _extract_keywords(self, code: str, language: str) -> Dict[str, int]:
        """提取关键字频率
        
        Args:
            code: 代码
            language: 代码语言
            
        Returns:
            关键字频率字典
        """
        keywords = {}
        if language == 'python':
            python_keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'import', 'from', 'return', 'print']
            for keyword in python_keywords:
                count = code.count(f' {keyword} ')
                if count > 0:
                    keywords[keyword] = count
        elif language == 'javascript':
            js_keywords = ['function', 'class', 'if', 'else', 'for', 'while', 'import', 'export', 'return', 'console.log']
            for keyword in js_keywords:
                count = code.count(keyword)
                if count > 0:
                    keywords[keyword] = count
        return keywords
    
    def _calculate_token_similarity(self, code1: str, code2: str, language: str) -> float:
        """计算token相似度
        
        Args:
            code1: 标准化后的代码1
            code2: 标准化后的代码2
            language: 代码语言
            
        Returns:
            token相似度（0-1）
        """
        tokens1 = code1.split()
        tokens2 = code2.split()
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # 使用difflib计算相似度
        seq_matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
        return seq_matcher.ratio()
    
    def _calculate_structure_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """计算结构相似度
        
        Args:
            features1: 代码1的特征
            features2: 代码2的特征
            
        Returns:
            结构相似度（0-1）
        """
        # 计算特征相似度
        similarity = 0
        total_features = 0
        
        # 比较数值特征
        numeric_features = ['line_count', 'token_count', 'function_count', 'class_count']
        for feature in numeric_features:
            val1 = features1.get(feature, 0)
            val2 = features2.get(feature, 0)
            if val1 or val2:
                similarity += 1 - abs(val1 - val2) / max(val1, val2)
                total_features += 1
        
        # 比较导入语句
        imports1 = set(features1.get('imports', []))
        imports2 = set(features2.get('imports', []))
        if imports1 or imports2:
            common_imports = imports1.intersection(imports2)
            similarity += len(common_imports) / max(len(imports1), len(imports2))
            total_features += 1
        
        # 比较关键字
        keywords1 = set(features1.get('keywords', {}).keys())
        keywords2 = set(features2.get('keywords', {}).keys())
        if keywords1 or keywords2:
            common_keywords = keywords1.intersection(keywords2)
            similarity += len(common_keywords) / max(len(keywords1), len(keywords2))
            total_features += 1
        
        if total_features == 0:
            return 0.0
        
        return similarity / total_features
    
    def _calculate_ast_similarity(self, code1: str, code2: str, language: str) -> float:
        """计算AST相似度
        
        Args:
            code1: 原始代码1
            code2: 原始代码2
            language: 代码语言
            
        Returns:
            AST相似度（0-1）
        """
        if language == 'python':
            try:
                tree1 = ast.parse(code1)
                tree2 = ast.parse(code2)
                
                # 比较AST结构
                return self._compare_ast(tree1, tree2)
            except:
                return 0.0
        else:
            # 对于其他语言，返回token相似度
            return self._calculate_token_similarity(code1, code2, language)
    
    def _compare_ast(self, node1, node2) -> float:
        """比较AST节点
        
        Args:
            node1: AST节点1
            node2: AST节点2
            
        Returns:
            相似度（0-1）
        """
        if type(node1) != type(node2):
            return 0.0
        
        # 计算子节点相似度
        children1 = list(ast.iter_child_nodes(node1))
        children2 = list(ast.iter_child_nodes(node2))
        
        if len(children1) != len(children2):
            return 0.0
        
        similarity = 1.0
        for child1, child2 in zip(children1, children2):
            similarity *= self._compare_ast(child1, child2)
        
        return similarity
    
    def _calculate_line_similarity(self, code1: str, code2: str) -> float:
        """计算行级别相似度
        
        Args:
            code1: 原始代码1
            code2: 原始代码2
            
        Returns:
            行级别相似度（0-1）
        """
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')
        
        if not lines1 or not lines2:
            return 0.0
        
        # 使用difflib计算相似度
        seq_matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return seq_matcher.ratio()
    
    def _calculate_overall_similarity(self, similarity_scores: Dict[str, float]) -> float:
        """计算综合相似度
        
        Args:
            similarity_scores: 各维度相似度得分
            
        Returns:
            综合相似度（0-1）
        """
        # 权重
        weights = {
            'token_similarity': 0.3,
            'structure_similarity': 0.2,
            'ast_similarity': 0.3,
            'line_similarity': 0.2
        }
        
        # 计算加权平均
        total_weight = sum(weights.values())
        weighted_sum = sum(score * weights.get(key, 0) for key, score in similarity_scores.items())
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _identify_similar_segments(self, code1: str, code2: str) -> List[Dict[str, Any]]:
        """识别相似代码片段
        
        Args:
            code1: 原始代码1
            code2: 原始代码2
            
        Returns:
            相似代码片段列表
        """
        similar_segments = []
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')
        
        # 使用difflib查找匹配的块
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        for block in matcher.get_matching_blocks():
            if block.size > 2:  # 至少3行相似
                segment = {
                    'code1_start': block.a,
                    'code1_end': block.a + block.size,
                    'code2_start': block.b,
                    'code2_end': block.b + block.size,
                    'lines': lines1[block.a:block.a + block.size],
                    'length': block.size
                }
                similar_segments.append(segment)
        
        return similar_segments
    
    def _evaluate_similarity_level(self, similarity: float) -> str:
        """评估相似度级别
        
        Args:
            similarity: 相似度得分
            
        Returns:
            相似度级别
        """
        if similarity >= 0.9:
            return 'identical'
        elif similarity >= 0.7:
            return 'high'
        elif similarity >= 0.5:
            return 'medium'
        elif similarity >= 0.3:
            return 'low'
        else:
            return 'none'


# 全局代码相似度检测引擎实例
code_similarity_engine = CodeSimilarityEngine()