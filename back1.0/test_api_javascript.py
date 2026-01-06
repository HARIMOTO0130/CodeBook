import requests
import json

# API接口URL
api_url = 'http://localhost:8000/api/books/chapters/practices-by-book/'

def test_api_javascript_practices():
    """测试API接口是否正确返回JavaScript练习题数据"""
    try:
        # 发送GET请求
        response = requests.get(api_url)
        
        if response.status_code == 200:
            print("✅ API接口调用成功")
            
            # 解析响应数据
            data = response.json()
            
            # 统计JavaScript练习题数量
            javascript_count = 0
            
            # 遍历所有书籍
            for book in data:
                book_title = book.get('title', '未知书籍')
                print(f"\n书籍: {book_title}")
                
                # 遍历书籍中的所有章节
                for chapter in book.get('chapters', []):
                    chapter_title = chapter.get('title', '未知章节')
                    
                    # 检查是否有练习题
                    if 'practice' in chapter:
                        practice = chapter['practice']
                        practice_title = practice.get('title', '未知练习题')
                        language = practice.get('language', '未知语言')
                        
                        print(f"  章节: {chapter_title} - 练习题: {practice_title} - 语言: {language}")
                        
                        # 如果是JavaScript练习题，增加计数
                        if language == 'javascript':
                            javascript_count += 1
            
            print(f"\n✅ 总共找到 {javascript_count} 个JavaScript语言的练习题")
            
            # 检查是否有JavaScript练习题
            if javascript_count > 0:
                print("✅ API接口已正确返回JavaScript练习题数据")
                return True
            else:
                print("❌ API接口未返回JavaScript练习题数据")
                return False
        else:
            print(f"❌ API接口调用失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_javascript_practices()
