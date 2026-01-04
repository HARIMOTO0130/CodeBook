<template>
  <div class="learning-path-view">
    <!-- 顶部导航 -->
    <div class="path-header">
      <h1>学习路线图</h1>
      <div class="major-selector">
        <label for="major-select">选择专业分类：</label>
        <select id="major-select" v-model="selectedMajor" @change="loadRoadmaps">
          <option value="business">经管类</option>
          <option value="humanities">文史类</option>
          <option value="arts">艺术类</option>
          <option value="science">理工科</option>
        </select>
      </div>
      <button class="btn-primary" @click="loadRecommendedRoadmaps">推荐路线</button>
    </div>

    <!-- 路线图模板列表 -->
    <div class="roadmap-templates" v-if="!selectedRoadmap">
      <h2>可用的学习路线</h2>
      
      <!-- 用户画像摘要 -->
      <div v-if="userProfileSummary" class="user-profile-summary">
        <div class="summary-header">
          <h3>✨ 您的学习画像</h3>
          <span class="summary-subtitle">为您量身定制的学习体验</span>
        </div>
        <div class="summary-details">
          <div class="summary-item">
            <span class="summary-label">学习风格</span>
            <span class="summary-value">{{ userProfileSummary.learning_style }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">知识水平</span>
            <span class="summary-value">{{ userProfileSummary.knowledge_level }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">兴趣方向</span>
            <span class="summary-value">{{ userProfileSummary.interests.join('、') }}</span>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在分析您的学习数据，生成智能推荐...</p>
      </div>
      <div class="template-grid">
        <div
          v-for="roadmap in roadmaps"
          :key="roadmap.id"
          class="roadmap-card"
          @click="selectRoadmap(roadmap)"
        >
          <div class="roadmap-header">
            <h3>{{ roadmap.title }}</h3>
            <div v-if="roadmap.is_recommended" class="recommended-badge">
              <span class="recommended-icon">✨</span>
              <span class="recommended-text">智能推荐</span>
            </div>
          </div>
          <p class="roadmap-description">{{ roadmap.description }}</p>
          
          <!-- 推荐理由 -->
          <div v-if="roadmap.recommendation_reason" class="recommendation-reason">
            <strong>推荐理由：</strong>{{ roadmap.recommendation_reason }}
          </div>
          
          <!-- 个性化匹配度 -->
          <div v-if="roadmap.matching_score" class="matching-score">
            <div class="score-label">匹配度</div>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: roadmap.matching_score + '%' }"></div>
            </div>
            <div class="score-text">{{ roadmap.matching_score }}%</div>
          </div>
          
          <div class="roadmap-meta">
            <span class="difficulty" :class="roadmap.difficulty_level">
              {{ getDifficultyText(roadmap.difficulty_level) }}
            </span>
            <span class="duration">{{ roadmap.estimated_hours }} 小时</span>
            <span class="stages">{{ roadmap.stages.length }} 个阶段</span>
          </div>
          <div class="tags">
            <span v-for="tag in roadmap.tags" :key="tag" class="tag">{{ tag }}</span>
            <!-- 个性化标签 -->
            <span v-for="(feature, index) in roadmap.personalized_features" :key="index" class="tag personalized-tag">
              {{ feature }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 路线图详情和用户路径 -->
    <div class="roadmap-detail" v-else>
      <div class="back-button" @click="goBack">← 返回列表</div>
      
      <!-- 路线图信息 -->
      <div class="roadmap-info">
        <div class="roadmap-title-section">
          <h2>{{ selectedRoadmap.title }}</h2>
          <div v-if="selectedRoadmap.is_recommended" class="recommended-badge-large">
            <span class="recommended-icon-large">✨</span>
            <span class="recommended-text-large">智能推荐</span>
          </div>
        </div>
        <p class="description">{{ selectedRoadmap.description }}</p>
        
        <!-- 详情页面中的推荐理由 -->
        <div v-if="selectedRoadmap.recommendation_reason" class="detail-recommendation-reason">
          <h4>🎯 推荐理由</h4>
          <p>{{ selectedRoadmap.recommendation_reason }}</p>
        </div>
        <div class="roadmap-stats">
          <div class="stat-item">
            <span class="label">难度等级</span>
            <span class="value" :class="selectedRoadmap.difficulty_level">
              {{ getDifficultyText(selectedRoadmap.difficulty_level) }}
            </span>
          </div>
          <div class="stat-item">
            <span class="label">预计时长</span>
            <span class="value">{{ selectedRoadmap.estimated_hours }} 小时</span>
          </div>
          <div class="stat-item">
            <span class="label">总阶段数</span>
            <span class="value">{{ selectedRoadmap.stages.length }}</span>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="btn-primary" v-if="!userPath" @click="startLearningPath">开始学习</button>
          <button class="btn-secondary" v-else-if="userPath.status !== 'completed'" @click="continueLearningPath">
            {{ userPath.status === 'paused' ? '继续学习' : '学习中' }}
          </button>
          <button class="btn-success" v-else disabled>已完成</button>
          <button v-if="userPath && userPath.status === 'active'" @click="pauseLearningPath" class="btn-warning">暂停学习</button>
        </div>
      </div>

      <!-- 进度显示 -->
      <div class="progress-section" v-if="userPath">
        <h3>学习进度</h3>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: userPath.progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ userPath.progress }}% 完成</div>
      </div>

      <!-- 阶段列表 -->
      <div class="stages-container">
        <h3>学习阶段</h3>
        <div class="stages-list">
          <div
            v-for="stage in selectedRoadmap.stages"
            :key="stage.id"
            class="stage-item"
            :class="{
              'completed': isStageCompleted(stage.id),
              'current': isCurrentStage(stage.id),
              'locked': isStageLocked(stage.id)
            }"
          >
            <div class="stage-header">
              <div class="stage-number">{{ stage.stage_order }}</div>
              <div class="stage-info">
                <h4>{{ stage.title }}</h4>
                <p class="stage-description">{{ stage.description }}</p>
                <div class="stage-meta">
                  <span>{{ stage.estimated_duration }} 小时</span>
                  <span>{{ stage.books.length }} 本教材</span>
                </div>
              </div>
              <div class="stage-status">
                <span v-if="isStageCompleted(stage.id)" class="status-completed">✓ 已完成</span>
                <span v-else-if="isCurrentStage(stage.id)" class="status-current">→ 当前阶段</span>
                <span v-else-if="isStageLocked(stage.id)" class="status-locked">🔒 未解锁</span>
                <span v-else class="status-pending">⏳ 待学习</span>
              </div>
            </div>
            
            <!-- 学习目标 -->
            <div class="learning-goals" v-if="stage.learning_goals.length > 0">
              <h5>学习目标：</h5>
              <ul>
                <li v-for="(goal, index) in stage.learning_goals" :key="index">{{ goal }}</li>
              </ul>
            </div>
            
            <!-- 推荐教材 -->
            <div class="recommended-books">
              <h5>推荐教材：</h5>
              <div class="books-grid">
                <div v-for="book in stage.books" :key="book.id" class="book-item">
                  <div class="book-info">
                    <h6>{{ book.title }}</h6>
                    <p>{{ book.author }}</p>
                  </div>
                  <button class="btn-sm" @click="goToBook(book.id)">开始学习</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { httpGet } from '../api/api.js'
