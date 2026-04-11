import json
from typing import List, Dict, Tuple, Optional, Any
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode

class Neo4jConnection:
    """Neo4j数据库连接管理器"""

    def __init__(self, uri: str = "bolt://localhost:7687",
                 username: str = "neo4j", password: str = "password"):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self._connect()

    def _connect(self):
        """建立数据库连接"""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            print(f"已连接到Neo4j: {self.uri}")
        except ImportError:
            print("neo4j驱动程序未安装，请运行: pip install neo4j")
            self.driver = None
        except Exception as e:
            print(f"连接Neo4j失败: {e}")
            self.driver = None

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            print("Neo4j连接已关闭")

    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """执行Cypher查询"""
        if not self.driver:
            print("未连接到Neo4j")
            return []

        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def execute_write(self, query: str, parameters: Dict = None) -> Any:
        """执行写操作"""
        if not self.driver:
            print("未连接到Neo4j")
            return None

        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return result.consume()


class Neo4jGraphManager:
    """Neo4j图数据库管理器"""

    def __init__(self, connection: Neo4jConnection = None):
        self.connection = connection or Neo4jConnection()
        self.storage = StorageManager()

    def create_concept_node(self, concept: Dict) -> bool:
        """创建概念节点"""
        query = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c.concept_name = $concept_name,
            c.level = $level,
            c.category = $category,
            c.description = $description,
            c.source = $source,
            c.difficulty = $difficulty,
            c.importance = $importance
        RETURN c
        """

        parameters = {
            'concept_id': concept.get('concept_id', ''),
            'concept_name': concept.get('concept_name', ''),
            'level': concept.get('level', 0),
            'category': concept.get('category', ''),
            'description': concept.get('description', ''),
            'source': concept.get('source', ''),
            'difficulty': concept.get('difficulty', 1),
            'importance': concept.get('importance', 1)
        }

        try:
            self.connection.execute_write(query, parameters)
            return True
        except Exception as e:
            print(f"创建概念节点失败: {e}")
            return False

    def create_relation(self, subject_id: str, predicate: str, object_id: str,
                       properties: Dict = None) -> bool:
        """创建关系"""
        query = f"""
        MATCH (s:Concept {{concept_id: $subject_id}})
        MATCH (o:Concept {{concept_id: $object_id}})
        MERGE (s)-[r:{predicate.upper()}]->(o)
        """

        if properties:
            for key, value in properties.items():
                query += f" SET r.{key} = ${key}"

        query += " RETURN r"

        parameters = {
            'subject_id': subject_id,
            'object_id': object_id,
            ** (properties or {})
        }

        try:
            self.connection.execute_write(query, parameters)
            return True
        except Exception as e:
            print(f"创建关系失败: {e}")
            return False

    def import_knowledge_graph(self, nodes: List[Dict], relations: List[Dict]) -> Dict:
        """导入知识图谱"""
        print(f"开始导入知识图谱: {len(nodes)} 个节点, {len(relations)} 条关系...")

        created_nodes = 0
        failed_nodes = 0

        for node in nodes:
            if self.create_concept_node(node):
                created_nodes += 1
            else:
                failed_nodes += 1

        print(f"节点导入完成: 成功 {created_nodes}, 失败 {failed_nodes}")

        created_relations = 0
        failed_relations = 0

        for relation in relations:
            subject = relation.get('subject_id', relation.get('subject', ''))
            predicate = relation.get('predicate', relation.get('relation', ''))
            obj = relation.get('object_id', relation.get('object', ''))

            if subject and predicate and obj:
                if self.create_relation(subject, predicate, obj):
                    created_relations += 1
                else:
                    failed_relations += 1

        print(f"关系导入完成: 成功 {created_relations}, 失败 {failed_relations}")

        result = {
            'nodes': {'total': len(nodes), 'created': created_nodes, 'failed': failed_nodes},
            'relations': {'total': len(relations), 'created': created_relations, 'failed': failed_relations}
        }

        self.storage.save_raw_data('neo4j', 'import_result', result)
        return result

    def query_learning_path(self, start_concept: str, end_concept: str, max_depth: int = 10) -> List[List[str]]:
        """查询学习路径"""
        query = f"""
        MATCH path = (start:Concept {{concept_name: $start_concept}})-[:REQUIRES*1..{max_depth}]->(end:Concept {{concept_name: $end_concept}})
        RETURN path
        LIMIT 10
        """

        parameters = {
            'start_concept': start_concept,
            'end_concept': end_concept
        }

        results = self.connection.execute_query(query, parameters)
        paths = []

        for record in results:
            path = record.get('path')
            if path:
                nodes = [node.get('concept_name') for node in path.nodes]
                paths.append(nodes)

        return paths

    def get_concept_relationships(self, concept_name: str) -> Dict:
        """获取概念的相关关系"""
        query = """
        MATCH (c:Concept {concept_name: $concept_name})-[r]->(related)
        RETURN type(r) as relation, related.concept_name as related_concept
        """

        outgoing = self.connection.execute_query(query, {'concept_name': concept_name})

        query = """
        MATCH (c:Concept {concept_name: $concept_name})<-[r]-(related)
        RETURN type(r) as relation, related.concept_name as related_concept
        """

        incoming = self.connection.execute_query(query, {'concept_name': concept_name})

        return {
            'outgoing': outgoing,
            'incoming': incoming
        }

    def get_subgraph(self, concept_name: str, depth: int = 2) -> Dict:
        """获取概念的子图"""
        query = f"""
        MATCH path = (c:Concept {{concept_name: $concept_name}})-[r*1..{depth}]->(related)
        RETURN path
        LIMIT 100
        """

        results = self.connection.execute_query(query, {'concept_name': concept_name})

        nodes = []
        edges = []
        node_set = set()

        for record in results:
            path = record.get('path')
            if path:
                for node in path.nodes:
                    node_id = node.get('concept_id')
                    if node_id not in node_set:
                        node_set.add(node_id)
                        nodes.append({
                            'id': node_id,
                            'label': node.get('concept_name'),
                            'level': node.get('level'),
                            'category': node.get('category')
                        })

                for rel in path.relationships:
                    edges.append({
                        'source': rel.start_node.get('concept_id'),
                        'target': rel.end_node.get('concept_id'),
                        'type': rel.type
                    })

        return {'nodes': nodes, 'edges': edges}

    def delete_all(self):
        """删除所有节点和关系"""
        query = "MATCH (n) DETACH DELETE n"
        self.connection.execute_write(query)
        print("已删除所有节点和关系")


class CypherGenerator:
    """Cypher查询生成器"""

    @staticmethod
    def generate_create_node_query(concept: Dict) -> str:
        """生成创建节点的Cypher查询"""
        labels = "Concept"

        properties = []
        for key, value in concept.items():
            if value is not None:
                if isinstance(value, str):
                    properties.append(f"{key}: '{value}'")
                elif isinstance(value, (int, float)):
                    properties.append(f"{key}: {value}")
                elif isinstance(value, list):
                    properties.append(f"{key}: {json.dumps(value)}")
                else:
                    properties.append(f"{key}: '{value}'")

        query = f"CREATE (n:{labels} {{{', '.join(properties)}}})"
        return query

    @staticmethod
    def generate_create_relation_query(subject_id: str, predicate: str,
                                      object_id: str, properties: Dict = None) -> str:
        """生成创建关系的Cypher查询"""
        query = f"""
        MATCH (s:Concept {{concept_id: '{subject_id}'}})
        MATCH (o:Concept {{concept_id: '{object_id}'}})
        CREATE (s)-[r:{predicate.upper()}"
        if properties:
            props = ", ".join([f"{k}: '{v}'" for k, v in properties.items()])
            query += f" {{{props}}}"
        query += "]->(o)"
        return query

    @staticmethod
    def generate_learning_path_query(start: str, end: str, max_depth: int = 10) -> str:
        """生成学习路径查询"""
        return f"""
        MATCH path = (start:Concept {{concept_name: '{start}'}})-[:REQUIRES*1..{max_depth}]->(end:Concept {{concept_name: '{end}'}})
        RETURN path
        ORDER BY length(path)
        LIMIT 10
        """

    @staticmethod
    def generate_batch_import_cypher(nodes: List[Dict], relations: List[Dict]) -> str:
        """生成批量导入的Cypher查询"""
        queries = []

        for node in nodes:
            queries.append(CypherGenerator.generate_create_node_query(node) + ";")

        for relation in relations:
            queries.append(CypherGenerator.generate_create_relation_query(
                relation.get('subject_id', ''),
                relation.get('predicate', ''),
                relation.get('object_id', '')
            ) + ";")

        return "\n".join(queries)


class GraphVisualizationExporter:
    """图可视化数据导出器"""

    def __init__(self):
        self.storage = StorageManager()

    def export_to_d3_json(self, nodes: List[Dict], relations: List[Dict]) -> Dict:
        """导出为D3.js可视化格式"""
        d3_data = {
            'nodes': [],
            'links': []
        }

        node_map = {}

        for idx, node in enumerate(nodes):
            node_id = node.get('concept_id', f"node_{idx}")
            node_map[node_id] = idx

            level = node.get('level', 0)
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            color = colors[level] if level < len(colors) else '#95A5A6'

            d3_data['nodes'].append({
                'id': node_id,
                'name': node.get('concept_name', ''),
                'level': level,
                'category': node.get('category', ''),
                'importance': node.get('importance', 1),
                'color': color
            })

        for relation in relations:
            subject_id = relation.get('subject_id', relation.get('subject', ''))
            object_id = relation.get('object_id', relation.get('object', ''))

            if subject_id in node_map and object_id in node_map:
                d3_data['links'].append({
                    'source': subject_id,
                    'target': object_id,
                    'type': relation.get('predicate', relation.get('relation', 'RELATED'))
                })

        self.storage.save_final_data('visualization', 'd3_json', d3_data)
        return d3_data

    def export_to_cytoscape_json(self, nodes: List[Dict], relations: List[Dict]) -> Dict:
        """导出为Cytoscape.js可视化格式"""
        cy_data = {
            'elements': {
                'nodes': [],
                'edges': []
            }
        }

        node_map = {}

        for idx, node in enumerate(nodes):
            node_id = node.get('concept_id', f"node_{idx}")
            node_map[node_id] = idx

            level = node.get('level', 0)
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            color = colors[level] if level < len(colors) else '#95A5A6'

            cy_data['elements']['nodes'].append({
                'data': {
                    'id': node_id,
                    'label': node.get('concept_name', ''),
                    'level': level,
                    'category': node.get('category', '')
                },
                'style': {
                    'background-color': color
                }
            })

        for relation in relations:
            subject_id = relation.get('subject_id', relation.get('subject', ''))
            object_id = relation.get('object_id', relation.get('object', ''))

            if subject_id in node_map and object_id in node_map:
                cy_data['elements']['edges'].append({
                    'data': {
                        'source': subject_id,
                        'target': object_id,
                        'label': relation.get('predicate', relation.get('relation', 'RELATED'))
                    }
                })

        self.storage.save_final_data('visualization', 'cytoscape_json', cy_data)
        return cy_data

    def export_to_csv(self, nodes: List[Dict], relations: List[Dict]) -> Dict:
        """导出为CSV格式"""
        node_csv = "concept_id,concept_name,level,category,description\n"
        for node in nodes:
            node_csv += f"{node.get('concept_id', '')},{node.get('concept_name', '')},{node.get('level', '')},{node.get('category', '')},{node.get('description', '').replace(',', ';')}\n"

        relation_csv = "subject,predicate,object\n"
        for relation in relations:
            relation_csv += f"{relation.get('subject_id', relation.get('subject', ''))},{relation.get('predicate', relation.get('relation', ''))},{relation.get('object_id', relation.get('object', ''))}\n"

        csv_data = {
            'nodes': node_csv,
            'relations': relation_csv
        }

        self.storage.save_raw_data('visualization', 'nodes_csv', node_csv)
        self.storage.save_raw_data('visualization', 'relations_csv', relation_csv)
        return csv_data


class Neo4jBackupManager:
    """Neo4j备份管理器"""

    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
        self.storage = StorageManager()

    def export_to_json(self, filename: str = "knowledge_graph_backup") -> str:
        """导出整个图数据库为JSON"""
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m"

        results = self.connection.execute_query(query)

        nodes = []
        relations = []
        node_ids = set()

        for record in results:
            node = record.get('n')
            if node and node.get('concept_id') not in node_ids:
                node_ids.add(node.get('concept_id'))
                nodes.append(dict(node))

            rel = record.get('r')
            if rel:
                relations.append({
                    'subject_id': rel.start_node.get('concept_id'),
                    'predicate': rel.type,
                    'object_id': rel.end_node.get('concept_id')
                })

        backup_data = {
            'nodes': nodes,
            'relations': relations,
            'metadata': {
                'total_nodes': len(nodes),
                'total_relations': len(relations)
            }
        }

        file_path = self.storage.storage.generate_filename(filename)
        with open(f"{self.storage.storage.base_path}/backup/{file_path}.json", 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        return file_path

    def import_from_json(self, file_path: str) -> bool:
        """从JSON文件导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            nodes = data.get('nodes', [])
            relations = data.get('relations', [])

            manager = Neo4jGraphManager(self.connection)
            result = manager.import_knowledge_graph(nodes, relations)

            return result['nodes']['failed'] == 0
        except Exception as e:
            print(f"导入失败: {e}")
            return False


if __name__ == "__main__":
    test_nodes = [
        {
            'concept_id': 'py',
            'concept_name': 'Python',
            'level': 1,
            'category': 'language',
            'description': 'Python编程语言',
            'source': 'test',
            'difficulty': 1,
            'importance': 1
        },
        {
            'concept_id': 'oop',
            'concept_name': '面向对象编程',
            'level': 2,
            'category': 'paradigm',
            'description': '面向对象编程范式',
            'source': 'test',
            'difficulty': 2,
            'importance': 1
        },
        {
            'concept_id': 'web',
            'concept_name': 'Web开发',
            'level': 2,
            'category': 'domain',
            'description': 'Web应用开发',
            'source': 'test',
            'difficulty': 3,
            'importance': 1
        }
    ]

    test_relations = [
        {'subject_id': 'oop', 'predicate': 'requires', 'object_id': 'py'},
        {'subject_id': 'web', 'predicate': 'requires', 'object_id': 'py'},
        {'subject_id': 'web', 'predicate': 'requires', 'object_id': 'oop'}
    ]

    cyper_queries = []
    for node in test_nodes:
        cyper_queries.append(CypherGenerator.generate_create_node_query(node))

    for relation in test_relations:
        cyper_queries.append(CypherGenerator.generate_create_relation_query(
            relation['subject_id'],
            relation['predicate'],
            relation['object_id']
        ))

    print("生成的Cypher查询:")
    for query in cyper_queries:
        print(query)
        print()

    exporter = GraphVisualizationExporter()
    d3_data = exporter.export_to_d3_json(test_nodes, test_relations)
    print(f"\nD3可视化数据: {len(d3_data['nodes'])} 节点, {len(d3_data['links'])} 链接")

    cy_data = exporter.export_to_cytoscape_json(test_nodes, test_relations)
    print(f"Cytoscape可视化数据: {len(cy_data['elements']['nodes'])} 节点, {len(cy_data['elements']['edges'])} 边")