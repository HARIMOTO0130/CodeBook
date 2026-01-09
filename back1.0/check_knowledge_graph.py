from django.contrib.auth import get_user_model
from apps.learning.models import KnowledgeNode, KnowledgeRelation, KnowledgeGraph

# 获取用户模型
User = get_user_model()

print("知识图谱数据检查：")
print("=" * 50)

# 检查知识图谱数量
graphs = KnowledgeGraph.objects.all()
print(f"知识图谱数量: {graphs.count()}")
for graph in graphs:
    print(f"  - {graph.name}: {graph.description}")

print()

# 检查知识节点数量
nodes = KnowledgeNode.objects.all()
print(f"知识节点数量: {nodes.count()}")
if nodes.count() > 0:
    print("示例节点：")
    for node in nodes[:5]:
        print(f"  - {node.title} ({node.type}, 层级: {node.level}, 难度: {node.difficulty})")

print()

# 检查知识关系数量
relations = KnowledgeRelation.objects.all()
print(f"知识关系数量: {relations.count()}")
if relations.count() > 0:
    print("示例关系：")
    for relation in relations[:5]:
        print(f"  - {relation.source.title} -> {relation.target.title} ({relation.relation_type}, 强度: {relation.strength})")

print()

# 检查默认图谱的节点和关系
print("默认知识图谱详情：")
default_graph = KnowledgeGraph.objects.filter(is_active=True).first()
if default_graph:
    default_nodes = KnowledgeNode.objects.filter(graph=default_graph)
    default_relations = KnowledgeRelation.objects.filter(graph=default_graph)
    print(f"  节点数量: {default_nodes.count()}")
    print(f"  关系数量: {default_relations.count()}")

print()
print("检查完成！")