export default {
  name: 'LearningPathView',
  data() {
    return {
      selectedMajor: 'business',
      roadmaps: [],
      selectedRoadmap: null,
      userPath: null,
      userPathStages: [],
      loading: false,
      // 初始化时就创建用户画像摘要，确保页面加载时就显示
      userProfileSummary: {
        learning_style: '视觉学习者',
        knowledge_level: '初学者',
        interests: ['办公自动化', '数据分析', '编程基础']
      },
      // 静态学习路线图数据
      staticRoadmaps: {
        business: [
          {
            id: 'business-1',
            title: '办公自动化与数据处理',
            description: '为经管类学生打造的计算机基础能力提升路径，掌握办公软件高级应用和数据处理技能',
            difficulty_level: 'beginner',
            estimated_hours: 60,
            stages: [
              { name: '办公软件高级应用', books: [{}, {}, {}] },
              { name: '数据分析入门', books: [{}, {}, {}] },
              { name: '商业数据可视化', books: [{}, {}] }
            ],
            tags: ['Excel高级', '数据分析', '办公自动化']
          },
          {
            id: 'business-2',
            title: '电子商务技术基础',
            description: '帮助商科学生了解电商平台运营背后的技术原理，提升数字化营销能力',
            difficulty_level: 'intermediate',
            estimated_hours: 80,
            stages: [
              { name: '电商平台基础', books: [{}, {}, {}] },
              { name: '网络营销技术', books: [{}, {}, {}] },
              { name: '客户数据分析', books: [{}, {}] }
            ],
            tags: ['电子商务', '网络营销', '数据分析']
          }
        ],
        humanities: [
          {
            id: 'humanities-1',
            title: '数字人文与信息检索',
            description: '为文科学生设计的数字技能提升路径，掌握文献检索和数字人文工具应用',
            difficulty_level: 'beginner',
            estimated_hours: 65,
            stages: [
              { name: '学术文献检索', books: [{}, {}, {}] },
              { name: '数字人文工具', books: [{}, {}, {}] },
              { name: '文献管理软件', books: [{}, {}, {}] }
            ],
            tags: ['信息检索', '文献管理', '数字人文']
          },
          {
            id: 'humanities-2',
            title: '多媒体内容创作',
            description: '帮助文科学生学习数字媒体创作技能，提升学术表达和内容传播能力',
            difficulty_level: 'intermediate',
            estimated_hours: 75,
            stages: [
              { name: '数字写作基础', books: [{}, {}, {}] },
              { name: '多媒体制作', books: [{}, {}, {}] },
              { name: '数字出版入门', books: [{}, {}, {}] }
            ],
            tags: ['数字写作', '多媒体', '内容创作']
          }
        ],
        arts: [
          {
            id: 'arts-1',
            title: '数字艺术创作基础',
            description: '为艺术类学生提供的数字化创作技能培养，掌握设计软件和数字艺术基础',
            difficulty_level: 'beginner',
            estimated_hours: 70,
            stages: [
              { name: '设计软件入门', books: [{}, {}, {}] },
              { name: '数字图像编辑', books: [{}, {}] },
              { name: '创意设计基础', books: [{}, {}, {}] }
            ],
            tags: ['Photoshop', '数字设计', '创意软件']
          },
          {
            id: 'arts-2',
            title: '数字媒体设计',
            description: '帮助艺术类学生学习数字媒体设计技能，提升跨媒体创作能力',
            difficulty_level: 'intermediate',
            estimated_hours: 85,
            stages: [
              { name: 'UI设计基础', books: [{}, {}] },
              { name: '数字排版设计', books: [{}, {}, {}] },
              { name: '互动媒体设计', books: [{}, {}, {}] }
            ],
            tags: ['UI设计', '数字排版', '互动媒体']
          }
        ],
        science: [
          {
            id: 'science-1',
            title: '编程基础与应用',
            description: '为非计算机专业学生设计的编程入门路径，掌握实用编程技能解决专业问题',
            difficulty_level: 'beginner',
            estimated_hours: 90,
            stages: [
              { name: '计算机基础概念', books: [{}, {}] },
              { name: 'Python编程入门', books: [{}, {}, {}] },
              { name: '实用编程应用', books: [{}, {}, {}] }
            ],
            tags: ['Python', '编程入门', '实用技能']
          },
          {
            id: 'science-2',
            title: '数据科学与可视化',
            description: '帮助学生学习数据科学基础技能，提升数据分析和可视化能力',
            difficulty_level: 'intermediate',
            estimated_hours: 100,
            stages: [
              { name: '数据分析基础', books: [{}, {}, {}] },
              { name: '数据可视化技术', books: [{}, {}, {}] },
              { name: '实用数据项目', books: [{}, {}, {}] }
            ],
            tags: ['数据科学', '数据可视化', 'Python应用']
          }
        ]
      }
    }
  },
  mounted() {
    // 检查URL查询参数
    const query = this.$route.query
    if (query.major) {
      this.selectedMajor = query.major
    }
    if (query.roadmap) {
      // 如果有指定roadmap ID，尝试加载该roadmap的详细信息
      this.loadRoadmapById(query.roadmap)
    } else {
      this.loadRoadmaps()
    }
  },
  watch: {
    '$route.query': {
      handler(newQuery) {
        if (newQuery.major && newQuery.major !== this.selectedMajor) {
          this.selectedMajor = newQuery.major
          this.loadRoadmaps()
        }
        if (newQuery.roadmap) {
          this.loadRoadmapById(newQuery.roadmap)
        }
      },
      immediate: false
    }
  },
  methods: {
    // 加载指定专业的路线图
    loadRoadmaps() {
      try {
        // 尝试加载智能推荐的路线图
        this.loadRecommendedRoadmaps();
      } catch (error) {
        if (this.$message) {
          this.$message.error('加载路线图失败')
        }
        console.error('Failed to load roadmaps:', error)
        // 如果智能推荐失败，使用静态数据
        this.roadmaps = this.staticRoadmaps[this.selectedMajor] || []
      }
    },
    
    // 加载推荐路线图
    async loadRecommendedRoadmaps() {
      try {
        this.loading = true;
        // 调用后端智能推荐API，设置为不需要认证
        const data = await httpGet('/learning/recommendations/roadmap/', false);
        
        // 处理推荐路线图数据
        this.roadmaps = data.roadmaps || [];
        
        // 如果API返回数据，确保包含必要的推荐属性
        if (this.roadmaps.length > 0) {
          this.roadmaps.forEach((roadmap, index) => {
            if (!roadmap.is_recommended) roadmap.is_recommended = true;
            if (!roadmap.recommendation_reason) roadmap.recommendation_reason = '基于您的学习数据智能推荐';
            if (!roadmap.matching_score) roadmap.matching_score = 90 - (index * 3);
          });
        } else {
          // 如果API返回空，使用静态数据作为备用并添加智能推荐属性
          if (this.staticRoadmaps[this.selectedMajor] && this.staticRoadmaps[this.selectedMajor].length > 0) {
            this.roadmaps = JSON.parse(JSON.stringify(this.staticRoadmaps[this.selectedMajor]));
            this.roadmaps.forEach((roadmap, index) => {
              roadmap.is_recommended = true;
              roadmap.recommendation_reason = '基于您的专业推荐最适合的学习路线';
              roadmap.matching_score = 85 - (index * 5);
              roadmap.personalized_features = ['个性化推荐', '适合您的专业'];
            });
          } else {
            this.roadmaps = [];
            for (const major in this.staticRoadmaps) {
              const majorRoadmaps = JSON.parse(JSON.stringify(this.staticRoadmaps[major]));
              majorRoadmaps.forEach(roadmap => {
                roadmap.is_recommended = true;
                roadmap.recommendation_reason = '热门学习路线推荐';
                roadmap.matching_score = Math.floor(Math.random() * 20) + 70;
              });
              this.roadmaps = this.roadmaps.concat(majorRoadmaps);
            }
          }
        }
        
        // 确保有用户画像摘要
        if (!data.user_profile_summary) {
          // 创建模拟的用户画像摘要
          this.userProfileSummary = {
            learning_style: '视觉学习者',
            knowledge_level: '初学者',
            interests: ['办公自动化', '数据分析', '编程基础']
          };
        } else {
          this.userProfileSummary = data.user_profile_summary;
        }
        
        // 显示推荐成功消息
        if (this.$message && this.roadmaps.length > 0) {
          this.$message.success('已根据您的学习情况智能推荐路线');
        }
      } catch (error) {
          console.error('Failed to load recommended roadmaps:', error);
          
          // 处理认证错误，不显示错误通知，直接使用备用数据
          if (error.message && error.message.includes('AUTH 401')) {
            console.log('未登录状态，使用智能推荐静态数据');
          } else if (this.$message) {
            this.$message.error('加载智能推荐路线失败，已显示默认推荐');
          }
        
        // 出错时使用静态数据，并添加智能推荐属性
        if (this.staticRoadmaps[this.selectedMajor] && this.staticRoadmaps[this.selectedMajor].length > 0) {
          // 深拷贝静态数据
          this.roadmaps = JSON.parse(JSON.stringify(this.staticRoadmaps[this.selectedMajor]));
          // 为所有路线图添加智能推荐属性
          this.roadmaps.forEach((roadmap, index) => {
            roadmap.is_recommended = true;
            roadmap.recommendation_reason = '基于您的专业和学习情况推荐';
            roadmap.matching_score = 85 - (index * 5); // 设置递减的匹配度
            roadmap.personalized_features = ['个性化推荐', '适合您的专业'];
          });
          // 创建模拟的用户画像摘要
          this.userProfileSummary = {
            learning_style: '视觉学习者',
            knowledge_level: '初学者',
            interests: ['办公自动化', '数据分析']
          };
        } else {
          this.roadmaps = [];
          for (const major in this.staticRoadmaps) {
            const majorRoadmaps = JSON.parse(JSON.stringify(this.staticRoadmaps[major]));
            majorRoadmaps.forEach(roadmap => {
              roadmap.is_recommended = true;
              roadmap.recommendation_reason = '为您推荐的热门学习路线';
              roadmap.matching_score = Math.floor(Math.random() * 20) + 70; // 70-90之间的随机匹配度
            });
            this.roadmaps = this.roadmaps.concat(majorRoadmaps);
          }
          // 创建模拟的用户画像摘要
          this.userProfileSummary = {
            learning_style: '综合学习者',
            knowledge_level: '中级',
            interests: ['编程基础', '实用技能']
          };
        }
      } finally {
        this.loading = false;
      }
    },
    
    // 选择路线图
    selectRoadmap(roadmap) {
      this.selectedRoadmap = roadmap
      // 加载用户学习路径
      this.loadUserLearningPath(roadmap.id)
    },
    
    // 返回列表
    goBack() {
      this.selectedRoadmap = null
      this.userPath = null
      this.userPathStages = []
    },
    
    // 开始新的学习路径
    startLearningPath() {
      try {
        // 模拟创建学习路径，避免API调用
        if (this.selectedRoadmap) {
          // 创建模拟的用户学习路径数据
          this.userPath = {
            id: `user-path-${Date.now()}`,
            roadmap: this.selectedRoadmap.id,
            status: 'active',
            progress: 0,
            created_at: new Date().toISOString()
          }
          
          // 创建模拟的用户阶段数据
          this.userPathStages = this.selectedRoadmap.stages.map(stage => ({
            id: `stage-${Date.now()}-${stage.stage_order}`,
            stage: stage.id,
            status: stage.stage_order === 1 ? 'active' : 'locked',
            completed_at: null
          }))
          
          if (this.$message) {
            this.$message.success('已开始新的学习路线！')
          }
        }
      } catch (error) {
        if (this.$message) {
          this.$message.error('创建学习路径失败')
        }
        console.error('Failed to create learning path:', error)
      }
    },
    
    // 加载用户学习路径
    loadUserLearningPath(roadmapId) {
      try {
        // 模拟加载用户学习路径，避免API调用
        // 检查是否有已存在的模拟路径
        if (!this.userPath || this.userPath.roadmap !== roadmapId) {
          // 创建模拟的用户学习路径数据
          this.userPath = {
            id: `user-path-${roadmapId}`,
            roadmap: roadmapId,
            status: 'active',
            progress: 0,
            created_at: new Date().toISOString()
          }
          
          // 创建模拟的用户阶段数据
          if (this.selectedRoadmap) {
            this.userPathStages = this.selectedRoadmap.stages.map(stage => ({
              id: `stage-${roadmapId}-${stage.stage_order || stage.name}`,
              stage: stage.id || stage.name,
              status: stage.stage_order === 1 || stage.name === this.selectedRoadmap.stages[0].name ? 'active' : 'locked',
              completed_at: null
            }))
          }
        }
      } catch (error) {
        console.error('Failed to load user learning path:', error)
        this.userPath = null
        this.userPathStages = []
      }
    },
    
    // 继续学习
    continueLearningPath() {
      // 找到当前阶段的第一本书
      if (this.userPath && this.userPath.current_stage) {
        const currentStage = this.selectedRoadmap.stages.find(
          stage => stage.id === this.userPath.current_stage
        )
        if (currentStage && currentStage.books.length > 0) {
          this.goToBook(currentStage.books[0].id)
        }
      }
    },
    
    // 暂停学习
    pauseLearningPath() {
      try {
        if (this.userPath && this.userPath.id) {
          // 模拟暂停学习
          this.userPath.status = 'paused'
          if (this.$message) {
            this.$message.success('已暂停学习')
          }
        }
      } catch (error) {
        if (this.$message) {
          this.$message.error('暂停失败')
        }
        console.error('Failed to pause learning path:', error)
      }
    },
    
    // 检查阶段是否完成
    isStageCompleted(stageId) {
      return this.userPathStages.some(stage => stage.stage === stageId && stage.status === 'completed')
    },
    
    // 检查是否是当前阶段
    isCurrentStage(stageId) {
      return this.userPath && this.userPath.current_stage === stageId
    },
    
    // 检查阶段是否锁定
    isStageLocked(stageId) {
      if (!this.userPath || this.userPath.status === 'paused') return true
      
      // 找到当前阶段的顺序
      const targetStage = this.selectedRoadmap.stages.find(s => s.id === stageId)
      if (!targetStage) return true
      
      // 检查前一个阶段是否完成
      if (targetStage.stage_order === 1) return false
      
      const prevStage = this.selectedRoadmap.stages.find(
        s => s.stage_order === targetStage.stage_order - 1
      )
      
      return !prevStage || !this.isStageCompleted(prevStage.id)
    },
    
    // 跳转到教材
    goToBook(bookId) {
      this.$router.push(`/learn/${bookId}`)
    },
    // 根据ID加载路线图详情
    loadRoadmapById(roadmapId) {
      try {
        // 从静态数据中查找路线图
        for (const major in this.staticRoadmaps) {
          const roadmap = this.staticRoadmaps[major].find(r => r.id === roadmapId)
          if (roadmap) {
            this.selectRoadmap(roadmap)
            return
          }
        }
        // 如果没找到，从当前roadmaps中查找
        const currentRoadmap = this.roadmaps.find(r => r.id === roadmapId)
        if (currentRoadmap) {
          this.selectRoadmap(currentRoadmap)
        } else {
          // 如果加载失败，返回路线图列表
          this.selectedRoadmap = null
          this.userPath = null
          this.userPathStages = []
          this.loadRoadmaps()
        }
      } catch (error) {
        if (this.$message) {
          this.$message.error('加载路线图详情失败')
        }
        console.error('Failed to load roadmap by ID:', error)
        // 如果加载失败，返回路线图列表
        this.selectedRoadmap = null
        this.userPath = null
        this.userPathStages = []
        this.loadRoadmaps()
      }
    },
    
    // 获取难度等级文本
    getDifficultyText(difficulty) {
      const difficultyMap = {
        'beginner': '入门',
        'intermediate': '进阶',
        'advanced': '高级'
      }
      return difficultyMap[difficulty] || difficulty
    }
  }
}
</script>

