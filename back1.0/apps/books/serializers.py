"""书籍序列化器"""
from rest_framework import serializers
from .models import (
    Book,
    Chapter,
    Practice,
    TestCase,
    PracticeChoiceOption,
    PracticeFillBlank,
    BookCategory,
    BookTag,
    BookVersion,
    ChapterVersion,
    ChapterMedia,
    BookReview,
)


class PracticeChoiceOptionSerializer(serializers.ModelSerializer):
    """选择题选项序列化器"""
    class Meta:
        model = PracticeChoiceOption
        fields = ('id', 'content', 'is_correct', 'order')


class PracticeFillBlankSerializer(serializers.ModelSerializer):
    """填空题空位序列化器"""
    class Meta:
        model = PracticeFillBlank
        fields = ('id', 'prompt', 'placeholder', 'correct_answer', 'order')


class TestCaseSerializer(serializers.ModelSerializer):
    """测试用例序列化器"""
    class Meta:
        model = TestCase
        fields = ('id', 'input_data', 'expected_output', 'order')


class PracticeSerializer(serializers.ModelSerializer):
    """练习题序列化器"""
    test_cases = TestCaseSerializer(many=True, read_only=True)
    choice_options = PracticeChoiceOptionSerializer(many=True, read_only=True)
    fill_blanks = PracticeFillBlankSerializer(many=True, read_only=True)
    
    class Meta:
        model = Practice
        fields = ('id', 'chapter', 'title', 'description', 'questions', 'language', 'difficulty', 
                  'order', 'created_at', 'updated_at', 'test_cases', 'choice_options', 'fill_blanks')
        read_only_fields = ('created_at', 'updated_at')


class PracticeDetailSerializer(serializers.ModelSerializer):
    """练习题详情序列化器（用于单独获取练习题详情）"""
    test_cases = TestCaseSerializer(many=True, read_only=True)
    choice_options = PracticeChoiceOptionSerializer(many=True, read_only=True)
    fill_blanks = PracticeFillBlankSerializer(many=True, read_only=True)
    
    class Meta:
        model = Practice
        fields = ('id', 'chapter', 'title', 'description', 'questions', 'language', 'difficulty', 
                  'order', 'created_at', 'updated_at', 'test_cases', 'choice_options', 'fill_blanks')
        read_only_fields = ('created_at', 'updated_at')


class ChapterSerializer(serializers.ModelSerializer):
    """章节序列化器（兼容性保留）"""
    # 不再直接包含practice字段，练习应该通过 /practice/ API 单独获取
    # practice = PracticeSerializer(read_only=True)
    has_practice = serializers.SerializerMethodField()
    # 添加merged_content字段 - 保持为CharField以避免双重JSON解析
    merged_content = serializers.CharField(default='', allow_null=True)
    # 添加层级关系字段
    is_main_chapter = serializers.BooleanField(default=True)
    parent_chapter = serializers.PrimaryKeyRelatedField(read_only=True)
    sub_chapters = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'type', 'duration', 'description', 'content', 'code', 'language', 'video_url', 'has_practice', 'merged_content', 'is_main_chapter', 'parent_chapter', 'sub_chapters', 'order')
    
    def get_has_practice(self, obj):
        # 通过检查是否有关联的practices来判断
        return hasattr(obj, 'practices') and obj.practices.exists()


class ChapterSummarySerializer(serializers.ModelSerializer):
    """章节摘要序列化器（用于书籍详情中展示章节列表）"""
    # 添加层级关系字段
    is_main_chapter = serializers.BooleanField(default=True)
    parent_chapter = serializers.PrimaryKeyRelatedField(read_only=True)
    # 添加merged_content字段，用于在书籍详情中展示章节内容
    merged_content = serializers.CharField(default='', allow_null=True)
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'type', 'duration', 'description', 'merged_content', 'is_main_chapter', 'parent_chapter')


class ChapterDetailSerializer(serializers.ModelSerializer):
    """章节详情序列化器（用于单独获取章节内容时）"""
    # 不再直接包含practice字段，练习应该通过 /practice/ API 单独获取
    # practice = PracticeSerializer(read_only=True)
    
    # 添加子章节信息
    sub_chapters = ChapterSummarySerializer(many=True, read_only=True)
    
    # 确保content字段总是被返回，即使为空
    content = serializers.CharField(default='', allow_blank=True)
    content_type = serializers.CharField(default='markdown', allow_blank=True)
    jupyter_content = serializers.CharField(default='', allow_null=True)
    # 优先使用merged_content字段，它包含了所有内容的统一表示 - 保持为CharField以避免双重JSON解析
    merged_content = serializers.CharField(default='', allow_null=True)
    # 添加层级关系字段
    is_main_chapter = serializers.BooleanField(default=True)
    parent_chapter = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'type', 'duration', 'description', 'content', 'content_type', 'jupyter_content', 'code', 'language', 'video_url', 'merged_content', 'sub_chapters', 'is_main_chapter', 'parent_chapter')


