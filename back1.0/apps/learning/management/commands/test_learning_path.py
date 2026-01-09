from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.learning.personalized_learning_path import PersonalizedLearningPathGenerator


class Command(BaseCommand):
    """测试个性化学习路径生成功能的管理命令"""
    help = '测试个性化学习路径生成功能'

    def handle(self, *args, **kwargs):
        """执行命令"""
        self.stdout.write(self.style.SUCCESS('测试个性化学习路径生成功能...'))
        self.stdout.write('=' * 50)

        # 获取用户模型
        User = get_user_model()
        
        # 获取第一个用户
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('找不到用户，请先创建用户'))
            return

        self.stdout.write(f'使用用户: {user.username}')
        self.stdout.write('')

        # 初始化学习路径生成器
        generator = PersonalizedLearningPathGenerator()

        # 测试生成学习路径
        learning_goal = "AI学习"
        max_nodes = 10

        self.stdout.write(f'生成学习路径: {learning_goal} (最大节点数: {max_nodes})')
        try:
            learning_path = generator.generate_learning_path(user, learning_goal, max_nodes)
            
            self.stdout.write(f"\n生成结果:")
            self.stdout.write(f"- 路径节点数: {len(learning_path.get('path', []))}")
            self.stdout.write(f"- 路径解释: {learning_path.get('explanation', '')}")
            self.stdout.write(f"- 学习建议数: {len(learning_path.get('suggestions', []))}")
            
            self.stdout.write(f"\n路径节点:")
            for i, node in enumerate(learning_path.get('path', [])):
                self.stdout.write(f"  {i+1}. {node.get('title')} ({node.get('type')}, 难度: {node.get('difficulty')})")
                self.stdout.write(f"     描述: {node.get('description', '')}")
                
            self.stdout.write(f"\n学习建议:")
            for i, suggestion in enumerate(learning_path.get('suggestions', [])):
                self.stdout.write(f"  {i+1}. {suggestion}")
                
            self.stdout.write(f"\n用户画像:")
            profile = learning_path.get('user_profile', {})
            self.stdout.write(f"  - 专业组: {profile.get('professional_group')}")
            self.stdout.write(f"  - 知识水平: {profile.get('knowledge_level')}")
            self.stdout.write(f"  - 平均掌握度: {profile.get('average_mastery'):.2f}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'生成学习路径失败: {e}'))
            import traceback
            traceback.print_exc()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('测试完成！'))