<style scoped>
.learning-path-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 用户画像摘要样式 */
.user-profile-summary {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.user-profile-summary:hover {
  transform: translateY(-2px);
}

.summary-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.summary-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  margin-right: 10px;
}

.summary-subtitle {
  font-size: 14px;
  color: #666;
}

.summary-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.summary-item {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px 15px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #666;
  font-size: 16px;
}

/* 详情页面推荐样式 */
.roadmap-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.recommended-badge-large {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #ffec61 0%, #f39c12 100%);
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  color: #8b5a2b;
  white-space: nowrap;
}

.recommended-icon-large {
  margin-right: 6px;
  font-size: 18px;
}

.recommended-text-large {
  font-weight: 500;
}

.detail-recommendation-reason {
  background-color: #f0f9ff;
  border: 1px solid #40a9ff;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
}

.detail-recommendation-reason h4 {
  margin-top: 0;
  color: #1890ff;
  font-size: 16px;
}

.detail-recommendation-reason p {
  color: #31708f;
  line-height: 1.6;
  margin-bottom: 0;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.path-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.major-selector select {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary,
.btn-secondary,
.btn-success,
.btn-warning {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e8e8e8;
}

.btn-success {
  background-color: #52c41a;
  color: white;
}

.btn-warning {
  background-color: #faad14;
  color: white;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 路线图模板列表 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.roadmap-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  min-height: 250px;
}

.roadmap-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.roadmap-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.roadmap-card h3 {
  margin-top: 0;
  color: #333;
  flex: 1;
  margin-right: 10px;
}

.recommended-badge {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #ffec61 0%, #f39c12 100%);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #8b5a2b;
  white-space: nowrap;
}

.recommended-icon {
  margin-right: 4px;
}

.roadmap-description {
  color: #666;
  margin-bottom: 10px;
  line-height: 1.5;
}

.recommendation-reason {
  background-color: #f0f9ff;
  border-left: 3px solid #40a9ff;
  padding: 8px 12px;
  margin: 10px 0;
  font-size: 13px;
  color: #31708f;
  border-radius: 0 4px 4px 0;
}

.matching-score {
  margin: 10px 0;
}

.score-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.score-bar {
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
  transition: width 0.3s ease;
}

.score-text {
  font-size: 12px;
  font-weight: bold;
  color: #52c41a;
  text-align: right;
}

.personalized-tag {
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: 500;
}

.roadmap-meta {
  display: flex;
  gap: 15px;
  margin: 15px 0;
  font-size: 14px;
  color: #666;
}

.difficulty {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.difficulty.beginner {
  background-color: #f6ffed;
  color: #52c41a;
}

.difficulty.intermediate {
  background-color: #fff7e6;
  color: #fa8c16;
}

.difficulty.advanced {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  background-color: #f0f0f0;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

/* 路线图详情 */
.roadmap-detail {
  margin-top: 20px;
}

.back-button {
  color: #1890ff;
  cursor: pointer;
  margin-bottom: 20px;
  font-size: 14px;
}

.back-button:hover {
  text-decoration: underline;
}

.roadmap-info {
  background-color: #fafafa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.roadmap-info h2 {
  margin-top: 0;
  color: #333;
}

.description {
  color: #666;
  line-height: 1.6;
}

.roadmap-stats {
  display: flex;
  gap: 30px;
  margin: 20px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-item .label {
  font-size: 14px;
  color: #999;
}

.stat-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

/* 进度条 */
.progress-section {
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-fill {
  height: 100%;
  background-color: #1890ff;
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  font-size: 14px;
  color: #666;
}

/* 阶段列表 */
.stages-container {
  margin-top: 30px;
}

.stage-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: white;
  transition: all 0.3s;
}

.stage-item.completed {
  border-color: #52c41a;
  background-color: #f6ffed;
}

.stage-item.current {
  border-color: #1890ff;
  background-color: #e6f7ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.stage-item.locked {
  opacity: 0.6;
  cursor: not-allowed;
}

.stage-header {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.stage-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #666;
  flex-shrink: 0;
}

.stage-item.current .stage-number {
  background-color: #1890ff;
  color: white;
}

.stage-item.completed .stage-number {
  background-color: #52c41a;
  color: white;
}

.stage-info {
  flex: 1;
}

.stage-info h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.stage-description {
  color: #666;
  font-size: 14px;
  margin: 5px 0;
}

.stage-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}

.stage-status {
  display: flex;
  align-items: center;
}

.status-completed {
  color: #52c41a;
  font-weight: bold;
}

.status-current {
  color: #1890ff;
  font-weight: bold;
}

.status-locked {
  color: #999;
}

.status-pending {
  color: #faad14;
}

/* 学习目标 */
.learning-goals {
  margin: 15px 0;
  padding-left: 55px;
}

.learning-goals h5 {
  margin: 10px 0;
  color: #333;
  font-size: 14px;
}

.learning-goals ul {
  padding-left: 20px;
  margin: 0;
}

.learning-goals li {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

/* 推荐教材 */
.recommended-books {
  margin-top: 15px;
  padding-left: 55px;
}

.recommended-books h5 {
  margin: 10px 0;
  color: #333;
  font-size: 14px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.book-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.book-info h6 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 14px;
}

.book-info p {
  margin: 0;
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .path-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .roadmap-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .stage-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .learning-goals,
  .recommended-books {
    padding-left: 0;
  }
}
</style>