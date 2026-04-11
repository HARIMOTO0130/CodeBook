import json
import re
from typing import List, Dict, Tuple, Optional
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode

class LLMPrompter:
    """大语言模型辅助生成器 - Self-Prompting Framework"""

    def __init__(self):
        self.storage = StorageManager()
        self.relation_synonyms = {}
        self.synthetic_samples = []
        self.extracted_triplets = []

    def generate_relation_synonyms(self, relations: List[str], llm_api=None) -> Dict[str, List[str]]:
        """
        第一轮：生成关系同义词
        例如："包含" → ["包括", "涵盖", "含有", "包含有"]
        """
        print("第一轮：生成关系同义词...")

        default_synonyms = {
            "包含": ["包括", "涵盖", "含有", "包含有", "涉及"],
            "依赖": ["需要", "要求", "基于", "取决于"],
            "前置": ["基础", "前提", "先决条件", "需要先学"],
            "后继": ["进阶", "后续", "延伸", "高级"],
            "属于": ["是", "归类于", "归属于", "类别为"],
            "类型": ["类别", "种类", "分类", "类型为"],
            "实现": ["实现方式", "通过", "使用", "采用"],
            "应用": ["用途", "使用场景", "应用场景", "使用于"],
            "学习": ["掌握", "了解", "学会", "习得"],
            "概念": ["知识点", "概念", "理论", "原理"]
        }

        if llm_api:
            try:
                prompt = f"""请为以下关系生成同义词列表（每个关系至少5个同义词）：
关系列表：{', '.join(relations)}

请按以下JSON格式输出：
{{
    "关系1": ["同义词1", "同义词2", ...],
    "关系2": ["同义词1", "同义词2", ...]
}}

只输出JSON，不要其他内容。"""

                result = llm_api.generate(prompt)
                synonyms = json.loads(result)
                self.relation_synonyms = synonyms
            except Exception as e:
                print(f"LLM API调用失败，使用默认同义词: {e}")
                self.relation_synonyms = default_synonyms
        else:
            self.relation_synonyms = default_synonyms

        self.storage.save_raw_data('llm', 'relation_synonyms', self.relation_synonyms)
        print(f"生成了 {len(self.relation_synonyms)} 个关系的同义词")
        return self.relation_synonyms

    def generate_synthetic_samples(self, templates: List[str], concepts: List[str], count: int = 100) -> List[Dict]:
        """
        第二轮：生成合成样本作为训练数据
        基于模板和概念生成多样化的训练样本
        """
        print(f"第二轮：生成 {count} 个合成样本...")

        synthetic_samples = []
        relations = list(self.relation_synonyms.keys())

        for i in range(count):
            import random
            template = random.choice(templates)
            relation = random.choice(relations) if relations else "包含"
            concept1 = random.choice(concepts) if concepts else f"概念{i % 10}"
            concept2 = random.choice(concepts) if concepts else f"概念{(i + 1) % 10}"

            synonyms = self.relation_synonyms.get(relation, ["包含"])
            relation_variant = random.choice(synonyms)

            text = template.format(
                concept1=concept1,
                concept2=concept2,
                relation=relation_variant
            )

            sample = {
                "id": f"synthetic_{i+1}",
                "text": text,
                "concept1": concept1,
                "concept2": concept2,
                "relation": relation,
                "relation_variant": relation_variant,
                "template": template,
                "source": "synthetic"
            }
            synthetic_samples.append(sample)

        self.synthetic_samples = synthetic_samples
        self.storage.save_raw_data('llm', 'synthetic_samples', synthetic_samples)
        print(f"生成了 {len(synthetic_samples)} 个合成样本")
        return synthetic_samples

    def extract_triplets(self, texts: List[str], llm_api=None) -> List[Tuple[str, str, str]]:
        """
        第三轮：从文本中抽取实体-关系-实体三元组
        使用LLM或规则进行抽取
        """
        print(f"第三轮：从 {len(texts)} 个文本中抽取三元组...")

        triplets = []

        if llm_api:
            try:
                for text in texts:
                    prompt = f"""从以下Python教程文本中抽取知识点三元组。
文本：{text}

请按以下格式输出三元组（每行一个）：
<实体1, 关系, 实体2>

示例：<列表推导式, 是一种, 创建列表方法>, <列表推导式, 基于, for循环>

只输出三元组，不要其他内容。"""

                    result = llm_api.generate(prompt)
                    extracted = self._parse_triplets(result)
                    triplets.extend(extracted)
            except Exception as e:
                print(f"LLM API调用失败，使用规则抽取: {e}")
                triplets = self._rule_based_extraction(texts)
        else:
            triplets = self._rule_based_extraction(texts)

        self.extracted_triplets = triplets
        self.storage.save_raw_data('llm', 'extracted_triplets', triplets)
        print(f"抽取了 {len(triplets)} 个三元组")
        return triplets

    def _parse_triplets(self, llm_output: str) -> List[Tuple[str, str, str]]:
        """解析LLM输出的三元组"""
        triplets = []
        pattern = r'<([^,]+),\s*([^,]+),\s*([^>]+)>'
        matches = re.findall(pattern, llm_output)

        for match in matches:
            entity1 = match[0].strip()
            relation = match[1].strip()
            entity2 = match[2].strip()
            triplets.append((entity1, relation, entity2))

        return triplets

    def _rule_based_extraction(self, texts: List[str]) -> List[Tuple[str, str, str]]:
        """基于规则的三元组抽取"""
        triplets = []

        relation_patterns = {
            "是一种": ["是", "属于", "为", "为一种"],
            "基于": ["基于", "依靠", "依赖", "使用"],
            "包含": ["包含", "包括", "涵盖", "含有"],
            "需要先学": ["需要先学", "前置", "基础是"],
            "进阶到": ["进阶到", "后续为", "高级为"]
        }

        for text in texts:
            for relation, variants in relation_patterns.items():
                for variant in variants:
                    if variant in text:
                        parts = text.split(variant)
                        if len(parts) == 2:
                            entity1 = parts[0].strip()
                            entity2 = parts[1].strip()
                            if entity1 and entity2:
                                triplets.append((entity1, relation, entity2))

        return triplets

    def generate_from_text_corpus(self, corpus: List[str], llm_api=None) -> Dict:
        """
        从文本语料库生成知识图谱
        完整的三轮流程
        """
        print("开始从文本语料库生成知识图谱...")

        unique_relations = set()
        for text in corpus:
            for relation in ["包含", "依赖", "前置", "后继", "属于", "类型", "实现", "应用"]:
                if relation in text:
                    unique_relations.add(relation)

        self.generate_relation_synonyms(list(unique_relations), llm_api)

        concepts = self._extract_concepts_from_corpus(corpus)
        templates = [
            "{concept1}{relation}{concept2}",
            "{concept1}是{concept2}的{relation}",
            "学习{concept1}之前需要先掌握{concept2}",
            "{concept1}进阶后会学到{concept2}",
            "{concept1}和{concept2}都是{relation}"
        ]
        self.generate_synthetic_samples(templates, concepts, count=len(corpus))

        self.extract_triplets(corpus, llm_api)

        knowledge_graph = {
            "relation_synonyms": self.relation_synonyms,
            "synthetic_samples": self.synthetic_samples,
            "triplets": self.extracted_triplets,
            "metadata": {
                "total_samples": len(self.synthetic_samples),
                "total_triplets": len(self.extracted_triplets),
                "unique_relations": len(unique_relations),
                "source": "llm_generation"
            }
        }

        self.storage.save_final_data('llm', 'knowledge_graph', knowledge_graph)
        print("知识图谱生成完成")
        return knowledge_graph

    def _extract_concepts_from_corpus(self, corpus: List[str]) -> List[str]:
        """从语料库中提取概念"""
        concepts = set()

        for text in corpus:
            words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text)
            for word in words:
                if len(word) >= 2:
                    concepts.add(word)

        return list(concepts)[:100]


