"""知识图谱自动构建引擎

该模块实现了从文本数据自动构建知识图谱的完整流程：
1. 数据采集与预处理
2. 实体识别（基于规则、深度学习和大模型）
3. 关系抽取（基于模式和语义理解）
4. 知识融合与去重
5. 质量控制与置信度评估

适用场景：
- 学术文献知识图谱构建
- 企业知识库自动化
- 智能问答系统知识支撑
- 推荐系统特征工程
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import hashlib

from django.db.models import Q
from django.conf import settings

from .models import KnowledgeGraph, KnowledgeNode, KnowledgeRelation
from .llm_integration import LLMService
from .knowledge_graph_engine import KnowledgeGraphEngine

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """提取的实体信息"""
    name: str
    type: str
    description: str = ""
    confidence: float = 0.0
    source_text: str = ""
    start_pos: int = 0
    end_pos: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    category: str = "general"  # concept, application, skill, resource


@dataclass
class ExtractedRelation:
    """提取的关系信息"""
    source_entity: str
    target_entity: str
    relation_type: str
    description: str = ""
    confidence: float = 0.0
    source_text: str = ""
    context: str = ""
    strength: float = 1.0
    bidirectional: bool = False


@dataclass
class PreprocessedDocument:
    """预处理后的文档"""
    id: str
    title: str
    content: str
    cleaned_content: str = ""
    sentences: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    entities: List[ExtractedEntity] = field(default_factory=list)
    relations: List[ExtractedRelation] = field(default_factory=list)


class KnowledgeGraphAutoBuilder:
    """知识图谱自动构建引擎"""
    
    def __init__(self, graph_id: int = None, use_llm: bool = True):
        """初始化知识图谱自动构建引擎
        
        Args:
            graph_id: 知识图谱ID，如果为None则创建新图谱
            use_llm: 是否使用大模型辅助构建
        """
        self.graph_id = graph_id
        self.use_llm = use_llm and getattr(settings, 'DOUBao_API_KEY', '')
        
        # 初始化大模型服务
        self.llm_service = LLMService(provider='doubao') if self.use_llm else None
        
        # 知识图谱引擎
        self.kg_engine = KnowledgeGraphEngine()
        
        # 实体类型定义
        self.entity_types = {
            'concept': ['概念', '定义', '理论', '原理', '模型'],
            'professional_integration': ['应用', '方法', '技术', '算法', '工具', '融合', '跨学科'],
            'skill': ['技能', '能力', '能力', '熟练度'],
            'resource': ['资源', '材料', '文献', '书籍', '课程']
        }
        
        # 关系类型定义
        self.relation_types = {
            'prerequisite': ['前置', '先修', '依赖', '需要', '前提'],
            'related': ['相关', '关联', '类似', '相似'],
            'application': ['应用', '用于', '实现'],
            'advanced': ['进阶', '高级', '深入', '扩展'],
            'professional': ['专业', '领域', '行业']
        }
        
        # 领域特定的实体模式
        self.entity_patterns = {
            'person': r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
            'organization': r'(?:大学|学院|研究所|公司|企业|组织|机构)',
            'location': r'(?:中国|美国|北京|上海|纽约|东京|伦敦)',
            'technology': r'(?:技术|算法|模型|框架|系统|平台)',
            'date': r'(?:19|20)\d{2}[年-]\d{1,2}[月-]?\d{0,2}',
            'percentage': r'\d+(?:\.\d+)?%',
            'quantity': r'\d+(?:,\d{3})*(?:个|种|类|项|条)'
        }
        
        # 停用词列表
        self.stopwords = set([
            '的', '了', '是', '在', '和', '与', '或', '以及',
            '对于', '关于', '通过', '使用', '利用', '采用',
            '可以', '能够', '需要', '要求', '应该', '必须'
        ])
        
        # 已识别的实体缓存（用于去重）
        self._entity_cache: Dict[str, ExtractedEntity] = {}
        self._processed_documents: List[PreprocessedDocument] = []
    
    def build_from_documents(self, documents: List[Dict[str, str]], 
                           graph_name: str = None,
                           merge_existing: bool = True) -> Dict[str, Any]:
        """从文档列表构建知识图谱
        
        Args:
            documents: 文档列表，每个文档包含 title 和 content
            graph_name: 知识图谱名称
            merge_existing: 是否与现有图谱合并
            
        Returns:
            构建结果统计
        """
        logger.info(f"开始从 {len(documents)} 个文档构建知识图谱")
        
        # 1. 创建或获取知识图谱
        if self.graph_id:
            try:
                graph = KnowledgeGraph.objects.get(id=self.graph_id)
            except KnowledgeGraph.DoesNotExist:
                graph = None
        else:
            graph = None
        
        if not graph:
            graph_name = graph_name or f"自动构建知识图谱 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            graph = KnowledgeGraph.objects.create(
                name=graph_name,
                description="由知识图谱自动构建引擎生成"
            )
            self.graph_id = graph.id
        
        # 2. 预处理文档
        logger.info("步骤1: 预处理文档...")
        processed_docs = []
        for doc in documents:
            processed_doc = self._preprocess_document(doc)
            processed_docs.append(processed_doc)
            self._processed_documents.append(processed_doc)
        
        # 3. 提取实体
        logger.info("步骤2: 提取实体...")
        all_entities = []
        for processed_doc in processed_docs:
            entities = self._extract_entities(processed_doc)
            processed_doc.entities = entities
            all_entities.extend(entities)
        
        # 4. 提取关系
        logger.info("步骤3: 提取关系...")
        all_relations = []
        for processed_doc in processed_docs:
            relations = self._extract_relations(processed_doc)
            processed_doc.relations = relations
            all_relations.extend(relations)
        
        # 5. 知识融合
        logger.info("步骤4: 知识融合...")
        merged_entities, merged_relations = self._knowledge_fusion(all_entities, all_relations)
        
        # 6. 保存到数据库
        logger.info("步骤5: 保存到数据库...")
        stats = self._save_to_graph(graph, merged_entities, merged_relations, merge_existing)
        
        # 7. 重建知识图谱索引
        self.kg_engine.build_knowledge_graph(self.graph_id)
        
        logger.info(f"知识图谱构建完成: {stats}")
        return stats
    
    def _preprocess_document(self, doc: Dict[str, str]) -> PreprocessedDocument:
        """预处理单个文档"""
        doc_id = hashlib.md5(doc.get('content', '').encode()).hexdigest()[:16]
        
        # 清洗文本
        cleaned_content = self._clean_text(doc.get('content', ''))
        
        # 句子分割
        sentences = self._split_sentences(cleaned_content)
        
        # 提取标题中的关键词
        title_keywords = self._extract_keywords(doc.get('title', ''))
        
        return PreprocessedDocument(
            id=doc_id,
            title=doc.get('title', ''),
            content=doc.get('content', ''),
            cleaned_content=cleaned_content,
            sentences=sentences,
            metadata={
                'title_keywords': title_keywords,
                'word_count': len(cleaned_content),
                'sentence_count': len(sentences)
            }
        )
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        
        # 规范化空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除多余空白
        text = text.strip()
        
        return text
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        # 中英文句子分割
        sentences = re.split(r'[。！？；\n]+', text)
        
        # 过滤空句子和过短的句子
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return sentences
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单关键词提取：TF-IDF风格
        words = re.findall(r'\b[\w]+\b', text.lower())
        
        # 过滤停用词和过短的词
        keywords = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        # 统计词频
        word_freq = defaultdict(int)
        for word in keywords:
            word_freq[word] += 1
        
        # 返回top 10关键词
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:10]]
    
    def _extract_entities(self, doc: PreprocessedDocument) -> List[ExtractedEntity]:
        """提取实体"""
        entities = []
        
        # 1. 基于规则的方法提取实体
        rule_entities = self._extract_entities_by_rule(doc)
        entities.extend(rule_entities)
        
        # 2. 如果启用大模型，使用大模型提取实体
        if self.use_llm and self.llm_service:
            llm_entities = self._extract_entities_by_llm(doc)
            entities.extend(llm_entities)
        
        # 3. 合并相似实体
        merged_entities = self._merge_similar_entities(entities)
        
        return merged_entities
    
    def _extract_entities_by_rule(self, doc: PreprocessedDocument) -> List[ExtractedEntity]:
        """基于规则提取实体"""
        entities = []
        
        for sentence in doc.sentences[:50]:  # 限制处理句子数量
            # 提取命名实体
            # 人名
            for match in re.finditer(self.entity_patterns['person'], sentence):
                entity = ExtractedEntity(
                    name=match.group(),
                    type='person',
                    description=sentence,
                    confidence=0.8,
                    source_text=sentence,
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                entities.append(entity)
            
            # 组织机构
            for match in re.finditer(self.entity_patterns['organization'], sentence):
                entity = ExtractedEntity(
                    name=match.group(),
                    type='organization',
                    description=sentence,
                    confidence=0.85,
                    source_text=sentence,
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                entities.append(entity)
            
            # 技术术语（基于模式匹配）
            for tech_pattern in [r'\b[\w]+技术\b', r'\b[\w]+算法\b', r'\b[\w]+模型\b']:
                for match in re.finditer(tech_pattern, sentence):
                    name = match.group()
                    if name not in self.stopwords:
                        entity = ExtractedEntity(
                            name=name,
                            type='technology',
                            description=sentence,
                            confidence=0.75,
                            source_text=sentence,
                            start_pos=match.start(),
                            end_pos=match.end()
                        )
                        entities.append(entity)
        
        return entities
    
    def _extract_entities_by_llm(self, doc: PreprocessedDocument) -> List[ExtractedEntity]:
        """使用大模型提取实体"""
        entities = []
        
        try:
            # 构建提示词
            prompt = f"""请从以下文本中提取知识实体（概念、应用、技能、资源），以JSON格式返回：

