"""自适应难度调整引擎

该模块实现自适应难度调整功能，根据用户的学习表现和能力水平，
自动调整练习题和学习内容的难度，确保学习内容始终处于用户的最近发展区。
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone

from apps.learning.models import LearningRecord, PracticeRecord, KnowledgeMastery


class AdaptiveDifficultyEngine:
    """自适应难度调整引擎
    
    核心功能：
    1. 评估用户能力水平
    2. 计算适合的内容难度
    3. 动态调整难度
    4. 生成难度调整建议
    """
    
    def __init__(self):
        """初始化难度调整引擎"""
        pass
    
    def evaluate_user_ability(self, user_id: int) -> Dict[str, Any]:
        """评估用户能力水平
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含用户能力评估结果的字典
        """
        try:
            # 获取用户练习记录
            practice_records = PracticeRecord.objects.filter(user_id=user_id).order_by('-created_at')
            
            if not practice_records.exists():
                return {
                    'error': '用户练习数据不足',
                    'ability_level': None
                }
            
            # 计算平均成绩
            avg_score = practice_records.aggregate(Avg('score'))['score__avg'] or 0
            
            # 计算成绩趋势
            trend = self._calculate_score_trend(practice_records)
            
            # 计算能力水平
            ability_level = self._calculate_ability_level(avg_score, trend)
            
            # 分析知识点掌握情况
            knowledge_mastery = self._analyze_knowledge_mastery(user_id)
            
            return {
                'ability_level': ability_level,
                'average_score': avg_score,
                'score_trend': trend,
                'knowledge_mastery': knowledge_mastery,
                'data_available': True,
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'error': f'评估失败: {str(e)}',
                'ability_level': None
            }
    
    def calculate_optimal_difficulty(self, user_id: int, knowledge_node_id: Optional[int] = None) -> Dict[str, Any]:
        """计算适合的内容难度
        
        Args:
            user_id: 用户ID
            knowledge_node_id: 知识点ID（可选）
            
        Returns:
            包含最优难度计算结果的字典
        """
        try:
            # 评估用户能力水平
            ability_evaluation = self.evaluate_user_ability(user_id)
            
            if 'error' in ability_evaluation:
                return {
                    'error': ability_evaluation['error'],
                    'optimal_difficulty': None
                }
            
            # 基础难度基于能力水平
            base_difficulty = ability_evaluation['ability_level']
            
            # 如果指定了知识点，考虑该知识点的掌握情况
            if knowledge_node_id:
                knowledge_adjustment = self._get_knowledge_difficulty_adjustment(user_id, knowledge_node_id)
                base_difficulty += knowledge_adjustment
            
            # 应用难度调整策略
            optimal_difficulty = self._apply_difficulty_strategy(base_difficulty, ability_evaluation['score_trend'])
            
            # 确保难度在合理范围内（1-5）
            optimal_difficulty = max(1, min(5, optimal_difficulty))
            
            return {
                'optimal_difficulty': optimal_difficulty,
                'ability_level': ability_evaluation['ability_level'],
                'adjustment_reason': self._generate_adjustment_reason(optimal_difficulty, ability_evaluation),
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'error': f'计算失败: {str(e)}',
                'optimal_difficulty': None
            }
    
    def adjust_difficulty(self, user_id: int, current_difficulty: float, performance: float) -> Dict[str, Any]:
        """根据用户表现动态调整难度
        
        Args:
            user_id: 用户ID
            current_difficulty: 当前难度
            performance: 用户表现（0-100）
            
        Returns:
            包含难度调整结果的字典
        """
        try:
            # 计算难度调整量
            adjustment = self._calculate_difficulty_adjustment(performance, current_difficulty)
            
            # 应用调整
            new_difficulty = current_difficulty + adjustment
            
            # 确保难度在合理范围内（1-5）
            new_difficulty = max(1, min(5, new_difficulty))
            
            # 记录调整历史
            adjustment_history = self._record_adjustment_history(user_id, current_difficulty, new_difficulty, performance)
            
            return {
                'old_difficulty': current_difficulty,
                'new_difficulty': new_difficulty,
                'adjustment': adjustment,
                'adjustment_reason': self._generate_adjustment_reason(new_difficulty, {'score_trend': 'improving' if adjustment > 0 else 'declining'}),
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'error': f'调整失败: {str(e)}',
                'new_difficulty': None
            }
    
    def generate_difficulty_recommendations(self, user_id: int) -> Dict[str, Any]:
        """生成难度调整建议
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含难度调整建议的字典
        """
        try:
            # 评估用户能力水平
            ability_evaluation = self.evaluate_user_ability(user_id)
            
            if 'error' in ability_evaluation:
                return {
                    'error': ability_evaluation['error'],
                    'recommendations': []
                }
            
            # 生成个性化建议
            recommendations = []
            
            # 基于能力水平的建议
            ability_recommendations = self._generate_ability_based_recommendations(ability_evaluation['ability_level'])
            recommendations.extend(ability_recommendations)
            
            # 基于成绩趋势的建议
            trend_recommendations = self._generate_trend_based_recommendations(ability_evaluation['score_trend'])
            recommendations.extend(trend_recommendations)
            
            # 基于知识点掌握的建议
            mastery_recommendations = self._generate_mastery_based_recommendations(ability_evaluation['knowledge_mastery'])
            recommendations.extend(mastery_recommendations)
            
            return {
                'recommendations': recommendations,
                'ability_evaluation': ability_evaluation,
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'error': f'生成建议失败: {str(e)}',
                'recommendations': []
            }
    
    def _calculate_score_trend(self, practice_records) -> str:
        """计算成绩趋势
        
        Args:
            practice_records: 练习记录集合
            
        Returns:
            成绩趋势类型: 'improving', 'declining', 'stable'
        """
        if practice_records.count() < 3:
            return 'insufficient_data'
        
        # 按时间顺序获取成绩
        scores = [record.score for record in practice_records.order_by('created_at') if record.score]
        
        if len(scores) < 3:
            return 'insufficient_data'
        
        # 计算线性回归斜率
        n = len(scores)
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(scores)
        sum_xy = sum(x[i] * scores[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return 'stable'
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 2:
            return 'improving'
        elif slope < -2:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_ability_level(self, avg_score: float, trend: str) -> float:
        """计算能力水平
        
        Args:
            avg_score: 平均成绩
            trend: 成绩趋势
            
        Returns:
            能力水平（1-5）
        """
        # 基础能力水平基于平均成绩
        base_ability = min(5, max(1, (avg_score / 20) + 1))
        
        # 根据趋势调整
        if trend == 'improving':
            base_ability += 0.5
        elif trend == 'declining':
            base_ability -= 0.5
        
        # 确保在合理范围内
        return max(1, min(5, base_ability))
    
    def _analyze_knowledge_mastery(self, user_id: int) -> Dict[str, Any]:
        """分析知识点掌握情况
        
        Args:
            user_id: 用户ID
            
        Returns:
            知识点掌握情况分析结果
        """
        # 获取用户知识点掌握记录
        mastery_records = KnowledgeMastery.objects.filter(user_id=user_id)
        
        if not mastery_records.exists():
            return {
                'mastery_levels': {},
                'average_mastery': 0,
                'total_knowledge_points': 0
            }
        
        # 计算平均掌握度
        avg_mastery = mastery_records.aggregate(Avg('mastery_level'))['mastery_level__avg'] or 0
        
        # 按掌握度分类知识点
        mastery_levels = {}
        for record in mastery_records:
            mastery_levels[record.knowledge_point] = record.mastery_level
        
        return {
            'mastery_levels': mastery_levels,
            'average_mastery': avg_mastery,
            'total_knowledge_points': mastery_records.count()
        }
    
    def _get_knowledge_difficulty_adjustment(self, user_id: int, knowledge_node_id: int) -> float:
        """获取知识点难度调整量
        
        Args:
            user_id: 用户ID
            knowledge_node_id: 知识点ID
            
        Returns:
            难度调整量
        """
        try:
            # 查找该知识点的掌握记录
            mastery_record = KnowledgeMastery.objects.filter(
                user_id=user_id,
                knowledge_point__id=knowledge_node_id
            ).first()
            
            if mastery_record:
                # 掌握度高则增加难度，掌握度低则降低难度
                return (mastery_record.mastery_level - 0.5) * 2
            else:
                return 0
        except Exception:
            return 0
    
    def _apply_difficulty_strategy(self, base_difficulty: float, trend: str) -> float:
        """应用难度调整策略
        
        Args:
            base_difficulty: 基础难度
            trend: 成绩趋势
            
        Returns:
            调整后的难度
        """
        # 根据趋势调整难度
        if trend == 'improving':
            # 成绩提升，适当增加难度
            return base_difficulty + 0.3
        elif trend == 'declining':
            # 成绩下降，适当降低难度
            return base_difficulty - 0.3
        else:
            # 成绩稳定，保持难度
            return base_difficulty
    
    def _calculate_difficulty_adjustment(self, performance: float, current_difficulty: float) -> float:
        """计算难度调整量
        
        Args:
            performance: 用户表现（0-100）
            current_difficulty: 当前难度
            
        Returns:
            难度调整量
        """
        # 表现优秀，增加难度
        if performance >= 90:
            return 0.5
        # 表现良好，小幅增加难度
        elif performance >= 70:
            return 0.2
        # 表现一般，保持难度
        elif performance >= 40:
            return 0
        # 表现较差，降低难度
        else:
            return -0.5
    
    def _record_adjustment_history(self, user_id: int, old_difficulty: float, new_difficulty: float, performance: float) -> Dict[str, Any]:
        """记录难度调整历史
        
        Args:
            user_id: 用户ID
            old_difficulty: 调整前难度
            new_difficulty: 调整后难度
            performance: 用户表现
            
        Returns:
            调整历史记录
        """
        # 这里可以实现历史记录的存储
        # 暂时返回调整信息
        return {
            'timestamp': datetime.now().isoformat(),
            'old_difficulty': old_difficulty,
            'new_difficulty': new_difficulty,
            'performance': performance,
            'adjustment': new_difficulty - old_difficulty
        }
    
    def _generate_adjustment_reason(self, new_difficulty: float, evaluation: Dict[str, Any]) -> str:
        """生成难度调整理由
        
        Args:
            new_difficulty: 新难度
            evaluation: 能力评估结果
            
        Returns:
            调整理由
        """
        if new_difficulty >= 4.5:
            return '基于您的优秀表现，推荐挑战更高难度的内容'
        elif new_difficulty >= 3.5:
            return '您的能力水平良好，推荐适中难度的内容'
        elif new_difficulty >= 2.5:
            return '建议从基础内容开始，逐步提高难度'
        else:
            return '推荐从简单内容开始，打好基础'
    
    def _generate_ability_based_recommendations(self, ability_level: float) -> List[Dict[str, Any]]:
        """生成基于能力水平的建议
        
        Args:
            ability_level: 能力水平
            
        Returns:
            建议列表
        """
        recommendations = []
        
        if ability_level >= 4:
            recommendations.append({
                'title': '挑战高难度内容',
                'description': '您的能力水平较高，建议尝试更具挑战性的内容',
                'priority': 'high',
                'estimated_time': 30
            })
        elif ability_level >= 3:
            recommendations.append({
                'title': '巩固中等难度内容',
                'description': '建议继续巩固中等难度的内容，逐步提高',
                'priority': 'medium',
                'estimated_time': 20
            })
        else:
            recommendations.append({
                'title': '加强基础知识',
                'description': '建议从基础内容开始，打好基础',
                'priority': 'high',
                'estimated_time': 45
            })
        
        return recommendations
    
    def _generate_trend_based_recommendations(self, trend: str) -> List[Dict[str, Any]]:
        """生成基于成绩趋势的建议
        
        Args:
            trend: 成绩趋势
            
        Returns:
            建议列表
        """
        recommendations = []
        
        if trend == 'improving':
            recommendations.append({
                'title': '适当增加难度',
                'description': '您的成绩呈上升趋势，建议适当增加学习内容的难度',
                'priority': 'medium',
                'estimated_time': 25
            })
        elif trend == 'declining':
            recommendations.append({
                'title': '调整学习策略',
                'description': '您的成绩呈下降趋势，建议调整学习策略，巩固基础',
                'priority': 'high',
                'estimated_time': 30
            })
        elif trend == 'stable':
            recommendations.append({
                'title': '保持当前节奏',
                'description': '您的成绩保持稳定，建议保持当前的学习节奏',
                'priority': 'low',
                'estimated_time': 15
            })
        
        return recommendations
    
    def _generate_mastery_based_recommendations(self, knowledge_mastery: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于知识点掌握的建议
        
        Args:
            knowledge_mastery: 知识点掌握情况
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 分析掌握度较低的知识点
        low_mastery_points = [k for k, v in knowledge_mastery['mastery_levels'].items() if v < 0.5]
        
        if low_mastery_points:
            recommendations.append({
                'title': '加强薄弱知识点',
                'description': f'建议重点加强以下知识点：{low_mastery_points[:3]}',
                'priority': 'high',
                'estimated_time': 30
            })
        
        # 分析掌握度较高的知识点
        high_mastery_points = [k for k, v in knowledge_mastery['mastery_levels'].items() if v > 0.8]
        
        if high_mastery_points:
            recommendations.append({
                'title': '拓展相关知识',
                'description': f'您已掌握以下知识点：{high_mastery_points[:3]}，建议学习相关的进阶内容',
                'priority': 'medium',
                'estimated_time': 25
            })
        
        return recommendations


# 全局难度调整引擎实例
adaptive_difficulty_engine = AdaptiveDifficultyEngine()