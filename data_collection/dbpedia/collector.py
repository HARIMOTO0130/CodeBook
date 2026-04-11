import requests
import json
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode

class DBpediaCollector:
    """DBpedia数据采集器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.sparql_endpoint = "https://dbpedia.org/sparql"
        self.user_agent = "StrategyKG Data Collector"
    
    def execute_sparql_query(self, query):
        """执行SPARQL查询"""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/sparql-results+json"
        }
        params = {"query": query}
        
        response = requests.get(self.sparql_endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"SPARQL查询失败: {response.status_code}")
            return None
    
    def collect_computer_science_concepts(self):
        """采集计算机科学概念数据"""
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?concept ?label ?comment WHERE {
          ?concept a dbo:ComputerLanguage || a dbo:Algorithm || a dbo:Software || a dbo:ProgrammingLanguage.
          OPTIONAL { ?concept rdfs:label ?label FILTER(LANG(?label) = 'zh'). }
          OPTIONAL { ?concept rdfs:label ?label FILTER(LANG(?label) = 'en'). }
          OPTIONAL { ?concept rdfs:comment ?comment FILTER(LANG(?comment) = 'zh'). }
          OPTIONAL { ?concept rdfs:comment ?comment FILTER(LANG(?comment) = 'en'). }
          LIMIT 100
        }
        """
        
        print("正在采集DBpedia计算机科学概念数据...")
        results = self.execute_sparql_query(query)
        
        if results:
            concepts = []
            for item in results['results']['bindings']:
                concept_id = item['concept']['value'].split('/')[-1]
                concept_name = item.get('label', {}).get('value', 'Unknown')
                description = item.get('comment', {}).get('value', '')
                
                node = KnowledgeNode(
                    concept_id=f"dbpedia_{concept_id}",
                    concept_name=concept_name,
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=2,  # 实体层
                    category="computer_science_concept",
                    description=description,
                    source="DBpedia",
                    depth=0,
                    parent_concept=None,
                    keywords=[concept_name, "computer science"],
                    difficulty=None,
                    importance=1
                )
                concepts.append(node.to_dict())
            
            self.storage.save_raw_data('dbpedia', 'computer_science_concepts', results)
            self.storage.save_processed_data('dbpedia', 'computer_science_concepts', concepts)
            
            print(f"采集到 {len(concepts)} 个计算机科学概念")
            return concepts
        return []
    
    def collect_courses(self):
        """采集课程数据"""
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?course ?label ?comment WHERE {
          ?course a dbo:Course.
          FILTER(CONTAINS(LCASE(STR(?label)), 'computer') || CONTAINS(LCASE(STR(?label)), 'programming') || CONTAINS(LCASE(STR(?label)), 'algorithm')).
          OPTIONAL { ?course rdfs:label ?label FILTER(LANG(?label) = 'en'). }
          OPTIONAL { ?course rdfs:comment ?comment FILTER(LANG(?comment) = 'en'). }
          LIMIT 50
        }
        """
        
        print("正在采集DBpedia课程数据...")
        results = self.execute_sparql_query(query)
        
        if results:
            courses = []
            for item in results['results']['bindings']:
                course_id = item['course']['value'].split('/')[-1]
                course_name = item.get('label', {}).get('value', 'Unknown')
                description = item.get('comment', {}).get('value', '')
                
                node = KnowledgeNode(
                    concept_id=f"dbpedia_{course_id}",
                    concept_name=course_name,
                    course_id=course_id,
                    prerequisites=[],
                    successors=[],
                    level=1,  # 分类层
                    category="course",
                    description=description,
                    source="DBpedia",
                    depth=0,
                    parent_concept=None,
                    keywords=[course_name, "course"],
                    difficulty=None,
                    importance=1
                )
                courses.append(node.to_dict())
            
            self.storage.save_raw_data('dbpedia', 'courses', results)
            self.storage.save_processed_data('dbpedia', 'courses', courses)
            
            print(f"采集到 {len(courses)} 个课程")
            return courses
        return []
    
    def collect_relations(self):
        """采集关系数据"""
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbp: <http://dbpedia.org/property/>
        
        SELECT ?subject ?subjectLabel ?predicate ?object ?objectLabel WHERE {
          {
            ?subject dbp:language ?object.
            ?subject rdfs:label ?subjectLabel FILTER(LANG(?subjectLabel) = 'en').
            ?object rdfs:label ?objectLabel FILTER(LANG(?objectLabel) = 'en').
          } UNION {
            ?subject dbo:programmingLanguage ?object.
            ?subject rdfs:label ?subjectLabel FILTER(LANG(?subjectLabel) = 'en').
            ?object rdfs:label ?objectLabel FILTER(LANG(?objectLabel) = 'en').
          }
          BIND("related" AS ?predicate)
          LIMIT 100
        }
        """
        
        print("正在采集DBpedia关系数据...")
        results = self.execute_sparql_query(query)
        
        if results:
            relations = []
            for item in results['results']['bindings']:
                subject_id = item['subject']['value'].split('/')[-1]
                subject_name = item.get('subjectLabel', {}).get('value', 'Unknown')
                predicate = item.get('predicate', {}).get('value', 'related')
                object_id = item['object']['value'].split('/')[-1]
                object_name = item.get('objectLabel', {}).get('value', 'Unknown')
                
                relation = {
                    'subject_id': f"dbpedia_{subject_id}",
                    'subject_name': subject_name,
                    'predicate': predicate,
                    'object_id': f"dbpedia_{object_id}",
                    'object_name': object_name,
                    'source': 'DBpedia'
                }
                relations.append(relation)
            
            self.storage.save_raw_data('dbpedia', 'relations', results)
            self.storage.save_processed_data('dbpedia', 'relations', relations)
            
            print(f"采集到 {len(relations)} 条关系")
            return relations
        return []
    
    def collect_all(self):
        """采集所有DBpedia数据"""
        print("开始采集DBpedia数据集...")
        
        computer_science_concepts = self.collect_computer_science_concepts()
        courses = self.collect_courses()
        relations = self.collect_relations()
        
        # 整合数据
        integrated_data = {
            "computer_science_concepts": computer_science_concepts,
            "courses": courses,
            "relations": relations
        }
        
        self.storage.save_final_data('dbpedia', 'integrated', integrated_data)
        
        print("DBpedia数据集采集完成")
        return integrated_data

if __name__ == "__main__":
    collector = DBpediaCollector()
    collector.collect_all()