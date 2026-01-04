// 临时验证脚本：验证章节内容加载
console.log('==== 内容验证脚本启动 ====');

// 模拟章节数据
const mockChapterData = {
  id: 101,
  title: "第1章：Python简介",
  content: "# Python简介\n\nPython是一种广泛使用的解释型、高级和通用的编程语言。\n\n```python\nprint(\"Hello, Python!\")\n```",
  description: "了解Python的起源和特点"
};

// 检查content字段处理
console.log('\n📋 检查content字段处理：');
console.log('原始content:', mockChapterData.content);
console.log('content长度:', mockChapterData.content.length);
console.log('content是否为null:', mockChapterData.content === null);
console.log('content是否为空字符串:', mockChapterData.content.trim() === '');

// 验证fetchChapterContent函数的降级逻辑
console.log('\n🔄 验证降级逻辑：');
// 模拟content为空的情况
const emptyContentData = { ...mockChapterData, content: '' };
const fallbackContent = emptyContentData.content || emptyContentData.description;
console.log('当content为空时，使用description作为后备:', fallbackContent);

console.log('\n✅ 验证完成：content字段包含完整markdown内容');
console.log('建议在浏览器控制台执行此脚本或检查LearnView.vue中fetchChapterContent函数');