class RelationSynonymGenerator:
    """关系同义词生成器"""

    def __init__(self):
        self.synonym_dict = {
            "包含": ["包括", "涵盖", "含有", "囊括", "包含有", "涉及"],
            "依赖": ["需要", "要求", "基于", "取决于", "以...为基础"],
            "前置": ["基础", "前提", "先决条件", "需要先学", "前置知识"],
            "后继": ["进阶", "后续", "延伸", "高级", "深入"],
            "属于": ["是", "归类于", "归属于", "类别为", "类型为"],
            "实现": ["实现方式", "通过", "使用", "采用", "运用"],
            "应用": ["用途", "使用场景", "应用场景", "使用于", "运用于"],
            "学习": ["掌握", "了解", "学会", "习得", "精通"],
            "概念": ["知识点", "概念", "理论", "原理", "知识"],
            "类型": ["类别", "种类", "分类", "类型为", "形式"],
            "基于": ["依据", "根据", "基于", "来源于", "源自"],
            "用于": ["应用于", "使用于", "适用于", "用于"],
            "创建": ["建立", "创建", "生成", "编写", "开发"],
            "处理": ["操作", "处理", "加工", "运算", "计算"]
        }

    def get_synonyms(self, relation: str) -> List[str]:
        """获取关系的同义词列表"""
        return self.synonym_dict.get(relation, [])

    def expand_text(self, text: str) -> List[str]:
        """扩展文本中的关系词为同义词"""
        expanded_texts = [text]

        for relation, synonyms in self.synonym_dict.items():
            for synonym in synonyms:
                if synonym in text:
                    for alt_synonym in synonyms:
                        if alt_synonym != synonym:
                            new_text = text.replace(synonym, alt_synonym)
                            expanded_texts.append(new_text)

        return expanded_texts


