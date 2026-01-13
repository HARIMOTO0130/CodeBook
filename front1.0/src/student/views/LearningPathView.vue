<template>
  <div class="learning-path-view">
    <!-- 顶部导航 -->
    <div class="path-header">
      <div class="header-left">
        <h1>
          <span class="title-icon">🗺️</span>
          <span class="title-text">学习路线图</span>
        </h1>
        <div class="subtitle-actions-container">
          <p class="header-subtitle">基于知识图谱和AI的个性化学习路径推荐</p>
          <div class="header-actions">
            <button class="btn-primary" @click="generateSmartPath" :disabled="generatingSmartPath">
              <span class="btn-icon">✨</span>
              {{ generatingSmartPath ? '生成中...' : '智能推荐' }}
            </button>
            <button class="btn-secondary" @click="showPersonalizedPathDialog = true">
              <span class="btn-icon">🎯</span>
              生成个性建议
            </button>
            <button class="btn-secondary" @click="openPreferenceDialog">
              <span class="btn-icon">⚙️</span>
              学习偏好
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 路线图模板列表 -->
    <div class="roadmap-templates" v-if="!selectedRoadmap">
      <h2>学习画像</h2>
      
      <!-- 用户画像摘要 -->
      <div v-if="userProfileSummary" class="user-profile-summary">
        <div class="summary-header">
          <div class="summary-title-section">
            <h3>✨ 您的学习画像</h3>
            <span class="summary-subtitle">基于AI分析的个性化学习特征</span>
          </div>
          <button class="refresh-profile-btn" @click="loadRecommendedRoadmaps" title="刷新画像">
            🔄
          </button>
        </div>
        <div class="summary-details">
          <div class="summary-item">
            <div class="summary-icon">🎨</div>
            <div class="summary-content">
              <span class="summary-label">学习风格</span>
              <span class="summary-value">{{ userProfileSummary.learning_style }}</span>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-icon">📊</div>
            <div class="summary-content">
              <span class="summary-label">知识水平</span>
              <span class="summary-value">{{ userProfileSummary.knowledge_level }}</span>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-icon">💡</div>
            <div class="summary-content">
              <span class="summary-label">兴趣方向</span>
              <div class="interests-list">
                <span 
                  v-for="(interest, index) in userProfileSummary.interests" 
                  :key="index"
                  class="interest-tag"
                >
                  {{ interest }}
                </span>
              </div>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-icon">🎯</div>
            <div class="summary-content">
              <span class="summary-label">专业组</span>
              <span class="summary-value">{{ userProfileSummary.professional_group }}</span>
            </div>
          </div>
        </div>
        
        <!-- 学习统计数据 -->
        <div class="learning-stats">
          <h4>📈 学习情况</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">学习时长</div>
              <div class="stat-value">{{ userProfileSummary.learning_stats.total_learning_minutes }} 分钟</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">完成练习</div>
              <div class="stat-value">{{ userProfileSummary.learning_stats.completed_practices }}/{{ userProfileSummary.learning_stats.total_practices }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">平均得分</div>
              <div class="stat-value">{{ userProfileSummary.learning_stats.avg_practice_score }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">学习章节</div>
              <div class="stat-value">{{ userProfileSummary.learning_stats.completed_chapters }}/{{ userProfileSummary.learning_stats.total_chapters }}</div>
            </div>
          </div>
        </div>
        
        <!-- 专业组详情 -->
        <div class="professional-group-detail" v-if="userProfileSummary.professional_group_info">
          <h4>🎓 专业组详情</h4>
          <div class="group-details">
            <div class="group-features">
              <h5>核心特征</h5>
              <div class="feature-tags">
                <span 
                  v-for="(feature, index) in userProfileSummary.professional_group_info.features.core_features" 
                  :key="index"
                  class="feature-tag"
                >
                  {{ feature }}
                </span>
              </div>
            </div>
            <div class="group-tools">
              <h5>推荐工具</h5>
              <div class="tool-tags">
                <span 
                  v-for="(tool, index) in userProfileSummary.professional_group_info.features.recommended_tools" 
                  :key="index"
                  class="tool-tag"
                >
                  {{ tool }}
                </span>
              </div>
            </div>
            <div class="group-career">
              <h5>职业方向</h5>
              <div class="career-tags">
                <span 
                  v-for="(career, index) in userProfileSummary.professional_group_info.features.career_paths" 
                  :key="index"
                  class="career-tag"
                >
                  {{ career }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 学习路径组件 -->
      <div class="learning-path-section">
        <h3>🚀 您的学习路径</h3>
        <!-- 智能推荐路径图 -->
        <div v-if="smartPathData && smartPathData.nodes && smartPathData.nodes.length > 0" class="smart-path-container">
          <div class="smart-path-header">
            <h4>智能推荐学习路径</h4>
            <button class="btn-sm btn-refresh" @click="generateSmartPath">重新生成</button>
          </div>
          <div class="smart-path-explanation" v-if="smartPathData.explanation">
            <p>{{ smartPathData.explanation }}</p>
          </div>
          <!-- 路径图可视化 -->
          <div class="smart-path-visualization">
            <svg :width="smartPathWidth" :height="smartPathHeight" class="path-svg">
              <!-- 绘制连接线 -->
              <g class="edges">
                <line
                  v-for="edge in smartPathData.edges"
                  :key="`${edge.source}-${edge.target}`"
                  :x1="getNodePosition(edge.source).x"
                  :y1="getNodePosition(edge.source).y"
                  :x2="getNodePosition(edge.target).x"
                  :y2="getNodePosition(edge.target).y"
                  class="path-edge"
                  :class="`edge-${edge.type}`"
                />
              </g>
              <!-- 绘制节点 -->
              <g class="nodes">
                <g
                  v-for="node in smartPathData.nodes"
                  :key="node.id"
                  :transform="`translate(${node.x}, ${node.y})`"
                  class="path-node"
                  :class="`node-${node.type} node-${node.status}`"
                  @click="selectPathNode(node)"
                >
                  <circle
                    :r="node.importance * 8 + 20"
                    class="node-circle"
                    :class="`difficulty-${Math.floor(node.difficulty)}`"
                  />
                  <text class="node-title" dy="5">{{ node.title }}</text>
                  <text class="node-level" dy="25">L{{ node.level }}</text>
                </g>
              </g>
            </svg>
          </div>
          <!-- 学习建议 -->
          <div v-if="smartPathData.suggestions && smartPathData.suggestions.length > 0" class="smart-path-suggestions">
            <h5>💡 学习建议</h5>
            <ul>
              <li v-for="(suggestion, index) in smartPathData.suggestions" :key="index">{{ suggestion }}</li>
            </ul>
          </div>
        </div>
        <!-- 未生成路径时的提示 -->
        <div v-else class="no-path">
          <p>点击"智能推荐"按钮生成您的个性化学习路径</p>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div class="template-grid">
        <!-- 骨架屏 -->
        <div
          v-if="loading"
          v-for="i in 4"
          :key="`skeleton-${i}`"
          class="roadmap-card"
        >
          <div class="roadmap-card-inner">
            <div class="skeleton skeleton-badge"></div>
            <div class="roadmap-header">
              <div class="skeleton skeleton-title"></div>
            </div>
            <div class="roadmap-image-placeholder">
              <div class="roadmap-image-bg"></div>
            </div>
            <div class="skeleton skeleton-content"></div>
            <div class="skeleton skeleton-content"></div>
            <div class="skeleton skeleton-content"></div>
            <div class="roadmap-meta">
              <div class="skeleton skeleton-tag"></div>
              <div class="skeleton skeleton-tag"></div>
              <div class="skeleton skeleton-tag"></div>
            </div>
            <div class="tags">
              <div class="skeleton skeleton-tag"></div>
              <div class="skeleton skeleton-tag"></div>
            </div>
          </div>
        </div>
        <!-- 实际内容 -->
        <div
          v-else
          v-for="roadmap in roadmaps"
          :key="roadmap.id"
          class="roadmap-card"
          @click="selectRoadmap(roadmap)"
        >
          <div class="roadmap-card-inner">
            <div class="roadmap-header">
              <h3>{{ roadmap.title }}</h3>
              <div v-if="roadmap.is_recommended" class="recommended-badge">
                <span class="recommended-icon">✨</span>
                <span class="recommended-text">智能推荐</span>
              </div>
            </div>
            <div class="roadmap-image-placeholder">
              <div class="roadmap-image-icon">🗺️</div>
              <div class="roadmap-image-bg" :style="{ backgroundColor: getRandomColor(roadmap.id) }"></div>
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
            <!-- 悬停时显示的额外信息 -->
            <div class="roadmap-hover-info">
              <div class="hover-info-item">
                <span class="info-icon">📚</span>
                <span class="info-text">{{ getTotalBooks(roadmap) }} 本教材</span>
              </div>
              <div class="hover-info-item">
                <span class="info-icon">💡</span>
                <span class="info-text">{{ getTotalLearningGoals(roadmap) }} 个学习目标</span>
              </div>
              <button class="hover-view-btn" @click.stop="selectRoadmap(roadmap)">
                查看详情 →
              </button>
            </div>
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
            <div class="learning-goals" v-if="stage.learning_goals && stage.learning_goals.length > 0">
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

    <!-- 个性化路径生成对话框 -->
    <div v-if="showPersonalizedPathDialog" class="dialog-overlay" @click="showPersonalizedPathDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>🎯 生成个性建议</h3>
          <button class="dialog-close" @click="showPersonalizedPathDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>学习目标：</label>
            <input 
              type="text" 
              v-model="personalizedPathGoal" 
              placeholder="例如：掌握Python数据分析"
              class="form-input"
            />
          </div>
          <div class="form-group">
          <label>建议数量：</label>
          <input 
            type="number" 
            v-model.number="personalizedPathMaxNodes" 
            min="5" 
            max="20"
            class="form-input"
          />
        </div>
          <div v-if="generatingPath" class="generating-status">
            <div class="loading-spinner-small"></div>
            <p>正在生成个性建议...</p>
          </div>
          <div v-if="personalizedPathResult" class="personalized-path-result">
            <h4>✨ 为您生成的个性建议：</h4>
            <div class="path-explanation">
              <p>{{ personalizedPathResult.explanation }}</p>
            </div>
            <div class="path-suggestions" v-if="personalizedPathResult.suggestions">
              <h5>💡 学习建议：</h5>
              <ul>
                <li v-for="(suggestion, index) in personalizedPathResult.suggestions" :key="index">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showPersonalizedPathDialog = false">取消</button>
          <button 
            class="btn-primary" 
            @click="generatePersonalizedPath"
            :disabled="!personalizedPathGoal || generatingPath"
          >
            {{ generatingPath ? '生成中...' : '生成建议' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 个性化学习建议面板 -->
    <div class="personalized-suggestions-panel" v-if="selectedRoadmap">
      <div class="suggestions-header">
        <div class="suggestions-title-section">
          <h3>💡 个性化学习建议</h3>
          <p class="suggestions-subtitle">基于您的知识图谱和AI分析生成的针对性建议</p>
        </div>
        <button class="refresh-suggestions-btn" @click="refreshPersonalizedSuggestions" :disabled="generatingSuggestions">
          {{ generatingSuggestions ? '刷新中...' : '🔄 刷新建议' }}
        </button>
      </div>
      <div v-if="generatingSuggestions" class="loading-container-small">
        <div class="loading-spinner-small"></div>
        <p>正在基于您的学习数据生成个性化建议...</p>
      </div>
      <div v-else-if="personalizedSuggestions.length > 0" class="suggestions-container">
        <!-- 学习方法建议 -->
        <div v-if="suggestionCategories.learning_method.length > 0" class="suggestion-category">
          <div class="category-header">
            <span class="category-icon">📚</span>
            <h4>学习方法</h4>
          </div>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestionCategories.learning_method" 
              :key="`method-${index}`" 
              class="suggestion-item"
            >
              <div class="suggestion-icon">💡</div>
              <div class="suggestion-content">{{ suggestion }}</div>
            </div>
          </div>
        </div>
        
        <!-- 时间管理建议 -->
        <div v-if="suggestionCategories.time_management.length > 0" class="suggestion-category">
          <div class="category-header">
            <span class="category-icon">⏰</span>
            <h4>时间管理</h4>
          </div>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestionCategories.time_management" 
              :key="`time-${index}`" 
              class="suggestion-item"
            >
              <div class="suggestion-icon">⏰</div>
              <div class="suggestion-content">{{ suggestion }}</div>
            </div>
          </div>
        </div>
        
        <!-- 资源推荐 -->
        <div v-if="suggestionCategories.resource_recommendation.length > 0" class="suggestion-category">
          <div class="category-header">
            <span class="category-icon">🛠️</span>
            <h4>资源推荐</h4>
          </div>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestionCategories.resource_recommendation" 
              :key="`resource-${index}`" 
              class="suggestion-item"
            >
              <div class="suggestion-icon">🛠️</div>
              <div class="suggestion-content">{{ suggestion }}</div>
            </div>
          </div>
        </div>
        
        <!-- 练习建议 -->
        <div v-if="suggestionCategories.practice_suggestion.length > 0" class="suggestion-category">
          <div class="category-header">
            <span class="category-icon">✏️</span>
            <h4>练习建议</h4>
          </div>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestionCategories.practice_suggestion" 
              :key="`practice-${index}`" 
              class="suggestion-item"
            >
              <div class="suggestion-icon">✏️</div>
              <div class="suggestion-content">{{ suggestion }}</div>
            </div>
          </div>
        </div>
        
        <!-- 激励反馈 -->
        <div v-if="suggestionCategories.motivation.length > 0" class="suggestion-category">
          <div class="category-header">
            <span class="category-icon">🌟</span>
            <h4>激励反馈</h4>
          </div>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestionCategories.motivation" 
              :key="`motivation-${index}`" 
              class="suggestion-item"
            >
              <div class="suggestion-icon">🌟</div>
              <div class="suggestion-content">{{ suggestion }}</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-suggestions">
        <p>暂无个性化学习建议，点击"刷新建议"按钮生成</p>
      </div>
    </div>
    
    <!-- 学习路径可视化图表 -->
    <div class="learning-path-visualization" v-if="selectedRoadmap && selectedRoadmap.stages.length > 0">
      <div class="visualization-header">
        <h3>🗺️ 学习路径可视化</h3>
        <div class="visualization-controls">
          <button class="btn-sm" @click="toggleVisualizationType">
            {{ visualizationType === 'timeline' ? '🔄 切换为关系图' : '🔄 切换为时间线' }}
          </button>
        </div>
      </div>
      <div class="visualization-container">
        <div v-if="visualizationType === 'timeline'" class="timeline-view">
          <div class="timeline-wrapper">
            <div class="timeline">
              <div 
                v-for="(stage, index) in selectedRoadmap.stages" 
                :key="stage.id || index" 
                class="timeline-node"
                :class="{
                  'completed': isStageCompleted(stage.id),
                  'current': isCurrentStage(stage.id),
                  'locked': isStageLocked(stage.id)
                }"
                @click="selectStage(stage)"
              >
                <div class="timeline-node-content">
                  <div class="timeline-node-header">
                    <div class="timeline-node-number">{{ stage.stage_order || index + 1 }}</div>
                    <div class="timeline-node-main">
                      <h4>{{ stage.title || stage.name }}</h4>
                      <p class="timeline-node-description">{{ stage.description || '' }}</p>
                    </div>
                    <div class="timeline-node-status">
                      <span v-if="isStageCompleted(stage.id)" class="status-badge status-completed">
                        <span class="status-icon">✓</span>
                        <span class="status-text">已完成</span>
                      </span>
                      <span v-else-if="isCurrentStage(stage.id)" class="status-badge status-current">
                        <span class="status-icon">→</span>
                        <span class="status-text">进行中</span>
                      </span>
                      <span v-else-if="isStageLocked(stage.id)" class="status-badge status-locked">
                        <span class="status-icon">🔒</span>
                        <span class="status-text">未解锁</span>
                      </span>
                      <span v-else class="status-badge status-pending">
                        <span class="status-icon">⏳</span>
                        <span class="status-text">待学习</span>
                      </span>
                    </div>
                  </div>
                  
                  <div class="timeline-node-details">
                    <div class="timeline-node-meta">
                      <span class="meta-item">
                        <span class="meta-icon">⏱️</span>
                        <span class="meta-text">{{ stage.estimated_duration || 0 }} 小时</span>
                      </span>
                      <span class="meta-item">
                        <span class="meta-icon">📚</span>
                        <span class="meta-text">{{ stage.books ? stage.books.length : 0 }} 本教材</span>
                      </span>
                      <span v-if="stage.learning_goals && stage.learning_goals.length > 0" class="meta-item">
                        <span class="meta-icon">🎯</span>
                        <span class="meta-text">{{ stage.learning_goals.length }} 个目标</span>
                      </span>
                    </div>
                    
                    <!-- 学习目标预览 -->
                    <div v-if="stage.learning_goals && stage.learning_goals.length > 0" class="learning-goals-preview">
                      <div class="goals-label">学习目标：</div>
                      <div class="goals-list">
                        <span 
                          v-for="(goal, goalIndex) in stage.learning_goals.slice(0, 3)" 
                          :key="goalIndex"
                          class="goal-tag"
                        >
                          {{ goal }}
                        </span>
                        <span v-if="stage.learning_goals.length > 3" class="goal-tag more">
                          +{{ stage.learning_goals.length - 3 }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- 操作按钮 -->
                    <div class="timeline-node-actions">
                      <button 
                        v-if="!isStageLocked(stage.id)" 
                        class="action-btn primary"
                        @click.stop="selectStage(stage)"
                      >
                        {{ isCurrentStage(stage.id) ? '继续学习' : '开始学习' }}
                      </button>
                      <button 
                        class="action-btn secondary"
                        @click.stop="showStageDetail(stage)"
                      >
                        查看详情
                      </button>
                    </div>
                  </div>
                </div>
                
                <!-- 连接线 -->
                <div 
                  v-if="index < selectedRoadmap.stages.length - 1" 
                  class="timeline-connector"
                  :class="{
                    'completed': isStageCompleted(stage.id),
                    'current': isCurrentStage(stage.id)
                  }"
                >
                  <div class="connector-line"></div>
                  <div class="connector-arrow">→</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="graph-view">
          <div v-if="knowledgeGraphNodes.length === 0" class="graph-placeholder">
            <div class="graph-icon">📊</div>
            <p>知识图谱关系图可视化</p>
            <p class="graph-hint">点击节点查看详情，拖动节点调整布局</p>
            <button class="btn-sm" @click="loadKnowledgeGraphData" style="margin-top: 16px;">
              加载知识图谱
            </button>
          </div>
          <div v-else class="knowledge-graph-container">
            <div class="graph-controls">
              <button class="btn-sm" @click="toggleGraphLayout">
                {{ graphLayout === 'hierarchical' ? '切换为力导向布局' : '切换为层级布局' }}
              </button>
              <button class="btn-sm" @click="toggleKnowledgeGraphExplanation">
                {{ showKnowledgeGraphExplanation ? '隐藏图谱解释' : '生成图谱解释' }}
              </button>
              <div class="layer-filter">
                <label>显示层级：</label>
                <select v-model="visibleLayers" multiple class="form-select">
                  <option value="concept">概念层</option>
                  <option value="professional">专业融合层</option>
                  <option value="skill">技能层</option>
                  <option value="resource">资源层</option>
                </select>
                <button class="btn-xs" @click="applyLayerFilter">应用筛选</button>
              </div>
            </div>
            
            <!-- 知识图谱统计分析面板 -->
            <div class="knowledge-graph-stats-panel">
              <h3>📊 知识图谱统计分析</h3>
              <div class="stats-container">
                <!-- 总览统计 -->
                <div class="stats-overview">
                  <div class="stat-item">
                    <div class="stat-label">总节点数</div>
                    <div class="stat-value">{{ knowledgeGraphStats.totalNodes }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-label">总关系数</div>
                    <div class="stat-value">{{ knowledgeGraphStats.totalRelations }}</div>
                  </div>
                </div>
                
                <!-- 层级分布 -->
                <div class="stats-section">
                  <h4>层级分布</h4>
                  <div class="distribution-chart">
                    <div 
                      v-for="(count, layer) in knowledgeGraphStats.layerDistribution" 
                      :key="layer"
                      class="distribution-item"
                    >
                      <div class="distribution-label">{{ getLayerLabel(layer) }}</div>
                      <div class="distribution-bar-container">
                        <div 
                          class="distribution-bar" 
                          :style="{ width: `${(count / knowledgeGraphStats.totalNodes) * 100}%` }"
                          :class="`layer-${layer}`"
                        ></div>
                        <div class="distribution-count">{{ count }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 关系类型分布 -->
                <div class="stats-section">
                  <h4>关系类型分布</h4>
                  <div class="distribution-chart">
                    <div 
                      v-for="(count, type) in knowledgeGraphStats.relationTypeDistribution" 
                      :key="type"
                      class="distribution-item"
                    >
                      <div class="distribution-label">{{ getRelationTypeLabel(type) }}</div>
                      <div class="distribution-bar-container">
                        <div 
                          class="distribution-bar" 
                          :style="{ width: `${(count / knowledgeGraphStats.totalRelations) * 100}%` }"
                          :class="`relation-${type}`"
                        ></div>
                        <div class="distribution-count">{{ count }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 掌握度分布 -->
                <div class="stats-section">
                  <h4>掌握度分布</h4>
                  <div class="distribution-chart">
                    <div class="distribution-item">
                      <div class="distribution-label">初级 (0-40%)</div>
                      <div class="distribution-bar-container">
                        <div 
                          class="distribution-bar beginner" 
                          :style="{ width: `${(knowledgeGraphStats.masteryLevelDistribution.beginner / knowledgeGraphStats.totalNodes) * 100}%` }"
                        ></div>
                        <div class="distribution-count">{{ knowledgeGraphStats.masteryLevelDistribution.beginner }}</div>
                      </div>
                    </div>
                    <div class="distribution-item">
                      <div class="distribution-label">中级 (40-80%)</div>
                      <div class="distribution-bar-container">
                        <div 
                          class="distribution-bar intermediate" 
                          :style="{ width: `${(knowledgeGraphStats.masteryLevelDistribution.intermediate / knowledgeGraphStats.totalNodes) * 100}%` }"
                        ></div>
                        <div class="distribution-count">{{ knowledgeGraphStats.masteryLevelDistribution.intermediate }}</div>
                      </div>
                    </div>
                    <div class="distribution-item">
                      <div class="distribution-label">高级 (80-100%)</div>
                      <div class="distribution-bar-container">
                        <div 
                          class="distribution-bar advanced" 
                          :style="{ width: `${(knowledgeGraphStats.masteryLevelDistribution.advanced / knowledgeGraphStats.totalNodes) * 100}%` }"
                        ></div>
                        <div class="distribution-count">{{ knowledgeGraphStats.masteryLevelDistribution.advanced }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 知识图谱解释区域 -->
            <div v-if="showKnowledgeGraphExplanation" class="knowledge-graph-explanation">
              <div class="explanation-header">
                <h4>🧠 知识图谱智能分析</h4>
                <button class="close-btn" @click="showKnowledgeGraphExplanation = false">×</button>
              </div>
              <div class="explanation-content">
                <div v-if="generatingGraphExplanation" class="loading-container-small">
                  <div class="loading-spinner-small"></div>
                  <p>AI正在分析知识图谱...</p>
                </div>
                <div v-else-if="knowledgeGraphExplanation" class="generated-explanation">
                  <p>{{ knowledgeGraphExplanation }}</p>
                </div>
                <div v-else class="no-explanation">
                  <p>点击"生成图谱解释"按钮，AI将为您分析当前知识图谱的结构和学习建议</p>
                </div>
              </div>
            </div>
            
            <!-- 知识图谱编辑控制 -->
            <div class="knowledge-graph-edit-controls">
              <button 
                class="btn-primary" 
                @click="toggleEditMode"
              >
                {{ isEditMode ? '退出编辑模式' : '进入编辑模式' }}
              </button>
              
              <div v-if="isEditMode" class="edit-mode-controls">
                <button class="btn-secondary" @click="showNodeForm = true">
                  添加节点
                </button>
                <button class="btn-secondary" @click="showRelationForm = true">
                  添加关系
                </button>
              </div>
            </div>
            
            <!-- 添加/编辑节点表单 -->
            <div v-if="showNodeForm" class="modal-overlay" @click="showNodeForm = false">
              <div class="modal-content" @click.stop>
                <div class="modal-header">
                  <h4>{{ editingNode ? '编辑节点' : '添加节点' }}</h4>
                  <button class="close-btn" @click="showNodeForm = false">×</button>
                </div>
                <div class="modal-body">
                  <form @submit.prevent="saveNode">
                    <div class="form-group">
                      <label>节点名称：</label>
                      <input 
                        type="text" 
                        v-model="newNode.title" 
                        required
                        class="form-input"
                      >
                    </div>
                    <div class="form-group">
                      <label>节点类型：</label>
                      <select v-model="newNode.type" class="form-select">
                        <option value="concept">概念</option>
                        <option value="skill">技能</option>
                        <option value="professional">专业</option>
                        <option value="resource">资源</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>层级：</label>
                      <select v-model="newNode.layer" class="form-select">
                        <option value="concept">概念层</option>
                        <option value="professional">专业融合层</option>
                        <option value="skill">技能层</option>
                        <option value="resource">资源层</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>难度：</label>
                      <select v-model="newNode.difficulty" class="form-select">
                        <option value="easy">简单</option>
                        <option value="medium">中等</option>
                        <option value="hard">困难</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>掌握度：</label>
                      <input 
                        type="number" 
                        v-model.number="newNode.mastery_level" 
                        min="0" 
                        max="100"
                        class="form-input"
                      >
                    </div>
                    <div class="form-actions">
                      <button type="button" class="btn-secondary" @click="showNodeForm = false">取消</button>
                      <button type="submit" class="btn-primary">{{ editingNode ? '保存' : '添加' }}</button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
            
            <!-- 添加/编辑关系表单 -->
            <div v-if="showRelationForm" class="modal-overlay" @click="showRelationForm = false">
              <div class="modal-content" @click.stop>
                <div class="modal-header">
                  <h4>{{ editingRelation ? '编辑关系' : '添加关系' }}</h4>
                  <button class="close-btn" @click="showRelationForm = false">×</button>
                </div>
                <div class="modal-body">
                  <form @submit.prevent="saveRelation">
                    <div class="form-group">
                      <label>源节点：</label>
                      <select v-model="newRelation.source" required class="form-select">
                        <option value="">请选择源节点</option>
                        <option 
                          v-for="node in knowledgeGraphNodes" 
                          :key="node.id" 
                          :value="node.id"
                        >
                          {{ node.title }}
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>目标节点：</label>
                      <select v-model="newRelation.target" required class="form-select">
                        <option value="">请选择目标节点</option>
                        <option 
                          v-for="node in knowledgeGraphNodes" 
                          :key="node.id" 
                          :value="node.id"
                        >
                          {{ node.title }}
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>关系类型：</label>
                      <select v-model="newRelation.relation_type" class="form-select">
                        <option value="prerequisite">前置知识</option>
                        <option value="related">相关知识</option>
                        <option value="resource">学习资源</option>
                        <option value="recommend">推荐学习</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>关系强度：</label>
                      <input 
                        type="number" 
                        v-model.number="newRelation.strength" 
                        min="0" 
                        max="5" 
                        step="0.1"
                        class="form-input"
                      >
                    </div>
                    <div class="form-actions">
                      <button type="button" class="btn-secondary" @click="showRelationForm = false">取消</button>
                      <button type="submit" class="btn-primary">{{ editingRelation ? '保存' : '添加' }}</button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
            <div class="knowledge-graph-container-wrapper">
              <div class="zoom-controls">
                <button class="btn-sm" @click="zoomIn">+</button>
                <button class="btn-sm" @click="zoomOut">-</button>
                <button class="btn-sm" @click="resetView">重置</button>
              </div>
              <div 
                class="knowledge-graph-svg-container"
                @mousedown="startDrag"
                @mousemove="drag"
                @mouseup="stopDrag"
                @mouseleave="stopDrag"
                @wheel="handleZoom"
              >
                <svg class="knowledge-graph-svg" :viewBox="`0 0 ${graphWidth} ${graphHeight}`">
                  <!-- 缩放和平移变换 -->
                  <g :transform="`translate(${translateX}, ${translateY}) scale(${scale})`">
                    <!-- 绘制关系线 -->
                    <g class="edges">
                      <line
                        v-for="(relation, index) in filteredRelations"
                        :key="`edge-${index}`"
                        :x1="getNodePosition(relation.source).x"
                        :y1="getNodePosition(relation.source).y"
                        :x2="getNodePosition(relation.target).x"
                        :y2="getNodePosition(relation.target).y"
                        :stroke="getRelationColor(relation.relation_type)"
                        :stroke-width="relation.strength || 2"
                        :opacity="0.6"
                        class="graph-edge"
                        :class="{ 'highlighted': isRelationHighlighted(relation) }"
                      />
                    </g>
              <!-- 绘制节点 -->
                    <g class="nodes">
                      <g
                        v-for="(node, index) in filteredNodes"
                        :key="`node-${index}`"
                        :transform="`translate(${getNodePosition(node.id).x}, ${getNodePosition(node.id).y})`"
                        class="graph-node"
                        :class="{ 
                          'selected': selectedNode && selectedNode.id === node.id,
                          'highlighted': isNodeHighlighted(node),
                          'completed': isNodeCompleted(node.id),
                          'current': isCurrentNode(node.id),
                          'locked': isNodeLocked(node.id)
                        }"
                        @click.stop="selectKnowledgeNode(node)"
                        @mouseenter="highlightRelatedNodes(node)"
                        @mouseleave="clearHighlights"
                      >
                        <circle
                          :r="getNodeRadius(node)"
                          :fill="getNodeColor(node)"
                          :stroke="selectedNode && selectedNode.id === node.id ? '#1890ff' : '#fff'"
                          :stroke-width="selectedNode && selectedNode.id === node.id ? 3 : 2"
                          class="node-circle"
                        />
                        <text
                          x="0"
                          y="0"
                          text-anchor="middle"
                          dominant-baseline="middle"
                          :fill="getNodeTextColor(node)"
                          :font-size="getNodeFontSize(node)"
                          class="node-text"
                        >
                          {{ node.title.length > 8 ? node.title.substring(0, 8) + '...' : node.title }}
                        </text>
                        <!-- 节点类型标签 -->
                        <text
                          x="0"
                          :y="getNodeRadius(node) + 16"
                          text-anchor="middle"
                          :font-size="10"
                          fill="#999"
                          class="node-type-label"
                        >
                          {{ getNodeTypeLabel(node.type) }}
                        </text>
                        <!-- 节点状态标记 -->
                        <circle
                          v-if="isCurrentNode(node.id)"
                          :r="getNodeRadius(node) + 6"
                          stroke="#1890ff"
                          stroke-width="2"
                          fill="none"
                          class="current-node-indicator"
                        />
                        <path
                          v-if="isNodeCompleted(node.id)"
                          d="M-8,-4 L-2,2 L8,-8"
                          stroke="#52c41a"
                          stroke-width="2"
                          fill="none"
                          class="completed-node-check"
                          :transform="`translate(${getNodeRadius(node)} - ${getNodeRadius(node)})`"
                        />
                      </g>
                    </g>
                  </g>
                </svg>
              </div>
            </div>
            <!-- 节点详情和LLM建议面板 -->
            <div v-if="selectedNode" class="node-detail-panel">
              <div class="node-detail-header">
                <h4>{{ selectedNode.title }}</h4>
                <button class="close-btn" @click="selectedNode = null">×</button>
              </div>
              <div class="node-detail-content">
                <div class="node-basic-info">
                  <div class="info-row">
                    <span class="info-label">类型：</span>
                    <span class="info-value">{{ getNodeTypeLabel(selectedNode.type) }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">难度：</span>
                    <span class="info-value">{{ getDifficultyLabel(selectedNode.difficulty) }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">层级：</span>
                    <span class="info-value">{{ getLayerLabel(selectedNode.layer) }}</span>
                  </div>
                  <div class="info-row" v-if="selectedNode.description">
                    <span class="info-label">描述：</span>
                    <span class="info-value">{{ selectedNode.description }}</span>
                  </div>
                  <div class="info-row" v-if="selectedNode.mastery_level">
                    <span class="info-label">掌握度：</span>
                    <div class="mastery-bar">
                      <div class="mastery-fill" :style="{ width: selectedNode.mastery_level + '%' }"></div>
                    </div>
                    <span class="mastery-text">{{ selectedNode.mastery_level }}%</span>
                  </div>
                </div>
                
                <!-- 相关节点 -->
                <div class="related-nodes-section">
                  <h5>🔗 相关节点</h5>
                  <div class="related-nodes-list">
                    <div 
                      v-for="relatedNodeId in getRelatedNodes(selectedNode.id)" 
                      :key="relatedNodeId"
                      class="related-node-item"
                      @click="selectKnowledgeNode(getNodeById(relatedNodeId))"
                    >
                      {{ getNodeById(relatedNodeId)?.title }}
                    </div>
                  </div>
                </div>
                
                <!-- LLM生成的学习建议 -->
                <div class="llm-suggestions-section">
                  <div class="suggestions-header">
                    <h5>💡 AI学习建议</h5>
                    <button 
                      class="btn-xs"
                      @click="generateLLMSuggestions(selectedNode)"
                      :disabled="generatingLLMSuggestions"
                    >
                      {{ generatingLLMSuggestions ? '生成中...' : '刷新建议' }}
                    </button>
                  </div>
                  <div class="suggestions-content">
                    <div v-if="generatingLLMSuggestions" class="loading-container-small">
                      <div class="loading-spinner-small"></div>
                      <p>AI正在生成建议...</p>
                    </div>
                    <div v-else-if="nodeLLMSuggestions[selectedNode.id]" class="generated-suggestions">
                      <ul>
                        <li v-for="(suggestion, index) in nodeLLMSuggestions[selectedNode.id]" :key="index">
                          {{ suggestion }}
                        </li>
                      </ul>
                    </div>
                    <div v-else class="no-suggestions">
                      <p>点击"刷新建议"按钮，AI将为您生成个性化学习建议</p>
                    </div>
                  </div>
                </div>
                
                <div class="node-actions">
                  <button class="btn-sm" @click="goToNodeContent(selectedNode)" style="margin-top: 12px;">
                    开始学习
                  </button>
                  <button class="btn-sm" @click="exploreRelatedNodes(selectedNode)" style="margin-top: 12px; margin-left: 8px;">
                    探索关联节点
                  </button>
                  <div v-if="isEditMode" style="margin-top: 12px; display: flex; gap: 8px;">
                    <button class="btn-sm btn-warning" @click="editNode(selectedNode)">
                      编辑节点
                    </button>
                    <button class="btn-sm btn-danger" @click="deleteNode(selectedNode)">
                      删除节点
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 学习偏好设置对话框 -->
    <div v-if="showPreferenceDialog" class="dialog-overlay" @click="showPreferenceDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>⚙️ 学习偏好设置</h3>
          <button class="dialog-close" @click="showPreferenceDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>学习目标：</label>
            <textarea 
              v-model="learningPreferences.learning_goals" 
              placeholder="请输入您的学习目标，用逗号分隔"
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>兴趣领域：</label>
            <textarea 
              v-model="learningPreferences.interest_areas" 
              placeholder="请输入您的兴趣领域，用逗号分隔"
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>每天可用学习时间（分钟）：</label>
            <input 
              type="number" 
              v-model.number="learningPreferences.daily_available_minutes" 
              min="30" 
              max="360"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>难度偏好：</label>
            <select v-model="learningPreferences.difficulty_preference" class="form-input">
              <option value="easy">偏简单</option>
              <option value="medium">适中</option>
              <option value="challenging">偏难</option>
              <option value="mixed">混合</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showPreferenceDialog = false">取消</button>
          <button 
            class="btn-primary" 
            @click="saveLearningPreferences"
          >
            保存偏好
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { httpGet, httpPost } from '../api/api.js'
import { api } from '../api/api.js'
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
      showPersonalizedPathDialog: false,
      personalizedPathGoal: '',
      personalizedPathMaxNodes: 5,
      generatingPath: false,
      personalizedPathResult: null,
      // 个性化学习建议相关
      generatingSuggestions: false,
      personalizedSuggestions: [],
      suggestionCategories: {
        learning_method: [],
        time_management: [],
        resource_recommendation: [],
        practice_suggestion: [],
        motivation: []
      },
      // 学习路径可视化相关
      visualizationType: 'graph',
      knowledgeGraphNodes: [],
      knowledgeGraphRelations: [],
      selectedNode: null,
      graphLayout: 'hierarchical', // hierarchical, force-directed
      graphWidth: 800,
      graphHeight: 600,
      // 知识图谱交互相关
      scale: 1,
      translateX: 0,
      translateY: 0,
      isDragging: false,
      lastMouseX: 0,
      lastMouseY: 0,
      // 知识图谱统计数据
      knowledgeGraphStats: {
        totalNodes: 0,
        totalRelations: 0,
        layerDistribution: {},
        relationTypeDistribution: {},
        masteryLevelDistribution: {
          beginner: 0,
          intermediate: 0,
          advanced: 0
        }
      },
      // 知识图谱编辑相关
      isEditMode: false,
      showNodeForm: false,
      showRelationForm: false,
      editingNode: null,
      editingRelation: null,
      newNode: {
        title: '',
        type: 'concept',
        layer: 'concept',
        difficulty: 'easy',
        mastery_level: 0
      },
      newRelation: {
        source: '',
        target: '',
        relation_type: 'related',
        strength: 1
      },
      // 知识图谱层级筛选
      visibleLayers: ['concept', 'professional', 'skill', 'resource'],
      filteredNodes: [],
      filteredRelations: [],
      // 节点高亮
      highlightedNodes: [],
      highlightedRelations: [],
      // 知识图谱AI分析相关
      showKnowledgeGraphExplanation: false,
      generatingGraphExplanation: false,
      knowledgeGraphExplanation: null,
      // LLM建议相关
      generatingLLMSuggestions: false,
      nodeLLMSuggestions: {}, // 存储每个节点的LLM建议
      // 学习偏好设置相关
      showPreferenceDialog: false,
      learningPreferences: {
        learning_goals: '',
        interest_areas: '',
        daily_available_minutes: 60,
        difficulty_preference: 'medium'
      },
      // 用户画像摘要初始值，避免页面空白
      userProfileSummary: {
        learning_style: '综合型',
        knowledge_level: '中级',
        interests: ['基础学习'],
        professional_group: '未确定',
        learning_stats: {
          total_learning_minutes: 0,
          completed_practices: 0,
          total_practices: 0,
          avg_practice_score: 0,
          completed_chapters: 0,
          total_chapters: 0
        },
        professional_group_info: {
          features: {
            core_features: [],
            recommended_tools: [],
            career_paths: []
          }
        }
      },
      // 智能推荐路径数据
      smartPathData: null,
      smartPathWidth: 1200,
      smartPathHeight: 600,
      generatingSmartPath: false
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
        console.error('Failed to load roadmaps:', error)
      }
    },
    
    // 加载推荐路线图
    async loadRecommendedRoadmaps() {
      try {
        this.loading = true;
        
        // 并行加载路线图和用户画像数据
        const [roadmapData, profileData] = await Promise.all([
          httpGet('/learning/recommendations/roadmap/', true).catch(error => {
            console.error('Failed to load roadmaps, using fallback:', error);
            return { roadmaps: [] };
          }),
          this.loadUserProfile().catch(error => {
            console.error('Failed to load user profile, using fallback:', error);
            return null;
          })
        ]);
        
        // 处理推荐路线图数据
        this.roadmaps = roadmapData.roadmaps || [];
        
        // 如果API返回数据，确保包含必要的推荐属性
        if (this.roadmaps.length > 0) {
          this.roadmaps.forEach((roadmap, index) => {
            if (!roadmap.is_recommended) roadmap.is_recommended = true;
            if (!roadmap.recommendation_reason) roadmap.recommendation_reason = '基于您的学习数据智能推荐';
            if (!roadmap.matching_score) roadmap.matching_score = 90 - (index * 3);
          });
        }
        
        // 显示推荐成功消息
        if (this.$message && this.roadmaps.length > 0) {
          this.$message.success('已根据您的学习情况智能推荐路线');
        }
      } catch (error) {
          console.error('Failed to load recommended roadmaps:', error);
          
          // 处理认证错误，不显示错误通知
          if (error.message && error.message.includes('AUTH 401')) {
            console.log('未登录状态，无法获取智能推荐');
          } else if (this.$message) {
            this.$message.error('加载智能推荐路线失败，请稍后重试');
          }
        
        // 出错时清空数据，确保不显示静态内容
        this.roadmaps = [];
        this.userProfileSummary = {
          learning_style: '综合型',
          knowledge_level: '中级',
          interests: ['基础学习']
        };
      } finally {
        this.loading = false;
      }
    },
    
    // 生成智能推荐学习路径
    async generateSmartPath() {
      try {
        this.generatingSmartPath = true;
        
        // 调用后端智能推荐路径API
        const data = await httpPost('/learning/personalized-path/smart-path/', {
          learning_goal: 'AI学习',
          max_nodes: 10
        }, true);
        
        // 处理返回的路径数据
        if (data && data.nodes && data.nodes.length > 0) {
          this.smartPathData = data;
          
          // 计算SVG画布大小
          if (data.nodes.length > 0) {
            const maxX = Math.max(...data.nodes.map(n => n.x)) + 200;
            const maxY = Math.max(...data.nodes.map(n => n.y)) + 200;
            this.smartPathWidth = Math.max(1200, maxX);
            this.smartPathHeight = Math.max(600, maxY);
          }
          
          if (this.$message) {
            this.$message.success('智能推荐路径生成成功！');
          }
        } else {
          if (this.$message) {
            this.$message.warning('暂时无法生成学习路径，请稍后重试');
          }
        }
      } catch (error) {
        console.error('Failed to generate smart path:', error);
        
        // 处理不同类型的错误
        if (error.message && error.message.includes('AUTH 401')) {
          if (this.$message) {
            this.$message.error('请先登录后再使用智能推荐功能');
          }
        } else if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED'))) {
          // 连接被拒绝，可能是后端服务未启动
          if (this.$message) {
            this.$message.error('无法连接到服务器，请确保后端服务已启动（运行 python manage.py runserver）');
          }
        } else if (error.message && error.message.includes('network')) {
          if (this.$message) {
            this.$message.error('网络请求失败，请检查网络连接或稍后重试');
          }
        } else {
          // 其他错误
          const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '未知错误';
          if (this.$message) {
            this.$message.error(`生成智能推荐路径失败：${errorMsg}`);
          }
        }
      } finally {
        this.generatingSmartPath = false;
      }
    },
    
    // 获取节点位置
    getNodePosition(nodeId) {
      if (!this.smartPathData || !this.smartPathData.nodes) {
        return { x: 0, y: 0 };
      }
      const node = this.smartPathData.nodes.find(n => n.id === nodeId);
      return node ? { x: node.x, y: node.y } : { x: 0, y: 0 };
    },
    
    // 选择路径节点
    selectPathNode(node) {
      // 可以在这里添加节点详情显示逻辑
      console.log('Selected path node:', node);
      if (this.$message) {
        this.$message.info(`已选择节点：${node.title}`);
      }
    },
    
    // 加载用户画像数据
    async loadUserProfile() {
      try {
        // 调用后端API获取用户画像数据
        const response = await httpGet('/users/users/profile/', true);
        const profileData = response;
        
        // 处理用户画像数据，适配前端显示格式
        if (profileData) {
          // 计算主导学习风格
          const dominantStyle = profileData.multi_dim_features.learning_style.dominant_style;
          const styleMap = {
            'visual': '视觉型',
            'auditory': '听觉型',
            'reading': '读写型',
            'kinesthetic': '动手型',
            'balanced': '综合型'
          };
          
          // 计算知识水平
          const masteryLevel = profileData.knowledge_state.overall_mastery;
          let knowledgeLevel;
          if (masteryLevel >= 0.7) {
            knowledgeLevel = '高级';
          } else if (masteryLevel >= 0.4) {
            knowledgeLevel = '中级';
          } else {
            knowledgeLevel = '初级';
          }
          
          // 更新用户画像摘要
          this.userProfileSummary = {
            learning_style: styleMap[dominantStyle] || '综合型',
            knowledge_level: knowledgeLevel,
            interests: profileData.multi_dim_features.interests.length > 0 ? 
                       profileData.multi_dim_features.interests : ['基础学习'],
            // 添加专业组信息
            professional_group: profileData.professional_tendency.dominant_group,
            // 添加学习统计数据
            learning_stats: profileData.learning_stats,
            // 添加学习偏好
            learning_preferences: profileData.learning_preferences,
            // 添加专业组详情
            professional_group_info: profileData.professional_group_info
          };
        }
      } catch (error) {
        console.error('Failed to load user profile:', error);
        // 使用默认值
        this.userProfileSummary = {
          learning_style: '综合型',
          knowledge_level: '中级',
          interests: ['基础学习'],
          professional_group: '未确定',
          learning_stats: {
            total_learning_minutes: 0,
            total_practices: 0,
            completed_practices: 0,
            avg_practice_score: 0,
            total_chapters: 0,
            completed_chapters: 0,
            avg_chapter_progress: 0,
            wrong_questions_count: 0,
            recent_learning_days: 0
          },
          learning_preferences: {
            learning_goals: [],
            major: null,
            interests: [],
            enable_learning_reminders: true,
            reminder_time: '09:00',
            daily_available_minutes: 60,
            difficulty_preference: 'medium'
          },
          professional_group_info: {
            dominant_group: '未确定',
            group_scores: {
              '经管类': 0,
              '文史类': 0,
              '艺术类': 0,
              '理工科': 0
            },
            features: {
              core_features: [],
              recommended_tools: [],
              career_paths: []
            },
            custom_major: null
          }
        };
      }
    },
    
    // 选择路线图
    selectRoadmap(roadmap) {
      this.selectedRoadmap = roadmap
      // 加载用户学习路径
      this.loadUserLearningPath(roadmap.id)
      // 自动加载个性化学习建议
      this.refreshPersonalizedSuggestions()
      // 自动加载知识图谱数据用于可视化
      this.loadKnowledgeGraphData()
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
              id: `stage-${roadmapId}-${stage.stage_order}`,
              stage: stage.id,
              status: stage.stage_order === 1 ? 'active' : 'locked',
              completed_at: null
            }))
          }
        }
      } catch (error) {
        console.error('Failed to load user learning path:', error)
      }
    },
    
    // 获取随机颜色，用于路线图卡片的背景色
    getRandomColor(id) {
      // 使用id生成一个一致的颜色
      const colors = ['#4a90e2', '#50e3c2', '#f5a623', '#d0021b', '#9013fe', '#7ed321', '#bd10e0', '#50e3c2'];
      const index = parseInt(id.replace(/\D/g, '')) % colors.length;
      return colors[index];
    },
    
    // 计算路线图的总教材数量
    getTotalBooks(roadmap) {
      if (!roadmap || !roadmap.stages) return 0;
      return roadmap.stages.reduce((total, stage) => {
        return total + (stage.books ? stage.books.length : 0);
      }, 0);
    },
    
    // 计算路线图的总学习目标数量
    getTotalLearningGoals(roadmap) {
      if (!roadmap || !roadmap.stages) return 0;
      return roadmap.stages.reduce((total, stage) => {
        return total + (stage.learning_goals ? stage.learning_goals.length : 0);
      }, 0);
    },
    
    // 获取难度文本
    getDifficultyText(level) {
      const difficultyMap = {
        easy: '简单',
        medium: '中等',
        hard: '困难',
        expert: '专家级'
      };
      return difficultyMap[level] || '未知';
    },
    
    // 检查阶段是否已完成
    isStageCompleted(stageId) {
      return this.userPathStages.some(stage => stage.stage === stageId && stage.status === 'completed');
    },
    
    // 检查是否为当前阶段
    isCurrentStage(stageId) {
      return this.userPathStages.some(stage => stage.stage === stageId && stage.status === 'active');
    },
    
    // 检查阶段是否锁定
    isStageLocked(stageId) {
      const stageIndex = this.selectedRoadmap?.stages.findIndex(s => s.id === stageId) || 0;
      // 如果是第一个阶段，或者前一个阶段已完成，则不锁定
      if (stageIndex === 0) return false;
      const previousStage = this.selectedRoadmap?.stages[stageIndex - 1];
      return !this.isStageCompleted(previousStage?.id);
    },
    
    // 继续学习路径
    continueLearningPath() {
      if (this.userPath) {
        this.userPath.status = 'active';
        // 模拟API调用更新学习路径状态
        this.$message?.success('已继续学习路径');
      }
    },
    
    // 暂停学习路径
    pauseLearningPath() {
      if (this.userPath) {
        this.userPath.status = 'paused';
        // 模拟API调用更新学习路径状态
        this.$message?.success('已暂停学习路径');
      }
    },
    
    // 刷新个性化学习建议
    async refreshPersonalizedSuggestions() {
      try {
        this.generatingSuggestions = true;
        // 调用实际API获取个性化建议
        const response = await api.generatePersonalizedSuggestions({
          learning_goal: this.learningGoal,
          knowledge_node_ids: this.selectedNodeIds
        });
        
        // 处理API返回的建议
        if (response && response.suggestions && Array.isArray(response.suggestions)) {
          // 简单分类：根据建议内容包含的关键词进行分类
          this.personalizedSuggestions = response.suggestions.map(content => {
            let category = 'general';
            if (content.includes('方法') || content.includes('学习')) {
              category = 'learning_method';
            } else if (content.includes('时间') || content.includes('安排')) {
              category = 'time_management';
            } else if (content.includes('资源') || content.includes('推荐')) {
              category = 'resource_recommendation';
            } else if (content.includes('练习') || content.includes('实践')) {
              category = 'practice_suggestion';
            } else if (content.includes('动力') || content.includes('目标')) {
              category = 'motivation';
            }
            return { category, content };
          });
        } else {
          // API返回格式不符合预期，使用默认建议
          this.personalizedSuggestions = [
            { category: 'general', content: '建议定期复习已学内容，加深理解' },
            { category: 'general', content: '结合实际项目进行练习，巩固所学知识' }
          ];
        }
        
        // 分类建议
        this.suggestionCategories = {
          learning_method: this.personalizedSuggestions.filter(s => s.category === 'learning_method').map(s => s.content),
          time_management: this.personalizedSuggestions.filter(s => s.category === 'time_management').map(s => s.content),
          resource_recommendation: this.personalizedSuggestions.filter(s => s.category === 'resource_recommendation').map(s => s.content),
          practice_suggestion: this.personalizedSuggestions.filter(s => s.category === 'practice_suggestion').map(s => s.content),
          motivation: this.personalizedSuggestions.filter(s => s.category === 'motivation').map(s => s.content)
        };
      } catch (error) {
        console.error('Failed to refresh personalized suggestions:', error);
        this.$message?.error('刷新个性化建议失败');
      } finally {
        this.generatingSuggestions = false;
      }
    },
    
    // 切换可视化类型
    toggleVisualizationType() {
      this.visualizationType = this.visualizationType === 'timeline' ? 'graph' : 'timeline';
    },
    
    // 选择阶段
    selectStage(stage) {
      // 可以在这里实现选择阶段后的逻辑，比如滚动到对应阶段
      console.log('Selected stage:', stage);
    },
    
    // 显示阶段详情
    showStageDetail(stage) {
      console.log('Show stage detail:', stage);
      // 可以在这里实现显示阶段详情的逻辑
    },
    
    // 加载知识图谱数据
    async loadKnowledgeGraphData() {
      try {
        // 尝试使用不同的API调用方式，确保能获取到数据
        let nodes = [];
        let relations = [];
        
        try {
          // 尝试使用httpGet工具函数调用API
          const [nodesData, relationsData] = await Promise.all([
            httpGet('/learning/knowledge-graph/nodes/', true),
            httpGet('/learning/knowledge-graph/relations/', true)
          ]);
          nodes = nodesData.nodes || [];
          relations = relationsData.relations || [];
        } catch (innerError) {
          console.error('API调用失败，尝试使用模拟数据:', innerError);
          // 如果API调用失败，使用模拟数据
          throw new Error('API调用失败');
        }
        
        // 处理返回的数据，适配前端数据结构
        this.knowledgeGraphNodes = nodes.map(node => ({
          id: node.id,
          title: node.title,
          type: node.type,
          layer: node.professional_group || node.type, // 使用专业组或type作为layer
          difficulty: node.difficulty,
          mastery_level: Math.random() * 100 // 随机生成掌握度，用于演示
        }));
        
        this.knowledgeGraphRelations = relations.map(relation => ({
          source: relation.source,
          target: relation.target,
          relation_type: relation.relation_type || 'related',
          strength: relation.strength || 1
        }));
        
        // 初始化筛选后的节点和关系
        this.filteredNodes = [...this.knowledgeGraphNodes];
        this.filteredRelations = [...this.knowledgeGraphRelations];
        
        // 应用力导向布局
        this.applyForceDirectedLayout();
        
        // 更新筛选后的节点位置（确保它们也有x和y属性）
        this.filteredNodes.forEach(node => {
          const position = this.getNodePosition(node.id);
          node.x = position.x;
          node.y = position.y;
        });
        
        // 计算知识图谱统计数据
        this.calculateKnowledgeGraphStats();
      } catch (error) {
        console.error('加载知识图谱数据失败:', error);
        // 加载失败时使用模拟数据
        this.loadMockKnowledgeGraphData();
      }
    },
    
    // 加载模拟知识图谱数据（备用）
    loadMockKnowledgeGraphData() {
      this.knowledgeGraphNodes = [
        { id: 'node-1', title: '基础知识', type: 'concept', layer: 'concept', difficulty: 'easy', mastery_level: 80 },
        { id: 'node-2', title: '专业知识', type: 'concept', layer: 'concept', difficulty: 'medium', mastery_level: 60 },
        { id: 'node-3', title: '实践技能', type: 'skill', layer: 'skill', difficulty: 'medium', mastery_level: 40 },
        { id: 'node-4', title: '高级应用', type: 'skill', layer: 'skill', difficulty: 'hard', mastery_level: 20 },
        { id: 'node-5', title: '研究方法', type: 'professional', layer: 'professional', difficulty: 'hard', mastery_level: 30 },
        { id: 'node-6', title: '学习资源', type: 'resource', layer: 'resource', difficulty: 'easy', mastery_level: 70 }
      ];
      
      this.knowledgeGraphRelations = [
        { source: 'node-1', target: 'node-2', relation_type: 'prerequisite', strength: 2 },
        { source: 'node-2', target: 'node-3', relation_type: 'prerequisite', strength: 2 },
        { source: 'node-3', target: 'node-4', relation_type: 'prerequisite', strength: 1.5 },
        { source: 'node-2', target: 'node-5', relation_type: 'related', strength: 1.5 },
        { source: 'node-3', target: 'node-5', relation_type: 'related', strength: 1 },
        { source: 'node-1', target: 'node-6', relation_type: 'resource', strength: 1 },
        { source: 'node-2', target: 'node-6', relation_type: 'resource', strength: 1 }
      ];
      
      // 初始化筛选后的节点和关系
      this.filteredNodes = [...this.knowledgeGraphNodes];
      this.filteredRelations = [...this.knowledgeGraphRelations];
      
      // 应用力导向布局
      this.applyForceDirectedLayout();
      
      // 更新筛选后的节点位置（确保它们也有x和y属性）
      this.filteredNodes.forEach(node => {
        const position = this.getNodePosition(node.id);
        node.x = position.x;
        node.y = position.y;
      });
      
      // 计算知识图谱统计数据
      this.calculateKnowledgeGraphStats();
    },
    
    // 力导向布局算法
    applyForceDirectedLayout() {
      // 实现简单的力导向布局
      const nodes = this.knowledgeGraphNodes;
      const relations = this.knowledgeGraphRelations;
      
      // 为每个节点初始化位置
      nodes.forEach(node => {
        // 初始位置在中心附近随机分布
        node.x = this.graphWidth / 2 + (Math.random() - 0.5) * 200;
        node.y = this.graphHeight / 2 + (Math.random() - 0.5) * 200;
        // 速度初始化
        node.vx = 0;
        node.vy = 0;
      });
      
      // 力导向参数
      const iterations = 50;
      const forceStrength = 0.05;
      const damping = 0.9;
      const repulsion = 100;
      
      for (let i = 0; i < iterations; i++) {
        // 计算节点间的排斥力
        for (let j = 0; j < nodes.length; j++) {
          for (let k = j + 1; k < nodes.length; k++) {
            const node1 = nodes[j];
            const node2 = nodes[k];
            
            const dx = node2.x - node1.x;
            const dy = node2.y - node1.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0) {
              const force = (repulsion / distance) * forceStrength;
              const fx = (dx / distance) * force;
              const fy = (dy / distance) * force;
              
              node1.vx -= fx;
              node1.vy -= fy;
              node2.vx += fx;
              node2.vy += fy;
            }
          }
        }
        
        // 计算边的吸引力
        relations.forEach(relation => {
          const sourceNode = nodes.find(n => n.id === relation.source);
          const targetNode = nodes.find(n => n.id === relation.target);
          
          if (sourceNode && targetNode) {
            const dx = targetNode.x - sourceNode.x;
            const dy = targetNode.y - sourceNode.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0) {
              const force = (distance - 100) * forceStrength * (relation.strength || 1);
              const fx = (dx / distance) * force;
              const fy = (dy / distance) * force;
              
              sourceNode.vx += fx;
              sourceNode.vy += fy;
              targetNode.vx -= fx;
              targetNode.vy -= fy;
            }
          }
        });
        
        // 更新节点位置
        nodes.forEach(node => {
          node.vx *= damping;
          node.vy *= damping;
          
          node.x += node.vx;
          node.y += node.vy;
          
          // 边界约束
          node.x = Math.max(50, Math.min(this.graphWidth - 50, node.x));
          node.y = Math.max(50, Math.min(this.graphHeight - 50, node.y));
        });
      }
    },
    
    // 切换图谱布局
    toggleGraphLayout() {
      this.graphLayout = this.graphLayout === 'hierarchical' ? 'force-directed' : 'hierarchical';
    },
    
    // 切换知识图谱解释
    toggleKnowledgeGraphExplanation() {
      this.showKnowledgeGraphExplanation = !this.showKnowledgeGraphExplanation;
      if (this.showKnowledgeGraphExplanation && !this.knowledgeGraphExplanation) {
        this.generateKnowledgeGraphExplanation();
      }
    },
    
    // 生成知识图谱解释
    async generateKnowledgeGraphExplanation() {
      try {
        this.generatingGraphExplanation = true;
        // 模拟API调用生成知识图谱解释
        await new Promise(resolve => setTimeout(resolve, 1500));
        this.knowledgeGraphExplanation = '这是一个基于您学习路径生成的知识图谱，展示了不同知识点之间的关联关系。您可以通过点击节点查看详细信息，并获得AI生成的个性化学习建议。建议您按照从基础知识到高级应用的顺序进行学习，同时结合实践技能的培养，以获得最佳的学习效果。';
      } catch (error) {
        console.error('Failed to generate knowledge graph explanation:', error);
        this.$message?.error('生成知识图谱解释失败');
      } finally {
        this.generatingGraphExplanation = false;
      }
    },
    
    // 应用层级筛选
    applyLayerFilter() {
      // 筛选节点和关系
      this.filteredNodes = this.knowledgeGraphNodes.filter(node => 
        this.visibleLayers.includes(node.layer)
      );
      
      this.filteredRelations = this.knowledgeGraphRelations.filter(relation => 
        this.filteredNodes.some(node => node.id === relation.source) &&
        this.filteredNodes.some(node => node.id === relation.target)
      );
    },
    
    // 检查关系是否高亮
    isRelationHighlighted(relation) {
      return this.highlightedRelations.some(r => 
        r.source === relation.source && r.target === relation.target
      );
    },
    
    // 检查节点是否高亮
    isNodeHighlighted(node) {
      return this.highlightedNodes.includes(node.id);
    },
    
    // 检查节点是否已完成
    isNodeCompleted(nodeId) {
      const node = this.knowledgeGraphNodes.find(n => n.id === nodeId);
      return node && node.mastery_level >= 80;
    },
    
    // 检查是否为当前节点
    isCurrentNode(nodeId) {
      const node = this.knowledgeGraphNodes.find(n => n.id === nodeId);
      return node && node.mastery_level >= 40 && node.mastery_level < 80;
    },
    
    // 检查节点是否锁定
    isNodeLocked(nodeId) {
      const node = this.knowledgeGraphNodes.find(n => n.id === nodeId);
      return node && node.mastery_level < 20;
    },
    
    // 选择知识节点
    selectKnowledgeNode(node) {
      this.selectedNode = node;
    },
    
    // 高亮相关节点
    highlightRelatedNodes(node) {
      // 清除之前的高亮
      this.clearHighlights();
      
      // 高亮当前节点
      this.highlightedNodes.push(node.id);
      
      // 高亮相关节点和关系
      const relatedRelations = this.knowledgeGraphRelations.filter(r => 
        r.source === node.id || r.target === node.id
      );
      
      this.highlightedRelations = relatedRelations;
      
      // 添加相关节点到高亮列表
      relatedRelations.forEach(relation => {
        if (relation.source !== node.id) {
          this.highlightedNodes.push(relation.source);
        }
        if (relation.target !== node.id) {
          this.highlightedNodes.push(relation.target);
        }
      });
    },
    
    // 清除高亮
    clearHighlights() {
      this.highlightedNodes = [];
      this.highlightedRelations = [];
    },
    
    // 计算知识图谱统计数据
    calculateKnowledgeGraphStats() {
      const nodes = this.knowledgeGraphNodes;
      const relations = this.knowledgeGraphRelations;
      
      // 计算总节点数和总关系数
      const totalNodes = nodes.length;
      const totalRelations = relations.length;
      
      // 计算层级分布
      const layerDistribution = {};
      nodes.forEach(node => {
        layerDistribution[node.layer] = (layerDistribution[node.layer] || 0) + 1;
      });
      
      // 计算关系类型分布
      const relationTypeDistribution = {};
      relations.forEach(relation => {
        relationTypeDistribution[relation.relation_type] = (relationTypeDistribution[relation.relation_type] || 0) + 1;
      });
      
      // 计算掌握度分布
      const masteryLevelDistribution = {
        beginner: 0,
        intermediate: 0,
        advanced: 0
      };
      nodes.forEach(node => {
        const mastery = node.mastery_level || 0;
        if (mastery < 40) {
          masteryLevelDistribution.beginner++;
        } else if (mastery < 80) {
          masteryLevelDistribution.intermediate++;
        } else {
          masteryLevelDistribution.advanced++;
        }
      });
      
      // 更新统计数据
      this.knowledgeGraphStats = {
        totalNodes,
        totalRelations,
        layerDistribution,
        relationTypeDistribution,
        masteryLevelDistribution
      };
    },
    
    // 获取节点位置（简单的布局算法）
    // 获取节点位置
    getNodePosition(nodeId) {
      // 首先尝试从主节点列表中查找
      let node = this.knowledgeGraphNodes.find(n => n.id === nodeId);
      
      // 如果主列表中没有，尝试从筛选后的节点列表中查找
      if (!node) {
        node = this.filteredNodes.find(n => n.id === nodeId);
      }
      
      if (!node) return { x: 0, y: 0 };
      
      // 如果节点已有计算好的位置（力导向布局），则使用该位置
      if (node.x !== undefined && node.y !== undefined) {
        return {
          x: node.x,
          y: node.y
        };
      }
      
      // 否则使用层级布局
      const layerPositions = {
        business: { x: 100, y: 150 },
        humanities: { x: 300, y: 100 },
        arts: { x: 500, y: 150 },
        science: { x: 300, y: 300 },
        concept: { x: 100, y: 200 },
        skill: { x: 300, y: 300 },
        professional: { x: 500, y: 200 },
        resource: { x: 200, y: 400 }
      };
      
      const basePosition = layerPositions[node.layer] || { x: 400, y: 300 };
      
      // 为同层级的节点添加偏移，确保每个节点有唯一位置
      const allNodes = [...this.knowledgeGraphNodes, ...this.filteredNodes];
      const uniqueNodes = [...new Map(allNodes.map(n => [n.id, n])).values()];
      const sameLayerNodes = uniqueNodes.filter(n => n.layer === node.layer);
      const index = sameLayerNodes.findIndex(n => n.id === nodeId);
      
      // 使用更合理的偏移算法，避免节点重叠
      const offsetX = (index % 5) * 150;
      const offsetY = Math.floor(index / 5) * 100;
      
      return {
        x: basePosition.x + offsetX,
        y: basePosition.y + offsetY
      };
    },
    
    // 获取关系颜色
    getRelationColor(relationType) {
      const colorMap = {
        prerequisite: '#1890ff',
        related: '#52c41a',
        resource: '#faad14',
        recommend: '#722ed1'
      };
      return colorMap[relationType] || '#d9d9d9';
    },
    
    // 缩放相关方法
    zoomIn() {
      this.scale = Math.min(this.scale * 1.2, 3);
    },
    
    zoomOut() {
      this.scale = Math.max(this.scale / 1.2, 0.5);
    },
    
    resetView() {
      this.scale = 1;
      this.translateX = 0;
      this.translateY = 0;
    },
    
    // 平移相关方法
    startDrag(event) {
      // 只有在空白处点击才开始平移
      if (event.target.tagName === 'svg' || event.target.tagName === 'g' || event.target.classList.contains('edges')) {
        this.isDragging = true;
        this.lastMouseX = event.clientX;
        this.lastMouseY = event.clientY;
      }
    },
    
    drag(event) {
      if (this.isDragging) {
        const deltaX = event.clientX - this.lastMouseX;
        const deltaY = event.clientY - this.lastMouseY;
        
        // 应用缩放因子到平移距离
        this.translateX += deltaX;
        this.translateY += deltaY;
        
        this.lastMouseX = event.clientX;
        this.lastMouseY = event.clientY;
      }
    },
    
    stopDrag() {
      this.isDragging = false;
    },
    
    // 滚轮缩放
    handleZoom(event) {
      event.preventDefault();
      
      // 计算缩放因子
      const delta = event.deltaY > 0 ? 0.8 : 1.25;
      const newScale = Math.max(0.5, Math.min(3, this.scale * delta));
      
      // 计算鼠标位置在SVG坐标系中的位置
      const rect = event.target.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      
      // 调整平移，使缩放围绕鼠标位置进行
      const scaleFactor = newScale / this.scale;
      this.translateX = mouseX - (mouseX - this.translateX) * scaleFactor;
      this.translateY = mouseY - (mouseY - this.translateY) * scaleFactor;
      
      this.scale = newScale;
    },
    
    // 获取层级标签
    getLayerLabel(layer) {
      const layerMap = {
        concept: '概念层',
        professional: '专业融合层',
        skill: '技能层',
        resource: '资源层'
      };
      return layerMap[layer] || layer;
    },
    
    // 获取关系类型标签
    getRelationTypeLabel(type) {
      const relationTypeMap = {
        prerequisite: '前置知识',
        related: '相关知识',
        resource: '学习资源',
        recommend: '推荐学习',
        extension: '扩展知识',
        contrast: '对比知识',
        example: '示例知识'
      };
      return relationTypeMap[type] || type;
    },
    
    // 获取节点半径
    getNodeRadius(node) {
      return 30;
    },
    
    // 获取节点颜色
    getNodeColor(node) {
      const colorMap = {
        concept: '#1890ff',
        skill: '#52c41a',
        professional: '#faad14',
        resource: '#722ed1'
      };
      return colorMap[node.type] || '#d9d9d9';
    },
    
    // 获取节点文本颜色
    getNodeTextColor(node) {
      return '#ffffff';
    },
    
    // 获取节点类型标签
    getNodeTypeLabel(type) {
      const labelMap = {
        concept: '概念',
        skill: '技能',
        professional: '专业',
        resource: '资源'
      };
      return labelMap[type] || '未知';
    },
    
    // 获取难度标签
    getDifficultyLabel(difficulty) {
      const labelMap = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      };
      return labelMap[difficulty] || '未知';
    },
    
    // 获取层级标签
    getLayerLabel(layer) {
      const labelMap = {
        concept: '概念层',
        professional: '专业融合层',
        skill: '技能层',
        resource: '资源层'
      };
      return labelMap[layer] || '未知';
    },
    
    // 获取相关节点
    getRelatedNodes(nodeId) {
      const relatedNodes = new Set();
      this.knowledgeGraphRelations.forEach(relation => {
        if (relation.source === nodeId) {
          relatedNodes.add(relation.target);
        }
        if (relation.target === nodeId) {
          relatedNodes.add(relation.source);
        }
      });
      return Array.from(relatedNodes);
    },
    
    // 通过ID获取节点
    getNodeById(nodeId) {
      return this.knowledgeGraphNodes.find(n => n.id === nodeId);
    },
    
    // 生成LLM建议
    async generateLLMSuggestions(node) {
      try {
        this.generatingLLMSuggestions = true;
        // 模拟API调用生成LLM建议
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 模拟生成LLM建议
        this.nodeLLMSuggestions[node.id] = [
          `建议先掌握${node.title}的基础知识，再深入学习相关内容`,
          `可以通过实践项目来巩固${node.title}的学习`,
          `推荐阅读相关书籍和论文，扩展${node.title}的知识面`,
          `定期复习${node.title}的关键概念，加深记忆`
        ];
      } catch (error) {
        console.error('Failed to generate LLM suggestions:', error);
        this.$message?.error('生成学习建议失败');
      } finally {
        this.generatingLLMSuggestions = false;
      }
    },
    
    // 跳转到节点内容
    goToNodeContent(node) {
      console.log('Go to node content:', node);
      // 可以在这里实现跳转到节点内容的逻辑
    },
    
    // 探索关联节点
    exploreRelatedNodes(node) {
      console.log('Explore related nodes:', node);
      // 可以在这里实现探索关联节点的逻辑
    },
    
    // 打开学习偏好对话框
    openPreferenceDialog() {
      this.showPreferenceDialog = true;
    },
    
    // 保存学习偏好
    saveLearningPreferences() {
      // 模拟保存学习偏好
      this.$message?.success('学习偏好已保存');
      this.showPreferenceDialog = false;
    },
    
    // 生成个性建议
    async generatePersonalizedPath() {
      try {
        this.generatingPath = true;
        
        // 调用实际API生成个性建议
        const response = await api.generatePersonalizedPath(this.personalizedPathGoal, this.personalizedPathMaxNodes);
        
        // 处理API返回的结果
        let generatedSuggestions = [];
        let explanation = `基于您的学习目标"${this.personalizedPathGoal}"和知识图谱分析，我们为您生成了个性化学习建议。这些建议结合了您的知识水平、学习目标和知识图谱关系，帮助您高效地达成学习目标。`;
        
        // 检查API返回结果
        if (response) {
          // 如果返回了suggestions，直接使用
          if (response.suggestions && Array.isArray(response.suggestions)) {
            generatedSuggestions = response.suggestions;
          }
          // 如果返回了explanation，使用它
          if (response.explanation) {
            explanation = response.explanation;
          }
          // 如果没有返回suggestions但返回了path，基于path生成建议
          if (response.path && Array.isArray(response.path) && generatedSuggestions.length === 0) {
            generatedSuggestions = response.path.map((node, index) => {
              return `建议学习${node.title}（${node.type}，难度：${node.difficulty}），${node.description}`;
            });
          }
        }
        
        // 如果API没有返回有效的建议，使用默认建议
        if (generatedSuggestions.length === 0) {
          generatedSuggestions = [
            `建议先了解${this.personalizedPathGoal}的基本概念和核心知识点`,
            `建议寻找${this.personalizedPathGoal}相关的优质学习资源`,
            `建议制定${this.personalizedPathGoal}的学习计划，分阶段推进`,
            `建议加入${this.personalizedPathGoal}相关的学习社区，与他人交流`,
            `建议定期总结${this.personalizedPathGoal}的学习成果，巩固记忆`
          ];
        }
        
        // 直接使用API返回的建议，跳过本地知识图谱检查
        if (false) {
          // 根据学习目标过滤相关节点
          const relevantNodes = this.knowledgeGraphNodes.filter(node => 
            node.title.toLowerCase().includes(this.personalizedPathGoal.toLowerCase()) ||
            this.personalizedPathGoal.toLowerCase().includes(node.title.toLowerCase())
          );
          
          // 如果找到相关节点，基于知识图谱生成建议
          if (relevantNodes.length > 0) {
            // 生成基于知识图谱的建议
            relevantNodes.forEach((node, index) => {
              const masteryLevel = node.mastery_level || 0;
              const difficulty = node.difficulty || 'medium';
              
              // 根据节点属性生成个性化建议
              if (masteryLevel < 30) {
                generatedSuggestions.push(`建议从${node.title}的基础知识开始学习，这是您当前掌握度较低的领域`);
              } else if (masteryLevel < 60) {
                generatedSuggestions.push(`建议深入学习${node.title}，您已经掌握了基础，可以进一步提升`);
              } else {
                generatedSuggestions.push(`建议将${node.title}应用到实践项目中，您已经有较好的掌握度`);
              }
              
              // 根据难度生成建议
              if (difficulty === 'easy') {
                generatedSuggestions.push(`建议加快${node.title}的学习进度，这是一个相对简单的主题`);
              } else if (difficulty === 'hard') {
                generatedSuggestions.push(`建议放慢${node.title}的学习节奏，多做练习巩固`);
              }
            });
            
            // 添加一些通用建议
            generatedSuggestions.push('建议结合知识图谱中的关联节点学习，形成完整的知识体系');
            generatedSuggestions.push('定期检查知识图谱，更新您的学习进度和掌握度');
            generatedSuggestions.push('根据知识图谱的层级关系，有序推进学习计划');
          } else {
            // 如果没有找到相关节点，生成基于学习目标的通用建议
            generatedSuggestions = [
              `建议先了解${this.personalizedPathGoal}的基本概念和核心知识点`,
              `建议寻找${this.personalizedPathGoal}相关的优质学习资源`,
              `建议制定${this.personalizedPathGoal}的学习计划，分阶段推进`,
              `建议加入${this.personalizedPathGoal}相关的学习社区，与他人交流`,
              `建议定期总结${this.personalizedPathGoal}的学习成果，巩固记忆`,
              `建议将${this.personalizedPathGoal}应用到实际项目中，提升实践能力`,
              `建议关注${this.personalizedPathGoal}的最新发展动态和趋势`,
              `建议寻找${this.personalizedPathGoal}领域的专家资源，学习他们的经验`,
              `建议通过练习和测试检验${this.personalizedPathGoal}的学习效果`,
              `建议将${this.personalizedPathGoal}与其他相关领域结合学习，拓宽知识面`
            ];
          }
        } else {
          // 如果没有知识图谱数据，生成基于学习目标的通用建议
          generatedSuggestions = [
            `建议先了解${this.personalizedPathGoal}的基本概念和核心知识点`,
            `建议寻找${this.personalizedPathGoal}相关的优质学习资源`,
            `建议制定${this.personalizedPathGoal}的学习计划，分阶段推进`,
            `建议加入${this.personalizedPathGoal}相关的学习社区，与他人交流`,
            `建议定期总结${this.personalizedPathGoal}的学习成果，巩固记忆`,
            `建议将${this.personalizedPathGoal}应用到实际项目中，提升实践能力`,
            `建议关注${this.personalizedPathGoal}的最新发展动态和趋势`,
            `建议寻找${this.personalizedPathGoal}领域的专家资源，学习他们的经验`,
            `建议通过练习和测试检验${this.personalizedPathGoal}的学习效果`,
            `建议将${this.personalizedPathGoal}与其他相关领域结合学习，拓宽知识面`
          ];
        }
        
        // 确保建议数量不超过用户指定的数量
        generatedSuggestions = generatedSuggestions.slice(0, this.personalizedPathMaxNodes);
        
        // 生成最终结果
        this.personalizedPathResult = {
          id: `personalized-path-${Date.now()}`,
          goal: this.personalizedPathGoal,
          explanation: `基于您的学习目标"${this.personalizedPathGoal}"和知识图谱分析，我们为您生成了${generatedSuggestions.length}条个性化学习建议。这些建议结合了您的知识水平、学习目标和知识图谱关系，帮助您高效地达成学习目标。`,
          suggestions: generatedSuggestions
        };
      } catch (error) {
        console.error('Failed to generate personalized suggestions:', error);
        this.$message?.error('生成个性建议失败');
      } finally {
        this.generatingPath = false;
      }
    },
    
    // 知识图谱编辑相关方法
    // 切换编辑模式
    toggleEditMode() {
      this.isEditMode = !this.isEditMode;
    },
    
    // 编辑节点
    editNode(node) {
      this.editingNode = node;
      this.newNode = { ...node };
      this.showNodeForm = true;
    },
    
    // 删除节点
    deleteNode(node) {
      if (confirm(`确定要删除节点 "${node.title}" 吗？`)) {
        // 删除节点
        const index = this.knowledgeGraphNodes.findIndex(n => n.id === node.id);
        if (index !== -1) {
          this.knowledgeGraphNodes.splice(index, 1);
        }
        
        // 删除与该节点相关的所有关系
        this.knowledgeGraphRelations = this.knowledgeGraphRelations.filter(relation => 
          relation.source !== node.id && relation.target !== node.id
        );
        
        // 更新筛选后的节点和关系
        this.applyLayerFilter();
        
        // 重新计算统计数据
        this.calculateKnowledgeGraphStats();
        
        // 清除选中状态
        if (this.selectedNode && this.selectedNode.id === node.id) {
          this.selectedNode = null;
        }
      }
    },
    
    // 保存节点
    saveNode() {
      if (this.editingNode) {
        // 更新现有节点
        const index = this.knowledgeGraphNodes.findIndex(n => n.id === this.editingNode.id);
        if (index !== -1) {
          this.knowledgeGraphNodes[index] = { ...this.newNode };
        }
      } else {
        // 添加新节点
        const newNodeId = `node-${Date.now()}`;
        this.knowledgeGraphNodes.push({
          ...this.newNode,
          id: newNodeId
        });
      }
      
      // 更新筛选后的节点和关系
      this.applyLayerFilter();
      
      // 重新计算统计数据
      this.calculateKnowledgeGraphStats();
      
      // 重置表单
      this.resetNodeForm();
    },
    
    // 重置节点表单
    resetNodeForm() {
      this.editingNode = null;
      this.newNode = {
        title: '',
        type: 'concept',
        layer: 'concept',
        difficulty: 'easy',
        mastery_level: 0
      };
      this.showNodeForm = false;
    },
    
    // 保存关系
    saveRelation() {
      if (this.editingRelation) {
        // 更新现有关系
        const index = this.knowledgeGraphRelations.findIndex(r => 
          r.source === this.editingRelation.source && r.target === this.editingRelation.target
        );
        if (index !== -1) {
          this.knowledgeGraphRelations[index] = { ...this.newRelation };
        }
      } else {
        // 添加新关系
        this.knowledgeGraphRelations.push({ ...this.newRelation });
      }
      
      // 更新筛选后的节点和关系
      this.applyLayerFilter();
      
      // 重新计算统计数据
      this.calculateKnowledgeGraphStats();
      
      // 重置表单
      this.resetRelationForm();
    },
    
    // 重置关系表单
    resetRelationForm() {
      this.editingRelation = null;
      this.newRelation = {
        source: '',
        target: '',
        relation_type: 'related',
        strength: 1
      };
      this.showRelationForm = false;
    }
  }
}
</script>

