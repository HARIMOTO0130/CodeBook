import { executeCode } from './src/api/api.js';

// 测试executeCode方法
async function testExecuteCode() {
  try {
    console.log('测试executeCode方法...');
    const result = await executeCode({
      language: 'python',
      code: 'print("Hello, World!")',
      input: ''
    });
    console.log('测试成功！');
    console.log('结果:', result);
  } catch (error) {
    console.error('测试失败！');
    console.error('错误:', error);
  }
}

testExecuteCode();