"""文件上传工具类"""
import hashlib
import mimetypes
import os
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FileUploadValidator:
    """文件上传验证器"""
    
    # 文件类型白名单
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    ALLOWED_DOCUMENT_TYPES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'text/plain',
        'text/markdown',
        'application/epub+zip',
    ]
    ALLOWED_VIDEO_TYPES = [
        'video/mp4',
        'video/avi',
        'video/quicktime',
        'video/x-msvideo',
        'video/webm',
    ]
    ALLOWED_AUDIO_TYPES = [
        'audio/mpeg',
        'audio/wav',
        'audio/ogg',
        'audio/mp4',
    ]
    
    # 文件大小限制（字节）
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DOCUMENT_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.md', '.epub'],
        'video': ['.mp4', '.avi', '.mov', '.webm'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
    }
    
    @classmethod
    def validate_file_type(cls, file: UploadedFile, resource_type: str = None) -> tuple[bool, str]:
        """
        验证文件类型
        
        Args:
            file: 上传的文件对象
            resource_type: 资源类型（image/document/video/audio）
            
        Returns:
            (is_valid, error_message)
        """
        # 获取文件MIME类型
        mime_type = file.content_type or mimetypes.guess_type(file.name)[0]
        
        # 获取文件扩展名
        ext = os.path.splitext(file.name)[1].lower()
        
        # 根据资源类型验证
        if resource_type == 'image':
            if mime_type not in cls.ALLOWED_IMAGE_TYPES:
                return False, f'不支持图片格式: {mime_type}，支持的格式: {", ".join(cls.ALLOWED_IMAGE_TYPES)}'
            if ext not in cls.ALLOWED_EXTENSIONS['image']:
                return False, f'不支持图片扩展名: {ext}'
        elif resource_type == 'document':
            if mime_type not in cls.ALLOWED_DOCUMENT_TYPES:
                return False, f'不支持文档格式: {mime_type}'
            if ext not in cls.ALLOWED_EXTENSIONS['document']:
                return False, f'不支持文档扩展名: {ext}'
        elif resource_type == 'video':
            if mime_type not in cls.ALLOWED_VIDEO_TYPES:
                return False, f'不支持视频格式: {mime_type}'
            if ext not in cls.ALLOWED_EXTENSIONS['video']:
                return False, f'不支持视频扩展名: {ext}'
        elif resource_type == 'audio':
            if mime_type not in cls.ALLOWED_AUDIO_TYPES:
                return False, f'不支持音频格式: {mime_type}'
            if ext not in cls.ALLOWED_EXTENSIONS['audio']:
                return False, f'不支持音频扩展名: {ext}'
        else:
            # 通用验证：检查是否在任一允许列表中
            all_allowed = (
                cls.ALLOWED_IMAGE_TYPES +
                cls.ALLOWED_DOCUMENT_TYPES +
                cls.ALLOWED_VIDEO_TYPES +
                cls.ALLOWED_AUDIO_TYPES
            )
            if mime_type not in all_allowed:
                return False, f'不支持的文件类型: {mime_type}'
        
        return True, ''
    
    @classmethod
    def validate_file_size(cls, file: UploadedFile, resource_type: str = None) -> tuple[bool, str]:
        """
        验证文件大小
        
        Args:
            file: 上传的文件对象
            resource_type: 资源类型
            
        Returns:
            (is_valid, error_message)
        """
        file_size = file.size
        
        # 根据资源类型设置不同的限制
        if resource_type == 'image':
            max_size = cls.MAX_IMAGE_SIZE
            max_size_mb = max_size / (1024 * 1024)
        elif resource_type == 'document':
            max_size = cls.MAX_DOCUMENT_SIZE
            max_size_mb = max_size / (1024 * 1024)
        elif resource_type == 'video':
            max_size = cls.MAX_VIDEO_SIZE
            max_size_mb = max_size / (1024 * 1024)
        else:
            max_size = cls.MAX_FILE_SIZE
            max_size_mb = max_size / (1024 * 1024)
        
        if file_size > max_size:
            file_size_mb = file_size / (1024 * 1024)
            return False, f'文件大小 {file_size_mb:.2f}MB 超过限制 {max_size_mb:.0f}MB'
        
        return True, ''
    
    @classmethod
    def validate(cls, file: UploadedFile, resource_type: str = None) -> tuple[bool, str]:
        """
        综合验证文件
        
        Args:
            file: 上传的文件对象
            resource_type: 资源类型
            
        Returns:
            (is_valid, error_message)
        """
        # 验证文件类型
        is_valid, error = cls.validate_file_type(file, resource_type)
        if not is_valid:
            return False, error
        
        # 验证文件大小
        is_valid, error = cls.validate_file_size(file, resource_type)
        if not is_valid:
            return False, error
        
        return True, ''


