from django.core.management.base import BaseCommand
from apps.learning.models import KnowledgeNode, KnowledgeRelation, KnowledgeGraph


class Command(BaseCommand):
    """初始化AI学习节点关系的管理命令"""
    help = '为AI学习节点创建关系数据'

    def handle(self, *args, **kwargs):
        """执行命令"""
        self.stdout.write(self.style.SUCCESS('初始化AI学习节点关系...'))

        # 获取默认知识图谱
        default_graph = KnowledgeGraph.objects.filter(is_active=True).first()
        if not default_graph:
            self.stdout.write(self.style.ERROR('找不到激活的知识图谱，请先创建知识图谱'))
            return

        # 获取所有节点
        nodes = KnowledgeNode.objects.filter(graph=default_graph)
        if nodes.count() < 5:
            self.stdout.write(self.style.ERROR('知识节点数量不足，至少需要5个节点'))
            return

        # 创建节点映射
        node_map = {node.title: node for node in nodes}
        
        # 定义AI学习相关关系
        ai_relations = [
            # AI学习基础路径
            ('计算机基础', 'AI基础', 'prerequisite', 1.0),
            ('编程语言', 'AI基础', 'prerequisite', 0.9),
            ('AI基础', '机器学习', 'prerequisite', 1.0),
            ('机器学习', '深度学习', 'prerequisite', 1.0),
            ('数据科学', '机器学习', 'prerequisite', 0.8),
            
            # 应用方向
            ('深度学习', '自然语言处理', 'prerequisite', 1.0),
            ('深度学习', '计算机视觉', 'prerequisite', 1.0),
            ('数据分析', '数据科学', 'prerequisite', 0.9),
            
            # 相关关系
            ('自然语言处理', '计算机视觉', 'related', 0.7),
            ('机器学习', '数据科学', 'related', 0.8),
        ]

        # 创建关系
        created_count = 0
        for source_title, target_title, relation_type, strength in ai_relations:
            if source_title in node_map and target_title in node_map:
                source_node = node_map[source_title]
                target_node = node_map[target_title]
                
                # 检查关系是否已存在
                existing_relation = KnowledgeRelation.objects.filter(
                    graph=default_graph,
                    source=source_node,
                    target=target_node,
                    relation_type=relation_type
                ).exists()
                
                if not existing_relation:
                    KnowledgeRelation.objects.create(
                        graph=default_graph,
                        source=source_node,
                        target=target_node,
                        relation_type=relation_type,
                        strength=strength
                    )
                    created_count += 1
                    self.stdout.write(f"创建关系: {source_title} -> {target_title} ({relation_type}, 强度: {strength})")
                else:
                    self.stdout.write(f"关系已存在: {source_title} -> {target_title} ({relation_type})")
            else:
                self.stdout.write(f"节点不存在: {source_title} 或 {target_title}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f"成功创建 {created_count} 个AI学习关系"))
        self.stdout.write(self.style.SUCCESS('AI学习关系初始化完成！'))
