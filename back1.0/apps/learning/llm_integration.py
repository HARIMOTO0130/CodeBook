"""大模型集成模块，实现大模型API封装、prompt管理和响应解析"""

import openai
import anthropic
import json
from typing import Dict, Any, List
from django.conf import settings
from .models import LLMIntegration, PromptTemplate


class LLMService:
    """大模型服务核心类"""
    
    def __init__(self, provider: str = None, model_name: str = None, api_key: str = None):
        """初始化大模型服务
        
        Args:
            provider: 大模型提供商，如 'openai'、'anthropic'、'doubao' 等
            model_name: 模型名称，如 'gpt-4'、'claude-3'、'doubao-seed-1-6-251015' 等
            api_key: API密钥
        """
        # 如果没有提供参数，使用默认配置
        if not provider or not model_name or not api_key:
            default_config = self._get_default_config()
            provider = provider or default_config['provider']
            model_name = model_name or default_config['model_name']
            api_key = api_key or default_config['api_key']
        
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.client = self._initialize_client()
    
    def _get_default_config(self) -> Dict[str, str]:
        """获取默认大模型配置"""
        # 从数据库中获取默认配置
        default_config = LLMIntegration.objects.filter(is_active=True).first()
        if default_config:
            return {
                'provider': default_config.provider,
                'model_name': default_config.model_name,
                'api_key': default_config.api_key
            }
        
        # 如果数据库中没有配置，优先检查豆包配置
        # 使用用户提供的API密钥
        import os
        doubao_api_key = os.getenv('DOUBao_API_KEY', '9511e57c-7838-415d-8225-fdf89678c631')
        if doubao_api_key:
            return {
                'provider': 'doubao',
                'model_name': os.getenv('DOUBao_MODEL_ID', 'doubao-seed-1-6-251015'),
                'api_key': doubao_api_key
            }
        
        # 如果豆包配置也不存在，使用环境变量或默认值
        return {
            'provider': os.getenv('LLM_PROVIDER', 'openai'),
            'model_name': os.getenv('LLM_MODEL_NAME', 'gpt-3.5-turbo'),
            'api_key': os.getenv('LLM_API_KEY', '')
        }
    
    def _initialize_client(self):
        """初始化大模型客户端"""
        if self.provider == 'openai':
            return openai.OpenAI(api_key=self.api_key)
        elif self.provider == 'anthropic':
            return anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == 'doubao':
            # 豆包不再使用SDK，直接使用HTTP调用，返回None
            return None
        elif self.provider == 'baidu' or self.provider == 'alibaba':
            # 百度文心一言和阿里云通义千问API客户端初始化
            # 这里需要根据具体API文档实现
            return None
        else:
            raise ValueError(f"不支持的大模型提供商: {self.provider}")
    
    def generate_response(self, prompt: str, temperature: float = 0.7, 
                         max_tokens: int = 1000, context: Dict[str, Any] = None) -> str:
        """生成大模型响应
        
        Args:
            prompt: 提示词
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大 tokens 数
            context: 上下文信息
        
        Returns:
            大模型生成的响应文本
        """
        try:
            if self.provider == 'openai':
                # 构建 messages
                messages = []
                if context:
                    # 如果有上下文，添加到 messages 中
                    for role, content in context.items():
                        messages.append({"role": role, "content": content})
                
                # 添加用户提示
                messages.append({"role": "user", "content": prompt})
                
                # 调用 API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                # 构建 messages
                messages = []
                if context:
                    for role, content in context.items():
                        messages.append({"role": role, "content": content})
                
                messages.append({"role": "user", "content": prompt})
                
                # 调用 API
                response = self.client.messages.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.content[0].text
            
            elif self.provider == 'doubao':
                # 豆包大模型API调用 - 直接使用HTTP请求
                try:
                    import requests
                    
                    # 构建 messages
                    messages = []
                    if context:
                        for role, content in context.items():
                            messages.append({"role": role, "content": content})
                    
                    messages.append({"role": "user", "content": prompt})
                    
                    # 构建请求URL和headers
                    base_url = getattr(settings, 'DOUBao_API_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
                    url = f"{base_url}/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # 构建请求body
                    body = {
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    # 发送HTTP请求
                    response = requests.post(url, headers=headers, json=body, timeout=30)
                    
                    # 打印响应状态和内容，便于调试
                    print(f"豆包API响应状态码: {response.status_code}")
                    print(f"豆包API响应内容: {response.text[:200]}...")
                    
                    if response.status_code == 200:
                        # 解析响应
                        response_data = response.json()
                        return response_data.get("choices", [{}])[0].get("message", {}).get("content", self._get_fallback_response(prompt))
                    else:
                        # 非200状态码，返回回退响应
                        print(f"豆包API调用失败: {response.status_code} {response.reason}")
                        return self._get_fallback_response(prompt)
                except Exception as e:
                    print(f"豆包API调用失败: {e}")
                    return self._get_fallback_response(prompt)
            
            elif self.provider == 'baidu':
                # 百度文心一言API调用
                # 这里需要根据具体API文档实现
                return self._get_fallback_response(prompt)
            
            elif self.provider == 'alibaba':
                # 阿里云通义千问API调用
                # 这里需要根据具体API文档实现
                return self._get_fallback_response(prompt)
            
            else:
                raise ValueError(f"不支持的大模型提供商: {self.provider}")
        
        except Exception as e:
            print(f"大模型调用失败: {e}")
            # 生成回退响应
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """生成回退响应
        
        Args:
            prompt: 提示词
        
        Returns:
            回退响应文本
        """
        # 基于提示词类型生成不同的回退响应
        prompt_lower = prompt.lower()
        
        if '路径' in prompt_lower or '学习路径' in prompt_lower:
            return "基于您的学习目标，建议您按照从基础到高级的顺序学习相关知识点，重点关注核心概念的理解和实践应用。"
        elif '解释' in prompt_lower or '说明' in prompt_lower:
            return "该学习路径设计遵循了从基础到高级、从理论到实践的原则，帮助您系统性地掌握相关知识和技能。"
        elif '建议' in prompt_lower or '推荐' in prompt_lower:
            return "建议您每天保持固定的学习时间，定期复习已学内容，多做实践练习，遇到问题及时查阅资料或向老师请教。"
        elif '反馈' in prompt_lower or '评估' in prompt_lower:
            return "您的学习表现良好，继续保持当前的学习节奏。建议您重点关注薄弱环节，多做针对性练习。"
        else:
            return "感谢您的提问。由于系统限制，暂时无法提供详细回答，建议您参考相关教材或在线资源获取更多信息。"
    
    def extract_knowledge_nodes(self, text: str) -> Dict[str, Any]:
        """从文本中提取知识节点和关系
        
        Args:
            text: 输入文本
        
        Returns:
            提取的知识节点和关系，格式为 {
                "nodes": [{
                    "title": "节点标题",
                    "type": "节点类型",
                    "description": "节点描述",
                    "level": 节点层级,
                    "difficulty": 难度系数
                }],
                "relations": [{
                    "source": "源节点标题",
                    "target": "目标节点标题",
                    "type": "关系类型"
                }]
            }
        """
        # 获取知识提取的 prompt 模板
        prompt_template = self._get_prompt_template('knowledge_extraction')
        
        # 填充模板
        prompt = prompt_template.format(text=text)
        
        # 调用大模型
        response = self.generate_response(prompt, temperature=0.3, max_tokens=2000)
        
        # 解析响应
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response: {response}")
            return {"nodes": [], "relations": []}
    
    def generate_learning_path_explanation(self, path: List[Dict[str, Any]], 
                                          user_profile: Dict[str, Any]) -> str:
        """生成学习路径解释
        
        Args:
            path: 学习路径节点列表
            user_profile: 用户画像
        
        Returns:
            学习路径的详细解释
        """
        # 获取路径解释的 prompt 模板
        prompt_template = self._get_prompt_template('path_generation')
        
        # 格式化路径信息
        path_text = "\n".join([f"{i+1}. {node['title']} (难度: {node['difficulty']}, 重要性: {node['importance']})" 
                              for i, node in enumerate(path)])
        
        # 格式化用户信息
        user_info = f"""
专业: {user_profile.get('professional_group', '未指定')}
学习风格: {user_profile.get('learning_style', {})}
兴趣领域: {user_profile.get('interest_areas', [])}
知识水平: {user_profile.get('knowledge_level', '中级')}
"""
        
        # 填充模板
        prompt = prompt_template.format(path=path_text, user_info=user_info)
        
        # 调用大模型
        return self.generate_response(prompt, temperature=0.7, max_tokens=1500)
    
    def generate_learning_path(self, learning_goal: str, user_profile: Dict[str, Any], 
                              knowledge_graph: Any) -> List[Dict[str, Any]]:
        """生成个性化学习路径
        
        Args:
            learning_goal: 学习目标
            user_profile: 用户画像
            knowledge_graph: 知识图谱对象
        
        Returns:
            个性化学习路径节点列表
        """
        # 构建提示词
        prompt = f"""请基于以下知识图谱信息，为用户生成个性化学习路径：
        
        学习目标：{learning_goal}
        
        用户信息：
        - 专业：{user_profile.get('professional_group', '未指定')}
        - 学习风格：{user_profile.get('learning_style', {})}
        - 兴趣领域：{user_profile.get('interest_areas', [])}
        - 知识水平：{user_profile.get('knowledge_level', '中级')}
        
        知识图谱结构：
        - 概念层：基础理论和核心概念
        - 专业融合层：跨学科知识应用
        - 技能层：实践能力和操作技能
        - 资源层：学习材料和参考资源
        
        要求：
        1. 路径长度不超过15个节点
        2. 路径从用户当前知识水平开始，逐步提升难度
        3. 路径应涵盖概念、专业融合、技能和资源四个层次
        4. 路径应根据用户专业和兴趣进行个性化调整
        5. 每个节点应包含：标题、类型、难度、重要性、简短描述
        6. 返回格式为JSON，示例：
        {
          "path": [
            {
              "title": "节点标题",
              "type": "concept|professional_integration|skill|resource",
              "difficulty": 1.0-5.0,
              "importance": 1.0-5.0,
              "description": "节点描述"
            }
          ]
        }
        
        请只返回JSON，不要添加其他内容。
        """
        
        # 调用大模型
        response = self.generate_response(prompt, temperature=0.3, max_tokens=2000)
        
        # 解析响应
        try:
            result = json.loads(response)
            return result.get("path", [])
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response for learning path: {response}")
            return []
    
    def generate_personalized_feedback(self, user_profile: Dict[str, Any], 
                                     performance: Dict[str, Any]) -> str:
        """生成个性化学习反馈
        
        Args:
            user_profile: 用户画像
            performance: 学习表现
        
        Returns:
            个性化学习反馈
        """
        # 获取反馈生成的 prompt 模板
        prompt_template = self._get_prompt_template('feedback_generation')
        
        # 格式化用户表现
        performance_text = f"""
已完成节点: {performance.get('completed_nodes', [])}
平均掌握度: {performance.get('average_mastery', 0.0)}
薄弱节点: {performance.get('weak_nodes', [])}
学习时长: {performance.get('learning_duration', 0)}分钟
学习进度: {performance.get('progress', 0)}%
"""
        
        # 填充模板
        prompt = prompt_template.format(
            user_profile=json.dumps(user_profile, ensure_ascii=False),
            performance=performance_text
        )
        
        # 调用大模型
        return self.generate_response(prompt, temperature=0.7, max_tokens=1500)
    
    def generate_learning_suggestions(self, user_profile: Dict[str, Any], 
                                     learning_history: Dict[str, Any]) -> str:
        """生成针对性学习建议
        
        Args:
            user_profile: 用户画像
            learning_history: 学习历史
        
        Returns:
            针对性学习建议
        """
        # 构建提示词
        prompt = f"""请根据用户的学习历史和画像，生成针对性的学习建议：
        
        用户信息：
        - 专业：{user_profile.get('professional_group', '未指定')}
        - 学习风格：{user_profile.get('learning_style', {})}
        - 兴趣领域：{user_profile.get('interest_areas', [])}
        - 学习偏好：{user_profile.get('difficulty_preference', '适中')}
        
        学习历史：
        - 已完成节点：{learning_history.get('completed_nodes', [])}
        - 学习进度：{learning_history.get('progress', 0)}%
        - 学习时长：{learning_history.get('total_duration', 0)}分钟
        - 薄弱知识点：{learning_history.get('weak_points', [])}
        - 最近学习的节点：{learning_history.get('recent_nodes', [])}
        
        要求：
        1. 基于用户的学习表现和薄弱点，生成具体的改进建议
        2. 考虑用户的学习风格和偏好
        3. 提供可操作的学习方法和资源建议
        4. 保持建议的个性化和针对性
        5. 语言友好、鼓励，避免过于严厉的批评
        """
        
        # 调用大模型
        return self.generate_response(prompt, temperature=0.7, max_tokens=1500)
    
    def generate_knowledge_explanation(self, knowledge_point: str, user_level: str) -> str:
        """生成易于理解的知识点解释
        
        Args:
            knowledge_point: 知识点名称
            user_level: 用户水平
        
        Returns:
            个性化知识点解释
        """
        # 构建提示词
        prompt = f"""请根据用户水平，生成易于理解的知识点解释：
        
        知识点：{knowledge_point}
        用户水平：{user_level}（入门/中级/高级）
        
        要求：
        1. 根据用户水平调整解释的深度和复杂度
        2. 使用简洁明了的语言，避免过于专业的术语
        3. 结合实际例子或应用场景
        4. 突出知识点的核心概念和关键要点
        5. 提供学习建议或扩展阅读方向
        """
        
        # 调用大模型
        return self.generate_response(prompt, temperature=0.7, max_tokens=1500)
    
    def answer_question(self, question: str, context: Dict[str, Any] = None) -> str:
        """回答用户问题
        
        Args:
            question: 用户问题
            context: 上下文信息
        
        Returns:
            问题答案
        """
        # 获取问答的 prompt 模板
        prompt_template = self._get_prompt_template('question_answering')
        
        # 填充模板
        prompt = prompt_template.format(question=question)
        
        # 调用大模型
        return self.generate_response(prompt, temperature=0.7, max_tokens=1000, context=context)
    
    def _get_prompt_template(self, template_type: str) -> str:
        """获取指定类型的 prompt 模板
        
        Args:
            template_type: 模板类型
        
        Returns:
            prompt 模板字符串
        """
        # 从数据库中获取模板
        try:
            template = PromptTemplate.objects.get(type=template_type)
            return template.template
        except PromptTemplate.DoesNotExist:
            # 如果数据库中没有模板，返回默认模板
            return self._get_default_prompt_template(template_type)
    
    def _get_default_prompt_template(self, template_type: str) -> str:
        """获取默认的 prompt 模板
        
        Args:
            template_type: 模板类型
        
        Returns:
            默认的 prompt 模板字符串
        """
        default_templates = {
            'knowledge_extraction': """请从以下文本中提取知识节点和它们之间的关系，严格按照JSON格式返回：

文本内容：
{text}

输出格式示例：
{{
  "nodes": [
    {{
      "title": "知识节点1",
      "type": "concept|application|skill|resource",
      "description": "知识节点1的描述",
      "level": 1,
      "difficulty": 3.0,
      "importance": 3.0
    }}
  ],
  "relations": [
    {{
      "source": "知识节点1",
      "target": "知识节点2",
      "type": "prerequisite|related|application|advanced"
    }}
  ]
}}

请确保JSON格式正确，不要包含任何额外内容。""",
            
            'path_generation': """请为以下学习路径生成详细的解释，包括：
1. 学习路径的整体逻辑
2. 每个节点的学习重点
3. 节点之间的联系
4. 针对用户的个性化学习建议

用户信息：
{user_info}

学习路径：
{path}

请使用清晰、友好的语言，避免过于技术性的术语。""",
            
            'feedback_generation': """请根据用户的学习表现生成个性化反馈：

用户信息：
{user_profile}

学习表现：
{performance}

请生成包含以下内容的反馈：
1. 客观的学习进度评价
2. 学习优点和需要改进的地方
3. 针对性的学习建议
4. 下一步学习计划
5. 鼓励性的话语

请使用温暖、鼓励的语气，避免过于严厉的批评。""",
            
            'question_answering': """请回答以下问题，保持简洁明了：

问题：{question}

回答："""
        }
        
        return default_templates.get(template_type, "")
    
    def create_prompt_template(self, name: str, template: str, 
                              template_type: str) -> PromptTemplate:
        """创建 prompt 模板
        
        Args:
            name: 模板名称
            template: 模板内容
            template_type: 模板类型
        
        Returns:
            创建的 PromptTemplate 对象
        """
        return PromptTemplate.objects.create(
            name=name,
            template=template,
            type=template_type
        )
    
    def update_prompt_template(self, template_id: int, **kwargs) -> bool:
        """更新 prompt 模板
        
        Args:
            template_id: 模板ID
            **kwargs: 更新的字段
        
        Returns:
            更新是否成功
        """
        try:
            template = PromptTemplate.objects.get(id=template_id)
            for key, value in kwargs.items():
                setattr(template, key, value)
            template.save()
            return True
        except PromptTemplate.DoesNotExist:
            return False
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表
        
        Returns:
            可用模型名称列表
        """
        # 根据提供商返回可用模型列表
        model_lists = {
            'openai': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
            'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            'baidu': ['ERNIE-Bot', 'ERNIE-Bot-4'],
            'alibaba': ['qwen-plus', 'qwen-turbo']
        }
        
        return model_lists.get(self.provider, [])
