import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.books.models import Practice, Book

def check_javascript_practices():
    """检查JavaScript相关的练习题数据"""
    
    # 查找数据分析与可视化入门书籍（ID=2）
    try:
        book = Book.objects.get(id=2)
        print(f"找到书籍: {book.title}")
        
        # 获取该书籍的所有练习题集
        practices = Practice.objects.filter(chapter__book=book)
        print(f"该书籍共有 {practices.count()} 个练习题集")
        
        javascript_practices = []
        
        for practice in practices:
            print(f"\n练习题集: {practice.title}")
            print(f"  ID: {practice.id}")
            print(f"  Language: {practice.language}")
            
            if practice.language == 'javascript':
                javascript_practices.append(practice)
                print(f"  ✅ 这是JavaScript练习题")
            
            # 检查是否有题目数据
            if practice.questions:
                print(f"  题目数量: {len(practice.questions)}")
            else:
                print(f"  ❌ 没有题目数据")
        
        print(f"\n📊 总结:")
        print(f"- 总练习题集数: {practices.count()}")
        print(f"- JavaScript练习题集数: {len(javascript_practices)}")
        
        if not javascript_practices:
            print("\n⚠️  没有找到JavaScript练习题集！")
            print("建议运行 add_javascript_practices.py 脚本添加JavaScript练习题")
        else:
            print("\n🎉 JavaScript练习题集已正确配置！")
            
    except Book.DoesNotExist:
        print("❌ 没有找到ID为2的书籍")
        print("所有书籍:")
        for b in Book.objects.all():
            print(f"  ID: {b.id}, 标题: {b.title}")

if __name__ == "__main__":
    check_javascript_practices()
