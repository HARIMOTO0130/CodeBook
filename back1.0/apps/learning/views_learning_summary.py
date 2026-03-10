"""学习摘要生成API视图

该模块实现学习摘要生成相关的API接口，
提供学习摘要生成、主题摘要生成等功能。
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.learning.learning_summary_engine import learning_summary_engine


class LearningSummaryView(APIView):
    """学习摘要生成主视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """生成学习摘要
        
        接收时间范围参数，返回学习摘要
        """
        try:
            # 获取参数
            time_range = request.query_params.get('time_range', 'week')
            user_id = request.user.id
            
            # 验证时间范围参数
            valid_time_ranges = ['day', 'week', 'month', 'year']
            if time_range not in valid_time_ranges:
                return Response(
                    {'error': '无效的时间范围参数，有效值为：day, week, month, year'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 调用学习摘要生成引擎
            result = learning_summary_engine.generate_summary(user_id, time_range)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'生成学习摘要失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TopicSummaryView(APIView):
    """主题学习摘要生成视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """生成特定主题的学习摘要
        
        接收主题参数，返回主题学习摘要
        """
        try:
            # 获取参数
            topic = request.query_params.get('topic', '')
            user_id = request.user.id
            
            # 验证主题参数
            if not topic:
                return Response(
                    {'error': '主题参数不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 调用学习摘要生成引擎
            result = learning_summary_engine.generate_topic_summary(user_id, topic)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'生成主题学习摘要失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SummaryHistoryView(APIView):
    """学习摘要历史视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学习摘要历史
        
        返回用户的学习摘要历史记录
        """
        try:
            # 模拟历史记录
            history = [
                {
                    'id': 1,
                    'time_range': 'week',
                    'generated_at': '2024-01-01T00:00:00Z',
                    'summary_preview': '在过去的一周中，您共完成了6个学习内容，总学习时长为205分钟...'
                },
                {
                    'id': 2,
                    'time_range': 'month',
                    'generated_at': '2023-12-31T00:00:00Z',
                    'summary_preview': '在过去的一个月中，您共完成了24个学习内容，总学习时长为820分钟...'
                },
                {
                    'id': 3,
                    'time_range': 'week',
                    'generated_at': '2023-12-25T00:00:00Z',
                    'summary_preview': '在过去的一周中，您共完成了5个学习内容，总学习时长为180分钟...'
                }
            ]
            
            return Response({
                'history': history,
                'total_count': len(history)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'获取学习摘要历史失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SummaryStatsView(APIView):
    """学习摘要统计视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学习摘要统计数据
        
        返回用户的学习统计数据
        """
        try:
            # 模拟统计数据
            stats = {
                'total_summaries': 12,
                'total_learning_time': 2400,  # 分钟
                'average_score': 85.5,
                'most_studied_topic': 'Python',
                'learning_streak': 7,  # 连续学习天数
                'content_type_distribution': {
                    'video': 40,
                    'exercise': 30,
                    'article': 30
                }
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'获取学习摘要统计数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )