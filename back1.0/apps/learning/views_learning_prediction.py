"""学习效果预测API视图"""

import json
import time
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import AIInteractionRecord
from .learning_prediction_engine import learning_prediction_engine


class LearningPredictionView(views.APIView):
    """
    学习效果预测API视图
    预测用户的学习效果和提供干预建议
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取学习效果预测
        """
        try:
            # 获取查询参数
            knowledge_node_id = request.query_params.get('knowledge_node_id', None)
            
            if knowledge_node_id:
                try:
                    knowledge_node_id = int(knowledge_node_id)
                except ValueError:
                    return Response(
                        {'error': '知识点ID必须是整数'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            start_time = time.time()
            
            # 生成预测
            result = learning_prediction_engine.predict_learning_effect(
                request.user.id,
                knowledge_node_id
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='learning_prediction',
                    user_input=json.dumps({
                        'knowledge_node_id': knowledge_node_id
                    }),
                    ai_response=json.dumps(result),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回预测结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"学习效果预测失败: {e}")
            return Response(
                {'error': f'预测失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchPredictionView(views.APIView):
    """
    批量学习效果预测API视图
    预测多个用户的学习效果
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        批量预测学习效果
        """
        try:
            # 获取请求参数
            user_ids = request.data.get('user_ids', [])
            
            if not user_ids or not isinstance(user_ids, list):
                return Response(
                    {'error': '用户ID列表不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_time = time.time()
            
            # 批量预测
            result = learning_prediction_engine.batch_predict(user_ids)
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='batch_prediction',
                    user_input=json.dumps({
                        'user_ids': user_ids,
                        'total_users': len(user_ids)
                    }),
                    ai_response=json.dumps(result),
                    session_id=request.data.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回预测结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"批量预测失败: {e}")
            return Response(
                {'error': f'批量预测失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictionHistoryView(views.APIView):
    """
    预测历史记录视图
    获取用户的预测历史
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取预测历史
        """
        try:
            # 获取查询参数
            days = int(request.query_params.get('days', 30))
            
            start_time = time.time()
            
            # 获取预测历史
            history = learning_prediction_engine.get_prediction_history(
                request.user.id,
                days
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='prediction_history',
                    user_input=json.dumps({
                        'days': days
                    }),
                    ai_response=json.dumps({'history': history}),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回历史记录
            return Response({
                'history': history,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"获取预测历史失败: {e}")
            return Response(
                {'error': f'获取历史失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InterventionView(views.APIView):
    """
    干预建议视图
    获取针对用户的干预建议
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取干预建议
        """
        try:
            # 获取查询参数
            knowledge_node_id = request.query_params.get('knowledge_node_id', None)
            
            if knowledge_node_id:
                try:
                    knowledge_node_id = int(knowledge_node_id)
                except ValueError:
                    return Response(
                        {'error': '知识点ID必须是整数'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            start_time = time.time()
            
            # 获取预测结果
            prediction_result = learning_prediction_engine.predict_learning_effect(
                request.user.id,
                knowledge_node_id
            )
            
            # 提取干预建议
            interventions = prediction_result.get('interventions', [])
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='intervention',
                    user_input=json.dumps({
                        'knowledge_node_id': knowledge_node_id
                    }),
                    ai_response=json.dumps({'interventions': interventions}),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回干预建议
            return Response({
                'interventions': interventions,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"获取干预建议失败: {e}")
            return Response(
                {'error': f'获取建议失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictionStatsView(views.APIView):
    """
    预测统计视图
    获取用户的预测统计数据
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取预测统计
        """
        try:
            # 获取最近30天的预测历史
            history = learning_prediction_engine.get_prediction_history(
                request.user.id,
                30
            )
            
            # 计算统计数据
            if history:
                scores = [h['score'] for h in history]
                masteries = [h['predicted_mastery'] for h in history]
                
                # 计算趋势（最近7天vs之前7天）
                if len(history) >= 14:
                    recent_scores = scores[-7:]
                    previous_scores = scores[-14:-7]
                    score_trend = (sum(recent_scores) - sum(previous_scores)) / 7
                else:
                    score_trend = 0
                
                # 计算风险分布
                risk_counts = {
                    'high': sum(1 for h in history if h['risk_level'] == 'high'),
                    'medium': sum(1 for h in history if h['risk_level'] == 'medium'),
                    'low': sum(1 for h in history if h['risk_level'] == 'low')
                }
                
                stats = {
                    'average_score': sum(scores) / len(scores),
                    'average_mastery': sum(masteries) / len(masteries),
                    'max_score': max(scores),
                    'min_score': min(scores),
                    'score_trend': score_trend,
                    'risk_distribution': risk_counts,
                    'total_predictions': len(history)
                }
            else:
                stats = {
                    'average_score': 0,
                    'average_mastery': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'score_trend': 0,
                    'risk_distribution': {'high': 0, 'medium': 0, 'low': 0},
                    'total_predictions': 0
                }
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='prediction_stats',
                    user_input=json.dumps({}),
                    ai_response=json.dumps(stats),
                    session_id=request.query_params.get('session_id', None),
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回统计数据
            return Response(
                {'stats': stats},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(f"获取预测统计失败: {e}")
            return Response(
                {'error': f'获取统计失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )