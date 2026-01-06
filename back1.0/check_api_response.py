import requests
import json

# API接口URL
api_url = 'http://localhost:8000/api/books/chapters/practices-by-book/'

def check_api_response():
    """查看API接口的完整响应数据结构"""
    try:
        # 发送GET请求
        response = requests.get(api_url)
        
        if response.status_code == 200:
            print("✅ API接口调用成功")
            
            # 解析响应数据
            data = response.json()
            
            print(f"\nAPI响应数据类型: {type(data)}")
            print(f"API响应数据长度: {len(data)}")
            
            # 打印前几个数据项的结构
            for i, item in enumerate(data[:3]):
                print(f"\n第{i+1}个数据项:")
                print(f"  键: {list(item.keys())}")
                
                # 如果是书籍数据，查看书籍结构
                if 'title' in item:
                    print(f"  书籍标题: {item.get('title')}")
                    print(f"  章节数量: {len(item.get('chapters', []))}")
                    
                    # 查看第一个章节的结构
                    if item.get('chapters'):
                        chapter = item['chapters'][0]
                        print(f"  第一个章节键: {list(chapter.keys())}")
                        print(f"  章节标题: {chapter.get('title')}")
                        
                        # 检查是否有练习题
                        if 'practice' in chapter:
                            practice = chapter['practice']
                            print(f"  练习题键: {list(practice.keys())}")
                            print(f"  练习题标题: {practice.get('title')}")
                            print(f"  练习题语言: {practice.get('language')}")
                            print(f"  练习题ID: {practice.get('id')}")
            
            # 保存完整响应到文件
            with open('api_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 完整API响应已保存到 api_response.json 文件")
            
            return True
        else:
            print(f"❌ API接口调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_api_response()
