"""学习记录序列化器"""
from rest_framework import serializers
from .models import LearningRecord, PracticeRecord, HeatmapData, WrongQuestion, UserLearningPath, RoadmapTemplate, RoadmapStage, RoadmapBook, UserPathStage, Note, JupyterDocument, LearningStyle, KnowledgeMastery, LearningRecommendation, LearningPreference


class LearningRecordSerializer(serializers.ModelSerializer):
    """学习记录序列化器"""
    class Meta:
        model = LearningRecord
        fields = ('id', 'book', 'chapter', 'progress', 'last_learn_time')
        read_only_fields = ('id', 'user', 'last_learn_time')


class SaveProgressSerializer(serializers.Serializer):
    """保存进度序列化器"""
    book_id = serializers.IntegerField(required=True)
    chapter_id = serializers.IntegerField(required=True)
    progress = serializers.IntegerField(required=True, min_value=0, max_value=100)


class PracticeRecordSerializer(serializers.ModelSerializer):
    """练习记录序列化器"""
    class Meta:
        model = PracticeRecord
        fields = ('id', 'book', 'chapter', 'score', 'completed', 'user_code', 'completed_time')
        read_only_fields = ('id', 'user', 'completed_time')


class HeatmapDataSerializer(serializers.ModelSerializer):
    """热力图数据序列化器"""
    class Meta:
        model = HeatmapData
        fields = ('date', 'minutes')


class RoadmapBookSerializer(serializers.ModelSerializer):
    """路线图书籍序列化器"""
    book = serializers.SerializerMethodField()
    importance_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RoadmapBook
        fields = ('book', 'recommended_order', 'importance', 'importance_display', 'notes')
    
    def get_book(self, obj):
        from apps.books.serializers import BookListSerializer
        return BookListSerializer(obj.book).data
    
    def get_importance_display(self, obj):
        return dict(RoadmapBook.importance.field.choices).get(obj.importance)


class RoadmapStageSerializer(serializers.ModelSerializer):
    """路线图阶段序列化器"""
    books = RoadmapBookSerializer(source='roadmap_books', many=True)
    
    class Meta:
        model = RoadmapStage
        fields = ('id', 'stage_order', 'title', 'description', 'learning_goals', 
                  'required_skills', 'estimated_duration', 'books')


class RoadmapTemplateSerializer(serializers.ModelSerializer):
    """路线图模板序列化器"""
    stages = RoadmapStageSerializer(many=True, read_only=True)
    major_display = serializers.SerializerMethodField()
    difficulty_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RoadmapTemplate
        fields = ('id', 'major', 'major_display', 'title', 'description', 
                  'difficulty_level', 'difficulty_display', 'estimated_hours', 
                  'tags', 'stages')
    
    def get_major_display(self, obj):
        return obj.get_major_display()
    
    def get_difficulty_display(self, obj):
        return obj.get_difficulty_display()


class UserPathStageSerializer(serializers.ModelSerializer):
    """用户路径阶段序列化器"""
    stage = RoadmapStageSerializer(read_only=True)
    
    class Meta:
        model = UserPathStage
        fields = ('stage', 'progress', 'is_completed', 'started_at', 'completed_at', 'notes')


class UserLearningPathSerializer(serializers.ModelSerializer):
    """用户学习路径序列化器"""
    roadmap = RoadmapTemplateSerializer(read_only=True)
    current_stage = RoadmapStageSerializer(read_only=True)
    stage_progress = UserPathStageSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserLearningPath
        fields = ('id', 'roadmap', 'current_stage', 'progress', 'started_at', 
                  'completed_at', 'custom_goals', 'is_active', 'stage_progress')


class CreateUserPathSerializer(serializers.Serializer):
    """创建用户学习路径序列化器"""
    roadmap_id = serializers.IntegerField(required=True)
    custom_goals = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class UpdatePathProgressSerializer(serializers.Serializer):
    """更新学习路径进度序列化器"""
    stage_id = serializers.IntegerField(required=True)
    progress = serializers.IntegerField(required=True, min_value=0, max_value=100)
    notes = serializers.CharField(required=False, allow_blank=True)


class SubmitPracticeSerializer(serializers.Serializer):
    """提交练习序列化器"""
    book_id = serializers.IntegerField(required=True)
    chapter_id = serializers.IntegerField(required=True)
    score = serializers.IntegerField(required=True, min_value=0, max_value=100)
    user_code = serializers.CharField(required=False, allow_blank=True)


