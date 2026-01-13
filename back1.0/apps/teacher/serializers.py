from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import models
from .models import (
    Class, Student, StudentClass, StudentLearningProgress, Homework, StudentHomework, StudentHomeworkFile,
    Notice, StudentNoticeRead, ClassResource, TeachingResource,
    CourseDesign, TeacherSetting, Report
)
from apps.books.models import Book, Chapter

User = get_user_model()


class BookSimpleSerializer(serializers.ModelSerializer):
    """教材简单序列化器"""
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover']


class ChapterSimpleSerializer(serializers.ModelSerializer):
    """章节简单序列化器"""
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'level']


class StudentSerializer(serializers.ModelSerializer):
    """学生序列化器"""
    class_name = serializers.CharField(read_only=True)
    progress = serializers.SerializerMethodField()
    avg_score = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()
    completed_assignments = serializers.SerializerMethodField()
    total_assignments = serializers.SerializerMethodField()
    last_learn_time = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    # 从关联的User对象获取学生姓名，确保始终显示最新的昵称或用户名
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_no', 'student_name', 'gender', 'phone',
            'class_name', 'status', 'created_at', 'updated_at',
            'progress', 'avg_score', 'submission_count', 'completed_assignments',
            'total_assignments', 'last_learn_time'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """从关联的User对象获取学生姓名，优先使用昵称"""
        try:
            if obj.user:
                # 如果有关联的User对象，优先使用昵称，否则使用用户名
                return obj.user.nickname or obj.user.username
        except AttributeError:
            # 如果没有user属性或访问出错，使用Student模型本身的student_name字段
            pass
        # 如果以上都没有，返回Student模型的student_name字段或默认值
        return obj.student_name or '未知学生'
    
    def get_gender(self, obj):
        """将性别转换为整数，处理字符串值"""
        gender = obj.gender
        if isinstance(gender, str):
            # 如果是字符串，转换为对应的整数
            gender_map = {'男': 1, '女': 2, '未知': 0}
            return gender_map.get(gender, 0)
        elif isinstance(gender, int):
            # 如果是整数，直接返回
            return gender
        else:
            # 其他情况返回0
            return 0
    
    def get_progress(self, obj):
        """计算学生学习进度"""
        from django.db.models import Q
        from .models import StudentLearningProgress
        
        total_records = StudentLearningProgress.objects.filter(student=obj).count()
        if total_records == 0:
            return 0
        
        completed_count = StudentLearningProgress.objects.filter(
            student=obj, learn_status=3
        ).count()
        
        return round((completed_count / total_records) * 100)
    
    def get_avg_score(self, obj):
        """计算学生平均成绩"""
        from .models import StudentHomework
        
        submissions = StudentHomework.objects.filter(
            student=obj, score__isnull=False
        )
        
        if not submissions.exists():
            return 0
        
        return round(submissions.aggregate(avg_score=models.Avg('score'))['avg_score'])
    
    def get_submission_count(self, obj):
        """获取学生作业提交总数"""
        from .models import StudentHomework
        return StudentHomework.objects.filter(student=obj).count()
    
    def get_completed_assignments(self, obj):
        """获取学生已完成作业数"""
        from .models import StudentHomework
        return StudentHomework.objects.filter(
            student=obj, status__gte=3
        ).count()
    
    def get_total_assignments(self, obj):
        """获取学生总作业数"""
        from .models import StudentHomework
        return StudentHomework.objects.filter(student=obj).count()
    
    def get_last_learn_time(self, obj):
        """获取学生最后学习时间"""
        from .models import StudentLearningProgress
        
        last_progress = StudentLearningProgress.objects.filter(
            student=obj
        ).order_by('-last_learn_time').first()
        
        if last_progress:
            return last_progress.last_learn_time
        return obj.updated_at


class ClassSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    # 用于写入操作的教材ID
    book_id = serializers.PrimaryKeyRelatedField(source='book', queryset=Book.objects.all(), required=False, allow_null=True, write_only=True)
    # 用于读取操作的详细教材信息
    book = BookSimpleSerializer(read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'teacher', 'teacher_name', 'book', 'book_id', 'book_title',
            'major', 'grade', 'description', 'status', 'student_count', 'course_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at', 'course_code']
    
    def validate(self, data):
        """验证数据，确保不会违反unique_together约束"""
        try:
            # 获取当前教师
            teacher = self.context['request'].user.teacher_profile
            # 获取当前要更新的班级实例
            instance = self.instance
            # 获取要设置的book
            book = data.get('book')
            
            # 如果没有提供book，使用当前实例的book（如果存在）
            if not book and instance:
                book = instance.book
            
            # 只有当提供了book或者当前实例有book时才进行验证
            if book:
                # 查找相同教师和教材的班级
                existing_classes = Class.objects.filter(teacher=teacher, book=book)
                if instance:
                    # 如果是更新操作，排除当前实例
                    existing_classes = existing_classes.exclude(id=instance.id)
                
                if existing_classes.exists():
                    raise serializers.ValidationError({'book': '您已经创建了使用该教材的班级，请选择其他教材'})
        except Exception as e:
            # 如果验证过程中出现任何错误，记录错误但不阻止更新
            print(f"验证班级数据时出现错误: {e}")
        
        return data


class StudentClassSerializer(serializers.ModelSerializer):
    """学生班级关系序列化器"""
    class_obj = ClassSerializer(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_obj', queryset=Class.objects.all(), write_only=True)
    
    class Meta:
        model = StudentClass
        fields = ['id', 'student', 'class_obj', 'class_id', 'is_active', 'joined_at']
        read_only_fields = ['id', 'student', 'joined_at']


class ReportSerializer(serializers.ModelSerializer):
    """报告序列化器"""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    student_name = serializers.SerializerMethodField(read_only=True)
    student_no = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'class_obj', 'class_name', 'student', 
            'student_name', 'student_no', 'start_date', 'end_date', 
            'include_progress', 'include_homework', 'include_attendance', 
            'include_performance', 'export_format', 'report_data', 'file_path', 
            'status', 'generated_at', 'updated_at'
        ]
        read_only_fields = ['id', 'generated_at', 'updated_at']
    
    def get_student_name(self, obj):
        if obj.student:
            return obj.student.student_name
        return ''
    
    def get_student_no(self, obj):
        if obj.student:
            return obj.student.student_no
        return ''


