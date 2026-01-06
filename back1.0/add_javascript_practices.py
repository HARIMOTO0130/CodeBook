import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.books.models import Practice, Chapter, Book

def add_javascript_practices():
    """添加JavaScript语言的练习题数据"""
    
    # 获取所有Practice对象
    practices = Practice.objects.all()
    
    if not practices.exists():
        print("没有找到练习题集")
        return
    
    print(f"找到 {practices.count()} 个练习题集")
    
    # 为部分练习题设置为JavaScript语言
    # 可以选择特定书籍或章节的练习题
    updated_count = 0
    
    for practice in practices:
        try:
            chapter = practice.chapter
            book = chapter.book
            
            # 这里可以根据需要选择哪些练习题设置为JavaScript
            # 例如：选择书籍ID为2（数据分析与可视化入门）的所有练习题
            if book.id == 2:
                print(f"\n处理练习题集: {practice.title}")
                print(f"所属书籍: {book.title}, 章节: {chapter.title}")
                
                # 设置language字段为javascript
                practice.language = 'javascript'
                practice.save()
                
                print(f"✅ 已将练习题集语言设置为javascript")
                updated_count += 1
                
        except Exception as e:
            print(f"❌ 处理练习题集 {practice.title} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n更新完成！共更新了 {updated_count} 个练习题集的语言为javascript")
    
    # 验证更新结果
    javascript_practices = Practice.objects.filter(language='javascript')
    print(f"\n当前JavaScript语言的练习题集数量: {javascript_practices.count()}")
    for practice in javascript_practices:
        print(f"- {practice.title} (书籍: {practice.chapter.book.title})")

if __name__ == "__main__":
    add_javascript_practices()
