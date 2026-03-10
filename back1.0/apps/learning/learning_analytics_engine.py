"""学习智能分析引擎

该模块实现学情智能分析功能，基于用户的学习行为数据，
分析学习模式、习惯和效果，提供个性化的学习建议和改进方案。
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone

from apps.learning.models import LearningRecord, PracticeRecord, StrategyUserProfile, KnowledgeNode


class LearningAnalyticsEngine:
    """学习智能分析引擎
    
    核心功能：
    1. 分析学习行为模式
    2. 识别学习习惯和偏好
    3. 检测学习障碍和瓶颈
    4. 生成个性化学习建议
    5. 提供学习效率分析
    """
    
    def __init__(self):
        """初始化分析引擎"""
        pass
    
    def analyze_learning_patterns(self, user_id: int) -> Dict[str, Any]:
        """分析用户学习模式
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含学习模式分析结果的字典
        """
        try:
            # 获取用户学习记录
            learning_records = LearningRecord.objects.filter(user_id=user_id).order_by('-created_at')
            
            if not learning_records.exists():
                return {
                    'error': '用户学习数据不足',
                    'patterns': None
                }
            
            # 分析学习时间分布
            time_distribution = self._analyze_time_distribution(learning_records)
            
            # 分析学习内容分布
            content_distribution = self._analyze_content_distribution(learning_records)
            
            # 分析学习效率
            learning_efficiency = self._analyze_learning_efficiency(learning_records)
            
            # 分析学习习惯
            learning_habits = self._analyze_learning_habits(learning_records)
            
            # 分析学习进展
            learning_progress = self._analyze_learning_progress(user_id)
            
            return {
                'patterns': {
                    'time_distribution': time_distribution,
                    'content_distribution': content_distribution,
                    'learning_efficiency': learning_efficiency,
                    'learning_habits': learning_habits,
                    'learning_progress': learning_progress
                },
                'data_available': True,
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'error': f'分析失败: {str(e)}',
                'patterns': None
            }
    
    def _analyze_time_distribution(self, learning_records) -> Dict[str, Any]:
        """分析学习时间分布
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            时间分布分析结果
        """
        # 按小时分析学习时间
        hourly_distribution = {hour: 0 for hour in range(24)}
        daily_distribution = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        
        for record in learning_records:
            hour = record.created_at.hour
            day_of_week = record.created_at.strftime('%A')
            hourly_distribution[hour] += 1
            daily_distribution[day_of_week] += 1
        
        # 找出学习高峰期
        peak_hour = max(hourly_distribution, key=hourly_distribution.get)
        peak_day = max(daily_distribution, key=daily_distribution.get)
        
        return {
            'hourly_distribution': hourly_distribution,
            'daily_distribution': daily_distribution,
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'total_learning_sessions': len(learning_records)
        }
    
    def _analyze_content_distribution(self, learning_records) -> Dict[str, Any]:
        """分析学习内容分布
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            内容分布分析结果
        """
        # 分析知识点分布
        knowledge_distribution = {}
        
        for record in learning_records:
            if record.knowledge_node:
                node_name = record.knowledge_node.title
                if node_name not in knowledge_distribution:
                    knowledge_distribution[node_name] = 0
                knowledge_distribution[node_name] += 1
        
        # 找出最常学习的知识点
        if knowledge_distribution:
            most_studied = max(knowledge_distribution, key=knowledge_distribution.get)
        else:
            most_studied = None
        
        return {
            'knowledge_distribution': knowledge_distribution,
            'most_studied_knowledge': most_studied,
            'unique_knowledge_nodes': len(knowledge_distribution)
        }
    
    def _analyze_learning_efficiency(self, learning_records) -> Dict[str, Any]:
        """分析学习效率
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            学习效率分析结果
        """
        # 计算学习时长和频率
        total_duration = sum(record.duration for record in learning_records if record.duration)
        average_duration = total_duration / len(learning_records) if learning_records else 0
        
        # 计算学习频率（每天平均学习次数）
        if learning_records:
            first_record = learning_records.last()
            last_record = learning_records.first()
            days_diff = (last_record.created_at - first_record.created_at).days + 1
            daily_frequency = len(learning_records) / days_diff
        else:
            daily_frequency = 0
        
        # 分析学习连续性
        continuity_score = self._calculate_continuity_score(learning_records)
        
        return {
            'total_learning_time': total_duration,
            'average_session_duration': average_duration,
            'daily_frequency': daily_frequency,
            'continuity_score': continuity_score,
            'efficiency_level': self._get_efficiency_level(continuity_score, daily_frequency)
        }
    
    def _calculate_continuity_score(self, learning_records) -> float:
        """计算学习连续性得分
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            连续性得分（0-100）
        """
        if not learning_records:
            return 0
        
        # 按日期分组
        daily_records = {}
        for record in learning_records:
            date_key = record.created_at.date()
            if date_key not in daily_records:
                daily_records[date_key] = []
            daily_records[date_key].append(record)
        
        # 计算连续学习天数
        sorted_dates = sorted(daily_records.keys())
        max_streak = 0
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        # 计算连续性得分
        total_days = (sorted_dates[-1] - sorted_dates[0]).days + 1
        active_days = len(daily_records)
        continuity_score = (active_days / total_days) * 100
        
        return min(100, continuity_score)
    
    def _get_efficiency_level(self, continuity_score: float, daily_frequency: float) -> str:
        """获取学习效率等级
        
        Args:
            continuity_score: 连续性得分
            daily_frequency: 每天学习频率
            
        Returns:
            效率等级
        """
        if continuity_score >= 80 and daily_frequency >= 3:
            return 'excellent'
        elif continuity_score >= 60 and daily_frequency >= 2:
            return 'good'
        elif continuity_score >= 40 and daily_frequency >= 1:
            return 'average'
        else:
            return 'needs_improvement'
    
    def _analyze_learning_habits(self, learning_records) -> Dict[str, Any]:
        """分析学习习惯
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            学习习惯分析结果
        """
        # 分析学习时间偏好
        time_preference = self._analyze_time_preference(learning_records)
        
        # 分析学习时长偏好
        duration_preference = self._analyze_duration_preference(learning_records)
        
        # 分析学习频率模式
        frequency_pattern = self._analyze_frequency_pattern(learning_records)
        
        return {
            'time_preference': time_preference,
            'duration_preference': duration_preference,
            'frequency_pattern': frequency_pattern
        }
    
    def _analyze_time_preference(self, learning_records) -> str:
        """分析学习时间偏好
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            时间偏好类型
        """
        morning_count = 0
        afternoon_count = 0
        evening_count = 0
        
        for record in learning_records:
            hour = record.created_at.hour
            if 6 <= hour < 12:
                morning_count += 1
            elif 12 <= hour < 18:
                afternoon_count += 1
            else:
                evening_count += 1
        
        max_count = max(morning_count, afternoon_count, evening_count)
        if max_count == morning_count:
            return 'morning'
        elif max_count == afternoon_count:
            return 'afternoon'
        else:
            return 'evening'
    
    def _analyze_duration_preference(self, learning_records) -> str:
        """分析学习时长偏好
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            时长偏好类型
        """
        short_sessions = 0  # < 15分钟
        medium_sessions = 0  # 15-60分钟
        long_sessions = 0  # > 60分钟
        
        for record in learning_records:
            duration = record.duration or 0
            if duration < 15:
                short_sessions += 1
            elif duration < 60:
                medium_sessions += 1
            else:
                long_sessions += 1
        
        max_count = max(short_sessions, medium_sessions, long_sessions)
        if max_count == short_sessions:
            return 'short'
        elif max_count == medium_sessions:
            return 'medium'
        else:
            return 'long'
    
    def _analyze_frequency_pattern(self, learning_records) -> str:
        """分析学习频率模式
        
        Args:
            learning_records: 学习记录集合
            
        Returns:
            频率模式类型
        """
        if not learning_records:
            return 'no_pattern'
        
        # 计算每天的学习次数
        daily_counts = {}
        for record in learning_records:
            date_key = record.created_at.date()
            if date_key not in daily_counts:
                daily_counts[date_key] = 0
            daily_counts[date_key] += 1
        
        # 分析频率模式
        average_daily = sum(daily_counts.values()) / len(daily_counts)
        if average_daily >= 3:
            return 'frequent'
        elif average_daily >= 1:
            return 'regular'
        else:
            return 'occasional'
    
    def _analyze_learning_progress(self, user_id: int) -> Dict[str, Any]:
        """分析学习进展
        
        Args:
            user_id: 用户ID
            
        Returns:
            学习进展分析结果
        """
        # 获取用户练习记录
        practice_records = PracticeRecord.objects.filter(user_id=user_id).order_by('created_at')
        
        # 分析练习成绩趋势
        score_trend = self._analyze_score_trend(practice_records)
        
        # 分析知识点掌握情况
        knowledge_mastery = self._analyze_knowledge_mastery(user_id)
        
        # 分析学习完成度
        completion_rate = self._analyze_completion_rate(user_id)
        
        return {
            'score_trend': score_trend,
            'knowledge_mastery': knowledge_mastery,
            'completion_rate': completion_rate
        }
    
    def _analyze_score_trend(self, practice_records) -> Dict[str, Any]:
        """分析练习成绩趋势
        
        Args:
            practice_records: 练习记录集合
            
        Returns:
            成绩趋势分析结果
        """
        if not practice_records.exists():
            return {
                'trend': 'insufficient_data',
                'average_score': 0,
                'score_improvement': 0
            }
        
        # 计算平均成绩
        scores = [record.score for record in practice_records if record.score]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # 分析成绩趋势
        if len(scores) >= 2:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            first_average = sum(first_half) / len(first_half)
            second_average = sum(second_half) / len(second_half)
            score_improvement = second_average - first_average
            
            if score_improvement > 5:
                trend = 'improving'
            elif score_improvement < -5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
            score_improvement = 0
        
        return {
            'trend': trend,
            'average_score': average_score,
            'score_improvement': score_improvement
        }
    
    def _analyze_knowledge_mastery(self, user_id: int) -> Dict[str, Any]:
        """分析知识点掌握情况
        
        Args:
            user_id: 用户ID
            
        Returns:
            知识点掌握情况分析结果
        """
        # 获取用户练习记录按知识点分组
        practice_by_knowledge = PracticeRecord.objects.filter(
            user_id=user_id
        ).values('knowledge_node__title').annotate(
            average_score=Avg('score'),
            practice_count=Count('id')
        )
        
        mastery_levels = {}
        for item in practice_by_knowledge:
            knowledge_title = item['knowledge_node__title']
            avg_score = item['average_score'] or 0
            
            if avg_score >= 80:
                mastery_levels[knowledge_title] = 'excellent'
            elif avg_score >= 60:
                mastery_levels[knowledge_title] = 'good'
            else:
                mastery_levels[knowledge_title] = 'needs_improvement'
        
        return {
            'mastery_levels': mastery_levels,
            'total_knowledge_nodes': len(mastery_levels)
        }
    
    def _analyze_completion_rate(self, user_id: int) -> float:
        """分析学习完成度
        
        Args:
            user_id: 用户ID
            
        Returns:
            完成率（0-100）
        """
        # 获取用户学习的知识点数量
        learned_nodes = LearningRecord.objects.filter(
            user_id=user_id
        ).values('knowledge_node').distinct().count()
        
        # 获取总知识点数量
        total_nodes = KnowledgeNode.objects.count()
        
        if total_nodes == 0:
            return 0
        
        completion_rate = (learned_nodes / total_nodes) * 100
        return min(100, completion_rate)
    
    def generate_learning_recommendations(self, user_id: int) -> Dict[str, Any]:
        """生成学习建议
        
        Args:
            user_id: 用户ID
            
        Returns:
            学习建议
        """
        try:
            # 分析学习模式
            analysis_result = self.analyze_learning_patterns(user_id)
            
            if 'error' in analysis_result:
                return {
                    'error': analysis_result['error'],
                    'recommendations': []
                }
            
            patterns = analysis_result['patterns']
            
            # 生成个性化建议
            recommendations = []
            
            # 基于时间分布的建议
            time_recommendations = self._generate_time_based_recommendations(patterns['time_distribution'])
            recommendations.extend(time_recommendations)
            
            # 基于学习效率的建议
            efficiency_recommendations = self._generate_efficiency_based_recommendations(patterns['learning_efficiency'])
            recommendations.extend(efficiency_recommendations)
            
            # 基于学习习惯的建议
            habit_recommendations = self._generate_habit_based_recommendations(patterns['learning_habits'])
            recommendations.extend(habit_recommendations)
            
            # 基于学习进展的建议
            progress_recommendations = self._generate_progress_based_recommendations(patterns['learning_progress'])
            recommendations.extend(progress_recommendations)
            
            # 基于内容分布的建议
            content_recommendations = self._generate_content_based_recommendations(patterns['content_distribution'])
            recommendations.extend(content_recommendations)
            
            return {
                'recommendations': recommendations,
                'analysis': patterns,
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'error': f'生成建议失败: {str(e)}',
                'recommendations': []
            }
    
    def _generate_time_based_recommendations(self, time_distribution: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于时间分布的建议
        
        Args:
            time_distribution: 时间分布分析结果
            
        Returns:
            时间相关建议列表
        """
        recommendations = []
        
        # 基于学习高峰期的建议
        peak_hour = time_distribution['peak_hour']
        if 6 <= peak_hour < 12:
            recommendations.append({
                'title': '保持晨学习惯',
                'description': '您在早晨学习效率较高，建议继续保持这个好习惯',
                'priority': 'high',
                'estimated_time': 5
            })
        elif 12 <= peak_hour < 18:
            recommendations.append({
                'title': '利用下午时间',
                'description': '您在下午学习效果较好，建议安排重要内容在这个时段学习',
                'priority': 'high',
                'estimated_time': 5
            })
        else:
            recommendations.append({
                'title': '注意休息',
                'description': '您在晚上学习较多，注意合理安排作息时间',
                'priority': 'medium',
                'estimated_time': 5
            })
        
        # 基于学习频率的建议
        total_sessions = time_distribution['total_learning_sessions']
        if total_sessions < 10:
            recommendations.append({
                'title': '增加学习频率',
                'description': '建议增加学习频率，每天至少进行1-2次学习会话',
                'priority': 'high',
                'estimated_time': 10
            })
        
        return recommendations
    
    def _generate_efficiency_based_recommendations(self, learning_efficiency: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于学习效率的建议
        
        Args:
            learning_efficiency: 学习效率分析结果
            
        Returns:
            效率相关建议列表
        """
        recommendations = []
        
        efficiency_level = learning_efficiency['efficiency_level']
        
        if efficiency_level == 'needs_improvement':
            recommendations.append({
                'title': '提高学习连续性',
                'description': '建议建立固定的学习时间表，提高学习的连续性',
                'priority': 'high',
                'estimated_time': 15
            })
        
        continuity_score = learning_efficiency['continuity_score']
        if continuity_score < 50:
            recommendations.append({
                'title': '培养学习习惯',
                'description': '建议每天固定时间学习，培养良好的学习习惯',
                'priority': 'medium',
                'estimated_time': 10
            })
        
        average_duration = learning_efficiency['average_session_duration']
        if average_duration < 15:
            recommendations.append({
                'title': '延长学习时间',
                'description': '建议每次学习时间不少于15分钟，以提高学习效果',
                'priority': 'medium',
                'estimated_time': 5
            })
        
        return recommendations
    
    def _generate_habit_based_recommendations(self, learning_habits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于学习习惯的建议
        
        Args:
            learning_habits: 学习习惯分析结果
            
        Returns:
            习惯相关建议列表
        """
        recommendations = []
        
        time_preference = learning_habits['time_preference']
        duration_preference = learning_habits['duration_preference']
        frequency_pattern = learning_habits['frequency_pattern']
        
        if frequency_pattern == 'occasional':
            recommendations.append({
                'title': '建立规律学习计划',
                'description': '建议制定每周学习计划，保持规律的学习节奏',
                'priority': 'high',
                'estimated_time': 20
            })
        
        if duration_preference == 'short':
            recommendations.append({
                'title': '增加单次学习时长',
                'description': '建议适当延长单次学习时间，深入理解学习内容',
                'priority': 'medium',
                'estimated_time': 10
            })
        
        return recommendations
    
    def _generate_progress_based_recommendations(self, learning_progress: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于学习进展的建议
        
        Args:
            learning_progress: 学习进展分析结果
            
        Returns:
            进展相关建议列表
        """
        recommendations = []
        
        score_trend = learning_progress['score_trend']
        if score_trend['trend'] == 'declining':
            recommendations.append({
                'title': '分析成绩下降原因',
                'description': '建议分析成绩下降的原因，调整学习方法',
                'priority': 'high',
                'estimated_time': 15
            })
        
        knowledge_mastery = learning_progress['knowledge_mastery']
        needs_improvement = [k for k, v in knowledge_mastery['mastery_levels'].items() if v == 'needs_improvement']
        if needs_improvement:
            recommendations.append({
                'title': '加强薄弱知识点',
                'description': f'建议重点加强以下知识点：{needs_improvement[:3]}',
                'priority': 'high',
                'estimated_time': 20
            })
        
        completion_rate = learning_progress['completion_rate']
        if completion_rate < 30:
            recommendations.append({
                'title': '扩大学习范围',
                'description': '建议扩大学习范围，接触更多知识点',
                'priority': 'medium',
                'estimated_time': 15
            })
        
        return recommendations
    
    def _generate_content_based_recommendations(self, content_distribution: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于内容分布的建议
        
        Args:
            content_distribution: 内容分布分析结果
            
        Returns:
            内容相关建议列表
        """
        recommendations = []
        
        unique_nodes = content_distribution['unique_knowledge_nodes']
        if unique_nodes < 5:
            recommendations.append({
                'title': '多样化学习内容',
                'description': '建议学习更多不同类型的知识点，拓宽知识面',
                'priority': 'medium',
                'estimated_time': 10
            })
        
        return recommendations


# 全局分析引擎实例
learning_analytics_engine = LearningAnalyticsEngine()
