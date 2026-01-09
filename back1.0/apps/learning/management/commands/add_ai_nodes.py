from django.core.management.base import BaseCommand
from apps.learning.models import KnowledgeNode, KnowledgeGraph


class Command(BaseCommand):
    """添加AI学习相关知识节点的管理命令"""
    help = '为知识图谱添加AI学习相关的知识节点'

    def handle(self, *args, **kwargs):
        """执行命令"""
        self.stdout.write(self.style.SUCCESS('添加AI学习相关知识节点...'))

        # 获取默认知识图谱
        default_graph = KnowledgeGraph.objects.filter(is_active=True).first()
        if not default_graph:
            self.stdout.write(self.style.ERROR('找不到激活的知识图谱，请先创建知识图谱'))
            return

        # 定义AI学习相关节点
        ai_nodes = [
            {
                'title': 'AI基础',
                'type': 'concept',
                'level': 1,
                'difficulty': 2.0,
                'importance': 5.0,
                'description': '人工智能的基本概念、发展历史和核心原理',
                'professional_group': 'science',
                'tags': ['AI', '人工智能', '基础']
            },
            {
                'title': '机器学习',
                'type': 'skill',
                'level': 2,
                'difficulty': 3.0,
                'importance': 5.0,
                'description': '机器学习算法原理、应用场景和实践方法',
                'professional_group': 'science',
                'tags': ['AI', '机器学习', '算法']
            },
            {
                'title': '深度学习',
                'type': 'skill',
                'level': 3,
                'difficulty': 4.0,
                'importance': 5.0,
                'description': '深度学习模型（如CNN、RNN、Transformer）的原理和应用',
                'professional_group': 'science',
                'tags': ['AI', '深度学习', '神经网络']
            },
            {
                'title': '自然语言处理',
                'type': 'skill',
                'level': 3,
                'difficulty': 4.0,
                'importance': 4.5,
                'description': '自然语言处理技术，包括文本分类、情感分析、机器翻译等',
                'professional_group': 'science',
                'tags': ['AI', 'NLP', '自然语言处理']
            },
            {
                'title': '计算机视觉',
                'type': 'skill',
                'level': 3,
                'difficulty': 4.0,
                'importance': 4.5,
                'description': '计算机视觉技术，包括图像识别、目标检测、图像生成等',
                'professional_group': 'science',
                'tags': ['AI', '计算机视觉', '图像处理']
            },
            {
                'title': '数据科学',
                'type': 'skill',
                'level': 2,
                'difficulty': 3.5,
                'importance': 4.5,
                'description': '数据处理、分析和可视化技术，为AI学习提供数据支持',
                'professional_group': 'science',
                'tags': ['数据科学', '数据分析', '数据可视化']
            }
        ]

        # 添加节点
        created_count = 0
        for node_data in ai_nodes:
            # 检查节点是否已存在
            existing_node = KnowledgeNode.objects.filter(
                graph=default_graph,
                title=node_data['title']
            ).exists()
            
            if not existing_node:
                KnowledgeNode.objects.create(
                    graph=default_graph,
                    **node_data
                )
                created_count += 1
                self.stdout.write(f"创建节点: {node_data['title']}")
            else:
                self.stdout.write(f"节点已存在: {node_data['title']}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f"成功创建 {created_count} 个AI学习相关节点"))
        self.stdout.write(self.style.SUCCESS('AI学习知识节点添加完成！'))
