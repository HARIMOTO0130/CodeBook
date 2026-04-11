# 数据模型定义

class KnowledgeNode:
    """知识节点模型"""
    def __init__(self, **kwargs):
        self.concept_id = kwargs.get('concept_id')
        self.concept_name = kwargs.get('concept_name')
        self.course_id = kwargs.get('course_id')
        self.prerequisites = kwargs.get('prerequisites', [])
        self.successors = kwargs.get('successors', [])
        self.level = kwargs.get('level', 0)  # 0: 概念层, 1: 分类层, 2: 实体层, 3: 动态层
        self.category = kwargs.get('category')
        self.description = kwargs.get('description')
        self.source = kwargs.get('source')
        self.depth = kwargs.get('depth', 0)
        self.parent_concept = kwargs.get('parent_concept')
        self.keywords = kwargs.get('keywords', [])
        self.difficulty = kwargs.get('difficulty')
        self.importance = kwargs.get('importance', 0)

    def to_dict(self):
        return {
            'concept_id': self.concept_id,
            'concept_name': self.concept_name,
            'course_id': self.course_id,
            'prerequisites': self.prerequisites,
            'successors': self.successors,
            'level': self.level,
            'category': self.category,
            'description': self.description,
            'source': self.source,
            'depth': self.depth,
            'parent_concept': self.parent_concept,
            'keywords': self.keywords,
            'difficulty': self.difficulty,
            'importance': self.importance
        }

class LearningPath:
    """学习路径模型"""
    def __init__(self, **kwargs):
        self.path_id = kwargs.get('path_id')
        self.path_name = kwargs.get('path_name')
        self.description = kwargs.get('description')
        self.nodes = kwargs.get('nodes', [])
        self.difficulty = kwargs.get('difficulty')
        self.estimated_time = kwargs.get('estimated_time')
        self.target_career = kwargs.get('target_career')
        self.source = kwargs.get('source')
        self.created_at = kwargs.get('created_at')

    def to_dict(self):
        return {
            'path_id': self.path_id,
            'path_name': self.path_name,
            'description': self.description,
            'nodes': self.nodes,
            'difficulty': self.difficulty,
            'estimated_time': self.estimated_time,
            'target_career': self.target_career,
            'source': self.source,
            'created_at': self.created_at
        }

class Course:
    """课程模型"""
    def __init__(self, **kwargs):
        self.course_id = kwargs.get('course_id')
        self.course_name = kwargs.get('course_name')
        self.description = kwargs.get('description')
        self.instructor = kwargs.get('instructor')
        self.institution = kwargs.get('institution')
        self.duration = kwargs.get('duration')
        self.difficulty = kwargs.get('difficulty')
        self.rating = kwargs.get('rating')
        self.enrollment_count = kwargs.get('enrollment_count')
        self.start_date = kwargs.get('start_date')
        self.source = kwargs.get('source')
        self.concepts = kwargs.get('concepts', [])

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'description': self.description,
            'instructor': self.instructor,
            'institution': self.institution,
            'duration': self.duration,
            'difficulty': self.difficulty,
            'rating': self.rating,
            'enrollment_count': self.enrollment_count,
            'start_date': self.start_date,
            'source': self.source,
            'concepts': self.concepts
        }

class Resource:
    """学习资源模型"""
    def __init__(self, **kwargs):
        self.resource_id = kwargs.get('resource_id')
        self.title = kwargs.get('title')
        self.url = kwargs.get('url')
        self.type = kwargs.get('type')  # video, article, book, etc.
        self.source = kwargs.get('source')
        self.author = kwargs.get('author')
        self.publish_date = kwargs.get('publish_date')
        self.duration = kwargs.get('duration')
        self.language = kwargs.get('language')
        self.concepts = kwargs.get('concepts', [])

    def to_dict(self):
        return {
            'resource_id': self.resource_id,
            'title': self.title,
            'url': self.url,
            'type': self.type,
            'source': self.source,
            'author': self.author,
            'publish_date': self.publish_date,
            'duration': self.duration,
            'language': self.language,
            'concepts': self.concepts
        }