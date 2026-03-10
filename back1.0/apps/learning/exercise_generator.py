"""自动习题生成引擎，基于知识点生成题目"""

import json
import random
import re
from typing import Dict, List, Any
from django.conf import settings
from .llm_integration import LLMService
from .models import KnowledgeNode


class ExerciseGenerator:
    """自动习题生成引擎核心类"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.exercise_types = self._init_exercise_types()
    
    def _init_exercise_types(self) -> Dict[str, Any]:
        """初始化习题类型配置"""
        return {
            'multiple_choice': {
                'name': '选择题',
                'difficulty_levels': {
                    'easy': 2,  # 选项数量
                    'medium': 4,  # 选项数量
                    'hard': 5  # 选项数量
                },
                'time_limit': 60  # 秒
            },
            'true_false': {
                'name': '判断题',
                'difficulty_levels': {
                    'easy': 1,  # 简单判断
                    'medium': 1,  # 中等判断
                    'hard': 1  # 复杂判断
                },
                'time_limit': 30  # 秒
            },
            'fill_blank': {
                'name': '填空题',
                'difficulty_levels': {
                    'easy': 1,  # 1个空
                    'medium': 2,  # 2个空
                    'hard': 3  # 3个空
                },
                'time_limit': 90  # 秒
            },
            'coding': {
                'name': '编程题',
                'difficulty_levels': {
                    'easy': 1,  # 简单函数
                    'medium': 2,  # 中等算法
                    'hard': 3  # 复杂算法
                },
                'time_limit': 300  # 秒
            },
            'short_answer': {
                'name': '简答题',
                'difficulty_levels': {
                    'easy': 1,  # 简单概念
                    'medium': 1,  # 中等理解
                    'hard': 2  # 复杂分析
                },
                'time_limit': 120  # 秒
            }
        }
    
    def generate_exercises(self, knowledge_points: List[str], 
                         exercise_type: str = 'multiple_choice',
                         difficulty: str = 'medium',
                         count: int = 5,
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成习题
        
        Args:
            knowledge_points: 知识点列表
            exercise_type: 习题类型
            difficulty: 难度等级
            count: 生成数量
            context: 上下文信息
        
        Returns:
            生成的习题列表
        """
        try:
            # 验证参数
            if not knowledge_points:
                return {
                    'error': '知识点不能为空',
                    'exercises': []
                }
            
            if exercise_type not in self.exercise_types:
                return {
                    'error': f'不支持的习题类型: {exercise_type}',
                    'exercises': []
                }
            
            if difficulty not in ['easy', 'medium', 'hard']:
                return {
                    'error': f'不支持的难度等级: {difficulty}',
                    'exercises': []
                }
            
            # 生成习题
            exercises = []
            for i in range(count):
                exercise = self._generate_single_exercise(
                    knowledge_points, 
                    exercise_type, 
                    difficulty,
                    context
                )
                if exercise:
                    exercises.append(exercise)
            
            return {
                'exercises': exercises,
                'exercise_type': exercise_type,
                'difficulty': difficulty,
                'count': len(exercises),
                'knowledge_points': knowledge_points
            }
            
        except Exception as e:
            return {
                'error': f'习题生成失败: {str(e)}',
                'exercises': []
            }
    
    def _generate_single_exercise(self, knowledge_points: List[str], 
                                exercise_type: str, 
                                difficulty: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成单个习题"""
        try:
            # 构建提示词
            prompt = self._build_prompt(knowledge_points, exercise_type, difficulty, context)
            
            # 使用LLM生成习题
            response = self.llm_service.generate_response(prompt, temperature=0.7)
            
            # 解析习题
            exercise = self._parse_exercise(response, exercise_type, difficulty)
            
            if exercise:
                # 添加元数据
                exercise.update({
                    'id': f'ex_{random.randint(100000, 999999)}',
                    'created_at': self._get_current_time(),
                    'difficulty': difficulty,
                    'exercise_type': exercise_type,
                    'time_limit': self.exercise_types[exercise_type]['time_limit']
                })
                
                return exercise
            
            return None
            
        except Exception as e:
            print(f"生成单个习题失败: {e}")
            return None
    
    def _build_prompt(self, knowledge_points: List[str], 
                     exercise_type: str, 
                     difficulty: str,
                     context: Dict[str, Any] = None) -> str:
        """构建生成习题的提示词"""
        
        type_name = self.exercise_types[exercise_type]['name']
        difficulty_map = {
            'easy': '简单',
            'medium': '中等',
            'hard': '困难'
        }
        
        prompt = f"""请基于以下知识点生成1道{difficulty_map[difficulty]}难度的{type_name}：

知识点：
{', '.join(knowledge_points)}

要求：
1. 题目必须与给定知识点紧密相关
2. 难度要符合{difficulty_map[difficulty]}级别
3. 题目表述清晰，逻辑严密
4. 答案正确，解析详细
5. 请以JSON格式返回，包含以下字段：
"""
        
        # 根据习题类型添加特定要求
        if exercise_type == 'multiple_choice':
            options_count = self.exercise_types[exercise_type]['difficulty_levels'][difficulty]
            prompt += f"""
{{
  "question": "题目内容",
  "options": ["选项A", "选项B", ...],  # {options_count}个选项
  "correct_answer": "正确选项",
  "explanation": "答案解析"
}}
"""
        
        elif exercise_type == 'true_false':
            prompt += f"""
{{
  "question": "题目内容",
  "correct_answer": true,  # true或false
  "explanation": "答案解析"
}}
"""
        
        elif exercise_type == 'fill_blank':
            blanks_count = self.exercise_types[exercise_type]['difficulty_levels'][difficulty]
            prompt += f"""
{{
  "question": "题目内容（使用[ ]表示空）",
  "correct_answers": ["答案1", "答案2", ...],  # {blanks_count}个答案
  "explanation": "答案解析"
}}
"""
        
        elif exercise_type == 'coding':
            prompt += f"""
{{
  "question": "编程题描述",
  "requirements": "具体要求",
  "input_format": "输入格式",
  "output_format": "输出格式",
  "examples": [
    {{"input": "输入示例", "output": "输出示例"}}
  ],
  "correct_answer": "参考代码",
  "explanation": "代码解析"
}}
"""
        
        elif exercise_type == 'short_answer':
            prompt += f"""
{{
  "question": "简答题题目",
  "correct_answer": "正确答案",
  "explanation": "答案解析"
}}
"""
        
        return prompt
    
    def _parse_exercise(self, response: str, exercise_type: str, difficulty: str) -> Dict[str, Any]:
        """解析生成的习题"""
        try:
            # 提取JSON部分（支持多行JSON）
            # 寻找第一个{和最后一个}之间的内容
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx+1]
                try:
                    exercise = json.loads(json_str)
                    
                    # 验证必要字段
                    if self._validate_exercise(exercise, exercise_type):
                        return exercise
                except json.JSONDecodeError:
                    pass
            
            # 如果不是JSON格式，尝试解析为文本格式
            return self._parse_text_exercise(response, exercise_type)
            
        except Exception as e:
            print(f"解析习题失败: {e}")
            return None
    
    def _parse_text_exercise(self, text: str, exercise_type: str) -> Dict[str, Any]:
        """解析文本格式的习题"""
        lines = text.split('\n')
        exercise = {}
        
        # 提取题目内容
        question_lines = []
        options = []
        correct_answer = ''
        explanation = ''
        
        # 状态标记
        in_question = True
        in_options = False
        in_answer = False
        in_explanation = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查行的类型
            if '题目' in line or 'Question' in line or line.startswith('Q:') or line.startswith('问题:'):
                question_lines.append(line.replace('题目:', '').replace('Question:', '').replace('Q:', '').replace('问题:', '').strip())
                in_question = True
                in_options = False
                in_answer = False
                in_explanation = False
            elif re.match(r'^[A-D]\.', line) or re.match(r'^[A-D]:', line):
                options.append(line)
                in_question = False
                in_options = True
                in_answer = False
                in_explanation = False
            elif '答案' in line or 'Answer' in line or line.startswith('A:'):
                correct_answer = line.replace('答案:', '').replace('Answer:', '').replace('A:', '').strip()
                in_question = False
                in_options = False
                in_answer = True
                in_explanation = False
            elif '解析' in line or 'Explanation' in line or '解释' in line:
                explanation = line.replace('解析:', '').replace('Explanation:', '').replace('解释:', '').strip()
                in_question = False
                in_options = False
                in_answer = False
                in_explanation = True
            elif in_question:
                question_lines.append(line)
            elif in_explanation:
                explanation += ' ' + line
        
        # 构建习题对象
        question = ' '.join(question_lines)
        
        if exercise_type == 'multiple_choice':
            exercise = {
                'question': question or '请根据知识点回答以下问题',
                'options': options or ['选项A', '选项B', '选项C', '选项D'],
                'correct_answer': correct_answer or 'A',
                'explanation': explanation or '本题考查相关知识点，正确答案为选项A'
            }
        
        elif exercise_type == 'true_false':
            exercise = {
                'question': question or '请判断以下陈述是否正确',
                'correct_answer': correct_answer.lower() == 'true' if correct_answer else True,
                'explanation': explanation or '本题考查相关知识点，正确答案为True'
            }
        
        elif exercise_type == 'fill_blank':
            exercise = {
                'question': question or '请填写以下空白处',
                'correct_answers': [correct_answer] if correct_answer else ['答案'],
                'explanation': explanation or '本题考查相关知识点，正确答案为上述内容'
            }
        
        elif exercise_type == 'coding':
            exercise = {
                'question': question or '请编写代码解决以下问题',
                'requirements': '请根据题目要求编写代码',
                'input_format': '输入格式：根据题目要求',
                'output_format': '输出格式：根据题目要求',
                'examples': [{'input': '输入示例', 'output': '输出示例'}],
                'correct_answer': correct_answer or 'def solution():\n    # 请在此处编写代码\n    pass',
                'explanation': explanation or '本题考查编程能力，正确答案如上所示'
            }
        
        elif exercise_type == 'short_answer':
            exercise = {
                'question': question or '请简要回答以下问题',
                'correct_answer': correct_answer or '正确答案',
                'explanation': explanation or '本题考查相关知识点，正确答案如上所示'
            }
        
        return exercise
    
    def _validate_exercise(self, exercise: Dict[str, Any], exercise_type: str) -> bool:
        """验证习题格式"""
        required_fields = {
            'multiple_choice': ['question', 'options', 'correct_answer', 'explanation'],
            'true_false': ['question', 'correct_answer', 'explanation'],
            'fill_blank': ['question', 'correct_answers', 'explanation'],
            'coding': ['question', 'requirements', 'input_format', 'output_format', 'examples', 'correct_answer', 'explanation'],
            'short_answer': ['question', 'correct_answer', 'explanation']
        }
        
        if exercise_type not in required_fields:
            return False
        
        for field in required_fields[exercise_type]:
            if field not in exercise:
                return False
        
        return True
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def generate_exercise_set(self, knowledge_tree: Dict[str, Any], 
                            difficulty_distribution: Dict[str, float] = None,
                            type_distribution: Dict[str, float] = None,
                            total_count: int = 10) -> Dict[str, Any]:
        """
        生成习题集
        
        Args:
            knowledge_tree: 知识点树结构
            difficulty_distribution: 难度分布
            type_distribution: 类型分布
            total_count: 总题数
        
        Returns:
            习题集
        """
        try:
            # 默认分布
            if not difficulty_distribution:
                difficulty_distribution = {
                    'easy': 0.3,
                    'medium': 0.5,
                    'hard': 0.2
                }
            
            if not type_distribution:
                type_distribution = {
                    'multiple_choice': 0.4,
                    'true_false': 0.2,
                    'fill_blank': 0.2,
                    'short_answer': 0.1,
                    'coding': 0.1
                }
            
            # 计算各类习题数量
            exercises = []
            
            # 从知识点树中提取所有知识点
            all_knowledge_points = self._extract_knowledge_points(knowledge_tree)
            
            if not all_knowledge_points:
                return {
                    'error': '知识点树中没有知识点',
                    'exercises': []
                }
            
            # 按分布生成习题
            for exercise_type, type_ratio in type_distribution.items():
                type_count = max(1, int(total_count * type_ratio))
                
                for difficulty, diff_ratio in difficulty_distribution.items():
                    diff_count = max(1, int(type_count * diff_ratio))
                    
                    # 随机选择知识点
                    selected_points = random.sample(
                        all_knowledge_points, 
                        min(len(all_knowledge_points), 3)
                    )
                    
                    # 生成习题
                    result = self.generate_exercises(
                        selected_points,
                        exercise_type,
                        difficulty,
                        diff_count
                    )
                    
                    exercises.extend(result.get('exercises', []))
            
            # 随机打乱顺序
            random.shuffle(exercises)
            
            # 截取指定数量
            exercises = exercises[:total_count]
            
            return {
                'exercises': exercises,
                'total_count': len(exercises),
                'difficulty_distribution': difficulty_distribution,
                'type_distribution': type_distribution
            }
            
        except Exception as e:
            return {
                'error': f'生成习题集失败: {str(e)}',
                'exercises': []
            }
    
    def _extract_knowledge_points(self, knowledge_tree: Dict[str, Any]) -> List[str]:
        """从知识点树中提取所有知识点"""
        points = []
        
        def extract(node):
            if 'name' in node:
                points.append(node['name'])
            if 'children' in node:
                for child in node['children']:
                    extract(child)
        
        extract(knowledge_tree)
        return points
    
    def get_recommended_exercises(self, user_id: int, count: int = 5) -> Dict[str, Any]:
        """
        根据用户学习情况推荐习题
        
        Args:
            user_id: 用户ID
            count: 推荐数量
        
        Returns:
            推荐习题
        """
        try:
            # 这里可以根据用户的学习记录、错误记录等信息推荐习题
            # 暂时返回随机生成的习题
            
            # 从数据库获取知识点
            knowledge_nodes = KnowledgeNode.objects.all()[:10]
            knowledge_points = [node.name for node in knowledge_nodes]
            
            if not knowledge_points:
                knowledge_points = ['Python基础', '数据结构', '算法']
            
            # 生成推荐习题
            exercise_types = list(self.exercise_types.keys())
            difficulties = ['easy', 'medium', 'hard']
            
            exercises = []
            for i in range(count):
                exercise_type = random.choice(exercise_types)
                difficulty = random.choice(difficulties)
                
                # 随机选择知识点
                selected_points = random.sample(
                    knowledge_points, 
                    min(len(knowledge_points), 2)
                )
                
                # 生成习题
                result = self.generate_exercises(
                    selected_points,
                    exercise_type,
                    difficulty,
                    1
                )
                
                exercises.extend(result.get('exercises', []))
            
            return {
                'exercises': exercises,
                'count': len(exercises),
                'recommendation_type': 'personalized'
            }
            
        except Exception as e:
            return {
                'error': f'推荐习题失败: {str(e)}',
                'exercises': []
            }


# 全局习题生成器实例
exercise_generator = ExerciseGenerator()