class FileHashCalculator:
    """文件哈希值计算器"""
    
    @staticmethod
    def calculate_md5(file: UploadedFile) -> str:
        """
        计算文件的MD5哈希值
        
        Args:
            file: 文件对象
            
        Returns:
            MD5哈希值（32位十六进制字符串）
        """
        md5_hash = hashlib.md5()
        file.seek(0)  # 确保从文件开头读取
        for chunk in file.chunks():
            md5_hash.update(chunk)
        file.seek(0)  # 重置文件指针
        return md5_hash.hexdigest()
    
    @staticmethod
    def calculate_sha256(file: UploadedFile) -> str:
        """
        计算文件的SHA256哈希值
        
        Args:
            file: 文件对象
            
        Returns:
            SHA256哈希值（64位十六进制字符串）
        """
        sha256_hash = hashlib.sha256()
        file.seek(0)
        for chunk in file.chunks():
            sha256_hash.update(chunk)
        file.seek(0)
        return sha256_hash.hexdigest()


class FileUploadHandler:
    """文件上传处理器"""
    
    def __init__(self, storage_path_prefix: str = 'uploads'):
        """
        初始化上传处理器
        
        Args:
            storage_path_prefix: 存储路径前缀
        """
        self.storage_path_prefix = storage_path_prefix
    
    def save_file(
        self,
        file: UploadedFile,
        subfolder: str = '',
        custom_filename: str = None,
        get_client_ip: callable = None
    ) -> dict:
        """
        保存文件并返回文件信息
        
        Args:
            file: 上传的文件对象
            subfolder: 子文件夹名称
            custom_filename: 自定义文件名（不含扩展名）
            get_client_ip: 获取客户端IP的函数
            
        Returns:
            包含文件信息的字典:
            {
                'file_path': 存储路径,
                'storage_path': 完整存储路径,
                'file_size': 文件大小,
                'file_hash': 文件哈希值,
                'mime_type': MIME类型,
                'upload_ip': 上传IP
            }
        """
        # 生成存储路径
        if custom_filename:
            filename = f"{custom_filename}{os.path.splitext(file.name)[1]}"
        else:
            filename = file.name
        
        # 构建完整路径
        if subfolder:
            storage_path = f'{self.storage_path_prefix}/{subfolder}/{filename}'
        else:
            storage_path = f'{self.storage_path_prefix}/{filename}'
        
        # 计算文件哈希值（在保存前计算，确保文件指针位置正确）
        file_hash = FileHashCalculator.calculate_md5(file)
        
        # 保存文件
        saved_path = default_storage.save(storage_path, file)
        
        # 获取完整存储路径
        full_storage_path = default_storage.path(saved_path) if hasattr(default_storage, 'path') else saved_path
        
        # 获取MIME类型
        mime_type = file.content_type or mimetypes.guess_type(file.name)[0]
        
        # 获取上传IP
        upload_ip = None
        if get_client_ip:
            try:
                upload_ip = get_client_ip()
            except Exception as e:
                logger.warning(f"Failed to get client IP: {e}")
        
        return {
            'file_path': saved_path,
            'storage_path': full_storage_path,
            'file_size': file.size,
            'file_hash': file_hash,
            'mime_type': mime_type,
            'upload_ip': upload_ip,
        }
    
    def check_duplicate(self, file_hash: str, model_class, hash_field: str = 'file_hash') -> object:
        """
        检查文件是否已存在（通过哈希值）
        
        Args:
            file_hash: 文件哈希值
            model_class: 模型类
            hash_field: 哈希值字段名
            
        Returns:
            如果存在返回模型实例，否则返回None
        """
        try:
            return model_class.objects.filter(**{hash_field: file_hash}).first()
        except Exception as e:
            logger.error(f"Error checking duplicate file: {e}")
            return None


def get_client_ip(request) -> str:
    """
    获取客户端IP地址
    
    Args:
        request: Django请求对象
        
    Returns:
        IP地址字符串
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

