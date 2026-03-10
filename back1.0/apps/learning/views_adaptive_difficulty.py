"""自适应难度调整API视图

该模块实现自适应难度调整相关的API接口，
提供用户能力评估、难度计算、动态调整和建议生成等功能。
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.learning.adaptive_difficulty_engine import adaptive_difficulty_engine


class AdaptiveDifficultyView(APIView):
    """自适应难度调整主视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """调整难度
        
        接收当前难度和用户表现，返回调整后的难度
        """
        try:
            user_id = request.user.id
            current_difficulty = request.data.get('current_difficulty', 3.0)
            performance = request.data.get('performance', 50)
            
            # 验证参数
            if not isinstance(current_difficulty, (int, float)) or current_difficulty < 1 or current_difficulty > 5:
                return Response(
                    {'error': '当前难度必须在1-5之间'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(performance, (int, float)) or performance < 0 or performance > 100:
                return Response(
                    {'error': '用户表现必须在0-100之间'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 调用难度调整引擎
            result = adaptive_difficulty_engine.adjust_difficulty(user_id, current_difficulty, performance)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'调整难度失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AbilityEvaluationView(APIView):
    """用户能力评估视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """评估用户能力水平
        
        返回用户的能力评估结果
        """
        try:
            user_id = request.user.id
            
            # 调用能力评估方法
            result = adaptive_difficulty_engine.evaluate_user_ability(user_id)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'评估能力失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OptimalDifficultyView(APIView):
    """最优难度计算视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """计算适合的内容难度
        
        可选择指定知识点ID
        """
        try:
            user_id = request.user.id
            knowledge_node_id = request.query_params.get('knowledge_node_id')
            
            # 转换知识点ID（如果提供）
            if knowledge_node_id:
                try:
                    knowledge_node_id = int(knowledge_node_id)
                except ValueError:
                    return Response(
                        {'error': '知识点ID必须是整数'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 调用最优难度计算方法
            result = adaptive_difficulty_engine.calculate_optimal_difficulty(user_id, knowledge_node_id)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'计算最优难度失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DifficultyRecommendationsView(APIView):
    """难度调整建议视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """生成难度调整建议
        
        返回个性化的难度调整建议
        """
        try:
            user_id = request.user.id
            
            # 调用建议生成方法
            result = adaptive_difficulty_engine.generate_difficulty_recommendations(user_id)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'生成建议失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )