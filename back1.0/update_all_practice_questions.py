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

def update_all_practice_questions():
    """为所有练习题集更新完整的题目内容"""
    
    # 获取所有Practice对象
    practices = Practice.objects.all()
    
    if not practices.exists():
        print("没有找到练习题集")
        return
    
    print(f"找到 {practices.count()} 个练习题集")
    
    for practice in practices:
        try:
            chapter = practice.chapter
            book = chapter.book
            
            print(f"\n处理练习题集: {practice.title}")
            print(f"所属书籍: {book.title}, 章节: {chapter.title}")
            print(f"书籍ID: {book.id}, 章节ID: {chapter.id}, 章节顺序: {chapter.order}")
            
            # 使用章节顺序而不是章节ID来匹配题目内容
            chapter_num = chapter.order
            
            # 调试：查看要生成的内容
            print(f"\n调试信息：")
            print(f"选择题题干: {get_choice_question(book, chapter_num)}")
            print(f"选择题选项1: {get_choice_option(book, chapter_num, 1)}")
            print(f"选择题选项2: {get_choice_option(book, chapter_num, 2)}")
            
            # 根据章节主题生成完整的练习题
            questions = []
            
            # 1. 选择题
            choice_question = {
                "id": 1,
                "type": "choice",
                "title": "选择题",
                "question": get_choice_question(book, chapter_num),
                "options": [
                    {"id": 1, "content": get_choice_option(book, chapter_num, 1), "is_correct": False},
                    {"id": 2, "content": get_choice_option(book, chapter_num, 2), "is_correct": True},
                    {"id": 3, "content": get_choice_option(book, chapter_num, 3), "is_correct": False},
                    {"id": 4, "content": get_choice_option(book, chapter_num, 4), "is_correct": False}
                ],
                "difficulty": 1,
                "order": 1
            }
            questions.append(choice_question)
            
            # 2. 填空题
            fill_question = {
                "id": 2,
                "type": "fill",
                "title": "填空题",
                "question": get_fill_question(book, chapter_num),
                "blanks": [
                    {"id": 1, "correct_answer": get_fill_answer(book, chapter_num, 1), "placeholder": "第一空"},
                    {"id": 2, "correct_answer": get_fill_answer(book, chapter_num, 2), "placeholder": "第二空"}
                ],
                "difficulty": 2,
                "order": 2
            }
            questions.append(fill_question)
            
            # 3. 判断题 - 注意：这里将type从true_false改为Judgment以匹配前端期望
            true_false_question = {
                "id": 3,
                "type": "Judgment",
                "title": "判断题",
                "question": get_true_false_question(book, chapter_num),
                "correct_answer": get_true_false_answer(book, chapter_num),
                "difficulty": 1,
                "order": 3
            }
            questions.append(true_false_question)
            
            # 4. 代码补全题
            code_completion_question = {
                "id": 4,
                "type": "code_completion",
                "title": "代码补全题",
                "question": get_code_completion_question(book, chapter_num),
                "code_template": get_code_template(book, chapter_num, "completion"),
                "test_cases": get_test_cases(book, chapter_num, "completion"),
                "difficulty": 2,
                "order": 4
            }
            questions.append(code_completion_question)
            
            # 5. 编程题
            programming_question = {
                "id": 5,
                "type": "programming",
                "title": "编程题",
                "question": get_programming_question(book, chapter_num),
                "code_template": get_code_template(book, chapter_num, "programming"),
                "test_cases": get_test_cases(book, chapter_num, "programming"),
                "difficulty": 3,
                "order": 5
            }
            questions.append(programming_question)
            
            # 更新练习题集的questions字段
            practice.questions = questions
            practice.save()
            
            print(f"✅ 成功更新练习题集，添加了 {len(questions)} 道完整题目")
            
        except Exception as e:
            print(f"❌ 处理练习题集 {practice.title} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n所有练习题集的题目更新完成！")

def get_choice_question(book, chapter_num):
    """根据书籍和章节顺序生成选择题题目"""
    questions = {
        # 大学计算机基础与应用
        (1, 1): "在《大学计算机基础与应用》中，计算机的核心处理器是以下哪一项？",
        (1, 2): "在《大学计算机基础与应用》中，操作系统的主要功能不包括以下哪一项？",
        (1, 3): "在《大学计算机基础与应用》中，Excel中用于求和的函数是？",
        
        # 数据分析与可视化入门
        (2, 1): "在《数据分析与可视化入门》中，以下哪个不是常用的数据分析工具？",
        (2, 2): "在《数据分析与可视化入门》中，数据清洗的主要目的是？",
        (2, 3): "在《数据分析与可视化入门》中，以下哪种图表适合展示数据的分布情况？",
        
        # 人工智能与机器学习基础
        (3, 1): "在《人工智能与机器学习基础》中，以下哪项不是人工智能的应用领域？",
        (3, 2): "在《人工智能与机器学习基础》中，监督学习的特点是？",
        (3, 3): "在《人工智能与机器学习基础》中，神经网络的基本组成单元是？",
    }
    
    return questions.get((book.id, chapter_num), f"在《{book.title}》中，关于第{chapter_num}章的选择题")

def get_choice_option(book, chapter, option_num):
    """根据书籍、章节和选项编号生成选择题选项"""
    options = {
        # 大学计算机基础与应用 - 第1章 计算机基础知识
        (1, 1, 1): "内存条",
        (1, 1, 2): "CPU",
        (1, 1, 3): "硬盘",
        (1, 1, 4): "显示器",
        
        # 大学计算机基础与应用 - 第2章 操作系统基础
        (1, 2, 1): "进程管理",
        (1, 2, 2): "文字处理",
        (1, 2, 3): "内存管理",
        (1, 2, 4): "文件管理",
        
        # 大学计算机基础与应用 - 第3章 办公软件应用
        (1, 3, 1): "SUM",
        (1, 3, 2): "AVERAGE",
        (1, 3, 3): "MAX",
        (1, 3, 4): "MIN",
        
        # 数据分析与可视化入门 - 第1章 数据分析基础
        (2, 1, 1): "Python",
        (2, 1, 2): "Word",
        (2, 1, 3): "Excel",
        (2, 1, 4): "SQL",
        
        # 数据分析与可视化入门 - 第2章 数据分析方法与应用
        (2, 2, 1): "提高数据质量",
        (2, 2, 2): "增加数据量",
        (2, 2, 3): "改变数据格式",
        (2, 2, 4): "加密数据",
        
        # 数据分析与可视化入门 - 第3章 数据可视化技术
        (2, 3, 1): "条形图",
        (2, 3, 2): "折线图",
        (2, 3, 3): "饼图",
        (2, 3, 4): "直方图",
        
        # 人工智能与机器学习基础 - 第1章 人工智能概述
        (3, 1, 1): "自然语言处理",
        (3, 1, 2): "数据存储",
        (3, 1, 3): "计算机视觉",
        (3, 1, 4): "机器学习",
        
        # 人工智能与机器学习基础 - 第2章 机器学习基础
        (3, 2, 1): "需要标记数据",
        (3, 2, 2): "不需要标记数据",
        (3, 2, 3): "只能处理文本数据",
        (3, 2, 4): "不需要算法",
        
        # 人工智能与机器学习基础 - 第3章 深度学习入门
        (3, 3, 1): "神经元",
        (3, 3, 2): "层",
        (3, 3, 3): "激活函数",
        (3, 3, 4): "权重",
    }
    
    return options.get((book.id, chapter.id, option_num), f"选项{chr(ord('A') + option_num - 1)}")

