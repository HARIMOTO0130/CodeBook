"""个性化学习路径生成算法，结合知识图谱和大模型"""

from typing import Dict, Any, List
from django.db.models import Q
from .models import KnowledgeGraph, KnowledgeNode, KnowledgeRelation, User, LearningStyle, KnowledgeMastery
from .knowledge_graph_engine import KnowledgeGraphEngine
from .llm_integration import LLMService


class PersonalizedLearningPathGenerator:
    """个性化学习路径生成器"""
    
    def __init__(self):
        self.kg_engine = KnowledgeGraphEngine()
        self.llm_service = LLMService()
        # 初始化时不构建完整图谱，而是在需要时根据用户专业组构建
        # 这样可以节省资源，并确保使用最新的用户专业组信息
        
        # 添加缓存机制
        self._graph_cache = {}
        self._user_profile_cache = {}
        self._path_cache = {}
        
        # 设置缓存过期时间（秒）
        self._CACHE_EXPIRY = 300  # 5分钟
    
    def generate_learning_path(self, user: User, learning_goal: str, max_nodes: int = 10) -> Dict[str, Any]:
        """生成个性化学习路径
        
        Args:
            user: 用户对象
            learning_goal: 学习目标
            max_nodes: 最大节点数量
        
        Returns:
            个性化学习路径，包含路径节点、解释和建议
        """
        import time
        current_time = time.time()
        
        # 生成缓存键
        user_id = user.id if hasattr(user, 'id') else 'anonymous'
        path_cache_key = f"{user_id}:{learning_goal}:{max_nodes}"
        
        # 检查路径缓存
        if path_cache_key in self._path_cache:
            cached_data = self._path_cache[path_cache_key]
            if current_time - cached_data['timestamp'] < self._CACHE_EXPIRY:
                print(f"[DEBUG] 使用缓存的学习路径结果")
                return cached_data['data']
        
        try:
            print(f"\n[DEBUG] 开始生成个性化学习路径")
            print(f"[DEBUG] 学习目标: {learning_goal}")
            print(f"[DEBUG] 最大节点数量: {max_nodes}")
            
            # 1. 获取用户画像（带缓存）
            user_profile_cache_key = f"user_profile:{user_id}"
            if user_profile_cache_key in self._user_profile_cache:
                cached_profile = self._user_profile_cache[user_profile_cache_key]
                if current_time - cached_profile['timestamp'] < self._CACHE_EXPIRY:
                    print(f"[DEBUG] 使用缓存的用户画像")
                    user_profile = cached_profile['data']
                else:
                    user_profile = self._get_user_profile(user)
                    self._user_profile_cache[user_profile_cache_key] = {
                        'data': user_profile,
                        'timestamp': current_time
                    }
            else:
                user_profile = self._get_user_profile(user)
                self._user_profile_cache[user_profile_cache_key] = {
                    'data': user_profile,
                    'timestamp': current_time
                }
            print(f"[DEBUG] 用户画像: {user_profile}")
            
            # 2. 根据用户专业组构建知识图谱（带缓存）
            professional_group = user_profile.get('professional_group', 'science')
            graph_cache_key = f"graph:{professional_group}"
            
            if graph_cache_key in self._graph_cache:
                cached_graph = self._graph_cache[graph_cache_key]
                if current_time - cached_graph['timestamp'] < self._CACHE_EXPIRY:
                    print(f"[DEBUG] 使用缓存的知识图谱")
                    # 直接使用缓存的图谱数据，无需重新构建
                else:
                    print(f"[DEBUG] 使用专业组: {professional_group}构建知识图谱")
                    self.kg_engine.build_knowledge_graph(professional_group=professional_group)
                    self._graph_cache[graph_cache_key] = {
                        'timestamp': current_time
                    }
            else:
                print(f"[DEBUG] 使用专业组: {professional_group}构建知识图谱")
                self.kg_engine.build_knowledge_graph(professional_group=professional_group)
                self._graph_cache[graph_cache_key] = {
                    'timestamp': current_time
                }
            print(f"[DEBUG] 知识图谱构建完成，节点数量: {len(self.kg_engine.graph.nodes)}, 边数量: {len(self.kg_engine.graph.edges)}")
            
            # 3. 使用知识图谱生成初始路径
            initial_path = self.kg_engine.get_recommended_path(user_profile, learning_goal, max_nodes)
            print(f"[DEBUG] 知识图谱生成的初始路径: {initial_path}")
            
            if not initial_path:
                # 如果知识图谱无法生成路径，创建默认路径
                print(f"[DEBUG] 知识图谱无法生成路径，创建默认路径")
                initial_path = self._create_default_path(learning_goal, max_nodes)
            
            # 4. 使用大模型优化学习路径
            try:
                print(f"[DEBUG] 开始使用大模型优化学习路径")
                optimized_path = self._optimize_path_with_llm(initial_path, user_profile)
                print(f"[DEBUG] 大模型优化后的路径: {optimized_path}")
            except Exception as e:
                print(f"[DEBUG] 优化学习路径失败: {e}")
                optimized_path = initial_path
            
            # 5. 生成学习路径解释
            try:
                print(f"[DEBUG] 开始生成学习路径解释")
                path_explanation = self.llm_service.generate_learning_path_explanation(optimized_path, user_profile)
                print(f"[DEBUG] 生成的路径解释: {path_explanation[:100]}...")
            except Exception as e:
                print(f"[DEBUG] 生成路径解释失败: {e}")
                path_explanation = f"为您生成了{learning_goal}的个性化学习路径，包含{len(optimized_path)}个核心知识点，建议按照顺序学习。"
            
            # 6. 生成个性化学习建议
            try:
                print(f"[DEBUG] 开始生成个性化学习建议")
                personalized_suggestions = self._generate_personalized_suggestions(optimized_path, user_profile)
                print(f"[DEBUG] 生成的个性化建议: {personalized_suggestions}")
            except Exception as e:
                print(f"[DEBUG] 生成个性化建议失败: {e}")
                personalized_suggestions = [
                    "建议按照从基础到高级的顺序学习",
                    "定期复习已学内容，加深理解",
                    "多做实践练习，巩固所学知识",
                    "遇到问题及时查阅资料或向老师请教",
                    "制定合理的学习计划，保持学习节奏"
                ]
            
            result = {
                "path": optimized_path,
                "explanation": path_explanation,
                "suggestions": personalized_suggestions,
                "user_profile": user_profile
            }
            
            # 更新路径缓存
            self._path_cache[path_cache_key] = {
                'data': result,
                'timestamp': current_time
            }
            
            print(f"[DEBUG] 最终生成的学习路径结果: {result}")
            return result
        except Exception as e:
            print(f"生成个性化学习路径失败: {e}")
            # 返回完整的回退响应
            fallback_path = self._create_default_path(learning_goal, max_nodes)
            return {
                "path": fallback_path,
                "explanation": f"为您生成了{learning_goal}的基础学习路径，建议按照顺序学习。",
                "suggestions": [
                    "建议每天学习1-2个知识点",
                    "结合实际项目进行练习",
                    "定期复习已学内容",
                    "关注知识点之间的联系",
                    "保持持续学习的习惯"
                ],
                "user_profile": self._get_user_profile(user)
            }
    
    def _create_default_path(self, learning_goal: str, max_nodes: int = 10) -> List[Dict[str, Any]]:
        """创建默认学习路径
        
        Args:
            learning_goal: 学习目标
            max_nodes: 最大节点数量
        
        Returns:
            默认学习路径
        """
        default_path = []
        for i in range(min(5, max_nodes)):
            default_path.append({
                "id": i + 1,
                "title": f"{learning_goal} - 阶段{i+1}",
                "type": "concept" if i == 0 else "skill",
                "level": 1 + i,
                "difficulty": 1.0 + i * 1.0,
                "importance": 5.0 - i * 0.5,
                "description": f"{learning_goal}的第{i+1}个学习阶段，重点掌握相关基础概念和实践技能。",
                "professional_group": "science",
                "tags": [learning_goal, f"阶段{i+1}"]
            })
        return default_path
    
    def _get_user_profile(self, user: User) -> Dict[str, Any]:
        """获取用户画像
        
        Args:
            user: 用户对象
        
        Returns:
            用户画像字典
        """
        # 1. 基本信息
        professional_group = 'science'  # 默认值
        # 优先使用UserPreferences中的major_category
        if hasattr(user, 'preferences') and user.preferences.major_category:
            professional_group = user.preferences.major_category
        # 其次使用User中的major
        elif hasattr(user, 'major') and user.major:
            professional_group = user.major
        # 最后使用默认值
        
        profile = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "professional_group": professional_group
        }
        
        # 2. 学习风格
        if hasattr(user, 'learning_style'):
            learning_style = user.learning_style
            profile['learning_style'] = {
                'visual_score': learning_style.visual_score,
                'auditory_score': learning_style.auditory_score,
                'reading_score': learning_style.reading_score,
                'kinesthetic_score': learning_style.kinesthetic_score,
                'pace_preference': learning_style.pace_preference,
                'difficulty_preference': getattr(learning_style, 'difficulty_preference', 'medium'),
                'preferred_resource_types': learning_style.preferred_resource_types
            }
        else:
            # 如果没有学习风格，使用默认值
            profile['learning_style'] = {
                'visual_score': 0.5,
                'auditory_score': 0.5,
                'reading_score': 0.5,
                'kinesthetic_score': 0.5,
                'pace_preference': 'balanced',
                'difficulty_preference': 'medium',
                'preferred_resource_types': []
            }
        
        # 3. 知识掌握度
        knowledge_mastery = KnowledgeMastery.objects.filter(user=user)
        if knowledge_mastery.exists():
            # 计算平均掌握度
            avg_mastery = sum(m.mastery_level for m in knowledge_mastery) / len(knowledge_mastery)
            profile['average_mastery'] = avg_mastery
            
            # 获取已掌握的知识点
            mastered_knowledge = [m.knowledge_point for m in knowledge_mastery if m.mastery_level >= 0.7]
            profile['current_knowledge'] = mastered_knowledge
            
            # 获取薄弱知识点
            weak_knowledge = [m.knowledge_point for m in knowledge_mastery if m.mastery_level < 0.4]
            profile['weak_knowledge'] = weak_knowledge
        else:
            profile['average_mastery'] = 0.0
            profile['current_knowledge'] = []
            profile['weak_knowledge'] = []
        
        # 4. 学习偏好
        if hasattr(user, 'learning_preference'):
            learning_preference = user.learning_preference
            profile['interest_areas'] = learning_preference.interest_areas
            profile['learning_goals'] = learning_preference.learning_goals
            profile['daily_available_minutes'] = learning_preference.daily_available_minutes
        else:
            profile['interest_areas'] = []
            profile['learning_goals'] = []
            profile['daily_available_minutes'] = 60
        
        # 5. 知识水平
        if profile['average_mastery'] < 0.3:
            profile['knowledge_level'] = '初级'
        elif profile['average_mastery'] < 0.7:
            profile['knowledge_level'] = '中级'
        else:
            profile['knowledge_level'] = '高级'
        
        return profile
    
    def _optimize_path_with_llm(self, path: List[Dict[str, Any]], 
                               user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用大模型优化学习路径
        
        Args:
            path: 初始学习路径
            user_profile: 用户画像
        
        Returns:
            优化后的学习路径
        """
        # 构建优化请求，更详细地描述用户画像和学习目标
        user_info = f"""
专业组：{user_profile.get('professional_group', '未指定')}
知识水平：{user_profile.get('knowledge_level', '中级')}
学习风格：{user_profile.get('learning_style', {})}
兴趣领域：{user_profile.get('interest_areas', [])}
当前知识：{user_profile.get('current_knowledge', [])}
薄弱知识点：{user_profile.get('weak_knowledge', [])}
学习目标：{user_profile.get('learning_goals', [])}
每天可用学习时间：{user_profile.get('daily_available_minutes', 60)}分钟
学习节奏偏好：{user_profile.get('learning_style', {}).get('pace_preference', 'balanced')}
难度偏好：{user_profile.get('learning_style', {}).get('difficulty_preference', 'medium')}
        """
        
        path_text = "\n".join([f"{i+1}. {node['title']} (难度: {node['difficulty']}, 类型: {node['type']}, 层级: {node['level']})" 
                              for i, node in enumerate(path)])
        
        prompt = f"""作为一名专业的教育顾问，请根据用户的详细信息优化以下学习路径：

{user_info}

初始学习路径：
{path_text}

优化要求：
1. 多目标优化：考虑学习效率、知识完整性、学习体验、专业融合度和能力发展
2. 调整节点顺序，使其更符合用户的学习节奏和认知负荷
3. 为每个节点建议适当的学习资源类型（如视频、文本、实践项目等）
4. 考虑用户的薄弱知识点，添加相关复习内容或前置准备
5. 针对用户的专业组特点，增强专业特色内容
6. 保持路径长度不超过原始长度
7. 确保路径符合先修关系约束
8. 输出优化后的路径，格式为：序号. 节点标题 (难度: 难度值, 类型: 节点类型, 资源: 推荐资源类型)

请只返回优化后的路径，不要添加其他说明。
        """
        
        # 调用大模型
        response = self.llm_service.generate_response(prompt, temperature=0.7, max_tokens=1500)
        
        # 解析优化后的路径
        optimized_path = self._parse_optimized_path(response, path)
        
        return optimized_path if optimized_path else path
    
    def _parse_optimized_path(self, response: str, original_path: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析大模型返回的优化路径
        
        Args:
            response: 大模型响应
            original_path: 原始路径
        
        Returns:
            解析后的优化路径
        """
        # 简单解析，将响应中的节点与原始路径中的节点匹配
        # 实际应用中需要更复杂的解析逻辑
        lines = response.strip().split('\n')
        optimized_path = []
        
        for line in lines:
            # 匹配 "数字. 节点标题" 格式
            if '.' in line:
                parts = line.split('.', 1)
                if len(parts) == 2:
                    node_title = parts[1].strip().split('(')[0].strip()
                    # 在原始路径中查找匹配的节点
                    matched_node = next((node for node in original_path 
                                      if node['title'] == node_title), None)
                    if matched_node:
                        optimized_path.append(matched_node)
        
        # 确保路径不为空，且长度不超过原始路径
        if optimized_path and len(optimized_path) <= len(original_path):
            return optimized_path
        else:
            return original_path
    
    def _generate_personalized_suggestions(self, path: List[Dict[str, Any]], 
                                          user_profile: Dict[str, Any]) -> List[str]:
        """生成个性化学习建议
        
        Args:
            path: 学习路径
            user_profile: 用户画像
        
        Returns:
            个性化学习建议列表
        """
        # 1. 基于学习风格的建议
        style_suggestions = self._generate_style_based_suggestions(user_profile['learning_style'])
        
        # 2. 基于路径的建议
        path_suggestions = self._generate_path_based_suggestions(path, user_profile)
        
        # 3. 基于专业的建议 - 增加建议数量
        professional_suggestions = self._generate_professional_suggestions(user_profile['professional_group'])
        
        # 4. 结合大模型生成的建议 - 增加建议数量
        llm_suggestions = []
        try:
            llm_suggestions = self._generate_llm_based_suggestions(path, user_profile)
        except Exception as e:
            print(f"生成大模型建议失败，使用基于规则的建议补充: {e}")
            # 大模型调用失败，不影响其他建议的生成
        
        # 合并所有建议，去重
        all_suggestions = list(set(style_suggestions + path_suggestions + 
                                 professional_suggestions + llm_suggestions))
        
        # 按建议长度排序，优先返回更长、更详细的建议
        all_suggestions.sort(key=lambda x: len(x), reverse=True)
        
        # 如果没有生成任何建议，返回默认建议
        if not all_suggestions:
            return [
                "建议按照从基础到高级的顺序学习，结合您的学习风格选择合适的学习方法",
                "定期复习已学内容，加深理解，建议每周安排固定的复习时间",
                "多做实践练习，巩固所学知识，将理论应用到实际问题中",
                "遇到问题及时查阅资料或向老师请教，不要积累问题",
                "制定合理的学习计划，保持学习节奏，避免过度疲劳",
                f"根据您的{user_profile.get('professional_group', '科学')}专业特点，优先学习与专业相关度高的内容",
                "关注行业动态和最新研究进展，拓展知识面",
                "利用多种学习资源，如书籍、视频、在线课程等，丰富学习体验",
                "与同学或同行交流学习经验，互相促进，共同进步",
                "保持积极的学习态度，相信自己能够掌握所学知识"
            ]
        
        return all_suggestions[:10]  # 返回前10条详细建议
    
    def _generate_style_based_suggestions(self, learning_style: Dict[str, Any]) -> List[str]:
        """基于学习风格生成建议
        
        Args:
            learning_style: 学习风格
        
        Returns:
            学习风格相关建议
        """
        suggestions = []
        
        # 视觉学习风格
        visual_score = learning_style.get('visual_score', 0.5)
        if visual_score > 0.7:
            suggestions.append(f"建议多使用图表、思维导图、流程图等视觉工具辅助学习，将抽象概念可视化，例如使用MindMaster或Xmind创建知识图谱，帮助您理解知识点之间的关联")
        
        # 听觉学习风格
        auditory_score = learning_style.get('auditory_score', 0.5)
        if auditory_score > 0.7:
            suggestions.append(f"建议朗读学习内容，寻找相关的音频讲解或视频教程，例如在B站或Coursera上搜索相关课程，同时可以尝试使用语音笔记工具记录学习心得")
        
        # 读写学习风格
        reading_score = learning_style.get('reading_score', 0.5)
        if reading_score > 0.7:
            suggestions.append(f"建议多做详细笔记，通过写来加强记忆，尝试使用康奈尔笔记法或思维导图笔记法，同时可以阅读相关的技术书籍和学术论文")
        
        # 动手实践学习风格
        kinesthetic_score = learning_style.get('kinesthetic_score', 0.5)
        if kinesthetic_score > 0.7:
            suggestions.append(f"建议多做练习题和实验，通过动手实践巩固知识，例如使用Python编写代码实现算法，或使用在线实验平台进行模拟实验")
        
        # 学习节奏偏好
        pace_preference = learning_style.get('pace_preference', 'balanced')
        if pace_preference == 'fast':
            suggestions.append(f"建议采用快速浏览+重点突破的学习方式，先快速掌握核心概念，然后针对重点难点进行深入学习，例如使用Pomodoro工作法，25分钟专注学习，5分钟休息")
        elif pace_preference == 'deep':
            suggestions.append(f"建议深入理解每个概念，不要急于求成，尝试使用费曼学习法，将学到的知识讲解给他人，以检验自己的理解程度")
        
        # 难度偏好
        difficulty_preference = learning_style.get('difficulty_preference', 'medium')
        if difficulty_preference == 'easy':
            suggestions.append(f"建议从简单内容开始，逐步提高难度，采用脚手架学习法，先掌握基础概念，再逐步学习复杂内容")
        elif difficulty_preference == 'challenging':
            suggestions.append(f"建议挑战一些有难度的内容，拓展知识面，例如参加在线编程竞赛或开源项目，尝试解决实际问题")
        
        return suggestions
    
    def _generate_path_based_suggestions(self, path: List[Dict[str, Any]], 
                                        user_profile: Dict[str, Any]) -> List[str]:
        """基于路径生成建议
        
        Args:
            path: 学习路径
            user_profile: 用户画像
        
        Returns:
            路径相关建议
        """
        suggestions = []
        professional_group = user_profile.get('professional_group', 'science')
        
        # 检查路径长度
        if len(path) > 7:
            suggestions.append(f"建议将学习路径拆分为多个小目标，每天完成1-2个节点，根据{professional_group}专业的特点，优先完成与专业相关度高的节点")
        
        # 检查难度变化
        difficulties = [node['difficulty'] for node in path]
        if max(difficulties) - min(difficulties) > 2.0:
            suggestions.append(f"学习路径难度波动较大，建议调整学习节奏，遇到困难节点时，结合{professional_group}专业的实际应用场景进行学习，例如对于{professional_group}专业的用户，可以尝试将复杂概念与专业案例结合理解")
        
        # 检查节点类型分布
        concept_nodes = [node for node in path if node['type'] == 'concept']
        skill_nodes = [node for node in path if node['type'] == 'skill']
        resource_nodes = [node for node in path if node['type'] == 'resource']
        
        if len(concept_nodes) > len(skill_nodes) * 2:
            suggestions.append(f"建议增加实践环节，将理论知识应用到{professional_group}专业的实际问题中，例如对于{professional_group}专业的用户，可以尝试使用所学概念解决专业相关的案例或项目")
        elif len(skill_nodes) > len(concept_nodes) * 2:
            suggestions.append(f"建议加强理论学习，深入理解技能背后的原理，特别是与{professional_group}专业相关的核心概念，这将有助于您更好地应用这些技能")
        
        if len(resource_nodes) == 0:
            suggestions.append(f"建议增加资源学习，寻找与{professional_group}专业相关的优质学习资源，例如专业书籍、在线课程、学术论文等，丰富您的学习材料")
        
        # 基于每天可用时间的建议
        daily_minutes = user_profile.get('daily_available_minutes', 60)
        total_difficulty = sum(node['difficulty'] for node in path)
        estimated_time = total_difficulty * 30  # 假设每个难度单位需要30分钟
        
        if estimated_time > daily_minutes * 7:  # 预计超过一周的学习时间
            suggestions.append(f"建议根据您的可用时间({daily_minutes}分钟/天)，合理安排学习计划，优先学习与{professional_group}专业相关度高的内容，确保学习效果")
        
        return suggestions
    
    def _generate_professional_suggestions(self, professional_group: str) -> List[str]:
        """基于专业生成建议
        
        Args:
            professional_group: 专业组
        
        Returns:
            专业相关建议
        """
        suggestions = []
        
        if professional_group == 'business':
            suggestions.append("建议结合真实商业案例（如电商推荐系统、金融风控）理解AI知识点，关注技术在实际业务场景中的ROI")
            suggestions.append("建议多思考如何将AI技术与商业决策流程融合，例如使用机器学习优化供应链管理或客户细分")
            suggestions.append("建议关注AI技术的成本效益分析，学习如何评估AI项目的商业价值")
            suggestions.append("建议结合数据分析工具（如Tableau、Power BI）可视化AI模型输出，提升商业决策效率")
        elif professional_group == 'humanities':
            suggestions.append("建议从历史和文化角度审视AI技术发展，研究技术与社会的互动关系")
            suggestions.append("建议关注AI技术的伦理问题，如算法偏见、隐私保护和数字鸿沟")
            suggestions.append("建议运用文本分析技术（如情感分析、主题建模）研究人文领域的大规模文本数据")
            suggestions.append("建议探索数字人文项目，例如使用AI技术进行历史文献数字化和分析")
        elif professional_group == 'science':
            suggestions.append("建议深入理解算法原理，不仅要会使用API，更要能实现核心算法逻辑")
            suggestions.append("建议多进行代码实现和实验，使用Python和机器学习框架（如TensorFlow、PyTorch）构建模型")
            suggestions.append("建议关注技术细节和最新研究进展，定期阅读顶会论文和技术博客")
            suggestions.append("建议进行模型优化和调参，学习如何提高模型性能和效率")
        elif professional_group == 'arts':
            suggestions.append("建议结合创意设计案例，将AI技术作为创作工具，探索人机协作的创作方式")
            suggestions.append("建议学习使用生成式AI工具（如MidJourney、Stable Diffusion）进行艺术创作")
            suggestions.append("建议关注AI在交互设计中的应用，探索如何使用AI增强用户体验")
            suggestions.append("建议将AI技术与传统艺术形式结合，创造跨媒介的艺术作品")
        
        return suggestions
    
    def _generate_llm_based_suggestions(self, path: List[Dict[str, Any]], 
                                       user_profile: Dict[str, Any]) -> List[str]:
        """基于大模型生成建议
        
        Args:
            path: 学习路径
            user_profile: 用户画像
        
        Returns:
            大模型生成的建议
        """
        try:
            # 构建更详细的路径信息，包含节点的难度、描述等
            detailed_path_text = "\n".join([f"{i+1}. {node['title']} ({node['type']}, 难度: {node['difficulty']}, 层级: {node['level']})\n   描述: {node.get('description', '')}" 
                                  for i, node in enumerate(path)])
            
            # 构建更详细的用户信息，包含学习风格的具体分数
            learning_style = user_profile['learning_style']
            style_details = f"视觉学习倾向: {learning_style.get('visual_score', 0.5)}, 听觉学习倾向: {learning_style.get('auditory_score', 0.5)}, 读写学习倾向: {learning_style.get('reading_score', 0.5)}, 动手学习倾向: {learning_style.get('kinesthetic_score', 0.5)}, 学习节奏偏好: {learning_style.get('pace_preference', 'balanced')}, 难度偏好: {learning_style.get('difficulty_preference', 'medium')}"
            
            prompt = f"""请为以下学习路径生成8条个性化学习建议，结合知识图谱和用户专业背景：

用户学习风格：{style_details}
用户专业：{user_profile['professional_group']}
用户知识水平：{user_profile['knowledge_level']}
用户兴趣领域：{user_profile.get('interest_areas', [])}
用户当前知识：{user_profile.get('current_knowledge', [])}
用户薄弱知识点：{user_profile.get('weak_knowledge', [])}

详细学习路径：
{detailed_path_text}

建议要求：
1. 每条建议至少包含20个汉字，详细具体，可操作性强
2. 个性化，紧密结合用户的专业背景、学习风格和知识水平
3. 针对{user_profile['professional_group']}专业的用户有明确的针对性
4. 覆盖不同方面：学习方法、资源选择、时间管理、实践建议、知识关联等
5. 结合知识图谱的层次结构（概念层、专业融合层、技能层、资源层）
6. 考虑用户的薄弱知识点，提供针对性的改进建议
7. 每条建议以"建议"开头
8. 避免过于笼统的建议，要具体到学习方法、工具、资源或实践方式

请只返回建议列表，不要添加其他说明。
        """
            
            # 调用大模型，增加max_tokens以获取更详细的建议
            response = self.llm_service.generate_response(prompt, temperature=0.7, max_tokens=1500)
            
            # 解析建议
            suggestions = []
            lines = response.strip().split('\n')
            
            for line in lines:
                # 更宽松的匹配条件，确保能捕获更多有效建议
                if '建议' in line and len(line) > 20:  # 只要包含"建议"且长度足够
                    # 提取以"建议"开头的部分
                    if line.startswith('建议'):
                        suggestions.append(line.strip())
                    else:
                        # 处理可能的格式问题，如"1. 建议"或其他前缀
                        suggestion_part = line.split('建议', 1)
                        if len(suggestion_part) > 1:
                            suggestions.append(f"建议{suggestion_part[1].strip()}")
            
            # 如果解析出的建议不足，生成基于规则的补充建议
            if len(suggestions) < 4:
                professional_group = user_profile.get('professional_group', 'science')
                # 补充基于专业的建议
                additional_suggestions = {
                    'business': [
                        "建议关注AI技术在商业决策中的应用，结合实际案例理解算法原理",
                        "建议学习数据分析工具，如Tableau或Power BI，辅助理解AI模型输出",
                        "建议关注AI项目的商业价值评估方法，提高项目决策能力",
                        "建议结合行业报告，了解AI技术在本行业的应用现状和趋势"
                    ],
                    'humanities': [
                        "建议从历史和文化角度审视AI技术发展，研究技术与社会的互动关系",
                        "建议关注AI伦理问题，如算法偏见、隐私保护和数字鸿沟",
                        "建议学习文本分析技术，如情感分析、主题建模，应用于人文研究",
                        "建议探索数字人文项目，使用AI技术进行历史文献数字化和分析"
                    ],
                    'science': [
                        "建议深入理解算法原理，尝试实现核心算法逻辑，增强实践能力",
                        "建议使用Python和机器学习框架构建模型，积累项目经验",
                        "建议关注技术细节和最新研究进展，定期阅读顶会论文和技术博客",
                        "建议进行模型优化和调参，提高模型性能和效率"
                    ],
                    'arts': [
                        "建议结合创意设计案例，将AI技术作为创作工具，探索人机协作方式",
                        "建议学习使用生成式AI工具进行艺术创作，拓展创作可能性",
                        "建议关注AI在交互设计中的应用，探索增强用户体验的新方法",
                        "建议将AI技术与传统艺术形式结合，创造跨媒介艺术作品"
                    ]
                }
                
                # 添加补充建议，确保总建议数足够
                suggestions.extend(additional_suggestions.get(professional_group, additional_suggestions['science']))
            
            return suggestions[:8]  # 返回前8条详细建议
        except Exception:
            # 返回基于规则的备选建议
            professional_group = user_profile.get('professional_group', 'science')
            fallback_suggestions = {
                'business': [
                    "建议关注AI技术在商业决策中的应用，结合实际案例理解算法原理",
                    "建议学习数据分析工具，辅助理解AI模型输出"
                ],
                'humanities': [
                    "建议从历史和文化角度审视AI技术发展，研究技术与社会的互动关系",
                    "建议关注AI伦理问题，如算法偏见、隐私保护"
                ],
                'science': [
                    "建议深入理解算法原理，尝试实现核心算法逻辑",
                    "建议使用Python和机器学习框架构建模型"
                ],
                'arts': [
                    "建议结合创意设计案例，将AI技术作为创作工具",
                    "建议学习使用生成式AI工具进行艺术创作"
                ]
            }
            return fallback_suggestions.get(professional_group, fallback_suggestions['science'])[:8]
    
    def update_learning_path(self, user: User, path: List[Dict[str, Any]], 
                           performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据学习表现更新学习路径
        
        基于文档中的动态路径调整算法，实现以下功能：
        1. 学习进度偏离检测与调整
        2. 学习困难检测与处理
        3. 兴趣变化检测与路径调整
        4. 表现异常检测与优化
        
        Args:
            user: 用户对象
            path: 当前学习路径
            performance: 学习表现
        
        Returns:
            更新后的学习路径
        """
        # 1. 获取用户画像
        user_profile = self._get_user_profile(user)
        
        # 2. 分析学习表现数据
        completed_node_ids = performance.get('completed_nodes', [])
        weak_node_ids = performance.get('weak_nodes', [])
        average_mastery = performance.get('average_mastery', 0.0)
        learning_duration = performance.get('learning_duration', 0)
        progress_rate = performance.get('progress_rate', 1.0)  # 实际进度与计划进度的比率
        
        # 3. 检测调整触发条件
        adjustment_triggers = self._detect_adjustment_triggers(performance, path)
        
        # 4. 根据触发条件选择调整策略
        updated_path = path.copy()
        
        if 'progress_deviation' in adjustment_triggers:
            # 进度偏离调整：调整学习节奏和资源分配
            updated_path = self._adjust_progress_rate(updated_path, progress_rate)
        
        if 'learning_difficulty' in adjustment_triggers:
            # 学习困难调整：添加辅助学习内容
            updated_path = self._handle_learning_difficulties(updated_path, weak_node_ids, user_profile)
        
        if 'interest_change' in adjustment_triggers:
            # 兴趣变化调整：重新规划部分路径
            updated_path = self._adjust_for_interest_change(updated_path, performance, user_profile)
        
        if 'performance_anomaly' in adjustment_triggers:
            # 表现异常调整：重路由策略
            updated_path = self._handle_performance_anomaly(updated_path, performance, user_profile)
        
        # 5. 应用通用调整策略
        updated_path = self._apply_general_adjustments(updated_path, completed_node_ids, weak_node_ids, user_profile)
        
        # 6. 使用大模型优化更新后的路径
        optimized_path = self._optimize_path_with_llm(updated_path, user_profile)
        
        # 7. 限制路径长度并返回
        return optimized_path[:15]  # 限制最大节点数量
    
    def _detect_adjustment_triggers(self, performance: Dict[str, Any], path: List[Dict[str, Any]]) -> List[str]:
        """检测路径调整触发条件
        
        根据文档中的触发条件：
        1. 学习进度偏离：实际进度与计划偏差过大
        2. 学习困难：在某个知识点遇到持续困难
        3. 兴趣变化：学习兴趣或目标发生变化
        4. 表现异常：学习表现显著低于预期
        
        Args:
            performance: 学习表现
            path: 当前学习路径
        
        Returns:
            调整触发条件列表
        """
        triggers = []
        
        # 1. 检测学习进度偏离
        progress_rate = performance.get('progress_rate', 1.0)
        if progress_rate < 0.5 or progress_rate > 2.0:
            triggers.append('progress_deviation')
        
        # 2. 检测学习困难
        weak_nodes = performance.get('weak_nodes', [])
        if len(weak_nodes) > len(path) * 0.3:  # 超过30%的节点是薄弱节点
            triggers.append('learning_difficulty')
        
        # 3. 检测兴趣变化
        interest_change = performance.get('interest_change', 0.0)
        if interest_change > 0.5:  # 兴趣变化超过50%
            triggers.append('interest_change')
        
        # 4. 检测表现异常
        average_mastery = performance.get('average_mastery', 0.0)
        if average_mastery < 0.4:  # 平均掌握度低于40%
            triggers.append('performance_anomaly')
        
        return triggers
    
    def _adjust_progress_rate(self, path: List[Dict[str, Any]], progress_rate: float) -> List[Dict[str, Any]]:
        """调整学习进度
        
        根据实际进度与计划进度的比率调整学习路径
        
        Args:
            path: 当前学习路径
            progress_rate: 实际进度与计划进度的比率
        
        Returns:
            调整后的学习路径
        """
        updated_path = path.copy()
        
        if progress_rate < 0.7:  # 进度过慢，减少难度或增加辅助内容
            for i, node in enumerate(updated_path):
                # 降低后续节点的难度
                if i > len(path) * 0.5:  # 只调整后半部分
                    updated_path[i]['difficulty'] = max(1.0, node['difficulty'] - 0.5)
        elif progress_rate > 1.5:  # 进度过快，增加难度或扩展内容
            for i, node in enumerate(updated_path):
                # 增加后续节点的难度
                if i > len(path) * 0.5:  # 只调整后半部分
                    updated_path[i]['difficulty'] = min(5.0, node['difficulty'] + 0.5)
        
        return updated_path
    
    def _handle_learning_difficulties(self, path: List[Dict[str, Any]], weak_node_ids: List[int], 
                                     user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理学习困难
        
        对于薄弱节点，添加相关复习内容和辅助资源
        
        Args:
            path: 当前学习路径
            weak_node_ids: 薄弱节点ID列表
            user_profile: 用户画像
        
        Returns:
            调整后的学习路径
        """
        updated_path = []
        
        for node in path:
            if node['id'] in weak_node_ids:
                # 1. 添加当前节点（重复学习）
                updated_path.append(node)
                
                # 2. 添加相关的前置节点或辅助节点
                related_nodes = self.kg_engine.get_related_nodes(node['id'], 
                                                              relation_type='prerequisite', 
                                                              limit=2)
                for related_node_id in related_nodes:
                    related_node = KnowledgeNode.objects.get(id=related_node_id)
                    updated_path.append({
                        "id": related_node.id,
                        "title": related_node.title,
                        "type": related_node.type,
                        "level": related_node.level,
                        "difficulty": related_node.difficulty,
                        "importance": related_node.importance,
                        "description": related_node.description,
                        "professional_group": related_node.professional_group,
                        "tags": related_node.tags
                    })
            else:
                updated_path.append(node)
        
        return updated_path
    
    def _adjust_for_interest_change(self, path: List[Dict[str, Any]], performance: Dict[str, Any], 
                                  user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据兴趣变化调整路径
        
        Args:
            path: 当前学习路径
            performance: 学习表现
            user_profile: 用户画像
        
        Returns:
            调整后的学习路径
        """
        # 简化实现：根据新兴趣重新排序后续节点
        new_interests = performance.get('new_interests', [])
        if not new_interests:
            return path
        
        updated_path = path.copy()
        
        # 对后续节点按兴趣匹配度重新排序
        if len(updated_path) > 3:  # 只调整后半部分
            # 计算每个节点与新兴趣的匹配度
            node_scores = []
            for node in updated_path[3:]:
                score = self._calculate_interest_match(node, new_interests)
                node_scores.append((node, score))
            
            # 按匹配度排序
            node_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 更新路径
            updated_path[3:] = [node for node, score in node_scores]
        
        return updated_path
    
    def _handle_performance_anomaly(self, path: List[Dict[str, Any]], performance: Dict[str, Any], 
                                  user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理表现异常
        
        当学习表现显著低于预期时，重路由学习路径
        
        Args:
            path: 当前学习路径
            performance: 学习表现
            user_profile: 用户画像
        
        Returns:
            调整后的学习路径
        """
        # 简化实现：替换表现不佳的节点序列
        weak_node_ids = performance.get('weak_nodes', [])
        if not weak_node_ids:
            return path
        
        updated_path = []
        skip_next = False
        
        for i, node in enumerate(path):
            if skip_next:
                skip_next = False
                continue
                
            if node['id'] in weak_node_ids and i < len(path) - 1:
                # 替换当前节点和下一个节点为更基础的路径
                base_path = self.kg_engine.get_shortest_path(
                    path[max(0, i-2)]['id'] if i >= 2 else path[0]['id'],
                    path[i+1]['id'],
                    weight='difficulty'  # 选择难度更低的路径
                )
                
                if base_path and len(base_path) > 1:
                    # 添加替换路径
                    for node_id in base_path[1:]:  # 跳过已经存在的起始节点
                        try:
                            replacement_node = KnowledgeNode.objects.get(id=node_id)
                            updated_path.append({
                                "id": replacement_node.id,
                                "title": replacement_node.title,
                                "type": replacement_node.type,
                                "level": replacement_node.level,
                                "difficulty": replacement_node.difficulty,
                                "importance": replacement_node.importance,
                                "description": replacement_node.description,
                                "professional_group": replacement_node.professional_group,
                                "tags": replacement_node.tags
                            })
                        except KnowledgeNode.DoesNotExist:
                            pass
                    skip_next = True
                else:
                    updated_path.append(node)
            else:
                updated_path.append(node)
        
        return updated_path
    
    def _apply_general_adjustments(self, path: List[Dict[str, Any]], completed_node_ids: List[int], 
                                  weak_node_ids: List[int], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用通用调整策略
        
        Args:
            path: 当前学习路径
            completed_node_ids: 已完成节点ID列表
            weak_node_ids: 薄弱节点ID列表
            user_profile: 用户画像
        
        Returns:
            调整后的学习路径
        """
        updated_path = []
        
        for node in path:
            if node['id'] in completed_node_ids:
                # 已完成节点：添加后续推荐节点
                next_nodes = self.kg_engine.recommend_next_nodes(node['id'], user_profile, limit=1)
                for next_node_id in next_nodes:
                    try:
                        next_node = KnowledgeNode.objects.get(id=next_node_id)
                        # 检查节点是否已经在路径中
                        if not any(n['id'] == next_node.id for n in updated_path):
                            updated_path.append({
                                "id": next_node.id,
                                "title": next_node.title,
                                "type": next_node.type,
                                "level": next_node.level,
                                "difficulty": next_node.difficulty,
                                "importance": next_node.importance,
                                "description": next_node.description,
                                "professional_group": next_node.professional_group,
                                "tags": next_node.tags
                            })
                    except KnowledgeNode.DoesNotExist:
                        pass
            else:
                updated_path.append(node)
        
        return updated_path
    
    def _calculate_interest_match(self, node: Dict[str, Any], interests: List[str]) -> float:
        """计算节点与兴趣的匹配度
        
        Args:
            node: 知识节点
            interests: 兴趣列表
        
        Returns:
            匹配度分数（0-1）
        """
        match_score = 0.0
        node_text = f"{node['title']} {node['description']} {' '.join(node['tags'])}".lower()
        
        for interest in interests:
            if interest.lower() in node_text:
                match_score += 1.0
        
        return match_score / (len(interests) + 1)  # 归一化到0-1之间
    
    def generate_learning_feedback(self, user: User, performance: Dict[str, Any]) -> Dict[str, Any]:
        """生成学习反馈
        
        Args:
            user: 用户对象
            performance: 学习表现
        
        Returns:
            学习反馈，包含评估和建议
        """
        # 1. 获取用户画像
        user_profile = self._get_user_profile(user)
        
        # 2. 使用大模型生成反馈
        feedback = self.llm_service.generate_personalized_feedback(user_profile, performance)
        
        # 3. 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(performance, user_profile)
        
        return {
            "feedback": feedback,
            "improvement_suggestions": improvement_suggestions
        }
    
    def _generate_improvement_suggestions(self, performance: Dict[str, Any], 
                                         user_profile: Dict[str, Any]) -> List[str]:
        """生成改进建议
        
        Args:
            performance: 学习表现
            user_profile: 用户画像
        
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 基于平均掌握度的建议
        average_mastery = performance.get('average_mastery', 0.0)
        if average_mastery < 0.5:
            suggestions.append("建议加强基础知识学习，多做练习题巩固")
        elif average_mastery < 0.8:
            suggestions.append("学习效果良好，建议重点关注薄弱环节，进一步提高")
        else:
            suggestions.append("学习效果优秀，建议挑战更高难度的内容，拓展知识面")
        
        # 基于学习时长的建议
        learning_duration = performance.get('learning_duration', 0)
        if learning_duration < 300:  # 少于5小时
            suggestions.append("建议增加学习时长，保持持续的学习状态")
        elif learning_duration > 1000:  # 超过16小时
            suggestions.append("学习时长充足，建议优化学习方法，提高学习效率")
        
        # 基于薄弱节点的建议
        weak_nodes = performance.get('weak_nodes', [])
        if len(weak_nodes) > 3:
            suggestions.append("建议重点复习薄弱知识点，多做相关练习")
        
        # 基于完成率的建议
        completion_rate = performance.get('completion_rate', 0.0)
        if completion_rate < 0.5:
            suggestions.append("建议制定明确的学习计划，提高学习完成率")
        
        return suggestions
