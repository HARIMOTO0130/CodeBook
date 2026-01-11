# -*- coding: utf-8 -*-
"""
Django管理命令：检查教师数据
使用方法: python manage.py check_teacher_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.teacher.models import Class, Student
from apps.books.models import Book

User = get_user_model()


class Command(BaseCommand):
    help = '检查教师数据并生成诊断报告'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("教师数据诊断报告"))
        self.stdout.write("=" * 80)

        # 1. 检查所有教师账号
        self.stdout.write("\n[1] 检查教师账号:")
        self.stdout.write("-" * 80)
        teachers = User.objects.filter(role='teacher')
        self.stdout.write(f"系统中教师总数: {teachers.count()}")
        for teacher in teachers:
            self.stdout.write(f"  - ID: {teacher.id}, 用户名: {teacher.username}, 姓名: {teacher.last_name}{teacher.first_name}")

        # 2. 检查每个教师的班级数据
        self.stdout.write("\n[2] 检查班级数据:")
        self.stdout.write("-" * 80)
        all_classes = Class.objects.all()
        self.stdout.write(f"系统中班级总数: {all_classes.count()}")
        if all_classes.count() > 0:
            for cls in all_classes:
                teacher_name = f"{cls.teacher.last_name}{cls.teacher.first_name}" if cls.teacher else "未知"
                self.stdout.write(f"  - 班级ID: {cls.id}, 名称: {cls.name}, 教师: {teacher_name} (ID: {cls.teacher.id if cls.teacher else 'N/A'})")
        else:
            self.stdout.write(self.style.WARNING("  [警告] 数据库中没有班级数据！"))

        # 3. 检查每个教师的学生数据
        self.stdout.write("\n[3] 检查学生数据:")
        self.stdout.write("-" * 80)
        all_students = Student.objects.all()
        self.stdout.write(f"系统中学生总数: {all_students.count()}")
        if all_students.count() > 0:
            for student in all_students[:10]:  # 只显示前10个
                class_name = student.class_obj.name if student.class_obj else "无班级"
                teacher_name = f"{student.class_obj.teacher.last_name}{student.class_obj.teacher.first_name}" if student.class_obj and student.class_obj.teacher else "未知"
                self.stdout.write(f"  - 学生: {student.student_name} ({student.student_no}), 班级: {class_name}, 教师: {teacher_name}")
            if all_students.count() > 10:
                self.stdout.write(f"  ... 还有 {all_students.count() - 10} 个学生")
        else:
            self.stdout.write(self.style.WARNING("  [警告] 数据库中没有学生数据！"))

        # 4. 检查特定教师（李华）的数据
        self.stdout.write("\n[4] 检查李华的数据:")
        self.stdout.write("-" * 80)
        lihua = User.objects.filter(username='lihua').first()
        if lihua:
            self.stdout.write(f"找到李华账号: ID={lihua.id}, 用户名={lihua.username}")
            lihua_classes = Class.objects.filter(teacher=lihua)
            self.stdout.write(f"  李华的班级数: {lihua_classes.count()}")
            for cls in lihua_classes:
                student_count = cls.students.count()
                self.stdout.write(f"    - {cls.name}: {student_count} 个学生")
                for student in cls.students.all():
                    self.stdout.write(f"        * {student.student_name} ({student.student_no})")
            
            if lihua_classes.count() == 0:
                self.stdout.write(self.style.ERROR("  [问题] 李华没有班级数据！"))
        else:
            self.stdout.write(self.style.WARNING("  [警告] 未找到李华账号"))

        # 5. 检查其他教师的数据
        self.stdout.write("\n[5] 检查其他教师的数据:")
        self.stdout.write("-" * 80)
        for teacher in teachers:
            if teacher.username != 'lihua':
                classes = Class.objects.filter(teacher=teacher)
                students = Student.objects.filter(class_obj__teacher=teacher)
                self.stdout.write(f"  {teacher.username} ({teacher.last_name}{teacher.first_name}):")
                self.stdout.write(f"    - 班级数: {classes.count()}")
                self.stdout.write(f"    - 学生数: {students.count()}")

        # 6. 检查教材数据
        self.stdout.write("\n[6] 检查教材数据:")
        self.stdout.write("-" * 80)
        books = Book.objects.all()
        self.stdout.write(f"系统中教材总数: {books.count()}")
        if books.count() > 0:
            for book in books[:5]:  # 只显示前5个
                self.stdout.write(f"  - ID: {book.id}, 书名: {book.title}")
        else:
            self.stdout.write(self.style.WARNING("  [警告] 数据库中没有教材数据！"))

        # 7. 诊断建议
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("诊断建议:")
        self.stdout.write("=" * 80)

        if all_classes.count() == 0:
            self.stdout.write(self.style.ERROR("[问题1] 数据库中没有班级数据"))
            self.stdout.write("  解决方案: 运行 python manage.py fix_teacher_data 创建测试数据")
        elif lihua and Class.objects.filter(teacher=lihua).count() == 0:
            self.stdout.write(self.style.ERROR("[问题2] 李华账号没有班级数据"))
            self.stdout.write("  解决方案: 运行 python manage.py fix_teacher_data 为李华创建测试数据")
        elif all_students.count() == 0:
            self.stdout.write(self.style.ERROR("[问题3] 数据库中没有学生数据"))
            self.stdout.write("  解决方案: 运行 python manage.py fix_teacher_data 创建测试数据")
        else:
            self.stdout.write(self.style.SUCCESS("[正常] 数据库中有数据"))
            self.stdout.write("  如果前端仍然显示为空，请检查:")
            self.stdout.write("    1. 后端API是否正确返回数据（检查浏览器Network标签）")
            self.stdout.write("    2. 前端是否正确解析API响应")
            self.stdout.write("    3. 登录用户的ID是否与数据库中的teacher_id匹配")

        self.stdout.write("\n" + "=" * 80)
