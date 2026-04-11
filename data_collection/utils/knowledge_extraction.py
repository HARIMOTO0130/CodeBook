import re
import json
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode

class NamedEntityRecognizer:
    """命名实体识别器 - 使用Hugging Face Transformers或spaCy"""

    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        self.storage = StorageManager()
        self.model_name = model_name
        self.ner_pipeline = None

    def load_model(self):
        """加载NER模型"""
        try:
            from transformers import pipeline
            self.ner_pipeline = pipeline("ner", model=self.model_name)
            print(f"已加载NER模型: {self.model_name}")
        except ImportError:
            print("transformers库未安装，使用规则匹配作为备选方案")
            self.ner_pipeline = None

    def recognize_entities(self, text: str, use_transformer: bool = True) -> List[Dict]:
        """识别文本中的实体"""
        if use_transformer and self.ner_pipeline:
            return self._recognize_with_transformer(text)
        else:
            return self._recognize_with_rules(text)

    def _recognize_with_transformer(self, text: str) -> List[Dict]:
        """使用Transformer模型识别实体"""
        entities = self.ner_pipeline(text)

        results = []
        current_entity = None
        current_type = None

        for entity in entities:
            word = entity.get('word', '')
            entity_type = entity.get('entity', '')

            if entity_type.startswith('B-'):
                if current_entity:
                    results.append({
                        'word': current_entity,
                        'type': current_type
                    })
                current_entity = word
                current_type = entity_type[2:]
            elif entity_type.startswith('I-') and current_type == entity_type[2:]:
                current_entity += ' ' + word
            else:
                if current_entity:
                    results.append({
                        'word': current_entity,
                        'type': current_type
                    })
                current_entity = None
                current_type = None

        if current_entity:
            results.append({
                'word': current_entity,
                'type': current_type
            })

        return results

    def _recognize_with_rules(self, text: str) -> List[Dict]:
        """使用规则匹配识别实体"""
        entities = []

        cs_terms = {
            'language': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin'],
            'framework': ['React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring', 'Express', 'Laravel'],
            'tool': ['Git', 'Docker', 'Kubernetes', 'Jenkins', 'Nginx', 'Apache'],
            'library': ['NumPy', 'Pandas', 'TensorFlow', 'PyTorch', 'OpenCV', 'Scikit-learn'],
            'concept': ['API', 'REST', 'OOP', 'MVC', 'CRUD', 'SQL', 'NoSQL', 'JSON', 'XML'],
            'domain': ['机器学习', '深度学习', 'Web开发', '数据分析', '云计算', '区块链', '人工智能']
        }

        for entity_type, terms in cs_terms.items():
            for term in terms:
                if term in text:
                    entities.append({
                        'word': term,
                        'type': entity_type,
                        'source': 'rule-based'
                    })

        return entities

    def extract_from_corpus(self, corpus: List[str]) -> Dict[str, List[str]]:
        """从语料库中提取所有实体"""
        all_entities = defaultdict(set)

        for text in corpus:
            entities = self.recognize_entities(text)
            for entity in entities:
                entity_type = entity.get('type', 'unknown')
                entity_word = entity.get('word', '')
                if entity_word:
                    all_entities[entity_type].add(entity_word)

        return {etype: list(words) for etype, words in all_entities.items()}