class HeatmapDataSerializer(serializers.ModelSerializer):
    """学习热力图数据序列化器"""
    date = serializers.DateField(format='%Y-%m-%d')
    
    class Meta:
        model = HeatmapData
        fields = ('date', 'minutes')


class WrongQuestionSerializer(serializers.ModelSerializer):
    """错题序列化器"""
    book_title = serializers.SerializerMethodField()
    attempt_time = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = WrongQuestion
        fields = ('id', 'title', 'difficulty', 'book', 'chapter', 'book_title', 'attempt_time')
        read_only_fields = ('id', 'user', 'attempt_time', 'book_title')

    def get_book_title(self, obj):
        try:
            return obj.book.title
        except Exception:
            return ''


class NoteSerializer(serializers.ModelSerializer):
    """笔记序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class JupyterDocumentSerializer(serializers.ModelSerializer):
    """Jupyter文档序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    user_info = serializers.SerializerMethodField()
    book_info = serializers.SerializerMethodField()
    chapter_info = serializers.SerializerMethodField()

    class Meta:
        model = JupyterDocument
        fields = ('id', 'title', 'content', 'book', 'chapter', 'user', 'user_info', 
                  'book_info', 'chapter_info', 'is_public', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'user_info', 'book_info', 'chapter_info', 
                           'created_at', 'updated_at')
    
    def get_user_info(self, obj):
        """获取用户基本信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'avatar': getattr(obj.user, 'avatar', '')
        }
    
    def get_book_info(self, obj):
        """获取书籍基本信息"""
        if obj.book:
            return {
                'id': obj.book.id,
                'title': obj.book.title,
                'cover': obj.book.cover
            }
        return None
    
    def get_chapter_info(self, obj):
        """获取章节基本信息"""
        if obj.chapter:
            return {
                'id': obj.chapter.id,
                'title': obj.chapter.title
            }
        return None


class CreateJupyterDocumentSerializer(serializers.Serializer):
    """创建Jupyter文档序列化器"""
    title = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(required=True)
    book_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    is_public = serializers.BooleanField(default=False)


class UpdateJupyterDocumentSerializer(serializers.Serializer):
    """更新Jupyter文档序列化器"""
    title = serializers.CharField(max_length=255, required=False)
    content = serializers.CharField(required=False)
    book_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    is_public = serializers.BooleanField(required=False)


class LearningStyleSerializer(serializers.ModelSerializer):
    """学习风格序列化器"""
    pace_preference_display = serializers.SerializerMethodField()
    environment_preference_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningStyle
        fields = ('id', 'visual_score', 'auditory_score', 'reading_score', 'kinesthetic_score',
                  'pace_preference', 'pace_preference_display', 'environment_preference',
                  'environment_preference_display', 'preferred_resource_types', 'updated_at')
        read_only_fields = ('id', 'user', 'updated_at')
    
    def get_pace_preference_display(self, obj):
        return dict(LearningStyle.pace_preference.field.choices).get(obj.pace_preference)
    
    def get_environment_preference_display(self, obj):
        return dict(LearningStyle.environment_preference.field.choices).get(obj.environment_preference)


class UpdateLearningStyleSerializer(serializers.Serializer):
    """更新学习风格序列化器"""
    visual_score = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    auditory_score = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    reading_score = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    kinesthetic_score = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    pace_preference = serializers.ChoiceField(choices=LearningStyle.pace_preference.field.choices, required=False)
    environment_preference = serializers.ChoiceField(choices=LearningStyle.environment_preference.field.choices, required=False)
    preferred_resource_types = serializers.ListField(child=serializers.CharField(), required=False)


class KnowledgeMasterySerializer(serializers.ModelSerializer):
    """知识掌握度序列化器"""
    book_info = serializers.SerializerMethodField()
    chapter_info = serializers.SerializerMethodField()
    assessed_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = KnowledgeMastery
        fields = ('id', 'knowledge_point', 'mastery_level', 'assessed_at', 'assessment_count',
                  'tags', 'book', 'book_info', 'chapter', 'chapter_info')
        read_only_fields = ('id', 'user', 'assessed_at', 'assessment_count')
    
    def get_book_info(self, obj):
        if obj.book:
            return {
                'id': obj.book.id,
                'title': obj.book.title
            }
        return None
    
    def get_chapter_info(self, obj):
        if obj.chapter:
            return {
                'id': obj.chapter.id,
                'title': obj.chapter.title
            }
        return None


class UpdateKnowledgeMasterySerializer(serializers.Serializer):
    """更新知识掌握度序列化器"""
    knowledge_point = serializers.CharField(max_length=255, required=True)
    mastery_level = serializers.FloatField(required=True, min_value=0.0, max_value=1.0)
    book_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class LearningRecommendationSerializer(serializers.ModelSerializer):
    """学习推荐序列化器"""
    recommendation_type_display = serializers.SerializerMethodField()
    user_feedback_display = serializers.SerializerMethodField()
    recommended_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    feedback_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, allow_null=True)
    
    # 关联对象的基本信息
    roadmap_info = serializers.SerializerMethodField()
    stage_info = serializers.SerializerMethodField()
    book_info = serializers.SerializerMethodField()
    chapter_info = serializers.SerializerMethodField()
    exercise_info = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningRecommendation
        fields = ('id', 'recommendation_type', 'recommendation_type_display', 'score',
                  'reason', 'recommended_at', 'user_feedback', 'user_feedback_display',
                  'feedback_at', 'roadmap', 'roadmap_info', 'stage', 'stage_info',
                  'book', 'book_info', 'chapter', 'chapter_info', 'exercise', 'exercise_info')
        read_only_fields = ('id', 'user', 'user_path', 'score', 'recommended_at')
    
    def get_recommendation_type_display(self, obj):
        return dict(LearningRecommendation.recommendation_type.field.choices).get(obj.recommendation_type)
    
    def get_user_feedback_display(self, obj):
        return dict(LearningRecommendation.user_feedback.field.choices).get(obj.user_feedback)
    
    def get_roadmap_info(self, obj):
        if obj.roadmap:
            return {
                'id': obj.roadmap.id,
                'title': obj.roadmap.title,
                'major': obj.roadmap.major,
                'difficulty_level': obj.roadmap.difficulty_level
            }
        return None
    
    def get_stage_info(self, obj):
        if obj.stage:
            return {
                'id': obj.stage.id,
                'title': obj.stage.title,
                'stage_order': obj.stage.stage_order
            }
        return None
    
    def get_book_info(self, obj):
        if obj.book:
            return {
                'id': obj.book.id,
                'title': obj.book.title,
                'cover': obj.book.cover
            }
        return None
    
    def get_chapter_info(self, obj):
        if obj.chapter:
            return {
                'id': obj.chapter.id,
                'title': obj.chapter.title,
                'chapter_number': obj.chapter.chapter_number
            }
        return None
    
    def get_exercise_info(self, obj):
        if obj.exercise:
            return {
                'id': obj.exercise.id,
                'title': obj.exercise.title,
                'difficulty': obj.exercise.difficulty,
                'category': obj.exercise.category
            }
        return None


class FeedbackRecommendationSerializer(serializers.Serializer):
    """反馈推荐序列化器"""
    feedback = serializers.ChoiceField(choices=LearningRecommendation.user_feedback.field.choices, required=True)


class LearningPreferenceSerializer(serializers.ModelSerializer):
    """学习偏好序列化器"""
    difficulty_preference_display = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = LearningPreference
        fields = ('id', 'learning_goals', 'interest_areas', 'daily_available_minutes',
                  'reminder_enabled', 'reminder_time', 'difficulty_preference',
                  'difficulty_preference_display', 'updated_at')
        read_only_fields = ('id', 'user', 'updated_at')
    
    def get_difficulty_preference_display(self, obj):
        return dict(LearningPreference.difficulty_preference.field.choices).get(obj.difficulty_preference)


class UpdateLearningPreferenceSerializer(serializers.Serializer):
    """更新学习偏好序列化器"""
    learning_goals = serializers.ListField(child=serializers.CharField(), required=False)
    interest_areas = serializers.ListField(child=serializers.CharField(), required=False)
    daily_available_minutes = serializers.IntegerField(required=False, min_value=0)
    reminder_enabled = serializers.BooleanField(required=False)
    reminder_time = serializers.TimeField(required=False, allow_null=True)
    difficulty_preference = serializers.ChoiceField(choices=LearningPreference.difficulty_preference.field.choices, required=False)