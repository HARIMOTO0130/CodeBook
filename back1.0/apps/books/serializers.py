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
    # 添加merged_content字段
    merged_content = serializers.JSONField(default=dict, allow_null=True)
    # 添加层级关系字段
    is_main_chapter = serializers.BooleanField(default=True)
    parent_chapter = serializers.PrimaryKeyRelatedField(read_only=True)
    sub_chapters = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'type', 'duration', 'description', 'content', 'code', 'language', 'video_url', 'has_practice', 'merged_content', 'is_main_chapter', 'parent_chapter', 'sub_chapters')
    
    def get_has_practice(self, obj):
        # 通过检查是否有关联的practices来判断
        return hasattr(obj, 'practices') and obj.practices.exists()


class ChapterSummarySerializer(serializers.ModelSerializer):
    """章节摘要序列化器（用于书籍详情中展示章节列表）"""
    # 添加层级关系字段
    is_main_chapter = serializers.BooleanField(default=True)
    parent_chapter = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'type', 'duration', 'description', 'is_main_chapter', 'parent_chapter')


class ChapterDetailSerializer(serializers.ModelSerializer):
    """章节详情序列化器（用于单独获取章节内容时）"""
    # 不再直接包含practice字段，练习应该通过 /practice/ API 单独获取
    # practice = PracticeSerializer(read_only=True)
    
    # 添加子章节信息
    sub_chapters = ChapterSummarySerializer(many=True, read_only=True)
    
    # 确保content字段总是被返回，即使为空
    content = serializers.CharField(default='', allow_blank=True)
    content_type = serializers.CharField(default='markdown', allow_blank=True)
    jupyter_content = serializers.JSONField(default=dict, allow_null=True)
    # 优先使用merged_content字段，它包含了所有内容的统一表示
    merged_content = serializers.JSONField(default=dict, allow_null=True)
    # 添加层级关系字段
    is_main_chapter = serializers.BooleanField(default=True)
    parent_chapter = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'type', 'duration', 'description', 'content', 'content_type', 'jupyter_content', 'code', 'language', 'video_url', 'merged_content', 'sub_chapters', 'is_main_chapter', 'parent_chapter')


class BookListSerializer(serializers.ModelSerializer):
    """书籍列表序列化器"""
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'cover', 'pdf_file', 'description', 'tag_list', 'chapter_count', 'progress', 'last_learn_time', 'owner')
    
    # 添加动态字段
    progress = serializers.SerializerMethodField()
    last_learn_time = serializers.SerializerMethodField()
    
    def get_progress(self, obj):
        # 这个字段将在视图中根据用户学习记录计算
        return None
    
    def get_last_learn_time(self, obj):
        # 这个字段将在视图中根据用户学习记录计算
        return None

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
    class Meta:
        model = BookCategory
        fields = ('id', 'name', 'slug', 'parent', 'description', 'order', 'created_at', 'updated_at')


class BookTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookTag
        fields = ('id', 'name', 'description', 'created_at')


class BookVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookVersion
        fields = (
            'id',
            'book',
            'version_number',
            'title',
            'author',
            'description',
            'pdf_file',
            'tags',
            'created_at',
            'created_by',
            'comment',
            'is_branch',
            'parent_version',
        )
        read_only_fields = ('created_at', 'created_by')


class ChapterVersionSerializer(serializers.ModelSerializer):
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
            'comment',
        )
        read_only_fields = ('created_at', 'created_by')


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