class RelationExtractor:
    """关系抽取器"""

    def __init__(self):
        self.storage = StorageManager()
        self.relation_patterns = {
            '前置': [
                r'(.+?)需要先掌握(.+?)',
                r'(.+?)的基础是(.+?)',
                r'(.+?)的前提是(.+?)',
                r'学习(.+?)之前需要先学(.+?)'
            ],
            '包含': [
                r'(.+?)包括(.+?)',
                r'(.+?)包含(.+?)',
                r'(.+?)涵盖(.+?)',
                r'(.+?)由(.+?)组成'
            ],
            '依赖': [
                r'(.+?)依赖(.+?)',
                r'(.+?)需要(.+?)',
                r'(.+?)基于(.+?)',
                r'(.+?)使用(.+?)'
            ],
            '进阶': [
                r'(.+?)进阶后是(.+?)',
                r'(.+?)的高级形式是(.+?)',
                r'学完(.+?)可以学(.+?)',
                r'(.+?)下一步是(.+?)'
            ],
            '类型': [
                r'(.+?)是一种(.+?)',
                r'(.+?)属于(.+?)类型',
                r'(.+?)是(.+?)的一种'
            ]
        }

    def extract_relations(self, text: str) -> List[Tuple[str, str, str]]:
        """从文本中抽取关系"""
        triplets = []

        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    if len(match.groups()) >= 2:
                        entity1 = match.group(1).strip()
                        entity2 = match.group(2).strip()
                        if entity1 and entity2:
                            triplets.append((entity1, relation_type, entity2))

        return triplets

    def extract_from_corpus(self, corpus: List[str]) -> List[Dict]:
        """从语料库中抽取所有关系"""
        all_relations = []

        for text in corpus:
            triplets = self.extract_relations(text)
            for entity1, relation, entity2 in triplets:
                all_relations.append({
                    'entity1': entity1,
                    'relation': relation,
                    'entity2': entity2,
                    'source_text': text
                })

        self.storage.save_raw_data('extraction', 'relations', all_relations)
        print(f"从语料库中抽取了 {len(all_relations)} 个关系")
        return all_relations


class DistantSupervisionExtractor:
    """远程监督关系抽取器"""

    def __init__(self):
        self.storage = StorageManager()
        self.known_relations = self._load_seed_relations()

    def _load_seed_relations(self) -> Dict:
        """加载种子关系"""
        return {
            'Python': ['编程语言', '面向对象', '解释型'],
            'Java': ['编程语言', '面向对象', '编译型'],
            'JavaScript': ['编程语言', '脚本语言', 'Web开发'],
            'React': ['前端框架', '组件化', '单页应用'],
            'Django': ['Web框架', 'Python', 'MVC'],
            '机器学习': ['人工智能', '数据科学', '算法'],
            '深度学习': ['机器学习', '神经网络', '人工智能'],
            'MySQL': ['关系型数据库', 'SQL', 'Web开发']
        }

    def extract_with_distant_supervision(self, corpus: List[str]) -> List[Dict]:
        """使用远程监督抽取关系"""
        relations = []

        for entity1, related_entities in self.known_relations.items():
            for text in corpus:
                if entity1 in text:
                    for entity2 in related_entities:
                        if entity2 in text:
                            relations.append({
                                'entity1': entity1,
                                'entity2': entity2,
                                'relation': 'related',
                                'confidence': 0.8,
                                'source': 'distant_supervision'
                            })

        self.storage.save_raw_data('extraction', 'distant_relations', relations)
        print(f"使用远程监督抽取了 {len(relations)} 个关系")
        return relations


