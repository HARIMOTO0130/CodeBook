from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Tool, ToolCategory, ExecutionHistory
from .serializers import (
    ToolSerializer, ToolCategorySerializer, 
    ExecutionHistorySerializer, ToolRunSerializer
)
from .engines import get_tool_implementation, TOOL_IMPLEMENTATIONS
import json

User = get_user_model()


class ToolCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """工具分类视图集"""
    queryset = ToolCategory.objects.all()
    serializer_class = ToolCategorySerializer
    permission_classes = [permissions.AllowAny]


class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    """工具视图集"""
    queryset = Tool.objects.filter(is_active=True)
    serializer_class = ToolSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """支持分类筛选"""
        try:
            queryset = super().get_queryset()
        except Exception as e:
            # 如果查询失败，可能是数据库表结构问题，尝试修复
            error_msg = str(e)
            if 'Unknown column' in error_msg and 'title' in error_msg:
                # 自动修复缺失的 title 列
                try:
                    from django.db import connection as db_conn
                    with db_conn.cursor() as cursor:
                        cursor.execute("SHOW COLUMNS FROM toolkit_tool LIKE 'title'")
                        if not cursor.fetchone():
                            cursor.execute("ALTER TABLE toolkit_tool ADD COLUMN title VARCHAR(100) NULL")
                            cursor.execute("UPDATE toolkit_tool SET title = '未命名工具' WHERE title IS NULL")
                            cursor.execute("ALTER TABLE toolkit_tool MODIFY COLUMN title VARCHAR(100) NOT NULL")
                    # 修复后重试
                    queryset = super().get_queryset()
                except Exception as fix_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"自动修复失败: {fix_error}")
                    # 返回空查询集而不是抛出错误
                    return Tool.objects.none()
            else:
                raise
        
        category = self.request.query_params.get('category', None)
        
        if category:
            try:
                queryset = queryset.filter(category__slug=category)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def run(self, request, pk=None):
        """运行工具"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"收到工具运行请求: tool_id={pk}, data={request.data}")
            
            # 获取工具
            try:
                tool = self.get_object()
                logger.info(f"找到工具: {tool.id}, {tool.title}, implementation_class={tool.implementation_class}")
            except Tool.DoesNotExist:
                logger.error(f"工具不存在: {pk}")
                return Response({
                    "success": False,
                    "error": "工具不存在",
                    "message": f"未找到ID为{pk}的工具"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 验证参数
            logger.info(f"请求数据: {request.data}, 类型: {type(request.data)}")
            serializer = ToolRunSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"参数验证失败: {serializer.errors}, 原始数据: {request.data}")
                error_messages = []
                for field, errors in serializer.errors.items():
                    if isinstance(errors, list):
                        error_messages.extend([f"{field}: {error}" for error in errors])
                    else:
                        error_messages.append(f"{field}: {errors}")
                
                return Response({
                    "success": False,
                    "error": "参数验证失败",
                    "details": error_messages,
                    "message": "请检查输入参数",
                    "debug_info": {
                        "serializer_errors": serializer.errors,
                        "request_data": request.data,
                        "request_data_type": str(type(request.data))
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            parameters = serializer.validated_data['parameters']
            logger.info(f"参数验证成功: {parameters}")
            
            # 获取工具实现
            tool_impl_class = get_tool_implementation(tool.implementation_class)
            logger.info(f"获取工具实现: implementation_class={tool.implementation_class}, found={tool_impl_class is not None}")
            
            if not tool_impl_class:
                logger.error(f"工具实现未找到: {tool.implementation_class}")
                return Response({
                    "success": False,
                    "error": "工具实现未找到",
                    "message": f"工具'{tool.title}'的实现类'{tool.implementation_class}'未找到",
                    "debug_info": f"TOOL_IMPLEMENTATIONS: {list(TOOL_IMPLEMENTATIONS.keys())}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 执行工具
            try:
                tool_impl = tool_impl_class()
                logger.info(f"开始执行工具: {tool_impl.__class__.__name__}")
                result = tool_impl.execute(parameters)
                logger.info(f"工具执行完成: {result}")
            except Exception as e:
                # 捕获工具执行过程中的异常
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"工具执行异常: {error_trace}")
                return Response({
                    "success": False,
                    "error": f"工具执行异常: {str(e)}",
                    "message": "工具执行过程中发生错误",
                    "details": error_trace
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 记录执行历史
            user = request.user if request.user.is_authenticated else None
            try:
                execution = ExecutionHistory.objects.create(
                    user=user,
                    tool=tool,
                    parameters=parameters,
                    result=json.dumps(result, ensure_ascii=False) if result.get('success') else '',
                    status='success' if result.get('success') else 'failed',
                    error_message=result.get('error', '')[:500]  # 限制错误信息长度
                )
                execution_id = execution.id
                logger.info(f"记录执行历史成功: {execution_id}")
            except Exception as e:
                # 如果记录历史失败，不影响返回结果
                execution_id = None
                logger.warning(f"记录执行历史失败: {str(e)}")
            
            # 返回结果
            if result.get('success'):
                logger.info(f"工具执行成功: {result}")
                return Response({
                    "success": True,
                    "execution_id": execution_id,
                    "result": result.get('result'),
                    "message": "工具执行成功"
                }, status=status.HTTP_200_OK)
            else:
                error_msg = result.get('error', '未知错误')
                logger.error(f"工具执行失败: {error_msg}, result={result}")
                return Response({
                    "success": False,
                    "execution_id": execution_id,
                    "error": error_msg,
                    "message": "工具执行失败",
                    "details": result.get('details') if isinstance(result.get('details'), list) else None,
                    "debug_info": f"result={result}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            # 捕获所有未预期的异常
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"工具执行异常: {error_trace}")
            
            return Response({
                "success": False,
                "error": f"服务器内部错误: {str(e)}",
                "message": "工具执行失败，请稍后重试",
                "details": error_trace
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecutionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """执行历史视图集"""
    serializer_class = ExecutionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的执行历史"""
        user = self.request.user
        return ExecutionHistory.objects.filter(user=user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的执行历史"""
        user = request.user
        recent_history = ExecutionHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        serializer = self.get_serializer(recent_history, many=True)
        return Response(serializer.data)