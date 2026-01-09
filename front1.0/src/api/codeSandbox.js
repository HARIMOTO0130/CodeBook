import axios from 'axios';

// 基础URL配置
const BASE_URL = import.meta.env.VITE_APP_API_BASE_URL || '/api';

/**
 * 获取支持的编程语言列表
 * @returns {Promise<Object>} 包含语言列表和默认语言的对象
 */
export const getSupportedLanguages = async () => {
  console.log('getSupportedLanguages函数被调用');
  console.log('使用的API URL:', `${BASE_URL}/learning/code-sandbox/languages/`);
  try {
    const response = await axios.get(`${BASE_URL}/learning/code-sandbox/languages/`);
    console.log('API请求成功，响应数据:', response.data);
    return response.data;
  } catch (error) {
    console.error('获取支持的编程语言失败:', error);
    if (error.response) {
      console.error('错误响应状态:', error.response.status);
      console.error('错误响应数据:', error.response.data);
    } else if (error.request) {
      console.error('没有收到响应:', error.request);
    } else {
      console.error('请求配置错误:', error.message);
    }
    console.error('错误配置:', error.config);
    // 返回默认值以确保应用正常运行
    return {
      languages: ['javascript', 'python'],
      default: 'javascript'
    };
  }
};

/**
 * 根据编程语言获取初始代码模板
 * @param {string} language 编程语言名称
 * @returns {Promise<Object>} 包含语言、代码模板和描述的对象
 */
export const getCodeTemplate = async (language) => {
  try {
    const response = await axios.get(`${BASE_URL}/learning/code-sandbox/template/${language}/`);
    return response.data;
  } catch (error) {
    console.error(`获取${language}代码模板失败:`, error);
    // 返回对应语言的默认模板
    return {
      language,
      template: getDefaultTemplate(language),
      description: `${language.toUpperCase()} 默认代码模板`
    };
  }
};

/**
 * 验证选择的编程语言是否支持
 * @param {string} language 编程语言名称
 * @returns {Promise<Object>} 包含语言支持状态的对象
 */
export const validateLanguage = async (language) => {
  try {
    const response = await axios.post(`${BASE_URL}/learning/code-sandbox/validate/`, { language });
    return response.data;
  } catch (error) {
    console.error(`验证${language}语言失败:`, error);
    return {
      language,
      is_supported: false
    };
  }
};

/**
 * 获取默认代码模板
 * @param {string} language 编程语言名称
 * @returns {string} 默认代码模板
 */
export function getDefaultTemplate(language) {
  const defaultTemplates = {
    javascript: `// JavaScript 默认模板
console.log("欢迎使用JavaScript编程!");

// 示例代码
let greeting = "Hello, World!";
console.log(greeting);`,
    python: `# Python 默认模板
print("欢迎使用Python编程!")

# 示例代码
greeting = "Hello, World!"
print(greeting)`,
    java: `// Java 默认模板
public class Main {
    public static void main(String[] args) {
        System.out.println("欢迎使用Java编程!");
        
        // 示例代码
        String greeting = "Hello, World!";
        System.out.println(greeting);
    }
}`,
    cpp: `// C++ 默认模板
#include <iostream>

int main() {
    std::cout << "欢迎使用C++编程!" << std::endl;
    
    // 示例代码
    std::string greeting = "Hello, World!";
    std::cout << greeting << std::endl;
    
    return 0;
}`,
    c: `// C 默认模板
#include <stdio.h>

int main() {
    printf("欢迎使用C语言编程!\n");
    
    // 示例代码
    char greeting[] = "Hello, World!";
    printf("%s\n", greeting);
    
    return 0;
}`,
    csharp: `// C# 默认模板
using System;

class Program {
    static void Main() {
        Console.WriteLine("欢迎使用C#编程!");
        
        // 示例代码
        string greeting = "Hello, World!";
        Console.WriteLine(greeting);
    }
}`,
    php: `<?php
// PHP 默认模板
echo "欢迎使用PHP编程!\n";

// 示例代码
$greeting = "Hello, World!";
echo $greeting . "\n";`,
    ruby: `# Ruby 默认模板
puts "欢迎使用Ruby编程!"

# 示例代码
greeting = "Hello, World!"
puts greeting`,
    go: `// Go 默认模板
package main

import "fmt"

func main() {
    fmt.Println("欢迎使用Go编程!")
    
    // 示例代码
    greeting := "Hello, World!"
    fmt.Println(greeting)
}`,
    rust: `// Rust 默认模板
fn main() {
    println!("欢迎使用Rust编程!");
    
    // 示例代码
    let greeting = "Hello, World!";
    println!("{}", greeting);
}`,
    html: `<!-- HTML 默认模板 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>欢迎使用HTML</title>
</head>
<body>
    <h1>欢迎使用HTML编程!</h1>
    <p>这是一个示例HTML页面。</p>
</body>
</html>`,
    css: `/* CSS 默认模板 */
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

/* 尝试修改这段代码，体验CSS的强大功能! */`
  };
  
  // 如果找不到指定语言的模板，返回一个通用模板
  return defaultTemplates[language.toLowerCase()] || `// ${language} 代码
// 开始编写你的代码`;
}