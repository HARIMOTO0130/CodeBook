"""代码沙盒相关视图函数"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# 支持的编程语言及其初始代码模板
CODE_TEMPLATES = {
    'python': '''# Python 初始代码
print("欢迎使用Python编程!")

# 这里是一些示例代码:
x = 10
y = 20
print(f"x + y = {x + y}")

# 尝试修改这段代码，体验Python的强大功能!''',
    'javascript': '''// JavaScript 初始代码
console.log("欢迎使用JavaScript编程!");

// 这里是一些示例代码:
let x = 10;
let y = 20;
console.log(`x + y = ${x + y}`);

// 尝试修改这段代码，体验JavaScript的强大功能!''',
    'java': '''// Java 初始代码
public class Main {
    public static void main(String[] args) {
        System.out.println("欢迎使用Java编程!");
        
        // 这里是一些示例代码:
        int x = 10;
        int y = 20;
        System.out.println("x + y = " + (x + y));
        
        // 尝试修改这段代码，体验Java的强大功能!
    }
}''',
    'c': '''// C 初始代码
#include <stdio.h>

int main() {
    printf("欢迎使用C语言编程!\n");
    
    // 这里是一些示例代码:
    int x = 10;
    int y = 20;
    printf("x + y = %d\n", x + y);
    
    // 尝试修改这段代码，体验C语言的强大功能!
    
    return 0;
}''',
    'cpp': '''// C++ 初始代码
#include <iostream>

int main() {
    std::cout << "欢迎使用C++编程!" << std::endl;
    
    // 这里是一些示例代码:
    int x = 10;
    int y = 20;
    std::cout << "x + y = " << (x + y) << std::endl;
    
    // 尝试修改这段代码，体验C++的强大功能!
    
    return 0;
}''',
    'html': '''<!-- HTML 初始代码 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML示例</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        p {
            color: #666;
        }
    </style>
</head>
<body>
    <h1>欢迎使用HTML编程!</h1>
    <p>这是一个简单的HTML示例页面。</p>
    <script>
        // 可以在这里添加JavaScript代码
        console.log("HTML页面加载完成");
    </script>
</body>
</html>''',
    'css': '''/* CSS 初始代码 */
/* 欢迎使用CSS编程! */

/* 这里是一些示例代码: */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f0f0f0;
}

h1 {
    color: #333;
    text-align: center;
    padding: 20px 0;
}

p {
    color: #666;
    font-size: 16px;
    line-height: 1.5;
    margin: 0 20px 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

/* 尝试修改这段代码，体验CSS的强大功能! */'''
}

# 支持的编程语言列表
SUPPORTED_LANGUAGES = list(CODE_TEMPLATES.keys())


@api_view(['GET'])
@permission_classes([AllowAny])
def get_languages(request):
    """
    获取支持的编程语言列表
    无需认证即可访问
    """
    try:
        return Response({
            'languages': SUPPORTED_LANGUAGES,
            'default': SUPPORTED_LANGUAGES[0] if SUPPORTED_LANGUAGES else None
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'获取语言列表失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_code_template(request, language):
    """
    根据选择的编程语言获取对应的初始代码模板
    无需认证即可访问
    """
    try:
        # 将语言转换为小写以保持一致性
        language = language.lower()
        
        # 检查语言是否支持
        if language not in SUPPORTED_LANGUAGES:
            return Response(
                {'error': f'不支持的编程语言: {language}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 返回对应的代码模板
        return Response(
            {
                'language': language,
                'template': CODE_TEMPLATES[language],
                'description': f'{language.upper()} 初始代码模板'
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'获取代码模板失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_language(request):
    """
    验证选择的编程语言是否支持
    无需认证即可访问
    """
    try:
        language = request.data.get('language', '').lower()
        
        if not language:
            return Response(
                {'error': '未提供编程语言'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_supported = language in SUPPORTED_LANGUAGES
        
        response_data = {
            'language': language,
            'is_supported': is_supported
        }
        
        # 如果支持，同时返回代码模板
        if is_supported:
            response_data['template'] = CODE_TEMPLATES[language]
            
        return Response(
            response_data,
            status=status.HTTP_200_OK if is_supported else status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'验证语言失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )