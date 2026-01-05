from django.core.management.base import BaseCommand
from apps.books.models import Chapter, Practice, PracticeChoiceOption, PracticeFillBlank, TestCase


class Command(BaseCommand):
    help = '创建示例练习题数据，每个章节至少5道题'

    def handle(self, *args, **options):
        """创建示例练习题数据"""
        
        # 获取所有章节
        chapters = Chapter.objects.all()
        
        if not chapters.exists():
            self.stdout.write(self.style.WARNING('没有找到章节，跳过创建示例练习题'))
            return
        
        self.stdout.write(f'找到 {chapters.count()} 个章节')
        
        # 为所有章节创建练习题
        for chapter in chapters:
            try:
                # 删除已存在的练习题
                if hasattr(chapter, 'practice') and chapter.practice:
                    chapter.practice.delete()
                    self.stdout.write(self.style.WARNING(f"删除章节 '{chapter.title}' 的旧练习题"))
                
                book_title = chapter.book.title
                chapter_title = chapter.title
                
                # 为每个章节创建5道不同类型的练习题
                practices = []
                
                # 1. 选择题
                practice1 = Practice.objects.create(
                    chapter=chapter,
                    question_type='choice',
                    title=f'{chapter_title} - 选择题1',
                    description='测试你对本章基础概念的理解',
                    question=f'在《{book_title}》中，以下关于"{chapter_title}"的描述，哪个是正确的？',
                    difficulty=1,
                    order=1
                )
                self._add_choice_options(practice1)
                practices.append(practice1)
                
                # 2. 判断题
                practice2 = Practice.objects.create(
                    chapter=chapter,
                    question_type='choice',
                    title=f'{chapter_title} - 判断题1',
                    description='判断以下说法是否正确',
                    question=f'在《{book_title}》中，关于"{chapter_title}"的说法：本章内容是计算机科学的基础知识。',
                    difficulty=1,
                    order=2
                )
                self._add_judgment_options(practice2)
                practices.append(practice2)
                
                # 3. 填空题
                practice3 = Practice.objects.create(
                    chapter=chapter,
                    question_type='fill',
                    title=f'{chapter_title} - 填空题1',
                    description='请根据本章内容完成填空',
                    question=f'请填写关于"{chapter_title}"的关键概念：',
                    difficulty=2,
                    order=3
                )
                self._add_fill_blanks(practice3)
                practices.append(practice3)
                
                # 4. 代码补全题
                practice4 = Practice.objects.create(
                    chapter=chapter,
                    question_type='code_completion',
                    title=f'{chapter_title} - 代码补全题',
                    description='请补全以下代码',
                    question=f'补全代码以实现"{chapter_title}"中描述的功能',
                    code_template=self._get_code_template(chapter, 'completion'),
                    language='python',
                    difficulty=2,
                    order=4
                )
                self._add_test_cases(practice4, 'completion')
                practices.append(practice4)
                
                # 5. 编程题
                practice5 = Practice.objects.create(
                    chapter=chapter,
                    question_type='programming',
                    title=f'{chapter_title} - 编程题',
                    description='编写一个函数来实现指定功能',
                    question=f'请编写一个函数，实现"{chapter_title}"中提到的功能',
                    code_template=self._get_code_template(chapter, 'programming'),
                    language='python',
                    difficulty=3,
                    order=5
                )
                self._add_test_cases(practice5, 'programming')
                practices.append(practice5)
                
                self.stdout.write(self.style.SUCCESS(f"✅ 成功为章节 '{chapter_title}' 创建 {len(practices)} 道练习题"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ 为章节 '{chapter.title}' 创建练习题时出错: {str(e)}"))
                import traceback
                traceback.print_exc()
        
        self.stdout.write(self.style.SUCCESS('示例练习题数据创建完成！'))
    
    def _add_choice_options(self, practice):
        """添加选择题选项"""
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
    
    def _add_judgment_options(self, practice):
        """添加判断题选项"""
        PracticeChoiceOption.objects.create(
            practice=practice,
            content='正确',
            is_correct=True,
            order=1
        )
        PracticeChoiceOption.objects.create(
            practice=practice,
            content='错误',
            is_correct=False,
            order=2
        )
    
    def _add_fill_blanks(self, practice):
        """添加填空题空位"""
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
    
    def _get_code_template(self, chapter, question_type):
        """根据章节获取代码模板"""
        chapter_id = chapter.id
        
        if question_type == 'completion':
            templates = {
                1: 'def hello_world():\n    print("_____")\n\nhello_world()',
                2: 'import os\n\ndef list_files():\n    files = os.listdir("_____")\n    return files',
                3: 'def calculate_average(scores):\n    total = sum(scores)\n    average = _____\n    return average',
                4: 'import pandas as pd\n\ndef count_missing(df):\n    missing = df.isnull()._____()\n    return missing',
                5: 'import numpy as np\n\ndef calculate_correlation(x, y):\n    corr = np.corrcoef(x, y)[_____][1]\n    return corr',
                6: 'import matplotlib.pyplot as plt\n\ndef create_bar_chart(labels, values):\n    plt.bar(labels, values)\n    plt._____("bar_chart.png")',
                7: 'from textblob import TextBlob\n\ndef analyze_sentiment(text):\n    blob = TextBlob(text)\n    sentiment = blob.sentiment._____\n    return sentiment',
                8: 'from sklearn.linear_model import LinearRegression\n\ndef train_model(X, y):\n    model = LinearRegression()\n    model._____(X, y)\n    return model',
                9: 'import numpy as np\n\ndef sigmoid(x):\n    return 1 / (1 + np.exp(-_____))'
            }
        else:
            templates = {
                1: 'def add_numbers(a, b):\n    # 在这里编写你的代码\n    pass',
                2: 'def get_python_files(folder):\n    # 在这里编写你的代码\n    pass',
                3: 'def calculate_student_average(scores):\n    # 在这里编写你的代码\n    pass',
                4: 'def count_missing_values(df):\n    # 在这里编写你的代码\n    pass',
                5: 'def calculate_correlation_coefficient(x, y):\n    # 在这里编写你的代码\n    pass',
                6: 'def create_simple_bar_chart(labels, values, filename):\n    # 在这里编写你的代码\n    pass',
                7: 'def simple_sentiment_analysis(text):\n    # 在这里编写你的代码\n    pass',
                8: 'def simple_linear_regression(X, y):\n    # 在这里编写你的代码\n    pass',
                9: 'def simple_neural_network(inputs, weights, bias):\n    # 在这里编写你的代码\n    pass'
            }
        
        return templates.get(chapter_id, templates[1])
    
    def _add_test_cases(self, practice, question_type):
        """添加测试用例"""
        chapter_id = practice.chapter.id
        
        if question_type == 'completion':
            test_cases = {
                1: [{'input_data': {}, 'expected_output': 'Hello, World!'}],
                2: [{'input_data': {}, 'expected_output': 'py文件列表'}],
                3: [{'input_data': {}, 'expected_output': '平均分'}],
                4: [{'input_data': {}, 'expected_output': '缺失值数量'}],
                5: [{'input_data': {}, 'expected_output': '相关系数'}],
                6: [{'input_data': {}, 'expected_output': 'bar_chart.png'}],
                7: [{'input_data': {}, 'expected_output': '情感分数'}],
                8: [{'input_data': {}, 'expected_output': '训练好的模型'}],
                9: [{'input_data': {}, 'expected_output': '激活值'}]
            }
        else:
            test_cases = {
                1: [
                    {'input_data': {'a': 5, 'b': 3}, 'expected_output': 8},
                    {'input_data': {'a': 10, 'b': 20}, 'expected_output': 30},
                    {'input_data': {'a': -5, 'b': 10}, 'expected_output': 5}
                ],
                2: [
                    {'input_data': {'folder': '.'}, 'expected_output': 'py文件列表'},
                    {'input_data': {'folder': '/home'}, 'expected_output': 'py文件列表'}
                ],
                3: [
                    {'input_data': {'scores': [85, 92, 88]}, 'expected_output': 88.33},
                    {'input_data': {'scores': [90, 95, 100]}, 'expected_output': 95.0}
                ],
                4: [
                    {'input_data': {'df': 'dataframe'}, 'expected_output': '缺失值数量'},
                    {'input_data': {'df': 'dataframe'}, 'expected_output': '缺失值数量'}
                ],
                5: [
                    {'input_data': {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}, 'expected_output': 1.0},
                    {'input_data': {'x': [1, 2, 3], 'y': [2, 4, 6]}, 'expected_output': 1.0}
                ],
                6: [
                    {'input_data': {'labels': ['A', 'B', 'C'], 'values': [10, 20, 15], 'filename': 'chart.png'}, 'expected_output': 'chart.png'}
                ],
                7: [
                    {'input_data': {'text': '这个产品非常好，我很喜欢！'}, 'expected_output': '正面'},
                    {'input_data': {'text': '这个产品很差，我不喜欢。'}, 'expected_output': '负面'}
                ],
                8: [
                    {'input_data': {'X': [[1], [2], [3]], 'y': [2, 4, 6]}, 'expected_output': '模型参数'},
                    {'input_data': {'X': [[1], [2]], 'y': [2, 4]}, 'expected_output': '模型参数'}
                ],
                9: [
                    {'input_data': {'inputs': [1.0, 2.0, 3.0], 'weights': [0.1, 0.2, 0.3], 'bias': 0.5}, 'expected_output': 1.7},
                    {'input_data': {'inputs': [1.0, 1.0], 'weights': [0.5, 0.5], 'bias': 0.0}, 'expected_output': 1.0}
                ]
            }
        
        cases = test_cases.get(chapter_id, test_cases[1])
        for i, case in enumerate(cases):
            TestCase.objects.create(
                practice=practice,
                input_data=case['input_data'],
                expected_output=case['expected_output'],
                order=i + 1
            )
