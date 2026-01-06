"""学习记录序列化器"""
from rest_framework import serializers
from .models import LearningRecord, PracticeRecord, HeatmapData, WrongQuestion, UserLearningPath, RoadmapTemplate, RoadmapStage, RoadmapBook, UserPathStage, Note, NoteTag, NoteAttachment, NoteVersion, NoteShare, JupyterDocument, LearningStyle, KnowledgeMastery, LearningRecommendation, LearningPreference


class LearningRecordSerializer(serializers.ModelSerializer):
    """学习记录序列化器"""
    class Meta:
        model = LearningRecord
        fields = ('id', 'book', 'chapter', 'progress', 'last_learn_time')
        read_only_fields = ('id', 'user', 'last_learn_time')


class LearningActivitySerializer(serializers.Serializer):
    """
    统一的学习活动序列化器
    用于将阅读/练习记录转换为前端需要的扁平结构
    """
    id = serializers.CharField()
    type = serializers.ChoiceField(choices=['reading', 'practice', 'video', 'quiz', 'unknown'])
    bookId = serializers.IntegerField()
    chapterId = serializers.IntegerField(required=False, allow_null=True)
    bookTitle = serializers.CharField(allow_blank=True)
    chapterTitle = serializers.CharField(allow_blank=True, required=False)
    duration = serializers.FloatField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=['completed', 'inProgress', 'unknown'])
    timestamp = serializers.DateTimeField()
    progress = serializers.IntegerField(required=False, allow_null=True)
    score = serializers.IntegerField(required=False, allow_null=True)


class SaveProgressSerializer(serializers.Serializer):
    """保存进度序列化器"""
    book_id = serializers.IntegerField(required=True)
    chapter_id = serializers.IntegerField(required=True)
    progress = serializers.IntegerField(required=True, min_value=0, max_value=100)


class PracticeRecordSerializer(serializers.ModelSerializer):
    """练习记录序列化器"""
    bookTitle = serializers.SerializerMethodField()
    chapterTitle = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source='completed_time')
    
    class Meta:
        model = PracticeRecord
        fields = ('id', 'book', 'chapter', 'bookTitle', 'chapterTitle', 'score', 'completed', 'user_code', 'completed_time', 'timestamp')
        read_only_fields = ('id', 'user', 'completed_time')
    
    def get_bookTitle(self, obj):
        return obj.book.title if obj.book else ''
    
    def get_chapterTitle(self, obj):
        return obj.chapter.title if obj.chapter else ''


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


class NoteTagSerializer(serializers.ModelSerializer):
    """笔记标签序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = NoteTag
        fields = ('id', 'name', 'color', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class NoteAttachmentSerializer(serializers.ModelSerializer):
    """笔记附件序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = NoteAttachment
        fields = ('id', 'file', 'file_name', 'file_size', 'file_type', 'created_at')
        read_only_fields = ('id', 'note', 'created_at')


class NoteVersionSerializer(serializers.ModelSerializer):
    """笔记版本序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = NoteVersion
        fields = ('id', 'title', 'content', 'version_number', 'created_at')
        read_only_fields = ('id', 'note', 'created_at')


class NoteShareSerializer(serializers.ModelSerializer):
    """笔记分享序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    note_title = serializers.SerializerMethodField()

    class Meta:
        model = NoteShare
        fields = ('id', 'share_code', 'note_title', 'expires_at', 'view_count', 'created_at')
        read_only_fields = ('id', 'note', 'shared_by', 'created_at')

    def get_note_title(self, obj):
        return obj.note.title


class NoteListSerializer(serializers.ModelSerializer):
    """笔记列表序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    tags = NoteTagSerializer(many=True, source='tag_relations__tag', read_only=True)
    book_title = serializers.SerializerMethodField()
    chapter_title = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'is_favorite', 'is_public', 'view_count', 
                  'created_at', 'updated_at', 'tags', 'book_title', 'chapter_title')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_book_title(self, obj):
        return obj.book.title if obj.book else ''

    def get_chapter_title(self, obj):
        return obj.chapter.title if obj.chapter else ''


class NoteDetailSerializer(serializers.ModelSerializer):
    """笔记详情序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    tags = serializers.SerializerMethodField()
    attachments = NoteAttachmentSerializer(many=True, read_only=True)
    book_title = serializers.SerializerMethodField()
    chapter_title = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'is_favorite', 'is_public', 'view_count', 
                  'created_at', 'updated_at', 'last_reviewed_at', 'book', 'chapter', 
                  'position', 'tags', 'attachments', 'book_title', 'chapter_title')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_book_title(self, obj):
        return obj.book.title if obj.book else ''

    def get_chapter_title(self, obj):
        return obj.chapter.title if obj.chapter else ''

    def get_tags(self, obj):
        tag_relations = obj.tag_relations.select_related('tag').all()
        return NoteTagSerializer([relation.tag for relation in tag_relations], many=True).data


class NoteCreateSerializer(serializers.ModelSerializer):
    """笔记创建序列化器"""
    tags = serializers.ListField(child=serializers.CharField(max_length=50), write_only=True, required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    tags_data = NoteTagSerializer(many=True, source='tag_relations__tag', read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'book', 'chapter', 'position', 'tags', 
                  'is_favorite', 'is_public', 'view_count', 'created_at', 'updated_at', 'tags_data')
        extra_kwargs = {
            'content': {'allow_blank': True, 'default': ''}
        }

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        note = Note.objects.create(**validated_data)
        
        # 创建版本历史
        NoteVersion.objects.create(
            note=note,
            title=note.title,
            content=note.content,
            version_number=1
        )
        
        # 处理标签
        self._process_tags(note, tags)
        
        # 重新加载note以获取关联的标签数据
        note.refresh_from_db()
        
        return note

    def _process_tags(self, note, tag_names):
        for tag_name in tag_names:
            tag, created = NoteTag.objects.get_or_create(
                user=note.user,
                name=tag_name.strip()
            )
            NoteTagRelation.objects.get_or_create(
                note=note,
                tag=tag
            )


class NoteUpdateSerializer(serializers.ModelSerializer):
    """笔记更新序列化器"""
    tags = serializers.ListField(child=serializers.CharField(max_length=50), write_only=True, required=False)

    class Meta:
        model = Note
        fields = ('title', 'content', 'is_favorite', 'is_public', 'tags')

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        # 检查内容是否真的发生了变化
        content_changed = 'content' in validated_data and validated_data['content'] != instance.content
        title_changed = 'title' in validated_data and validated_data['title'] != instance.title
        
        # 只在内容或标题发生变化时创建版本历史
        if content_changed or title_changed:
            current_version = instance.versions.count()
            # 限制版本数量，最多保留最近20个版本
            if current_version >= 20:
                # 删除最旧的版本
                oldest_version = instance.versions.order_by('version_number').first()
                if oldest_version:
                    oldest_version.delete()
            
            NoteVersion.objects.create(
                note=instance,
                title=instance.title,
                content=instance.content,
                version_number=current_version + 1
            )
        
        # 更新笔记
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 处理标签
        if tags is not None:
            # 清除现有标签关联
            instance.tag_relations.all().delete()
            # 添加新标签
            for tag_name in tags:
                tag, created = NoteTag.objects.get_or_create(
                    user=instance.user,
                    name=tag_name.strip()
                )
                NoteTagRelation.objects.get_or_create(
                    note=instance,
                    tag=tag
                )
        
        return instance


class NoteSerializer(serializers.ModelSerializer):
    """笔记默认序列化器"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'is_favorite', 'is_public', 'view_count', 
                  'created_at', 'updated_at', 'book', 'chapter', 'position')
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