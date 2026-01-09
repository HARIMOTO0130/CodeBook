"""知识图谱构建测试用例"""

import unittest
from django.test import TestCase
from apps.learning.models import KnowledgeGraph, KnowledgeNode, KnowledgeRelation
from apps.learning.knowledge_graph_engine import KnowledgeGraphEngine
from apps.learning.knowledge_graph_auto_builder import KnowledgeGraphAutoBuilder


class TestKnowledgeGraphConstruction(TestCase):
    """知识图谱构建测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建测试知识图谱
        self.graph = KnowledgeGraph.objects.create(
            name="测试知识图谱",
            description="用于测试的知识图谱"
        )
        
        # 创建测试节点
        self.node1 = KnowledgeNode.objects.create(
            graph=self.graph,
            title="机器学习",
            type="concept",
            level=1,
            difficulty=3.0,
            importance=4.0,
            description="机器学习是人工智能的一个分支，让计算机能够从数据中学习",
            professional_group="science",
            tags=["人工智能", "机器学习"]
        )
        
        self.node2 = KnowledgeNode.objects.create(
            graph=self.graph,
            title="监督学习",
            type="concept",
            level=2,
            difficulty=3.5,
            importance=4.5,
            description="监督学习是机器学习的一种方法，使用标记数据进行训练",
            professional_group="science",
            tags=["机器学习", "监督学习"]
        )
        
        self.node3 = KnowledgeNode.objects.create(
            graph=self.graph,
            title="Python编程",
            type="skill",
            level=1,
            difficulty=2.5,
            importance=4.0,
            description="Python是一种广泛使用的编程语言，特别适合机器学习",
            professional_group="science",
            tags=["编程", "Python"]
        )
        
        # 创建测试关系
        self.relation1 = KnowledgeRelation.objects.create(
            graph=self.graph,
            source=self.node1,
            target=self.node2,
            relation_type="prerequisite",
            strength=0.8
        )
        
        self.relation2 = KnowledgeRelation.objects.create(
            graph=self.graph,
            source=self.node3,
            target=self.node1,
            relation_type="application",
            strength=0.9
        )
    
    def test_knowledge_graph_engine_build(self):
        """测试知识图谱引擎构建"""
        engine = KnowledgeGraphEngine()
        graph = engine.build_knowledge_graph(self.graph.id)
        
        # 验证图结构
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
    
    def test_relation_strength_calculation(self):
        """测试关系强度计算"""
        engine = KnowledgeGraphEngine()
        engine.build_knowledge_graph(self.graph.id)
        
        # 验证关系强度是否在合理范围内
        for u, v, data in engine.graph.edges(data=True):
            self.assertGreaterEqual(data['strength'], 0.1)
            self.assertLessEqual(data['strength'], 1.0)
    
    def test_professional_group_specific_graph(self):
        """测试专业组特异性知识图谱"""
        engine = KnowledgeGraphEngine()
        graph = engine.build_knowledge_graph(professional_group='science')
        
        # 验证图结构
        self.assertGreaterEqual(len(graph.nodes), 0)
    
    def test_node_embedding_generation(self):
        """测试节点嵌入生成"""
        engine = KnowledgeGraphEngine()
        engine.build_knowledge_graph(self.graph.id)
        
        # 测试不同方法的嵌入生成
        for method in ['graphsage', 'degree']:
            embeddings = engine.generate_node_embeddings(embedding_dim=64, method=method)
            self.assertEqual(len(embeddings), 3)
            for node_id, embedding in embeddings.items():
                self.assertEqual(len(embedding), 64)
    
    def test_professional_embeddings(self):
        """测试专业组特异性嵌入"""
        engine = KnowledgeGraphEngine()
        engine.build_knowledge_graph(self.graph.id)
        
        embeddings = engine.generate_professional_embeddings('science', embedding_dim=64)
        self.assertEqual(len(embeddings), 3)
    
    def test_knowledge_graph_auto_builder(self):
        """测试知识图谱自动构建器"""
        builder = KnowledgeGraphAutoBuilder(use_llm=False)  # 禁用大模型，避免API调用
        
        # 测试文档构建
        documents = [
            {
                'title': '机器学习入门',
                'content': '机器学习是人工智能的一个分支，让计算机能够从数据中学习。监督学习是机器学习的一种方法，使用标记数据进行训练。Python是一种广泛使用的编程语言，特别适合机器学习。'
            }
        ]
        
        result = builder.build_from_documents(documents, graph_name='测试自动构建图谱')
        
        # 验证构建结果
        self.assertIn('new_entities', result)
        self.assertIn('new_relations', result)
        self.assertGreaterEqual(result['total_entities'], 1)
    
    def test_get_shortest_path(self):
        """测试最短路径获取"""
        engine = KnowledgeGraphEngine()
        engine.build_knowledge_graph(self.graph.id)
        
        # 测试获取最短路径
        path = engine.get_shortest_path(self.node3.id, self.node2.id)
        self.assertIsNotNone(path)
        self.assertIn(self.node3.id, path)
        self.assertIn(self.node2.id, path)
    
    def test_get_related_nodes(self):
        """测试获取相关节点"""
        engine = KnowledgeGraphEngine()
        engine.build_knowledge_graph(self.graph.id)
        
        # 测试获取相关节点
        related_nodes = engine.get_related_nodes(self.node1.id, limit=2)
        self.assertIsInstance(related_nodes, list)
        self.assertLessEqual(len(related_nodes), 2)
    
    def test_node_importance(self):
        """测试节点重要性计算"""
        engine = KnowledgeGraphEngine()
        engine.build_knowledge_graph(self.graph.id)
        
        # 测试获取节点重要性
        importance = engine.get_node_importance(self.node1.id)
        self.assertGreaterEqual(importance, 0.0)


class TestKnowledgeGraphModels(TestCase):
    """知识图谱模型测试"""
    
    def test_knowledge_node_creation(self):
        """测试知识节点创建"""
        graph = KnowledgeGraph.objects.create(
            name="测试模型图谱",
            description="用于测试模型的知识图谱"
        )
        
        node = KnowledgeNode.objects.create(
            graph=graph,
            title="测试节点",
            type="concept",
            level=1,
            difficulty=3.0,
            importance=4.0,
            description="测试节点描述",
            professional_group="science",
            tags=["测试", "节点"]
        )
        
        # 验证节点创建
        self.assertEqual(node.title, "测试节点")
        self.assertEqual(node.type, "concept")
        self.assertEqual(node.professional_group, "science")
    
    def test_knowledge_relation_creation(self):
        """测试知识关系创建"""
        graph = KnowledgeGraph.objects.create(
            name="测试关系图谱",
            description="用于测试关系的知识图谱"
        )
        
        node1 = KnowledgeNode.objects.create(
            graph=graph,
            title="节点1",
            type="concept",
            level=1,
            difficulty=3.0,
            importance=4.0,
            description="节点1描述",
            professional_group="science",
            tags=["节点1"]
        )
        
        node2 = KnowledgeNode.objects.create(
            graph=graph,
            title="节点2",
            type="concept",
            level=2,
            difficulty=3.5,
            importance=4.5,
            description="节点2描述",
            professional_group="science",
            tags=["节点2"]
        )
        
        relation = KnowledgeRelation.objects.create(
            graph=graph,
            source=node1,
            target=node2,
            relation_type="prerequisite",
            strength=0.8
        )
        
        # 验证关系创建
        self.assertEqual(relation.source, node1)
        self.assertEqual(relation.target, node2)
        self.assertEqual(relation.relation_type, "prerequisite")
        self.assertEqual(relation.strength, 0.8)


if __name__ == '__main__':
    unittest.main()