<style scoped>
/* 学习路线图卡片增强样式 */
.roadmap-card {
  perspective: 1000px;
  transform-style: preserve-3d;
}

.roadmap-card-inner {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  cursor: pointer;
}

.roadmap-card:hover .roadmap-card-inner {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  border-color: #1890ff;
}

/* 路线图图片占位符 */
.roadmap-image-placeholder {
  position: relative;
  width: 100%;
  height: 120px;
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.roadmap-image-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.1;
  transition: opacity 0.3s ease;
}

.roadmap-card:hover .roadmap-image-bg {
  opacity: 0.15;
}

.roadmap-image-icon {
  position: relative;
  font-size: 48px;
  z-index: 1;
  transition: transform 0.3s ease;
}

.roadmap-card:hover .roadmap-image-icon {
  transform: scale(1.1) rotate(5deg);
}

/* 悬停信息 */
.roadmap-hover-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(255, 255, 255, 0.95), transparent);
  padding: 20px;
  transform: translateY(100%);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.roadmap-card:hover .roadmap-hover-info {
  transform: translateY(0);
}

.hover-info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.info-icon {
  font-size: 16px;
}

.hover-view-btn {
  align-self: flex-end;
  background: #1890ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.hover-view-btn:hover {
  background: #40a9ff;
}

