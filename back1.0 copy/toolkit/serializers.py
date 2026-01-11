from rest_framework import serializers
from .models import Tool, ToolCategory, ToolParameter, ExecutionHistory


class ToolCategorySerializer(serializers.ModelSerializer):
    """工具分类序列化器"""
    
    class Meta:
        model = ToolCategory
        fields = ['id', 'name', 'slug', 'description']


class ToolParameterSerializer(serializers.ModelSerializer):
    """工具参数序列化器"""
    
    class Meta:
        model = ToolParameter
        fields = [
            'name', 'label', 'type', 'placeholder', 
            'default_value', 'is_required', 'options', 'order'
        ]


class ToolSerializer(serializers.ModelSerializer):
    """工具序列化器"""
    category_name = serializers.ReadOnlyField(source='category.name')
    params = ToolParameterSerializer(source='parameters', many=True, read_only=True)
    
    class Meta:
        model = Tool
        fields = [
            'id', 'name', 'description', 'icon', 'category', 'category_name',
            'book_id', 'book_title', 'chapter_number', 'first_section_id',
            'params', 'is_active'
        ]


class ExecutionHistorySerializer(serializers.ModelSerializer):
    """执行历史序列化器"""
    tool_name = serializers.ReadOnlyField(source='tool.name')
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = ExecutionHistory
        fields = [
            'id', 'user', 'user_name', 'tool', 'tool_name',
            'parameters', 'result', 'status', 'error_message', 'created_at'
        ]


class ToolRunSerializer(serializers.Serializer):
    """工具运行参数序列化器"""
    parameters = serializers.JSONField(required=True, help_text="工具执行参数")
    
    def validate_parameters(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("参数必须是JSON对象")
        return value