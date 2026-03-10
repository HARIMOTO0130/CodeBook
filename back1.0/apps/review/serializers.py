# -*- coding: utf-8 -*-
"""审核模块序列化器"""
from rest_framework import serializers
from .models import ReviewTask, ManualReviewRecord, AIReviewRecord, WorkflowLog, ReviewRuleConfig, BookEditHistory, TeacherProfile
from apps.books.models import Book, BookVersion


class ReviewTaskListSerializer(serializers.ModelSerializer):
    """审核任务列表序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_reviewer_name = serializers.CharField(source='assigned_reviewer.username', read_only=True)
    
    # 提交人信息
    submitted_by_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewTask
        fields = ['id', 'book_id', 'book_title', 'book_author', 'task_type', 'task_type_display',
                  'priority', 'priority_display', 'status', 'status_display', 'assigned_reviewer',
                  'assigned_reviewer_name', 'submitted_by_name', 'submitted_at', 'deadline',
                  'version_number', 'chapter_count', 'created_at', 'submitted_by_info',
                  'book_isbn', 'book_language', 'book_word_count', 'category_name']
    
    def get_submitted_by_info(self, obj):
        """获取提交人详细信息"""
        return {
            'id': obj.submitted_by_id,
            'name': obj.submitted_by_name,
            'username': obj.submitted_by_username,
            'employee_id': obj.submitted_by_employee_id,
            'department': obj.submitted_by_department,
            'email': obj.submitted_by_email,
            'phone': obj.submitted_by_phone,
        }


class ReviewTaskDetailSerializer(serializers.ModelSerializer):
    """审核任务详情序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_reviewer_name = serializers.CharField(source='assigned_reviewer.username', read_only=True)
    ai_record = serializers.SerializerMethodField()
    manual_records = serializers.SerializerMethodField()
    edit_history = serializers.SerializerMethodField()
    
    # 提交人信息
    submitted_by_info = serializers.SerializerMethodField()
    modified_by_info = serializers.SerializerMethodField()
    original_uploader_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewTask
        fields = ['id', 'book_id', 'book_title', 'book_subtitle', 'book_author', 'book_isbn',
                  'book_language', 'book_word_count', 'task_type', 'task_type_display',
                  'priority', 'priority_display', 'status', 'status_display', 'assigned_reviewer',
                  'assigned_reviewer_name', 'submitted_by_id', 'submitted_by_name', 'submitted_at',
                  'deadline', 'version_number', 'previous_version', 'chapter_count', 'description',
                  'change_summary', 'category_name', 'tags', 'created_at', 'updated_at',
                  'original_uploaded_at', 'last_modified_at', 'ai_record', 'manual_records',
                  'edit_history', 'submitted_by_info', 'modified_by_info', 'original_uploader_info']
    
    def get_ai_record(self, obj):
        try:
            record = obj.ai_record
            return AIReviewRecordSerializer(record).data
        except AIReviewRecord.DoesNotExist:
            return None
    
    def get_manual_records(self, obj):
        records = obj.manual_records.all()[:3]
        return ManualReviewRecordListSerializer(records, many=True).data
    
    def get_edit_history(self, obj):
        """获取教材修改历史"""
        history = obj.edit_history.all()[:10]
        return BookEditHistorySerializer(history, many=True).data
    
    def get_submitted_by_info(self, obj):
        """获取提交人详细信息"""
        return {
            'id': obj.submitted_by_id,
            'name': obj.submitted_by_name,
            'username': obj.submitted_by_username,
            'employee_id': obj.submitted_by_employee_id,
            'department': obj.submitted_by_department,
            'email': obj.submitted_by_email,
            'phone': obj.submitted_by_phone,
        }
    
    def get_modified_by_info(self, obj):
        """获取修改人详细信息"""
        return {
            'id': obj.modified_by_id,
            'name': obj.modified_by_name,
            'username': obj.modified_by_username,
            'employee_id': obj.modified_by_employee_id,
            'department': obj.modified_by_department,
        }
    
    def get_original_uploader_info(self, obj):
        """获取原始上传者详细信息"""
        return {
            'id': obj.original_uploader_id,
            'name': obj.original_uploader_name,
            'username': obj.original_uploader_username,
            'employee_id': obj.original_uploader_employee_id,
            'department': obj.original_uploader_department,
        }


class ManualReviewRecordListSerializer(serializers.ModelSerializer):
    """人工审核记录列表序列化器"""
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    average_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ManualReviewRecord
        fields = ['id', 'reviewer', 'reviewer_name', 'decision', 'decision_display', 
                  'average_score', 'completed_at', 'created_at']


