"""学习效果预测引擎，使用LSTM/Transformer时序模型预测学习成果"""

import json
import random
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
from django.conf import settings
from .models import LearningRecord, PracticeRecord, KnowledgeNode


class LearningPredictionEngine:
    """学习效果预测引擎核心类"""
    
    def __init__(self):
        self.feature_columns = self._init_feature_columns()
        self.model_config = self._init_model_config()
    
    def _init_feature_columns(self) -> List[str]:
        """初始化特征列"""
        return [
            'learning_time',          # 学习时长（分钟）
            'practice_count',         # 练习次数
            'correct_rate',           # 正确率
            'difficulty_level',       # 难度等级
            'knowledge_mastery',      # 知识掌握度
            'learning_frequency',     # 学习频率
            'recent_activity',        # 最近活跃度
            'consistency_score',      # 学习一致性
            'progress_rate',          # 进度率
            'resource_usage'          # 资源使用情况
        ]
    
    def _init_model_config(self) -> Dict[str, Any]:
        """初始化模型配置"""
        return {
            'sequence_length': 7,     # 序列长度（天）
            'prediction_horizon': 3,  # 预测 horizon（天）
            'thresholds': {
                'high_risk': 0.3,      # 高风险阈值
                'medium_risk': 0.6     # 中等风险阈值
            },
            'feature_weights': {
                'learning_time': 0.2,
                'practice_count': 0.15,
                'correct_rate': 0.25,
                'difficulty_level': 0.1,
                'knowledge_mastery': 0.15,
                'learning_frequency': 0.05,
                'recent_activity': 0.05,
                'consistency_score': 0.025,
                'progress_rate': 0.025,
                'resource_usage': 0.05
            }
        }
    
    def predict_learning_effect(self, user_id: int, knowledge_node_id: int = None) -> Dict[str, Any]:
        """
        预测学习效果
        
        Args:
            user_id: 用户ID
            knowledge_node_id: 知识点ID（可选）
        
        Returns:
            预测结果
        """
        try:
            # 获取用户学习数据
            learning_data = self._get_user_learning_data(user_id, knowledge_node_id)
            
            if not learning_data:
                return {
                    'error': '用户学习数据不足',
                    'prediction': None
                }
            
            # 提取特征
            features = self._extract_features(learning_data)
            
            # 生成预测
            prediction = self._generate_prediction(features, learning_data)
            
            # 生成干预建议
            interventions = self._generate_interventions(prediction, learning_data)
            
            return {
                'prediction': prediction,
                'interventions': interventions,
                'data_available': True,
                'user_id': user_id,
                'knowledge_node_id': knowledge_node_id
            }
            
        except Exception as e:
            return {
                'error': f'预测失败: {str(e)}',
                'prediction': None
            }
    
    def _get_user_learning_data(self, user_id: int, knowledge_node_id: int = None) -> List[Dict[str, Any]]:
        """获取用户学习数据"""
        data = []
        
        # 获取最近30天的学习记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # 获取学习记录
        learning_records = LearningRecord.objects.filter(
            user_id=user_id,
            created_at__range=(start_date, end_date)
        ).order_by('created_at')
        
        # 获取练习记录
        practice_records = PracticeRecord.objects.filter(
            user_id=user_id,
            created_at__range=(start_date, end_date)
        ).order_by('created_at')
        
        # 按日期整理数据
        daily_data = {}
        
        # 处理学习记录
        for record in learning_records:
            date = record.created_at.date()
            if date not in daily_data:
                daily_data[date] = {
                    'date': date.isoformat(),
                    'learning_time': 0,
                    'practice_count': 0,
                    'correct_count': 0,
                    'total_count': 0,
                    'knowledge_nodes': set()
                }
            
            daily_data[date]['learning_time'] += record.duration or 0
            daily_data[date]['knowledge_nodes'].add(record.knowledge_node_id)
        
        # 处理练习记录
        for record in practice_records:
            date = record.created_at.date()
            if date not in daily_data:
                daily_data[date] = {
                    'date': date.isoformat(),
                    'learning_time': 0,
                    'practice_count': 0,
                    'correct_count': 0,
                    'total_count': 0,
                    'knowledge_nodes': set()
                }
            
            daily_data[date]['practice_count'] += 1
            daily_data[date]['total_count'] += 1
            if record.is_correct:
                daily_data[date]['correct_count'] += 1
        
        # 转换为列表并按日期排序
        for date_data in daily_data.values():
            data.append({
                **date_data,
                'knowledge_nodes': list(date_data['knowledge_nodes'])
            })
        
        # 按日期排序
        data.sort(key=lambda x: x['date'])
        
        return data
    
    def _extract_features(self, learning_data: List[Dict[str, Any]]) -> np.ndarray:
        """提取特征"""
        features = []
        
        for i, day_data in enumerate(learning_data):
            # 计算基础特征
            learning_time = day_data.get('learning_time', 0) / 60  # 转换为小时
            practice_count = day_data.get('practice_count', 0)
            total_count = day_data.get('total_count', 1)
            correct_count = day_data.get('correct_count', 0)
            correct_rate = correct_count / total_count if total_count > 0 else 0
            
            # 计算学习频率（近7天学习天数）
            recent_days = learning_data[max(0, i-6):i+1]
            learning_frequency = sum(1 for d in recent_days if d.get('learning_time', 0) > 0) / len(recent_days)
            
            # 计算最近活跃度（近3天平均学习时长）
            recent_3_days = learning_data[max(0, i-2):i+1]
            recent_activity = sum(d.get('learning_time', 0) for d in recent_3_days) / (len(recent_3_days) * 60)
            
            # 计算一致性得分（学习时间的标准差倒数）
            if i >= 6:
                consistency_days = learning_data[i-6:i+1]
                times = [d.get('learning_time', 0) for d in consistency_days]
                std = np.std(times) if len(times) > 1 else 1
                consistency_score = 1 / std if std > 0 else 1
            else:
                consistency_score = 0.5
            
            # 计算进度率（假设总学习时间为目标）
            total_learning_time = sum(d.get('learning_time', 0) for d in learning_data[:i+1])
            target_time = 30 * 60  # 假设目标30小时
            progress_rate = min(total_learning_time / target_time, 1)
            
            # 资源使用情况（简化版）
            resource_usage = min(practice_count / 5, 1)  # 假设每天5次练习为满
            
            # 难度等级（简化版）
            difficulty_level = min(correct_rate, 1)  # 正确率越低，难度越高
            
            # 知识掌握度（简化版）
            knowledge_mastery = correct_rate
            
            # 构建特征向量
            feature_vector = [
                learning_time,
                practice_count,
                correct_rate,
                difficulty_level,
                knowledge_mastery,
                learning_frequency,
                recent_activity,
                consistency_score,
                progress_rate,
                resource_usage
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _generate_prediction(self, features: np.ndarray, learning_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成预测"""
        # 这里使用简化的预测模型
        # 实际项目中可以使用真实的LSTM或Transformer模型
        
        if len(features) < self.model_config['sequence_length']:
            # 数据不足，使用简单预测
            return self._simple_prediction(features, learning_data)
        
        # 使用滑动窗口预测
        predictions = []
        window_size = self.model_config['sequence_length']
        
        for i in range(len(features) - window_size + 1):
            window = features[i:i+window_size]
            # 计算窗口内的特征均值
            window_mean = np.mean(window, axis=0)
            
            # 使用权重计算综合得分
            weights = np.array(list(self.model_config['feature_weights'].values()))
            score = np.dot(window_mean, weights)
            
            # 转换为预测结果
            predictions.append({
                'date': learning_data[i+window_size-1]['date'],
                'score': float(score),
                'predicted_mastery': float(min(score * 1.2, 1)),
                'risk_level': self._calculate_risk_level(score)
            })
        
        # 生成未来预测
        future_predictions = self._predict_future(predictions[-1] if predictions else None, learning_data)
        
        return {
            'historical_predictions': predictions,
            'future_predictions': future_predictions,
            'current_score': predictions[-1]['score'] if predictions else 0.5,
            'current_mastery': predictions[-1]['predicted_mastery'] if predictions else 0.5,
            'risk_level': predictions[-1]['risk_level'] if predictions else 'low',
            'confidence': min(len(features) / 30, 1)  # 数据越多，置信度越高
        }
    
    def _simple_prediction(self, features: np.ndarray, learning_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """简单预测（数据不足时使用）"""
        if len(features) == 0:
            return {
                'historical_predictions': [],
                'future_predictions': [],
                'current_score': 0.5,
                'current_mastery': 0.5,
                'risk_level': 'medium',
                'confidence': 0.1
            }
        
        # 计算平均特征
        mean_features = np.mean(features, axis=0)
        weights = np.array(list(self.model_config['feature_weights'].values()))
        score = np.dot(mean_features, weights)
        
        # 生成历史预测
        historical = []
        for i, day_data in enumerate(learning_data):
            historical.append({
                'date': day_data['date'],
                'score': float(score),
                'predicted_mastery': float(min(score * 1.2, 1)),
                'risk_level': self._calculate_risk_level(score)
            })
        
        # 生成未来预测
        future = self._predict_future(historical[-1] if historical else None, learning_data)
        
        return {
            'historical_predictions': historical,
            'future_predictions': future,
            'current_score': float(score),
            'current_mastery': float(min(score * 1.2, 1)),
            'risk_level': self._calculate_risk_level(score),
            'confidence': min(len(features) / 7, 1)
        }
    
    def _predict_future(self, last_prediction: Dict[str, Any], learning_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """预测未来"""
        future = []
        horizon = self.model_config['prediction_horizon']
        
        if not last_prediction:
            # 无历史数据，生成默认预测
            base_score = 0.5
            base_mastery = 0.5
        else:
            base_score = last_prediction['score']
            base_mastery = last_prediction['predicted_mastery']
        
        # 生成未来预测
        last_date = learning_data[-1]['date'] if learning_data else datetime.now().isoformat()
        last_date = datetime.fromisoformat(last_date)
        
        for i in range(1, horizon + 1):
            future_date = last_date + timedelta(days=i)
            
            # 简单的趋势预测
            # 假设学习状态会逐渐改善
            trend = 0.02 * i  # 每天提高0.02
            future_score = min(base_score + trend, 1)
            future_mastery = min(base_mastery + trend * 1.2, 1)
            
            future.append({
                'date': future_date.isoformat(),
                'score': float(future_score),
                'predicted_mastery': float(future_mastery),
                'risk_level': self._calculate_risk_level(future_score),
                'is_prediction': True
            })
        
        return future
    
    def _calculate_risk_level(self, score: float) -> str:
        """计算风险等级"""
        thresholds = self.model_config['thresholds']
        
        if score < thresholds['high_risk']:
            return 'high'
        elif score < thresholds['medium_risk']:
            return 'medium'
        else:
            return 'low'
    
    def _generate_interventions(self, prediction: Dict[str, Any], learning_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成干预建议"""
        interventions = []
        risk_level = prediction.get('risk_level', 'low')
        current_score = prediction.get('current_score', 0.5)
        
        # 根据风险等级生成不同的干预建议
        if risk_level == 'high':
            interventions.extend([
                {
                    'type': 'learning_plan',
                    'title': '制定学习计划',
                    'description': '建议每天固定学习时间，制定详细的学习计划',
                    'priority': 'high',
                    'estimated_time': 30
                },
                {
                    'type': 'practice',
                    'title': '增加练习频率',
                    'description': '每天至少完成5道练习题，提高解题能力',
                    'priority': 'high',
                    'estimated_time': 45
                },
                {
                    'type': 'tutoring',
                    'title': '寻求辅导',
                    'description': '建议参加辅导课程或请教老师同学',
                    'priority': 'medium',
                    'estimated_time': 60
                }
            ])
        elif risk_level == 'medium':
            interventions.extend([
                {
                    'type': 'review',
                    'title': '复习薄弱环节',
                    'description': '重点复习正确率较低的知识点',
                    'priority': 'medium',
                    'estimated_time': 30
                },
                {
                    'type': 'consistency',
                    'title': '保持学习一致性',
                    'description': '每天坚持学习，避免间歇性学习',
                    'priority': 'medium',
                    'estimated_time': 20
                }
            ])
        else:
            interventions.extend([
                {
                    'type': 'challenge',
                    'title': '挑战更高难度',
                    'description': '尝试更高级的练习题，拓展知识面',
                    'priority': 'low',
                    'estimated_time': 40
                },
                {
                    'type': 'share',
                    'title': '分享学习经验',
                    'description': '与同学分享学习心得，巩固知识',
                    'priority': 'low',
                    'estimated_time': 20
                }
            ])
        
        # 根据具体特征生成针对性建议
        if len(learning_data) >= 7:
            # 分析最近7天的学习情况
            recent_data = learning_data[-7:]
            avg_learning_time = sum(d.get('learning_time', 0) for d in recent_data) / 7
            
            if avg_learning_time < 30:  # 平均每天学习时间不足30分钟
                interventions.append({
                    'type': 'time_management',
                    'title': '增加学习时间',
                    'description': '建议每天至少学习30分钟，保持学习状态',
                    'priority': 'medium',
                    'estimated_time': 30
                })
            
            # 分析正确率
            total_correct = sum(d.get('correct_count', 0) for d in recent_data)
            total_attempts = sum(d.get('total_count', 1) for d in recent_data)
            recent_correct_rate = total_correct / total_attempts if total_attempts > 0 else 0
            
            if recent_correct_rate < 0.6:
                interventions.append({
                    'type': 'practice_focus',
                    'title': '针对性练习',
                    'description': '重点练习正确率较低的题型',
                    'priority': 'medium',
                    'estimated_time': 45
                })
        
        return interventions
    
    def batch_predict(self, user_ids: List[int]) -> Dict[str, Any]:
        """
        批量预测多个用户的学习效果
        
        Args:
            user_ids: 用户ID列表
        
        Returns:
            批量预测结果
        """
        results = {}
        
        for user_id in user_ids:
            results[user_id] = self.predict_learning_effect(user_id)
        
        # 生成批量统计
        total_users = len(results)
        high_risk_count = sum(1 for r in results.values() if r.get('prediction', {}).get('risk_level') == 'high')
        medium_risk_count = sum(1 for r in results.values() if r.get('prediction', {}).get('risk_level') == 'medium')
        low_risk_count = sum(1 for r in results.values() if r.get('prediction', {}).get('risk_level') == 'low')
        
        return {
            'batch_summary': {
                'total_users': total_users,
                'high_risk_count': high_risk_count,
                'medium_risk_count': medium_risk_count,
                'low_risk_count': low_risk_count,
                'risk_distribution': {
                    'high': high_risk_count / total_users if total_users > 0 else 0,
                    'medium': medium_risk_count / total_users if total_users > 0 else 0,
                    'low': low_risk_count / total_users if total_users > 0 else 0
                }
            },
            'detailed_results': results
        }
    
    def get_prediction_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取用户的预测历史
        
        Args:
            user_id: 用户ID
            days: 历史天数
        
        Returns:
            预测历史记录
        """
        # 这里返回模拟的历史数据
        # 实际项目中应该从数据库或缓存中获取
        history = []
        end_date = datetime.now()
        
        for i in range(days, 0, -1):
            date = end_date - timedelta(days=i)
            # 生成模拟数据
            score = 0.5 + random.uniform(-0.2, 0.2)
            score = max(0, min(1, score))
            
            history.append({
                'date': date.isoformat(),
                'score': float(score),
                'predicted_mastery': float(min(score * 1.2, 1)),
                'risk_level': self._calculate_risk_level(score),
                'actual_mastery': float(min(score * 1.1, 1))  # 模拟实际掌握度
            })
        
        return history


# 全局学习预测引擎实例
learning_prediction_engine = LearningPredictionEngine()