def get_fill_question(book, chapter_num):
    """根据书籍和章节生成填空题题目"""
    questions = {
        (1, 1): "计算机系统由______和______两部分组成。",
        (1, 2): "操作系统的主要功能包括______管理、______管理和______管理。",
        (1, 3): "Word文档的扩展名是______，Excel文档的扩展名是______。",
        
        (2, 1): "数据分析的基本步骤包括数据收集、______、______和结果呈现。",
        (2, 2): "数据类型主要包括数值型、______和______。",
        (2, 3): "常用的数据可视化工具包括______、______和______。",
        
        (3, 1): "人工智能的三大核心技术包括机器学习、______和______。",
        (3, 2): "机器学习算法主要分为监督学习、______和______三大类。",
        (3, 3): "深度学习的特点是具有______层神经网络结构。",
    }
    
    return questions.get((book.id, chapter_num), f"关于第{chapter_num}章的填空题")

def get_fill_answer(book, chapter_num, blank_num):
    """根据书籍、章节和空白编号生成填空题答案"""
    answers = {
        # 大学计算机基础与应用 - 第1章 计算机基础知识
        (1, 1, 1): "硬件",
        (1, 1, 2): "软件",
        
        # 大学计算机基础与应用 - 第2章 操作系统基础
        (1, 2, 1): "进程",
        (1, 2, 2): "内存",
        (1, 2, 3): "文件",
        
        # 大学计算机基础与应用 - 第3章 办公软件应用
        (1, 3, 1): "docx",
        (1, 3, 2): "xlsx",
        
        # 数据分析与可视化入门 - 第1章 数据分析基础
        (2, 1, 1): "数据清洗",
        (2, 1, 2): "数据分析",
        
        # 数据分析与可视化入门 - 第2章 数据分析方法与应用
        (2, 2, 1): "文本型",
        (2, 2, 2): "日期型",
        
        # 数据分析与可视化入门 - 第3章 数据可视化技术
        (2, 3, 1): "Excel",
        (2, 3, 2): "Python",
        (2, 3, 3): "Tableau",
        
        # 人工智能与机器学习基础 - 第1章 人工智能概述
        (3, 1, 1): "自然语言处理",
        (3, 1, 2): "计算机视觉",
        
        # 人工智能与机器学习基础 - 第2章 机器学习基础
        (3, 2, 1): "无监督学习",
        (3, 2, 2): "强化学习",
        
        # 人工智能与机器学习基础 - 第3章 深度学习入门
        (3, 3, 1): "多层",
    }
    
    return answers.get((book.id, chapter_num, blank_num), f"答案{blank_num}")

def get_true_false_question(book, chapter_num):
    """根据书籍和章节生成判断题题目"""
    questions = {
        (1, 1): "计算机的基本存储单位是字节(Byte)。",
        (1, 2): "Windows是目前最流行的操作系统之一。",
        (1, 3): "PowerPoint主要用于文字处理。",
        
        (2, 1): "数据分析只能使用Python语言。",
        (2, 2): "数据可视化有助于更好地理解数据。",
        (2, 3): "饼图适合比较不同类别的数据大小。",
        
        (3, 1): "人工智能可以完全替代人类工作。",
        (3, 2): "机器学习需要大量的数据支持。",
        (3, 3): "深度学习是机器学习的一个分支。",
    }
    
    return questions.get((book.id, chapter_num), f"关于第{chapter_num}章的判断题")

def get_true_false_answer(book, chapter_num):
    """根据书籍和章节生成判断题答案"""
    answers = {
        (1, 1): True,
        (1, 2): True,
        (1, 3): False,
        
        (2, 1): False,
        (2, 2): True,
        (2, 3): True,
        
        (3, 1): False,
        (3, 2): True,
        (3, 3): True,
    }
    
    return answers.get((book.id, chapter_num), True)

def get_code_completion_question(book, chapter_num):
    """根据书籍和章节生成代码补全题题目"""
    questions = {
        (1, 1): "请补全以下Python代码，实现打印'Hello World'的功能。",
        (1, 2): "请补全以下代码，计算两个数的和。",
        (1, 3): "请补全以下Excel公式，计算A1到A10的平均值。",
        
        (2, 1): "请补全以下Python代码，使用pandas读取CSV文件。",
        (2, 2): "请补全以下代码，计算数据的平均值。",
        (2, 3): "请补全以下代码，绘制简单的折线图。",
        
        (3, 1): "请补全以下代码，定义一个简单的Python函数。",
        (3, 2): "请补全以下代码，实现简单的线性回归。",
        (3, 3): "请补全以下代码，定义一个简单的神经网络层。",
    }
    
    return questions.get((book.id, chapter_num), f"关于第{chapter_num}章的代码补全题")

def get_programming_question(book, chapter_num):
    """根据书籍和章节生成编程题题目"""
    questions = {
        (1, 1): "请编写一个Python函数，实现两个数的加法运算。",
        (1, 2): "请编写一个Python程序，打印1到100之间的所有偶数。",
        (1, 3): "请编写一个Python程序，统计一段文本中每个单词出现的频率。",
        
        (2, 1): "请编写一个Python程序，使用pandas读取CSV文件并显示前5行数据。",
        (2, 2): "请编写一个Python程序，计算数据的均值、中位数和标准差。",
        (2, 3): "请编写一个Python程序，使用matplotlib绘制柱状图。",
        
        (3, 1): "请编写一个Python程序，实现简单的线性搜索算法。",
        (3, 2): "请编写一个Python程序，实现简单的冒泡排序算法。",
        (3, 3): "请编写一个Python程序，实现简单的神经网络前向传播。",
    }
    
    return questions.get((book.id, chapter_num), f"关于第{chapter_num}章的编程题")

def get_code_template(book, chapter, question_type):
    """根据书籍、章节和题目类型生成代码模板"""
    templates = {
        # 大学计算机基础与应用
        (1, 1, "completion"): "print(______)",
        (1, 1, "programming"): "def add(a, b):\n    # 在这里编写你的代码\n    pass",
        
        (1, 2, "completion"): "def sum(a, b):\n    return ______",
        (1, 2, "programming"): "# 打印1到100之间的所有偶数\nfor i in range(1, 101):\n    # 在这里编写你的代码",
        
        (1, 3, "completion"): "=______(A1:A10)",
        (1, 3, "programming"): "text = \"Hello world hello python\"\n# 统计每个单词出现的频率\nword_count = {}\n# 在这里编写你的代码",
        
        # 数据分析与可视化入门
        (2, 1, "completion"): "import pandas as pd\ndf = pd.______(\"data.csv\")",
        (2, 1, "programming"): "import pandas as pd\n# 读取CSV文件并显示前5行数据\ndf = pd.read_csv(\"data.csv\")\n# 在这里编写你的代码",
        
        (2, 2, "completion"): "import numpy as np\navg = np.______(data)",
        (2, 2, "programming"): "import numpy as np\ndata = [10, 20, 30, 40, 50]\n# 计算平均值、中位数和标准差\n# 在这里编写你的代码",
        
        (2, 3, "completion"): "import matplotlib.pyplot as plt\nplt.______(x, y)\nplt.show()",
        (2, 3, "programming"): "import matplotlib.pyplot as plt\nlabels = ['A', 'B', 'C', 'D']\nvalues = [10, 20, 30, 40]\n# 绘制柱状图\n# 在这里编写你的代码",
        
        # 人工智能与机器学习基础
        (3, 1, "completion"): "def predict(x, w, b):\n    return ______ * x + b",
        (3, 1, "programming"): "# 实现简单的线性回归预测\nimport numpy as np\n\ndef linear_regression(x, y):\n    # 在这里编写你的代码\n    return w, b",
        
        (3, 2, "completion"): "from sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression()\nmodel.______(X_train, y_train)",
        (3, 2, "programming"): "# 使用scikit-learn进行分类任务\nfrom sklearn.datasets import load_iris\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\n\n# 加载数据\ndata = load_iris()\nX, y = data.data, data.target\n\n# 划分训练集和测试集\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n# 在这里编写你的代码",
        
        (3, 3, "completion"): "import tensorflow as tf\nlayer = tf.keras.layers.______(units=10, activation='relu')",
        (3, 3, "programming"): "# 使用TensorFlow定义一个简单的神经网络\nimport tensorflow as tf\n\n# 定义模型\nmodel = tf.keras.Sequential([\n    # 在这里编写你的代码\n])\n\n# 编译模型\nmodel.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])\n",
    }
    
    return templates.get((book.id, chapter.id, question_type), "# 在这里编写你的代码")