class ManualReviewRecordDetailSerializer(serializers.ModelSerializer):
    """人工审核记录详情序列化器"""
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    average_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ManualReviewRecord
        fields = ['id', 'task', 'reviewer', 'reviewer_name', 'decision', 'decision_display',
                  'overall_comment', 'content_quality_score', 'accuracy_score', 
                  'completeness_score', 'formatting_score', 'language_score', 'average_score',
                  'content_issues', 'format_issues', 'suggestions', 'started_at', 
                  'completed_at', 'review_duration', 'created_at', 'updated_at']
        read_only_fields = ['task', 'reviewer', 'started_at', 'completed_at', 'review_duration']


class ManualReviewCreateSerializer(serializers.ModelSerializer):
    """创建人工审核记录序列化器"""
    
    class Meta:
        model = ManualReviewRecord
        fields = ['decision', 'overall_comment', 'content_quality_score', 'accuracy_score',
                  'completeness_score', 'formatting_score', 'language_score', 
                  'content_issues', 'format_issues', 'suggestions']
    
    def validate(self, data):
        scores = ['content_quality_score', 'accuracy_score', 'completeness_score', 
                  'formatting_score', 'language_score']
        for score_field in scores:
            score = data.get(score_field)
            if score is not None and (score < 1 or score > 5):
                raise serializers.ValidationError({score_field: '评分必须在1-5之间'})
        return data


class AIReviewRecordSerializer(serializers.ModelSerializer):
    """AI审核记录序列化器"""
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = AIReviewRecord
        fields = ['id', 'task', 'overall_score', 'risk_level', 'risk_level_display',
                  'content_compliance_score', 'accuracy_score', 'completeness_score',
                  'readability_score', 'detected_issues', 'risk_items', 'suggestions',
                  'model_version', 'processing_time', 'status', 'error_message', 
                  'created_at', 'updated_at']
        read_only_fields = ['task', 'created_at', 'updated_at']


class WorkflowLogSerializer(serializers.ModelSerializer):
    """审核流程日志序列化器"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    actor_type_display = serializers.CharField(source='get_actor_type_display', read_only=True)
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    
    class Meta:
        model = WorkflowLog
        fields = ['id', 'task', 'action', 'action_display', 'actor', 'actor_name',
                  'actor_type', 'actor_type_display', 'from_status', 'to_status',
                  'comment', 'extra_data', 'created_at']


class ReviewRuleConfigSerializer(serializers.ModelSerializer):
    """审核规则配置序列化器"""
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)
    
    class Meta:
        model = ReviewRuleConfig
        fields = ['id', 'rule_name', 'rule_type', 'rule_type_display', 'description',
                  'rule_config', 'is_active', 'priority', 'created_at', 'updated_at']


class TaskStatsSerializer(serializers.Serializer):
    """任务统计序列化器"""
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    in_review = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
    today_reviewed = serializers.IntegerField()
    my_pending = serializers.IntegerField()
    my_completed = serializers.IntegerField()


class BookEditHistorySerializer(serializers.ModelSerializer):
    """教材修改历史序列化器"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = BookEditHistory
        fields = ['id', 'book_id', 'book_title', 'action', 'action_display',
                  'actor_name', 'actor_username', 'actor_employee_id', 'actor_department',
                  'version_number', 'previous_version', 'changes_summary', 'created_at']


class TeacherProfileSerializer(serializers.ModelSerializer):
    """教师档案序列化器"""
    
    class Meta:
        model = TeacherProfile
        fields = ['id', 'employee_id', 'name', 'department', 'title', 'email', 'phone',
                  'office_location', 'teaching_subjects', 'research_areas',
                  'total_uploaded_books', 'total_modified_books', 'approved_books',
                  'rejected_books', 'is_active', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    """教材列表序列化器（审核端）"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tag_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'subtitle', 'author', 'cover', 'description',
                  'status', 'status_display', 'current_version', 'total_chapters',
                  'word_count', 'language', 'isbn', 'created_at', 'updated_at',
                  'tag_list']
    
    def get_tag_list(self, obj):
        """获取标签列表"""
        try:
            tags = obj.tags
            if tags:
                import json
                return json.loads(tags)
            return []
        except:
            return []


class BookDetailSerializer(serializers.ModelSerializer):
    """教材详情序列化器（审核端）"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tag_list = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'subtitle', 'author', 'cover', 'description',
                  'status', 'status_display', 'current_version', 'total_chapters',
                  'word_count', 'language', 'isbn', 'created_at', 'updated_at',
                  'tag_list', 'category', 'introduction']
    
    def get_tag_list(self, obj):
        """获取标签列表"""
        try:
            tags = obj.tags
            if tags:
                import json
                return json.loads(tags)
            return []
        except:
            return []
    
    def get_category(self, obj):
        """获取分类名称"""
        try:
            categories = obj.categories.all()
            if categories.exists():
                return categories.first().name
            return None
        except:
            return None


class BookVersionSerializer(serializers.ModelSerializer):
    """教材版本序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = BookVersion
        fields = ['id', 'version_number', 'title', 'subtitle', 'author',
                  'description', 'created_at', 'created_by', 'created_by_name',
                  'comment', 'is_branch']
