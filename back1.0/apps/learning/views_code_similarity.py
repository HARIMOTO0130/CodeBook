"""代码相似度检测API视图

该模块实现代码相似度检测相关的API接口，
提供代码相似度计算、批量比较等功能。
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.learning.code_similarity_engine import code_similarity_engine


class CodeSimilarityView(APIView):
    """代码相似度检测主视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """计算两段代码的相似度
        
        接收两段代码和语言类型，返回相似度计算结果
        """
        try:
            code1 = request.data.get('code1', '')
            code2 = request.data.get('code2', '')
            language = request.data.get('language', 'python')
            
            # 验证参数
            if not code1 or not code2:
                return Response(
                    {'error': '两段代码都不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 调用相似度检测引擎
            result = code_similarity_engine.calculate_similarity(code1, code2, language)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'计算相似度失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchSimilarityView(APIView):
    """批量代码相似度检测视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """批量比较代码相似度
        
        接收目标代码和参考代码列表，返回批量比较结果
        """
        try:
            target_code = request.data.get('target_code', '')
            reference_codes = request.data.get('reference_codes', [])
            language = request.data.get('language', 'python')
            
            # 验证参数
            if not target_code:
                return Response(
                    {'error': '目标代码不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(reference_codes, list):
                return Response(
                    {'error': '参考代码必须是列表'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 调用批量比较方法
            result = code_similarity_engine.batch_compare(target_code, reference_codes, language)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'批量比较失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimilarityAnalysisView(APIView):
    """相似度分析视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """分析代码相似度结果
        
        接收相似度计算结果，返回详细分析
        """
        try:
            similarity_result = request.data.get('similarity_result', {})
            
            # 验证参数
            if not similarity_result:
                return Response(
                    {'error': '相似度结果不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 分析相似度结果
            analysis = self._analyze_similarity_result(similarity_result)
            
            return Response(analysis, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'分析相似度结果失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _analyze_similarity_result(self, similarity_result: dict) -> dict:
        """分析相似度结果
        
        Args:
            similarity_result: 相似度计算结果
            
        Returns:
            分析结果
        """
        analysis = {
            'overall_analysis': self._analyze_overall_similarity(similarity_result.get('overall_similarity', 0)),
            'detailed_analysis': self._analyze_detailed_similarity(similarity_result.get('similarity_scores', {})),
            'segment_analysis': self._analyze_similar_segments(similarity_result.get('similar_segments', [])),
            'recommendations': self._generate_recommendations(similarity_result)
        }
        
        return analysis
    
    def _analyze_overall_similarity(self, overall_similarity: float) -> dict:
        """分析综合相似度
        
        Args:
            overall_similarity: 综合相似度得分
            
        Returns:
            分析结果
        """
        if overall_similarity >= 0.9:
            return {
                'level': 'identical',
                'description': '代码几乎完全相同',
                'severity': 'high',
                'message': '两段代码高度相似，可能存在抄袭行为'
            }
        elif overall_similarity >= 0.7:
            return {
                'level': 'high',
                'description': '代码高度相似',
                'severity': 'medium',
                'message': '两段代码有较多相似之处，建议检查是否存在借鉴'
            }
        elif overall_similarity >= 0.5:
            return {
                'level': 'medium',
                'description': '代码中度相似',
                'severity': 'low',
                'message': '两段代码有一定相似性，可能是思路相近'
            }
        else:
            return {
                'level': 'low',
                'description': '代码相似度较低',
                'severity': 'none',
                'message': '两段代码相似度较低，不存在抄袭风险'
            }
    
    def _analyze_detailed_similarity(self, similarity_scores: dict) -> dict:
        """分析详细相似度
        
        Args:
            similarity_scores: 各维度相似度得分
            
        Returns:
            分析结果
        """
        analysis = {}
        
        for score_type, score in similarity_scores.items():
            if score_type == 'token_similarity':
                analysis[score_type] = {
                    'score': score,
                    'description': '代码令牌相似度',
                    'interpretation': self._interpret_score(score, '代码词汇和语法结构的相似程度')
                }
            elif score_type == 'structure_similarity':
                analysis[score_type] = {
                    'score': score,
                    'description': '代码结构相似度',
                    'interpretation': self._interpret_score(score, '代码结构和组织方式的相似程度')
                }
            elif score_type == 'ast_similarity':
                analysis[score_type] = {
                    'score': score,
                    'description': '抽象语法树相似度',
                    'interpretation': self._interpret_score(score, '代码语法结构的相似程度')
                }
            elif score_type == 'line_similarity':
                analysis[score_type] = {
                    'score': score,
                    'description': '行级别相似度',
                    'interpretation': self._interpret_score(score, '代码行的相似程度')
                }
        
        return analysis
    
    def _interpret_score(self, score: float, description: str) -> str:
        """解释相似度得分
        
        Args:
            score: 相似度得分
            description: 得分描述
            
        Returns:
            解释文本
        """
        if score >= 0.9:
            return f'{description}极高，几乎完全相同'
        elif score >= 0.7:
            return f'{description}较高，有明显相似性'
        elif score >= 0.5:
            return f'{description}中等，存在一定相似性'
        else:
            return f'{description}较低，相似性不明显'
    
    def _analyze_similar_segments(self, similar_segments: list) -> dict:
        """分析相似代码片段
        
        Args:
            similar_segments: 相似代码片段列表
            
        Returns:
            分析结果
        """
        if not similar_segments:
            return {
                'count': 0,
                'total_length': 0,
                'description': '未发现明显相似的代码片段'
            }
        
        total_length = sum(segment['length'] for segment in similar_segments)
        
        return {
            'count': len(similar_segments),
            'total_length': total_length,
            'longest_segment': max(similar_segments, key=lambda x: x['length']) if similar_segments else None,
            'description': f'发现{len(similar_segments)}个相似代码片段，总长度为{total_length}行'
        }
    
    def _generate_recommendations(self, similarity_result: dict) -> list:
        """生成建议
        
        Args:
            similarity_result: 相似度计算结果
            
        Returns:
            建议列表
        """
        recommendations = []
        overall_similarity = similarity_result.get('overall_similarity', 0)
        
        if overall_similarity >= 0.9:
            recommendations.append({
                'title': '检查抄袭行为',
                'description': '代码相似度极高，可能存在抄袭行为，请仔细检查',
                'priority': 'high'
            })
        elif overall_similarity >= 0.7:
            recommendations.append({
                'title': '确认代码来源',
                'description': '代码相似度较高，建议确认代码来源，确保没有不当借鉴',
                'priority': 'medium'
            })
        elif overall_similarity >= 0.5:
            recommendations.append({
                'title': '优化代码结构',
                'description': '代码有一定相似性，可以考虑优化代码结构，增加原创性',
                'priority': 'low'
            })
        else:
            recommendations.append({
                'title': '保持原创性',
                'description': '代码相似度较低，继续保持原创性',
                'priority': 'low'
            })
        
        # 添加通用建议
        recommendations.append({
            'title': '代码规范',
            'description': '无论相似度如何，都应该遵循良好的代码规范和命名约定',
            'priority': 'medium'
        })
        
        recommendations.append({
            'title': '添加注释',
            'description': '为代码添加详细注释，说明实现思路和关键部分',
            'priority': 'medium'
        })
        
        return recommendations