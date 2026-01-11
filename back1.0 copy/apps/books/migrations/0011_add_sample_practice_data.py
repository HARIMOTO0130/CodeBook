# Generated manually to add sample practice data

from django.db import migrations


def create_sample_practices(apps, schema_editor):
    """创建示例练习题数据"""
    Chapter = apps.get_model('books', 'Chapter')
    Practice = apps.get_model('books', 'Practice')
    PracticeChoiceOption = apps.get_model('books', 'PracticeChoiceOption')
    PracticeFillBlank = apps.get_model('books', 'PracticeFillBlank')
    TestCase = apps.get_model('books', 'TestCase')
    
    # 获取所有章节
    chapters = Chapter.objects.all()
    
    if not chapters.exists():
        print("没有找到章节，跳过创建示例练习题")
        return
    
    # 为前5个章节创建不同类型的练习题
    for i, chapter in enumerate(chapters[:5]):
        try:
            if i == 0:
                # 创建选择题
                practice = Practice.objects.create(
                    chapter=chapter,
                    question_type='choice',
                    title=f'{chapter.title} - 选择题',
                    description='测试你对本章基础概念的理解',
                    question='以下哪个选项是正确的？',
                    difficulty=1,
                    order=1
                )
                
                # 添加选项
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='选项A：这是错误答案',
                    is_correct=False,
                    order=1
                )
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='选项B：这是正确答案',
                    is_correct=True,
                    order=2
                )
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='选项C：这是错误答案',
                    is_correct=False,
                    order=3
                )
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='选项D：这是错误答案',
                    is_correct=False,
                    order=4
                )
                
            elif i == 1:
                # 创建填空题
                practice = Practice.objects.create(
                    chapter=chapter,
                    question_type='fill',
                    title=f'{chapter.title} - 填空题',
                    description='请根据本章内容完成填空',
                    question='请填写以下空格：',
                    difficulty=2,
                    order=1
                )
                
                # 添加空位
                PracticeFillBlank.objects.create(
                    practice=practice,
                    prompt='第一个空格：',
                    placeholder='请输入答案',
                    correct_answer='正确答案1',
                    order=1
                )
                PracticeFillBlank.objects.create(
                    practice=practice,
                    prompt='第二个空格：',
                    placeholder='请输入答案',
                    correct_answer='正确答案2',
                    order=2
                )
                
            elif i == 2:
                # 创建代码补全题
                practice = Practice.objects.create(
                    chapter=chapter,
                    question_type='code_completion',
                    title=f'{chapter.title} - 代码补全题',
                    description='请补全以下代码',
                    question='补全代码以实现指定功能',
                    code_template='def hello_world():\n    print("_____")\n\nhello_world()',
                    language='python',
                    difficulty=2,
                    order=1
                )
                
                # 添加测试用例
                TestCase.objects.create(
                    practice=practice,
                    input_data={},
                    expected_output='Hello, World!',
                    order=1
                )
                
            elif i == 3:
                # 创建编程题
                practice = Practice.objects.create(
                    chapter=chapter,
                    question_type='programming',
                    title=f'{chapter.title} - 编程题',
                    description='编写一个函数来实现指定功能',
                    question='请编写一个函数，计算两个数的和',
                    code_template='def add_numbers(a, b):\n    # 在这里编写你的代码\n    pass',
                    language='python',
                    difficulty=3,
                    order=1
                )
                
                # 添加测试用例
                TestCase.objects.create(
                    practice=practice,
                    input_data={'a': 5, 'b': 3},
                    expected_output=8,
                    order=1
                )
                TestCase.objects.create(
                    practice=practice,
                    input_data={'a': 10, 'b': 20},
                    expected_output=30,
                    order=2
                )
                TestCase.objects.create(
                    practice=practice,
                    input_data={'a': -5, 'b': 10},
                    expected_output=5,
                    order=3
                )
                
            else:
                # 创建另一个选择题
                practice = Practice.objects.create(
                    chapter=chapter,
                    question_type='choice',
                    title=f'{chapter.title} - 综合选择题',
                    description='综合测试你对本章内容的掌握',
                    question='以下哪个描述是正确的？',
                    difficulty=2,
                    order=1
                )
                
                # 添加选项
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='描述A：这是错误描述',
                    is_correct=False,
                    order=1
                )
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='描述B：这是错误描述',
                    is_correct=False,
                    order=2
                )
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='描述C：这是正确描述',
                    is_correct=True,
                    order=3
                )
                PracticeChoiceOption.objects.create(
                    practice=practice,
                    content='描述D：这是错误描述',
                    is_correct=False,
                    order=4
                )
            
            print(f"成功为章节 '{chapter.title}' 创建练习题")
            
        except Exception as e:
            print(f"为章节 '{chapter.title}' 创建练习题时出错: {str(e)}")


def remove_sample_practices(apps, schema_editor):
    """删除示例练习题数据"""
    Practice = apps.get_model('books', 'Practice')
    Practice.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_auto_20260104_2041'),
    ]

    operations = [
        migrations.RunPython(create_sample_practices, remove_sample_practices),
    ]
