# -*- coding: utf-8 -*-
"""
Django管理命令：修复教师数据
使用方法: python manage.py fix_teacher_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.teacher.models import Class, Student
from apps.books.models import Book

User = get_user_model()


class Command(BaseCommand):
    help = '为所有教师创建测试数据（如果不存在）'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("教师数据修复工具"))
        self.stdout.write("=" * 80)

        # 1. 检查教师账号
        self.stdout.write("\n[步骤1] 检查教师账号...")
        teachers = User.objects.filter(role='teacher')
        self.stdout.write(f"  找到 {teachers.count()} 个教师账号")

        if teachers.count() == 0:
            self.stdout.write(self.style.ERROR("  [错误] 没有找到教师账号！"))
            self.stdout.write("  请先创建教师账号")
            return

        # 显示所有教师
        for teacher in teachers:
            self.stdout.write(f"    - {teacher.username} (ID: {teacher.id}, 姓名: {teacher.last_name}{teacher.first_name})")

        # 2. 检查教材
        self.stdout.write("\n[步骤2] 检查教材...")
        books = Book.objects.all()
        self.stdout.write(f"  找到 {books.count()} 本教材")

        if books.count() == 0:
            self.stdout.write(self.style.WARNING("  [警告] 没有教材，创建默认教材..."))
            book = Book.objects.create(
                title="Python程序设计基础",
                author="系统自动创建",
                description="默认教材，用于测试"
            )
            self.stdout.write(self.style.SUCCESS(f"  [成功] 创建教材: {book.title} (ID: {book.id})"))
            books = Book.objects.all()
        else:
            book = books.first()
            self.stdout.write(f"  使用教材: {book.title} (ID: {book.id})")

        # 3. 为每个教师创建测试数据（如果没有数据）
        self.stdout.write("\n[步骤3] 创建测试数据...")
        created_count = 0
        
        for teacher in teachers:
            teacher_classes = Class.objects.filter(teacher=teacher)
            
            if teacher_classes.count() == 0:
                self.stdout.write(f"\n  教师 {teacher.username} ({teacher.last_name}{teacher.first_name}):")
                self.stdout.write(f"    [创建] 创建测试班级...")
                
                # 创建2个测试班级
                classes_data = [
                    {
                        'name': f'{teacher.last_name}{teacher.first_name}的2024-1班',
                        'major': '计算机科学',
                        'grade': '2024',
                        'students': [
                            {'name': '学生A', 'student_no': f'{teacher.id}001'},
                            {'name': '学生B', 'student_no': f'{teacher.id}002'},
                            {'name': '学生C', 'student_no': f'{teacher.id}003'},
                        ]
                    },
                    {
                        'name': f'{teacher.last_name}{teacher.first_name}的2024-2班',
                        'major': '软件工程',
                        'grade': '2024',
                        'students': [
                            {'name': '学生D', 'student_no': f'{teacher.id}004'},
                            {'name': '学生E', 'student_no': f'{teacher.id}005'},
                        ]
                    }
                ]
                
                for class_data in classes_data:
                    # 检查是否已存在同名班级
                    existing = Class.objects.filter(teacher=teacher, name=class_data['name']).first()
                    if existing:
                        self.stdout.write(f"      [跳过] 班级 {class_data['name']} 已存在")
                        continue
                    
                    # 创建班级
                    try:
                        new_class = Class.objects.create(
                            name=class_data['name'],
                            major=class_data['major'],
                            grade=class_data['grade'],
                            academic_year='2024-2025',
                            semester='1',
                            teacher=teacher,
                            book=book,
                            description=f"测试班级 - {class_data['name']}"
                        )
                        self.stdout.write(self.style.SUCCESS(f"      [成功] 创建班级: {new_class.name} (ID: {new_class.id})"))
                        created_count += 1
                        
                        # 创建学生
                        for student_data in class_data['students']:
                            # 检查学号是否已存在
                            existing_student = Student.objects.filter(student_no=student_data['student_no']).first()
                            if existing_student:
                                # 如果存在，更新班级
                                existing_student.class_obj = new_class
                                existing_student.save()
                                self.stdout.write(f"        - 更新学生: {existing_student.student_name} ({existing_student.student_no})")
                            else:
                                student = Student.objects.create(
                                    student_name=student_data['name'],
                                    student_no=student_data['student_no'],
                                    class_obj=new_class
                                )
                                self.stdout.write(f"        - 创建学生: {student.student_name} ({student.student_no})")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"      [错误] 创建班级失败: {e}"))
            else:
                self.stdout.write(f"\n  教师 {teacher.username}: 已有 {teacher_classes.count()} 个班级，跳过")

        # 4. 最终验证
        self.stdout.write("\n[步骤4] 最终验证...")
        self.stdout.write("-" * 80)
        total_classes = Class.objects.all().count()
        total_students = Student.objects.all().count()

        self.stdout.write(f"  系统总班级数: {total_classes}")
        self.stdout.write(f"  系统总学生数: {total_students}")

        for teacher in teachers:
            classes = Class.objects.filter(teacher=teacher)
            students = Student.objects.filter(class_obj__teacher=teacher)
            self.stdout.write(f"\n  {teacher.username} ({teacher.last_name}{teacher.first_name}):")
            self.stdout.write(f"    班级数: {classes.count()}")
            self.stdout.write(f"    学生数: {students.count()}")

        self.stdout.write("\n" + "=" * 80)
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"[成功] 创建了 {created_count} 个新班级"))
        else:
            self.stdout.write(self.style.SUCCESS("[完成] 所有教师都有数据，无需创建"))
        self.stdout.write("=" * 80)