class BookListSerializer(serializers.ModelSerializer):
    """书籍列表序列化器"""
    owner = serializers.SerializerMethodField()
    # 直接定义为DateTimeField，不使用SerializerMethodField
    progress = serializers.IntegerField(default=0)
    last_learn_time = serializers.DateTimeField(allow_null=True)
    
    class Meta:
        model = Book
        fields = ('id', 'title', 'subtitle', 'author', 'cover', 'pdf_file', 'description', 'tag_list', 'chapter_count', 'progress', 'last_learn_time', 'owner')
    
    def get_owner(self, obj):
        return getattr(obj.owner, 'id', None)


class BookDetailSerializer(serializers.ModelSerializer):
    """书籍详情序列化器"""
    chapters = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    
    categories = serializers.SlugRelatedField(
        slug_field='name',
        many=True,
        read_only=True
    )
    tag_objects = serializers.SlugRelatedField(
        slug_field='name',
        many=True,
        read_only=True
    )

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'subtitle',
            'author',
            'cover',
            'pdf_file',
            'description',
            'tag_list',
            'categories',
            'tag_objects',
            'chapter_count',
            'chapters',
            'owner',
            'is_archived',
            'current_version',
        )

    def get_owner(self, obj):
        return getattr(obj.owner, 'id', None)
        
    def get_chapters(self, obj):
        """只返回非练习类型的章节"""
        # 排除practice类型的章节
        chapters = obj.chapters.filter(type__in=['reading', 'video']).order_by('order')
        serializer = ChapterSummarySerializer(chapters, many=True)
        return serializer.data


# ===== 教材提供者端相关序列化器 =====


class BookCategorySerializer(serializers.ModelSerializer):
    """教材分类序列化器"""
    book_count = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BookCategory
        fields = ('id', 'name', 'slug', 'parent', 'parent_name', 'description', 'order', 'book_count', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_book_count(self, obj):
        """获取该分类下的书籍数量"""
        return obj.books.filter(is_archived=False).count()
    
    def get_parent_name(self, obj):
        """获取父分类名称"""
        return obj.parent.name if obj.parent else None
    
    def validate_parent(self, value):
        """验证父分类不能是自己"""
        if self.instance and value and value.id == self.instance.id:
            raise serializers.ValidationError("分类不能将自己设为父分类")
        return value
    
    def validate_slug(self, value):
        """验证slug格式"""
        if not value:
            raise serializers.ValidationError("分类标识不能为空")
        # 检查slug是否只包含字母、数字、连字符和下划线
        import re
        if not re.match(r'^[a-z0-9_-]+$', value):
            raise serializers.ValidationError("分类标识只能包含小写字母、数字、连字符和下划线")
        return value


class BookTagSerializer(serializers.ModelSerializer):
    """教材标签序列化器"""
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BookTag
        fields = ('id', 'name', 'description', 'book_count', 'created_at')
        read_only_fields = ('created_at',)
    
    def get_book_count(self, obj):
        """获取该标签下的书籍数量"""
        return obj.books.filter(is_archived=False).count()
    
    def validate_name(self, value):
        """验证标签名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("标签名称不能为空")
        # 检查名称长度
        if len(value) > 50:
            raise serializers.ValidationError("标签名称不能超过50个字符")
        return value.strip()


class BookVersionSerializer(serializers.ModelSerializer):
    """书籍版本序列化器"""
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BookVersion
        fields = (
            'id',
            'book',
            'version_number',
            'title',
            'subtitle',
            'author',
            'description',
            'pdf_file',
            'tags',
            'created_at',
            'created_by',
            'created_by_name',
            'comment',
            'is_branch',
            'parent_version',
        )
        read_only_fields = ('created_at', 'created_by')
    
    def get_created_by_name(self, obj):
        """获取创建人名称"""
        if obj.created_by:
            return obj.created_by.username if hasattr(obj.created_by, 'username') else str(obj.created_by)
        return None


class ChapterVersionSerializer(serializers.ModelSerializer):
    """章节版本序列化器"""
    # 保持merged_content为CharField以避免双重JSON解析
    merged_content = serializers.CharField(default='', allow_null=True)
    jupyter_content = serializers.CharField(default='', allow_null=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChapterVersion
        fields = (
            'id',
            'chapter',
            'version_number',
            'title',
            'description',
            'content',
            'code',
            'jupyter_content',
            'merged_content',
            'language',
            'created_at',
            'created_by',
            'created_by_name',
            'comment',
        )
        read_only_fields = ('created_at', 'created_by')
    
    def get_created_by_name(self, obj):
        """获取创建人名称"""
        if obj.created_by:
            return obj.created_by.username if hasattr(obj.created_by, 'username') else str(obj.created_by)
        return None


class ChapterMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterMedia
        fields = (
            'id',
            'chapter',
            'media_type',
            'url',
            'file',
            'title',
            'description',
            'order',
            'created_at',
        )
        read_only_fields = ('created_at',)


class BookReviewSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username')

    class Meta:
        model = BookReview
        fields = (
            'id',
            'book',
            'book_title',
            'reviewer',
            'reviewer_name',
            'status',
            'comment',
            'created_at',
        )
        read_only_fields = ('created_at',)