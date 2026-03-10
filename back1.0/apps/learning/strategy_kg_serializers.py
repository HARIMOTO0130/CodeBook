"""StrategyKG 序列化器

为 StrategyKG 模型提供 REST API 序列化功能
"""

from rest_framework import serializers
from .strategy_kg_models import (
    StrategyKnowledgeNode,
    StrategyRelation,
    StrategyLearningPath,
    StrategyPathNode,
    UserStrategyPath,
    UserNodeProgress,
    StrategyRecommendation,
    StrategyUserProfile,
    StrategyResource,
)


class StrategyKnowledgeNodeSerializer(serializers.ModelSerializer):
    """StrategyKG 知识节点序列化器"""
    
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    node_type_display = serializers.CharField(source='get_node_type_display', read_only=True)
    temporal_display = serializers.CharField(source='get_temporal_display', read_only=True)
    
    class Meta:
        model = StrategyKnowledgeNode
        fields = [
            'id', 'title', 'description', 'level', 'level_display',
            'node_type', 'node_type_display', 'temporal', 'temporal_display',
            'difficulty', 'importance', 'tags', 'metadata',
            'professional_group', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StrategyRelationSerializer(serializers.ModelSerializer):
    """StrategyKG 知识关系序列化器"""
    
    relation_type_display = serializers.CharField(source='get_relation_type_display', read_only=True)
    source_title = serializers.CharField(source='source.title', read_only=True)
    target_title = serializers.CharField(source='target.title', read_only=True)
    
    class Meta:
        model = StrategyRelation
        fields = [
            'id', 'source', 'source_title', 'target', 'target_title',
            'relation_type', 'relation_type_display', 'strength',
            'confidence', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StrategyPathNodeSerializer(serializers.ModelSerializer):
    """StrategyKG 路径节点序列化器"""
    
    node_data = StrategyKnowledgeNodeSerializer(source='node', read_only=True)
    
    class Meta:
        model = StrategyPathNode
        fields = [
            'id', 'path', 'node', 'node_data', 'order',
            'is_required', 'estimated_hours'
        ]


class StrategyLearningPathSerializer(serializers.ModelSerializer):
    """StrategyKG 学习路径序列化器"""
    
    difficulty_level_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    path_nodes = StrategyPathNodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = StrategyLearningPath
        fields = [
            'id', 'title', 'description', 'professional_group',
            'difficulty_level', 'difficulty_level_display',
            'estimated_hours', 'tags', 'status', 'status_display',
            'path_nodes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserNodeProgressSerializer(serializers.ModelSerializer):
    """用户节点进度序列化器"""
    
    node_data = StrategyKnowledgeNodeSerializer(source='node', read_only=True)
    mastery_level_display = serializers.CharField(source='get_mastery_level_display', read_only=True)
    
    class Meta:
        model = UserNodeProgress
        fields = [
            'id', 'user', 'user_path', 'node', 'node_data',
            'mastery_level', 'mastery_level_display',
            'learning_hours', 'notes', 'started_at',
            'completed_at', 'updated_at'
        ]
        read_only_fields = ['started_at', 'updated_at']


class UserStrategyPathSerializer(serializers.ModelSerializer):
    """用户 StrategyKG 学习路径序列化器"""
    
    path_data = StrategyLearningPathSerializer(source='path', read_only=True)
    current_node_data = StrategyPathNodeSerializer(source='current_node', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UserStrategyPath
        fields = [
            'id', 'user', 'path', 'path_data', 'current_node',
            'current_node_data', 'progress', 'status', 'status_display',
            'custom_goals', 'notes', 'started_at', 'completed_at',
            'updated_at'
        ]
        read_only_fields = ['started_at', 'updated_at']


class StrategyRecommendationSerializer(serializers.ModelSerializer):
    """StrategyKG 个性化推荐序列化器"""
    
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    path_data = StrategyLearningPathSerializer(source='recommended_path', read_only=True)
    node_data = StrategyKnowledgeNodeSerializer(source='recommended_node', read_only=True)
    
    class Meta:
        model = StrategyRecommendation
        fields = [
            'id', 'user', 'recommendation_type', 'recommendation_type_display',
            'recommended_path', 'path_data', 'recommended_node', 'node_data',
            'matching_score', 'recommendation_reason', 'is_accepted',
            'user_feedback', 'created_at'
        ]
        read_only_fields = ['created_at']


class StrategyUserProfileSerializer(serializers.ModelSerializer):
    """StrategyKG 用户画像序列化器"""
    
    learning_style_display = serializers.CharField(source='get_learning_style_display', read_only=True)
    pacing_preference_display = serializers.CharField(source='get_pacing_preference_display', read_only=True)
    knowledge_level_display = serializers.CharField(source='get_knowledge_level_display', read_only=True)
    
    class Meta:
        model = StrategyUserProfile
        fields = [
            'id', 'user', 'professional_group', 'knowledge_level',
            'knowledge_level_display', 'learning_style', 'learning_style_display',
            'pacing_preference', 'pacing_preference_display', 'interests',
            'learning_goals', 'total_learning_minutes', 'completed_practices',
            'avg_practice_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StrategyResourceSerializer(serializers.ModelSerializer):
    """StrategyKG 学习资源序列化器"""
    
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    node_data = StrategyKnowledgeNodeSerializer(source='node', read_only=True)
    
    class Meta:
        model = StrategyResource
        fields = [
            'id', 'title', 'description', 'resource_type',
            'resource_type_display', 'url', 'node', 'node_data',
            'book', 'chapter', 'difficulty', 'quality_score',
            'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']