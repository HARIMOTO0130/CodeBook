import requests
import json

# 测试获取练习题API
def test_practice_api():
    # 设置API基础URL
    base_url = 'http://localhost:8000/api/student/books/chapters'
    
    # 测试章节ID列表（可以根据实际情况修改）
    chapter_ids = [19, 20, 21]  # 第1章、第2章、第3章
    
    for chapter_id in chapter_ids:
        url = f'{base_url}/{chapter_id}/practice/'
        print(f"\n=== 测试章节 {chapter_id} 的练习题API ===")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # 解析JSON响应
            data = response.json()
            
            # 打印响应基本信息
            print(f"API状态码: {response.status_code}")
            print(f"响应数据类型: {type(data)}")
            print(f"响应数据结构: {list(data.keys())}")
            
            # 检查是否有questions字段
            if 'questions' in data:
                print(f"问题数量: {len(data['questions'])}")
                
                # 打印每个问题的详细信息
                for i, question in enumerate(data['questions']):
                    print(f"\n问题 {i+1}:")
                    print(f"  类型: {question.get('type')}")
                    print(f"  题干: {question.get('content')}")
                    print(f"  字段列表: {list(question.keys())}")
                    
                    # 检查选择题的选项字段
                    if question.get('type') == 'choice':
                        if 'choice_options' in question:
                            print(f"  选择题选项字段: choice_options")
                            print(f"  选项数量: {len(question['choice_options'])}")
                            for j, option in enumerate(question['choice_options']):
                                print(f"    选项 {j+1}: {option.get('content')}, 正确: {option.get('is_correct')}")
                        elif 'options' in question:
                            print(f"  选择题选项字段: options")
                            print(f"  选项数量: {len(question['options'])}")
                            for j, option in enumerate(question['options']):
                                print(f"    选项 {j+1}: {option.get('content')}, 正确: {option.get('is_correct')}")
                        else:
                            print(f"  ❌ 选择题没有找到选项字段")
                    
                    # 检查判断题
                    elif question.get('type') == 'true_false':
                        print(f"  正确答案: {question.get('correct_answer')}")
                    
                    # 检查填空题
                    elif question.get('type') == 'fill':
                        if 'fill_blanks' in question:
                            print(f"  填空题字段: fill_blanks")
                            print(f"  空数量: {len(question['fill_blanks'])}")
                            for j, blank in enumerate(question['fill_blanks']):
                                print(f"    空 {j+1}: {blank.get('prompt')}, 正确答案: {blank.get('correct_answer')}")
                        else:
                            print(f"  ❌ 填空题没有找到fill_blanks字段")
            else:
                print("❌ 响应中没有找到questions字段")
                print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"响应内容: {response.text}")

if __name__ == '__main__':
    test_practice_api()