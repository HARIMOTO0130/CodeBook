# -*- coding: utf-8 -*-
"""初始化审核系统数据命令"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from apps.users.models import User, ReviewerProfile
from apps.review.models import ReviewRuleConfig


class Command(BaseCommand):
    help = '初始化审核系统数据，包括默认审核员账号和规则配置'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化审核系统数据...')
        
        self._create_groups()
        self._create_default_user()
        self._create_review_rules()
        
        self.stdout.write(self.style.SUCCESS('审核系统数据初始化完成！'))
    
    def _create_groups(self):
        """创建用户组"""
        groups_data = {
            'reviewer': '审核员',
            'senior_reviewer': '高级审核员',
            'review_admin': '审核管理员',
        }
        
        for name, description in groups_data.items():
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'  创建用户组: {description}')
    
    def _create_default_user(self):
        """创建默认审核员账号"""
        username = 'check'
        password = '123456'
        email = 'check@review.com'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'  用户 {username} 已存在，跳过创建')
            return
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='reviewer',
            nickname='审核员',
            department='审核部'
        )
        
        ReviewerProfile.objects.create(
            user=user,
            position='审核员',
            review_quota=50,
            specialty_areas=['计算机科学', '编程基础'],
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'  创建默认审核员账号: {username}'))
        self.stdout.write(f'    密码: {password}')
        self.stdout.write(f'    邮箱: {email}')
    
    def _create_review_rules(self):
        """创建审核规则配置"""
        rules = [
            {
                'rule_name': '内容合规性检查',
                'rule_type': 'content',
                'description': '检查教材内容是否符合法律法规和道德规范',
                'rule_config': {
                    'check_political': True,
                    'check_violence': True,
                    'check_pornography': True,
                    'check_discrimination': True,
                },
                'priority': 10,
            },
            {
                'rule_name': '准确性检查',
                'rule_type': 'content',
                'description': '检查知识点和代码的准确性',
                'rule_config': {
                    'check_code_execution': True,
                    'check_knowledge_accuracy': True,
                    'check_reference_validity': True,
                },
                'priority': 9,
            },
            {
                'rule_name': '格式规范检查',
                'rule_type': 'format',
                'description': '检查教材格式是否符合规范',
                'rule_config': {
                    'check_markdown': True,
                    'check_code_block': True,
                    'check_image_quality': True,
                    'min_image_dpi': 150,
                },
                'priority': 5,
            },
            {
                'rule_name': 'AI审核配置',
                'rule_type': 'ai',
                'description': 'AI审核模型配置',
                'rule_config': {
                    'model': 'doubao',
                    'max_tokens': 4096,
                    'temperature': 0.3,
                    'timeout': 120,
                },
                'priority': 1,
            },
        ]
        
        for rule_data in rules:
            rule, created = ReviewRuleConfig.objects.get_or_create(
                rule_name=rule_data['rule_name'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f"  创建规则: {rule_data['rule_name']}")
