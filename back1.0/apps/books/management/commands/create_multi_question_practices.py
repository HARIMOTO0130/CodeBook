from django.core.management.base import BaseCommand
from apps.books.models import Chapter, Practice
import json


class Command(BaseCommand):
    help = '创建包含6道题的练习题数据，每个章节一个练习题集'

    def handle(self, *args, **options):
        """创建包含6道题的练习题数据"""
        
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
                chapter.practices.all().delete()
                self.stdout.write(self.style.WARNING(f"删除章节 '{chapter.title}' 的旧练习题"))
                
                book_title = chapter.book.title
                chapter_title = chapter.title
                
                # 创建包含6道题的练习题集
                practice = Practice.objects.create(
                    chapter=chapter,
                    title=f'{chapter_title} - 练习题集',
                    description=f'《{book_title}》{chapter_title}的练习题，包含6道不同类型的题目',
                    questions=self._generate_questions(chapter, book_title, chapter_title),
                    language='python',
                    difficulty=2,
                    order=1
                )
                
                self.stdout.write(self.style.SUCCESS(f"成功为章节 '{chapter_title}' 创建练习题集，包含6道题"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"为章节 '{chapter.title}' 创建练习题失败: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('所有练习题创建完成！'))
    
    def _generate_questions(self, chapter, book_title, chapter_title):
        """生成6道不同类型的题目"""
        questions = []
        
        # 1. 选择题
        questions.append({
            'type': 'choice',
            'title': f'{chapter_title} - 选择题',
            'description': '测试你对本章基础概念的理解',
            'question': f'在《{book_title}》中，以下关于"{chapter_title}"的描述，哪个是正确的？',
            'options': [
                {'content': '这是一个基础概念，涵盖了本章的核心内容', 'is_correct': True},
                {'content': '这是一个错误的描述，与本章内容无关', 'is_correct': False},
                {'content': '这是一个不完整的描述，缺少关键信息', 'is_correct': False},
                {'content': '这是一个过时的描述，已被更新', 'is_correct': False}
            ],
            'difficulty': 1,
            'order': 1
        })
        
        # 2. 判断题
        questions.append({
            'type': 'choice',
            'title': f'{chapter_title} - 判断题',
            'description': '判断以下说法是否正确',
            'question': f'在《{book_title}》中，关于"{chapter_title}"的说法：本章内容是计算机科学的基础知识。',
            'options': [
                {'content': '正确', 'is_correct': True},
                {'content': '错误', 'is_correct': False}
            ],
            'difficulty': 1,
            'order': 2
        })
        
        # 3. 填空题
        questions.append({
            'type': 'fill',
            'title': f'{chapter_title} - 填空题',
            'description': '请根据本章内容完成填空',
            'question': f'请填写关于"{chapter_title}"的关键概念：\n\n在计算机科学中，____是____的基础。',
            'blanks': [
                {'prompt': '第一个空', 'placeholder': '请输入答案', 'correct_answer': '数据结构'},
                {'prompt': '第二个空', 'placeholder': '请输入答案', 'correct_answer': '算法设计'}
            ],
            'difficulty': 2,
            'order': 3
        })
        
        # 4. 代码补全题
        questions.append({
            'type': 'code_completion',
            'title': f'{chapter_title} - 代码补全题',
            'description': '请补全以下代码',
            'question': f'补全代码以实现"{chapter_title}"中描述的功能',
            'code_template': self._get_code_template(chapter, 'completion'),
            'language': 'python',
            'difficulty': 2,
            'order': 4
        })
        
        # 5. 编程题1
        questions.append({
            'type': 'programming',
            'title': f'{chapter_title} - 编程题1',
            'description': '编写一个函数来实现指定功能',
            'question': f'请编写一个函数，实现"{chapter_title}"中提到的功能',
            'code_template': self._get_code_template(chapter, 'programming'),
            'language': 'python',
            'difficulty': 3,
            'order': 5
        })
        
        # 6. 编程题2
        questions.append({
            'type': 'programming',
            'title': f'{chapter_title} - 编程题2',
            'description': '编写一个函数来解决实际问题',
            'question': f'基于"{chapter_title}"的知识，编写一个函数解决以下问题',
            'code_template': self._get_code_template(chapter, 'programming2'),
            'language': 'python',
            'difficulty': 3,
            'order': 6
        })
        
        return questions
    
    def _get_code_template(self, chapter, template_type):
        """根据章节和模板类型生成代码模板"""
        chapter_lower = chapter.title.lower()
        
        if 'python' in chapter_lower or '基础' in chapter_lower:
            if template_type == 'completion':
                return '''def process_data(data):
    """
    处理数据并返回结果
    """
    # 请补全以下代码
    result = []
    for item in data:
        # 在这里添加你的代码
        pass
    
    return result'''
            elif template_type == 'programming':
                return '''def calculate_average(numbers):
    """
    计算数字列表的平均值
    
    参数:
        numbers: 数字列表
        
    返回:
        平均值
    """
    # 请实现这个函数
    pass'''
            elif template_type == 'programming2':
                return '''def find_max_min(numbers):
    """
    找到数字列表中的最大值和最小值
    
    参数:
        numbers: 数字列表
        
    返回:
        (最大值, 最小值) 的元组
    """
    # 请实现这个函数
    pass'''
        
        elif 'java' in chapter_lower or '面向对象' in chapter_lower:
            if template_type == 'completion':
                return '''public class DataProcessor {
    public List<Integer> processData(List<Integer> data) {
        // 请补全以下代码
        List<Integer> result = new ArrayList<>();
        for (Integer item : data) {
            // 在这里添加你的代码
        }
        return result;
    }
}'''
            elif template_type == 'programming':
                return '''public class Calculator {
    public double calculateAverage(List<Double> numbers) {
        // 请实现这个方法
        return 0.0;
    }
}'''
            elif template_type == 'programming2':
                return '''public class NumberUtils {
    public int[] findMaxMin(int[] numbers) {
        // 请实现这个方法，返回 [最大值, 最小值]
        return new int[2];
    }
}'''
        
        elif 'javascript' in chapter_lower or 'web' in chapter_lower:
            if template_type == 'completion':
                return '''function processData(data) {
    /**
     * 处理数据并返回结果
     */
    const result = [];
    data.forEach(item => {
        // 请补全以下代码
    });
    return result;
}'''
            elif template_type == 'programming':
                return '''function calculateAverage(numbers) {
    /**
     * 计算数字数组的平均值
     * @param {number[]} numbers - 数字数组
     * @returns {number} 平均值
     */
    // 请实现这个函数
}'''
            elif template_type == 'programming2':
                return '''function findMaxMin(numbers) {
    /**
     * 找到数字数组中的最大值和最小值
     * @param {number[]} numbers - 数字数组
     * @returns {[number, number]} [最大值, 最小值]
     */
    // 请实现这个函数
}'''
        
        elif 'c++' in chapter_lower or 'cpp' in chapter_lower:
            if template_type == 'completion':
                return '''#include <vector>
#include <algorithm>

std::vector<int> processData(const std::vector<int>& data) {
    // 请补全以下代码
    std::vector<int> result;
    for (int item : data) {
        // 在这里添加你的代码
    }
    return result;
}'''
            elif template_type == 'programming':
                return '''double calculateAverage(const std::vector<double>& numbers) {
    // 请实现这个函数
    return 0.0;
}'''
            elif template_type == 'programming2':
                return '''std::pair<int, int> findMaxMin(const std::vector<int>& numbers) {
    // 请实现这个函数，返回 {最大值, 最小值}
    return {0, 0};
}'''
        
        else:
            # 默认Python模板
            if template_type == 'completion':
                return '''def process_data(data):
    """
    处理数据并返回结果
    """
    # 请补全以下代码
    result = []
    for item in data:
        # 在这里添加你的代码
        pass
    
    return result'''
            elif template_type == 'programming':
                return '''def calculate_average(numbers):
    """
    计算数字列表的平均值
    
    参数:
        numbers: 数字列表
        
    返回:
        平均值
    """
    # 请实现这个函数
    pass'''
            elif template_type == 'programming2':
                return '''def find_max_min(numbers):
    """
    找到数字列表中的最大值和最小值
    
    参数:
        numbers: 数字列表
        
    返回:
        (最大值, 最小值) 的元组
    """
    # 请实现这个函数
    pass'''
