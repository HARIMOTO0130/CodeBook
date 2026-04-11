import os
import json
import hashlib
from datetime import datetime
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.quality_control import DataQualityController

class DataIntegrationManager:
    """数据整合管理器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.quality_controller = DataQualityController()
    
    def load_processed_data(self, source):
        """加载处理后的数据"""
        files = self.storage.list_files('processed')
        
        data = {}
        for file in files:
            # 获取文件名（不含路径）
            filename = file.split('/')[-1]
            
            # 对于教育平台，需要特殊处理
            if source == 'education_platforms':
                # 教育平台数据包括coursera、edx、bilibili、leetcode
                if any(prefix in filename for prefix in ['coursera_', 'edx_', 'bilibili_', 'leetcode_']):
                    # 提取平台名称
                    base_name = filename.replace('.json', '')
                    platform = base_name.split('_')[0]
                    data_type = '_'.join(base_name.split('_')[1:])
                    key = f"{platform}_{data_type}"
                    file_path = os.path.join(self.storage.base_path, file)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data[key] = json.load(f)
            else:
                # 其他数据源
                if filename.startswith(f'{source}_'):
                    base_name = filename.replace(f'{source}_', '').replace('.json', '')
                    file_path = os.path.join(self.storage.base_path, file)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data[base_name] = json.load(f)
        
        return data
    
    def merge_concepts(self, concepts_list):
        """合并知识点数据"""
        merged_concepts = []
        concept_map = {}
        
        for concepts in concepts_list:
            if not concepts:
                continue
            
            for concept in concepts:
                # 生成唯一标识
                concept_key = self._generate_concept_key(concept)
                
                if concept_key not in concept_map:
                    # 新概念，添加到映射
                    concept_map[concept_key] = concept
                else:
                    # 已有概念，合并信息
                    existing_concept = concept_map[concept_key]
                    
                    # 合并前置依赖和后继节点
                    if 'prerequisites' in concept:
                        existing_concept['prerequisites'] = list(set(existing_concept.get('prerequisites', []) + concept['prerequisites']))
                    if 'successors' in concept:
                        existing_concept['successors'] = list(set(existing_concept.get('successors', []) + concept['successors']))
                    
                    # 合并关键词
                    if 'keywords' in concept:
                        existing_concept['keywords'] = list(set(existing_concept.get('keywords', []) + concept['keywords']))
                    
                    # 合并描述
                    if 'description' in concept and concept['description']:
                        if not existing_concept.get('description'):
                            existing_concept['description'] = concept['description']
                        elif concept['description'] not in existing_concept['description']:
                            existing_concept['description'] += f"\n{concept['description']}"
                    
                    # 合并来源
                    if 'source' in concept:
                        if isinstance(existing_concept.get('source'), list):
                            if concept['source'] not in existing_concept['source']:
                                existing_concept['source'].append(concept['source'])
                        else:
                            existing_concept['source'] = [existing_concept.get('source'), concept['source']]
        
        # 转换为列表
        for concept in concept_map.values():
            merged_concepts.append(concept)
        
        return merged_concepts
    
    def _generate_concept_key(self, concept):
        """生成概念的唯一标识"""
        name = concept.get('concept_name', '').lower().strip()
        category = concept.get('category', '').lower().strip()
        key = f"{name}_{category}"
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def build_relations(self, concepts):
        """构建知识点之间的关系"""
        relations = []
        concept_id_map = {}
        
        # 构建概念ID映射
        for concept in concepts:
            if 'concept_id' in concept:
                concept_id_map[concept['concept_id']] = concept
        
        # 构建关系
        for concept in concepts:
            concept_id = concept.get('concept_id')
            
            # 处理前置依赖关系
            for prereq_id in concept.get('prerequisites', []):
                if prereq_id in concept_id_map:
                    relation = {
                        'subject_id': concept_id,
                        'subject_name': concept.get('concept_name'),
                        'predicate': 'requires',
                        'object_id': prereq_id,
                        'object_name': concept_id_map[prereq_id].get('concept_name'),
                        'source': concept.get('source')
                    }
                    relations.append(relation)
            
            # 处理后继关系
            for successor_id in concept.get('successors', []):
                if successor_id in concept_id_map:
                    relation = {
                        'subject_id': concept_id,
                        'subject_name': concept.get('concept_name'),
                        'predicate': 'leads_to',
                        'object_id': successor_id,
                        'object_name': concept_id_map[successor_id].get('concept_name'),
                        'source': concept.get('source')
                    }
                    relations.append(relation)
        
        return relations
    
    def integrate_data(self):
        """整合所有数据源的数据"""
        print("开始整合数据...")
        
        # 加载各个数据源的处理后数据
        mooccube_data = self.load_processed_data('mooccube')
        wikidata_data = self.load_processed_data('wikidata')
        dbpedia_data = self.load_processed_data('dbpedia')
        education_data = self.load_processed_data('education_platforms')
        textbooks_data = self.load_processed_data('textbooks')
        
        # 收集所有知识点数据
        concepts_list = []
        
        # MOOCCube知识点
        if 'concepts' in mooccube_data:
            concepts_list.append(mooccube_data['concepts'])
        
        # Wikidata数据
        if 'programming_languages' in wikidata_data:
            concepts_list.append(wikidata_data['programming_languages'])
        if 'algorithms' in wikidata_data:
            concepts_list.append(wikidata_data['algorithms'])
        if 'computer_science_topics' in wikidata_data:
            concepts_list.append(wikidata_data['computer_science_topics'])
        
        # DBpedia数据
        if 'computer_science_concepts' in dbpedia_data:
            concepts_list.append(dbpedia_data['computer_science_concepts'])
        if 'courses' in dbpedia_data:
            concepts_list.append(dbpedia_data['courses'])
        
        # 教育平台数据
        if 'leetcode_problems' in education_data:
            concepts_list.append(education_data['leetcode_problems'])
        
        # 教材数据
        for key, value in textbooks_data.items():
            if isinstance(value, list):
                concepts_list.append(value)
        
        # 合并知识点
        merged_concepts = self.merge_concepts(concepts_list)
        print(f"合并后知识点数量: {len(merged_concepts)}")
        
        # 构建关系
        relations = self.build_relations(merged_concepts)
        print(f"构建关系数量: {len(relations)}")
        
        # 收集课程数据
        courses = []
        if 'courses' in mooccube_data:
            courses.extend(mooccube_data['courses'])
        if 'coursera_courses' in education_data:
            courses.extend(education_data['coursera_courses'])
        if 'edx_courses' in education_data:
            courses.extend(education_data['edx_courses'])
        
        # 收集资源数据
        resources = []
        if 'bilibili_videos' in education_data:
            resources.extend(education_data['bilibili_videos'])
        
        # 数据质量控制
        quality_controller = DataQualityController()
        
        # 处理知识点数据
        processed_concepts, concept_errors = quality_controller.process_dataset(merged_concepts, 'node')
        print(f"处理后知识点数量: {len(processed_concepts)}")
        print(f"知识点错误数量: {len(concept_errors)}")
        
        # 处理课程数据
        processed_courses, course_errors = quality_controller.process_dataset(courses, 'course')
        print(f"处理后课程数量: {len(processed_courses)}")
        print(f"课程错误数量: {len(course_errors)}")
        
        # 处理资源数据
        processed_resources, resource_errors = quality_controller.process_dataset(resources, 'resource')
        print(f"处理后资源数量: {len(processed_resources)}")
        print(f"资源错误数量: {len(resource_errors)}")
        
        # 生成整合数据
        integrated_data = {
            'concepts': processed_concepts,
            'relations': relations,
            'courses': processed_courses,
            'resources': processed_resources,
            'metadata': {
                'total_concepts': len(processed_concepts),
                'total_relations': len(relations),
                'total_courses': len(processed_courses),
                'total_resources': len(processed_resources),
                'integration_time': datetime.now().isoformat(),
                'sources': ['MOOCCube', 'Wikidata', 'DBpedia', 'Coursera', 'edX', 'Bilibili', 'LeetCode', 'Textbooks']
            }
        }
        
        # 保存整合数据
        self.storage.save_final_data('integrated', 'knowledge_graph', integrated_data)
        
        # 生成质量报告
        concept_report = quality_controller.generate_quality_report(merged_concepts, 'node')
        course_report = quality_controller.generate_quality_report(courses, 'course')
        resource_report = quality_controller.generate_quality_report(resources, 'resource')
        
        quality_report = {
            'concepts': concept_report,
            'courses': course_report,
            'resources': resource_report,
            'timestamp': datetime.now().isoformat()
        }
        
        self.storage.save_final_data('integrated', 'quality_report', quality_report)
        
        print("数据整合完成")
        return integrated_data
    
    def export_to_strategy_kg(self):
        """导出数据到StrategyKG系统"""
        # 加载整合数据
        integrated_data = self.storage.load_data('integrated', 'final', 'knowledge_graph')
        
        if not integrated_data:
            print("没有整合数据可导出")
            return
        
        # 转换为StrategyKG格式
        strategy_kg_data = {
            'nodes': integrated_data.get('concepts', []),
            'relations': integrated_data.get('relations', []),
            'courses': integrated_data.get('courses', []),
            'resources': integrated_data.get('resources', []),
            'metadata': integrated_data.get('metadata', {})
        }
        
        # 保存导出数据
        self.storage.save_final_data('strategy_kg', 'export_data', strategy_kg_data)
        
        print("数据导出到StrategyKG完成")
        return strategy_kg_data

if __name__ == "__main__":
    manager = DataIntegrationManager()
    integrated_data = manager.integrate_data()
    manager.export_to_strategy_kg()