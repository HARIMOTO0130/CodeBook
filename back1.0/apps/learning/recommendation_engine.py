"""智能自适应学习路径推荐引擎"""
import math
import random
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Sum
from .models import (
    LearningStyle, KnowledgeMastery, LearningRecommendation, LearningPreference,
    LearningRecord, PracticeRecord, UserLearningPath, RoadmapTemplate, RoadmapStage,
    RoadmapBook, UserPathStage, Exercise, ExerciseRecord
)


class RecommendationEngine:
    """智能推荐引擎核心类"""
    
    def __init__(self, user):
        self.user = user
        # 初始化用户画像相关数据
        self._init_user_profile()
    
    def _init_user_profile(self):
        """初始化用户画像数据"""
        # 获取或创建用户学习风格
        try:
            self.learning_style = self.user.learning_style
        except LearningStyle.DoesNotExist:
            self.learning_style = LearningStyle.objects.create(user=self.user)
        
        # 获取或创建用户学习偏好
        try:
            self.learning_preference = self.user.learning_preference
        except LearningPreference.DoesNotExist:
            self.learning_preference = LearningPreference.objects.create(user=self.user)
        
        # 获取用户知识掌握度
        self.knowledge_mastery = KnowledgeMastery.objects.filter(user=self.user)
        
        # 获取用户学习记录
        self.learning_records = LearningRecord.objects.filter(user=self.user)
        
        # 获取用户练习记录
        self.practice_records = PracticeRecord.objects.filter(user=self.user)
        
        # 获取用户学习路径
        self.user_paths = UserLearningPath.objects.filter(user=self.user)
    
    def build_user_profile(self):
        """构建和更新用户画像"""
        try:
            # 基于学习行为分析学习风格
            self._analyze_learning_style()
            
            # 更新知识掌握度
            self._update_knowledge_mastery()
            
            # 计算总学习时间
            total_learning_time = self._calculate_total_learning_time()
            
            # 获取已完成章节数
            completed_chapters = self._get_completed_chapters_count()
            
            # 获取学习频率
            learning_frequency = self._calculate_learning_frequency()
            
            # 获取平均练习成绩
            avg_score = self._calculate_average_score()
            
            # 确定知识水平
            knowledge_level = self._determine_knowledge_level()
            
            # 确定主要兴趣领域
            interest_areas = self._determine_interest_areas()
            
            # 更新用户学习偏好
            self._update_learning_preferences(total_learning_time, completed_chapters, avg_score, interest_areas)
            
            # 将LearningStyle对象转换为字典
            learning_style_dict = {
                'visual_score': self.learning_style.visual_score,
                'auditory_score': self.learning_style.auditory_score,
                'reading_score': self.learning_style.reading_score,
                'kinesthetic_score': self.learning_style.kinesthetic_score,
                'dominant_style': self._get_dominant_style()
            }
            
            return {
                'learning_style': learning_style_dict,
                'learning_preference': self.learning_preference,
                'knowledge_mastery': self.knowledge_mastery,
                'total_learning_time': total_learning_time,
                'completed_chapters': completed_chapters,
                'learning_frequency': learning_frequency,
                'average_score': avg_score,
                'knowledge_level': knowledge_level,
                'interest_areas': interest_areas,
                'dominant_style': self._get_dominant_style()
            }
        except Exception as e:
            print(f"构建用户画像失败: {e}")
            # 返回基础用户画像
            # 使用字典而不是LearningStyle对象
            return {
                'learning_style': {
                    'visual_score': 0.5,
                    'auditory_score': 0.5,
                    'reading_score': 0.5,
                    'kinesthetic_score': 0.5,
                    'dominant_style': '综合型'
                },
                'learning_preference': self.learning_preference,
                'knowledge_mastery': self.knowledge_mastery,
                'total_learning_time': 0,
                'completed_chapters': 0,
                'learning_frequency': 0,
                'average_score': 0,
                'knowledge_level': '初级',
                'interest_areas': [],
                'dominant_style': '综合型'
            }
    
    def _calculate_learning_frequency(self):
        """计算学习频率（最近30天内的学习天数）"""
        from .models import HeatmapData
        from datetime import datetime, timedelta
        
        # 获取最近30天的学习数据
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_data = HeatmapData.objects.filter(
            user=self.user,
            date__gte=thirty_days_ago,
            minutes__gt=0
        )
        
        return recent_data.count()
    
    def _calculate_average_score(self):
        """计算平均练习成绩"""
        if self.practice_records.exists():
            return self.practice_records.filter(completed=True).aggregate(Avg('score'))['score__avg'] or 0
        return 0
    
    def _determine_knowledge_level(self):
        """确定知识水平"""
        # 基于已完成章节数和平均成绩确定知识水平
        completed_chapters = self._get_completed_chapters_count()
        avg_score = self._calculate_average_score()
        
        if completed_chapters >= 50 and avg_score >= 80:
            return '高级'
        elif completed_chapters >= 20 and avg_score >= 60:
            return '中级'
        else:
            return '初级'
    
    def _determine_interest_areas(self):
        """确定主要兴趣领域"""
        # 基于学习记录和练习记录确定兴趣领域
        from collections import Counter
        
        interests = []
        
        # 从学习记录中提取兴趣
        for record in self.learning_records:
            # 从书籍和章节标题中提取关键词
            book_title = record.book.title.lower()
            chapter_title = record.chapter.title.lower()
            
            # 简单的兴趣关键词提取
            for keyword in ['python', '数据分析', '编程', 'web', '前端', '后端', 'java', '机器学习', 'ai']:
                if keyword in book_title or keyword in chapter_title:
                    interests.append(keyword)
        
        # 从练习记录中提取兴趣
        for record in self.practice_records:
            book_title = record.book.title.lower() if record.book else ''
            chapter_title = record.chapter.title.lower() if record.chapter else ''
            
            for keyword in ['python', '数据分析', '编程', 'web', '前端', '后端', 'java', '机器学习', 'ai']:
                if keyword in book_title or keyword in chapter_title:
                    interests.append(keyword)
        
        # 统计兴趣关键词
        interest_counts = Counter(interests)
        
        # 返回前3个主要兴趣领域
        return [interest for interest, count in interest_counts.most_common(3)]
    
    def _get_dominant_style(self):
        """获取主导学习风格"""
        visual_score = self.learning_style.visual_score
        auditory_score = self.learning_style.auditory_score
        reading_score = self.learning_style.reading_score
        kinesthetic_score = self.learning_style.kinesthetic_score
        
        # 确定主导学习风格
        scores = {
            '视觉型': visual_score,
            '听觉型': auditory_score,
            '读写型': reading_score,
            '动觉型': kinesthetic_score
        }
        
        dominant_style = max(scores, key=scores.get)
        
        # 如果各风格分数差异不大，返回综合型
        if max(scores.values()) - min(scores.values()) < 0.2:
            dominant_style = '综合型'
        
        return dominant_style
    
    def _update_learning_preferences(self, total_learning_time, completed_chapters, avg_score, interest_areas):
        """更新学习偏好"""
        # 如果兴趣领域不为空，更新用户学习偏好
        if interest_areas and not self.learning_preference.interest_areas:
            self.learning_preference.interest_areas = interest_areas
            self.learning_preference.save()
        
        # 根据平均成绩调整难度偏好
        if avg_score >= 85:
            self.learning_preference.difficulty_preference = 'challenging'
            self.learning_preference.save()
        elif avg_score < 60:
            self.learning_preference.difficulty_preference = 'easy'
            self.learning_preference.save()
    
    def _analyze_learning_style(self):
        """分析用户学习风格"""
        # 基于学习记录和练习记录分析学习风格
        visual_score = 0.5
        auditory_score = 0.5
        reading_score = 0.5
        kinesthetic_score = 0.5
        
        # 示例：基于完成练习的方式分析
        if self.practice_records.exists():
            code_submission_count = self.practice_records.filter(user_code__isnull=False).count()
            total_practices = self.practice_records.count()
            
            if total_practices > 0:
                # 提交代码越多，动手实践倾向越高
                kinesthetic_score = min(1.0, code_submission_count / total_practices)
                
        # 更新学习风格
        self.learning_style.visual_score = visual_score
        self.learning_style.auditory_score = auditory_score
        self.learning_style.reading_score = reading_score
        self.learning_style.kinesthetic_score = kinesthetic_score
        self.learning_style.save()
    
    def _update_knowledge_mastery(self):
        """更新用户知识掌握度"""
        # 基于练习成绩计算知识掌握度
        for practice in self.practice_records.filter(completed=True):
            # 简单示例：使用练习分数作为掌握度
            mastery_level = practice.score / 100.0
            
            # 创建或更新知识点掌握度
            knowledge_point = f"{practice.book.title}-{practice.chapter.title}"
            mastery, created = KnowledgeMastery.objects.get_or_create(
                user=self.user,
                book=practice.book,
                chapter=practice.chapter,
                knowledge_point=knowledge_point,
                defaults={
                    'mastery_level': mastery_level,
                    'assessment_count': 1,
                    'tags': []
                }
            )
            
            if not created:
                # 加权平均更新掌握度
                new_assessment_count = mastery.assessment_count + 1
                mastery.mastery_level = ((mastery.mastery_level * mastery.assessment_count) + mastery_level) / new_assessment_count
                mastery.assessment_count = new_assessment_count
                mastery.save()
    
    def _calculate_total_learning_time(self):
        """计算总学习时间"""
        from .models import HeatmapData
        total_minutes = HeatmapData.objects.filter(user=self.user).aggregate(Sum('minutes'))['minutes__sum'] or 0
        return total_minutes
    
    def _get_completed_chapters_count(self):
        """获取已完成章节数"""
        return self.learning_records.filter(progress=100).count()
    
    def recommend_roadmaps(self, limit=5):
        """推荐初始学习路线图"""
        # 1. 获取所有激活的路线图
        roadmaps = RoadmapTemplate.objects.filter(is_active=True)
        
        # 如果没有路线图，返回模拟推荐
        if not roadmaps.exists():
            return []
        
        # 2. 基于用户画像计算匹配度
        roadmap_scores = []
        for roadmap in roadmaps:
            score = self._calculate_roadmap_match_score(roadmap)
            roadmap_scores.append((roadmap, score))
        
        # 3. 按匹配度排序
        roadmap_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 4. 获取推荐结果
        recommendations = []
        for roadmap, score in roadmap_scores[:limit]:
            # 计算推荐原因
            reason = self._generate_recommendation_reason(roadmap)
            
            # 创建推荐记录
            try:
                recommendation = LearningRecommendation.objects.create(
                    user=self.user,
                    recommendation_type='roadmap',
                    roadmap=roadmap,
                    score=score,
                    reason=reason
                )
                recommendations.append(recommendation)
            except Exception as e:
                # 如果创建推荐记录失败，仍然添加推荐
                class MockRecommendation:
                    def __init__(self, roadmap, score, reason):
                        self.roadmap = roadmap
                        self.score = score
                        self.reason = reason
                recommendations.append(MockRecommendation(roadmap, score, reason))
        
        return recommendations
    
    def _calculate_roadmap_match_score(self, roadmap):
        """计算路线图与用户的匹配度分数"""
        score = 0.0
        
        # 基础分数
        base_score = 0.5
        
        # 根据学习偏好调整
        if self.learning_preference.difficulty_preference == 'easy' and roadmap.difficulty_level == 'beginner':
            score += 0.2
        elif self.learning_preference.difficulty_preference == 'medium' and roadmap.difficulty_level == 'intermediate':
            score += 0.2
        elif self.learning_preference.difficulty_preference == 'challenging' and roadmap.difficulty_level == 'advanced':
            score += 0.2
        
        # 根据学习目标和路线图标签匹配
        for goal in self.learning_preference.learning_goals:
            for tag in roadmap.tags:
                if goal.lower() in tag.lower():
                    score += 0.1
        
        # 根据兴趣领域匹配
        for interest in self.learning_preference.interest_areas:
            if interest.lower() in roadmap.title.lower() or interest.lower() in roadmap.description.lower():
                score += 0.15
        
        # 根据用户已有知识调整难度匹配
        if self._should_adjust_difficulty_based_on_knowledge(roadmap):
            score += 0.1
        
        # 确保分数在0-1范围内
        return min(1.0, max(0.0, base_score + score))
    
    def _should_adjust_difficulty_based_on_knowledge(self, roadmap):
        """根据用户知识水平调整难度匹配"""
        # 简单实现：基于已完成章节数量判断
        completed_chapters = self._get_completed_chapters_count()
        
        if roadmap.difficulty_level == 'beginner' and completed_chapters < 10:
            return True
        elif roadmap.difficulty_level == 'intermediate' and 10 <= completed_chapters < 50:
            return True
        elif roadmap.difficulty_level == 'advanced' and completed_chapters >= 50:
            return True
        
        return False
    
    def _generate_recommendation_reason(self, roadmap):
        """生成路线图推荐原因"""
        reasons = []
        
        # 基于难度的原因
        if roadmap.difficulty_level == 'beginner':
            reasons.append("适合初学者的学习路径")
        elif roadmap.difficulty_level == 'intermediate':
            reasons.append("符合您当前学习水平的进阶内容")
        elif roadmap.difficulty_level == 'advanced':
            reasons.append("挑战您的高级学习内容")
        
        # 基于学习目标的原因
        for goal in self.learning_preference.learning_goals:
            for tag in roadmap.tags:
                if goal.lower() in tag.lower():
                    reasons.append(f"与您的学习目标 '{goal}' 相关")
                    break
        
        # 基于兴趣的原因
        for interest in self.learning_preference.interest_areas:
            if interest.lower() in roadmap.title.lower():
                reasons.append(f"基于您对 '{interest}' 的兴趣推荐")
                break
        
        # 添加时间预估
        reasons.append(f"预计学习时间：{roadmap.estimated_hours} 小时")
        
        return '; '.join(reasons)
    
    def recommend_next_content(self, user_path=None):
        """推荐下一步学习内容"""
        # 如果没有指定学习路径，使用活跃的路径
        if not user_path:
            try:
                user_path = UserLearningPath.objects.filter(user=self.user, is_active=True).latest('started_at')
            except UserLearningPath.DoesNotExist:
                return []
        
        recommendations = []
        
        # 获取当前阶段
        current_stage = user_path.current_stage
        if not current_stage:
            # 如果没有当前阶段，推荐第一个阶段
            try:
                current_stage = RoadmapStage.objects.filter(roadmap=user_path.roadmap).order_by('stage_order').first()
            except RoadmapStage.DoesNotExist:
                return []
        
        # 推荐当前阶段的书籍
        stage_books = RoadmapBook.objects.filter(stage=current_stage).order_by('recommended_order')
        
        for roadmap_book in stage_books:
            # 检查用户是否已学习过这本书的大部分内容
            book_chapters_count = roadmap_book.book.chapters.count()
            completed_chapters = LearningRecord.objects.filter(
                user=self.user,
                book=roadmap_book.book,
                progress=100
            ).count()
            
            # 如果完成率低于50%，推荐这本书
            if completed_chapters < book_chapters_count * 0.5:
                score = self._calculate_content_match_score(roadmap_book.book, current_stage)
                
                # 创建推荐记录
                recommendation = LearningRecommendation.objects.create(
                    user=self.user,
                    user_path=user_path,
                    recommendation_type='book',
                    book=roadmap_book.book,
                    score=score,
                    reason=f"当前阶段 '{current_stage.title}' 的推荐书籍，重要程度：{roadmap_book.get_importance_display()}"
                )
                recommendations.append(recommendation)
        
        # 推荐相关练习题
        exercises = self._recommend_exercises(current_stage)
        recommendations.extend(exercises)
        
        # 按分数排序
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    def _calculate_content_match_score(self, content, stage):
        """计算学习内容与用户的匹配度"""
        base_score = 0.6
        
        # 基于重要程度加分
        if hasattr(content, 'roadmap_books'):
            roadmap_book = content.roadmap_books.filter(stage=stage).first()
            if roadmap_book:
                base_score += (roadmap_book.importance - 1) * 0.1  # 重要程度1-4，转换为0-0.3的加分
        
        # 基于学习风格调整
        # 这里可以根据内容类型和用户学习风格进一步调整分数
        
        return min(1.0, base_score)
    
    def _recommend_exercises(self, stage):
        """推荐与当前阶段相关的练习题"""
        recommendations = []
        
        # 获取当前阶段的学习目标关键词
        learning_goal_keywords = []
        for goal in stage.learning_goals:
            # 简单分词，实际应用中可以使用更复杂的NLP方法
            keywords = goal.lower().split()
            learning_goal_keywords.extend(keywords)
        
        # 查找相关练习题
        relevant_exercises = Exercise.objects.filter(
            difficulty__in=self._get_preferred_difficulty_range()
        )
        
        for exercise in relevant_exercises:
            # 计算练习题与学习目标的相关性
            relevance_score = 0.0
            exercise_text = f"{exercise.title} {exercise.description} {exercise.question}".lower()
            
            for keyword in learning_goal_keywords:
                if keyword in exercise_text:
                    relevance_score += 0.1
            
            # 检查用户是否已经通过了这个练习
            is_already_passed = ExerciseRecord.objects.filter(
                user=self.user,
                exercise=exercise,
                passed=True
            ).exists()
            
            if relevance_score > 0 and not is_already_passed:
                # 创建推荐记录
                recommendation = LearningRecommendation.objects.create(
                    user=self.user,
                    recommendation_type='exercise',
                    exercise=exercise,
                    score=min(1.0, 0.5 + relevance_score),
                    reason=f"与当前阶段学习目标相关的练习题，难度：{exercise.get_difficulty_display()}"
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _get_preferred_difficulty_range(self):
        """获取用户偏好的难度范围"""
        if self.learning_preference.difficulty_preference == 'easy':
            return [1, 2]  # 简单、中等偏简单
        elif self.learning_preference.difficulty_preference == 'medium':
            return [2, 3]  # 中等、中等偏难
        elif self.learning_preference.difficulty_preference == 'challenging':
            return [3]  # 困难
        else:  # mixed
            return [1, 2, 3]  # 全部难度
    
    def optimize_learning_strategy(self, user_path):
        """优化学习策略"""
        # 根据学习风格生成学习建议
        suggestions = []
        
        # 基于视觉学习偏好
        if self.learning_style.visual_score > 0.7:
            suggestions.append("建议使用图表、思维导图等视觉辅助工具来理解和记忆知识点")
        
        # 基于听觉学习偏好
        if self.learning_style.auditory_score > 0.7:
            suggestions.append("建议朗读学习内容或寻找相关音频资源")
        
        # 基于读写学习偏好
        if self.learning_style.reading_score > 0.7:
            suggestions.append("建议多做笔记，通过写来加强记忆")
        
        # 基于动手实践偏好
        if self.learning_style.kinesthetic_score > 0.7:
            suggestions.append("建议多做练习题，通过实际操作来巩固知识")
        
        # 基于学习节奏偏好
        if self.learning_style.pace_preference == 'fast':
            suggestions.append("建议采用快速浏览+重点突破的学习方式")
        elif self.learning_style.pace_preference == 'deep':
            suggestions.append("建议深入理解每个概念，不要急于求成")
        
        # 基于每天可用时间的学习计划建议
        daily_minutes = self.learning_preference.daily_available_minutes
        if daily_minutes < 30:
            suggestions.append("建议每天至少学习30分钟，形成学习习惯")
        elif daily_minutes >= 120:
            suggestions.append("建议将学习时间分成多个30-45分钟的时间段，提高学习效率")
        
        # 基于当前进度的建议
        current_progress = user_path.progress
        if current_progress < 20:
            suggestions.append("刚开始学习，建议先熟悉整体框架，再逐步深入")
        elif 20 <= current_progress < 60:
            suggestions.append("学习进展顺利，继续保持！建议定期复习已学内容")
        elif current_progress >= 60:
            suggestions.append("接近完成，建议重点关注难点和薄弱环节")
        
        return suggestions
    
    def evaluate_learning_effect(self):
        """评估学习效果"""
        # 计算平均练习成绩
        avg_score = self.practice_records.filter(completed=True).aggregate(Avg('score'))['score__avg'] or 0
        
        # 计算完成率
        total_chapters = sum(record.book.chapters.count() for record in self.learning_records)
        completed_chapters = self.learning_records.filter(progress=100).count()
        completion_rate = completed_chapters / total_chapters if total_chapters > 0 else 0
        
        # 计算学习连续性（最近7天的学习天数）
        consecutive_days = self._calculate_consecutive_days()
        
        # 分析学习瓶颈（得分较低的章节）
        weak_chapters = self._identify_weak_chapters()
        
        return {
            'average_score': round(avg_score, 2),
            'completion_rate': round(completion_rate * 100, 2),
            'consecutive_days': consecutive_days,
            'weak_chapters': weak_chapters,
            'suggestions': self._generate_improvement_suggestions(avg_score, completion_rate, consecutive_days)
        }
    
    def _calculate_consecutive_days(self):
        """计算连续学习天数"""
        from .models import HeatmapData
        
        # 获取最近的学习记录，按日期降序排列
        recent_learning_days = list(HeatmapData.objects.filter(
            user=self.user,
            minutes__gt=0
        ).order_by('-date').values_list('date', flat=True))
        
        if not recent_learning_days:
            return 0
        
        # 计算连续天数
        consecutive_days = 0
        current_date = datetime.now().date()
        
        for learning_date in recent_learning_days:
            if learning_date == current_date or learning_date == current_date - timedelta(days=1):
                consecutive_days += 1
                current_date = learning_date
            else:
                break
        
        return consecutive_days
    
    def _identify_weak_chapters(self):
        """识别薄弱章节"""
        weak_chapters = []
        
        # 查找分数低于60分的练习记录对应的章节
        weak_practices = self.practice_records.filter(score__lt=60)
        
        for practice in weak_practices:
            weak_chapters.append({
                'book_title': practice.book.title,
                'chapter_title': practice.chapter.title,
                'score': practice.score,
                'completed_time': practice.completed_time
            })
        
        return weak_chapters[:5]  # 返回前5个薄弱章节
    
    def _generate_improvement_suggestions(self, avg_score, completion_rate, consecutive_days):
        """生成改进建议"""
        suggestions = []
        
        # 基于平均成绩的建议
        if avg_score < 60:
            suggestions.append("建议加强基础知识学习，多做相关练习")
        elif avg_score < 80:
            suggestions.append("学习效果良好，建议进一步提高练习难度")
        else:
            suggestions.append("学习效果优秀，建议尝试更具挑战性的内容")
        
        # 基于完成率的建议
        if completion_rate < 30:
            suggestions.append("建议制定明确的学习计划，每天坚持学习")
        elif completion_rate < 70:
            suggestions.append("继续保持学习进度，可以适当加快速度")
        
        # 基于学习连续性的建议
        if consecutive_days < 3:
            suggestions.append("建议培养每天学习的习惯，提高学习连续性")
        elif consecutive_days >= 7:
            suggestions.append("学习习惯很好，继续保持！")
        
        return suggestions