def get_test_cases(book, chapter, question_type):
    """根据书籍、章节和题目类型生成测试用例"""
    test_cases = {
        # 大学计算机基础与应用
        (1, 1, "completion"): [
            {"id": 1, "input": {}, "expected_output": "Hello World"}
        ],
        (1, 1, "programming"): [
            {"id": 1, "input": {"a": 1, "b": 2}, "expected_output": 3},
            {"id": 2, "input": {"a": -1, "b": 1}, "expected_output": 0}
        ],
        
        (1, 2, "completion"): [
            {"id": 1, "input": {"a": 3, "b": 5}, "expected_output": 8}
        ],
        (1, 2, "programming"): [
            {"id": 1, "input": {}, "expected_output": "2 4 6 8 ... 100"}
        ],
        
        (1, 3, "completion"): [
            {"id": 1, "input": {}, "expected_output": "AVERAGE"}
        ],
        (1, 3, "programming"): [
            {"id": 1, "input": {"text": "Hello world hello python"}, "expected_output": {"hello": 2, "world": 1, "python": 1}}
        ],
        
        # 数据分析与可视化入门
        (2, 1, "completion"): [
            {"id": 1, "input": {}, "expected_output": "read_csv"}
        ],
        (2, 1, "programming"): [
            {"id": 1, "input": {}, "expected_output": "DataFrame head"}
        ],
        
        (2, 2, "completion"): [
            {"id": 1, "input": {}, "expected_output": "mean"}
        ],
        (2, 2, "programming"): [
            {"id": 1, "input": {"data": [10, 20, 30, 40, 50]}, "expected_output": {"mean": 30, "median": 30, "std": 14.1421}}
        ],
        
        (2, 3, "completion"): [
            {"id": 1, "input": {}, "expected_output": "plot"}
        ],
        (2, 3, "programming"): [
            {"id": 1, "input": {}, "expected_output": "Bar chart displayed"}
        ],
        
        # 人工智能与机器学习基础
        (3, 1, "completion"): [
            {"id": 1, "input": {}, "expected_output": "w"}
        ],
        (3, 1, "programming"): [
            {"id": 1, "input": {"x": [1, 2, 3], "y": [2, 4, 6]}, "expected_output": {"w": 2, "b": 0}}
        ],
        
        (3, 2, "completion"): [
            {"id": 1, "input": {}, "expected_output": "fit"}
        ],
        (3, 2, "programming"): [
            {"id": 1, "input": {}, "expected_output": "Model trained with accuracy > 0.8"}
        ],
        
        (3, 3, "completion"): [
            {"id": 1, "input": {}, "expected_output": "Dense"}
        ],
        (3, 3, "programming"): [
            {"id": 1, "input": {}, "expected_output": "Neural network defined"}
        ],
    }
    
    # 默认测试用例
    default_test_cases = {
        "completion": [
            {"id": 1, "input": {}, "expected_output": "正确答案"}
        ],
        "programming": [
            {"id": 1, "input": {}, "expected_output": "程序运行正确"}
        ]
    }
    
    return test_cases.get((book.id, chapter.id, question_type), default_test_cases.get(question_type, []))

if __name__ == "__main__":
    update_all_practice_questions()