/* 路线图卡片网格布局增强 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .roadmap-card-inner {
    padding: 16px;
  }
  
  .roadmap-image-placeholder {
    height: 100px;
  }
  
  .roadmap-image-icon {
    font-size: 36px;
  }
}

/* 匹配度进度条增强 */
.matching-score {
  margin: 12px 0;
}

.score-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 6px 0;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a, #1890ff);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 标签样式增强 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag {
  background: #f5f5f5;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.tag:hover {
  background: #e6f7ff;
  color: #1890ff;
  border-color: #91d5ff;
}

.personalized-tag {
  background: #fff7e6;
  color: #fa8c16;
}

.personalized-tag:hover {
  background: #fff1d6;
  color: #fa8c16;
  border-color: #ffd591;
}

/* 推荐理由样式增强 */
.recommendation-reason {
  margin: 12px 0;
  padding: 12px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  font-size: 14px;
}

/* 加载状态增强 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #666;
  font-size: 16px;
  line-height: 1.5;
}

/* 骨架屏样式 */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-card {
  padding: 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.skeleton-title {
  width: 70%;
  height: 24px;
  margin-bottom: 12px;
}

.skeleton-subtitle {
  width: 50%;
  height: 16px;
  margin-bottom: 16px;
}

.skeleton-content {
  width: 100%;
  height: 12px;
  margin-bottom: 8px;
}

.skeleton-content:last-child {
  width: 80%;
  margin-bottom: 0;
}

.skeleton-badge {
  width: 60px;
  height: 20px;
  display: inline-block;
  margin-bottom: 12px;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.skeleton-tag {
  width: 40px;
  height: 20px;
}

/* 页面容器样式 */
.learning-path-view {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 顶部导航样式增强 */
.path-header {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  background: white;
  padding: 24px 32px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

@media (max-width: 768px) {
  .path-header {
    padding: 16px 20px;
    margin-bottom: 16px;
  }
}

.path-header:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #e6f7ff;
  transform: translateY(-2px);
}

.header-left {
  flex: 1;
  margin-right: 32px;
}

/* h1 样式优化 */
h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  animation: fadeInDown 0.6s ease-out;
}

/* 标题图标样式 */
.title-icon {
  font-size: 36px;
  color: #667eea;
  display: inline-block;
  animation: rotate 3s linear infinite;
}

/* 标题文本样式 */
.title-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline-block;
}

h1::before {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  animation: expandFromCenter 0.8s ease-out 0.2s both;
}

/* p 副标题样式优化 */
.header-subtitle {
  margin: 12px 0 0 0;
  font-size: 16px;
  color: #666;
  line-height: 1.5;
  animation: fadeInUp 0.6s ease-out 0.4s both;
  position: relative;
  padding-left: 24px;
}

.header-subtitle::before {
  content: '💡';
  position: absolute;
  left: 0;
  top: 0;
  font-size: 18px;
  animation: pulse 2s infinite;
}

/* 标题区域动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes expandFromCenter {
  from {
    width: 0;
    left: 50%;
  }
  to {
    width: 60px;
    left: 0;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* 副标题和操作按钮容器 */
.subtitle-actions-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  margin-top: 12px;
}

