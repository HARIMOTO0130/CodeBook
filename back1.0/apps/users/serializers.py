"""用户序列化器"""
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, UserPreferences
from apps.learning.models import LearningStyle, KnowledgeMastery, LearningPreference


class UserPreferencesSerializer(serializers.ModelSerializer):
    """用户偏好设置序列化器"""
    class Meta:
        model = UserPreferences
        fields = (
            'default_language', 'code_theme', 'auto_play_video', 'keyboard_shortcuts', 'show_line_numbers', 'use_vim_mode',
            'learning_goals', 'major_category', 'major', 'learning_stage', 'interests',
            'enable_learning_reminders', 'reminder_time', 'daily_reminder', 'deadline_reminder'
        )


class LearningStyleSerializer(serializers.ModelSerializer):
    """学习风格序列化器"""
    class Meta:
        model = LearningStyle
        fields = (
            'visual_score', 'auditory_score', 'reading_score', 'kinesthetic_score',
            'pace_preference', 'environment_preference', 'preferred_resource_types'
        )


class KnowledgeMasterySerializer(serializers.ModelSerializer):
    """知识掌握度序列化器"""
    class Meta:
        model = KnowledgeMastery
        fields = (
            'knowledge_point', 'mastery_level', 'assessed_at', 'assessment_count', 'tags'
        )


class LearningPreferenceSerializer(serializers.ModelSerializer):
    """学习偏好序列化器"""
    class Meta:
        model = LearningPreference
        fields = (
            'learning_goals', 'interest_areas', 'daily_available_minutes',
            'reminder_enabled', 'reminder_time', 'difficulty_preference'
        )


