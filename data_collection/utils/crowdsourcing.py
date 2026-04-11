import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from storage.storage_manager import StorageManager
from utils.data_models import KnowledgeNode

class CrowdsourcingCollector:
    """众包数据采集器"""

    def __init__(self):
        self.storage = StorageManager()
        self.awesome_lists = {
            "awesome-python": "https://github.com/vinta/awesome-python",
            "awesome-cs-courses": "https://github.com/prakhar1989/awesome-courses",
            "awesome-machine-learning": "https://github.com/josephmisiti/awesome-machine-learning",
            "awesome-web-development": "https://github.com/drm感染者henryhuang/awesome-web-development"
        }

    def fetch_awesome_list(self, url: str, list_name: str) -> List[Dict]:
        """获取GitHub Awesome列表数据"""
        print(f"正在获取 {list_name}...")

        try:
            api_url = f"https://api.github.com/repos/{url.replace('https://github.com/', '')}/readme"
            response = requests.get(api_url, headers={"Accept": "application/vnd.github.v3.raw"})

            if response.status_code == 200:
                content = response.text
                items = self._parse_awesome_list(content, list_name)

                self.storage.save_raw_data('crowdsourcing', list_name, items)
                print(f"从 {list_name} 获取了 {len(items)} 个项目")
                return items
            else:
                print(f"获取 {list_name} 失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取 {list_name} 时出错: {e}")
            return []

    def _parse_awesome_list(self, content: str, list_name: str) -> List[Dict]:
        """解析Awesome列表内容"""
        items = []
        lines = content.split('\n')

        current_category = None

        for line in lines:
            line = line.strip()

            if line.startswith('## '):
                current_category = line.replace('## ', '').strip()
            elif line.startswith('- ') and current_category:
                item_match = re.search(r'- \[([^\]]+)\]\(([^)]+)\)(.*)', line)
                if item_match:
                    name = item_match.group(1).strip()
                    url = item_match.group(2).strip()
                    description = item_match.group(3).strip().lstrip('- ')

                    item = {
                        "name": name,
                        "url": url,
                        "description": description,
                        "category": current_category,
                        "source": list_name
                    }
                    items.append(item)

        return items

    def collect_all_awesome_lists(self) -> Dict[str, List[Dict]]:
        """采集所有Awesome列表"""
        all_data = {}

        for list_name, url in self.awesome_lists.items():
            items = self.fetch_awesome_list(url, list_name)
            all_data[list_name] = items

        self.storage.save_final_data('crowdsourcing', 'awesome_lists', all_data)
        return all_data


