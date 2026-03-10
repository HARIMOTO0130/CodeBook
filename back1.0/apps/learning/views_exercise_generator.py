"""习题生成API视图"""

import json
import time
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import AIInteractionRecord
from .exercise_generator import exercise_generator


class ExerciseGeneratorView(views.APIView):
    """
    自动习题生成API视图
    支持基于知识点生成各类习题
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        处理习题生成请求
        """
        try:
            # 获取请求参数
            knowledge_points = request.data.get('knowledge_points', [])
            exercise_type = request.data.get('exercise_type', 'multiple_choice')
            difficulty = request.data.get('difficulty', 'medium')
            count = int(request.data.get('count', 5))
            context = request.data.get('context', {})
            
            start_time = time.time()
            
            # 验证参数
            if not knowledge_points:
                return Response(
                    {'error': '知识点不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 生成习题
            result = exercise_generator.generate_exercises(
                knowledge_points,
                exercise_type,
                difficulty,
                count,
                context
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史（如果用户已认证）
            if request.user.is_authenticated:
                try:
                    AIInteractionRecord.objects.create(
                        user=request.user,
                        interaction_type='exercise_generation',
                        user_input=json.dumps({
                            'knowledge_points': knowledge_points,
                            'exercise_type': exercise_type,
                            'difficulty': difficulty,
                            'count': count
                        }),
                        ai_response=json.dumps(result),
                        session_id=request.data.get('session_id', None),
                        context=context,
                        response_time=response_time,
                        tokens_used=0
                    )
                except Exception as e:
                    print(f"保存AI交互记录失败: {e}")
            
            # 返回生成结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"习题生成失败: {e}")
            return Response(
                {'error': f'习题生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExerciseSetGeneratorView(views.APIView):
    """
    习题集生成API视图
    生成包含多种类型和难度的习题集
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        处理习题集生成请求
        """
        try:
            # 获取请求参数
            knowledge_tree = request.data.get('knowledge_tree', {})
            difficulty_distribution = request.data.get('difficulty_distribution', None)
            type_distribution = request.data.get('type_distribution', None)
            total_count = int(request.data.get('total_count', 10))
            context = request.data.get('context', {})
            
            start_time = time.time()
            
            # 验证参数
            if not knowledge_tree:
                return Response(
                    {'error': '知识点树不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 生成习题集
            result = exercise_generator.generate_exercise_set(
                knowledge_tree,
                difficulty_distribution,
                type_distribution,
                total_count
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史（如果用户已认证）
            if request.user.is_authenticated:
                try:
                    AIInteractionRecord.objects.create(
                        user=request.user,
                        interaction_type='exercise_set_generation',
                        user_input=json.dumps({
                            'total_count': total_count,
                            'difficulty_distribution': difficulty_distribution,
                            'type_distribution': type_distribution
                        }),
                        ai_response=json.dumps(result),
                        session_id=request.data.get('session_id', None),
                        context=context,
                        response_time=response_time,
                        tokens_used=0
                    )
                except Exception as e:
                    print(f"保存AI交互记录失败: {e}")
            
            # 返回生成结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"习题集生成失败: {e}")
            return Response(
                {'error': f'习题集生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExerciseRecommendationView(views.APIView):
    """
    习题推荐API视图
    根据用户学习情况推荐习题
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取推荐习题
        """
        try:
            # 获取查询参数
            count = int(request.query_params.get('count', 5))
            
            start_time = time.time()
            
            # 生成推荐习题
            result = exercise_generator.get_recommended_exercises(
                request.user.id,
                count
            )
            
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='exercise_recommendation',
                    user_input=json.dumps({
                        'count': count
                    }),
                    ai_response=json.dumps(result),
                    session_id=request.query_params.get('session_id', None),
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                print(f"保存AI交互记录失败: {e}")
            
            # 返回推荐结果
            return Response({
                'result': result,
                'response_time': round(response_time, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"习题推荐失败: {e}")
            return Response(
                {'error': f'习题推荐失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExerciseHistoryView(views.APIView):
    """
    习题生成历史记录视图
    获取用户的历史习题生成记录
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取用户的习题生成历史
        """
        try:
            # 获取查询参数
            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            
            # 查询用户的习题生成记录
            records = AIInteractionRecord.objects.filter(
                user=request.user,
                interaction_type__in=['exercise_generation', 'exercise_set_generation']
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
                    'interaction_type': record.interaction_type,
                    'knowledge_points': user_input.get('knowledge_points', []),
                    'exercise_type': user_input.get('exercise_type', 'unknown'),
                    'difficulty': user_input.get('difficulty', 'medium'),
                    'count': user_input.get('count', 0),
                    'generated_count': len(ai_response.get('exercises', [])) if isinstance(ai_response, dict) else 0,
                    'response_time': record.response_time
                })
            
            # 获取总数
            total_count = AIInteractionRecord.objects.filter(
                user=request.user,
                interaction_type__in=['exercise_generation', 'exercise_set_generation']
            ).count()
            
            return Response({
                'history': history_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"获取习题生成历史失败: {e}")
            return Response(
                {'error': f'获取历史记录失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExerciseTypesView(views.APIView):
    """
    习题类型视图
    获取支持的习题类型和配置
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        获取习题类型配置
        """
        try:
            # 获取习题类型配置
            exercise_types = {
                'multiple_choice': {
                    'name': '选择题',
                    'description': '从多个选项中选择正确答案',
                    'difficulty_levels': {
                        'easy': '简单（2个选项）',
                        'medium': '中等（4个选项）',
                        'hard': '困难（5个选项）'
                    }
                },
                'true_false': {
                    'name': '判断题',
                    'description': '判断陈述是否正确',
                    'difficulty_levels': {
                        'easy': '简单',
                        'medium': '中等',
                        'hard': '困难'
                    }
                },
                'fill_blank': {
                    'name': '填空题',
                    'description': '填写缺失的内容',
                    'difficulty_levels': {
                        'easy': '简单（1个空）',
                        'medium': '中等（2个空）',
                        'hard': '困难（3个空）'
                    }
                },
                'coding': {
                    'name': '编程题',
                    'description': '编写代码解决问题',
                    'difficulty_levels': {
                        'easy': '简单（基础函数）',
                        'medium': '中等（算法实现）',
                        'hard': '困难（复杂算法）'
                    }
                },
                'short_answer': {
                    'name': '简答题',
                    'description': '简要回答问题',
                    'difficulty_levels': {
                        'easy': '简单（概念解释）',
                        'medium': '中等（原理阐述）',
                        'hard': '困难（分析讨论）'
                    }
                }
            }
            
            return Response({
                'exercise_types': exercise_types,
                'difficulty_levels': {
                    'easy': '简单',
                    'medium': '中等',
                    'hard': '困难'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"获取习题类型失败: {e}")
            return Response(
                {'error': f'获取习题类型失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )