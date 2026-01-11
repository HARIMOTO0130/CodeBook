# Generated migration file for teacher models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0001_initial'),
        ('books', '0014_booktag_book_is_archived_alter_book_tags_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 删除旧的模型
        migrations.RemoveField(
            model_name='class',
            name='students',
        ),
        migrations.DeleteModel(
            name='Assignment',
        ),
        migrations.DeleteModel(
            name='AssignmentSubmission',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.DeleteModel(
            name='TeacherProfile',
        ),
        migrations.DeleteModel(
            name='StudentProfile',
        ),
        
        # 修改Class模型
        migrations.AlterModelTable(
            name='class',
            table='class',
        ),
        migrations.RenameField(
            model_name='class',
            old_name='name',
            new_name='name',
        ),
        migrations.AddField(
            model_name='class',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='books.book', verbose_name='关联教材', db_column='book_id'),
        ),
        migrations.AddField(
            model_name='class',
            name='status',
            field=models.IntegerField(default=1, verbose_name='状态', help_text='1-正常，0-解散'),
        ),
        migrations.AlterField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_classes', to=settings.AUTH_USER_MODEL, verbose_name='教师', db_column='teacher_id'),
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('teacher', 'book')},
        ),
        
        # 创建新模型
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(db_column='student_id', primary_key=True, serialize=False)),
                ('student_no', models.CharField(max_length=50, unique=True, verbose_name='学生学号')),
                ('student_name', models.CharField(max_length=100, verbose_name='学生姓名')),
                ('gender', models.IntegerField(blank=True, null=True, verbose_name='性别', help_text='1-男，2-女，0-未知')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='联系电话')),
                ('status', models.IntegerField(default=1, verbose_name='状态', help_text='1-正常，0-离校/退班')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='create_time', verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='update_time', verbose_name='更新时间')),
                ('class_obj', models.ForeignKey(db_column='class_id', on_delete=django.db.models.deletion.CASCADE, related_name='students', to='teacher.class', verbose_name='所属班级')),
            ],
            options={
                'verbose_name': '学生',
                'verbose_name_plural': '学生',
                'db_table': 'student',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.AutoField(db_column='homework_id', primary_key=True, serialize=False)),
                ('homework_name', models.CharField(max_length=200, verbose_name='作业名称')),
                ('homework_content', models.TextField(verbose_name='作业内容')),
                ('start_time', models.DateTimeField(verbose_name='作业发布时间')),
                ('end_time', models.DateTimeField(verbose_name='作业截止时间')),
                ('total_score', models.IntegerField(default=100, verbose_name='作业总分')),
                ('status', models.IntegerField(default=1, verbose_name='状态', help_text='1-未发布，2-已发布，3-已截止')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='create_time', verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='update_time', verbose_name='更新时间')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to=settings.AUTH_USER_MODEL, verbose_name='创建教师')),
                ('class_obj', models.ForeignKey(db_column='class_id', on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='teacher.class', verbose_name='所属班级')),
                ('chapter', models.ForeignKey(db_column='chapter_id', on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='books.chapter', verbose_name='关联章节')),
            ],
            options={
                'verbose_name': '作业',
                'verbose_name_plural': '作业',
                'db_table': 'homework',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StudentHomework',
            fields=[
                ('id', models.AutoField(db_column='submit_id', primary_key=True, serialize=False)),
                ('submit_content', models.TextField(blank=True, null=True, verbose_name='提交内容')),
                ('submit_file_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='提交文件地址')),
                ('submit_time', models.DateTimeField(blank=True, null=True, verbose_name='提交时间')),
                ('correct_time', models.DateTimeField(blank=True, null=True, verbose_name='批改时间')),
                ('score', models.IntegerField(blank=True, null=True, verbose_name='得分')),
                ('correct_comment', models.TextField(blank=True, null=True, verbose_name='批改评语')),
                ('status', models.IntegerField(default=1, verbose_name='状态', help_text='1-未提交，2-已提交，3-已批改，4-已退回')),
                ('homework', models.ForeignKey(db_column='homework_id', on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='teacher.homework', verbose_name='作业')),
                ('student', models.ForeignKey(db_column='student_id', on_delete=django.db.models.deletion.CASCADE, related_name='homework_submissions', to='teacher.student', verbose_name='学生')),
                ('correct_teacher', models.ForeignKey(blank=True, db_column='correct_teacher_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corrected_homeworks', to=settings.AUTH_USER_MODEL, verbose_name='批改教师')),
            ],
            options={
                'verbose_name': '学生作业提交',
                'verbose_name_plural': '学生作业提交',
                'db_table': 'student_homework',
                'unique_together': {('homework', 'student')},
            },
        ),
        migrations.CreateModel(
            name='StudentLearningProgress',
            fields=[
                ('id', models.AutoField(db_column='progress_id', primary_key=True, serialize=False)),
                ('learn_time', models.IntegerField(default=0, verbose_name='学习时长（分钟）')),
                ('learn_status', models.IntegerField(default=1, verbose_name='学习状态', help_text='1-未学习，2-学习中，3-已完成')),
                ('last_learn_time', models.DateTimeField(blank=True, null=True, verbose_name='最后学习时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='create_time', verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='update_time', verbose_name='更新时间')),
                ('student', models.ForeignKey(db_column='student_id', on_delete=django.db.models.deletion.CASCADE, related_name='learning_progress', to='teacher.student', verbose_name='学生')),
                ('chapter', models.ForeignKey(db_column='chapter_id', on_delete=django.db.models.deletion.CASCADE, related_name='student_progress', to='books.chapter', verbose_name='章节')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='student_progress', to=settings.AUTH_USER_MODEL, verbose_name='教师')),
            ],
            options={
                'verbose_name': '学生学习进度',
                'verbose_name_plural': '学生学习进度',
                'db_table': 'student_learning_progress',
                'unique_together': {('student', 'chapter')},
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(db_column='notice_id', primary_key=True, serialize=False)),
                ('notice_title', models.CharField(max_length=200, verbose_name='通知标题')),
                ('notice_content', models.TextField(verbose_name='通知内容')),
                ('publish_time', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('expire_time', models.DateTimeField(blank=True, null=True, verbose_name='过期时间')),
                ('read_count', models.IntegerField(default=0, verbose_name='已读次数')),
                ('status', models.IntegerField(default=1, verbose_name='状态', help_text='1-有效，0-已删除')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='sent_notices', to=settings.AUTH_USER_MODEL, verbose_name='发布教师')),
                ('class_obj', models.ForeignKey(blank=True, db_column='class_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notices', to='teacher.class', verbose_name='所属班级', help_text='NULL表示全体学生')),
            ],
            options={
                'verbose_name': '通知',
                'verbose_name_plural': '通知',
                'db_table': 'notice',
                'ordering': ['-publish_time'],
            },
        ),
        migrations.CreateModel(
            name='StudentNoticeRead',
            fields=[
                ('id', models.AutoField(db_column='read_id', primary_key=True, serialize=False)),
                ('read_time', models.DateTimeField(blank=True, null=True, verbose_name='阅读时间')),
                ('is_read', models.IntegerField(default=0, verbose_name='是否已读', help_text='0-未读，1-已读')),
                ('notice', models.ForeignKey(db_column='notice_id', on_delete=django.db.models.deletion.CASCADE, related_name='read_records', to='teacher.notice', verbose_name='通知')),
                ('student', models.ForeignKey(db_column='student_id', on_delete=django.db.models.deletion.CASCADE, related_name='notice_reads', to='teacher.student', verbose_name='学生')),
            ],
            options={
                'verbose_name': '学生通知阅读记录',
                'verbose_name_plural': '学生通知阅读记录',
                'db_table': 'student_notice_read',
                'unique_together': {('notice', 'student')},
            },
        ),
        migrations.CreateModel(
            name='ClassResource',
            fields=[
                ('id', models.AutoField(db_column='resource_id', primary_key=True, serialize=False)),
                ('resource_name', models.CharField(max_length=200, verbose_name='资源名称')),
                ('resource_type', models.CharField(max_length=50, verbose_name='资源类型', help_text='文档、视频、音频、图片等')),
                ('resource_url', models.CharField(max_length=255, verbose_name='资源存储地址')),
                ('upload_time', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('download_count', models.IntegerField(default=0, verbose_name='下载次数')),
                ('resource_desc', models.CharField(blank=True, max_length=500, null=True, verbose_name='资源描述')),
                ('class_obj', models.ForeignKey(db_column='class_id', on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='teacher.class', verbose_name='所属班级')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='class_resources', to=settings.AUTH_USER_MODEL, verbose_name='所属教师')),
            ],
            options={
                'verbose_name': '班级资源',
                'verbose_name_plural': '班级资源',
                'db_table': 'class_resource',
                'ordering': ['-upload_time'],
            },
        ),
        migrations.CreateModel(
            name='TeachingResource',
            fields=[
                ('id', models.AutoField(db_column='resource_id', primary_key=True, serialize=False)),
                ('resource_name', models.CharField(max_length=200, verbose_name='资源名称')),
                ('resource_type', models.CharField(max_length=50, verbose_name='资源类型', help_text='课件、教案、习题等')),
                ('resource_url', models.CharField(max_length=255, verbose_name='资源存储地址')),
                ('upload_time', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('resource_desc', models.CharField(blank=True, max_length=500, null=True, verbose_name='资源描述')),
                ('chapter', models.ForeignKey(db_column='chapter_id', on_delete=django.db.models.deletion.CASCADE, related_name='teaching_resources', to='books.chapter', verbose_name='所属章节')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='teaching_resources', to=settings.AUTH_USER_MODEL, verbose_name='上传教师')),
            ],
            options={
                'verbose_name': '教学资源',
                'verbose_name_plural': '教学资源',
                'db_table': 'teaching_resource',
                'ordering': ['-upload_time'],
            },
        ),
        migrations.CreateModel(
            name='CourseDesign',
            fields=[
                ('id', models.AutoField(db_column='design_id', primary_key=True, serialize=False)),
                ('design_title', models.CharField(max_length=200, verbose_name='设计标题')),
                ('design_content', models.TextField(blank=True, null=True, verbose_name='设计内容')),
                ('teaching_hours', models.IntegerField(blank=True, null=True, verbose_name='预计课时')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='create_time', verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='update_time', verbose_name='更新时间')),
                ('class_obj', models.ForeignKey(db_column='class_id', on_delete=django.db.models.deletion.CASCADE, related_name='course_designs', to='teacher.class', verbose_name='所属班级')),
                ('chapter', models.ForeignKey(db_column='chapter_id', on_delete=django.db.models.deletion.CASCADE, related_name='course_designs', to='books.chapter', verbose_name='关联章节')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='course_designs', to=settings.AUTH_USER_MODEL, verbose_name='设计教师')),
            ],
            options={
                'verbose_name': '课程设计',
                'verbose_name_plural': '课程设计',
                'db_table': 'course_design',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TeacherSetting',
            fields=[
                ('id', models.AutoField(db_column='setting_id', primary_key=True, serialize=False)),
                ('setting_key', models.CharField(max_length=50, verbose_name='设置项key', help_text='theme、notify_type等')),
                ('setting_value', models.CharField(max_length=255, verbose_name='设置项值')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='create_time', verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='update_time', verbose_name='更新时间')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL, verbose_name='教师')),
            ],
            options={
                'verbose_name': '教师个人设置',
                'verbose_name_plural': '教师个人设置',
                'db_table': 'teacher_setting',
                'unique_together': {('teacher', 'setting_key')},
            },
        ),
        migrations.CreateModel(
            name='TeachingToolLog',
            fields=[
                ('id', models.AutoField(db_column='log_id', primary_key=True, serialize=False)),
                ('tool_name', models.CharField(max_length=100, verbose_name='工具名称', help_text='计时器、随机点名、答题卡等')),
                ('use_time', models.DateTimeField(auto_now_add=True, verbose_name='使用时间')),
                ('use_duration', models.IntegerField(default=0, verbose_name='使用时长（秒）')),
                ('teacher', models.ForeignKey(db_column='teacher_id', on_delete=django.db.models.deletion.CASCADE, related_name='tool_logs', to=settings.AUTH_USER_MODEL, verbose_name='教师')),
                ('class_obj', models.ForeignKey(blank=True, db_column='class_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tool_logs', to='teacher.class', verbose_name='使用的班级')),
            ],
            options={
                'verbose_name': '教学工具使用记录',
                'verbose_name_plural': '教学工具使用记录',
                'db_table': 'teaching_tool_log',
                'ordering': ['-use_time'],
            },
        ),
        
        # 添加索引
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['class_obj'], name='idx_student_class'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['student_name'], name='idx_student_name'),
        ),
        migrations.AddIndex(
            model_name='homework',
            index=models.Index(fields=['teacher'], name='idx_homework_teacher'),
        ),
        migrations.AddIndex(
            model_name='homework',
            index=models.Index(fields=['class_obj'], name='idx_homework_class'),
        ),
        migrations.AddIndex(
            model_name='homework',
            index=models.Index(fields=['status'], name='idx_homework_status'),
        ),
        migrations.AddIndex(
            model_name='studenthomework',
            index=models.Index(fields=['student'], name='idx_submit_student'),
        ),
        migrations.AddIndex(
            model_name='studenthomework',
            index=models.Index(fields=['status'], name='idx_submit_status'),
        ),
        migrations.AddIndex(
            model_name='studentlearningprogress',
            index=models.Index(fields=['teacher'], name='idx_progress_teacher'),
        ),
        migrations.AddIndex(
            model_name='studentlearningprogress',
            index=models.Index(fields=['learn_status'], name='idx_progress_status'),
        ),
        migrations.AddIndex(
            model_name='notice',
            index=models.Index(fields=['teacher'], name='idx_notice_teacher'),
        ),
        migrations.AddIndex(
            model_name='notice',
            index=models.Index(fields=['class_obj'], name='idx_notice_class'),
        ),
        migrations.AddIndex(
            model_name='classresource',
            index=models.Index(fields=['class_obj'], name='idx_classres_class'),
        ),
        migrations.AddIndex(
            model_name='classresource',
            index=models.Index(fields=['teacher'], name='idx_classres_teacher'),
        ),
        migrations.AddIndex(
            model_name='teachingresource',
            index=models.Index(fields=['chapter'], name='idx_teachres_chapter'),
        ),
        migrations.AddIndex(
            model_name='teachingresource',
            index=models.Index(fields=['teacher'], name='idx_teachres_teacher'),
        ),
        migrations.AddIndex(
            model_name='coursedesign',
            index=models.Index(fields=['class_obj'], name='idx_design_class'),
        ),
        migrations.AddIndex(
            model_name='coursedesign',
            index=models.Index(fields=['chapter'], name='idx_design_chapter'),
        ),
        migrations.AddIndex(
            model_name='teachingtoollog',
            index=models.Index(fields=['teacher'], name='idx_toollog_teacher'),
        ),
        migrations.AddIndex(
            model_name='teachingtoollog',
            index=models.Index(fields=['tool_name'], name='idx_toollog_name'),
        ),
        migrations.AddIndex(
            model_name='teachingtoollog',
            index=models.Index(fields=['class_obj'], name='idx_toollog_class'),
        ),
    ]
