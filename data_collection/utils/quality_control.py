import re
import json
import time
from datetime import datetime
from data_collection.config.config import QUALITY_CONFIG

class DataQualityController:
    """数据质量控制器"""
    
    def __init__(self):
        self.required_fields = QUALITY_CONFIG['validation']['required_fields']
        self.min_confidence = QUALITY_CONFIG['validation']['min_confidence']
    
    def validate_node(self, node):
        """验证知识节点数据"""
        # 检查必填字段
        for field in self.required_fields:
            if field not in node or not node[field]:
                return False, f"缺少必填字段: {field}"
        
        # 验证概念ID格式
        if not isinstance(node.get('concept_id'), str) or not node['concept_id']:
            return False, "概念ID格式不正确"
        
        # 验证概念名称
        if not isinstance(node.get('concept_name'), str) or not node['concept_name']:
            return False, "概念名称格式不正确"
        
        # 验证层级
        level = node.get('level', 0)
        if not isinstance(level, int) or level < 0 or level > 3:
            return False, "层级值超出范围"
        
        # 验证前置依赖和后继节点
        if not isinstance(node.get('prerequisites'), list):
            return False, "前置依赖必须是列表"
        if not isinstance(node.get('successors'), list):
            return False, "后继节点必须是列表"
        
        return True, "验证通过"
    
    def clean_text(self, text):
        """清洗文本数据"""
        if not text:
            return ""
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 去除首尾空格
        text = text.strip()
        
        # 修复编码问题
        try:
            text = text.encode('utf-8').decode('utf-8')
        except:
            pass
        
        return text
    
    def normalize_name(self, name):
        """标准化名称"""
        if not name:
            return ""
        
        # 转换为小写
        name = name.lower()
        
        # 去除特殊字符
        name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\s]', '', name)
        
        # 去除多余空格
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    def remove_duplicates(self, items, key_field='concept_id'):
        """移除重复数据"""
        seen = set()
        unique_items = []
        
        for item in items:
            key = item.get(key_field)
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def validate_course(self, course):
        """验证课程数据"""
        required_fields = ['course_id', 'course_name', 'source']
        
        for field in required_fields:
            if field not in course or not course[field]:
                return False, f"缺少必填字段: {field}"
        
        return True, "验证通过"
    
    def validate_resource(self, resource):
        """验证资源数据"""
        required_fields = ['resource_id', 'title', 'url', 'type', 'source']
        
        for field in required_fields:
            if field not in resource or not resource[field]:
                return False, f"缺少必填字段: {field}"
        
        # 验证URL格式
        if not re.match(r'^https?://', resource.get('url', '')):
            return False, "URL格式不正确"
        
        return True, "验证通过"
    
    def clean_node(self, node):
        """清洗知识节点数据"""
        # 清洗文本字段
        text_fields = ['concept_name', 'description', 'category', 'source']
        for field in text_fields:
            if field in node:
                node[field] = self.clean_text(node[field])
        
        # 标准化名称
        if 'concept_name' in node:
            node['concept_name'] = self.normalize_name(node['concept_name'])
        
        # 确保列表字段
        list_fields = ['prerequisites', 'successors', 'keywords']
        for field in list_fields:
            if field not in node:
                node[field] = []
            elif not isinstance(node[field], list):
                node[field] = [node[field]]
        
        # 确保数值字段
        num_fields = ['level', 'depth', 'difficulty', 'importance']
        for field in num_fields:
            if field in node:
                try:
                    node[field] = float(node[field]) if '.' in str(node[field]) else int(node[field])
                except:
                    node[field] = 0
        
        return node
    
    def clean_course(self, course):
        """清洗课程数据"""
        # 清洗文本字段
        text_fields = ['course_name', 'description', 'instructor', 'institution', 'source']
        for field in text_fields:
            if field in course:
                course[field] = self.clean_text(course[field])
        
        # 确保列表字段
        if 'concepts' not in course:
            course['concepts'] = []
        elif not isinstance(course['concepts'], list):
            course['concepts'] = [course['concepts']]
        
        # 确保数值字段
        num_fields = ['rating', 'enrollment_count']
        for field in num_fields:
            if field in course:
                try:
                    course[field] = float(course[field]) if '.' in str(course[field]) else int(course[field])
                except:
                    course[field] = 0
        
        return course
    
    def clean_resource(self, resource):
        """清洗资源数据"""
        # 清洗文本字段
        text_fields = ['title', 'url', 'type', 'source', 'author', 'language']
        for field in text_fields:
            if field in resource:
                resource[field] = self.clean_text(resource[field])
        
        # 确保列表字段
        if 'concepts' not in resource:
            resource['concepts'] = []
        elif not isinstance(resource['concepts'], list):
            resource['concepts'] = [resource['concepts']]
        
        return resource
    
    def process_dataset(self, dataset, data_type='node'):
        """处理整个数据集"""
        if not isinstance(dataset, list):
            return []
        
        processed_data = []
        errors = []
        
        for item in dataset:
            # 清洗数据
            if data_type == 'node':
                cleaned_item = self.clean_node(item)
                valid, message = self.validate_node(cleaned_item)
            elif data_type == 'course':
                cleaned_item = self.clean_course(item)
                valid, message = self.validate_course(cleaned_item)
            elif data_type == 'resource':
                cleaned_item = self.clean_resource(item)
                valid, message = self.validate_resource(cleaned_item)
            else:
                continue
            
            if valid:
                processed_data.append(cleaned_item)
            else:
                errors.append({'item': item, 'error': message})
        
        # 移除重复数据
        if data_type == 'node':
            processed_data = self.remove_duplicates(processed_data, 'concept_id')
        elif data_type == 'course':
            processed_data = self.remove_duplicates(processed_data, 'course_id')
        elif data_type == 'resource':
            processed_data = self.remove_duplicates(processed_data, 'resource_id')
        
        return processed_data, errors
    
    def generate_quality_report(self, dataset, data_type='node'):
        """生成质量报告"""
        processed_data, errors = self.process_dataset(dataset, data_type)
        
        report = {
            'original_count': len(dataset),
            'processed_count': len(processed_data),
            'error_count': len(errors),
            'error_rate': len(errors) / len(dataset) if dataset else 0,
            'success_rate': len(processed_data) / len(dataset) if dataset else 0,
            'errors': errors[:10],  # 只显示前10个错误
            'timestamp': datetime.now().isoformat()
        }
        
        return report

if __name__ == "__main__":
    # 测试数据质量控制
    test_nodes = [
        {
            "concept_id": "CS101",
            "concept_name": "   Binary Search   ",
            "course_id": "C_Algorithm",
            "prerequisites": ["Array", "Time Complexity"],
            "successors": ["Binary Search Tree", "Graph Search"],
            "level": 2,
            "description": "Binary search is an efficient algorithm for finding an item from a sorted list of items."
        },
        {
            "concept_id": "CS102",
            "concept_name": "   Sorting Algorithms   ",
            "course_id": "C_Algorithm",
            "prerequisites": ["Array"],
            "successors": ["Binary Search"],
            "level": 2,
            "description": "Sorting algorithms are algorithms that put elements of a list in a certain order."
        }
    ]
    
    controller = DataQualityController()
    report = controller.generate_quality_report(test_nodes, 'node')
    print(json.dumps(report, ensure_ascii=False, indent=2))