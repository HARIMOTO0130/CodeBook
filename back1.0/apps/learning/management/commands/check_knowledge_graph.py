from django.core.management.base import BaseCommand
from apps.learning.models import KnowledgeNode, KnowledgeRelation, KnowledgeGraph


class Command(BaseCommand):
    """检查知识图谱数据的管理命令"""
    help = '检查知识图谱数据，包括节点、关系和图谱信息'

    def handle(self, *args, **kwargs):
        """执行命令"""
        self.stdout.write(self.style.SUCCESS('知识图谱数据检查：'))
        self.stdout.write('=' * 50)

        # 检查知识图谱数量
        graphs = KnowledgeGraph.objects.all()
        self.stdout.write(f'知识图谱数量: {graphs.count()}')
        for graph in graphs:
            self.stdout.write(f'  - {graph.name}: {graph.description}')

        self.stdout.write('')

        # 检查知识节点数量
        nodes = KnowledgeNode.objects.all()
        self.stdout.write(f'知识节点数量: {nodes.count()}')
        if nodes.count() > 0:
            self.stdout.write('示例节点：')
            for node in nodes[:5]:
                self.stdout.write(f'  - {node.title} ({node.type}, 层级: {node.level}, 难度: {node.difficulty})')

        self.stdout.write('')

        # 检查知识关系数量
        relations = KnowledgeRelation.objects.all()
        self.stdout.write(f'知识关系数量: {relations.count()}')
        if relations.count() > 0:
            self.stdout.write('示例关系：')
            for relation in relations[:5]:
                self.stdout.write(f'  - {relation.source.title} -> {relation.target.title} ({relation.relation_type}, 强度: {relation.strength})')

        self.stdout.write('')

        # 检查默认图谱的节点和关系
        self.stdout.write('默认知识图谱详情：')
        default_graph = KnowledgeGraph.objects.filter(is_active=True).first()
        if default_graph:
            default_nodes = KnowledgeNode.objects.filter(graph=default_graph)
            default_relations = KnowledgeRelation.objects.filter(graph=default_graph)
            self.stdout.write(f'  节点数量: {default_nodes.count()}')
            self.stdout.write(f'  关系数量: {default_relations.count()}')
        else:
            self.stdout.write('  没有激活的知识图谱')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('检查完成！'))
