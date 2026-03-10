"""学习摘要生成引擎

该模块实现学习摘要生成功能，根据用户的学习记录和学习数据，
自动生成学习摘要，帮助用户回顾和总结学习内容。
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter


class LearningSummaryEngine:
    """学习摘要生成引擎
    
    核心功能：
    1. 分析学习记录
    2. 提取关键知识点
    3. 生成学习摘要
    4. 提供学习建议
    """
    
    def __init__(self):
        """初始化学习摘要生成引擎"""
        pass
    
    def generate_summary(self, user_id: int, time_range: str = 'week') -> Dict[str, Any]:
        """生成学习摘要
        
        Args:
            user_id: 用户ID
            time_range: 时间范围 ('day', 'week', 'month', 'year')
            
        Returns:
            包含学习摘要的字典
        """
        try:
            # 获取时间范围
            start_date, end_date = self._get_date_range(time_range)
            
            # 模拟获取学习记录
            learning_records = self._get_learning_records(user_id, start_date, end_date)
            
            # 分析学习记录
            analysis = self._analyze_learning_records(learning_records)
            
            # 生成摘要
            summary = self._generate_summary_text(analysis, time_range)
            
            # 提取关键知识点
            key_points = self._extract_key_points(learning_records)
            
            # 生成学习建议
            recommendations = self._generate_recommendations(analysis)
            
            # 计算学习统计数据
            statistics = self._calculate_statistics(learning_records)
            
            return {
                'summary': summary,
                'key_points': key_points,
                'recommendations': recommendations,
                'statistics': statistics,
                'time_range': time_range,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'生成学习摘要失败: {str(e)}',
                'summary': '无法生成学习摘要，请稍后重试'
            }
    
    def generate_topic_summary(self, user_id: int, topic: str) -> Dict[str, Any]:
        """生成特定主题的学习摘要
        
        Args:
            user_id: 用户ID
            topic: 主题
            
        Returns:
            包含主题学习摘要的字典
        """
        try:
            # 模拟获取主题相关的学习记录
            learning_records = self._get_topic_records(user_id, topic)
            
            # 分析学习记录
            analysis = self._analyze_learning_records(learning_records)
            
            # 生成主题摘要
            summary = self._generate_topic_summary_text(analysis, topic)
            
            # 提取关键知识点
            key_points = self._extract_key_points(learning_records)
            
            # 生成学习建议
            recommendations = self._generate_recommendations(analysis)
            
            # 计算学习统计数据
            statistics = self._calculate_statistics(learning_records)
            
            return {
                'summary': summary,
                'key_points': key_points,
                'recommendations': recommendations,
                'statistics': statistics,
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'生成主题学习摘要失败: {str(e)}',
                'summary': '无法生成主题学习摘要，请稍后重试'
            }
    
    def _get_date_range(self, time_range: str) -> tuple:
        """获取时间范围
        
        Args:
            time_range: 时间范围
            
        Returns:
            (开始日期, 结束日期)
        """
        end_date = datetime.now()
        
        if time_range == 'day':
            start_date = end_date - timedelta(days=1)
        elif time_range == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif time_range == 'month':
            start_date = end_date - timedelta(days=30)
        elif time_range == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(weeks=1)
        
        return start_date, end_date
    
    def _get_learning_records(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取学习记录
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            学习记录列表
        """
        # 模拟学习记录
        mock_records = [
            {
                'id': 1,
                'user_id': user_id,
                'content_type': 'video',
                'content_title': 'Python基础语法',
                'duration': 30,
                'completed': True,
                'score': 85,
                'timestamp': (end_date - timedelta(days=6)).isoformat(),
                'tags': ['Python', '基础语法', '变量', '数据类型']
            },
            {
                'id': 2,
                'user_id': user_id,
                'content_type': 'exercise',
                'content_title': 'Python变量和数据类型练习',
                'duration': 20,
                'completed': True,
                'score': 90,
                'timestamp': (end_date - timedelta(days=5)).isoformat(),
                'tags': ['Python', '变量', '数据类型', '练习']
            },
            {
                'id': 3,
                'user_id': user_id,
                'content_type': 'article',
                'content_title': 'Python函数编程',
                'duration': 45,
                'completed': True,
                'score': 80,
                'timestamp': (end_date - timedelta(days=4)).isoformat(),
                'tags': ['Python', '函数', '编程', '参数']
            },
            {
                'id': 4,
                'user_id': user_id,
                'content_type': 'video',
                'content_title': 'Python控制流',
                'duration': 35,
                'completed': True,
                'score': 88,
                'timestamp': (end_date - timedelta(days=3)).isoformat(),
                'tags': ['Python', '控制流', '条件语句', '循环']
            },
            {
                'id': 5,
                'user_id': user_id,
                'content_type': 'exercise',
                'content_title': 'Python控制流练习',
                'duration': 25,
                'completed': True,
                'score': 75,
                'timestamp': (end_date - timedelta(days=2)).isoformat(),
                'tags': ['Python', '控制流', '条件语句', '循环', '练习']
            },
            {
                'id': 6,
                'user_id': user_id,
                'content_type': 'article',
                'content_title': 'Python数据结构',
                'duration': 50,
                'completed': True,
                'score': 82,
                'timestamp': (end_date - timedelta(days=1)).isoformat(),
                'tags': ['Python', '数据结构', '列表', '字典', '元组']
            }
        ]
        
        # 过滤时间范围内的记录
        filtered_records = [
            record for record in mock_records
            if start_date <= datetime.fromisoformat(record['timestamp']) <= end_date
        ]
        
        return filtered_records
    
    def _get_topic_records(self, user_id: int, topic: str) -> List[Dict[str, Any]]:
        """获取主题相关的学习记录
        
        Args:
            user_id: 用户ID
            topic: 主题
            
        Returns:
            主题相关的学习记录列表
        """
        # 模拟主题相关的学习记录
        mock_records = [
            {
                'id': 1,
                'user_id': user_id,
                'content_type': 'video',
                'content_title': 'Python基础语法',
                'duration': 30,
                'completed': True,
                'score': 85,
                'timestamp': (datetime.now() - timedelta(days=10)).isoformat(),
                'tags': ['Python', '基础语法', '变量', '数据类型']
            },
            {
                'id': 2,
                'user_id': user_id,
                'content_type': 'exercise',
                'content_title': 'Python变量和数据类型练习',
                'duration': 20,
                'completed': True,
                'score': 90,
                'timestamp': (datetime.now() - timedelta(days=9)).isoformat(),
                'tags': ['Python', '变量', '数据类型', '练习']
            },
            {
                'id': 3,
                'user_id': user_id,
                'content_type': 'article',
                'content_title': 'Python函数编程',
                'duration': 45,
                'completed': True,
                'score': 80,
                'timestamp': (datetime.now() - timedelta(days=8)).isoformat(),
                'tags': ['Python', '函数', '编程', '参数']
            },
            {
                'id': 4,
                'user_id': user_id,
                'content_type': 'video',
                'content_title': 'Python控制流',
                'duration': 35,
                'completed': True,
                'score': 88,
                'timestamp': (datetime.now() - timedelta(days=7)).isoformat(),
                'tags': ['Python', '控制流', '条件语句', '循环']
            }
        ]
        
        # 过滤主题相关的记录
        filtered_records = [
            record for record in mock_records
            if topic.lower() in record['content_title'].lower() or 
               any(topic.lower() in tag.lower() for tag in record['tags'])
        ]
        
        return filtered_records
    
    def _analyze_learning_records(self, learning_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析学习记录
        
        Args:
            learning_records: 学习记录列表
            
        Returns:
            分析结果
        """
        if not learning_records:
            return {
                'total_records': 0,
                'total_duration': 0,
                'average_score': 0,
                'completed_records': 0,
                'content_type_distribution': {},
                'tag_distribution': {},
                'weekly_distribution': {},
                'daily_distribution': {}
            }
        
        # 计算总记录数
        total_records = len(learning_records)
        
        # 计算总学习时长
        total_duration = sum(record.get('duration', 0) for record in learning_records)
        
        # 计算平均得分
        scores = [record.get('score', 0) for record in learning_records if record.get('score')]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # 计算已完成记录数
        completed_records = sum(1 for record in learning_records if record.get('completed', False))
        
        # 内容类型分布
        content_type_distribution = Counter(record.get('content_type', 'unknown') for record in learning_records)
        
        # 标签分布
        all_tags = []
        for record in learning_records:
            all_tags.extend(record.get('tags', []))
        tag_distribution = Counter(all_tags)
        
        # 每周分布
        weekly_distribution = Counter()
        for record in learning_records:
            timestamp = datetime.fromisoformat(record['timestamp'])
            week_key = timestamp.strftime('%Y-W%U')
            weekly_distribution[week_key] += 1
        
        # 每日分布
        daily_distribution = Counter()
        for record in learning_records:
            timestamp = datetime.fromisoformat(record['timestamp'])
            day_key = timestamp.strftime('%Y-%m-%d')
            daily_distribution[day_key] += 1
        
        return {
            'total_records': total_records,
            'total_duration': total_duration,
            'average_score': average_score,
            'completed_records': completed_records,
            'content_type_distribution': dict(content_type_distribution),
            'tag_distribution': dict(tag_distribution),
            'weekly_distribution': dict(weekly_distribution),
            'daily_distribution': dict(daily_distribution)
        }
    
    def _generate_summary_text(self, analysis: Dict[str, Any], time_range: str) -> str:
        """生成学习摘要文本
        
        Args:
            analysis: 学习记录分析结果
            time_range: 时间范围
            
        Returns:
            学习摘要文本
        """
        if analysis['total_records'] == 0:
            return f'在过去的{self._get_time_range_text(time_range)}中，您没有学习记录。'
        
        # 时间范围文本
        time_range_text = self._get_time_range_text(time_range)
        
        # 内容类型分布文本
        content_type_text = ''
        for content_type, count in analysis['content_type_distribution'].items():
            content_type_text += f'{content_type} {count}个，'
        content_type_text = content_type_text.rstrip('，')
        
        # 标签分布文本
        top_tags = sorted(analysis['tag_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]
        top_tags_text = ', '.join([tag for tag, _ in top_tags])
        
        # 生成摘要
        summary = f'在过去的{time_range_text}中，您共完成了{analysis["completed_records"]}个学习内容，总学习时长为{analysis["total_duration"]}分钟，平均得分为{analysis["average_score"]:.1f}分。\n\n'
        summary += f'学习内容包括：{content_type_text}。\n\n'
        summary += f'主要学习主题包括：{top_tags_text}。\n\n'
        summary += '您的学习表现良好，继续保持！'
        
        return summary
    
    def _generate_topic_summary_text(self, analysis: Dict[str, Any], topic: str) -> str:
        """生成主题学习摘要文本
        
        Args:
            analysis: 学习记录分析结果
            topic: 主题
            
        Returns:
            主题学习摘要文本
        """
        if analysis['total_records'] == 0:
            return f'您还没有关于{topic}的学习记录。'
        
        # 内容类型分布文本
        content_type_text = ''
        for content_type, count in analysis['content_type_distribution'].items():
            content_type_text += f'{content_type} {count}个，'
        content_type_text = content_type_text.rstrip('，')
        
        # 标签分布文本
        top_tags = sorted(analysis['tag_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]
        top_tags_text = ', '.join([tag for tag, _ in top_tags])
        
        # 生成摘要
        summary = f'关于{topic}，您共完成了{analysis["completed_records"]}个学习内容，总学习时长为{analysis["total_duration"]}分钟，平均得分为{analysis["average_score"]:.1f}分。\n\n'
        summary += f'学习内容包括：{content_type_text}。\n\n'
        summary += f'相关主题包括：{top_tags_text}。\n\n'
        summary += f'您在{topic}方面的学习表现良好，继续保持！'
        
        return summary
    
    def _extract_key_points(self, learning_records: List[Dict[str, Any]]) -> List[str]:
        """提取关键知识点
        
        Args:
            learning_records: 学习记录列表
            
        Returns:
            关键知识点列表
        """
        if not learning_records:
            return []
        
        # 提取所有标签
        all_tags = []
        for record in learning_records:
            all_tags.extend(record.get('tags', []))
        
        # 统计标签频率
        tag_counter = Counter(all_tags)
        
        # 提取频率最高的标签作为关键知识点
        top_tags = [tag for tag, _ in tag_counter.most_common(10)]
        
        return top_tags
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成学习建议
        
        Args:
            analysis: 学习记录分析结果
            
        Returns:
            学习建议列表
        """
        recommendations = []
        
        # 基于学习时长的建议
        if analysis['total_duration'] < 60:
            recommendations.append({
                'title': '增加学习时间',
                'description': '建议每天至少学习30分钟，保持学习的连续性',
                'priority': 'medium'
            })
        
        # 基于内容类型的建议
        content_types = set(analysis['content_type_distribution'].keys())
        if 'video' not in content_types:
            recommendations.append({
                'title': '增加视频学习',
                'description': '视频学习可以帮助您更好地理解复杂概念',
                'priority': 'low'
            })
        if 'exercise' not in content_types:
            recommendations.append({
                'title': '增加练习',
                'description': '通过练习巩固所学知识，提高应用能力',
                'priority': 'medium'
            })
        if 'article' not in content_types:
            recommendations.append({
                'title': '增加阅读',
                'description': '阅读相关文章可以拓宽您的知识面',
                'priority': 'low'
            })
        
        # 基于得分的建议
        if analysis['average_score'] < 70:
            recommendations.append({
                'title': '加强基础知识',
                'description': '建议复习基础知识，确保掌握核心概念',
                'priority': 'high'
            })
        elif analysis['average_score'] < 85:
            recommendations.append({
                'title': '提高学习深度',
                'description': '建议深入学习重点内容，提高学习质量',
                'priority': 'medium'
            })
        else:
            recommendations.append({
                'title': '挑战更高难度',
                'description': '您的学习表现优秀，可以尝试更具挑战性的内容',
                'priority': 'low'
            })
        
        # 通用建议
        recommendations.append({
            'title': '定期复习',
            'description': '定期复习所学内容，巩固记忆',
            'priority': 'medium'
        })
        
        recommendations.append({
            'title': '学习笔记',
            'description': '养成做学习笔记的习惯，帮助整理思路',
            'priority': 'low'
        })
        
        return recommendations
    
    def _calculate_statistics(self, learning_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算学习统计数据
        
        Args:
            learning_records: 学习记录列表
            
        Returns:
            学习统计数据
        """
        if not learning_records:
            return {
                'total_records': 0,
                'total_duration': 0,
                'average_duration': 0,
                'average_score': 0,
                'completion_rate': 0,
                'content_type_stats': {},
                'daily_average_duration': 0
            }
        
        # 总记录数
        total_records = len(learning_records)
        
        # 总学习时长
        total_duration = sum(record.get('duration', 0) for record in learning_records)
        
        # 平均学习时长
        average_duration = total_duration / total_records if total_records > 0 else 0
        
        # 平均得分
        scores = [record.get('score', 0) for record in learning_records if record.get('score')]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # 完成率
        completed_records = sum(1 for record in learning_records if record.get('completed', False))
        completion_rate = (completed_records / total_records) * 100 if total_records > 0 else 0
        
        # 内容类型统计
        content_type_stats = {}
        for content_type, count in Counter(record.get('content_type', 'unknown') for record in learning_records).items():
            type_records = [r for r in learning_records if r.get('content_type') == content_type]
            type_duration = sum(r.get('duration', 0) for r in type_records)
            type_scores = [r.get('score', 0) for r in type_records if r.get('score')]
            type_average_score = sum(type_scores) / len(type_scores) if type_scores else 0
            
            content_type_stats[content_type] = {
                'count': count,
                'duration': type_duration,
                'average_score': type_average_score
            }
        
        # 每日平均学习时长
        unique_days = len(set(datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d') for record in learning_records))
        daily_average_duration = total_duration / unique_days if unique_days > 0 else 0
        
        return {
            'total_records': total_records,
            'total_duration': total_duration,
            'average_duration': average_duration,
            'average_score': average_score,
            'completion_rate': completion_rate,
            'content_type_stats': content_type_stats,
            'daily_average_duration': daily_average_duration
        }
    
    def _get_time_range_text(self, time_range: str) -> str:
        """获取时间范围文本
        
        Args:
            time_range: 时间范围
            
        Returns:
            时间范围文本
        """
        time_range_map = {
            'day': '一天',
            'week': '一周',
            'month': '一个月',
            'year': '一年'
        }
        return time_range_map.get(time_range, '一周')


# 全局学习摘要生成引擎实例
learning_summary_engine = LearningSummaryEngine()