from django.contrib.auth import get_user_model
from apps.learning.personalized_learning_path import PersonalizedLearningPathGenerator

# 获取用户模型
User = get_user_model()

print("测试个性化学习路径生成功能...")
print("=" * 50)

# 获取第一个用户
user = User.objects.first()
if not user:
    print("找不到用户，请先创建用户")
    exit(1)

print(f"使用用户: {user.username}")
print()

# 初始化学习路径生成器
generator = PersonalizedLearningPathGenerator()

# 测试生成学习路径
learning_goal = "AI学习"
max_nodes = 10

print(f"生成学习路径: {learning_goal} (最大节点数: {max_nodes})")
try:
    learning_path = generator.generate_learning_path(user, learning_goal, max_nodes)
    
    print(f"\n生成结果:")
    print(f"- 路径节点数: {len(learning_path.get('path', []))}")
    print(f"- 路径解释: {learning_path.get('explanation', '')}")
    print(f"- 学习建议数: {len(learning_path.get('suggestions', []))}")
    
    print(f"\n路径节点:")
    for i, node in enumerate(learning_path.get('path', [])):
        print(f"  {i+1}. {node.get('title')} ({node.get('type')}, 难度: {node.get('difficulty')})")
        print(f"     描述: {node.get('description', '')}")
        
    print(f"\n学习建议:")
    for i, suggestion in enumerate(learning_path.get('suggestions', [])):
        print(f"  {i+1}. {suggestion}")
        
    print(f"\n用户画像:")
    profile = learning_path.get('user_profile', {})
    print(f"  - 专业组: {profile.get('professional_group')}")
    print(f"  - 知识水平: {profile.get('knowledge_level')}")
    print(f"  - 平均掌握度: {profile.get('average_mastery'):.2f}")
    
except Exception as e:
    print(f"生成学习路径失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成！")
