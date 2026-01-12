# Generated migration for adding upload-related fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_classresource_coursedesign_homework_notice_student_and_more'),
    ]

    operations = [
        # Add fields to ClassResource
        migrations.AddField(
            model_name='classresource',
            name='file_size',
            field=models.BigIntegerField(default=0, verbose_name='文件大小（字节）', db_column='file_size'),
        ),
        migrations.AddField(
            model_name='classresource',
            name='file_hash',
            field=models.CharField(blank=True, help_text='MD5或SHA256哈希值', max_length=64, null=True, verbose_name='文件哈希值', db_column='file_hash'),
        ),
        migrations.AddField(
            model_name='classresource',
            name='upload_status',
            field=models.CharField(choices=[('uploading', '上传中'), ('completed', '已完成'), ('failed', '失败')], default='completed', max_length=20, verbose_name='上传状态', db_column='upload_status'),
        ),
        migrations.AddField(
            model_name='classresource',
            name='storage_path',
            field=models.TextField(blank=True, null=True, verbose_name='完整存储路径', db_column='storage_path'),
        ),
        migrations.AddField(
            model_name='classresource',
            name='mime_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='文件MIME类型', db_column='mime_type'),
        ),
        migrations.AddField(
            model_name='classresource',
            name='upload_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='上传IP地址', db_column='upload_ip'),
        ),
        migrations.AddField(
            model_name='classresource',
            name='retry_count',
            field=models.IntegerField(default=0, verbose_name='重试次数', db_column='retry_count'),
        ),
        
        # Add indexes for ClassResource
        migrations.AddIndex(
            model_name='classresource',
            index=models.Index(fields=['file_hash'], name='class_resou_file_h_ix'),
        ),
        migrations.AddIndex(
            model_name='classresource',
            index=models.Index(fields=['upload_status'], name='class_resou_upload__ix'),
        ),
        
        # Modify TeachingResource file field to TextField
        migrations.AlterField(
            model_name='teachingresource',
            name='file',
            field=models.TextField(help_text='完整文件路径或文件名', verbose_name='文件存储路径', db_column='file'),
        ),
        
        # Modify TeachingResource file_size to BigIntegerField
        migrations.AlterField(
            model_name='teachingresource',
            name='file_size',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='文件大小（字节）', db_column='file_size'),
        ),
        
        # Add fields to TeachingResource
        migrations.AddField(
            model_name='teachingresource',
            name='file_hash',
            field=models.CharField(blank=True, help_text='MD5或SHA256哈希值', max_length=64, null=True, verbose_name='文件哈希值', db_column='file_hash'),
        ),
        migrations.AddField(
            model_name='teachingresource',
            name='upload_status',
            field=models.CharField(choices=[('uploading', '上传中'), ('completed', '已完成'), ('failed', '失败')], default='completed', max_length=20, verbose_name='上传状态', db_column='upload_status'),
        ),
        migrations.AddField(
            model_name='teachingresource',
            name='storage_path',
            field=models.TextField(blank=True, null=True, verbose_name='完整存储路径', db_column='storage_path'),
        ),
        migrations.AddField(
            model_name='teachingresource',
            name='mime_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='文件MIME类型', db_column='mime_type'),
        ),
        migrations.AddField(
            model_name='teachingresource',
            name='upload_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='上传IP地址', db_column='upload_ip'),
        ),
        migrations.AddField(
            model_name='teachingresource',
            name='retry_count',
            field=models.IntegerField(default=0, verbose_name='重试次数', db_column='retry_count'),
        ),
        
        # Add indexes for TeachingResource
        migrations.AddIndex(
            model_name='teachingresource',
            index=models.Index(fields=['file_hash'], name='teacher_tea_file_h_ix'),
        ),
        migrations.AddIndex(
            model_name='teachingresource',
            index=models.Index(fields=['upload_status'], name='teacher_tea_upload__ix'),
        ),
    ]