/* 头部操作区域样式优化 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  animation: fadeInRight 0.6s ease-out 0.6s both;
}

@media (max-width: 768px) {
  .subtitle-actions-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-top: 8px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
    gap: 8px;
    margin-top: 8px;
  }
  
  .header-actions button {
    flex: 1;
    min-width: 90px;
    padding: 8px 10px;
    font-size: 12px;
  }
  
  .btn-icon {
    font-size: 12px;
    margin-right: 4px;
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 专业选择器样式优化 */
.major-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.major-selector:hover {
  background: #e6f7ff;
  border-color: #91d5ff;
  transform: translateY(-1px);
}

.major-selector label {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

select {
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

select:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 按钮样式优化 */
button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

button:hover::before {
  width: 300px;
  height: 300px;
}

button span {
  position: relative;
  z-index: 1;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #333;
  border: 1px solid #d9d9d9;
}

.btn-secondary:hover {
  background: #f5f7fa;
  border-color: #1890ff;
  color: #1890ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}

.btn-icon {
  font-size: 18px;
  animation: rotate 2s infinite linear;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 用户画像摘要样式增强 */
.user-profile-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease-out 0.8s both;
}

.user-profile-summary:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-title-section h3 {
  margin: 0;
  font-size: 20px;
}

.summary-subtitle {
  font-size: 14px;
  opacity: 0.9;
  display: block;
  margin-top: 4px;
}

.refresh-profile-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-profile-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(180deg) scale(1.1);
}

.summary-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  animation: fadeInUp 0.6s ease-out;
}

.summary-icon {
  font-size: 24px;
  margin-top: 2px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.summary-content {
  flex: 1;
}

.summary-label {
  display: block;
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  font-size: 16px;
  font-weight: 500;
}

.interests-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.interest-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.interest-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* 学习统计数据样式 */
.learning-stats {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  backdrop-filter: blur(10px);
}

.learning-stats h4 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
}

/* 专业组详情样式 */
.professional-group-detail {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  backdrop-filter: blur(10px);
}

.professional-group-detail h4 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.group-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.group-features, .group-tools, .group-career {
  margin-bottom: 16px;
}

.group-features h5, .group-tools h5, .group-career h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
}

