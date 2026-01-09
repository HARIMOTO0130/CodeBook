"""初始化知识图谱数据"""
from django.core.management.base import BaseCommand
from apps.learning.models import KnowledgeGraph, KnowledgeNode, KnowledgeRelation


class Command(BaseCommand):
    help = '初始化知识图谱数据'

    def handle(self, *args, **kwargs):
        """执行命令"""
        self.stdout.write('正在初始化知识图谱数据...')
        
        # 创建默认知识图谱
        graph, created = KnowledgeGraph.objects.get_or_create(
            name='默认知识图谱',
            defaults={
                'description': '系统默认生成的知识图谱',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'创建知识图谱: {graph.name}')
        else:
            self.stdout.write(f'知识图谱已存在: {graph.name}')
        
        # 检查是否已有节点
        if KnowledgeNode.objects.filter(graph=graph).exists():
            self.stdout.write('知识图谱已有数据，跳过初始化')
            return
        
        # 创建基础节点
        nodes = []
        node_data = [
            {
                'title': '计算机基础',
                'type': 'concept',
                'level': 1,
                'difficulty': 1.0,
                'importance': 5.0,
                'professional_group': 'science',
                'description': '计算机科学的基础知识，包括计算机组成、操作系统、网络等'
            },
            {
                'title': '编程语言',
                'type': 'skill',
                'level': 1,
                'difficulty': 2.0,
                'importance': 5.0,
                'professional_group': 'science',
                'description': '学习和掌握编程语言，如Python、Java等'
            },
            {
                'title': '数据分析',
                'type': 'skill',
                'level': 2,
                'difficulty': 3.0,
                'importance': 4.5,
                'professional_group': 'science',
                'description': '使用数据分析工具和技术进行数据处理和分析'
            },
            {
                'title': '机器学习',
                'type': 'concept',
                'level': 3,
                'difficulty': 4.0,
                'importance': 4.5,
                'professional_group': 'science',
                'description': '机器学习算法和模型的学习和应用'
            },
            {
                'title': '深度学习',
                'type': 'concept',
                'level': 4,
                'difficulty': 4.5,
                'importance': 4.0,
                'professional_group': 'science',
                'description': '深度学习算法和神经网络模型'
            },
            {
                'title': '人工智能',
                'type': 'concept',
                'level': 5,
                'difficulty': 5.0,
                'importance': 5.0,
                'professional_group': 'science',
                'description': '人工智能的前沿技术和应用'
            },
            {
                'title': 'web开发',
                'type': 'skill',
                'level': 2,
                'difficulty': 3.0,
                'importance': 4.0,
                'professional_group': 'science',
                'description': '网站和web应用的开发技术'
            },
            {
                'title': '数据库',
                'type': 'skill',
                'level': 2,
                'difficulty': 3.0,
                'importance': 4.5,
                'professional_group': 'science',
                'description': '数据库设计和管理技术'
            }
        ]
        
        for data in node_data:
            node = KnowledgeNode.objects.create(
                graph=graph,
                **data
            )
            nodes.append(node)
            self.stdout.write(f'创建节点: {node.title}')
        
        # 创建关系
        relations = [
            (0, 1, 'prerequisite'),
            (1, 2, 'related'),
            (1, 7, 'related'),
            (1, 6, 'related'),
            (2, 3, 'prerequisite'),
            (3, 4, 'prerequisite'),
            (4, 5, 'prerequisite'),
            (6, 7, 'related'),
            (0, 7, 'related')
        ]
        
        for source_idx, target_idx, relation_type in relations:
            if source_idx < len(nodes) and target_idx < len(nodes):
                relation = KnowledgeRelation.objects.create(
                    graph=graph,
                    source=nodes[source_idx],
                    target=nodes[target_idx],
                    relation_type=relation_type,
                    strength=1.0
                )
                self.stdout.write(f'创建关系: {nodes[source_idx].title} → {nodes[target_idx].title} ({relation_type})')
        
        self.stdout.write(self.style.SUCCESS('知识图谱数据初始化完成'))