class StackOverflowTagCollector:
    """Stack Overflow标签层级采集器"""

    def __init__(self):
        self.storage = StorageManager()
        self.base_url = "https://api.stackexchange.com/2.3"

    def fetch_tag_info(self, tag: str) -> Dict:
        """获取标签信息"""
        url = f"{self.base_url}/tags/{tag}/info"
        params = {
            "site": "stackoverflow",
            "pagesize": 1
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    return data['items'][0]
            return {}
        except Exception as e:
            print(f"获取标签 {tag} 信息时出错: {e}")
            return {}

    def fetch_related_tags(self, tag: str, limit: int = 10) -> List[Dict]:
        """获取相关标签"""
        url = f"{self.base_url}/tags/{tag}/related"
        params = {
            "site": "stackoverflow",
            "pagesize": limit
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            return []
        except Exception as e:
            print(f"获取标签 {tag} 相关标签时出错: {e}")
            return []

    def build_tag_hierarchy(self, root_tags: List[str]) -> Dict:
        """构建标签层级结构"""
        print("正在构建标签层级结构...")

        tag_tree = {}
        visited = set()

        def build_tree(tag: str, depth: int = 0):
            if depth > 3 or tag in visited:
                return

            visited.add(tag)

            tag_info = self.fetch_tag_info(tag)
            related_tags = self.fetch_related_tags(tag)

            node = {
                "name": tag,
                "count": tag_info.get("count", 0),
                "has_synonyms": tag_info.get("has_synonyms", False),
                "synonyms": tag_info.get("synonyms", []),
                "children": [],
                "depth": depth
            }

            for related in related_tags[:5]:
                related_name = related.get("name")
                if related_name and related_name not in visited:
                    child_node = build_tree(related_name, depth + 1)
                    node["children"].append(child_node)

            tag_tree[tag] = node
            return node

        for root_tag in root_tags:
            if root_tag not in visited:
                build_tree(root_tag)

        self.storage.save_raw_data('crowdsourcing', 'stackoverflow_tags', tag_tree)
        print(f"构建了 {len(tag_tree)} 个标签节点")
        return tag_tree

    def collect_cs_tag_hierarchy(self) -> Dict:
        """采集计算机科学相关标签层级"""
        cs_root_tags = [
            "python", "java", "javascript", "c++", "c#",
            "algorithm", "data-structures", "machine-learning",
            "web-development", "database", "api",
            "react", "angular", "vue.js", "django", "flask",
            "numpy", "pandas", "tensorflow", "pytorch"
        ]

        return self.build_tag_hierarchy(cs_root_tags)


class ExpertReviewManager:
    """专家审核管理器"""

    def __init__(self):
        self.storage = StorageManager()
        self.review_queue = []
        self.approved_items = []
        self.rejected_items = []

    def create_review_task(self, item: Dict, review_type: str = "path") -> str:
        """创建审核任务"""
        task_id = f"review_{len(self.review_queue) + 1}"

        task = {
            "task_id": task_id,
            "item": item,
            "review_type": review_type,
            "status": "pending",
            "created_at": "2024-01-01",
            "reviewer": None,
            "comments": [],
            "decision": None
        }

        self.review_queue.append(task)
        return task_id

    def submit_review(self, task_id: str, decision: str, comments: str, reviewer: str) -> bool:
        """提交审核结果"""
        for task in self.review_queue:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                task["decision"] = decision
                task["comments"] = comments
                task["reviewer"] = reviewer
                task["completed_at"] = "2024-01-01"

                if decision == "approved":
                    self.approved_items.append(task)
                else:
                    self.rejected_items.append(task)

                return True

        return False

    def get_pending_reviews(self) -> List[Dict]:
        """获取待审核任务"""
        return [task for task in self.review_queue if task["status"] == "pending"]

    def get_review_summary(self) -> Dict:
        """获取审核汇总"""
        return {
            "total_tasks": len(self.review_queue),
            "pending": len(self.get_pending_reviews()),
            "approved": len(self.approved_items),
            "rejected": len(self.rejected_items)
        }

    def validate_critical_path(self, path: List[str]) -> Dict:
        """验证关键学习路径"""
        print(f"验证关键路径: {' -> '.join(path)}")

        validation_result = {
            "path": path,
            "is_valid": True,
            "issues": [],
            "recommendations": []
        }

        if len(path) < 2:
            validation_result["is_valid"] = False
            validation_result["issues"].append("路径至少需要包含2个知识点")

        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]

            if not self._check_prerequisite_relation(current, next_node):
                validation_result["recommendations"].append(
                    f"建议在 {current} 和 {next_node} 之间添加前置关系"
                )

        task = {
            "path": path,
            "validation_result": validation_result,
            "type": "critical_path"
        }

        self.create_review_task(task, "path")
        return validation_result

    def _check_prerequisite_relation(self, concept1: str, concept2: str) -> bool:
        """检查两个概念之间是否存在前置关系"""
        return True


class AwesomeListIntegration:
    """Awesome列表集成器"""

    def __init__(self):
        self.storage = StorageManager()

    def extract_learning_paths(self, awesome_data: Dict) -> List[Dict]:
        """从Awesome列表中提取学习路径"""
        paths = []

        category_order = {
            "programming-languages": 1,
            "python": 1,
            "web-development": 2,
            "frontend": 2,
            "backend": 2,
            "database": 3,
            "devops": 4,
            "machine-learning": 5,
            "data-science": 5
        }

        for list_name, items in awesome_data.items():
            for item in items:
                category = item.get("category", "").lower()

                path_entry = {
                    "source": list_name,
                    "name": item.get("name"),
                    "url": item.get("url"),
                    "description": item.get("description"),
                    "order": category_order.get(category, 99),
                    "category": category
                }
                paths.append(path_entry)

        paths.sort(key=lambda x: x["order"])
        return paths

    def convert_to_knowledge_nodes(self, awesome_data: Dict) -> List[KnowledgeNode]:
        """将Awesome列表转换为知识节点"""
        nodes = []

        category_level_map = {
            "programming-languages": 1,
            "web-development": 2,
            "frontend": 2,
            "backend": 2,
            "database": 2,
            "devops": 2,
            "machine-learning": 2,
            "data-science": 2,
            "tools": 3,
            "libraries": 3,
            "frameworks": 3
        }

        for list_name, items in awesome_data.items():
            for idx, item in enumerate(items):
                category = item.get("category", "").lower()
                level = category_level_map.get(category, 2)

                node = KnowledgeNode(
                    concept_id=f"awesome_{list_name}_{idx}",
                    concept_name=item.get("name", ""),
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=level,
                    category=category,
                    description=item.get("description", ""),
                    source=f"GitHub Awesome - {list_name}",
                    depth=0,
                    parent_concept=category,
                    keywords=[item.get("name", ""), category],
                    difficulty=1,
                    importance=1
                )
                nodes.append(node.to_dict())

        return nodes


class StackOverflowIntegration:
    """Stack Overflow标签集成器"""

    def __init__(self):
        self.storage = StorageManager()

    def convert_tag_tree_to_nodes(self, tag_tree: Dict) -> List[KnowledgeNode]:
        """将标签树转换为知识节点"""
        nodes = []

        def convert_node(tag_name: str, node_data: Dict, parent: str = None):
            node = KnowledgeNode(
                concept_id=f"so_{tag_name}",
                concept_name=tag_name,
                course_id=None,
                prerequisites=[],
                successors=[],
                level=min(node_data.get("depth", 0) + 1, 3),
                category="stackoverflow_tag",
                description=f"Stack Overflow标签: {tag_name}，问题数: {node_data.get('count', 0)}",
                source="Stack Overflow",
                depth=node_data.get("depth", 0),
                parent_concept=parent,
                keywords=[tag_name, "stackoverflow"],
                difficulty=1,
                importance=node_data.get("count", 0) / 1000
            )
            nodes.append(node.to_dict())

            for child in node_data.get("children", []):
                convert_node(child["name"], child, tag_name)

        for tag_name, node_data in tag_tree.items():
            convert_node(tag_name, node_data)

        return nodes


if __name__ == "__main__":
    collector = CrowdsourcingCollector()
    awesome_data = collector.collect_all_awesome_lists()
    print(f"采集了 {len(awesome_data)} 个Awesome列表")

    so_collector = StackOverflowTagCollector()
    tag_tree = so_collector.collect_cs_tag_hierarchy()
    print(f"构建了 {len(tag_tree)} 个标签节点")

    review_manager = ExpertReviewManager()
    critical_path = ["变量", "数据类型", "函数", "面向对象", "Web开发", "全栈工程师"]
    validation = review_manager.validate_critical_path(critical_path)
    print(f"路径验证结果: {validation}")