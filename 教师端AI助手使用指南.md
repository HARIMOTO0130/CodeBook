# 教师端AI助手使用指南

## 功能概述

教师端AI助手是一个专门为教师设计的智能助手，可以基于学生数据提供个性化的教学建议和分析。

## 核心特性

### 1. 学生数据集成
- **学生选择器**：教师可以选择特定学生，AI将基于该学生的学习数据进行分析
- **班级选择器**：教师可以选择班级，AI将基于班级整体数据进行分析
- **自动上下文**：选择学生或班级后，AI会自动获取相关学习数据作为上下文

### 2. 智能分析能力
- 学生学习进度分析
- 练习记录统计
- AI使用情况追踪
- 个性化教学建议
- 班级整体情况分析

## 后端API接口

### 教师端AI助手接口
```
POST /api/teacher/ai-assistant/
```

**请求参数：**
```json
{
  "question": "分析这个学生的学习情况",
  "session_id": "可选，会话ID",
  "student_id": "可选，学生ID",
  "class_id": "可选，班级ID",
  "context": {}
}
```

**响应示例：**
```json
{
  "question": "分析这个学生的学习情况",
  "answer": "根据该学生的学习数据...",
  "session_id": "uuid",
  "response_time": 1.23,
  "context_used": {
    "has_student_context": true,
    "has_class_context": false
  }
}
```

## 前端集成方式

### 1. 在教师端页面中使用

```vue
<template>
  <div>
    <!-- 只在教师端路由显示 -->
    <TeacherAIAssistant v-if="isTeacherRoute" />
  </div>
</template>

<script>
import TeacherAIAssistant from '@/teacher/components/TeacherAIAssistant.vue'

export default {
  components: {
    TeacherAIAssistant
  },
  computed: {
    isTeacherRoute() {
      return this.$route.path.startsWith('/teacher/')
    }
  }
}
</script>
```

### 2. 在App.vue中条件渲染

```vue
<template>
  <!-- 学生端AI助手 -->
  <div v-if="isStudentRoute" class="ai-assistant">
    <!-- 学生端样式 -->
  </div>
  
  <!-- 教师端AI助手 - 使用不同的组件和样式 -->
  <TeacherAIAssistant v-if="isTeacherRoute" />
</template>
```

### 3. 样式隔离

使用CSS类名前缀确保样式只在教师端生效：

```css
/* 教师端专用样式 - 使用 .teacher- 前缀 */
.teacher-ai-assistant {
  /* 只在教师端显示 */
}

/* 学生端样式 - 使用不同的类名 */
.ai-assistant {
  /* 只在学生端显示 */
}
```

## 样式特点

### 教师端专用视觉标识
1. **紫色渐变主题**：使用 `#667eea` 到 `#764ba2` 的渐变，区别于学生端
2. **教师图标**：使用 👨‍🏫 图标标识
3. **"教师专用"徽章**：在头部显示明显的标识
4. **数据上下文提示**：显示"基于XX数据"的提示

### 关键样式类
- `.teacher-ai-assistant` - 主容器
- `.teacher-header` - 教师端头部
- `.teacher-badge` - "教师专用"徽章
- `.teacher-quick-btn` - 教师端快速问题按钮
- `.context-badge` - 数据上下文提示

## 使用示例

### 示例1：分析单个学生
1. 在学生详情页面，选择学生
2. 提问："这个学生的学习情况如何？"
3. AI会基于该学生的学习进度、练习记录等数据进行分析

### 示例2：分析班级整体情况
1. 在班级详情页面，选择班级
2. 提问："这个班级的整体学习进度如何？"
3. AI会基于班级所有学生的数据进行分析

### 示例3：获取教学建议
1. 选择学生或班级（可选）
2. 提问："推荐适合这个班级的教学方法"
3. AI会基于数据提供个性化建议

## 权限控制

- 只有教师角色可以访问 `/api/teacher/ai-assistant/` 接口
- 教师只能访问其班级的学生数据
- 所有数据访问都经过权限验证

## 注意事项

1. **数据隐私**：确保教师只能访问其权限范围内的学生数据
2. **样式隔离**：使用条件渲染和CSS类名前缀确保样式只在教师端显示
3. **性能优化**：学生和班级列表可以缓存，避免频繁请求
4. **错误处理**：妥善处理API请求失败的情况

## 扩展功能建议

1. **历史记录**：保存教师的AI交互历史
2. **常用问题**：记录教师常用的分析问题
3. **数据导出**：支持导出AI分析结果
4. **批量分析**：支持同时分析多个学生
