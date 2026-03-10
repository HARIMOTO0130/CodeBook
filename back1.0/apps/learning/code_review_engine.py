"""智能代码审查引擎，结合AST分析和LLM生成审查建议"""

import ast
import re
import json
from typing import Dict, List, Any
from django.conf import settings
from .llm_integration import LLMService


class CodeReviewEngine:
    """智能代码审查引擎核心类"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.rule_patterns = self._init_rule_patterns()
    
    def _init_rule_patterns(self) -> Dict[str, Any]:
        """初始化代码审查规则模式"""
        return {
            'naming_conventions': {
                'function_name': r'^[a-z_][a-z0-9_]*$',
                'class_name': r'^[A-Z][a-zA-Z0-9]*$',
                'variable_name': r'^[a-z_][a-z0-9_]*$',
                'constant_name': r'^[A-Z_][A-Z0-9_]*$'
            },
            'code_smells': {
                'long_function': 50,  # 函数行数阈值
                'complex_condition': 3,  # 条件复杂度阈值
                'deep_nesting': 4,  # 嵌套深度阈值
                'magic_number': True,  # 魔法数字检测
                'duplicated_code': True  # 重复代码检测
            }
        }
    
    def review_code(self, code: str, language: str = 'python', 
                   context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        审查代码并生成建议
        
        Args:
            code: 代码内容
            language: 编程语言
            context: 上下文信息（如用户信息、学习进度等）
        
        Returns:
            审查结果，包含建议和评分
        """
        try:
            # 1. 基础语法检查
            syntax_issues = self._check_syntax(code, language)
            
            # 2. 代码质量分析
            quality_issues = self._analyze_code_quality(code, language)
            
            # 3. 使用LLM生成智能建议
            llm_suggestions = self._generate_llm_suggestions(code, language, context)
            
            # 4. 计算综合评分
            overall_score = self._calculate_overall_score(syntax_issues, quality_issues, llm_suggestions)
            
            # 5. 生成审查报告
            review_report = {
                'overall_score': overall_score,
                'syntax_issues': syntax_issues,
                'quality_issues': quality_issues,
                'llm_suggestions': llm_suggestions,
                'improvement_suggestions': self._generate_improvement_suggestions(
                    syntax_issues, quality_issues, llm_suggestions
                ),
                'language': language,
                'code_length': len(code.split('\n'))
            }
            
            return review_report
            
        except Exception as e:
            return {
                'error': f'代码审查失败: {str(e)}',
                'overall_score': 0,
                'syntax_issues': [],
                'quality_issues': [],
                'llm_suggestions': [],
                'improvement_suggestions': ['代码审查服务暂时不可用，请稍后重试']
            }
    
    def _check_syntax(self, code: str, language: str) -> List[Dict[str, Any]]:
        """检查代码语法问题"""
        issues = []
        
        if language.lower() == 'python':
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'severity': 'high',
                    'message': f'语法错误: {str(e)}',
                    'line': e.lineno if hasattr(e, 'lineno') else None,
                    'column': e.offset if hasattr(e, 'offset') else None
                })
        
        # 检查常见语法问题
        issues.extend(self._check_common_syntax_issues(code, language))
        
        return issues
    
    def _check_common_syntax_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """检查常见的语法问题"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查缩进
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # 非空行应该有缩进（除非是顶层代码）
                if i > 1 and not lines[i-2].strip().endswith(':'):
                    issues.append({
                        'type': 'indentation',
                        'severity': 'medium',
                        'message': '第{}行: 缩进可能不正确'.format(i),
                        'line': i
                    })
            
            # 检查未关闭的括号
            if line.count('(') > line.count(')'):
                issues.append({
                    'type': 'unclosed_parenthesis',
                    'severity': 'medium',
                    'message': '第{}行: 可能有未关闭的括号'.format(i),
                    'line': i
                })
            
            # 检查未关闭的引号
            if (line.count('"') % 2 != 0 or line.count("'") % 2 != 0):
                issues.append({
                    'type': 'unclosed_quotes',
                    'severity': 'medium',
                    'message': '第{}行: 可能有未关闭的引号'.format(i),
                    'line': i
                })
        
        return issues
    
    def _analyze_code_quality(self, code: str, language: str) -> List[Dict[str, Any]]:
        """分析代码质量问题"""
        issues = []
        
        if language.lower() == 'python':
            try:
                tree = ast.parse(code)
                
                # 分析函数长度
                issues.extend(self._analyze_function_length(tree))
                
                # 分析变量命名
                issues.extend(self._analyze_naming_conventions(tree))
                
                # 分析代码复杂度
                issues.extend(self._analyze_complexity(tree))
                
                # 分析重复代码
                issues.extend(self._analyze_duplicated_code(code))
                
            except SyntaxError:
                # 语法错误已在前面检查过
                pass
        
        return issues
    
    def _analyze_function_length(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """分析函数长度"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数体行数
                function_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                
                if function_lines > self.rule_patterns['code_smells']['long_function']:
                    issues.append({
                        'type': 'long_function',
                        'severity': 'medium',
                        'message': f'函数 {node.name} 过长 ({function_lines} 行)，建议拆分为更小的函数',
                        'line': node.lineno,
                        'function_name': node.name
                    })
        
        return issues
    
    def _analyze_naming_conventions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """分析命名规范"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数命名
                if not re.match(self.rule_patterns['naming_conventions']['function_name'], node.name):
                    issues.append({
                        'type': 'naming_convention',
                        'severity': 'low',
                        'message': f'函数命名不规范: {node.name}，建议使用小写字母和下划线',
                        'line': node.lineno,
                        'element': 'function',
                        'name': node.name
                    })
            
            elif isinstance(node, ast.ClassDef):
                # 检查类命名
                if not re.match(self.rule_patterns['naming_conventions']['class_name'], node.name):
                    issues.append({
                        'type': 'naming_convention',
                        'severity': 'low',
                        'message': f'类命名不规范: {node.name}，建议使用驼峰命名法',
                        'line': node.lineno,
                        'element': 'class',
                        'name': node.name
                    })
            
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # 检查变量命名
                if not re.match(self.rule_patterns['naming_conventions']['variable_name'], node.id):
                    # 排除内置函数和特殊变量
                    if not (node.id.startswith('__') and node.id.endswith('__')):
                        issues.append({
                            'type': 'naming_convention',
                            'severity': 'low',
                            'message': f'变量命名不规范: {node.id}，建议使用小写字母和下划线',
                            'line': getattr(node, 'lineno', 0),
                            'element': 'variable',
                            'name': node.id
                        })
        
        return issues
    
    def _analyze_complexity(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """分析代码复杂度"""
        issues = []
        
        class ComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.max_nesting = 0
                self.current_nesting = 0
            
            def visit_If(self, node):
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
            
            def visit_For(self, node):
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
            
            def visit_While(self, node):
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
        
        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)
        
        if analyzer.max_nesting > self.rule_patterns['code_smells']['deep_nesting']:
            issues.append({
                'type': 'deep_nesting',
                'severity': 'medium',
                'message': f'代码嵌套过深 (最大嵌套层数: {analyzer.max_nesting})，建议简化逻辑',
                'max_nesting': analyzer.max_nesting
            })
        
        return issues
    
    def _analyze_duplicated_code(self, code: str) -> List[Dict[str, Any]]:
        """分析重复代码"""
        issues = []
        
        # 简单的重复代码检测（基于行重复）
        lines = code.split('\n')
        line_counts = {}
        
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) > 10:  # 忽略空行和短行
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        for line, count in line_counts.items():
            if count > 3:  # 同一行出现超过3次
                issues.append({
                    'type': 'duplicated_code',
                    'severity': 'low',
                    'message': f'检测到重复代码行 (出现 {count} 次)，建议提取为函数',
                    'pattern': line[:50] + '...' if len(line) > 50 else line,
                    'count': count
                })
        
        return issues
    
    def _generate_llm_suggestions(self, code: str, language: str, 
                                 context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """使用LLM生成智能代码建议"""
        try:
            # 构建提示词
            prompt = f"""请对以下{language}代码进行审查，提供改进建议：

