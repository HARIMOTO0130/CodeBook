import re
import json
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from difflib import SequenceMatcher
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode

class EntityAligner:
    """实体对齐器"""

    def __init__(self):
        self.storage = StorageManager()
        self.similarity_threshold = 0.8

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """计算两个实体名称的相似度"""
        name1 = self._normalize_name(name1)
        name2 = self._normalize_name(name2)

        return SequenceMatcher(None, name1, name2).ratio()

    def _normalize_name(self, name: str) -> str:
        """标准化实体名称"""
        name = name.lower().strip()
        name = re.sub(r'[^\w\u4e00-\u9fa5]', '', name)
        return name

    def find_similar_entities(self, entities: List[Dict], threshold: float = None) -> List[Tuple[int, int, float]]:
        """查找相似的实体对"""
        if threshold is None:
            threshold = self.similarity_threshold

        similar_pairs = []

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                name1 = entities[i].get('concept_name', entities[i].get('name', ''))
                name2 = entities[j].get('concept_name', entities[j].get('name', ''))

                similarity = self.calculate_similarity(name1, name2)

                if similarity >= threshold:
                    similar_pairs.append((i, j, similarity))

        return similar_pairs

    def align_entities(self, entities: List[Dict], threshold: float = None) -> Dict:
        """对齐实体，返回对齐结果"""
        if threshold is None:
            threshold = self.similarity_threshold

        alignment_result = {
            'aligned_pairs': [],
            'unaligned_entities': [],
            'clusters': []
        }

        aligned = set()
        clusters = []

        similar_pairs = self.find_similar_entities(entities, threshold)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)

        for i, j, similarity in similar_pairs:
            if i not in aligned and j not in aligned:
                clusters.append([i, j])
                aligned.add(i)
                aligned.add(j)
                alignment_result['aligned_pairs'].append({
                    'entity1_index': i,
                    'entity2_index': j,
                    'similarity': similarity,
                    'entity1_name': entities[i].get('concept_name', entities[i].get('name', '')),
                    'entity2_name': entities[j].get('concept_name', entities[j].get('name', ''))
                })

        for idx in range(len(entities)):
            if idx not in aligned:
                alignment_result['unaligned_entities'].append({
                    'index': idx,
                    'entity': entities[idx]
                })

        alignment_result['clusters'] = clusters
        self.storage.save_raw_data('fusion', 'entity_alignment', alignment_result)

        return alignment_result


class FuzzyMatcher:
    """模糊匹配器"""

    def __init__(self):
        self.storage = StorageManager()

    def fuzzy_match(self, source: str, targets: List[str], threshold: float = 0.8) -> Optional[Tuple[str, float]]:
        """模糊匹配"""
        best_match = None
        best_score = 0

        for target in targets:
            score = self._fuzzy_ratio(source, target)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = target

        return (best_match, best_score) if best_match else None

    def _fuzzy_ratio(self, s1: str, s2: str) -> float:
        """计算模糊匹配分数"""
        s1 = s1.lower().strip()
        s2 = s2.lower().strip()

        if s1 == s2:
            return 1.0

        if s1 in s2 or s2 in s1:
            return 0.9

        return SequenceMatcher(None, s1, s2).ratio()

    def find_matches(self, source: str, targets: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """查找最匹配的前k个目标"""
        matches = []

        for target in targets:
            score = self._fuzzy_ratio(source, target)
            matches.append((target, score))

        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:top_k]