文档标题：{doc.title}
文档内容（前1000字）：{doc.cleaned_content[:1000]}

要求：
1. 提取所有重要的知识实体
2. 确定每个实体的类型（concept/application/skill/resource）
3. 为每个实体提供简要描述
4. 返回格式示例：
{{
  "entities": [
    {{
      "name": "实体名称",
      "type": "实体类型",
      "description": "实体描述"
    }}
  ]
}}

请只返回JSON，不要添加其他内容。
"""
            
            # 调用大模型
            response = self.llm_service.generate_response(
                prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            # 解析响应
            try:
                result = json.loads(response)
                for entity_data in result.get('entities', []):
                    entity = ExtractedEntity(
                        name=entity_data.get('name', ''),
                        type=entity_data.get('type', 'concept'),
                        description=entity_data.get('description', ''),
                        confidence=0.9,  # 大模型置信度较高
                        source_text=doc.title
                    )
                    entities.append(entity)
            except json.JSONDecodeError:
                logger.warning(f"无法解析大模型返回的实体: {response[:200]}")
                
        except Exception as e:
            logger.error(f"大模型实体提取失败: {e}")
        
        return entities
    
    def _merge_similar_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """合并相似实体"""
        merged = []
        
        for entity in entities:
            # 检查是否与已存在的实体相似
            found = False
            for existing in merged:
                # 名称相似（忽略大小写和空白）
                if (existing.name.lower().strip() == entity.name.lower().strip() or
                    entity.name.lower().strip() in existing.name.lower().strip() or
                    existing.name.lower().strip() in entity.name.lower().strip()):
                    
                    # 合并描述（取更长的）
                    if len(entity.description) > len(existing.description):
                        existing.description = entity.description
                    
                    # 更新置信度（取平均值）
                    existing.confidence = (existing.confidence + entity.confidence) / 2
                    
                    found = True
                    break
            
            if not found:
                merged.append(entity)
        
        return merged
    
    def _extract_relations(self, doc: PreprocessedDocument) -> List[ExtractedRelation]:
        """提取关系"""
        relations = []
        
        # 1. 基于模式的关系抽取
        pattern_relations = self._extract_relations_by_pattern(doc)
        relations.extend(pattern_relations)
        
        # 2. 如果启用大模型，使用大模型抽取关系
        if self.use_llm and self.llm_service:
            llm_relations = self._extract_relations_by_llm(doc)
            relations.extend(llm_relations)
        
        return relations
    
    def _extract_relations_by_pattern(self, doc: PreprocessedDocument) -> List[ExtractedRelation]:
        """基于模式抽取关系"""
        relations = []
        
        # 关系模式定义
        relation_patterns = [
            # A是B的基础/前提
            (r'([^\s，,]+)是([^\s，,]+)的基础', 'prerequisite', 0.8),
            (r'([^\s，,]+)是([^\s，,]+)的前提', 'prerequisite', 0.8),
            (r'([^\s，,]+)需要先掌握([^\s，,]+)', 'prerequisite', 0.75),
            (r'学习([^\s，,]+)之前?先学习([^\s，,]+)', 'prerequisite', 0.75),
            
            # A与B相关
            (r'([^\s，,]+)和([^\s，,]+)相关', 'related', 0.8),
            (r'([^\s，,]+)与([^\s，,]+)相关', 'related', 0.8),
            (r'([^\s，,]+)和([^\s，,]+)类似', 'related', 0.75),
            
            # A应用于B
            (r'([^\s，,]+)应用于([^\s，,]+)', 'application', 0.85),
            (r'([^\s，,]+)用于([^\s，,]+)', 'application', 0.85),
            (r'([^\s，,]+)可以(用来|用于)([^\s，,]+)', 'application', 0.8),
            
            # A是B的进阶
            (r'([^\s，,]+)是([^\s，,]+)的进阶', 'advanced', 0.8),
            (r'([^\s，,]+)是([^\s，,]+)的高级版本', 'advanced', 0.8),
            (r'在([^\s，,]+)基础上学习([^\s，,]+)', 'advanced', 0.75),
        ]
        
        for sentence in doc.sentences[:50]:
            for pattern, rel_type, confidence in relation_patterns:
                for match in re.finditer(pattern, sentence):
                    groups = match.groups()
                    if len(groups) >= 2:
                        source = groups[0].strip()
                        target = groups[1].strip()
                        
                        # 过滤掉太短或包含停用词的实体
                        if (len(source) < 2 or len(target) < 2 or
                            source in self.stopwords or target in self.stopwords):
                            continue
                        
                        relation = ExtractedRelation(
                            source_entity=source,
                            target_entity=target,
                            relation_type=rel_type,
                            description=sentence,
                            confidence=confidence,
                            source_text=sentence,
                            context=sentence[:200]
                        )
                        relations.append(relation)
        
        return relations
    
    def _extract_relations_by_llm(self, doc: PreprocessedDocument) -> List[ExtractedRelation]:
        """使用大模型抽取关系"""
        relations = []
        
        try:
            # 构建提示词
            prompt = f"""请从以下文本中提取知识实体之间的关系，以JSON格式返回：

