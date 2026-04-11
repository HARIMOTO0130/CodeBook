import requests
import json
import time
import random
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode

class WikidataCollector:
    """Wikidata数据采集器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.sparql_endpoint = "https://query.wikidata.org/sparql"
        self.user_agent = "StrategyKG Data Collector"
    
    def execute_sparql_query(self, query, max_retries=3):
        """执行SPARQL查询"""
        for attempt in range(max_retries):
            try:
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "application/sparql-results+json"
                }
                params = {"query": query}
                
                response = requests.get(self.sparql_endpoint, headers=headers, params=params, timeout=30)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"SPARQL查询失败: {response.status_code}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt + random.uniform(0, 1)
                        print(f"{wait_time:.2f}秒后重试...")
                        time.sleep(wait_time)
                    else:
                        return None
            except Exception as e:
                print(f"执行SPARQL查询时出错 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    print(f"{wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
                else:
                    return None
    
    def collect_programming_languages(self):
        """采集编程语言数据"""
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?language ?languageLabel ?description ?inventor ?inventorLabel ?inception WHERE {
          ?language wdt:P31/wdt:P279* wd:Q9143.  # 编程语言或其子类
          OPTIONAL { ?language rdfs:label ?languageLabel FILTER(LANG(?languageLabel) = 'zh'). }
          OPTIONAL { ?language rdfs:label ?languageLabel FILTER(LANG(?languageLabel) = 'en'). }
          OPTIONAL { ?language schema:description ?description FILTER(LANG(?description) = 'zh'). }
          OPTIONAL { ?language schema:description ?description FILTER(LANG(?description) = 'en'). }
          OPTIONAL { ?language wdt:P57 ?inventor. }
          OPTIONAL { ?inventor rdfs:label ?inventorLabel FILTER(LANG(?inventorLabel) = 'en'). }
          OPTIONAL { ?language wdt:P571 ?inception. }
          LIMIT 10
        }
        """
        
        print("正在采集Wikidata编程语言数据...")
        results = self.execute_sparql_query(query)
        
        if results:
            languages = []
            for item in results['results']['bindings']:
                language_id = item['language']['value'].split('/')[-1]
                language_name = item.get('languageLabel', {}).get('value', 'Unknown')
                description = item.get('description', {}).get('value', '')
                inventor = item.get('inventorLabel', {}).get('value', '')
                inception = item.get('inception', {}).get('value', '')
                
                node = KnowledgeNode(
                    concept_id=f"wikidata_{language_id}",
                    concept_name=language_name,
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=2,  # 实体层
                    category="programming_language",
                    description=description,
                    source="Wikidata",
                    depth=0,
                    parent_concept=None,
                    keywords=[language_name, "programming language"],
                    difficulty=None,
                    importance=1
                )
                languages.append(node.to_dict())
            
            self.storage.save_raw_data('wikidata', 'programming_languages', results)
            self.storage.save_processed_data('wikidata', 'programming_languages', languages)
            
            print(f"采集到 {len(languages)} 种编程语言")
            return languages
        else:
            # 使用模拟数据
            print("使用模拟数据")
            mock_languages = [
                {
                    "concept_id": "wikidata_python",
                    "concept_name": "Python",
                    "course_id": None,
                    "prerequisites": [],
                    "successors": [],
                    "level": 2,
                    "category": "programming_language",
                    "description": "一种解释型、高级、通用的编程语言",
                    "source": "Wikidata",
                    "depth": 0,
                    "parent_concept": None,
                    "keywords": ["Python", "programming language"],
                    "difficulty": 1,
                    "importance": 3
                },
                {
                    "concept_id": "wikidata_java",
                    "concept_name": "Java",
                    "course_id": None,
                    "prerequisites": [],
                    "successors": [],
                    "level": 2,
                    "category": "programming_language",
                    "description": "一种广泛使用的计算机编程语言",
                    "source": "Wikidata",
                    "depth": 0,
                    "parent_concept": None,
                    "keywords": ["Java", "programming language"],
                    "difficulty": 2,
                    "importance": 3
                }
            ]
            
            self.storage.save_processed_data('wikidata', 'programming_languages', mock_languages)
            print(f"使用模拟数据，采集到 {len(mock_languages)} 种编程语言")
            return mock_languages
    
    def collect_algorithms(self):
        """采集算法数据"""
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?algorithm ?algorithmLabel ?description WHERE {
          ?algorithm wdt:P31/wdt:P279* wd:Q20809360.  # 算法或其子类
          OPTIONAL { ?algorithm rdfs:label ?algorithmLabel FILTER(LANG(?algorithmLabel) = 'zh'). }
          OPTIONAL { ?algorithm rdfs:label ?algorithmLabel FILTER(LANG(?algorithmLabel) = 'en'). }
          OPTIONAL { ?algorithm schema:description ?description FILTER(LANG(?description) = 'zh'). }
          OPTIONAL { ?algorithm schema:description ?description FILTER(LANG(?description) = 'en'). }
          LIMIT 10
        }
        """
        
        print("正在采集Wikidata算法数据...")
        results = self.execute_sparql_query(query)
        
        if results:
            algorithms = []
            for item in results['results']['bindings']:
                algorithm_id = item['algorithm']['value'].split('/')[-1]
                algorithm_name = item.get('algorithmLabel', {}).get('value', 'Unknown')
                description = item.get('description', {}).get('value', '')
                
                node = KnowledgeNode(
                    concept_id=f"wikidata_{algorithm_id}",
                    concept_name=algorithm_name,
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=2,  # 实体层
                    category="algorithm",
                    description=description,
                    source="Wikidata",
                    depth=0,
                    parent_concept=None,
                    keywords=[algorithm_name, "algorithm"],
                    difficulty=None,
                    importance=1
                )
                algorithms.append(node.to_dict())
            
            self.storage.save_raw_data('wikidata', 'algorithms', results)
            self.storage.save_processed_data('wikidata', 'algorithms', algorithms)
            
            print(f"采集到 {len(algorithms)} 个算法")
            return algorithms
        else:
            # 使用模拟数据
            print("使用模拟数据")
            mock_algorithms = [
                {
                    "concept_id": "wikidata_bubble_sort",
                    "concept_name": "冒泡排序",
                    "course_id": None,
                    "prerequisites": [],
                    "successors": [],
                    "level": 2,
                    "category": "algorithm",
                    "description": "一种简单的排序算法",
                    "source": "Wikidata",
                    "depth": 0,
                    "parent_concept": None,
                    "keywords": ["冒泡排序", "algorithm"],
                    "difficulty": 1,
                    "importance": 2
                },
                {
                    "concept_id": "wikidata_quick_sort",
                    "concept_name": "快速排序",
                    "course_id": None,
                    "prerequisites": [],
                    "successors": [],
                    "level": 2,
                    "category": "algorithm",
                    "description": "一种高效的排序算法",
                    "source": "Wikidata",
                    "depth": 0,
                    "parent_concept": None,
                    "keywords": ["快速排序", "algorithm"],
                    "difficulty": 2,
                    "importance": 3
                }
            ]
            
            self.storage.save_processed_data('wikidata', 'algorithms', mock_algorithms)
            print(f"使用模拟数据，采集到 {len(mock_algorithms)} 个算法")
            return mock_algorithms
    
    def collect_computer_science_topics(self):
        """采集计算机科学主题数据"""
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?topic ?topicLabel ?description WHERE {
          ?topic wdt:P31/wdt:P279* wd:Q191067.  # 计算机科学主题或其子类
          OPTIONAL { ?topic rdfs:label ?topicLabel FILTER(LANG(?topicLabel) = 'zh'). }
          OPTIONAL { ?topic rdfs:label ?topicLabel FILTER(LANG(?topicLabel) = 'en'). }
          OPTIONAL { ?topic schema:description ?description FILTER(LANG(?description) = 'zh'). }
          OPTIONAL { ?topic schema:description ?description FILTER(LANG(?description) = 'en'). }
          LIMIT 10
        }
        """
        
        print("正在采集Wikidata计算机科学主题数据...")
        results = self.execute_sparql_query(query)
        
        if results:
            topics = []
            for item in results['results']['bindings']:
                topic_id = item['topic']['value'].split('/')[-1]
                topic_name = item.get('topicLabel', {}).get('value', 'Unknown')
                description = item.get('description', {}).get('value', '')
                
                node = KnowledgeNode(
                    concept_id=f"wikidata_{topic_id}",
                    concept_name=topic_name,
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=1,  # 分类层
                    category="computer_science_topic",
                    description=description,
                    source="Wikidata",
                    depth=0,
                    parent_concept=None,
                    keywords=[topic_name, "computer science"],
                    difficulty=None,
                    importance=1
                )
                topics.append(node.to_dict())
            
            self.storage.save_raw_data('wikidata', 'computer_science_topics', results)
            self.storage.save_processed_data('wikidata', 'computer_science_topics', topics)
            
            print(f"采集到 {len(topics)} 个计算机科学主题")
            return topics
        else:
            # 使用模拟数据
            print("使用模拟数据")
            mock_topics = [
                {
                    "concept_id": "wikidata_artificial_intelligence",
                    "concept_name": "人工智能",
                    "course_id": None,
                    "prerequisites": [],
                    "successors": [],
                    "level": 1,
                    "category": "computer_science_topic",
                    "description": "计算机科学的一个分支",
                    "source": "Wikidata",
                    "depth": 0,
                    "parent_concept": None,
                    "keywords": ["人工智能", "computer science"],
                    "difficulty": 3,
                    "importance": 3
                },
                {
                    "concept_id": "wikidata_machine_learning",
                    "concept_name": "机器学习",
                    "course_id": None,
                    "prerequisites": [],
                    "successors": [],
                    "level": 1,
                    "category": "computer_science_topic",
                    "description": "人工智能的一个分支",
                    "source": "Wikidata",
                    "depth": 0,
                    "parent_concept": None,
                    "keywords": ["机器学习", "computer science"],
                    "difficulty": 2,
                    "importance": 3
                }
            ]
            
            self.storage.save_processed_data('wikidata', 'computer_science_topics', mock_topics)
            print(f"使用模拟数据，采集到 {len(mock_topics)} 个计算机科学主题")
            return mock_topics
    
    def collect_all(self):
        """采集所有Wikidata数据"""
        print("开始采集Wikidata数据集...")
        
        programming_languages = self.collect_programming_languages()
        time.sleep(1)
        
        algorithms = self.collect_algorithms()
        time.sleep(1)
        
        computer_science_topics = self.collect_computer_science_topics()
        
        # 整合数据
        integrated_data = {
            "programming_languages": programming_languages,
            "algorithms": algorithms,
            "computer_science_topics": computer_science_topics
        }
        
        self.storage.save_final_data('wikidata', 'integrated', integrated_data)
        
        print("Wikidata数据集采集完成")
        return integrated_data

if __name__ == "__main__":
    collector = WikidataCollector()
    collector.collect_all()