代码：
```{language}
{code}
```

请从以下角度提供建议：
1. 代码可读性
2. 代码效率
3. 最佳实践
4. 潜在bug
5. 代码风格

请以JSON格式返回，包含以下字段：
- suggestions: 建议列表
- overall_comment: 总体评价
- improvement_areas: 需要改进的领域

每个建议包含：
- type: 建议类型
- severity: 严重程度 (low/medium/high)
- message: 具体建议
- line: 相关行号（如果有）
"""
            
            response = self.llm_service.generate_response(prompt, temperature=0.3)
            
            # 解析LLM响应
            try:
                suggestions_data = json.loads(response)
                return suggestions_data.get('suggestions', [])
            except json.JSONDecodeError:
                # 如果LLM返回的不是JSON，解析为文本格式
                return self._parse_text_suggestions(response)
                
        except Exception as e:
            print(f"LLM建议生成失败: {e}")
            return []
    
    def _parse_text_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """解析文本格式的建议"""
        suggestions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # 简单的文本解析逻辑
                suggestions.append({
                    'type': 'general',
                    'severity': 'medium',
                    'message': line,
                    'source': 'llm'
                })
        
        return suggestions[:5]  # 限制返回数量
    
    def _calculate_overall_score(self, syntax_issues: List[Dict], 
                                quality_issues: List[Dict], 
                                llm_suggestions: List[Dict]) -> float:
        """计算综合评分"""
        base_score = 100.0
        
        # 语法错误扣分（严重）
        for issue in syntax_issues:
            if issue['severity'] == 'high':
                base_score -= 20
            elif issue['severity'] == 'medium':
                base_score -= 10
            else:
                base_score -= 5
        
        # 质量问题扣分
        for issue in quality_issues:
            if issue['severity'] == 'high':
                base_score -= 15
            elif issue['severity'] == 'medium':
                base_score -= 8
            else:
                base_score -= 3
        
        # LLM建议扣分（较轻）
        for suggestion in llm_suggestions:
            if suggestion.get('severity') == 'high':
                base_score -= 5
            elif suggestion.get('severity') == 'medium':
                base_score -= 2
            else:
                base_score -= 1
        
        return max(0, min(100, base_score))
    
    def _generate_improvement_suggestions(self, syntax_issues: List[Dict], 
                                         quality_issues: List[Dict], 
                                         llm_suggestions: List[Dict]) -> List[str]:
        """生成改进建议摘要"""
        suggestions = []
        
        # 根据问题类型生成建议
        if syntax_issues:
            syntax_count = len([i for i in syntax_issues if i['severity'] == 'high'])
            if syntax_count > 0:
                suggestions.append(f'修复 {syntax_count} 个语法错误')
        
        quality_count = len(quality_issues)
        if quality_count > 0:
            suggestions.append(f'改进 {quality_count} 个代码质量问题')
        
        llm_count = len(llm_suggestions)
        if llm_count > 0:
            suggestions.append(f'参考 {llm_count} 个AI优化建议')
        
        if not suggestions:
            suggestions.append('代码质量良好，继续保持！')
        
        return suggestions
    
    def batch_review(self, code_snippets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量代码审查"""
        results = {}
        
        for snippet in code_snippets:
            code = snippet.get('code', '')
            language = snippet.get('language', 'python')
            context = snippet.get('context', {})
            
            if code:
                results[snippet.get('id', str(len(results)))] = self.review_code(code, language, context)
        
        # 生成批量审查摘要
        total_snippets = len(results)
        avg_score = sum(result['overall_score'] for result in results.values()) / total_snippets if total_snippets > 0 else 0
        
        return {
            'batch_summary': {
                'total_snippets': total_snippets,
                'average_score': round(avg_score, 2),
                'snippets_reviewed': list(results.keys())
            },
            'detailed_results': results
        }