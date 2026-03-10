<template>
  <div class="exercise-generator-component">
    <!-- 生成配置区域 -->
    <div class="config-section">
      <div class="config-header">
        <h3>习题生成配置</h3>
        <div class="config-actions">
          <button @click="loadExample" class="btn btn-secondary">加载示例</button>
          <button @click="clearConfig" class="btn btn-secondary">清空配置</button>
          <button @click="generateExercises" :disabled="isGenerating" class="btn btn-primary">
            {{ isGenerating ? '生成中...' : '生成习题' }}
          </button>
        </div>
      </div>

      <!-- 知识点输入 -->
      <div class="config-item">
        <label for="knowledge-points">知识点 <span class="required">*</span></label>
        <div class="knowledge-points-input">
          <div class="tags-container">
            <span 
              v-for="(point, index) in knowledgePoints" 
              :key="index"
              class="tag"
            >
              {{ point }}
              <button @click="removeKnowledgePoint(index)" class="tag-remove">×</button>
            </span>
          </div>
          <div class="input-group">
            <input 
              type="text" 
              v-model="newKnowledgePoint"
              @keyup.enter="addKnowledgePoint"
              placeholder="输入知识点并按回车"
              class="input"
            >
            <button @click="addKnowledgePoint" class="btn btn-sm btn-primary">添加</button>
          </div>
        </div>
      </div>

      <!-- 习题类型选择 -->
      <div class="config-item">
        <label for="exercise-type">习题类型 <span class="required">*</span></label>
        <select v-model="exerciseType" id="exercise-type" class="select">
          <option v-for="(type, key) in exerciseTypes" :key="key" :value="key">
            {{ type.name }}
          </option>
        </select>
      </div>

      <!-- 难度选择 -->
      <div class="config-item">
        <label for="difficulty">难度 <span class="required">*</span></label>
        <select v-model="difficulty" id="difficulty" class="select">
          <option v-for="(name, key) in difficultyLevels" :key="key" :value="key">
            {{ name }}
          </option>
        </select>
      </div>

      <!-- 数量选择 -->
      <div class="config-item">
        <label for="count">生成数量 <span class="required">*</span></label>
        <div class="number-input">
          <button @click="count = Math.max(1, count - 1)" class="btn btn-sm">-</button>
          <input 
            type="number" 
            v-model.number="count"
            min="1"
            max="20"
            class="input"
          >
          <button @click="count = Math.min(20, count + 1)" class="btn btn-sm">+</button>
        </div>
      </div>
    </div>

    <!-- 生成结果区域 -->
    <div class="result-section" v-if="generatedExercises.length > 0">
      <div class="result-header">
        <h3>生成结果</h3>
        <div class="result-info">
          <span>共生成 {{ generatedExercises.length }} 道习题</span>
          <button @click="exportExercises" class="btn btn-secondary">导出习题</button>
        </div>
      </div>

      <div class="exercises-list">
        <div 
          v-for="(exercise, index) in generatedExercises" 
          :key="exercise.id || index"
          class="exercise-card"
        >
          <div class="exercise-header">
            <div class="exercise-meta">
              <span class="exercise-type">{{ exercise.type_name }}</span>
              <span class="exercise-difficulty" :class="`difficulty-${exercise.difficulty}`">
                {{ exercise.difficulty_name }}
              </span>
              <span class="exercise-time">
                ⏱ {{ exercise.estimated_time }} 分钟
              </span>
            </div>
            <div class="exercise-actions">
              <button @click="previewExercise(exercise)" class="btn btn-sm btn-primary">
                预览
              </button>
            </div>
          </div>
          
          <div class="exercise-content">
            <p class="exercise-question">{{ exercise.question }}</p>
            
            <!-- 选择题选项 -->
            <div v-if="exercise.exercise_type === 'multiple_choice' && exercise.options" class="exercise-options">
              <div 
                v-for="(option, optIndex) in exercise.options" 
                :key="optIndex"
                class="option"
              >
                <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}.</span>
                <span class="option-text">{{ option }}</span>
              </div>
            </div>
            
            <!-- 编程题 -->
            <div v-if="exercise.exercise_type === 'coding'" class="exercise-coding">
              <div v-if="exercise.requirements" class="coding-requirement">
                <strong>要求：</strong>{{ exercise.requirements }}
              </div>
              <div v-if="exercise.examples && exercise.examples.length > 0" class="coding-examples">
                <strong>示例：</strong>
                <div v-for="(example, exIndex) in exercise.examples" :key="exIndex" class="example">
                  <div><strong>输入：</strong>{{ example.input }}</div>
                  <div><strong>输出：</strong>{{ example.output }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isGenerating" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在生成习题...</p>
    </div>

    <!-- 习题预览模态框 -->
    <div v-if="showPreview" class="modal-overlay" @click="closePreview">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>习题预览</h3>
          <button @click="closePreview" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="previewExerciseData" class="preview-content">
            <div class="preview-header">
              <span class="preview-type">{{ previewExerciseData.type_name }}</span>
              <span class="preview-difficulty" :class="`difficulty-${previewExerciseData.difficulty}`">
                {{ previewExerciseData.difficulty_name }}
              </span>
            </div>
            
            <div class="preview-question">
              <h4>题目</h4>
              <p>{{ previewExerciseData.question }}</p>
            </div>
            
            <!-- 选项 -->
            <div v-if="previewExerciseData.exercise_type === 'multiple_choice' && previewExerciseData.options" class="preview-options">
              <h4>选项</h4>
              <div 
                v-for="(option, index) in previewExerciseData.options" 
                :key="index"
                class="preview-option"
                :class="{ correct: option === previewExerciseData.correct_answer }"
              >
                <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                <span class="option-text">{{ option }}</span>
              </div>
            </div>
            
            <!-- 编程题详情 -->
            <div v-if="previewExerciseData.exercise_type === 'coding'" class="preview-coding">
              <div v-if="previewExerciseData.requirements">
                <h4>要求</h4>
                <p>{{ previewExerciseData.requirements }}</p>
              </div>
              <div v-if="previewExerciseData.input_format">
                <h4>输入格式</h4>
                <p>{{ previewExerciseData.input_format }}</p>
              </div>
              <div v-if="previewExerciseData.output_format">
                <h4>输出格式</h4>
                <p>{{ previewExerciseData.output_format }}</p>
              </div>
              <div v-if="previewExerciseData.examples && previewExerciseData.examples.length > 0">
                <h4>示例</h4>
                <div v-for="(example, index) in previewExerciseData.examples" :key="index" class="preview-example">
                  <div><strong>输入：</strong>{{ example.input }}</div>
                  <div><strong>输出：</strong>{{ example.output }}</div>
                </div>
              </div>
            </div>
            
            <!-- 答案和解析 -->
            <div class="preview-answer">
              <h4>答案</h4>
              <div v-if="previewExerciseData.correct_answer" class="answer-content">
                {{ previewExerciseData.correct_answer }}
              </div>
              <div v-else-if="previewExerciseData.correct_answers" class="answer-content">
                {{ previewExerciseData.correct_answers.join('，') }}
              </div>
            </div>
            
            <div class="preview-explanation">
              <h4>解析</h4>
              <p>{{ previewExerciseData.explanation }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api } from '../api/api.js'

export default {
  name: 'ExerciseGeneratorComponent',
  
  setup() {
    // 状态管理
    const knowledgePoints = ref([])
    const newKnowledgePoint = ref('')
    const exerciseType = ref('multiple_choice')
    const difficulty = ref('medium')
    const count = ref(5)
    const isGenerating = ref(false)
    const generatedExercises = ref([])
    const exerciseTypes = ref({})
    const difficultyLevels = ref({
      easy: '简单',
      medium: '中等',
      hard: '困难'
    })
    const showPreview = ref(false)
    const previewExerciseData = ref(null)

    // 工具函数
    const validateKnowledgePoints = (points) => {
      if (!Array.isArray(points)) {
        return { valid: false, message: '知识点必须是数组' }
      }
      if (points.length === 0) {
        return { valid: false, message: '知识点不能为空' }
      }
      if (points.length > 10) {
        return { valid: false, message: '知识点数量不能超过10个' }
      }
      return { valid: true, message: '知识点验证通过' }
    }

    const formatExercises = (exercises) => {
      return (exercises || []).map(exercise => {
        const formatted = { ...exercise }
        
        // 标准化习题类型
        const typeNames = {
          multiple_choice: '选择题',
          true_false: '判断题',
          fill_blank: '填空题',
          coding: '编程题',
          short_answer: '简答题'
        }
        formatted.type_name = typeNames[formatted.exercise_type] || formatted.exercise_type
        
        // 标准化难度
        const difficultyNames = {
          easy: '简单',
          medium: '中等',
          hard: '困难'
        }
        formatted.difficulty_name = difficultyNames[formatted.difficulty] || formatted.difficulty
        
        // 计算预估完成时间
        const baseTimes = {
          multiple_choice: 1,
          true_false: 0.5,
          fill_blank: 1.5,
          short_answer: 2,
          coding: 5
        }
        const difficultyMultipliers = {
          easy: 0.8,
          medium: 1.0,
          hard: 1.5
        }
        const baseTime = baseTimes[formatted.exercise_type] || 1
        const multiplier = difficultyMultipliers[formatted.difficulty] || 1
        formatted.estimated_time = Math.round(baseTime * multiplier * 10) / 10
        
        // 确保习题有完整的字段
        if (!formatted.question) {
          formatted.question = '请根据知识点回答以下问题'
        }
        if (!formatted.explanation) {
          formatted.explanation = '本题考查相关知识点'
        }
        if (formatted.exercise_type === 'multiple_choice' && !formatted.options) {
          formatted.options = ['选项A', '选项B', '选项C', '选项D']
        }
        if (formatted.exercise_type === 'multiple_choice' && !formatted.correct_answer) {
          formatted.correct_answer = 'A'
        }
        if (formatted.exercise_type === 'true_false' && formatted.correct_answer === undefined) {
          formatted.correct_answer = true
        }
        if (formatted.exercise_type === 'fill_blank' && !formatted.correct_answers) {
          formatted.correct_answers = ['答案']
        }
        if (formatted.exercise_type === 'coding' && !formatted.correct_answer) {
          formatted.correct_answer = 'def solution():\n    # 请在此处编写代码\n    pass'
        }
        if (formatted.exercise_type === 'short_answer' && !formatted.correct_answer) {
          formatted.correct_answer = '正确答案'
        }
        
        return formatted
      })
    }

    const getExampleKnowledgePoints = () => {
      return [
        'Python语法基础',
        '数据结构',
        '算法',
        '面向对象编程',
        '函数式编程'
      ]
    }

    // 方法
    const addKnowledgePoint = () => {
      if (newKnowledgePoint.value.trim() && !knowledgePoints.value.includes(newKnowledgePoint.value.trim())) {
        knowledgePoints.value.push(newKnowledgePoint.value.trim())
        newKnowledgePoint.value = ''
      }
    }

    const removeKnowledgePoint = (index) => {
      knowledgePoints.value.splice(index, 1)
    }

    const loadExample = () => {
      knowledgePoints.value = getExampleKnowledgePoints()
      exerciseType.value = 'multiple_choice'
      difficulty.value = 'medium'
      count.value = 5
    }

    const clearConfig = () => {
      knowledgePoints.value = []
      newKnowledgePoint.value = ''
      exerciseType.value = 'multiple_choice'
      difficulty.value = 'medium'
      count.value = 5
      generatedExercises.value = []
    }

    const generateExercises = async () => {
      // 验证输入
      const validation = validateKnowledgePoints(knowledgePoints.value)
      if (!validation.valid) {
        alert(validation.message)
        return
      }

      isGenerating.value = true
      
      try {
        const result = await api.generateExercises({
          knowledge_points: knowledgePoints.value,
          exercise_type: exerciseType.value,
          difficulty: difficulty.value,
          count: count.value
        })
        
        console.log('API响应:', result)
        
        if (result && result.exercises) {
          generatedExercises.value = formatExercises(result.exercises)
        } else if (result && result.result && result.result.exercises) {
          generatedExercises.value = formatExercises(result.result.exercises)
        } else {
          console.error('API响应格式错误:', result)
          alert('生成习题失败，响应格式错误')
        }
        
      } catch (error) {
        console.error('生成习题失败:', error)
        alert('生成习题失败，请稍后重试')
      } finally {
        isGenerating.value = false
      }
    }

    const previewExercise = (exercise) => {
      previewExerciseData.value = exercise
      showPreview.value = true
    }

    const closePreview = () => {
      showPreview.value = false
      previewExerciseData.value = null
    }

    const exportExercises = () => {
      if (generatedExercises.value.length === 0) {
        alert('没有可导出的习题')
        return
      }

      // 导出为JSON格式
      const exportData = {
        generated_at: new Date().toISOString(),
        exercises: generatedExercises.value,
        metadata: {
          knowledge_points: knowledgePoints.value,
          exercise_type: exerciseType.value,
          difficulty: difficulty.value,
          count: count.value
        }
      }

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `exercises_${Date.now()}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    // 加载习题类型配置
    const loadExerciseTypes = async () => {
      try {
        const typesData = await api.getExerciseTypes()
        if (typesData.exercise_types) {
          exerciseTypes.value = typesData.exercise_types
        }
      } catch (error) {
        console.error('加载习题类型失败:', error)
      }
    }

    // 生命周期
    onMounted(() => {
      loadExerciseTypes()
      loadExample()
    })

    return {
      // 状态
      knowledgePoints,
      newKnowledgePoint,
      exerciseType,
      difficulty,
      count,
      isGenerating,
      generatedExercises,
      exerciseTypes,
      difficultyLevels,
      showPreview,
      previewExerciseData,
      
      // 方法
      addKnowledgePoint,
      removeKnowledgePoint,
      loadExample,
      clearConfig,
      generateExercises,
      previewExercise,
      closePreview,
      exportExercises
    }
  }
}
</script>

<style scoped>
.exercise-generator-component {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.config-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.config-header h3 {
  margin: 0;
  color: #2d3748;
}

.config-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3182ce;
}

.btn-primary:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.config-item {
  margin-bottom: 20px;
}

.config-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #2d3748;
}

.required {
  color: #e53e3e;
}

.knowledge-points-input {
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  padding: 10px;
  background: white;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.tag {
  display: inline-flex;
  align-items: center;
  background: #e2e8f0;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  gap: 5px;
}

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #718096;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-group {
  display: flex;
  gap: 10px;
}

.input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
}

.select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

.number-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.number-input .input {
  width: 80px;
  text-align: center;
}

.result-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e2e8f0;
}

.result-header h3 {
  margin: 0;
  color: #2d3748;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.exercise-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.2s;
}

.exercise-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f7fafc;
}

.exercise-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.exercise-type {
  background: #4299e1;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.exercise-difficulty {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.difficulty-easy {
  background: #38a169;
  color: white;
}

.difficulty-medium {
  background: #ed8936;
  color: white;
}

.difficulty-hard {
  background: #e53e3e;
  color: white;
}

.exercise-time {
  font-size: 12px;
  color: #718096;
}

.exercise-question {
  margin: 10px 0;
  line-height: 1.5;
  color: #2d3748;
}

.exercise-options {
  margin: 10px 0;
}

.option {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #f7fafc;
}

.option-label {
  font-weight: bold;
  min-width: 20px;
}

.exercise-coding {
  margin: 10px 0;
}

.coding-requirement,
.coding-examples {
  margin-bottom: 10px;
  padding: 10px;
  background: #f7fafc;
  border-radius: 4px;
}

.example {
  margin-top: 5px;
  padding: 5px;
  background: white;
  border-radius: 3px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #718096;
}

.modal-body {
  padding: 20px;
}

.preview-content {
  line-height: 1.6;
}

.preview-header {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.preview-type {
  background: #4299e1;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.preview-difficulty {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.preview-question {
  margin-bottom: 20px;
}

.preview-question h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.preview-options {
  margin-bottom: 20px;
}

.preview-options h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.preview-option {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #f7fafc;
}

.preview-option.correct {
  background: #c6f6d5;
  border: 1px solid #68d391;
}

.preview-coding {
  margin-bottom: 20px;
}

.preview-coding h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.preview-example {
  margin-top: 5px;
  padding: 8px;
  background: #f7fafc;
  border-radius: 4px;
}

.preview-answer {
  margin-bottom: 20px;
  padding: 15px;
  background: #ebf8ff;
  border-radius: 4px;
}

.preview-answer h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.answer-content {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
}

.preview-explanation {
  padding: 15px;
  background: #f7fafc;
  border-radius: 4px;
}

.preview-explanation h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .exercise-generator-component {
    padding: 10px;
  }
  
  .config-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .config-actions {
    justify-content: center;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .number-input {
    justify-content: flex-start;
  }
  
  .result-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .result-info {
    justify-content: space-between;
  }
}
</style>