.feature-tags, .tool-tags, .career-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag, .tool-tag, .career-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.feature-tag:hover, .tool-tag:hover, .career-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
  backdrop-filter: blur(4px);
}

.dialog-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideInUp 0.3s ease-out;
  border: 1px solid transparent;
  position: relative;
  background: linear-gradient(135deg, white 0%, #f5f7fa 100%);
}

.dialog-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px 16px 0 0;
}

/* 对话框头部样式 */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
  margin-bottom: 20px;
}

.dialog-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: none;
}

.dialog-close:hover {
  background: #f5f5f5;
  color: #666;
  transform: rotate(90deg);
}

/* 对话框主体样式 */
.dialog-body {
  padding: 0 24px 24px;
}

/* 表单组样式 */
.form-group {
  margin-bottom: 24px;
  transition: all 0.3s ease;
  position: relative;
}

.form-group:hover {
  transform: translateX(4px);
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-group:hover label {
  color: #667eea;
}

/* 表单输入框样式 */
.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
  outline: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

/* 知识图谱相关样式 */
.graph-view {
  width: 100%;
  height: 600px;
  display: flex;
  flex-direction: column;
  background-color: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.graph-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #fafafa;
  border: 2px dashed #ddd;
  border-radius: 8px;
  color: #666;
}

.graph-placeholder .graph-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.knowledge-graph-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.knowledge-graph-stats-panel {
  padding: 16px;
  background-color: white;
  border-bottom: 1px solid #eee;
}

.knowledge-graph-explanation {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
}

.knowledge-graph-edit-controls {
  padding: 16px;
  background-color: white;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 8px;
}

.knowledge-graph-container-wrapper {
  flex: 1;
  position: relative;
  overflow: auto;
  background-color: white;
}

.knowledge-graph-svg-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  cursor: grab;
  position: relative;
}

