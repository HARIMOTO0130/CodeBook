#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化学习路线图数据脚本
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.learning.models import RoadmapTemplate, RoadmapStage, RoadmapBook
from apps.books.models import Book

def create_initial_roadmaps():
    """创建初始学习路线图数据"""
    print("开始创建学习路线图初始数据...")
    
    # 检查是否已有数据
    if RoadmapTemplate.objects.exists():
        print("学习路线图数据已存在，跳过初始化")
        return
    
    # 获取一些示例书籍（如果没有则创建示例书籍）
    def get_or_create_example_books():
        books = []
        book_titles = [
            "Python编程入门",
            "数据分析基础",
            "机器学习实战",
            "Web应用开发",
            "高级算法与数据结构",
            "财务分析与建模",
            "商业智能与决策",
            "市场营销策略",
            "中国文学史",
            "古代文献研究",
            "艺术设计基础",
            "数字媒体创作"
        ]
        
        for title in book_titles:
            book, created = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': '系统示例',
                    'description': f'{title}的示例描述',
                    'chapter_count': 10,
                    'tags': '["示例", "教程"]'
                }
            )
            books.append(book)
        
        return books
    
    books = get_or_create_example_books()
    
    # 1. 经管类路线图
    business_roadmaps = [
        {
            'title': '商业数据分析进阶',
            'description': '从数据分析基础到商业决策支持的完整学习路径，掌握数据驱动的商业分析技能。',
            'major': 'business',
            'difficulty_level': 'intermediate',
            'estimated_hours': 80,
            'tags': ['数据分析', '商业智能', 'Excel', 'Python'],
            'stages': [
                {
                    'title': '数据分析基础',
                    'description': '掌握数据分析的基本概念和工具',
                    'stage_order': 1,
                    'estimated_duration': 20,
                    'learning_goals': [
                        '理解数据类型和统计概念',
                        '掌握Excel数据分析功能',
                        '学习Python基础语法'
                    ],
                    'book_indices': [0, 1]
                },
                {
                    'title': '商业分析方法',
                    'description': '学习商业场景下的数据处理和分析方法',
                    'stage_order': 2,
                    'estimated_duration': 25,
                    'learning_goals': [
                        '掌握数据清洗和预处理技术',
                        '学习数据可视化方法',
                        '理解商业指标和KPI'
                    ],
                    'book_indices': [1, 5]
                },
                {
                    'title': '商业决策支持',
                    'description': '学习如何用数据支持商业决策',
                    'stage_order': 3,
                    'estimated_duration': 35,
                    'learning_goals': [
                        '掌握预测分析技术',
                        '学习业务模型构建',
                        '理解数据驱动决策流程'
                    ],
                    'book_indices': [2, 6]
                }
            ]
        },
        {
            'title': '数字营销全栈',
            'description': '从数字营销基础到高级策略的全面学习路径。',
            'major': 'business',
            'difficulty_level': 'beginner',
            'estimated_hours': 60,
            'tags': ['数字营销', '社交媒体', 'SEO', '内容营销'],
            'stages': [
                {
                    'title': '数字营销基础',
                    'description': '了解数字营销的核心概念和渠道',
                    'stage_order': 1,
                    'estimated_duration': 15,
                    'learning_goals': [
                        '理解数字营销框架',
                        '掌握主要数字营销渠道',
                        '学习营销数据分析基础'
                    ],
                    'book_indices': [6, 7]
                },
                {
                    'title': '内容与社交营销',
                    'description': '深入学习内容创作和社交媒体营销策略',
                    'stage_order': 2,
                    'estimated_duration': 20,
                    'learning_goals': [
                        '掌握内容创作技巧',
                        '学习社交媒体运营策略',
                        '理解用户生成内容管理'
                    ],
                    'book_indices': [7, 11]
                },
                {
                    'title': '营销技术与优化',
                    'description': '学习营销技术工具和效果优化方法',
                    'stage_order': 3,
                    'estimated_duration': 25,
                    'learning_goals': [
                        '掌握SEO和SEM技术',
                        '学习营销自动化工具',
                        '理解A/B测试和优化'
                    ],
                    'book_indices': [3, 7]
                }
            ]
        }
    ]
    
    # 2. 文史类路线图
    humanities_roadmaps = [
        {
            'title': '中国古代文学研究',
            'description': '系统学习中国古代文学的发展历程和代表作品。',
            'major': 'humanities',
            'difficulty_level': 'advanced',
            'estimated_hours': 100,
            'tags': ['古代文学', '文学史', '经典阅读', '文学理论'],
            'stages': [
                {
                    'title': '先秦两汉文学',
                    'description': '学习中国文学的起源和早期发展',
                    'stage_order': 1,
                    'estimated_duration': 30,
                    'learning_goals': [
                        '掌握《诗经》《楚辞》等经典',
                        '理解汉赋的艺术特色',
                        '学习早期文学理论'
                    ],
                    'book_indices': [8, 9]
                },
                {
                    'title': '唐宋文学高峰',
                    'description': '深入学习唐诗宋词等文学巅峰成就',
                    'stage_order': 2,
                    'estimated_duration': 40,
                    'learning_goals': [
                        '掌握唐诗流派和代表诗人',
                        '学习宋词的发展和艺术特色',
                        '理解唐宋散文的成就'
                    ],
                    'book_indices': [8, 9]
                },
                {
                    'title': '元明清文学转型',
                    'description': '学习文学形式的转型和新发展',
                    'stage_order': 3,
                    'estimated_duration': 30,
                    'learning_goals': [
                        '掌握元曲的艺术特色',
                        '学习明清小说的发展',
                        '理解古代文学的现代价值'
                    ],
                    'book_indices': [8, 9]
                }
            ]
        }
    ]
    
    # 3. 艺术类路线图
    arts_roadmaps = [
        {
            'title': '数字艺术创作',
            'description': '从基础设计到数字艺术创作的完整学习路径。',
            'major': 'arts',
            'difficulty_level': 'intermediate',
            'estimated_hours': 70,
            'tags': ['数字艺术', '设计', '创意', '多媒体'],
            'stages': [
                {
                    'title': '设计基础',
                    'description': '学习设计的基本原理和构成',
                    'stage_order': 1,
                    'estimated_duration': 20,
                    'learning_goals': [
                        '理解色彩理论和应用',
                        '掌握排版和布局原则',
                        '学习设计软件基础'
                    ],
                    'book_indices': [10, 11]
                },
                {
                    'title': '数字插画创作',
                    'description': '学习数字插画的创作技巧和风格',
                    'stage_order': 2,
                    'estimated_duration': 25,
                    'learning_goals': [
                        '掌握数字绘画基础',
                        '学习不同风格的插画技巧',
                        '理解角色设计原则'
                    ],
                    'book_indices': [10, 11]
                },
                {
                    'title': '多媒体艺术项目',
                    'description': '综合应用数字艺术技能完成项目',
                    'stage_order': 3,
                    'estimated_duration': 25,
                    'learning_goals': [
                        '掌握多媒体项目规划',
                        '学习跨媒体创作技巧',
                        '理解艺术作品展示和推广'
                    ],
                    'book_indices': [3, 11]
                }
            ]
        }
    ]
    
    # 4. 理工科路线图
    science_roadmaps = [
        {
            'title': 'Python全栈开发',
            'description': '从Python基础到全栈Web开发的系统学习路径。',
            'major': 'science',
            'difficulty_level': 'intermediate',
            'estimated_hours': 90,
            'tags': ['Python', 'Web开发', '全栈', '数据库'],
            'stages': [
                {
                    'title': 'Python编程基础',
                    'description': '掌握Python语言核心概念和编程技巧',
                    'stage_order': 1,
                    'estimated_duration': 25,
                    'learning_goals': [
                        '掌握Python语法和数据结构',
                        '学习面向对象编程',
                        '理解常用算法和设计模式'
                    ],
                    'book_indices': [0, 4]
                },
                {
                    'title': 'Web前端开发',
                    'description': '学习现代Web前端技术栈',
                    'stage_order': 2,
                    'estimated_duration': 30,
                    'learning_goals': [
                        '掌握HTML/CSS基础',
                        '学习JavaScript编程',
                        '理解现代前端框架'
                    ],
                    'book_indices': [3, 0]
                },
                {
                    'title': '后端与数据库',
                    'description': '学习后端开发和数据库设计',
                    'stage_order': 3,
                    'estimated_duration': 35,
                    'learning_goals': [
                        '掌握Python Web框架',
                        '学习数据库设计和SQL',
                        '理解API开发和部署'
                    ],
                    'book_indices': [3, 4]
                }
            ]
        },
        {
            'title': '机器学习工程师',
            'description': '从数据科学基础到机器学习工程的专业学习路径。',
            'major': 'science',
            'difficulty_level': 'advanced',
            'estimated_hours': 120,
            'tags': ['机器学习', '数据科学', 'Python', 'AI'],
            'stages': [
                {
                    'title': '数据科学基础',
                    'description': '学习数据科学的核心概念和工具',
                    'stage_order': 1,
                    'estimated_duration': 35,
                    'learning_goals': [
                        '掌握Python数据处理库',
                        '学习统计学基础',
                        '理解数据可视化技术'
                    ],
                    'book_indices': [1, 2, 0]
                },
                {
                    'title': '机器学习算法',
                    'description': '深入学习各类机器学习算法',
                    'stage_order': 2,
                    'estimated_duration': 45,
                    'learning_goals': [
                        '掌握监督学习算法',
                        '学习无监督学习方法',
                        '理解模型评估和调优'
                    ],
                    'book_indices': [2, 4]
                },
                {
                    'title': '机器学习工程',
                    'description': '学习将机器学习模型部署到生产环境',
                    'stage_order': 3,
                    'estimated_duration': 40,
                    'learning_goals': [
                        '掌握模型部署技术',
                        '学习ML系统设计',
                        '理解MLOps最佳实践'
                    ],
                    'book_indices': [2, 3]
                }
            ]
        }
    ]
    
    # 合并所有路线图
    all_roadmaps = business_roadmaps + humanities_roadmaps + arts_roadmaps + science_roadmaps
    
    # 创建路线图数据
    for roadmap_data in all_roadmaps:
        # 创建路线图模板
        roadmap = RoadmapTemplate.objects.create(
            title=roadmap_data['title'],
            description=roadmap_data['description'],
            major=roadmap_data['major'],
            difficulty_level=roadmap_data['difficulty_level'],
            estimated_hours=roadmap_data['estimated_hours'],
            tags=roadmap_data['tags']
        )
        print(f"创建路线图: {roadmap.title} ({roadmap.major})")
        
        # 创建阶段
        for stage_data in roadmap_data['stages']:
            stage = RoadmapStage.objects.create(
                roadmap=roadmap,
                title=stage_data['title'],
                description=stage_data['description'],
                stage_order=stage_data['stage_order'],
                estimated_duration=stage_data['estimated_duration'],
                learning_goals=stage_data['learning_goals']
            )
            print(f"  - 创建阶段: {stage.title} (第{stage.stage_order}阶段)")
            
            # 创建书籍关联
            for book_idx in stage_data['book_indices']:
                if book_idx < len(books):
                    book = books[book_idx]
                    RoadmapBook.objects.create(
                        stage=stage,
                        book=book
                    )
                    print(f"    * 关联书籍: {book.title}")
    
    print(f"\n初始化完成！成功创建了 {RoadmapTemplate.objects.count()} 个路线图模板")
    print(f"包含 {RoadmapStage.objects.count()} 个学习阶段和 {RoadmapBook.objects.count()} 个书籍关联")

if __name__ == '__main__':
    create_initial_roadmaps()