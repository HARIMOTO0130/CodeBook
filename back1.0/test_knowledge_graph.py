#!/usr/bin/env python
"""测试知识图谱构建功能"""

import os
import sys

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.learning.models import KnowledgeGraph, KnowledgeNode, KnowledgeRelation
from apps.learning.knowledge_graph_engine import KnowledgeGraphEngine

def test_knowledge_graph_building():
    """测试知识图谱构建"""
    print("=== 测试知识图谱构建功能 ===")
    
    # 1. 统计现有节点和关系数量
    all_nodes_count = KnowledgeNode.objects.count()
    all_relations_count = KnowledgeRelation.objects.count()
    print(f"1. 现有节点总数: {all_nodes_count}")
    print(f"1. 现有关系总数: {all_relations_count}")
    
    # 2. 初始化知识图谱引擎
    engine = KnowledgeGraphEngine()
    
    # 3. 构建知识图谱
    print("2. 开始构建知识图谱...")
    graph = engine.build_knowledge_graph()
    
    # 4. 检查图中节点和关系数量
    nodes_in_graph = len(graph.nodes)
    relations_in_graph = len(graph.edges)
    print(f"3. 构建后的知识图谱节点数量: {nodes_in_graph}")
    print(f"3. 构建后的知识图谱关系数量: {relations_in_graph}")
    
    # 5. 验证节点和关系是否正确关联
    if nodes_in_graph > 0 and relations_in_graph > 0:
        print("4. ✅ 测试成功: 知识图谱已正确构建")
    else:
        print("4. ❌ 测试失败: 知识图谱构建失败，节点或关系数量为0")
        
    # 6. 检查数据库中节点的关联情况
    print("5. 检查数据库中节点的关联情况...")
    unlinked_nodes = KnowledgeNode.objects.filter(graph__isnull=True).count()
    unlinked_relations = KnowledgeRelation.objects.filter(graph__isnull=True).count()
    print(f"5. 未关联到图谱的节点数量: {unlinked_nodes}")
    print(f"5. 未关联到图谱的关系数量: {unlinked_relations}")
    
    if unlinked_nodes == 0 and unlinked_relations == 0:
        print("6. ✅ 测试成功: 所有节点和关系都已关联到知识图谱")
    else:
        print("6. ⚠️  警告: 仍有节点或关系未关联到知识图谱")
    
    return nodes_in_graph > 0 and relations_in_graph > 0

if __name__ == "__main__":
    test_knowledge_graph_building()