class BERTRelationClassifier:
    """基于BERT的关系分类器"""

    def __init__(self, model_name: str = "bert-base-uncased"):
        self.storage = StorageManager()
        self.model_name = model_name
        self.classifier = None

    def load_model(self):
        """加载BERT模型"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=6
            )
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            print(f"已加载BERT模型: {self.model_name}")
        except ImportError:
            print("transformers库未安装，无法使用BERT分类器")
        except Exception as e:
            print(f"加载BERT模型时出错: {e}")

    def classify_relation(self, entity1: str, entity2: str, text: str) -> Dict:
        """分类实体之间的关系类型"""
        if not self.classifier:
            return {'relation': 'unknown', 'confidence': 0.0}

        input_text = f"{entity1} [SEP] {entity2} [SEP] {text}"

        try:
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits

            relation_types = ['前置', '包含', '依赖', '进阶', '类型', '其他']
            probs = torch.softmax(predictions, dim=1)
            predicted_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][predicted_class].item()

            return {
                'relation': relation_types[predicted_class],
                'confidence': confidence,
                'entity1': entity1,
                'entity2': entity2,
                'text': text
            }
        except Exception as e:
            print(f"关系分类时出错: {e}")
            return {'relation': 'unknown', 'confidence': 0.0}


class KnowledgeExtractor:
    """知识抽取综合管理器"""

    def __init__(self):
        self.storage = StorageManager()
        self.ner = NamedEntityRecognizer()
        self.relation_extractor = RelationExtractor()
        self.distant_extractor = DistantSupervisionExtractor()

    def extract_knowledge(self, corpus: List[str], use_transformer: bool = False) -> Dict:
        """从语料库中抽取知识"""
        print(f"开始从 {len(corpus)} 个文本中抽取知识...")

        all_entities = []
        all_relations = []

        print("步骤1: 实体抽取...")
        for text in corpus:
            entities = self.ner.recognize_entities(text, use_transformer)
            all_entities.extend(entities)
        print(f"抽取了 {len(all_entities)} 个实体")

        print("步骤2: 关系抽取（规则匹配）...")
        relations = self.relation_extractor.extract_from_corpus(corpus)
        all_relations.extend(relations)
        print(f"抽取了 {len(relations)} 个关系")

        print("步骤3: 关系抽取（远程监督）...")
        distant_relations = self.distant_extractor.extract_with_distant_supervision(corpus)
        all_relations.extend(distant_relations)
        print(f"远程监督抽取了 {len(distant_relations)} 个关系")

        knowledge_graph = {
            'entities': all_entities,
            'relations': all_relations,
            'metadata': {
                'total_entities': len(all_entities),
                'total_relations': len(all_relations),
                'source': 'knowledge_extraction',
                'extraction_methods': ['ner', 'rule_based', 'distant_supervision']
            }
        }

        self.storage.save_final_data('extraction', 'knowledge_graph', knowledge_graph)
        print("知识抽取完成")
        return knowledge_graph

    def convert_to_knowledge_nodes(self, knowledge_graph: Dict) -> List[KnowledgeNode]:
        """将抽取的知识转换为知识节点"""
        nodes = []
        node_map = {}

        for entity in knowledge_graph.get('entities', []):
            entity_name = entity.get('word', '')
            entity_type = entity.get('type', 'unknown')

            if entity_name not in node_map:
                node = KnowledgeNode(
                    concept_id=f"extracted_{entity_name}",
                    concept_name=entity_name,
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=2,
                    category=entity_type,
                    description=f"从文本中抽取的{entity_type}实体",
                    source="knowledge_extraction",
                    depth=0,
                    parent_concept=None,
                    keywords=[entity_name],
                    difficulty=1,
                    importance=1
                )
                nodes.append(node.to_dict())
                node_map[entity_name] = True

        return nodes


class TextPreprocessor:
    """文本预处理器"""

    def __init__(self):
        self.stop_words = set(['的', '是', '在', '和', '了', '与', '或', '以及', '等', '包括'])

    def clean_text(self, text: str) -> str:
        """清洗文本"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', text)
        text = text.strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """分词"""
        text = self.clean_text(text)
        tokens = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z0-9]+', text)
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 1]
        return tokens

    def preprocess_corpus(self, corpus: List[str]) -> List[str]:
        """预处理语料库"""
        return [self.clean_text(text) for text in corpus]


if __name__ == "__main__":
    corpus = [
        "Python是一种广泛使用的解释型、高级和通用的编程语言",
        "Python支持多种编程范式，包括结构化、过程式、反射式、面向对象和函数式编程",
        "学习Python需要先掌握变量和数据类型",
        "Python的基础包括基本语法、数据类型、控制流",
        "学完基础语法后可以继续学习函数和模块",
        "面向对象编程是Python的重要组成部分",
        "Django是一个Python Web框架",
        "学习Web开发需要先掌握HTML、CSS、JavaScript",
        "Flask是Python的轻量级Web框架",
        "数据分析需要掌握Pandas和NumPy",
        "机器学习是人工智能的一个分支",
        "深度学习是机器学习的一个分支",
        "TensorFlow是一个开源软件库，用于机器学习和人工智能",
        "React是一个用于构建用户界面的JavaScript库",
        "Vue.js是一个渐进式JavaScript框架"
    ]

    extractor = KnowledgeExtractor()
    result = extractor.extract_knowledge(corpus)

    print(f"实体数量: {result['metadata']['total_entities']}")
    print(f"关系数量: {result['metadata']['total_relations']}")

    print("\n抽取的实体:")
    for entity in result['entities'][:10]:
        print(f"  - {entity['word']} ({entity['type']})")

    print("\n抽取的关系:")
    for relation in result['relations'][:10]:
        print(f"  - {relation['entity1']} --[{relation['relation']}]--> {relation['entity2']}")