class ClassDetailSerializer(serializers.ModelSerializer):
    """班级详情序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    book = BookSimpleSerializer(read_only=True)
    students = serializers.SerializerMethodField()
    student_count = serializers.IntegerField(read_only=True)
    
    def get_students(self, obj):
        """获取班级学生"""
        students = Student.objects.filter(student_classes__class_obj=obj, student_classes__is_active=True)
        return StudentSerializer(students, many=True).data
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'teacher', 'teacher_name', 'book',
            'major', 'grade', 'description', 'status', 'students',
            'student_count', 'course_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']


class StudentLearningProgressSerializer(serializers.ModelSerializer):
    """学生学习进度序列化器"""
    student_name = serializers.CharField(source='student.student_name', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    
    class Meta:
        model = StudentLearningProgress
        fields = [
            'id', 'student', 'student_name', 'chapter', 'chapter_title',
            'teacher', 'learn_time', 'learn_status', 'last_learn_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']


class HomeworkSerializer(serializers.ModelSerializer):
    """作业序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    submission_count = serializers.SerializerMethodField()
    # 添加字段别名以兼容前端
    title = serializers.CharField(source='homework_name', read_only=True)
    due_date = serializers.DateTimeField(source='end_time', read_only=True)
    
    class Meta:
        model = Homework
        fields = [
            'id', 'homework_name', 'title', 'teacher', 'teacher_name',
            'class_obj', 'class_name', 'chapter', 'chapter_title',
            'homework_content', 'start_time', 'end_time', 'due_date', 'total_score',
            'status', 'submission_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()


class StudentHomeworkFileSerializer(serializers.ModelSerializer):
    """学生作业文件序列化器"""
    file_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StudentHomeworkFile
        fields = [
            'id', 'file_name', 'file_path', 'file_url', 'file_size', 'mime_type',
            'upload_status', 'upload_time'
        ]
        read_only_fields = ['id', 'file_url', 'upload_time', 'file_path', 'file_size', 'mime_type']
    
    def get_file_url(self, obj):
        """生成文件下载URL"""
        from django.conf import settings
        return f"{settings.MEDIA_URL}{obj.file_path}"


class StudentHomeworkSerializer(serializers.ModelSerializer):
    """学生作业提交序列化器"""
    student_name = serializers.SerializerMethodField(read_only=True)
    student_no = serializers.SerializerMethodField(read_only=True)
    homework_name = serializers.SerializerMethodField(read_only=True)
    files = StudentHomeworkFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentHomework
        fields = [
            'id', 'homework', 'homework_name', 'student', 'student_name', 'student_no',
            'submit_content', 'score', 'feedback', 'submit_time', 'grade_time', 'status', 'files'
        ]
        read_only_fields = ['id', 'submit_time', 'grade_time', 'files']
    
    def get_student_name(self, obj):
        """安全获取学生姓名"""
        try:
            return obj.student.student_name if obj.student else '未知学生'
        except AttributeError:
            return '未知学生'
    
    def get_student_no(self, obj):
        """安全获取学号"""
        try:
            return obj.student.student_no if obj.student else '未知学号'
        except AttributeError:
            return '未知学号'
    
    def get_homework_name(self, obj):
        """安全获取作业名称"""
        try:
            return obj.homework.homework_name if obj.homework else '未知作业'
        except AttributeError:
            return '未知作业'


class NoticeSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True, allow_null=True)
    
    # 确保is_important和type字段有默认值
    type = serializers.ChoiceField(choices=Notice.NOTICE_TYPE_CHOICES, default='announcement')
    is_important = serializers.BooleanField(default=False)
    
    class Meta:
        model = Notice
        fields = [
            'id', 'teacher', 'teacher_name', 'class_obj', 'class_name',
            'notice_title', 'notice_content', 'type', 'is_important', 'publish_time', 'expire_time',
            'read_count', 'status'
        ]
        read_only_fields = ['id', 'teacher', 'publish_time', 'read_count']


class StudentNoticeReadSerializer(serializers.ModelSerializer):
    """学生通知阅读记录序列化器"""
    student_name = serializers.CharField(source='student.student_name', read_only=True)
    notice_title = serializers.CharField(source='notice.notice_title', read_only=True)
    
    class Meta:
        model = StudentNoticeRead
        fields = [
            'id', 'notice', 'notice_title', 'student', 'student_name',
            'read_time', 'is_read'
        ]
        read_only_fields = ['id']


