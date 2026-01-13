"""书籍URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
import tempfile
import os
import json

from .views import (
    BookViewSet,
    ChapterViewSet,
    BookCategoryViewSet,
    BookTagViewSet,
    BookVersionViewSet,
    ChapterVersionViewSet,
    ChapterMediaViewSet,
    BookReviewViewSet,
)
from .docx_processor import process_docx
from .models import Book, Chapter

router = DefaultRouter()

# 教材提供者端接口（通过 /api/provider/books/* 访问）
router.register(r'categories', BookCategoryViewSet, basename='book-category')
router.register(r'tags', BookTagViewSet, basename='book-tag')
router.register(r'versions', BookVersionViewSet, basename='book-version')
router.register(r'chapter-versions', ChapterVersionViewSet, basename='chapter-version')
router.register(r'media', ChapterMediaViewSet, basename='chapter-media')
router.register(r'reviews', BookReviewViewSet, basename='book-review')

# 学生端/公共接口 - 最后注册以避免路由冲突
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'', BookViewSet, basename='book')

# 确保Chapter模型在视图类中可用
from .models import Chapter

# 创建独立的DOCX导入视图类
class SimpleDocxImportView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """DOCX导入视图，包含完整的文档解析和内容填充逻辑"""
        try:
            # 检查是否有上传的文件
            if 'file' not in request.FILES:
                return Response(
                    {'detail': '未提供.docx文件'},
                    status=400
                )
            
            # 获取上传的文件
            docx_file = request.FILES['file']
            
            # 获取章节数量限制
            try:
                chapter_limit = int(request.data.get('chapter_count', 0))
            except ValueError:
                chapter_limit = 0  # 0表示导入所有章节
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                tmp.write(docx_file.read())
                tmp_path = tmp.name
            
            # 创建临时图片目录
            image_temp_dir = tempfile.mkdtemp()
            
            try:
                # 处理.docx文件，提取图片
                print(f"开始处理.docx文件: {tmp_path}")
                docx_result = process_docx(tmp_path, image_output_dir=image_temp_dir)
                
                # 获取教材信息
                title = request.data.get('title', '导入的教材')
                description = request.data.get('description', '')
                author = request.data.get('author', '匿名用户')
                
                # 创建教材
                book = Book.objects.create(
                    title=title,
                    description=description,
                    author=author,
                    owner=None  # 匿名用户，owner设置为None
                )
                
                # 获取要导入的章节（优先使用实际章节）
                if docx_result['chapters']:
                    # 使用实际章节
                    chapters_to_import = docx_result['chapters']
                else:
                    # 如果没有实际章节，使用匹配后的章节
                    chapters_to_import = docx_result['matched_chapters']
                
                # 如果有章节数量限制，截取指定数量的章节
                if chapter_limit > 0:
                    chapters_to_import = chapters_to_import[:chapter_limit]
                
                # 创建章节
                created_chapters = []
                for i, chapter in enumerate(chapters_to_import):
                    # 创建章节对象
                    chapter_obj = Chapter.objects.create(
                        book=book,
                        title=chapter['title'],
                        description=f"章节 {i+1}: {chapter['title']}",
                        content=chapter['content'],
                        content_type='jupyter',
                        order=i+1,
                        level=chapter.get('level', 1),
                        language='python'
                    )
                    
                    # 使用ContentConverter将Markdown内容转换为Jupyter格式
                    from apps.books.content_converter import ContentConverter
                    converter = ContentConverter()
                    jupyter_data = converter.markdown_to_jupyter(chapter['content'])
                    
                    # 更新章节的Jupyter相关字段
                    chapter_obj.jupyter_content = json.dumps(jupyter_data)
                    chapter_obj.save()
                    
                    created_chapters.append(chapter_obj)
                
                # 处理图片（保存到media目录并更新引用）
                if docx_result['images']:
                    from django.conf import settings
                    import shutil
                    import uuid
                    import re
                    
                    # 保存所有图片的URL
                    image_urls = []
                    
                    for image_info in docx_result['images']:
                        # 生成唯一文件名
                        unique_filename = f"{uuid.uuid4()}_{image_info['filename']}"
                        image_path = os.path.join('book_images', str(book.id), unique_filename)
                        
                        # 创建目标目录
                        media_image_dir = os.path.join(settings.MEDIA_ROOT, 'book_images', str(book.id))
                        if not os.path.exists(media_image_dir):
                            os.makedirs(media_image_dir)
                        
                        # 复制图片到media目录
                        source_path = image_info['path']
                        dest_path = os.path.join(media_image_dir, unique_filename)
                        shutil.copy2(source_path, dest_path)
                        
                        # 获取图片的完整URL路径，使用绝对URL以确保可访问性
                        image_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{image_path}"
                        image_urls.append(image_url)
                    
                    # 更新所有章节内容中的图片引用
                    for chapter_obj in created_chapters:
                        # 重新加载章节内容
                        chapter_obj.refresh_from_db()
                        content = chapter_obj.content
                        merged_content = None
                        
                        # 尝试解析merged_content
                        try:
                            merged_content = json.loads(chapter_obj.merged_content)
                        except json.JSONDecodeError:
                            pass
                        
                        # 查找内容中的所有图片引用，包括IMAGE_MARKER和markdown图片格式
                        # 首先查找IMAGE_MARKER格式
                        image_markers = re.findall(r'\[IMAGE_MARKER_[\w\d]+\]', content)
                        
                        # 逐个替换图片引用
                        replacement_index = 0
                        
                        # 先替换IMAGE_MARKER格式
                        for marker in image_markers:
                            if replacement_index < len(image_urls):
                                # 使用后端实际生成的完整URL替换
                                content = content.replace(marker, f"![图片]({image_urls[replacement_index]})")
                                replacement_index += 1
                        
                        # 然后替换所有可能的图片引用格式，包括原始的image_xxx.png格式
                        for i in range(replacement_index, len(image_urls)):
                            image_url = image_urls[i]
                            # 提取图片文件名
                            image_filename = image_url.split('/')[-1]
                            # 提取核心图片ID
                            image_id_match = re.search(r'image_(\d+_[0-9a-f]+)\.png', image_filename)
                            if image_id_match:
                                image_id = image_id_match.group(1)
                                # 替换所有包含这个图片ID的引用
                                content = content.replace(f"(image_{image_id}.png)", f"({image_url})")
                        
                        # 保存更新后的内容
                        chapter_obj.content = content
                        
                        # 更新merged_content中的图片引用
                        if merged_content and isinstance(merged_content, dict) and 'cells' in merged_content:
                            for cell in merged_content['cells']:
                                if 'source' in cell:
                                    new_source = []
                                    for line in cell['source']:
                                        updated_line = line
                                        for i, marker in enumerate(image_markers):
                                            if i < len(image_urls):
                                                new_url = image_urls[i]
                                                updated_line = updated_line.replace(marker, f"![图片]({new_url})")
                                        new_source.append(updated_line)
                                    cell['source'] = new_source
                            
                            # 保存更新后的合并内容
                            chapter_obj.merged_content = json.dumps(merged_content)
                        
                        chapter_obj.save()
                
                # 更新教材章节数
                book.chapter_count = len(created_chapters)
                book.total_chapters = len(chapters_to_import)
                book.save()
                
                return Response({
                    'status': 'success',
                    'message': 'DOCX文件导入成功，内容已解析',
                    'book_id': book.id,
                    'title': book.title,
                    'chapter_count': book.chapter_count,
                    'imported_chapters': [ch.title for ch in created_chapters]
                }, status=201)
                
            finally:
                # 清理临时文件
                os.unlink(tmp_path)
                for file in os.listdir(image_temp_dir):
                    os.unlink(os.path.join(image_temp_dir, file))
                os.rmdir(image_temp_dir)
                
        except Exception as e:
            print(f"导入DOCX文件时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'detail': f'导入失败: {str(e)}'},
                status=500
            )


urlpatterns = [
    # 添加独立的DOCX导入URL，放在最前面以避免被其他路由覆盖
    path('upload-docx/', SimpleDocxImportView.as_view(), name='import_docx_simple'),
    path('', include(router.urls)),
    path('chapters/book/<int:book_id>/', ChapterViewSet.as_view({'get': 'by_book'})),
]