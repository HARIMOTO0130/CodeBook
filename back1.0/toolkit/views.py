from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Tool, ToolCategory, ExecutionHistory
from .serializers import (
    ToolSerializer, ToolCategorySerializer, 
    ExecutionHistorySerializer, ToolRunSerializer
)
from .engines import get_tool_implementation
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
        queryset = super().get_queryset()
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
        # 获取工具
        try:
            tool = self.get_object()
        except Tool.DoesNotExist:
            return Response(
                {"error": "工具不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 验证参数
        serializer = ToolRunSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        parameters = serializer.validated_data['parameters']
        
        # 获取工具实现
        tool_impl_class = get_tool_implementation(tool.implementation_class)
        if not tool_impl_class:
            return Response(
                {"error": "工具实现未找到"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 执行工具
        tool_impl = tool_impl_class()
        result = tool_impl.execute(parameters)
        
        # 记录执行历史
        user = request.user if request.user.is_authenticated else None
        # 确保error_message字段有值，即使是空字符串也明确设置
        error_message = result.get('error', '')
        if error_message is None:
            error_message = ''
            
        execution = ExecutionHistory.objects.create(
            user=user,
            tool=tool,
            parameters=parameters,
            result=json.dumps(result) if result.get('success') else '',
            status='success' if result.get('success') else 'failed',
            error_message=error_message
        )
        
        # 返回结果
        if result.get('success'):
            return Response({
                "success": True,
                "execution_id": execution.id,
                "result": result.get('result'),
                "message": "工具执行成功"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "execution_id": execution.id,
                "error": result.get('error'),
                "message": "工具执行失败"
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