"""将现有章节内容转换为标准Jupyter Notebook格式"""
import json
import logging
from apps.books.models import Chapter, JupyterNotebook, JupyterCell, JupyterOutput

logger = logging.getLogger(__name__)


def create_sample_jupyter_notebook(chapter_id=None):
    """为指定章节创建示例Jupyter Notebook"""
    try:
        # 获取章节，如果没有指定，获取第一个内容类型为jupyter的章节
        if chapter_id:
            chapter = Chapter.objects.get(id=chapter_id)
        else:
            chapter = Chapter.objects.filter(content_type='jupyter').first()
            
        if not chapter:
            # 如果没有jupyter类型的章节，获取第一个阅读类型的章节
            chapter = Chapter.objects.filter(type='reading').first()
            
        if not chapter:
            print("没有找到可用于创建Jupyter Notebook的章节")
            return None
        
        print(f"为章节创建Jupyter Notebook: {chapter.title}")
        
        # 创建标准Jupyter Notebook数据
        standard_notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": f"# {chapter.title}\n\n{chapter.description}",
                    "metadata": {}
                },
                {
                    "cell_type": "code",
                    "execution_count": 1,
                    "metadata": {},
                    "outputs": [
                        {
                            "output_type": "execute_result",
                            "execution_count": 1,
                            "metadata": {},
                            "data": {
                                "text/plain": ["'Hello, Jupyter!'"],
                                "application/json": {"message": "Hello from CodeBook!"}
                            }
                        }
                    ],
                    "source": "# 示例代码\nprint('Hello, Jupyter!')\n\n# 返回一些数据\n'Hello, Jupyter!'".splitlines()
                },
                {
                    "cell_type": "markdown",
                    "source": "## 练习与思考\n\n尝试修改上面的代码，输出你自己的消息。",
                    "metadata": {}
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.12.0"
                },
                "chapter_info": {
                    "chapter_id": chapter.id,
                    "title": chapter.title,
                    "book_id": chapter.book.id,
                    "book_title": chapter.book.title
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        
        # 如果章节已有jupyter_content，尝试解析并使用
        if chapter.jupyter_content:
            try:
                existing_content = json.loads(chapter.jupyter_content)
                # 如果是标准格式，直接使用
                if isinstance(existing_content, dict) and 'cells' in existing_content:
                    standard_notebook = existing_content
                    print("检测到现有标准格式Jupyter内容，已使用")
            except Exception as e:
                print(f"解析现有Jupyter内容失败，使用默认模板: {str(e)}")
        
        # 创建或更新JupyterNotebook实例
        notebook, created = JupyterNotebook.objects.update_or_create(
            chapter=chapter,
            defaults={
                'nbformat': standard_notebook.get('nbformat', 4),
                'nbformat_minor': standard_notebook.get('nbformat_minor', 5),
                'metadata': standard_notebook.get('metadata', {})
            }
        )
        
        # 从标准格式加载数据
        success = notebook.from_standard_format(standard_notebook)
        
        if success:
            print(f"{'创建' if created else '更新'}成功! Jupyter Notebook ID: {notebook.id}")
            
            # 可选：更新章节的content_type为jupyter
            chapter.content_type = 'jupyter'
            chapter.save()
            
            return notebook
        else:
            print("从标准格式加载数据失败")
            return None
            
    except Exception as e:
        print(f"创建示例Jupyter Notebook失败: {str(e)}")
        logger.error(f"Error creating sample Jupyter Notebook: {str(e)}")
        return None


def convert_all_jupyter_chapters():
    """转换所有内容类型为jupyter的章节"""
    jupyter_chapters = Chapter.objects.filter(content_type='jupyter')
    print(f"找到 {jupyter_chapters.count()} 个Jupyter类型的章节")
    
    success_count = 0
    for chapter in jupyter_chapters:
        try:
            notebook = create_sample_jupyter_notebook(chapter.id)
            if notebook:
                success_count += 1
        except Exception as e:
            print(f"转换章节 {chapter.title} 失败: {str(e)}")
    
    print(f"转换完成! 成功: {success_count}, 总数: {jupyter_chapters.count()}")


def demonstrate_standard_format():
    """演示标准Jupyter格式的使用"""
    # 创建示例Notebook
    notebook = create_sample_jupyter_notebook()
    if not notebook:
        print("无法创建示例Notebook，跳过演示")
        return
    
    print("\n=== 演示从数据库读取并转换为标准格式 ===")
    
    # 从数据库读取并转换为标准格式
    standard_format = notebook.to_standard_format()
    
    # 打印基本信息
    print(f"Notebook格式版本: {standard_format['nbformat']}.{standard_format['nbformat_minor']}")
    print(f"单元格数量: {len(standard_format['cells'])}")
    print(f"包含元数据: {bool(standard_format['metadata'])}")
    
    # 打印前两个单元格的信息
    for i, cell in enumerate(standard_format['cells'][:2]):
        print(f"\n单元格 {i+1}:")
        print(f"  类型: {cell['cell_type']}")
        print(f"  内容长度: {len(str(cell['source']))} 字符")
        if cell['cell_type'] == 'code' and 'outputs' in cell:
            print(f"  输出数量: {len(cell['outputs'])}")


def create_demo_notebook():
    """创建一个完整的演示Notebook"""
    # 获取或创建一个演示章节
    demo_book = Chapter.objects.first().book if Chapter.objects.exists() else None
    if not demo_book:
        print("没有找到书籍，无法创建演示Notebook")
        return
    
    # 创建演示章节
    demo_chapter, created = Chapter.objects.get_or_create(
        title="Jupyter Notebook 演示章节",
        book=demo_book,
        defaults={
            'type': 'reading',
            'content_type': 'jupyter',
            'description': "这是一个标准Jupyter Notebook格式的演示章节",
            'order': 999
        }
    )
    
    # 创建完整的演示Notebook
    notebook = create_sample_jupyter_notebook(demo_chapter.id)
    print(f"演示Notebook已{'创建' if created else '更新'}: {notebook}")


if __name__ == "__main__":
    print("===== Jupyter Notebook 转换工具 =====")
    print("1. 创建示例Jupyter Notebook")
    print("2. 转换所有Jupyter类型章节")
    print("3. 演示标准格式使用")
    print("4. 创建完整演示Notebook")
    
    choice = input("请选择操作 (1-4): ")
    
    if choice == '1':
        chapter_id = input("请输入章节ID (留空使用默认章节): ")
        create_sample_jupyter_notebook(int(chapter_id) if chapter_id else None)
    elif choice == '2':
        confirm = input("确定要转换所有Jupyter类型章节吗？(y/n): ")
        if confirm.lower() == 'y':
            convert_all_jupyter_chapters()
    elif choice == '3':
        demonstrate_standard_format()
    elif choice == '4':
        create_demo_notebook()
    else:
        print("无效的选择")