class KnowledgeFusionManager:
    """知识融合管理器"""

    def __init__(self):
        self.storage = StorageManager()
        self.entity_aligner = EntityAligner()
        self.fuzzy_matcher = FuzzyMatcher()

    def fuse_knowledge_sources(self, sources: Dict[str, List[Dict]]) -> Dict:
        """融合多个知识源的数据"""
        print("开始知识融合...")

        all_entities = []
        source_mapping = {}

        for source_name, entities in sources.items():
            for entity in entities:
                entity_copy = entity.copy()
                entity_copy['source'] = source_name
                entity_copy['original_id'] = entity_copy.get('concept_id', entity_copy.get('id', ''))
                all_entities.append(entity_copy)

        print(f"融合了 {len(all_entities)} 个实体")

        print("步骤1: 实体对齐...")
        alignment = self.entity_aligner.align_entities(all_entities)
        print(f"对齐了 {len(alignment['aligned_pairs'])} 对实体")
        print(f"未对齐实体: {len(alignment['unaligned_entities'])} 个")

        print("步骤2: 构建融合实体...")
        fused_entities = self._build_fused_entities(all_entities, alignment)
        print(f"生成了 {len(fused_entities)} 个融合实体")

        print("步骤3: 融合关系...")
        fused_relations = self._fuse_relations(sources)
        print(f"融合了 {len(fused_relations)} 条关系")

        fusion_result = {
            'fused_entities': fused_entities,
            'fused_relations': fused_relations,
            'alignment': alignment,
            'metadata': {
                'total_sources': len(sources),
                'total_original_entities': len(all_entities),
                'total_fused_entities': len(fused_entities),
                'total_relations': len(fused_relations),
                'source': 'knowledge_fusion'
            }
        }

        self.storage.save_final_data('fusion', 'knowledge_fusion', fusion_result)
        print("知识融合完成")
        return fusion_result

    def _build_fused_entities(self, entities: List[Dict], alignment: Dict) -> List[Dict]:
        """构建融合后的实体"""
        fused_entities = []
        entity_index_map = {}

        for cluster in alignment['clusters']:
            if len(cluster) >= 2:
                merged_entity = self._merge_entities([entities[idx] for idx in cluster])
                fused_entities.append(merged_entity)

                for idx in cluster:
                    entity_index_map[idx] = len(fused_entities) - 1

        for unaligned in alignment['unaligned_entities']:
            idx = unaligned['index']
            entity = unaligned['entity']
            if idx not in entity_index_map:
                fused_entities.append(entity)
                entity_index_map[idx] = len(fused_entities) - 1

        return fused_entities

    def _merge_entities(self, entities: List[Dict]) -> Dict:
        """合并多个相似实体"""
        if len(entities) == 1:
            return entities[0]

        merged = {
            'concept_id': entities[0].get('concept_id', f"fused_{id(entities)}"),
            'concept_name': entities[0].get('concept_name', ''),
            'sources': [],
            'all_names': [],
            'prerequisites': [],
            'successors': [],
            'keywords': set(),
            'description': ''
        }

        for entity in entities:
            merged['sources'].append(entity.get('source', 'unknown'))

            name = entity.get('concept_name', '')
            if name and name not in merged['all_names']:
                merged['all_names'].append(name)

            if entity.get('description') and not merged['description']:
                merged['description'] = entity['description']
            elif entity.get('description'):
                merged['description'] += f"\n{entity['description']}"

            if 'prerequisites' in entity:
                for prereq in entity['prerequisites']:
                    if prereq not in merged['prerequisites']:
                        merged['prerequisites'].append(prereq)

            if 'successors' in entity:
                for successor in entity['successors']:
                    if successor not in merged['successors']:
                        merged['successors'].append(successor)

            if 'keywords' in entity:
                for keyword in entity['keywords']:
                    merged['keywords'].add(keyword)

        merged['keywords'] = list(merged['keywords'])
        merged['merged_from'] = len(entities)
        merged['concept_name'] = merged['all_names'][0] if merged['all_names'] else ''

        return merged

    def _fuse_relations(self, sources: Dict[str, List[Dict]]) -> List[Dict]:
        """融合关系数据"""
        all_relations = []

        for source_name, entities in sources.items():
            for entity in entities:
                if 'prerequisites' in entity:
                    concept_name = entity.get('concept_name', '')
                    for prereq in entity['prerequisites']:
                        all_relations.append({
                            'subject': concept_name,
                            'predicate': 'requires',
                            'object': prereq,
                            'source': source_name
                        })

                if 'successors' in entity:
                    concept_name = entity.get('concept_name', '')
                    for successor in entity['successors']:
                        all_relations.append({
                            'subject': concept_name,
                            'predicate': 'leads_to',
                            'object': successor,
                            'source': source_name
                        })

        unique_relations = []
        seen = set()

        for relation in all_relations:
            key = (relation['subject'], relation['predicate'], relation['object'])
            if key not in seen:
                seen.add(key)
                unique_relations.append(relation)

        return unique_relations


class CrossSourceLinker:
    """跨源链接器"""

    def __init__(self):
        self.storage = StorageManager()

    def link_entities(self, source1_data: List[Dict], source2_data: List[Dict],
                     source1_name: str = "source1", source2_name: str = "source2") -> List[Dict]:
        """链接两个数据源的实体"""
        links = []

        source1_names = {e.get('concept_name', e.get('name', '')): e for e in source1_data}
        source2_names = {e.get('concept_name', e.get('name', '')): e for e in source2_data}

        fuzzy_matcher = FuzzyMatcher()

        for name1, entity1 in source1_names.items():
            match_result = fuzzy_matcher.fuzzy_match(name1, list(source2_names.keys()))

            if match_result:
                name2, score = match_result
                entity2 = source2_names[name2]

                links.append({
                    'source1_entity': entity1,
                    'source2_entity': entity2,
                    'source1_name': name1,
                    'source2_name': name2,
                    'similarity': score,
                    'link_type': 'fuzzy_match'
                })

        self.storage.save_raw_data('fusion', 'cross_source_links', links)
        return links


