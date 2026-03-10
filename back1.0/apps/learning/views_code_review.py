"""代码审查API视图"""

import json
import time
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import AIInteractionRecord
from .code_review_engine import CodeReviewEngine


class CodeReviewView(views.APIView):
    """
    智能代码审查API视图
    支持单次代码审查和批量代码审查
    """
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.review_engine = CodeReviewEngine()
    
    def post(self, request):
        """
        处理代码审查请求
        支持单代码审查和批量审查
        """
        try:
            # 获取请求参数
            code = request.data.get('code', '')
            language = request.data.get('language', 'python')
            context = request.data.get('context', {})
            batch_mode = request.data.get('batch_mode', False)
            code_snippets = request.data.get('code_snippets', [])
            
            start_time = time.time()
            
            if batch_mode and code_snippets:
                # 批量审查模式
                result = self.review_engine.batch_review(code_snippets)
            else:
                # 单代码审查模式
                if not code.strip():
                    return Response(
                        {'error': '代码内容不能为空'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                result = self.review_engine.review_code(code, language, context)
            
            response_time = time.time() - start_time
            
            # 记录交互历史（如果用户已认证）
            if request.user.is_authenticated:
                try:
                    AIInteractionRecord.objects.create(
                        user=request.user,
                        interaction_type='code_review',
                        user_input=json.dumps({
                            'code_length': len(code) if not batch_mode else len(code_snippets),
                            'language': language,
                            'batch_mode': batch_mode
                        }),
                        ai_response=json.dumps(result),
                        session_id=request.data.get('session_id', None),
                        context=context,
                        response_time=response_time,
                        tokens_used=0
                    )
                except Exception as e:
                    print(f"保存AI交互记录失败: {e}")
            
            # 返回审查结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2),
                'batch_mode': batch_mode
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"代码审查处理失败: {e}")
            return Response(
                {'error': f'代码审查失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeReviewHistoryView(views.APIView):
    """
    代码审查历史记录视图
    获取用户的历史代码审查记录
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户的代码审查历史"""
        try:
            # 获取查询参数
            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            
            # 查询用户的代码审查记录
            records = AIInteractionRecord.objects.filter(
                user=request.user,
                interaction_type='code_review'
            ).order_by('-created_at')[offset:offset + limit]
            
            # 格式化返回数据
            history_data = []
            for record in records:
                try:
                    user_input = json.loads(record.user_input)
                    ai_response = json.loads(record.ai_response)
                except json.JSONDecodeError:
                    user_input = {'error': '数据解析失败'}
                    ai_response = {'error': '数据解析失败'}
                
                history_data.append({
                    'id': record.id,
                    'created_at': record.created_at.isoformat(),
                    'code_length': user_input.get('code_length', 0),
                    'language': user_input.get('language', 'unknown'),
                    'batch_mode': user_input.get('batch_mode', False),
                    'overall_score': ai_response.get('overall_score', 0) if isinstance(ai_response, dict) else 0,
                    'response_time': record.response_time
                })
            
            # 获取总数
            total_count = AIInteractionRecord.objects.filter(
                user=request.user,
                interaction_type='code_review'
            ).count()
            
            return Response({
                'history': history_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"获取代码审查历史失败: {e}")
            return Response(
                {'error': f'获取历史记录失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeReviewDetailView(views.APIView):
    """
    代码审查详情视图
    获取特定代码审查记录的详细信息
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, record_id):
        """获取特定审查记录的详细信息"""
        try:
            # 查询记录
            record = AIInteractionRecord.objects.get(
                id=record_id,
                user=request.user,
                interaction_type='code_review'
            )
            
            # 解析数据
            try:
                user_input = json.loads(record.user_input)
                ai_response = json.loads(record.ai_response)
            except json.JSONDecodeError:
                user_input = {'error': '数据解析失败'}
                ai_response = {'error': '数据解析失败'}
            
            # 返回详细信息
            return Response({
                'id': record.id,
                'created_at': record.created_at.isoformat(),
                'user_input': user_input,
                'ai_response': ai_response,
                'response_time': record.response_time,
                'session_id': record.session_id
            }, status=status.HTTP_200_OK)
            
        except AIInteractionRecord.DoesNotExist:
            return Response(
                {'error': '记录不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"获取代码审查详情失败: {e}")
            return Response(
                {'error': f'获取详情失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeReviewStatsView(views.APIView):
    """
    代码审查统计视图
    获取用户的代码审查统计数据
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户的代码审查统计信息"""
        try:
            # 获取用户的所有代码审查记录
            records = AIInteractionRecord.objects.filter(
                user=request.user,
                interaction_type='code_review'
            )
            
            # 基础统计
            total_reviews = records.count()
            
            # 计算平均分数
            total_score = 0
            valid_reviews = 0
            
            for record in records:
                try:
                    ai_response = json.loads(record.ai_response)
                    if isinstance(ai_response, dict) and 'overall_score' in ai_response:
                        total_score += ai_response['overall_score']
                        valid_reviews += 1
                except json.JSONDecodeError:
                    continue
            
            avg_score = round(total_score / valid_reviews, 2) if valid_reviews > 0 else 0
            
            # 按语言统计
            language_stats = {}
            for record in records:
                try:
                    user_input = json.loads(record.user_input)
                    language = user_input.get('language', 'unknown')
                    language_stats[language] = language_stats.get(language, 0) + 1
                except json.JSONDecodeError:
                    continue
            
            # 按时间统计（最近30天）
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_records = records.filter(created_at__gte=thirty_days_ago)
            reviews_by_day = {}
            
            for record in recent_records:
                day = record.created_at.date().isoformat()
                reviews_by_day[day] = reviews_by_day.get(day, 0) + 1
            
            return Response({
                'total_reviews': total_reviews,
                'average_score': avg_score,
                'language_distribution': language_stats,
                'recent_activity': reviews_by_day,
                'valid_reviews': valid_reviews
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"获取代码审查统计失败: {e}")
            return Response(
                {'error': f'获取统计信息失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )