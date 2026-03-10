"""学习智能分析API视图

该模块提供学情智能分析相关的API接口，包括：
1. 学习模式分析
2. 学习建议生成
3. 学习习惯分析
4. 学习效率评估
"""

import time
import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.learning.models import AIInteractionRecord
from apps.learning.learning_analytics_engine import learning_analytics_engine


class LearningAnalyticsView(APIView):
    """学习智能分析视图
    
    提供学习模式分析和建议生成的API接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学习智能分析结果
        
        Returns:
            学习分析结果和建议
        """
        try:
            start_time = time.time()
            
            # 分析学习模式
            analysis_result = learning_analytics_engine.analyze_learning_patterns(
                request.user.id
            )
            
            # 生成学习建议
            recommendations_result = learning_analytics_engine.generate_learning_recommendations(
                request.user.id
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='learning_analytics',
                    user_input=json.dumps({}),
                    ai_response=json.dumps({
                        'analysis': analysis_result,
                        'recommendations': recommendations_result
                    }),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回分析结果
            return Response({
                'analysis': analysis_result,
                'recommendations': recommendations_result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"学习智能分析失败: {e}")
            return Response(
                {'error': f'分析失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningPatternsView(APIView):
    """学习模式分析视图
    
    专门提供学习模式分析的API接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学习模式分析结果
        
        Returns:
            学习模式分析结果
        """
        try:
            start_time = time.time()
            
            # 分析学习模式
            result = learning_analytics_engine.analyze_learning_patterns(
                request.user.id
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='learning_patterns',
                    user_input=json.dumps({}),
                    ai_response=json.dumps(result),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回分析结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"学习模式分析失败: {e}")
            return Response(
                {'error': f'分析失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningRecommendationsView(APIView):
    """学习建议生成视图
    
    专门提供学习建议生成的API接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学习建议
        
        Returns:
            学习建议列表
        """
        try:
            start_time = time.time()
            
            # 生成学习建议
            result = learning_analytics_engine.generate_learning_recommendations(
                request.user.id
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='learning_recommendations',
                    user_input=json.dumps({}),
                    ai_response=json.dumps(result),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回建议结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"学习建议生成失败: {e}")
            return Response(
                {'error': f'生成建议失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningEfficiencyView(APIView):
    """学习效率评估视图
    
    提供学习效率评估的API接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学习效率评估
        
        Returns:
            学习效率评估结果
        """
        try:
            start_time = time.time()
            
            # 分析学习模式
            analysis_result = learning_analytics_engine.analyze_learning_patterns(
                request.user.id
            )
            
            # 提取效率相关数据
            if 'patterns' in analysis_result:
                efficiency_data = analysis_result['patterns'].get('learning_efficiency', {})
                habits_data = analysis_result['patterns'].get('learning_habits', {})
                time_data = analysis_result['patterns'].get('time_distribution', {})
                
                efficiency_result = {
                    'learning_efficiency': efficiency_data,
                    'learning_habits': habits_data,
                    'time_distribution': time_data
                }
            else:
                efficiency_result = {
                    'learning_efficiency': {},
                    'learning_habits': {},
                    'time_distribution': {}
                }
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='learning_efficiency',
                    user_input=json.dumps({}),
                    ai_response=json.dumps(efficiency_result),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回效率评估结果
            return Response({
                'result': efficiency_result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"学习效率评估失败: {e}")
            return Response(
                {'error': f'评估失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