文档标题：{doc.title}
文档内容（前1500字）：{doc.cleaned_content[:1500]}

要求：
1. 识别文本中的知识实体
2. 确定实体之间的关系类型（prerequisite/related/application/advanced/professional）
3. 关系类型说明：
   - prerequisite: 前置依赖（A是B的基础/前提）
   - related: 相关知识（A与B相关/类似）
   - application: 应用场景（A应用于B）
   - advanced: 进阶知识（A是B的进阶）
   - professional: 专业关联（A属于B领域）

4. 返回格式示例：
{{
  "relations": [
    {{
      "source": "实体A",
      "target": "实体B",
      "type": "关系类型",
      "description": "关系描述"
    }}
  ]
}}

请只返回JSON，不要添加其他内容。
"""
            
            # 调用大模型
            response = self.llm_service.generate_response(
                prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            # 解析响应
            try:
                result = json.loads(response)
                for rel_data in result.get('relations', []):
                    relation = ExtractedRelation(
                        source_entity=rel_data.get('source', ''),
                        target_entity=rel_data.get('target', ''),
                        relation_type=rel_data.get('type', 'related'),
                        description=rel_data.get('description', ''),
                        confidence=0.9,
                        source_text=doc.title
                    )
                    relations.append(relation)
            except json.JSONDecodeError:
                logger.warning(f"无法解析大模型返回的关系: {response[:200]}")
                
        except Exception as e:
            logger.error(f"大模型关系抽取失败: {e}")
        
        return relations
    
    def _knowledge_fusion(self, entities: List[ExtractedEntity], 
                         relations: List[ExtractedRelation]) -> Tuple[List[ExtractedEntity], List[ExtractedRelation]]:
        """知识融合"""
        
        # 1. 实体去重和融合
        fused_entities = self._fuse_entities(entities)
        
        # 2. 关系去重和融合
        fused_relations = self._fuse_relations(relations)
        
        # 3. 实体分类
        for entity in fused_entities:
            entity.category = self._classify_entity(entity)
        
        return fused_entities, fused_relations
    
    def _fuse_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """融合实体"""
        entity_dict: Dict[str, ExtractedEntity] = {}
        
        for entity in entities:
            # 生成实体唯一标识（规范化名称）
            normalized_name = entity.name.lower().strip()
            
            if normalized_name in entity_dict:
                # 融合实体信息
                existing = entity_dict[normalized_name]
                
                # 更新描述（取更长的）
                if len(entity.description) > len(existing.description):
                    existing.description = entity.description
                
                # 更新置信度
                existing.confidence = max(existing.confidence, entity.confidence)
                
                # 合并属性
                existing.attributes.update(entity.attributes)
                
                # 合并别名
                for alias in entity.aliases:
                    if alias not in existing.aliases:
                        existing.aliases.append(alias)
            else:
                entity_dict[normalized_name] = entity
        
        # 过滤低置信度实体
        filtered_entities = [e for e in entity_dict.values() if e.confidence >= 0.5]
        
        return filtered_entities
    
    def _fuse_relations(self, relations: List[ExtractedRelation]) -> List[ExtractedRelation]:
        """融合关系"""
        relation_dict: Dict[Tuple[str, str, str], ExtractedRelation] = {}
        
        for relation in relations:
            # 生成关系唯一标识
            key = (relation.source_entity.lower().strip(),
                   relation.target_entity.lower().strip(),
                   relation.relation_type)
            
            if key in relation_dict:
                # 更新置信度
                existing = relation_dict[key]
                existing.confidence = max(existing.confidence, relation.confidence)
                existing.strength = (existing.strength + relation.strength) / 2
            else:
                relation_dict[key] = relation
        
        # 过滤低置信度关系
        filtered_relations = [r for r in relation_dict.values() if r.confidence >= 0.5]
        
        return filtered_relations
    
    def _classify_entity(self, entity: ExtractedEntity) -> str:
        """分类实体"""
        text = (entity.name + ' ' + entity.description).lower()
        
        # 基于关键词分类
        for category, keywords in self.entity_types.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        # 默认返回concept
        return 'concept'
    
    def _save_to_graph(self, graph: KnowledgeGraph,
                      entities: List[ExtractedEntity],
                      relations: List[ExtractedRelation],
                      merge_existing: bool) -> Dict[str, Any]:
        """保存到知识图谱"""
        stats = {
            'total_entities': len(entities),
            'total_relations': len(relations),
            'new_entities': 0,
            'new_relations': 0,
            'merged_entities': 0,
            'merged_relations': 0
        }
        
        # 1. 保存实体
        existing_nodes = {}
        if merge_existing:
            for node in KnowledgeNode.objects.filter(graph=graph):
                existing_nodes[node.title.lower().strip()] = node
        
        entity_id_map = {}  # 实体名称 -> 节点ID
        
        for entity in entities:
            normalized_name = entity.name.lower().strip()
            
            if normalized_name in existing_nodes:
                # 使用现有节点
                node = existing_nodes[normalized_name]
                stats['merged_entities'] += 1
            else:
                # 创建新节点
                node = KnowledgeNode.objects.create(
                    graph=graph,
                    title=entity.name,
                    type=entity.type,
                    level=self._estimate_difficulty(entity),
                    difficulty=entity.confidence * 5,
                    importance=self._estimate_importance(entity),
                    description=entity.description[:500],
                    professional_group='science',
                    tags=[entity.category]
                )
                stats['new_entities'] += 1
            
            entity_id_map[normalized_name] = node.id
        
        # 2. 保存关系
        existing_relations = set()
        if merge_existing:
            for rel in KnowledgeRelation.objects.filter(graph=graph):
                key = (rel.source.title.lower().strip(),
                       rel.target.title.lower().strip(),
                       rel.relation_type)
                existing_relations.add(key)
        
        for relation in relations:
            source_name = relation.source_entity.lower().strip()
            target_name = relation.target_entity.lower().strip()
            
            # 跳过不存在的实体
            if source_name not in entity_id_map or target_name not in entity_id_map:
                continue
            
            key = (source_name, target_name, relation.relation_type)
            
            if key in existing_relations:
                stats['merged_relations'] += 1
                continue
            
            # 创建关系
            try:
                KnowledgeRelation.objects.create(
                    graph=graph,
                    source_id=entity_id_map[source_name],
                    target_id=entity_id_map[target_name],
                    relation_type=relation.relation_type,
                    strength=relation.strength
                )
                stats['new_relations'] += 1
            except Exception as e:
                logger.warning(f"创建关系失败: {e}")
        
        return stats
    
    def _estimate_difficulty(self, entity: ExtractedEntity) -> int:
        """估计实体难度"""
        # 基于描述长度和置信度估计
        desc_length = len(entity.description)
        
        if desc_length < 50:
            return 1
        elif desc_length < 200:
            return 2
        elif desc_length < 500:
            return 3
        else:
            return 4
    
    def _estimate_importance(self, entity: ExtractedEntity) -> float:
        """估计实体重要性"""
        # 基于置信度和出现频率
        base_importance = entity.confidence
        
        # 如果是核心概念类型，增加重要性
        if entity.type in ['concept', 'technology']:
            base_importance += 0.2
        
        return min(5.0, base_importance * 5)
    
    def build_from_text_corpus(self, texts: List[str], 
                              graph_name: str = None) -> Dict[str, Any]:
        """从文本语料库构建知识图谱
        
        Args:
            texts: 文本列表
            graph_name: 知识图谱名称
            
        Returns:
            构建结果统计
        """
        documents = [{'title': f'文档{i+1}', 'content': text} for i, text in enumerate(texts)]
        return self.build_from_documents(documents, graph_name)
    
    def incremental_build(self, new_documents: List[Dict[str, str]]) -> Dict[str, Any]:
        """增量构建知识图谱
        
        Args:
            new_documents: 新增文档列表
            
        Returns:
            构建结果统计
        """
        if not self.graph_id:
            raise ValueError("增量构建需要指定图谱ID")
        
        try:
            graph = KnowledgeGraph.objects.get(id=self.graph_id)
        except KnowledgeGraph.DoesNotExist:
            raise ValueError(f"图谱ID {self.graph_id} 不存在")
        
        # 执行增量构建
        return self.build_from_documents(
            new_documents,
            graph_name=graph.name,
            merge_existing=True
        )


class KnowledgeGraphQualityChecker:
    """知识图谱质量检查器"""
    
    def __init__(self, graph_id: int):
        self.graph_id = graph_id
    
    def check_completeness(self) -> Dict[str, Any]:
        """检查知识图谱完整性"""
        graph = KnowledgeGraph.objects.get(id=self.graph_id)
        
        nodes = KnowledgeNode.objects.filter(graph=graph)
        relations = KnowledgeRelation.objects.filter(graph=graph)
        
        return {
            'total_nodes': nodes.count(),
            'total_relations': relations.count(),
            'avg_relations_per_node': relations.count() / max(1, nodes.count()),
            'isolated_nodes': self._find_isolated_nodes(nodes, relations),
            'orphaned_nodes': self._find_orphaned_nodes(nodes, relations)
        }
    
    def _find_isolated_nodes(self, nodes, relations) -> int:
        """查找孤立节点"""
        connected_node_ids = set()
        for rel in relations:
            connected_node_ids.add(rel.source_id)
            connected_node_ids.add(rel.target_id)
        
        return nodes.count() - len(connected_node_ids)
    
    def _find_orphaned_nodes(self, nodes, relations) -> int:
        """查找孤儿节点（没有入边或出边）"""
        # 这里可以实现更复杂的逻辑
        return 0
    
    def check_consistency(self) -> List[Dict[str, Any]]:
        """检查知识图谱一致性"""
        issues = []
        
        graph = KnowledgeGraph.objects.get(id=self.graph_id)
        
        # 检查循环依赖
        relations = KnowledgeRelation.objects.filter(graph=graph)
        
        # 构建图
        G = nx.DiGraph()
        for rel in relations:
            G.add_edge(rel.source_id, rel.target_id, relation_type=rel.relation_type)
        
        # 检测环
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                issues.append({
                    'type': 'cycle',
                    'message': f'发现 {len(cycles)} 个循环依赖',
                    'details': cycles[:5]
                })
        except:
            pass
        
        # 检查孤立节点
        completeness = self.check_completeness()
        if completeness['isolated_nodes'] > 0:
            issues.append({
                'type': 'isolated_nodes',
                'message': f'发现 {completeness["isolated_nodes"]} 个孤立节点',
                'count': completeness['isolated_nodes']
            })
        
        return issues
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """生成质量报告"""
        return {
            'graph_id': self.graph_id,
            'completeness': self.check_completeness(),
            'consistency_issues': self.check_consistency(),
            'overall_score': self._calculate_overall_score()
        }
    
    def _calculate_overall_score(self) -> float:
        """计算总体质量分数"""
        completeness = self.check_completeness()
        issues = self.check_consistency()
        
        base_score = 1.0
        
        # 扣分项
        base_score -= len(issues) * 0.1
        base_score -= completeness['isolated_nodes'] * 0.01
        
        return max(0.0, min(1.0, base_score))


# 便捷函数
def build_knowledge_graph_from_texts(texts: List[str], 
                                     graph_name: str = None) -> Dict[str, Any]:
    """从文本列表构建知识图谱"""
    builder = KnowledgeGraphAutoBuilder(use_llm=True)
    return builder.build_from_text_corpus(texts, graph_name)


def incremental_extend_knowledge_graph(graph_id: int, 
                                       new_texts: List[str]) -> Dict[str, Any]:
    """增量扩展知识图谱"""
    builder = KnowledgeGraphAutoBuilder(graph_id=graph_id, use_llm=True)
    return builder.build_from_text_corpus(new_texts)