.knowledge-graph-svg-container:active {
  cursor: grabbing;
}

.knowledge-graph-svg {
  width: 100%;
  height: 100%;
}

/* 知识图谱节点和边的样式 */
.nodes {
  cursor: pointer;
}

.nodes circle {
  stroke: white;
  stroke-width: 2px;
  transition: all 0.3s ease;
}

.nodes circle:hover {
  filter: brightness(1.2);
  stroke-width: 3px;
}

.edges line {
  stroke: #999;
  stroke-opacity: 0.6;
  transition: all 0.3s ease;
}

.edges line:hover {
  stroke-opacity: 1;
  stroke-width: 3px;
}

/* 缩放控制按钮 */
.zoom-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  gap: 8px;
  z-index: 10;
}

.zoom-controls button {
  width: 32px;
  height: 32px;
  border: none;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  font-size: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
}

.zoom-controls button:hover {
  background-color: #f0f0f0;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* 节点详情面板 */
.node-detail-panel {
  position: absolute;
  right: 10px;
  top: 10px;
  width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 100;
  max-height: calc(100% - 20px);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .knowledge-graph-stats-panel {
    padding: 12px;
  }
  
  .knowledge-graph-explanation {
    width: 250px;
    bottom: 10px;
    right: 10px;
  }
  
  .knowledge-graph-edit-controls {
    padding: 12px;
    flex-wrap: wrap;
  }
  
  .knowledge-graph-edit-controls button {
    flex: 1;
    min-width: 100px;
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .node-detail-panel {
    width: calc(100% - 20px);
    left: 10px;
    right: 10px;
    top: 10px;
    max-height: calc(70% - 20px);
  }
  
  .node-detail-header h4 {
    font-size: 16px;
  }
  
  .node-basic-info .info-row {
    font-size: 13px;
  }
  
  .related-nodes-section h5, .llm-suggestions-section h5 {
    font-size: 15px;
  }
  
  .related-node-item {
    font-size: 13px;
    padding: 8px;
  }
  
  .generated-suggestions li {
    font-size: 13px;
    line-height: 1.5;
  }
  
  .node-actions button {
    width: 48%;
    padding: 8px;
    font-size: 13px;
  }
}

.node-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.node-detail-header h4 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #666;
  background-color: #f0f0f0;
}

.node-basic-info {
  margin-bottom: 16px;
}

.info-row {
  margin-bottom: 8px;
}

.info-label {
  font-weight: 500;
  color: #666;
  margin-right: 8px;
}

.info-value {
  color: #333;
}

.mastery-bar {
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin: 8px 0;
}

.mastery-fill {
  height: 100%;
  background-color: #52c41a;
  transition: width 0.3s ease;
}

.mastery-text {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.related-nodes-section {
  margin-top: 16px;
}

.related-nodes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.related-node-item {
  background-color: #f0f0f0;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.related-node-item:hover {
  background-color: #e0e0e0;
  color: #333;
}

.node-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

/* 节点类型样式 */
.nodes .node-circle {
  transition: all 0.3s ease;
}

.nodes .node-text {
  font-size: 12px;
  fill: #333;
  pointer-events: none;
}

.nodes .node-type-label {
  font-size: 10px;
  fill: #666;
  pointer-events: none;
}

/* 节点状态样式 */
.current-node-indicator {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    stroke-width: 2;
    opacity: 1;
  }
  50% {
    stroke-width: 4;
    opacity: 0.7;
  }
  100% {
    stroke-width: 2;
    opacity: 1;
  }
}

.completed-node-check {
  stroke: #52c41a;
  stroke-width: 2;
}

/* 节点高亮样式 */
.highlighted circle {
  stroke: #1890ff;
  stroke-width: 4px;
}

.highlighted line {
  stroke: #1890ff;
  stroke-width: 3px;
  stroke-opacity: 1;
}

/* 编辑模式样式 */
.edit-mode-controls {
  display: flex;
  gap: 8px;
  margin-left: 16px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h4 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.modal-body {
  margin-bottom: 24px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 按钮样式 */
.btn-primary {
  background-color: #667eea;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: #5a6fd8;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
  transform: translateY(-1px);
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-warning {
  background-color: #faad14;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-warning:hover {
  background-color: #f79e02;
  transform: translateY(-1px);
}

.btn-danger {
  background-color: #ff4d4f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background-color: #ff3838;
  transform: translateY(-1px);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* 对话框底部样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px;
  border-top: 1px solid #f0f0f0;
}

.dialog-footer button {
  padding: 10px 20px;
  font-size: 14px;
}

/* 加载状态样式 */
.generating-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  margin-top: 16px;
}

.loading-spinner-small {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

/* 个性化路径结果样式 */
.personalized-path-result {
  margin-top: 24px;
  padding: 20px;
  background: #f0f4ff;
  border: 1px solid #adc6ff;
  border-radius: 8px;
  animation: fadeIn 0.5s ease-out;
}

.personalized-path-result h4 {
  margin-top: 0;
  color: #1890ff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.path-explanation {
  margin: 12px 0;
  line-height: 1.6;
  color: #333;
}

.path-suggestions h5 {
  margin-bottom: 8px;
  color: #52c41a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.path-suggestions ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.path-suggestions li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #555;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 学习路径组件样式 */
.learning-path-section {
  margin-bottom: 30px;
}

/* 智能推荐路径图样式 */
.smart-path-container {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
}

.smart-path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.smart-path-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.btn-refresh {
  padding: 6px 16px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-refresh:hover {
  background: #e0e0e0;
}

.smart-path-explanation {
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.smart-path-visualization {
  width: 100%;
  overflow: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  padding: 20px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .smart-path-container {
    padding: 16px;
    margin-top: 16px;
  }
  
  .smart-path-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
  }
  
  .smart-path-header h4 {
    font-size: 16px;
  }
  
  .btn-refresh {
    padding: 5px 12px;
    font-size: 13px;
  }
  
  .smart-path-explanation {
    padding: 10px 12px;
    margin-bottom: 16px;
    font-size: 13px;
    line-height: 1.5;
  }
  
  .smart-path-visualization {
    padding: 10px;
    margin-bottom: 16px;
  }
  
  /* 调整路径节点大小 */
  .path-node .node-circle {
    r: 20 !important;
  }
  
  .path-node .node-title {
    font-size: 10px;
  }
  
  .path-node .node-level {
    font-size: 8px;
    dy: 18;
  }
}

.path-svg {
  display: block;
  margin: 0 auto;
}

.path-edge {
  stroke: #4a90e2;
  stroke-width: 2;
  fill: none;
  opacity: 0.6;
  transition: all 0.3s;
}

.path-edge:hover {
  stroke-width: 3;
  opacity: 1;
}

.edge-next {
  stroke: #4a90e2;
}

.edge-prerequisite {
  stroke: #f5a623;
  stroke-dasharray: 5,5;
}

.edge-related {
  stroke: #50e3c2;
  stroke-dasharray: 3,3;
}

.path-node {
  cursor: pointer;
  transition: all 0.3s;
}

.path-node:hover {
  transform: scale(1.1);
}

.node-circle {
  fill: #4a90e2;
  stroke: #fff;
  stroke-width: 2;
  transition: all 0.3s;
}

.path-node:hover .node-circle {
  stroke-width: 3;
  filter: brightness(1.1);
}

.node-concept .node-circle {
  fill: #4a90e2;
}

.node-skill .node-circle {
  fill: #50e3c2;
}

.node-resource .node-circle {
  fill: #f5a623;
}

.node-pending .node-circle {
  opacity: 0.7;
}

.node-current .node-circle {
  fill: #7ed321;
  animation: pulse 2s infinite;
}

.node-completed .node-circle {
  fill: #bd10e0;
}

.difficulty-1 .node-circle {
  fill: #7ed321;
}

.difficulty-2 .node-circle {
  fill: #50e3c2;
}

.difficulty-3 .node-circle {
  fill: #4a90e2;
}

.difficulty-4 .node-circle {
  fill: #f5a623;
}

.difficulty-5 .node-circle {
  fill: #d0021b;
}

.node-title {
  font-size: 12px;
  font-weight: 600;
  fill: #333;
  text-anchor: middle;
  pointer-events: none;
}

.node-level {
  font-size: 10px;
  fill: #666;
  text-anchor: middle;
  pointer-events: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.smart-path-suggestions {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-top: 20px;
}

.smart-path-suggestions h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.smart-path-suggestions ul {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.smart-path-suggestions li {
  padding: 8px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
}

.smart-path-suggestions li:before {
  content: "•";
  color: #4a90e2;
  font-weight: bold;
  position: absolute;
  left: -16px;
}

.no-path {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.no-path p {
  margin: 0 0 16px 0;
  font-size: 14px;
}

.learning-path-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.learning-path-section:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #1890ff;
  transform: translateY(-2px);
}

.learning-path-section h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.current-path {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #f0f0f0;
}

.path-header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.path-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.path-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.path-status.active {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.path-status.completed {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.path-status.paused {
  background: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.path-progress {
  margin-bottom: 16px;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a, #1890ff);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
  text-align: right;
}

.path-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.no-path {
  text-align: center;
  padding: 30px;
  color: #666;
  background: #fafafa;
  border-radius: 8px;
  border: 1px dashed #d9d9d9;
}

.no-path p {
  margin: 0 0 16px 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .path-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left {
    margin-right: 0;
    margin-bottom: 24px;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
  
  .path-header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .path-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .learning-path-view {
    padding: 12px;
  }
  
  .path-header {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .header-subtitle {
    font-size: 14px;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .major-selector {
    justify-content: space-between;
  }
  
  button {
    width: 100%;
    justify-content: center;
  }
  
  .summary-details {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .user-profile-summary {
    padding: 16px;
  }
  
  .summary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .summary-title-section h3 {
    font-size: 18px;
  }
  
  .summary-subtitle {
    font-size: 13px;
  }
  
  .refresh-profile-btn {
    padding: 6px;
    font-size: 16px;
  }
  
  .learning-stats {
    padding: 16px;
    margin-top: 16px;
  }
  
  .learning-stats h4 {
    font-size: 16px;
    margin-bottom: 12px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .stat-value {
    font-size: 14px;
  }
  
  .professional-group-detail {
    padding: 16px;
    margin-top: 16px;
  }
  
  .professional-group-detail h4 {
    font-size: 16px;
    margin-bottom: 12px;
  }
  
  .group-details {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .group-features h5, .group-tools h5, .group-career h5 {
    font-size: 14px;
  }
  
  .feature-tags, .tool-tags, .career-tags {
    gap: 6px;
  }
  
  .feature-tag, .tool-tag, .career-tag {
    font-size: 12px;
    padding: 4px 8px;
  }
  
  .learning-path-section {
    padding: 16px;
  }
  
  .current-path {
    padding: 16px;
  }
  
  .path-title {
    font-size: 16px;
  }
  
  .dialog-content {
    width: 95%;
    margin: 16px;
  }
  
  .dialog-header,
  .dialog-body,
  .dialog-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .dialog-footer {
    flex-direction: column;
  }
  
  .dialog-footer button {
    width: 100%;
  }
}
</style>
