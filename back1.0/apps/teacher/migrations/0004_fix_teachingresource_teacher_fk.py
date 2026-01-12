# Generated migration to fix TeachingResource teacher foreign key
# 修复初始迁移中错误地将teacher字段引用到User表的问题

from django.db import migrations, models
import django.db.models.deletion


def fix_foreign_key(apps, schema_editor):
    """修复外键约束"""
    db = schema_editor.connection
    with db.cursor() as cursor:
        # 获取外键约束名称
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'teacher_teachingresource' 
            AND COLUMN_NAME = 'teacher_id' 
            AND REFERENCED_TABLE_NAME = 'users_user'
        """)
        result = cursor.fetchone()
        if result:
            constraint_name = result[0]
            # 删除旧的外键约束
            cursor.execute(f"ALTER TABLE teacher_teachingresource DROP FOREIGN KEY {constraint_name}")


def reverse_fix_foreign_key(apps, schema_editor):
    """回滚操作（如果需要）"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0003_add_upload_fields'),
    ]

    operations = [
        # 先删除旧的外键约束
        migrations.RunPython(fix_foreign_key, reverse_fix_foreign_key),
        # 修改teacher字段，使其引用teacher表而不是users_user表
        migrations.AlterField(
            model_name='teachingresource',
            name='teacher',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='teaching_resources',
                to='teacher.teacher',
                verbose_name='上传教师',
                db_column='teacher_id'
            ),
        ),
    ]