class ClassResourceSerializer(serializers.ModelSerializer):
    """班级资源序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    
    class Meta:
        model = ClassResource
        fields = [
            'id', 'class_obj', 'class_name', 'teacher', 'teacher_name',
            'resource_name', 'resource_type', 'resource_url', 'upload_time',
            'download_count', 'resource_desc',
            'file_size', 'file_hash', 'upload_status', 'storage_path',
            'mime_type', 'upload_ip', 'retry_count'
        ]
        read_only_fields = [
            'id', 'teacher', 'upload_time', 'download_count',
            'file_hash', 'upload_status', 'storage_path', 'mime_type',
            'upload_ip', 'retry_count'
        ]


class TeachingResourceSerializer(serializers.ModelSerializer):
    """教学资源序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    
    # 明确字段定义，确保验证正确
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    file = serializers.CharField(required=True, allow_blank=False)
    resource_type = serializers.CharField(max_length=20, required=True)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    is_public = serializers.BooleanField(required=False, default=True)
    file_size = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    # 将teacher字段标记为read_only，因为我们会在save时自动设置它
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = TeachingResource
        fields = [
            'id', 'title', 'description', 'file', 'resource_type', 'category',
            'is_public', 'file_size', 'created_at', 'updated_at',
            'teacher', 'teacher_name',
            'file_hash', 'upload_status', 'storage_path',
            'mime_type', 'upload_ip', 'retry_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'teacher', 'file_hash', 'upload_status', 'storage_path',
            'mime_type', 'upload_ip', 'retry_count'
        ]
    
    def validate_resource_type(self, value):
        """验证资源类型"""
        if not value:
            return 'other'
        # 确保resource_type长度不超过20
        if len(value) > 20:
            return value[:20]
        return value
    
    def validate_category(self, value):
        """验证分类"""
        if value == '' or value is None:
            return None
        # 确保category长度不超过100
        if len(value) > 100:
            return value[:100]
        return value
    
    def validate_file_size(self, value):
        """验证文件大小"""
        if value is None:
            return None
        # 确保是整数类型
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


class CourseDesignSerializer(serializers.ModelSerializer):
    """课程设计序列化器"""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    
    class Meta:
        model = CourseDesign
        fields = [
            'id', 'class_obj', 'class_name', 'chapter', 'chapter_title',
            'teacher', 'teacher_name', 'design_title', 'design_content',
            'teaching_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']


class TeacherSettingSerializer(serializers.ModelSerializer):
    """教师设置序列化器"""
    class Meta:
        model = TeacherSetting
        fields = [
            'id', 'teacher', 'setting_key', 'setting_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']


# TeachingToolLogSerializer类已暂时移除，因为TeachingToolLog模型已被移除


class TeacherInfoSerializer(serializers.ModelSerializer):
    """教师信息序列化器"""
    # User模型的基本字段
    # Teacher模型的字段通过重写to_representation方法包含
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def to_representation(self, instance):
        """扩展返回数据，包含Teacher模型的字段"""
        data = super().to_representation(instance)
        
        # 确保avatar字段返回完整的URL
        if instance.avatar:
            try:
                # 处理ImageFieldFile对象
                avatar_value = str(instance.avatar)  # 转换为字符串
                
                # 如果User模型的avatar字段已经是完整URL，直接使用
                if isinstance(avatar_value, str) and avatar_value.startswith(('http://', 'https://')):
                    data['avatar'] = avatar_value
                else:
                    # 如果不是完整URL，尝试生成完整URL
                    try:
                        from django.conf import settings
                        # 检查request上下文是否存在
                        if self.context and self.context.get('request'):
                            request = self.context['request']
                            base_url = f'https://{request.get_host()}' if request.is_secure() else f'http://{request.get_host()}'
                            data['avatar'] = f'{base_url}{settings.MEDIA_URL}{avatar_value}'
                        else:
                            # 如果没有request上下文，直接返回相对路径
                            data['avatar'] = avatar_value
                    except Exception as e:
                        # 如果生成完整URL失败，直接返回相对路径
                        data['avatar'] = avatar_value
            except Exception as e:
                # 如果处理avatar失败，返回默认值
                data['avatar'] = str(instance.avatar) if instance.avatar else ''
        
        # 尝试获取Teacher实例
        try:
            teacher = instance.teacher_profile
            
            # 添加Teacher模型的字段，确保返回空字符串而不是None，以便前端正确显示
            data['phone'] = teacher.phone or ''
            data['department'] = teacher.department or ''
            data['title'] = teacher.position or ''  # 前端使用title，后端使用position
            data['bio'] = teacher.introduction or ''  # 前端使用bio，后端使用introduction
            data['teacher_number'] = teacher.teacher_number or ''  # 教师编号
        except AttributeError:
            # 如果没有Teacher实例，添加空字符串默认值
            data['phone'] = ''
            data['department'] = ''
            data['title'] = ''
            data['bio'] = ''
            data['teacher_number'] = ''
        
        return data