class UserProfileSerializer(serializers.Serializer):
    """用户画像序列化器"""
    # 基本信息
    user = serializers.SerializerMethodField()
    
    # 多维度特征提取
    multi_dim_features = serializers.SerializerMethodField()
    
    # 知识状态评估
    knowledge_state = serializers.SerializerMethodField()
    
    # 专业倾向性分析
    professional_tendency = serializers.SerializerMethodField()
    
    # 学习情况数据
    learning_stats = serializers.SerializerMethodField()
    
    # 学习偏好
    learning_preferences = serializers.SerializerMethodField()
    
    # 专业组信息
    professional_group_info = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """获取用户基本信息"""
        user = obj['user']
        return {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'email': user.email,
            'role': user.role,
            'avatar': user.avatar.url if user.avatar else None,
            'learning_stage': user.preferences.learning_stage if hasattr(user, 'preferences') else 'beginner'
        }
    
    def get_multi_dim_features(self, obj):
        """获取多维度特征"""
        user = obj['user']
        learning_style = obj.get('learning_style')
        learning_preference = obj.get('learning_preference')
        
        # 计算学习风格类型
        style_scores = {}
        if learning_style:
            style_scores = {
                'visual': learning_style.visual_score,
                'auditory': learning_style.auditory_score,
                'reading': learning_style.reading_score,
                'kinesthetic': learning_style.kinesthetic_score
            }
            dominant_style = max(style_scores, key=style_scores.get)
        else:
            dominant_style = 'balanced'
        
        # 构建多维度特征
        multi_dim_features = {
            'learning_style': {
                'dominant_style': dominant_style,
                'scores': style_scores
            },
            'learning_goals': user.preferences.learning_goals if hasattr(user, 'preferences') else [],
            'interests': user.preferences.interests if hasattr(user, 'preferences') else [],
            'daily_available_time': learning_preference.daily_available_minutes if learning_preference else 60,
            'difficulty_preference': learning_preference.difficulty_preference if learning_preference else 'medium'
        }
        
        return multi_dim_features
    
    def get_knowledge_state(self, obj):
        """获取知识状态评估"""
        knowledge_mastery = obj.get('knowledge_mastery', [])
        
        # 计算平均掌握度
        if knowledge_mastery:
            avg_mastery = sum(km.mastery_level for km in knowledge_mastery) / len(knowledge_mastery)
        else:
            avg_mastery = 0.0
        
        # 按掌握度分类知识点
        mastered = [km for km in knowledge_mastery if km.mastery_level >= 0.7]
        in_progress = [km for km in knowledge_mastery if 0.3 <= km.mastery_level < 0.7]
        needs_improvement = [km for km in knowledge_mastery if km.mastery_level < 0.3]
        
        # 提取标签频率
        tag_freq = {}
        for km in knowledge_mastery:
            for tag in km.tags:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1
        
        top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        knowledge_state = {
            'overall_mastery': round(avg_mastery, 2),
            'mastery_distribution': {
                'mastered': len(mastered),
                'in_progress': len(in_progress),
                'needs_improvement': len(needs_improvement)
            },
            'top_tags': [tag[0] for tag in top_tags],
            'knowledge_points': KnowledgeMasterySerializer(knowledge_mastery, many=True).data
        }
        
        return knowledge_state
    
    def get_professional_tendency(self, obj):
        """获取专业倾向性分析"""
        user = obj['user']
        knowledge_mastery = obj.get('knowledge_mastery', [])
        
        # 专业组映射
        professional_groups = {
            'business': '经管类',
            'humanities': '文史类',
            'arts': '艺术类',
            'science': '理工科'
        }
        
        # 计算专业倾向性分数
        group_scores = {
            'business': 0.0,
            'humanities': 0.0,
            'arts': 0.0,
            'science': 0.0
        }
        
        # 根据知识掌握度计算专业分数
        for km in knowledge_mastery:
            for tag in km.tags:
                # 简单的标签匹配逻辑，实际应用中可能需要更复杂的映射
                tag_lower = tag.lower()
                if any(keyword in tag_lower for keyword in ['business', 'finance', 'management', 'economics']):
                    group_scores['business'] += km.mastery_level
                elif any(keyword in tag_lower for keyword in ['literature', 'history', 'philosophy', 'culture']):
                    group_scores['humanities'] += km.mastery_level
                elif any(keyword in tag_lower for keyword in ['art', 'design', 'creative', 'aesthetic']):
                    group_scores['arts'] += km.mastery_level
                elif any(keyword in tag_lower for keyword in ['science', 'technology', 'engineering', 'math']):
                    group_scores['science'] += km.mastery_level
        
        # 计算最高分的专业组
        max_score = max(group_scores.values())
        dominant_group = max(group_scores, key=group_scores.get) if max_score > 0 else 'science'
        
        professional_tendency = {
            'dominant_group': professional_groups[dominant_group],
            'group_scores': {
                professional_groups[group]: round(score, 2) for group, score in group_scores.items()
            }
        }
        
        return professional_tendency
    
    def get_learning_stats(self, obj):
        """获取学习情况数据"""
        learning_records = obj.get('learning_records', [])
        practice_records = obj.get('practice_records', [])
        heatmap_data = obj.get('heatmap_data', [])
        wrong_questions = obj.get('wrong_questions', [])
        
        # 计算学习时长
        total_learning_minutes = sum(record.minutes for record in heatmap_data)
        
        # 计算练习完成情况
        total_practices = len(practice_records)
        completed_practices = len([record for record in practice_records if record.completed])
        avg_score = sum(record.score for record in practice_records) / total_practices if total_practices > 0 else 0
        
        # 计算学习进度
        total_chapters = len(set((record.book.id, record.chapter.id) for record in learning_records))
        completed_chapters = len([record for record in learning_records if record.progress >= 100])
        avg_progress = sum(record.progress for record in learning_records) / total_chapters if total_chapters > 0 else 0
        
        return {
            'total_learning_minutes': total_learning_minutes,
            'total_practices': total_practices,
            'completed_practices': completed_practices,
            'avg_practice_score': round(avg_score, 2),
            'total_chapters': total_chapters,
            'completed_chapters': completed_chapters,
            'avg_chapter_progress': round(avg_progress, 2),
            'wrong_questions_count': len(wrong_questions),
            'recent_learning_days': len(set(record.date for record in heatmap_data))
        }
    
    def get_learning_preferences(self, obj):
        """获取学习偏好"""
        user = obj['user']
        learning_preference = obj.get('learning_preference')
        
        if hasattr(user, 'preferences'):
            return {
                'learning_goals': user.preferences.learning_goals,
                'major': user.preferences.major,
                'interests': user.preferences.interests,
                'enable_learning_reminders': user.preferences.enable_learning_reminders,
                'reminder_time': user.preferences.reminder_time.strftime('%H:%M') if user.preferences.reminder_time else '09:00',
                'daily_available_minutes': learning_preference.daily_available_minutes if learning_preference else 60,
                'difficulty_preference': learning_preference.difficulty_preference if learning_preference else 'medium'
            }
        return {
            'learning_goals': [],
            'major': None,
            'interests': [],
            'enable_learning_reminders': True,
            'reminder_time': '09:00',
            'daily_available_minutes': 60,
            'difficulty_preference': 'medium'
        }
    
    def get_professional_group_info(self, obj):
        """获取专业组信息"""
        user = obj['user']
        professional_tendency = self.get_professional_tendency(obj)
        dominant_group = professional_tendency['dominant_group']
        
        # 专业组特征映射
        group_features = {
            '经管类': {
                'core_features': ['案例驱动', '数据导向', '商业思维'],
                'recommended_tools': ['商业智能工具', '数据分析工具', '可视化工具'],
                'career_paths': ['商业分析师', '数据分析师', '项目经理']
            },
            '文史类': {
                'core_features': ['文本分析', '批判性思维', '文化理解'],
                'recommended_tools': ['文本分析工具', '数字人文工具', '内容创作工具'],
                'career_paths': ['数字人文研究员', '内容分析师', '文化遗产保护']
            },
            '艺术类': {
                'core_features': ['创意表达', '工具掌握', '美学设计'],
                'recommended_tools': ['生成艺术工具', '创意设计工具', '交互媒体工具'],
                'career_paths': ['创意设计师', '生成艺术家', '交互媒体设计师']
            },
            '理工科': {
                'core_features': ['实践导向', '算法深度', '系统设计'],
                'recommended_tools': ['编程工具', '部署工具链', '算法库'],
                'career_paths': ['软件工程师', '算法工程师', '系统架构师']
            }
        }
        
        return {
            'dominant_group': dominant_group,
            'group_scores': professional_tendency['group_scores'],
            'features': group_features.get(dominant_group, {
                'core_features': [],
                'recommended_tools': [],
                'career_paths': []
            }),
            'custom_major': user.preferences.major if hasattr(user, 'preferences') else None
        }


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    preferences = UserPreferencesSerializer(required=False)
    role = serializers.CharField(read_only=True)
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'nickname', 'email', 'phone', 'avatar', 'bio', 
            'role', 'profile_visibility', 'learning_records_visibility', 'preferences'
        )
        read_only_fields = ('id', 'role')
    
    def get_avatar(self, obj):
        """返回完整的头像URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def update(self, instance, validated_data):
        preferences_data = validated_data.pop('preferences', None)
        
        # 更新用户基本信息
        instance = super().update(instance, validated_data)
        
        # 更新用户偏好设置
        if preferences_data:
            preferences, created = UserPreferences.objects.get_or_create(user=instance)
            for key, value in preferences_data.items():
                setattr(preferences, key, value)
            preferences.save()
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, min_length=3, max_length=150)
    role = serializers.ChoiceField(
        choices=[('student', '学生'), ('teacher', '教师'), ('provider', '教材提供者'), ('admin', '管理员')],
        default='student',
        required=False,
        allow_blank=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {
            'username': {
                'required': True,
                'min_length': 3,
                'max_length': 150,
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message='用户名已存在，请更换其他用户名'
                    )
                ]
            },
            'email': {
                'required': True,
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message='邮箱已被注册，请更换其他邮箱'
                    )
                ]
            }
        }
    
    def create(self, validated_data):
        role = validated_data.pop('role', 'student')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        # 创建默认偏好设置
        UserPreferences.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)