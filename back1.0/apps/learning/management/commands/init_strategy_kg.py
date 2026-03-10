"""初始化 StrategyKG 知识图谱数据

创建四层知识结构的基础数据，包括：
- Level 0: 概念层（基础理论）
- Level 1: 分类层（技术领域）
- Level 2: 实体层（具体技能）
- Level 3: 动态层（实时数据）
"""

from django.core.management.base import BaseCommand
from apps.learning.strategy_kg_models import (
    StrategyKnowledgeNode,
    StrategyRelation,
    StrategyLearningPath,
    StrategyPathNode,
    StrategyResource,
)


class Command(BaseCommand):
    help = '初始化 StrategyKG 知识图谱数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化 StrategyKG 知识图谱数据...')
        
        professional_groups = ['business', 'science', 'humanities', 'arts']
        
        for group in professional_groups:
            self._create_knowledge_nodes(group)
            self._create_relations(group)
            self._create_learning_paths(group)
            self._create_resources(group)
        
        self.stdout.write(self.style.SUCCESS('StrategyKG 知识图谱数据初始化完成！'))
    
    def _create_knowledge_nodes(self, professional_group):
        """创建知识节点"""
        self.stdout.write(f'创建 {professional_group} 专业组的知识节点...')
        
        if professional_group == 'business':
            nodes_data = [
                # Level 0: 概念层
                {
                    'title': '算法复杂度',
                    'description': '衡量算法效率的指标，包括时间复杂度和空间复杂度',
                    'level': 0,
                    'node_type': 'concept',
                    'temporal': 'atemporal',
                    'difficulty': 2.0,
                    'importance': 5.0,
                    'tags': ['基础理论', '算法'],
                    'professional_group': professional_group
                },
                {
                    'title': '面向对象编程',
                    'description': '一种编程范式，基于对象和类的概念',
                    'level': 0,
                    'node_type': 'concept',
                    'temporal': 'atemporal',
                    'difficulty': 2.5,
                    'importance': 5.0,
                    'tags': ['基础理论', '编程范式'],
                    'professional_group': professional_group
                },
                # Level 1: 分类层
                {
                    'title': '前端开发',
                    'description': '创建用户界面和用户体验的软件开发',
                    'level': 1,
                    'node_type': 'skill',
                    'temporal': 'long_term',
                    'difficulty': 3.0,
                    'importance': 4.5,
                    'tags': ['Web开发', 'UI/UX'],
                    'professional_group': professional_group
                },
                {
                    'title': '机器学习',
                    'description': '人工智能的一个分支，使计算机能够从数据中学习',
                    'level': 1,
                    'node_type': 'skill',
                    'temporal': 'long_term',
                    'difficulty': 4.0,
                    'importance': 4.8,
                    'tags': ['AI', '数据科学'],
                    'professional_group': professional_group
                },
                # Level 2: 实体层
                {
                    'title': 'React框架',
                    'description': '用于构建用户界面的JavaScript库',
                    'level': 2,
                    'node_type': 'skill',
                    'temporal': 'historical',
                    'difficulty': 3.5,
                    'importance': 4.2,
                    'tags': ['前端', 'JavaScript', '框架'],
                    'professional_group': professional_group
                },
                {
                    'title': 'Python语法',
                    'description': 'Python编程语言的基础语法和特性',
                    'level': 2,
                    'node_type': 'skill',
                    'temporal': 'historical',
                    'difficulty': 2.0,
                    'importance': 4.5,
                    'tags': ['Python', '编程基础'],
                    'professional_group': professional_group
                },
                {
                    'title': '数据分析',
                    'description': '使用统计和计算方法从数据中提取洞察',
                    'level': 2,
                    'node_type': 'skill',
                    'temporal': 'historical',
                    'difficulty': 3.5,
                    'importance': 4.3,
                    'tags': ['数据科学', '统计'],
                    'professional_group': professional_group
                },
                # Level 3: 动态层
                {
                    'title': 'Python 3.12新特性',
                    'description': 'Python 3.12版本引入的新功能和改进',
                    'level': 3,
                    'node_type': 'resource',
                    'temporal': 'realtime',
                    'difficulty': 3.0,
                    'importance': 3.5,
                    'tags': ['Python', '新特性', '更新'],
                    'professional_group': professional_group
                },
                {
                    'title': 'React 18并发模式',
                    'description': 'React 18引入的并发渲染模式',
                    'level': 3,
                    'node_type': 'resource',
                    'temporal': 'realtime',
                    'difficulty': 4.0,
                    'importance': 3.8,
                    'tags': ['React', '并发', '新特性'],
                    'professional_group': professional_group
                },
            ]
        elif professional_group == 'science':
            nodes_data = [
                # Level 0: 概念层
                {
                    'title': '数据结构',
                    'description': '组织和存储数据的方式，影响算法效率',
                    'level': 0,
                    'node_type': 'concept',
                    'temporal': 'atemporal',
                    'difficulty': 2.5,
                    'importance': 5.0,
                    'tags': ['基础理论', '计算机科学'],
                    'professional_group': professional_group
                },
                {
                    'title': '计算机网络',
                    'description': '计算机之间通信和资源共享的系统',
                    'level': 0,
                    'node_type': 'concept',
                    'temporal': 'atemporal',
                    'difficulty': 3.0,
                    'importance': 4.8,
                    'tags': ['基础理论', '网络'],
                    'professional_group': professional_group
                },
                # Level 1: 分类层
                {
                    'title': '后端开发',
                    'description': '服务器端应用程序开发',
                    'level': 1,
                    'node_type': 'skill',
                    'temporal': 'long_term',
                    'difficulty': 3.5,
                    'importance': 4.5,
                    'tags': ['Web开发', '服务器'],
                    'professional_group': professional_group
                },
                {
                    'title': '数据库管理',
                    'description': '设计、实现和维护数据库系统',
                    'level': 1,
                    'node_type': 'skill',
                    'temporal': 'long_term',
                    'difficulty': 3.5,
                    'importance': 4.6,
                    'tags': ['数据库', '数据管理'],
                    'professional_group': professional_group
                },
                # Level 2: 实体层
                {
                    'title': 'Django框架',
                    'description': 'Python Web开发框架',
                    'level': 2,
                    'node_type': 'skill',
                    'temporal': 'historical',
                    'difficulty': 3.5,
                    'importance': 4.3,
                    'tags': ['Python', 'Web框架', '后端'],
                    'professional_group': professional_group
                },
                {
                    'title': 'SQL查询',
                    'description': '结构化查询语言，用于数据库操作',
                    'level': 2,
                    'node_type': 'skill',
                    'temporal': 'historical',
                    'difficulty': 2.5,
                    'importance': 4.5,
                    'tags': ['数据库', 'SQL'],
                    'professional_group': professional_group
                },
                # Level 3: 动态层
                {
                    'title': 'Django 5.0新特性',
                    'description': 'Django 5.0版本的新功能和改进',
                    'level': 3,
                    'node_type': 'resource',
                    'temporal': 'realtime',
                    'difficulty': 3.5,
                    'importance': 3.6,
                    'tags': ['Django', '新特性'],
                    'professional_group': professional_group
                },
            ]
        else:
            nodes_data = []
        
        for node_data in nodes_data:
            StrategyKnowledgeNode.objects.get_or_create(
                title=node_data['title'],
                professional_group=professional_group,
                defaults=node_data
            )
        
        self.stdout.write(f'创建了 {len(nodes_data)} 个知识节点')
    
    def _create_relations(self, professional_group):
        """创建知识关系"""
        self.stdout.write(f'创建 {professional_group} 专业组的知识关系...')
        
        nodes = {node.title: node for node in StrategyKnowledgeNode.objects.filter(professional_group=professional_group)}
        
        if professional_group == 'business':
            relations_data = [
                ('算法复杂度', '面向对象编程', 'related', 0.7),
                ('算法复杂度', '前端开发', 'requires', 0.9),
                ('算法复杂度', '机器学习', 'requires', 0.95),
                ('面向对象编程', '前端开发', 'requires', 0.85),
                ('面向对象编程', 'Python语法', 'requires', 0.8),
                ('前端开发', 'React框架', 'leads_to', 0.9),
                ('机器学习', '数据分析', 'leads_to', 0.85),
                ('机器学习', 'Python语法', 'requires', 0.9),
                ('Python语法', '数据分析', 'requires', 0.8),
                ('Python语法', 'Python 3.12新特性', 'similar_to', 0.7),
                ('React框架', 'React 18并发模式', 'similar_to', 0.75),
            ]
        elif professional_group == 'science':
            relations_data = [
                ('数据结构', '计算机网络', 'related', 0.6),
                ('数据结构', '后端开发', 'requires', 0.9),
                ('数据结构', '数据库管理', 'requires', 0.85),
                ('计算机网络', '后端开发', 'requires', 0.8),
                ('后端开发', 'Django框架', 'leads_to', 0.9),
                ('数据库管理', 'SQL查询', 'leads_to', 0.95),
                ('数据库管理', 'Django框架', 'related', 0.7),
                ('Django框架', 'Django 5.0新特性', 'similar_to', 0.7),
            ]
        else:
            relations_data = []
        
        for source_title, target_title, relation_type, strength in relations_data:
            if source_title in nodes and target_title in nodes:
                StrategyRelation.objects.get_or_create(
                    source=nodes[source_title],
                    target=nodes[target_title],
                    relation_type=relation_type,
                    defaults={'strength': strength}
                )
        
        self.stdout.write(f'创建了 {len(relations_data)} 条知识关系')
    
    def _create_learning_paths(self, professional_group):
        """创建学习路径"""
        self.stdout.write(f'创建 {professional_group} 专业组的学习路径...')
        
        if professional_group == 'business':
            paths_data = [
                {
                    'title': 'Python数据分析入门',
                    'description': '从零基础到掌握Python数据分析技能',
                    'professional_group': professional_group,
                    'difficulty_level': 'beginner',
                    'estimated_hours': 60,
                    'tags': ['Python', '数据分析', '入门'],
                    'nodes': [
                        ('Python语法', 1, True, 10),
                        ('数据分析', 2, True, 20),
                        ('机器学习', 3, True, 30),
                    ]
                },
                {
                    'title': '前端开发进阶',
                    'description': '掌握现代前端开发技术栈',
                    'professional_group': professional_group,
                    'difficulty_level': 'intermediate',
                    'estimated_hours': 80,
                    'tags': ['前端', 'React', '进阶'],
                    'nodes': [
                        ('算法复杂度', 1, True, 5),
                        ('面向对象编程', 2, True, 10),
                        ('前端开发', 3, True, 20),
                        ('React框架', 4, True, 45),
                    ]
                },
            ]
        elif professional_group == 'science':
            paths_data = [
                {
                    'title': 'Python后端开发',
                    'description': '使用Python和Django构建后端应用',
                    'professional_group': professional_group,
                    'difficulty_level': 'intermediate',
                    'estimated_hours': 70,
                    'tags': ['Python', 'Django', '后端'],
                    'nodes': [
                        ('Python语法', 1, True, 10),
                        ('数据结构', 2, True, 15),
                        ('后端开发', 3, True, 20),
                        ('Django框架', 4, True, 25),
                    ]
                },
            ]
        else:
            paths_data = []
        
        nodes_map = {node.title: node for node in StrategyKnowledgeNode.objects.filter(professional_group=professional_group)}
        
        for path_data in paths_data:
            path, created = StrategyLearningPath.objects.get_or_create(
                title=path_data['title'],
                professional_group=professional_group,
                defaults={k: v for k, v in path_data.items() if k != 'nodes'}
            )
            
            if created:
                for node_title, order, is_required, estimated_hours in path_data['nodes']:
                    if node_title in nodes_map:
                        StrategyPathNode.objects.create(
                            path=path,
                            node=nodes_map[node_title],
                            order=order,
                            is_required=is_required,
                            estimated_hours=estimated_hours
                        )
        
        self.stdout.write(f'创建了 {len(paths_data)} 条学习路径')
    
    def _create_resources(self, professional_group):
        """创建学习资源"""
        self.stdout.write(f'创建 {professional_group} 专业组的学习资源...')
        
        nodes = {node.title: node for node in StrategyKnowledgeNode.objects.filter(professional_group=professional_group)}
        
        if professional_group == 'business':
            resources_data = [
                {
                    'title': 'Python官方文档',
                    'description': 'Python编程语言的官方文档',
                    'resource_type': 'article',
                    'url': 'https://docs.python.org/3/',
                    'node_title': 'Python语法',
                    'difficulty': 2.0,
                    'quality_score': 5.0,
                    'tags': ['官方文档', '参考']
                },
                {
                    'title': 'React官方教程',
                    'description': 'React框架的官方教程',
                    'resource_type': 'article',
                    'url': 'https://react.dev/learn',
                    'node_title': 'React框架',
                    'difficulty': 3.5,
                    'quality_score': 5.0,
                    'tags': ['官方教程', 'React']
                },
            ]
        elif professional_group == 'science':
            resources_data = [
                {
                    'title': 'Django官方文档',
                    'description': 'Django Web框架的官方文档',
                    'resource_type': 'article',
                    'url': 'https://docs.djangoproject.com/',
                    'node_title': 'Django框架',
                    'difficulty': 3.5,
                    'quality_score': 5.0,
                    'tags': ['官方文档', 'Django']
                },
            ]
        else:
            resources_data = []
        
        for resource_data in resources_data:
            node_title = resource_data.pop('node_title')
            if node_title in nodes:
                StrategyResource.objects.get_or_create(
                    title=resource_data['title'],
                    node=nodes[node_title],
                    defaults=resource_data
                )
        
        self.stdout.write(f'创建了 {len(resources_data)} 个学习资源')