class KnowledgeMerger:
    """知识合并器"""

    def __init__(self):
        self.storage = StorageManager()

    def merge_knowledge_graphs(self, graphs: List[Dict]) -> Dict:
        """合并多个知识图谱"""
        print(f"开始合并 {len(graphs)} 个知识图谱...")

        merged_graph = {
            'nodes': [],
            'relations': [],
            'metadata': {
                'source_graphs': len(graphs),
                'source': 'knowledge_merger'
            }
        }

        all_concepts = {}
        all_relations = []

        for graph in graphs:
            nodes = graph.get('nodes', graph.get('concepts', []))
            relations = graph.get('relations', [])

            for node in nodes:
                concept_id = node.get('concept_id', node.get('id', ''))
                if concept_id not in all_concepts:
                    all_concepts[concept_id] = node

            all_relations.extend(relations)

        merged_graph['nodes'] = list(all_concepts.values())
        merged_graph['relations'] = all_relations
        merged_graph['metadata']['total_nodes'] = len(merged_graph['nodes'])
        merged_graph['metadata']['total_relations'] = len(merged_graph['relations'])

        print(f"合并完成: {len(merged_graph['nodes'])} 个节点, {len(merged_graph['relations'])} 条关系")

        return merged_graph


class SynonymResolver:
    """同义词解析器"""

    def __init__(self):
        self.storage = StorageManager()
        self.synonym_groups = {}

    def add_synonym(self, term: str, group_id: str):
        """添加同义词"""
        if group_id not in self.synonym_groups:
            self.synonym_groups[group_id] = set()
        self.synonym_groups[group_id].add(term)

    def resolve_synonyms(self, term: str) -> str:
        """解析同义词，返回标准形式"""
        for group_id, terms in self.synonym_groups.items():
            if term in terms:
                return group_id
        return term

    def auto_discover_synonyms(self, entities: List[Dict]) -> Dict:
        """自动发现同义词"""
        print("自动发现同义词...")

        synonym_map = {}
        entity_names = [e.get('concept_name', '') for e in entities if e.get('concept_name')]

        fuzzy_matcher = FuzzyMatcher()

        for i, name1 in enumerate(entity_names):
            matches = fuzzy_matcher.find_matches(name1, entity_names[i+1:], top_k=3)

            for name2, score in matches:
                if score > 0.85:
                    if name1 not in synonym_map:
                        synonym_map[name1] = name2

        self.storage.save_raw_data('fusion', 'synonyms', synonym_map)
        print(f"发现 {len(synonym_map)} 个同义词对")
        return synonym_map


if __name__ == "__main__":
    sources = {
        "MOOCCube": [
            {"concept_id": "CS101", "concept_name": "Python基础", "prerequisites": [], "successors": ["Python进阶"]},
            {"concept_id": "CS102", "concept_name": "Python进阶", "prerequisites": ["Python基础"], "successors": ["Web开发"]},
            {"concept_id": "CS103", "concept_name": "Web开发", "prerequisites": ["Python进阶"], "successors": []}
        ],
        "Wikidata": [
            {"concept_id": "WD_Python", "concept_name": "Python编程语言", "prerequisites": [], "successors": []},
            {"concept_id": "WD_WebDev", "concept_name": "Web开发", "prerequisites": [], "successors": []}
        ],
        "Custom": [
            {"concept_id": "CUST_001", "concept_name": "Python 基础教程", "prerequisites": [], "successors": ["Python进阶"]},
            {"concept_id": "CUST_002", "concept_name": "Python", "prerequisites": [], "successors": []}
        ]
    }

    fusion_manager = KnowledgeFusionManager()
    result = fusion_manager.fuse_knowledge_sources(sources)

    print(f"\n融合结果:")
    print(f"  原始实体总数: {result['metadata']['total_original_entities']}")
    print(f"  融合后实体数: {result['metadata']['total_fused_entities']}")
    print(f"  关系总数: {result['metadata']['total_relations']}")
    print(f"  对齐的实体对: {len(result['alignment']['aligned_pairs'])}")

    print("\n融合后的实体:")
    for entity in result['fused_entities'][:5]:
        print(f"  - {entity.get('concept_name')} (来源: {entity.get('sources', [])})")