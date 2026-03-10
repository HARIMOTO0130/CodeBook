"""StrategyKG 知识图谱 API 接口

提供知识图谱的 CRUD 操作、路径规划、个性化推荐等功能
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from django.utils import timezone

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
from .strategy_kg_serializers import (
    StrategyKnowledgeNodeSerializer,
    StrategyRelationSerializer,
    StrategyLearningPathSerializer,
    StrategyPathNodeSerializer,
    UserStrategyPathSerializer,
    UserNodeProgressSerializer,
    StrategyRecommendationSerializer,
    StrategyUserProfileSerializer,
    StrategyResourceSerializer,
)


class StrategyKnowledgeNodeViewSet(viewsets.ModelViewSet):
    """StrategyKG 知识节点 API"""
    
    queryset = StrategyKnowledgeNode.objects.all()
    serializer_class = StrategyKnowledgeNodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        level = self.request.query_params.get('level')
        node_type = self.request.query_params.get('node_type')
        professional_group = self.request.query_params.get('professional_group')
        
        if level is not None:
            queryset = queryset.filter(level=level)
        if node_type:
            queryset = queryset.filter(node_type=node_type)
        if professional_group:
            queryset = queryset.filter(professional_group=professional_group)
        
        return queryset.order_by('level', 'importance')
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """按层级获取知识节点"""
        level = request.query_params.get('level')
        if level is None:
            return Response(
                {'error': 'level parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nodes = self.get_queryset().filter(level=level)
        serializer = self.get_serializer(nodes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def graph_data(self, request):
        """获取知识图谱数据（节点和关系）"""
        professional_group = request.query_params.get('professional_group')
        
        nodes = self.get_queryset()
        if professional_group:
            nodes = nodes.filter(professional_group=professional_group)
        
        node_serializer = self.get_serializer(nodes, many=True)
        
        relations = StrategyRelation.objects.all()
        if professional_group:
            relations = relations.filter(
                Q(source__professional_group=professional_group) |
                Q(target__professional_group=professional_group)
            )
        
        relation_serializer = StrategyRelationSerializer(relations, many=True)
        
        return Response({
            'nodes': node_serializer.data,
            'edges': relation_serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def related_nodes(self, request, pk=None):
        """获取节点的相关节点"""
        node = self.get_object()
        
        incoming_relations = node.incoming_relations.all()
        outgoing_relations = node.outgoing_relations.all()
        
        related_nodes = set()
        for relation in incoming_relations:
            related_nodes.add(relation.source)
        for relation in outgoing_relations:
            related_nodes.add(relation.target)
        
        serializer = self.get_serializer(related_nodes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """获取节点的学习资源"""
        node = self.get_object()
        resources = node.resources.all()
        serializer = StrategyResourceSerializer(resources, many=True)
        return Response(serializer.data)


class StrategyRelationViewSet(viewsets.ModelViewSet):
    """StrategyKG 知识关系 API"""
    
    queryset = StrategyRelation.objects.all()
    serializer_class = StrategyRelationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        relation_type = self.request.query_params.get('relation_type')
        source_id = self.request.query_params.get('source_id')
        target_id = self.request.query_params.get('target_id')
        
        if relation_type:
            queryset = queryset.filter(relation_type=relation_type)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        
        return queryset.order_by('-strength')


class StrategyLearningPathViewSet(viewsets.ModelViewSet):
    """StrategyKG 学习路径 API"""
    
    queryset = StrategyLearningPath.objects.filter(status='active')
    serializer_class = StrategyLearningPathSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        professional_group = self.request.query_params.get('professional_group')
        difficulty_level = self.request.query_params.get('difficulty_level')
        
        if professional_group:
            queryset = queryset.filter(professional_group=professional_group)
        if difficulty_level:
            queryset = queryset.filter(difficulty_level=difficulty_level)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """获取推荐的学习路径"""
        user = request.user
        
        try:
            profile = user.strategy_profile
        except StrategyUserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        paths = self.get_queryset().filter(
            professional_group=profile.professional_group
        )
        
        serializer = self.get_serializer(paths, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def nodes(self, request, pk=None):
        """获取路径的所有节点"""
        path = self.get_object()
        path_nodes = path.path_nodes.all().select_related('node')
        serializer = StrategyPathNodeSerializer(path_nodes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """开始学习路径"""
        path = self.get_object()
        user = request.user
        
        user_path, created = UserStrategyPath.objects.get_or_create(
            user=user,
            path=path,
            defaults={
                'status': 'active',
                'progress': 0
            }
        )
        
        if created:
            first_node = path.path_nodes.filter(order=1).first()
            if first_node:
                user_path.current_node = first_node
                user_path.save()
        
        serializer = UserStrategyPathSerializer(user_path)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """暂停学习路径"""
        path = self.get_object()
        user = request.user
        
        try:
            user_path = UserStrategyPath.objects.get(user=user, path=path)
            user_path.status = 'paused'
            user_path.save()
            serializer = UserStrategyPathSerializer(user_path)
            return Response(serializer.data)
        except UserStrategyPath.DoesNotExist:
            return Response(
                {'error': 'User path not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """继续学习路径"""
        path = self.get_object()
        user = request.user
        
        try:
            user_path = UserStrategyPath.objects.get(user=user, path=path)
            user_path.status = 'active'
            user_path.save()
            serializer = UserStrategyPathSerializer(user_path)
            return Response(serializer.data)
        except UserStrategyPath.DoesNotExist:
            return Response(
                {'error': 'User path not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UserStrategyPathViewSet(viewsets.ModelViewSet):
    """用户 StrategyKG 学习路径 API"""
    
    queryset = UserStrategyPath.objects.all()
    serializer_class = UserStrategyPathSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset.order_by('-updated_at')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前激活的学习路径"""
        active_paths = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_paths, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取学习路径的详细进度"""
        user_path = self.get_object()
        node_progresses = user_path.node_progresses.all().select_related('node')
        
        serializer = UserNodeProgressSerializer(node_progresses, many=True)
        return Response({
            'user_path': UserStrategyPathSerializer(user_path).data,
            'node_progresses': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """更新学习进度"""
        user_path = self.get_object()
        node_id = request.data.get('node_id')
        mastery_level = request.data.get('mastery_level')
        learning_hours = request.data.get('learning_hours', 0)
        notes = request.data.get('notes', '')
        
        if not node_id:
            return Response(
                {'error': 'node_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            node = StrategyKnowledgeNode.objects.get(id=node_id)
        except StrategyKnowledgeNode.DoesNotExist:
            return Response(
                {'error': 'Node not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        node_progress, created = UserNodeProgress.objects.get_or_create(
            user_path=user_path,
            node=node,
            defaults={
                'mastery_level': mastery_level or 0,
                'learning_hours': learning_hours,
                'notes': notes
            }
        )
        
        if not created:
            if mastery_level is not None:
                node_progress.mastery_level = mastery_level
            if learning_hours:
                node_progress.learning_hours += learning_hours
            if notes:
                node_progress.notes = notes
            node_progress.save()
        
        if mastery_level == 4:
            node_progress.completed_at = timezone.now()
            node_progress.save()
        
        self._recalculate_path_progress(user_path)
        
        serializer = UserNodeProgressSerializer(node_progress)
        return Response(serializer.data)
    
    def _recalculate_path_progress(self, user_path):
        """重新计算路径进度"""
        total_nodes = user_path.path.path_nodes.count()
        if total_nodes == 0:
            return
        
        completed_nodes = user_path.node_progresses.filter(
            mastery_level=4
        ).count()
        
        progress = int((completed_nodes / total_nodes) * 100)
        user_path.progress = progress
        
        if progress == 100:
            user_path.status = 'completed'
            user_path.completed_at = timezone.now()
        
        user_path.save()


class StrategyRecommendationViewSet(viewsets.ModelViewSet):
    """StrategyKG 个性化推荐 API"""
    
    queryset = StrategyRecommendation.objects.all()
    serializer_class = StrategyRecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset.order_by('-matching_score', '-created_at')
    
    @action(detail=False, methods=['get'])
    def paths(self, request):
        """获取路径推荐"""
        recommendations = self.get_queryset().filter(recommendation_type='path')
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nodes(self, request):
        """获取节点推荐"""
        recommendations = self.get_queryset().filter(recommendation_type='node')
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受推荐"""
        recommendation = self.get_object()
        recommendation.is_accepted = True
        recommendation.save()
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝推荐"""
        recommendation = self.get_object()
        recommendation.is_accepted = False
        recommendation.user_feedback = request.data.get('feedback', '')
        recommendation.save()
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)


class StrategyUserProfileViewSet(viewsets.ModelViewSet):
    """StrategyKG 用户画像 API"""
    
    queryset = StrategyUserProfile.objects.all()
    serializer_class = StrategyUserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get', 'post'])
    def me(self, request):
        """获取或更新当前用户的画像"""
        if request.method == 'GET':
            try:
                profile = self.get_queryset().get()
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            except StrategyUserProfile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            try:
                profile = self.get_queryset().get()
                serializer = self.get_serializer(profile, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            except StrategyUserProfile.DoesNotExist:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class StrategyResourceViewSet(viewsets.ModelViewSet):
    """StrategyKG 学习资源 API"""
    
    queryset = StrategyResource.objects.all()
    serializer_class = StrategyResourceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        resource_type = self.request.query_params.get('resource_type')
        node_id = self.request.query_params.get('node_id')
        
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        if node_id:
            queryset = queryset.filter(node_id=node_id)
        
        return queryset.order_by('-quality_score')
    
    @action(detail=False, methods=['get'])
    def by_node(self, request):
        """按节点获取资源"""
        node_id = request.query_params.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resources = self.get_queryset().filter(node_id=node_id)
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)