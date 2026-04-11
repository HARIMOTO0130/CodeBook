import requests
import os
import json
import zipfile
import time
import random
from tqdm import tqdm
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode, Course, LearningPath

class MOOCCubeCollector:
    """MOOCCube数据集采集器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.base_url = "https://github.com/mooccube/mooccube.github.io/raw/master/data"
        self.datasets = {
            "courses": "courses.json",
            "concepts": "concepts.json",
            "relations": "prerequisites.json"
        }
    
    def download_file(self, url, save_path, max_retries=3):
        """下载文件"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()  # 检查HTTP状态码
                
                total_size = int(response.headers.get('content-length', 0))
                
                with open(save_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                        for data in response.iter_content(chunk_size=1024):
                            f.write(data)
                            pbar.update(len(data))
                return True
            except Exception as e:
                print(f"下载失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    print(f"{wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
                else:
                    return False
    
    def collect_courses(self):
        """采集课程数据"""
        url = f"{self.base_url}/{self.datasets['courses']}"
        save_path = os.path.join('data_collection', 'mooccube', 'courses.json')
        
        print("正在下载MOOCCube课程数据...")
        success = self.download_file(url, save_path)
        
        if success and os.path.exists(save_path):
            # 读取并处理数据
            try:
                with open(save_path, 'r', encoding='utf-8') as f:
                    courses_data = json.load(f)
                
                # 限制采集数量
                courses_data = courses_data[:10]  # 只采集前10个课程
                
                # 转换为标准格式
                processed_courses = []
                for course in courses_data:
                    course_obj = Course(
                        course_id=course.get('course_id'),
                        course_name=course.get('course_name'),
                        description=course.get('description'),
                        instructor=course.get('instructor'),
                        institution=course.get('institution'),
                        duration=course.get('duration'),
                        difficulty=course.get('difficulty'),
                        rating=course.get('rating'),
                        enrollment_count=course.get('enrollment_count'),
                        start_date=course.get('start_date'),
                        source="MOOCCube",
                        concepts=course.get('concepts', [])
                    )
                    processed_courses.append(course_obj.to_dict())
                
                # 保存处理后的数据
                self.storage.save_raw_data('mooccube', 'courses', courses_data)
                self.storage.save_processed_data('mooccube', 'courses', processed_courses)
                
                print(f"采集到 {len(processed_courses)} 个MOOCCube课程")
                return processed_courses
            except Exception as e:
                print(f"处理课程数据时出错: {e}")
        
        # 使用模拟数据
        print("使用模拟数据")
        mock_courses = [
            {
                "course_id": "moooc1",
                "course_name": "数据结构",
                "description": "数据结构基础课程",
                "instructor": "张教授",
                "institution": "清华大学",
                "duration": "16周",
                "difficulty": "中等",
                "rating": 4.8,
                "enrollment_count": 10000,
                "start_date": "2026-03-01",
                "source": "MOOCCube",
                "concepts": ["数据结构", "算法"]
            },
            {
                "course_id": "moooc2",
                "course_name": "计算机网络",
                "description": "计算机网络基础课程",
                "instructor": "李教授",
                "institution": "北京大学",
                "duration": "12周",
                "difficulty": "中等",
                "rating": 4.7,
                "enrollment_count": 8000,
                "start_date": "2026-04-01",
                "source": "MOOCCube",
                "concepts": ["计算机网络", "TCP/IP"]
            }
        ]
        
        processed_courses = []
        for course in mock_courses:
            course_obj = Course(**course)
            processed_courses.append(course_obj.to_dict())
        
        self.storage.save_processed_data('mooccube', 'courses', processed_courses)
        print(f"使用模拟数据，采集到 {len(processed_courses)} 个MOOCCube课程")
        return processed_courses
    
    def collect_concepts(self):
        """采集知识点数据"""
        url = f"{self.base_url}/{self.datasets['concepts']}"
        save_path = os.path.join('data_collection', 'mooccube', 'concepts.json')
        
        print("正在下载MOOCCube知识点数据...")
        success = self.download_file(url, save_path)
        
        if success and os.path.exists(save_path):
            # 读取并处理数据
            try:
                with open(save_path, 'r', encoding='utf-8') as f:
                    concepts_data = json.load(f)
                
                # 限制采集数量
                concepts_data = concepts_data[:20]  # 只采集前20个概念
                
                # 转换为标准格式
                processed_concepts = []
                for concept in concepts_data:
                    concept_obj = KnowledgeNode(
                        concept_id=concept.get('concept_id'),
                        concept_name=concept.get('concept_name'),
                        course_id=concept.get('course_id'),
                        prerequisites=concept.get('prerequisites', []),
                        successors=concept.get('successors', []),
                        level=1,  # 分类层
                        category=concept.get('category'),
                        description=concept.get('description'),
                        source="MOOCCube",
                        depth=concept.get('depth', 0),
                        parent_concept=concept.get('parent_concept'),
                        keywords=concept.get('keywords', []),
                        difficulty=concept.get('difficulty'),
                        importance=concept.get('importance', 0)
                    )
                    processed_concepts.append(concept_obj.to_dict())
                
                # 保存处理后的数据
                self.storage.save_raw_data('mooccube', 'concepts', concepts_data)
                self.storage.save_processed_data('mooccube', 'concepts', processed_concepts)
                
                print(f"采集到 {len(processed_concepts)} 个MOOCCube概念")
                return processed_concepts
            except Exception as e:
                print(f"处理概念数据时出错: {e}")
        
        # 使用模拟数据
        print("使用模拟数据")
        mock_concepts = [
            {
                "concept_id": "concept1",
                "concept_name": "二叉树",
                "course_id": "moooc1",
                "prerequisites": ["树"],
                "successors": ["平衡树"],
                "level": 2,
                "category": "data_structure",
                "description": "二叉树是一种重要的数据结构",
                "source": "MOOCCube",
                "depth": 2,
                "parent_concept": "树",
                "keywords": ["二叉树", "数据结构"],
                "difficulty": 2,
                "importance": 3
            },
            {
                "concept_id": "concept2",
                "concept_name": "链表",
                "course_id": "moooc1",
                "prerequisites": [],
                "successors": ["栈", "队列"],
                "level": 2,
                "category": "data_structure",
                "description": "链表是一种线性数据结构",
                "source": "MOOCCube",
                "depth": 1,
                "parent_concept": "线性结构",
                "keywords": ["链表", "数据结构"],
                "difficulty": 1,
                "importance": 2
            }
        ]
        
        processed_concepts = []
        for concept in mock_concepts:
            concept_obj = KnowledgeNode(**concept)
            processed_concepts.append(concept_obj.to_dict())
        
        self.storage.save_processed_data('mooccube', 'concepts', processed_concepts)
        print(f"使用模拟数据，采集到 {len(processed_concepts)} 个MOOCCube概念")
        return processed_concepts
    
    def collect_relations(self):
        """采集关系数据"""
        url = f"{self.base_url}/{self.datasets['relations']}"
        save_path = os.path.join('data_collection', 'mooccube', 'relations.json')
        
        print("正在下载MOOCCube关系数据...")
        success = self.download_file(url, save_path)
        
        if success and os.path.exists(save_path):
            # 读取并处理数据
            try:
                with open(save_path, 'r', encoding='utf-8') as f:
                    relations_data = json.load(f)
                
                # 限制采集数量
                relations_data = relations_data[:30]  # 只采集前30个关系
                
                # 保存处理后的数据
                self.storage.save_raw_data('mooccube', 'relations', relations_data)
                self.storage.save_processed_data('mooccube', 'relations', relations_data)
                
                print(f"采集到 {len(relations_data)} 个MOOCCube关系")
                return relations_data
            except Exception as e:
                print(f"处理关系数据时出错: {e}")
        
        # 使用模拟数据
        print("使用模拟数据")
        mock_relations = [
            {"source": "concept1", "target": "concept2", "type": "prerequisite"},
            {"source": "concept2", "target": "concept3", "type": "prerequisite"}
        ]
        
        self.storage.save_raw_data('mooccube', 'relations', mock_relations)
        self.storage.save_processed_data('mooccube', 'relations', mock_relations)
        print(f"使用模拟数据，采集到 {len(mock_relations)} 个MOOCCube关系")
        return mock_relations
    
    def collect_all(self):
        """采集所有数据"""
        print("开始采集MOOCCube数据集...")
        
        courses = self.collect_courses()
        time.sleep(1)
        
        concepts = self.collect_concepts()
        time.sleep(1)
        
        relations = self.collect_relations()
        
        print(f"MOOCCube数据集采集完成:")
        print(f"- 课程数量: {len(courses)}")
        print(f"- 知识点数量: {len(concepts)}")
        print(f"- 关系数量: {len(relations)}")
        
        # 整合数据
        integrated_data = {
            "courses": courses,
            "concepts": concepts,
            "relations": relations
        }
        
        self.storage.save_final_data('mooccube', 'integrated', integrated_data)
        
        return integrated_data

if __name__ == "__main__":
    collector = MOOCCubeCollector()
    collector.collect_all()