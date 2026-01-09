"""知识图谱引擎，实现多层次知识图谱构建、关系强度计算和路径规划"""

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q
from .models import KnowledgeGraph, KnowledgeNode, KnowledgeRelation


class KnowledgeGraphEngine:
    """知识图谱引擎核心类"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.vectorizer = TfidfVectorizer()
        # 使用一个默认文档来初始化向量器，避免空词汇表错误
        self.vectorizer.fit(['default'])  # 初始化向量器
    
    def build_knowledge_graph(self, graph_id=None, professional_group=None):
        """构建或更新知识图谱
        
        Args:
            graph_id: 知识图谱ID
            professional_group: 专业组名称，用于构建专业组特异性知识图谱
        
        Returns:
            构建好的知识图谱
        """
        # 1. 获取或创建知识图谱
        if graph_id:
            graph = KnowledgeGraph.objects.get(id=graph_id)
        elif professional_group:
            # 创建或获取专业组特异性知识图谱
            graph_name = f"{professional_group}专业知识图谱"
            graph, created = KnowledgeGraph.objects.get_or_create(
                name=graph_name,
                defaults={
                    'description': f"{professional_group}专业的特异性知识图谱",
                    'is_active': True
                }
            )
        else:
            # 如果没有指定图谱ID和专业组，使用默认激活的图谱
            graph = KnowledgeGraph.objects.filter(is_active=True).first()
            if not graph:
                # 如果没有激活的图谱，创建一个默认图谱
                graph = KnowledgeGraph.objects.create(
                    name="默认知识图谱",
                    description="系统默认生成的知识图谱"
                )
        
        # 2. 获取节点
        # 对于专业组图谱，确保包含所有相关节点
        if professional_group:
            # 获取所有节点，然后关联到专业组图谱
            # 这样可以确保专业组图谱包含所有相关节点，包括新添加的节点
            all_nodes = KnowledgeNode.objects.all()
            # 将它们关联到当前图谱
            for node in all_nodes:
                node.graph = graph
                node.save()
            # 查询该图谱的节点
            nodes_query = KnowledgeNode.objects.filter(graph=graph)
            # 对于专业组特异性图谱，优先显示该专业组的节点
            nodes_query = nodes_query.order_by(
                '-professional_group',  # 相同专业组的节点排在前面
                'level',
                'importance',
                'difficulty'
            )
        else:
            # 非专业组图谱，使用原有逻辑
            nodes_query = KnowledgeNode.objects.filter(graph=graph)
            
            # 如果没有找到关联到该图谱的节点，将所有现有节点关联到该图谱
            if not nodes_query.exists():
                # 获取所有没有关联图谱的节点
                all_nodes = KnowledgeNode.objects.all()
                # 将它们关联到当前图谱
                for node in all_nodes:
                    node.graph = graph
                    node.save()
                # 重新查询节点
                nodes_query = KnowledgeNode.objects.filter(graph=graph)
        nodes = nodes_query
        
        # 3. 获取关系
        # 对于专业组图谱，确保包含所有相关关系
        if professional_group:
            # 获取所有关系，然后关联到专业组图谱
            all_relations = KnowledgeRelation.objects.all()
            # 将它们关联到当前图谱
            for relation in all_relations:
                relation.graph = graph
                relation.save()
            # 查询该图谱的关系
            relations_query = KnowledgeRelation.objects.filter(graph=graph)
            # 对于专业组特异性图谱，优先显示与该专业组相关的关系
            relations_query = relations_query.filter(
                Q(source__professional_group=professional_group) | 
                Q(target__professional_group=professional_group)
            )
        else:
            # 非专业组图谱，使用原有逻辑
            relations_query = KnowledgeRelation.objects.filter(graph=graph)
            
            # 如果没有找到关联到该图谱的关系，将所有现有关系关联到该图谱
            if not relations_query.exists():
                # 获取所有没有关联图谱的关系
                all_relations = KnowledgeRelation.objects.all()
                # 将它们关联到当前图谱
                for relation in all_relations:
                    relation.graph = graph
                    relation.save()
                # 重新查询关系
                relations_query = KnowledgeRelation.objects.filter(graph=graph)
        relations = relations_query
        
        # 4. 构建图结构
        self._build_graph_structure(nodes, relations)
        
        # 5. 计算关系强度（考虑专业组）
        self._calculate_relation_strengths(professional_group)
        
        # 6. 如果是专业组特异性图谱，调整节点重要性
        if professional_group:
            self._adjust_node_importance_by_professional_group(professional_group)
        
        return self.graph
    
    def _build_graph_structure(self, nodes, relations):
        """构建图结构"""
        # 清空现有图
        self.graph.clear()
        
        # 添加节点
        for node in nodes:
            self.graph.add_node(
                node.id,
                title=node.title,
                type=node.type,
                level=node.level,
                difficulty=node.difficulty,
                importance=node.importance,
                professional_group=node.professional_group,
                description=node.description,
                tags=node.tags
            )
        
        # 添加关系
        for relation in relations:
            self.graph.add_edge(
                relation.source.id,
                relation.target.id,
                relation_type=relation.relation_type,
                strength=relation.strength
            )
    
    def _calculate_relation_strengths(self, professional_group=None):
        """计算关系强度
        
        根据文档要求，关系强度 = α × 结构强度 + β × 语义强度 + γ × 行为强度
        并考虑不同专业组的权重调整
        
        Args:
            professional_group: 专业组名称，用于计算专业组特异性关系强度
        """
        # 1. 获取所有节点的描述和信息
        node_info = {}
        for node_id in self.graph.nodes():
            node = self.graph.nodes[node_id]
            node_info[node_id] = {
                'description': node['description'],
                'type': node['type'],
                'level': node['level'],
                'professional_group': node['professional_group']
            }
        
        # 2. 计算语义相似度
        semantic_similarities = self._calculate_semantic_similarity(node_info)
        
        # 3. 计算结构强度
        structural_strengths = self._calculate_structural_strength(professional_group)
        
        # 4. 计算行为强度
        behavioral_strengths = self._calculate_behavioral_strength()
        
        # 5. 结合三种强度计算最终关系强度
        # 更新所有关系的强度
        for edge in self.graph.edges():
            source_id, target_id = edge
            relation_type = self.graph.edges[source_id, target_id]['relation_type']
            
            # 获取专业组信息，调整权重
            if professional_group:
                # 使用指定的专业组
                current_professional_group = professional_group
            else:
                # 使用源节点的专业组
                current_professional_group = node_info[source_id]['professional_group']
            
            # 调整权重
            alpha, beta, gamma = self._adjust_weights_by_professional_group(current_professional_group, relation_type)
            
            # 计算各强度分量
            semantic = semantic_similarities.get((source_id, target_id), 0.5)
            structural = structural_strengths.get((source_id, target_id), 1.0)
            behavioral = behavioral_strengths.get((source_id, target_id), 0.5)
            
            # 计算最终强度
            original_strength = self.graph.edges[source_id, target_id]['strength']
            new_strength = alpha * structural + beta * semantic + gamma * behavioral
            
            # 平滑过渡，避免突变
            new_strength = 0.7 * original_strength + 0.3 * new_strength
            new_strength = max(0.1, min(1.0, new_strength))  # 限制在0.1-1.0之间
            
            # 更新图中的关系强度
            self.graph.edges[source_id, target_id]['strength'] = new_strength
            
            # 更新数据库中的关系强度
            try:
                relation = KnowledgeRelation.objects.get(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=relation_type
                )
                relation.strength = new_strength
                relation.save()
            except KnowledgeRelation.DoesNotExist:
                pass
    
    def _calculate_semantic_similarity(self, node_info):
        """计算节点间的语义相似度"""
        node_ids = list(node_info.keys())
        if len(node_ids) < 2:
            return {}
        
        # 使用TF-IDF计算文本相似度
        texts = [node_info[node_id]['description'] for node_id in node_ids]
        tfidf_matrix = self.vectorizer.transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # 构建相似度字典
        semantic_similarities = {}
        for i, source_id in enumerate(node_ids):
            for j, target_id in enumerate(node_ids):
                if i != j:
                    semantic_similarities[(source_id, target_id)] = similarity_matrix[i][j]
        
        return semantic_similarities
    
    def _calculate_structural_strength(self, professional_group=None):
        """计算结构强度
        
        基于知识逻辑的结构化分析，考虑节点类型、层级等因素
        
        Args:
            professional_group: 专业组名称，用于计算专业组特异性结构强度
        """
        structural_strengths = {}
        
        for edge in self.graph.edges():
            source_id, target_id = edge
            source_node = self.graph.nodes[source_id]
            target_node = self.graph.nodes[target_id]
            relation_type = self.graph.edges[source_id, target_id]['relation_type']
            
            # 基础结构强度
            strength = 1.0
            
            # 根据关系类型调整
            if relation_type == 'prerequisite':
                strength *= 1.5  # 前置依赖关系强度更高
            elif relation_type == 'related':
                strength *= 0.8  # 相关关系强度较低
            
            # 根据节点类型调整
            if source_node['type'] == 'concept' and target_node['type'] == 'professional_integration':
                strength *= 1.3  # 从概念到专业融合层的关系强度更高
            elif source_node['type'] == 'professional_integration' and target_node['type'] == 'skill':
                strength *= 1.4  # 从专业融合层到技能层的关系强度更高
            elif source_node['type'] == 'skill' and target_node['type'] == 'resource':
                strength *= 1.2  # 从技能到资源的关系强度更高
            
            # 根据节点层级调整
            if target_node['level'] - source_node['level'] == 1:
                strength *= 1.3  # 相邻层级的关系强度更高
            elif abs(target_node['level'] - source_node['level']) > 2:
                strength *= 0.6  # 跨多层级的关系强度较低
            
            # 根据专业组调整
            if professional_group:
                # 增强与当前专业组相关的节点之间的关系强度
                if (source_node['professional_group'] == professional_group and 
                    target_node['professional_group'] == professional_group):
                    strength *= 1.5  # 同一专业组内的关系强度更高
                elif (source_node['professional_group'] == professional_group or 
                      target_node['professional_group'] == professional_group):
                    strength *= 1.2  # 与当前专业组相关的关系强度适中
            
            structural_strengths[(source_id, target_id)] = strength
        
        return structural_strengths
    
    def _calculate_behavioral_strength(self):
        """计算行为强度
        
        基于用户学习行为的关联分析（协同过滤）
        计算用户学习行为中知识点之间的关联强度
        """
        from .models import KnowledgeMastery
        import pandas as pd
        from collections import defaultdict
        
        behavioral_strengths = {}
        
        try:
            # 获取所有用户的知识点掌握度数据
            mastery_records = KnowledgeMastery.objects.all().select_related('user')
            
            if not mastery_records.exists():
                return behavioral_strengths
            
            # 构建用户-知识点掌握度矩阵
            user_knowledge_map = defaultdict(dict)
            
            for record in mastery_records:
                user_id = record.user.id
                knowledge_point = record.knowledge_point
                mastery_level = record.mastery_level
                user_knowledge_map[user_id][knowledge_point] = mastery_level
            
            # 转换为DataFrame，便于计算相关性
            df = pd.DataFrame.from_dict(user_knowledge_map, orient='index').fillna(0)
            
            if len(df.columns) < 2:
                return behavioral_strengths
            
            # 计算知识点之间的皮尔逊相关性
            correlation_matrix = df.corr(method='pearson')
            
            # 获取所有节点的标题，用于匹配
            node_titles = {node_id: self.graph.nodes[node_id]['title'] for node_id in self.graph.nodes()}
            
            # 构建反向映射：标题 -> 节点ID
            title_to_node_id = {title: node_id for node_id, title in node_titles.items()}
            
            # 计算节点对之间的行为强度
            for edge in self.graph.edges():
                source_id, target_id = edge
                source_title = node_titles.get(source_id, '')
                target_title = node_titles.get(target_id, '')
                
                if source_title in correlation_matrix and target_title in correlation_matrix:
                    # 使用相关性作为行为强度，范围[-1, 1]，转换为[0, 1]
                    correlation = correlation_matrix.loc[source_title, target_title]
                    behavioral_strength = (correlation + 1) / 2  # 归一化到[0, 1]
                else:
                    # 如果没有足够的数据，使用默认值0.5
                    behavioral_strength = 0.5
                
                behavioral_strengths[(source_id, target_id)] = behavioral_strength
                
        except ImportError:
            # 如果没有安装pandas，使用简单的实现
            behavioral_strengths = self._simple_behavioral_strength()
        except Exception as e:
            # 捕获其他异常，确保方法不会崩溃
            print(f"计算行为强度失败: {e}")
            behavioral_strengths = {}
        
        return behavioral_strengths
        
    def _simple_behavioral_strength(self):
        """简单的行为强度计算实现（当pandas不可用时）
        
        基于节点之间的共享标签计算行为强度
        """
        behavioral_strengths = {}
        
        for edge in self.graph.edges():
            source_id, target_id = edge
            source_node = self.graph.nodes[source_id]
            target_node = self.graph.nodes[target_id]
            
            # 获取节点标签
            source_tags = set(source_node.get('tags', []))
            target_tags = set(target_node.get('tags', []))
            
            # 计算标签相似度（Jaccard系数）
            if source_tags or target_tags:
                intersection = len(source_tags.intersection(target_tags))
                union = len(source_tags.union(target_tags))
                similarity = intersection / union if union > 0 else 0
            else:
                similarity = 0.5
            
            behavioral_strengths[(source_id, target_id)] = similarity
        
        return behavioral_strengths
    
    def _adjust_weights_by_professional_group(self, professional_group, relation_type):
        """根据专业组调整权重
        
        不同专业组对不同类型关系的权重不同
        例如：经管组更重视应用关系，理工组更重视先修关系
        """
        # 默认权重
        alpha = 0.4  # 结构强度权重
        beta = 0.3   # 语义强度权重
        gamma = 0.3  # 行为强度权重
        
        # 专业组特定调整
        if professional_group == 'business':
            # 经管组：更重视应用关系和行为数据
            if relation_type == 'application':
                alpha = 0.3
                beta = 0.3
                gamma = 0.4
        elif professional_group == 'science':
            # 理工组：更重视先修关系和结构强度
            if relation_type == 'prerequisite':
                alpha = 0.5
                beta = 0.2
                gamma = 0.3
        elif professional_group == 'humanities':
            # 文史组：更重视语义相似度
            beta = 0.4
            alpha = 0.3
            gamma = 0.3
        elif professional_group == 'arts':
            # 艺术组：更重视行为数据和应用关系
            gamma = 0.4
            alpha = 0.3
            beta = 0.3
        
        return alpha, beta, gamma
    
    def _adjust_node_importance_by_professional_group(self, professional_group):
        """根据专业组调整节点重要性
        
        为专业组特异性知识图谱调整节点重要性，使该专业组相关的节点更重要
        
        Args:
            professional_group: 专业组名称
        """
        for node_id in self.graph.nodes():
            node = self.graph.nodes[node_id]
            
            # 根据节点所属专业组调整重要性
            if node['professional_group'] == professional_group:
                # 同一专业组的节点重要性提升20%
                node['importance'] *= 1.2
            else:
                # 其他专业组的节点重要性降低10%
                node['importance'] *= 0.9
            
            # 确保重要性在合理范围内
            node['importance'] = max(1.0, min(5.0, node['importance']))
            
            # 更新数据库中的重要性
            try:
                knowledge_node = KnowledgeNode.objects.get(id=node_id)
                knowledge_node.importance = node['importance']
                knowledge_node.save()
            except KnowledgeNode.DoesNotExist:
                pass
    
    def get_shortest_path(self, start_node_id, end_node_id, weight='strength'):
        """获取最短学习路径
        
        Args:
            start_node_id: 起始节点ID
            end_node_id: 目标节点ID
            weight: 权重类型，'strength'表示使用关系强度（强度越大，路径越优）
        
        Returns:
            路径节点ID列表，如果没有路径返回None
        """
        try:
            if weight == 'strength':
                # 转换强度为距离（强度越大，距离越小）
                path = nx.shortest_path(
                    self.graph,
                    source=start_node_id,
                    target=end_node_id,
                    weight=lambda u, v, d: 1 / (d.get('strength', 1.0) + 0.001)
                )
            else:
                # 使用其他权重
                path = nx.shortest_path(
                    self.graph,
                    source=start_node_id,
                    target=end_node_id,
                    weight=weight
                )
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_recommended_path(self, user_profile, learning_goal, max_nodes=10):
        """获取推荐学习路径
        
        Args:
            user_profile: 用户画像
            learning_goal: 学习目标
            max_nodes: 最大节点数量
        
        Returns:
            推荐路径的节点列表
        """
        try:
            print(f"[DEBUG] 开始获取推荐路径，学习目标: {learning_goal}")
            
            # 1. 查找目标节点
            goal_node = self._find_goal_node(learning_goal)
            if not goal_node:
                # 如果找不到精确匹配的目标节点，使用默认节点
                goal_node = self._get_default_goal_node(learning_goal)
                if not goal_node:
                    return []
            
            # 检查目标节点是否在图中
            if goal_node.id not in self.graph.nodes():
                print(f"[DEBUG] 目标节点 {goal_node.id} 不在图中，使用默认路径")
                return self._create_default_path(learning_goal, max_nodes)
            
            print(f"[DEBUG] 找到目标节点: {goal_node.title} (ID: {goal_node.id})")
            
            # 2. 查找当前知识节点
            current_nodes = self._find_current_nodes(user_profile)
            if not current_nodes:
                # 如果没有当前知识节点，从基础节点开始
                current_nodes = self._find_base_nodes()
                if not current_nodes:
                    # 如果没有基础节点，创建一个默认的起始节点
                    current_node = self._create_default_start_node()
                    current_nodes = [current_node]
            
            # 过滤出在图中的当前节点
            current_nodes_in_graph = [node for node in current_nodes if node.id in self.graph.nodes()]
            if not current_nodes_in_graph:
                # 如果没有当前节点在图中，使用图中的第一个节点作为起始节点
                graph_nodes = list(self.graph.nodes())
                if not graph_nodes:
                    return self._create_default_path(learning_goal, max_nodes)
                start_node_id = graph_nodes[0]
                try:
                    start_node = KnowledgeNode.objects.get(id=start_node_id)
                    current_nodes_in_graph = [start_node]
                except KnowledgeNode.DoesNotExist:
                    return self._create_default_path(learning_goal, max_nodes)
            
            print(f"[DEBUG] 找到当前节点: {[node.title for node in current_nodes_in_graph]}")
            
            # 3. 计算所有可能的路径
            all_paths = []
            for start_node in current_nodes_in_graph:
                print(f"[DEBUG] 尝试从节点 {start_node.title} (ID: {start_node.id}) 到 {goal_node.title} (ID: {goal_node.id}) 计算路径")
                # 只有当起始节点不是目标节点时才计算路径
                if start_node.id != goal_node.id:
                    path = self.get_shortest_path(start_node.id, goal_node.id)
                    if path and len(path) > 1:  # 确保路径至少有两个节点
                        all_paths.append(path)
            
            if not all_paths:
                print(f"[DEBUG] 没有找到完整路径，创建扩展路径")
                # 创建一个扩展路径，从基础节点到目标节点
                # 首先找到一个合适的起始节点（不是目标节点）
                valid_start_nodes = [node for node in current_nodes_in_graph if node.id != goal_node.id]
                if not valid_start_nodes:
                    # 如果没有其他起始节点，从图中随机选择一个不同的节点
                    all_graph_nodes = list(self.graph.nodes())
                    if len(all_graph_nodes) > 1:
                        # 选择第一个与目标节点不同的节点
                        start_node_id = next((n_id for n_id in all_graph_nodes if n_id != goal_node.id), None)
                        if start_node_id:
                            # 创建一个包含起始节点和目标节点的路径
                            direct_path = [start_node_id, goal_node.id]
                            all_paths = [direct_path]
                        else:
                            # 如果只有一个节点，创建一个包含多个阶段的默认路径
                            return self._create_default_path(learning_goal, max_nodes)
                    else:
                        # 如果只有一个节点，创建一个包含多个阶段的默认路径
                        return self._create_default_path(learning_goal, max_nodes)
                else:
                    # 使用第一个有效起始节点创建路径
                    start_node = valid_start_nodes[0]
                    direct_path = [start_node.id, goal_node.id]
                    all_paths = [direct_path]
            
            # 4. 选择最优路径
            # 选择长度适中的路径，避免过短或过长
            optimal_path = None
            min_length = 2  # 最小路径长度
            max_optimal_length = min(max_nodes, 8)  # 最大优化路径长度
            
            # 先尝试找到长度在min_length到max_optimal_length之间的路径
            for path in all_paths:
                if min_length <= len(path) <= max_optimal_length:
                    optimal_path = path
                    break
            
            # 如果没有找到合适长度的路径，选择最长的路径
            if not optimal_path:
                optimal_path = max(all_paths, key=len)  # 选择最长的路径，确保包含足够的学习节点
            print(f"[DEBUG] 最优路径: {optimal_path}")
            
            # 5. 限制路径长度
            if len(optimal_path) > max_nodes:
                optimal_path = optimal_path[:max_nodes]
            
            # 6. 获取路径节点详细信息
            path_details = []
            for node_id in optimal_path:
                try:
                    node = KnowledgeNode.objects.get(id=node_id)
                    path_details.append({
                        "id": node.id,
                        "title": node.title,
                        "type": node.type,
                        "level": node.level,
                        "difficulty": node.difficulty,
                        "importance": node.importance,
                        "description": node.description,
                        "professional_group": node.professional_group,
                        "tags": node.tags
                    })
                except KnowledgeNode.DoesNotExist:
                    # 如果节点不存在，跳过该节点
                    continue
            
            print(f"[DEBUG] 最终路径详情: {path_details}")
            return path_details
        except Exception as e:
            print(f"生成推荐路径失败: {e}")
            # 返回一个默认的简化路径
            return self._create_default_path(learning_goal, max_nodes)
    
    def _get_default_goal_node(self, learning_goal):
        """获取默认目标节点
        
        Args:
            learning_goal: 学习目标
        
        Returns:
            默认目标节点
        """
        try:
            # 尝试获取任何节点作为默认目标节点
            return KnowledgeNode.objects.first()
        except KnowledgeNode.DoesNotExist:
            return None
    
    def _create_default_start_node(self):
        """创建默认起始节点
        
        Returns:
            默认起始节点
        """
        # 从数据库中获取默认图谱
        graph = KnowledgeGraph.objects.filter(is_active=True).first()
        if not graph:
            graph = KnowledgeGraph.objects.create(
                name="默认知识图谱",
                description="系统默认生成的知识图谱"
            )
        
        # 创建一个默认起始节点
        node = KnowledgeNode.objects.create(
            graph=graph,
            title="基础知识",
            type="concept",
            level=1,
            difficulty=1.0,
            importance=5.0,
            professional_group="science",
            description="基础知识节点，作为学习路径的起点"
        )
        
        # 添加到图中
        self.graph.add_node(
            node.id,
            title=node.title,
            type=node.type,
            level=node.level,
            difficulty=node.difficulty,
            importance=node.importance,
            professional_group=node.professional_group,
            description=node.description,
            tags=node.tags
        )
        
        return node
    
    def _create_default_path(self, learning_goal, max_nodes=10):
        """创建默认学习路径
        
        Args:
            learning_goal: 学习目标
            max_nodes: 最大节点数量
        
        Returns:
            默认学习路径
        """
        default_path = []
        for i in range(min(3, max_nodes)):
            default_path.append({
                "id": i + 1,
                "title": f"{learning_goal} - 阶段{i+1}",
                "type": "concept" if i == 0 else "skill",
                "level": 1 + i,
                "difficulty": 1.0 + i * 1.0,
                "importance": 5.0 - i * 0.5,
                "description": f"{learning_goal}的第{i+1}个学习阶段",
                "professional_group": "science",
                "tags": [learning_goal]
            })
        return default_path
    
    def _find_goal_node(self, learning_goal):
        """根据学习目标查找目标节点"""
        # 在知识图谱中查找与学习目标匹配的节点
        nodes = KnowledgeNode.objects.filter(
            Q(title__icontains=learning_goal) | 
            Q(description__icontains=learning_goal)
        )
        
        if nodes.exists():
            return nodes.first()
        
        # 如果没有直接匹配的节点，查找相关节点
        for node_id in self.graph.nodes():
            node = self.graph.nodes[node_id]
            tags = node.get('tags', [])
            if learning_goal.lower() in [tag.lower() for tag in tags]:
                return KnowledgeNode.objects.get(id=node_id)
        
        return None
    
    def _find_current_nodes(self, user_profile):
        """查找用户当前知识节点"""
        current_knowledge = user_profile.get('current_knowledge', [])
        current_nodes = []
        
        for knowledge in current_knowledge:
            nodes = KnowledgeNode.objects.filter(
                Q(title__icontains=knowledge) | 
                Q(description__icontains=knowledge) |
                Q(tags__contains=[knowledge])
            )
            current_nodes.extend(nodes)
        
        return current_nodes
    
    def _find_base_nodes(self):
        """查找基础节点"""
        return KnowledgeNode.objects.filter(level=1)
    
    def recommend_next_nodes(self, current_node_id, user_profile, limit=5):
        """推荐下一个学习节点
        
        Args:
            current_node_id: 当前节点ID
            user_profile: 用户画像
            limit: 推荐数量
        
        Returns:
            推荐节点ID列表
        """
        # 1. 获取当前节点的所有后继节点
        successors = list(self.graph.successors(current_node_id))
        
        # 2. 计算每个后继节点的推荐分数
        recommendations = []
        for node_id in successors:
            node = self.graph.nodes[node_id]
            
            # 计算推荐分数
            score = self._calculate_recommendation_score(node, user_profile)
            recommendations.append((node_id, score))
        
        # 3. 按分数排序并返回前N个
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [node_id for node_id, score in recommendations[:limit]]
    
    def _calculate_recommendation_score(self, node, user_profile):
        """计算推荐分数"""
        # 基础分数
        base_score = 1.0
        
        # 难度匹配分数（难度适中的节点得分更高）
        difficulty_preference = user_profile.get('difficulty_preference', 'medium')
        if difficulty_preference == 'easy':
            difficulty_match = 1.0 - abs(node['difficulty'] - 2.0) / 5.0
        elif difficulty_preference == 'medium':
            difficulty_match = 1.0 - abs(node['difficulty'] - 3.0) / 5.0
        elif difficulty_preference == 'challenging':
            difficulty_match = 1.0 - abs(node['difficulty'] - 4.0) / 5.0
        else:  # mixed
            difficulty_match = 1.0 - abs(node['difficulty'] - 3.0) / 5.0
        
        # 专业匹配分数
        professional_group = user_profile.get('professional_group', 'science')
        professional_match = 1.0 if node['professional_group'] == professional_group else 0.7
        
        # 兴趣匹配分数
        interest_match = 1.0
        if user_profile.get('interest_areas'):
            node_text = f"{node['title']} {node['description']}".lower()
            interest_score = sum(1 for interest in user_profile['interest_areas'] 
                                if interest.lower() in node_text)
            interest_match = interest_score / (len(user_profile['interest_areas']) + 1)
        
        # 学习风格匹配分数（暂时简化处理）
        learning_style_match = 1.0
        
        # 综合分数
        total_score = base_score * difficulty_match * professional_match * interest_match * learning_style_match
        return total_score
    
    def update_relation_strength(self, relation_id, new_strength):
        """更新关系强度"""
        try:
            relation = KnowledgeRelation.objects.get(id=relation_id)
            relation.strength = new_strength
            relation.save()
            
            # 更新图中的关系强度
            if self.graph.has_edge(relation.source.id, relation.target.id):
                self.graph.edges[relation.source.id, relation.target.id]['strength'] = new_strength
            
            return True
        except KnowledgeRelation.DoesNotExist:
            return False
    
    def add_node(self, node_data):
        """添加知识节点"""
        node = KnowledgeNode.objects.create(**node_data)
        
        # 添加到图中
        self.graph.add_node(
            node.id,
            title=node.title,
            type=node.type,
            level=node.level,
            difficulty=node.difficulty,
            importance=node.importance,
            professional_group=node.professional_group,
            description=node.description,
            tags=node.tags
        )
        
        return node
    
    def add_relation(self, relation_data):
        """添加知识关系"""
        relation = KnowledgeRelation.objects.create(**relation_data)
        
        # 添加到图中
        self.graph.add_edge(
            relation.source.id,
            relation.target.id,
            relation_type=relation.relation_type,
            strength=relation.strength
        )
        
        return relation
    
    def get_node_importance(self, node_id):
        """计算节点重要性"""
        # 使用PageRank算法计算节点重要性
        pagerank = nx.pagerank(self.graph, weight='strength')
        return pagerank.get(node_id, 0.0)
    
    def get_related_nodes(self, node_id, relation_type=None, limit=5):
        """获取相关节点"""
        if relation_type:
            # 获取特定类型的相关节点
            related_nodes = []
            for neighbor_id in self.graph.neighbors(node_id):
                edge_data = self.graph.edges[node_id, neighbor_id]
                if edge_data['relation_type'] == relation_type:
                    related_nodes.append(neighbor_id)
        else:
            # 获取所有相关节点
            related_nodes = list(self.graph.neighbors(node_id))
        
        # 按关系强度排序
        related_nodes.sort(
            key=lambda n: self.graph.edges[node_id, n]['strength'] if self.graph.has_edge(node_id, n) else 0,
            reverse=True
        )
        
        return related_nodes[:limit]
    
    def generate_node_embeddings(self, embedding_dim=64, method='graphsage'):
        """生成节点嵌入
        
        Args:
            embedding_dim: 嵌入维度
            method: 嵌入方法，可选值：'graphsage', 'node2vec', 'deepwalk', 'degree'
            
        Returns:
            节点嵌入字典，格式：{node_id: embedding_vector}
        """
        node_embeddings = {}
        
        try:
            if method == 'graphsage':
                # 使用GraphSAGE生成嵌入（简化实现）
                node_embeddings = self._graphsage_embedding(embedding_dim)
            elif method == 'node2vec':
                # 使用Node2Vec生成嵌入
                node_embeddings = self._node2vec_embedding(embedding_dim)
            elif method == 'deepwalk':
                # 使用DeepWalk生成嵌入
                node_embeddings = self._deepwalk_embedding(embedding_dim)
            else:
                # 使用基于度的嵌入
                node_embeddings = self._degree_based_embedding(embedding_dim)
        except Exception as e:
            print(f"生成节点嵌入失败: {e}")
            # 回退到基于度的嵌入
            node_embeddings = self._degree_based_embedding(embedding_dim)
        
        return node_embeddings
    
    def _graphsage_embedding(self, embedding_dim):
        """GraphSAGE嵌入实现（简化版本）
        
        基于节点特征和邻居聚合生成嵌入
        """
        # 为每个节点生成初始特征
        initial_features = self._get_node_features()
        
        # 确保初始特征向量长度为embedding_dim
        normalized_features = {}
        for node_id, features in initial_features.items():
            # 扩展或截断特征向量到目标维度
            if len(features) < embedding_dim:
                # 补零
                normalized = np.pad(features, (0, embedding_dim - len(features)))
            else:
                # 截断
                normalized = features[:embedding_dim]
            normalized_features[node_id] = normalized
        
        # 迭代聚合邻居特征
        for _ in range(2):  # 2层聚合
            new_features = {}
            for node_id in self.graph.nodes():
                # 获取节点的邻居
                neighbors = list(self.graph.neighbors(node_id))
                if not neighbors:
                    # 如果没有邻居，使用自身特征
                    new_features[node_id] = normalized_features.get(node_id, np.zeros(embedding_dim))
                    continue
                
                # 聚合邻居特征（简单平均）
                neighbor_features = np.mean([normalized_features.get(n_id, np.zeros(embedding_dim)) for n_id in neighbors], axis=0)
                
                # 结合自身特征
                self_feature = normalized_features.get(node_id, np.zeros(embedding_dim))
                combined = np.concatenate([self_feature, neighbor_features])
                
                # 降维到目标维度
                if len(combined) > embedding_dim:
                    # 使用简单的线性降维（取前embedding_dim个元素）
                    combined = combined[:embedding_dim]
                elif len(combined) < embedding_dim:
                    # 补零
                    combined = np.pad(combined, (0, embedding_dim - len(combined)))
                
                new_features[node_id] = combined
            
            normalized_features = new_features
        
        return normalized_features
    
    def _node2vec_embedding(self, embedding_dim):
        """Node2Vec嵌入实现（简化版本）
        
        基于随机游走生成节点嵌入
        """
        # 简化实现，使用NetworkX的随机游走和词嵌入方法
        try:
            from gensim.models import Word2Vec
            
            # 生成随机游走序列
            walks = []
            for node in self.graph.nodes():
                for _ in range(5):  # 每个节点生成5条游走路径
                    walk = nx.random_walk(self.graph, node, length=10)
                    walks.append([str(n) for n in walk])
            
            # 训练Word2Vec模型
            model = Word2Vec(walks, vector_size=embedding_dim, window=3, min_count=1, sg=1, workers=4)
            
            # 生成嵌入
            node_embeddings = {}
            for node_id in self.graph.nodes():
                node_str = str(node_id)
                if node_str in model.wv:
                    node_embeddings[node_id] = model.wv[node_str].tolist()
                else:
                    node_embeddings[node_id] = np.random.rand(embedding_dim).tolist()
            
            return node_embeddings
        except ImportError:
            # 如果没有安装gensim，回退到基于度的嵌入
            return self._degree_based_embedding(embedding_dim)
    
    def _deepwalk_embedding(self, embedding_dim):
        """DeepWalk嵌入实现（简化版本）
        
        基于无偏随机游走生成节点嵌入
        """
        # DeepWalk是Node2Vec的特例（p=q=1）
        return self._node2vec_embedding(embedding_dim)
    
    def _degree_based_embedding(self, embedding_dim):
        """基于度的简单嵌入
        
        使用节点的度和其他图特征生成嵌入
        """
        node_embeddings = {}
        
        # 计算图的各种中心性指标
        degree_centrality = nx.degree_centrality(self.graph)
        in_degree_centrality = nx.in_degree_centrality(self.graph)
        out_degree_centrality = nx.out_degree_centrality(self.graph)
        betweenness = nx.betweenness_centrality(self.graph)
        closeness = nx.closeness_centrality(self.graph)
        
        for node_id in self.graph.nodes():
            # 组合多种中心性指标作为嵌入
            features = np.array([
                degree_centrality.get(node_id, 0),
                in_degree_centrality.get(node_id, 0),
                out_degree_centrality.get(node_id, 0),
                betweenness.get(node_id, 0),
                closeness.get(node_id, 0)
            ])
            
            # 扩展到目标维度
            embedding = np.zeros(embedding_dim)
            embedding[:len(features)] = features
            
            # 填充剩余维度（使用随机值）
            if len(features) < embedding_dim:
                embedding[len(features):] = np.random.rand(embedding_dim - len(features))
            
            node_embeddings[node_id] = embedding.tolist()
        
        return node_embeddings
    
    def _get_node_features(self):
        """获取节点的多模态特征
        
        融合文本、关系、行为等多模态信息
        """
        node_features = {}
        
        # 为每个节点生成特征向量
        for node_id in self.graph.nodes():
            node = self.graph.nodes[node_id]
            
            # 文本特征（简化为TF-IDF向量的长度和平均相似度）
            text_length = len(node['description'])
            
            # 结构特征
            degree = self.graph.degree(node_id)
            in_degree = self.graph.in_degree(node_id)
            out_degree = self.graph.out_degree(node_id)
            
            # 节点属性特征
            difficulty = node['difficulty']
            importance = node['importance']
            level = node['level']
            
            # 专业组特征（独热编码）
            professional_group = node['professional_group']
            group_mapping = {'business': 0, 'humanities': 1, 'arts': 2, 'science': 3}
            group_idx = group_mapping.get(professional_group, 0)
            group_onehot = [0] * 4
            group_onehot[group_idx] = 1
            
            # 节点类型特征（独热编码）
            type_mapping = {'concept': 0, 'professional_integration': 1, 'skill': 2, 'resource': 3}
            type_idx = type_mapping.get(node['type'], 0)
            type_onehot = [0] * 4
            type_onehot[type_idx] = 1
            
            # 组合所有特征
            features = np.array([
                text_length,
                degree,
                in_degree,
                out_degree,
                difficulty,
                importance,
                level
            ] + group_onehot + type_onehot)
            
            node_features[node_id] = features
        
        return node_features
    
    def generate_professional_embeddings(self, professional_group, embedding_dim=64):
        """生成专业组特异性嵌入
        
        Args:
            professional_group: 专业组名称
            embedding_dim: 嵌入维度
            
        Returns:
            专业组特异性节点嵌入字典
        """
        # 获取所有节点嵌入
        all_embeddings = self.generate_node_embeddings(embedding_dim)
        
        # 生成专业组特异性嵌入（通过加权融合）
        professional_embeddings = {}
        
        for node_id, embedding in all_embeddings.items():
            node = self.graph.nodes[node_id]
            node_group = node['professional_group']
            
            # 根据节点所属专业组调整嵌入权重
            if node_group == professional_group:
                # 同一专业组，权重更高
                weight = 1.5
            else:
                # 不同专业组，权重较低
                weight = 0.7
            
            # 调整嵌入
            adjusted_embedding = np.array(embedding) * weight
            professional_embeddings[node_id] = adjusted_embedding.tolist()
        
        return professional_embeddings
