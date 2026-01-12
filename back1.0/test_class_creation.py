#!/usr/bin/env python3
"""
测试班级创建功能是否能正确地将数据存储到数据库中
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.teacher.models import Teacher, Class
from apps.books.models import Book

def test_class_creation():
    """测试班级创建功能"""
    print("开始测试班级创建功能...")
    
    try:
        # 查找现有教师
        teacher = Teacher.objects.first()
        if not teacher:
            print("错误: 没有找到教师记录，请先创建教师")
            return False
        print(f"找到教师: {teacher.teacher_name}")
        
        # 查找现有教材
        book = Book.objects.first()
        if not book:
            print("错误: 没有找到教材记录，请先创建教材")
            return False
        print(f"找到教材: {book.title}")
        
        # 创建班级
        class_name = "测试班级2024"
        class_obj = Class.objects.create(
            name=class_name,
            teacher=teacher,
            book=book,
            major="计算机科学",
            grade="2024",
            academic_year="2024-2025",
            semester="1",
            description="这是一个测试班级"
        )
        print(f"成功创建班级: {class_obj.name}")
        
        # 验证班级是否正确存储到数据库中
        db_class = Class.objects.get(id=class_obj.id)
        print(f"从数据库中获取到班级: {db_class.name}")
        print(f"班级ID: {db_class.id}")
        print(f"班级名称: {db_class.name}")
        print(f"教师: {db_class.teacher.teacher_name}")
        print(f"教材: {db_class.book.title}")
        print(f"专业: {db_class.major}")
        print(f"年级: {db_class.grade}")
        print(f"创建时间: {db_class.created_at}")
        print(f"更新时间: {db_class.updated_at}")
        
        # 清理测试数据
        class_obj.delete()
        print(f"已删除测试班级: {class_name}")
        
        print("班级创建功能测试成功！")
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_class_creation()