class SyntheticSampleGenerator:
    """合成样本生成器"""

    def __init__(self):
        self.templates = {
            "definition": [
                "{concept1}{relation}{concept2}",
                "{concept1}是{concept2}的一种",
                "{concept1}即{concept2}",
                "{concept1}指的是{concept2}"
            ],
            "prerequisite": [
                "学习{concept1}需要先掌握{concept2}",
                "{concept1}的基础是{concept2}",
                "在学习{concept1}之前，应当先了解{concept2}",
                "{concept1}的前提知识包括{concept2}"
            ],
            "progression": [
                "学完{concept1}后可以继续学习{concept2}",
                "{concept1}进阶后会学到{concept2}",
                "{concept1}的进阶内容是{concept2}",
                "掌握{concept1}后可以过渡到{concept2}"
            ],
            "application": [
                "{concept1}常用于{concept2}",
                "{concept1}的应用场景包括{concept2}",
                "{concept1}在实际项目中用于{concept2}",
                "{concept1}可以应用于{concept2}"
            ]
        }

    def generate(self, concepts: List[str], count: int = 100) -> List[Dict]:
        """生成合成样本"""
        import random
        samples = []

        for i in range(count):
            template_type = random.choice(list(self.templates.keys()))
            template = random.choice(self.templates[template_type])
            concept1 = random.choice(concepts) if concepts else f"概念{i % 10}"
            concept2 = random.choice(concepts) if concepts else f"概念{(i + 1) % 10}"

            text = template.format(concept1=concept1, concept2=concept2)

            sample = {
                "id": f"sample_{i+1}",
                "text": text,
                "template_type": template_type,
                "concept1": concept1,
                "concept2": concept2,
                "source": "synthetic"
            }
            samples.append(sample)

        return samples


class TripletExtractor:
    """三元组抽取器"""

    def __init__(self):
        self.patterns = {
            "definition": r"(.+?)(?:是|即|指的是|即指)(.+?)(?:的|一种|一种|)",
            "prerequisite": r"(.+?)(?:需要|前提|基础是|先学|先了解)(.+?)(?:的|后|再|)",
            "progression": r"(.+?)(?:进阶|后续|过渡到|继续学习)(.+?)(?:的|后|内容|)",
            "application": r"(.+?)(?:用于|应用|使用于|运用于)(.+?)(?:的|场景|中|)"
        }

    def extract(self, texts: List[str]) -> List[Tuple[str, str, str]]:
        """从文本中抽取三元组"""
        triplets = []

        for text in texts:
            for relation, pattern in self.patterns.items():
                matches = re.findall(pattern, text)
                for match in matches:
                    if len(match) >= 2:
                        entity1 = match[0].strip()
                        entity2 = match[1].strip()
                        if entity1 and entity2:
                            triplets.append((entity1, relation, entity2))

        return triplets


if __name__ == "__main__":
    prompter = LLMPrompter()

    sample_corpus = [
        "列表推导式是Python中一种简洁的创建列表的方法，它基于for循环和条件表达式",
        "学习Python需要先掌握变量和数据类型",
        "Python的基础包括基本语法、数据类型、控制流",
        "学完基础语法后可以继续学习函数和模块",
        "面向对象编程是Python的重要组成部分",
        "Django是一个Python Web框架",
        "学习Web开发需要先掌握HTML、CSS、JavaScript",
        "Flask是Python的轻量级Web框架",
        "数据分析需要掌握Pandas和NumPy",
        "机器学习是人工智能的一个分支"
    ]

    result = prompter.generate_from_text_corpus(sample_corpus)
    print(json.dumps(result, ensure_ascii=False, indent=2))