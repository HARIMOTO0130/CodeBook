#!/usr/bin/env python3
"""
初始化数据脚本 - 填充基础的计算机科学知识点和学习路径
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_collection.storage.storage_manager import StorageManager

def create_initial_data():
    """创建初始化数据"""
    print("创建初始化数据...")
    
    storage = StorageManager()
    
    # 1. 基础知识点数据
    basic_concepts = [
        {
            "concept_id": "cs001",
            "concept_name": "计算机基础",
            "level": 0,
            "category": "基础理论",
            "description": "计算机科学的基本概念和原理",
            "source": "初始化数据",
            "difficulty": "入门",
            "importance": 5,
            "prerequisites": [],
            "successors": ["cs002", "cs003"]
        },
        {
            "concept_id": "cs002",
            "concept_name": "编程语言",
            "level": 1,
            "category": "核心技能",
            "description": "编程基础和语言学习",
            "source": "初始化数据",
            "difficulty": "入门",
            "importance": 5,
            "prerequisites": ["cs001"],
            "successors": ["cs004", "cs005"]
        },
        {
            "concept_id": "cs003",
            "concept_name": "数据结构",
            "level": 1,
            "category": "核心技能",
            "description": "数据组织和存储的基本结构",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 5,
            "prerequisites": ["cs001"],
            "successors": ["cs006", "cs007"]
        },
        {
            "concept_id": "cs004",
            "concept_name": "Python",
            "level": 2,
            "category": "编程语言",
            "description": "Python编程语言",
            "source": "初始化数据",
            "difficulty": "入门",
            "importance": 5,
            "prerequisites": ["cs002"],
            "successors": ["cs008", "cs009"]
        },
        {
            "concept_id": "cs005",
            "concept_name": "Java",
            "level": 2,
            "category": "编程语言",
            "description": "Java编程语言",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 4,
            "prerequisites": ["cs002"],
            "successors": ["cs010"]
        },
        {
            "concept_id": "cs006",
            "concept_name": "算法",
            "level": 2,
            "category": "核心技能",
            "description": "算法设计与分析",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 5,
            "prerequisites": ["cs003"],
            "successors": ["cs011", "cs012"]
        },
        {
            "concept_id": "cs007",
            "concept_name": "数据库",
            "level": 2,
            "category": "核心技能",
            "description": "数据库原理与应用",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 4,
            "prerequisites": ["cs003"],
            "successors": ["cs013"]
        },
        {
            "concept_id": "cs008",
            "concept_name": "Web开发",
            "level": 3,
            "category": "应用技能",
            "description": "Web应用开发",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 4,
            "prerequisites": ["cs004"],
            "successors": ["cs014"]
        },
        {
            "concept_id": "cs009",
            "concept_name": "数据科学",
            "level": 3,
            "category": "应用技能",
            "description": "数据分析与机器学习",
            "source": "初始化数据",
            "difficulty": "高级",
            "importance": 4,
            "prerequisites": ["cs004", "cs006"],
            "successors": ["cs015"]
        },
        {
            "concept_id": "cs010",
            "concept_name": "后端开发",
            "level": 3,
            "category": "应用技能",
            "description": "服务器端应用开发",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 4,
            "prerequisites": ["cs005", "cs007"],
            "successors": ["cs014"]
        },
        {
            "concept_id": "cs011",
            "concept_name": "排序算法",
            "level": 3,
            "category": "算法",
            "description": "各种排序算法的实现与分析",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 3,
            "prerequisites": ["cs006"],
            "successors": []
        },
        {
            "concept_id": "cs012",
            "concept_name": "搜索算法",
            "level": 3,
            "category": "算法",
            "description": "各种搜索算法的实现与分析",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 3,
            "prerequisites": ["cs006"],
            "successors": []
        },
        {
            "concept_id": "cs013",
            "concept_name": "SQL",
            "level": 3,
            "category": "数据库",
            "description": "SQL语言与数据库操作",
            "source": "初始化数据",
            "difficulty": "中级",
            "importance": 4,
            "prerequisites": ["cs007"],
            "successors": []
        },
        {
            "concept_id": "cs014",
            "concept_name": "全栈开发",
            "level": 4,
            "category": "应用技能",
            "description": "前后端一体化开发",
            "source": "初始化数据",
            "difficulty": "高级",
            "importance": 4,
            "prerequisites": ["cs008", "cs010"],
            "successors": []
        },
        {
            "concept_id": "cs015",
            "concept_name": "机器学习",
            "level": 4,
            "category": "应用技能",
            "description": "机器学习算法与应用",
            "source": "初始化数据",
            "difficulty": "高级",
            "importance": 5,
            "prerequisites": ["cs009"],
            "successors": []
        }
    ]
    
    # 2. 学习路径数据
    learning_paths = [
        {
            "path_id": "path001",
            "path_name": "Python全栈开发",
            "description": "从Python基础到全栈开发的完整学习路径",
            "nodes": ["cs001", "cs002", "cs004", "cs008", "cs014"],
            "difficulty": "中级",
            "estimated_time": "6个月",
            "target_career": "全栈工程师",
            "source": "初始化数据",
            "created_at": datetime.now().isoformat()
        },
        {
            "path_id": "path002",
            "path_name": "数据科学与机器学习",
            "description": "从Python基础到机器学习的完整学习路径",
            "nodes": ["cs001", "cs002", "cs004", "cs003", "cs006", "cs009", "cs015"],
            "difficulty": "高级",
            "estimated_time": "8个月",
            "target_career": "数据科学家",
            "source": "初始化数据",
            "created_at": datetime.now().isoformat()
        },
        {
            "path_id": "path003",
            "path_name": "Java后端开发",
            "description": "从Java基础到后端开发的完整学习路径",
            "nodes": ["cs001", "cs002", "cs005", "cs003", "cs007", "cs010"],
            "difficulty": "中级",
            "estimated_time": "7个月",
            "target_career": "后端工程师",
            "source": "初始化数据",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    # 3. 课程数据
    courses = [
        {
            "course_id": "course001",
            "course_name": "Python编程基础",
            "description": "Python语言的基础语法和编程技巧",
            "instructor": "张教授",
            "institution": "北京大学",
            "duration": "8周",
            "difficulty": "入门",
            "rating": 4.8,
            "enrollment_count": 10000,
            "source": "初始化数据",
            "concepts": ["cs004"]
        },
        {
            "course_id": "course002",
            "course_name": "数据结构与算法",
            "description": "数据结构和算法的基本原理与实现",
            "instructor": "李教授",
            "institution": "清华大学",
            "duration": "12周",
            "difficulty": "中级",
            "rating": 4.7,
            "enrollment_count": 8000,
            "source": "初始化数据",
            "concepts": ["cs003", "cs006"]
        },
        {
            "course_id": "course003",
            "course_name": "Web开发实战",
            "description": "使用Python进行Web应用开发",
            "instructor": "王老师",
            "institution": "复旦大学",
            "duration": "10周",
            "difficulty": "中级",
            "rating": 4.6,
            "enrollment_count": 6000,
            "source": "初始化数据",
            "concepts": ["cs008"]
        }
    ]
    
    # 4. 资源数据
    resources = [
        {
            "resource_id": "res001",
            "title": "Python官方文档",
            "url": "https://docs.python.org/3/",
            "type": "文档",
            "source": "Python.org",
            "concepts": ["cs004"]
        },
        {
            "resource_id": "res002",
            "title": "数据结构与算法分析",
            "url": "https://book.douban.com/subject/1139426/",
            "type": "书籍",
            "source": "豆瓣读书",
            "concepts": ["cs003", "cs006"]
        },
        {
            "resource_id": "res003",
            "title": "Web开发教程",
            "url": "https://developer.mozilla.org/zh-CN/docs/Web",
            "type": "教程",
            "source": "MDN",
            "concepts": ["cs008"]
        }
    ]
    
    # 5. 关系数据
    relations = []
    for concept in basic_concepts:
        # 前置关系
        for prereq_id in concept.get('prerequisites', []):
            relations.append({
                'subject_id': concept['concept_id'],
                'subject_name': concept['concept_name'],
                'predicate': 'requires',
                'object_id': prereq_id,
                'object_name': next((c['concept_name'] for c in basic_concepts if c['concept_id'] == prereq_id), ''),
                'source': '初始化数据'
            })
        # 后继关系
        for successor_id in concept.get('successors', []):
            relations.append({
                'subject_id': concept['concept_id'],
                'subject_name': concept['concept_name'],
                'predicate': 'leads_to',
                'object_id': successor_id,
                'object_name': next((c['concept_name'] for c in basic_concepts if c['concept_id'] == successor_id), ''),
                'source': '初始化数据'
            })
    
    # 保存数据
    storage.save_final_data('init', 'concepts', basic_concepts)
    storage.save_final_data('init', 'learning_paths', learning_paths)
    storage.save_final_data('init', 'courses', courses)
    storage.save_final_data('init', 'resources', resources)
    storage.save_final_data('init', 'relations', relations)
    
    # 生成整合数据
    integrated_data = {
        'concepts': basic_concepts,
        'relations': relations,
        'courses': courses,
        'resources': resources,
        'metadata': {
            'total_concepts': len(basic_concepts),
            'total_relations': len(relations),
            'total_courses': len(courses),
            'total_resources': len(resources),
            'integration_time': datetime.now().isoformat(),
            'sources': ['初始化数据']
        }
    }
    
    storage.save_final_data('integrated', 'knowledge_graph', integrated_data)
    
    # 导出到StrategyKG
    strategy_kg_data = {
        'nodes': basic_concepts,
        'relations': relations,
        'courses': courses,
        'resources': resources,
        'metadata': integrated_data['metadata']
    }
    
    storage.save_final_data('strategy_kg', 'export_data', strategy_kg_data)
    
    print("初始化数据创建完成！")
    print(f"创建了 {len(basic_concepts)} 个知识点")
    print(f"创建了 {len(relations)} 个关系")
    print(f"创建了 {len(learning_paths)} 个学习路径")
    print(f"创建了 {len(courses)} 个课程")
    print(f"创建了 {len(resources)} 个资源")

if __name__ == "__main__":
    create_initial_data()
