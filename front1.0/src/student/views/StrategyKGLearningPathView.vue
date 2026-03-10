<template>
  <div class="strategy-kg-learning-path">
    <div class="page-header">
      <div class="header-content">
        <h1>
          <span class="header-icon">🧠</span>
          <span class="header-title">StrategyKG 智能学习路径</span>
        </h1>
        <p class="header-subtitle">基于四层知识图谱的个性化学习路径推荐系统</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="refreshData" :disabled="loading">
          <span class="btn-icon">🔄</span>
          刷新数据
        </button>
        <button class="btn-secondary" @click="showProfileDialog = true">
          <span class="btn-icon">👤</span>
          用户画像
        </button>
      </div>
    </div>

    <div class="content-grid">
      <div class="main-content">
        <div class="knowledge-graph-section">
          <div class="section-header">
            <h2>📊 知识图谱可视化</h2>
            <div class="level-tabs">
              <button
                v-for="level in levels"
                :key="level.value"
                class="level-tab"
                :class="{ active: selectedLevel === level.value }"
                @click="selectedLevel = level.value"
              >
                {{ level.label }}
              </button>
            </div>
          </div>

          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>加载知识图谱数据...</p>
          </div>

          <div v-else class="graph-container" ref="graphContainer">
            <svg :viewBox="`0 0 ${graphWidth} ${graphHeight}`" class="knowledge-graph">
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#999" />
                </marker>
              </defs>
              
              <g class="edges">
                <line
                  v-for="edge in filteredEdges"
                  :key="`${edge.source}-${edge.target}`"
                  :x1="getNodePosition(edge.source).x"
                  :y1="getNodePosition(edge.source).y"
                  :x2="getNodePosition(edge.target).x"
                  :y2="getNodePosition(edge.target).y"
                  class="graph-edge"
                  :class="`edge-${edge.relation_type}`"
                  :stroke-width="edge.strength * 2"
                  marker-end="url(#arrowhead)"
                />
                <text
                  v-for="edge in filteredEdges"
                  :key="`label-${edge.source}-${edge.target}`"
                  :x="(getNodePosition(edge.source).x + getNodePosition(edge.target).x) / 2"
                  :y="(getNodePosition(edge.source).y + getNodePosition(edge.target).y) / 2 - 5"
                  class="edge-label"
                >
                  {{ getRelationLabel(edge.relation_type) }}
                </text>
              </g>

              <g class="nodes">
                <g
                  v-for="node in filteredNodes"
                  :key="node.id"
                  :transform="`translate(${node.x}, ${node.y})`"
                  class="graph-node"
                  :class="`node-level-${node.level} node-type-${node.node_type}`"
                  @click="selectNode(node)"
                  @mouseenter="showNodeTooltip(node)"
                  @mouseleave="hideNodeTooltip"
                >
                  <circle
                    :r="getNodeRadius(node)"
                    class="node-circle"
                    :fill="getNodeColor(node)"
                    :stroke="getNodeBorderColor(node)"
                    :stroke-width="getNodeBorderWidth(node)"
                  />
                  <text class="node-title" dy="5">{{ node.title }}</text>
                  <text class="node-level" dy="25">L{{ node.level }}</text>
                  <circle
                    v-if="node.importance >= 4.5"
                    :r="6"
                    class="importance-star"
                    cx="15"
                    cy="-15"
                  />
                </g>
              </g>
            </svg>

            <div v-if="selectedNode" class="node-tooltip" :style="tooltipStyle">
              <h4>{{ selectedNode.title }}</h4>
              <p>{{ selectedNode.description }}</p>
              <div class="node-meta">
                <span class="meta-item">层级: L{{ selectedNode.level }}</span>
                <span class="meta-item">难度: {{ selectedNode.difficulty.toFixed(1) }}</span>
                <span class="meta-item">重要性: {{ selectedNode.importance.toFixed(1) }}</span>
              </div>
              <button class="btn-sm btn-primary" @click="viewNodeDetails(selectedNode)">
                查看详情
              </button>
            </div>
          </div>

          <div class="graph-legend">
            <h4>图例</h4>
            <div class="legend-items">
              <div class="legend-item">
                <div class="legend-color" style="background: #1890ff;"></div>
                <span>Level 0 - 概念层</span>
              </div>
              <div class="legend-item">
                <div class="legend-color" style="background: #52c41a;"></div>
                <span>Level 1 - 分类层</span>
              </div>
              <div class="legend-item">
                <div class="legend-color" style="background: #faad14;"></div>
                <span>Level 2 - 实体层</span>
              </div>
              <div class="legend-item">
                <div class="legend-color" style="background: #722ed1;"></div>
                <span>Level 3 - 动态层</span>
              </div>
            </div>
          </div>
        </div>

        <div class="learning-paths-section">
          <div class="section-header">
            <h2>🎯 推荐学习路径</h2>
            <button class="btn-sm btn-secondary" @click="loadRecommendedPaths">
              刷新推荐
            </button>
          </div>

          <div v-if="pathsLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>加载学习路径...</p>
          </div>

          <div v-else class="paths-grid">
            <div
              v-for="path in recommendedPaths"
              :key="path.id"
              class="path-card"
              @click="selectPath(path)"
            >
              <div class="path-header">
                <h3>{{ path.title }}</h3>
                <span class="difficulty-badge" :class="path.difficulty_level">
                  {{ getDifficultyText(path.difficulty_level) }}
                </span>
              </div>
              <p class="path-description">{{ path.description }}</p>
              <div class="path-stats">
                <span class="stat-item">
                  <span class="stat-icon">⏱️</span>
                  {{ path.estimated_hours }} 小时
                </span>
                <span class="stat-item">
                  <span class="stat-icon">📚</span>
                  {{ path.path_nodes.length }} 个节点
                </span>
              </div>
              <div class="path-tags">
                <span v-for="tag in path.tags.slice(0, 3)" :key="tag" class="tag">
                  {{ tag }}
                </span>
              </div>
              <div class="path-actions">
                <button class="btn-sm btn-primary" @click.stop="startPath(path)">
                  开始学习
                </button>
                <button class="btn-sm btn-secondary" @click.stop="viewPathDetails(path)">
                  查看详情
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar">
        <div class="user-profile-card">
          <h3>👤 用户画像</h3>
          <div v-if="userProfile" class="profile-content">
            <div class="profile-item">
              <span class="profile-label">专业组:</span>
              <span class="profile-value">{{ getProfessionalGroupText(userProfile.professional_group) }}</span>
            </div>
            <div class="profile-item">
              <span class="profile-label">知识水平:</span>
              <span class="profile-value">{{ getKnowledgeLevelText(userProfile.knowledge_level) }}</span>
            </div>
            <div class="profile-item">
              <span class="profile-label">学习风格:</span>
              <span class="profile-value">{{ getLearningStyleText(userProfile.learning_style) }}</span>
            </div>
            <div class="profile-stats">
              <div class="stat-box">
                <div class="stat-value">{{ userProfile.total_learning_minutes }}</div>
                <div class="stat-label">学习时长(分钟)</div>
              </div>
              <div class="stat-box">
                <div class="stat-value">{{ userProfile.completed_practices }}</div>
                <div class="stat-label">完成练习</div>
              </div>
              <div class="stat-box">
                <div class="stat-value">{{ userProfile.avg_practice_score.toFixed(1) }}</div>
                <div class="stat-label">平均得分</div>
              </div>
            </div>
            <div class="profile-interests">
              <h4>兴趣领域</h4>
              <div class="interests-tags">
                <span v-for="interest in userProfile.interests" :key="interest" class="interest-tag">
                  {{ interest }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="no-profile">
            <p>暂无用户画像数据</p>
            <button class="btn-sm btn-primary" @click="showProfileDialog = true">
              创建画像
            </button>
          </div>
        </div>

        <div class="active-paths-card">
          <h3>📚 进行中的学习路径</h3>
          <div v-if="activePaths.length > 0" class="active-paths-list">
            <div
              v-for="userPath in activePaths"
              :key="userPath.id"
              class="active-path-item"
            >
              <div class="path-info">
                <h4>{{ userPath.path_data.title }}</h4>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: userPath.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ userPath.progress }}%</span>
              </div>
              <div class="path-actions">
                <button class="btn-sm btn-primary" @click="continuePath(userPath)">
                  继续
                </button>
              </div>
            </div>
          </div>
          <div v-else class="no-active-paths">
            <p>暂无进行中的学习路径</p>
          </div>
        </div>

        <div class="recommendations-card">
          <h3>💡 个性化推荐</h3>
          <div v-if="recommendations.length > 0" class="recommendations-list">
            <div
              v-for="rec in recommendations"
              :key="rec.id"
              class="recommendation-item"
            >
              <div class="rec-content">
                <h4>{{ rec.recommendation_type_display }}</h4>
                <p>{{ rec.recommendation_reason }}</p>
                <div class="matching-score">
                  <span class="score-label">匹配度:</span>
                  <span class="score-value">{{ (rec.matching_score * 100).toFixed(0) }}%</span>
                </div>
              </div>
              <div class="rec-actions">
                <button class="btn-sm btn-success" @click="acceptRecommendation(rec)">
                  接受
                </button>
                <button class="btn-sm btn-secondary" @click="rejectRecommendation(rec)">
                  拒绝
                </button>
              </div>
            </div>
          </div>
          <div v-else class="no-recommendations">
            <p>暂无推荐内容</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showProfileDialog" class="dialog-overlay" @click="showProfileDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>👤 用户画像设置</h3>
          <button class="dialog-close" @click="showProfileDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>专业组:</label>
            <select v-model="profileForm.professional_group" class="form-input">
              <option value="business">经管类</option>
              <option value="science">理工科</option>
              <option value="humanities">文史类</option>
              <option value="arts">艺术类</option>
            </select>
          </div>
          <div class="form-group">
            <label>知识水平:</label>
            <select v-model="profileForm.knowledge_level" class="form-input">
              <option value="beginner">初学者</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
            </select>
          </div>
          <div class="form-group">
            <label>学习风格:</label>
            <select v-model="profileForm.learning_style" class="form-input">
              <option value="visual">视觉学习者</option>
              <option value="auditory">听觉学习者</option>
              <option value="reading">读写学习者</option>
              <option value="kinesthetic">动手实践学习者</option>
            </select>
          </div>
          <div class="form-group">
            <label>兴趣领域 (用逗号分隔):</label>
            <input
              type="text"
              v-model="interestsInput"
              placeholder="例如: Python, 数据分析, 机器学习"
              class="form-input"
            />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showProfileDialog = false">取消</button>
          <button class="btn-primary" @click="saveProfile">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import strategyAPI from '../api/strategy_kg_api.js'

export default {
  name: 'StrategyKGLearningPath',
  data() {
    return {
      loading: false,
      pathsLoading: false,
      selectedLevel: null,
      graphWidth: 800,
      graphHeight: 600,
      
      levels: [
        { value: null, label: '全部' },
        { value: 0, label: 'Level 0 - 概念层' },
        { value: 1, label: 'Level 1 - 分类层' },
        { value: 2, label: 'Level 2 - 实体层' },
        { value: 3, label: 'Level 3 - 动态层' }
      ],
      
      nodes: [],
      edges: [],
      recommendedPaths: [],
      activePaths: [],
      recommendations: [],
      userProfile: null,
      
      selectedNode: null,
      tooltipStyle: {},
      showProfileDialog: false,
      
      profileForm: {
        professional_group: 'business',
        knowledge_level: 'beginner',
        learning_style: 'visual',
        interests: []
      },
      interestsInput: ''
    }
  },
  computed: {
    filteredNodes() {
      if (this.selectedLevel === null) {
        return this.nodes
      }
      return this.nodes.filter(node => node.level === this.selectedLevel)
    },
    filteredEdges() {
      const nodeIds = new Set(this.filteredNodes.map(n => n.id))
      return this.edges.filter(edge => 
        nodeIds.has(edge.source) && nodeIds.has(edge.target)
      )
    }
  },
  mounted() {
    this.loadGraphData()
    this.loadUserProfile()
    this.loadRecommendedPaths()
    this.loadActivePaths()
    this.loadRecommendations()
  },
  methods: {
    async loadGraphData() {
      this.loading = true
      try {
        const response = await strategyAPI.nodes.graphData()
        this.nodes = response.data.nodes.map(node => ({
          ...node,
          x: this.calculateNodeX(node),
          y: this.calculateNodeY(node)
        }))
        this.edges = response.data.edges
      } catch (error) {
        console.error('加载知识图谱数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadUserProfile() {
      try {
        const response = await strategyAPI.profile.me()
        this.userProfile = response.data
        if (this.userProfile) {
          this.profileForm = {
            professional_group: this.userProfile.professional_group,
            knowledge_level: this.userProfile.knowledge_level,
            learning_style: this.userProfile.learning_style,
            interests: this.userProfile.interests
          }
          this.interestsInput = this.userProfile.interests.join(', ')
        }
      } catch (error) {
        console.error('加载用户画像失败:', error)
      }
    },
    
    async loadRecommendedPaths() {
      this.pathsLoading = true
      try {
        const response = await strategyAPI.paths.recommended({
          professional_group: this.userProfile?.professional_group || 'business'
        })
        this.recommendedPaths = response.data
      } catch (error) {
        console.error('加载推荐路径失败:', error)
      } finally {
        this.pathsLoading = false
      }
    },
    
    async loadActivePaths() {
      try {
        const response = await strategyAPI.userPaths.active()
        this.activePaths = response.data
      } catch (error) {
        console.error('加载进行中的路径失败:', error)
      }
    },
    
    async loadRecommendations() {
      try {
        const response = await strategyAPI.recommendations.list()
        this.recommendations = response.data.slice(0, 5)
      } catch (error) {
        console.error('加载推荐失败:', error)
      }
    },
    
    calculateNodeX(node) {
      const levelWidth = this.graphWidth / 4
      const baseX = levelWidth * node.level + levelWidth / 2
      const offset = (node.id % 5) * 40 - 80
      return baseX + offset
    },
    
    calculateNodeY(node) {
      const levelHeight = this.graphHeight / 5
      return levelHeight * (node.id % 5) + levelHeight / 2
    },
    
    getNodePosition(nodeId) {
      const node = this.nodes.find(n => n.id === nodeId)
      return node ? { x: node.x, y: node.y } : { x: 0, y: 0 }
    },
    
    getNodeRadius(node) {
      return 30 + node.importance * 5
    },
    
    getNodeColor(node) {
      const colors = {
        0: '#1890ff',
        1: '#52c41a',
        2: '#faad14',
        3: '#722ed1'
      }
      return colors[node.level] || '#999'
    },
    
    getNodeBorderColor(node) {
      return node.importance >= 4.5 ? '#ff4d4f' : '#fff'
    },
    
    getNodeBorderWidth(node) {
      return node.importance >= 4.5 ? 3 : 2
    },
    
    getRelationLabel(type) {
      const labels = {
        requires: '前置',
        belongs_to: '属于',
        includes: '包含',
        recommends: '推荐',
        leads_to: '导向',
        applies_to: '应用',
        similar_to: '相似'
      }
      return labels[type] || type
    },
    
    getDifficultyText(difficulty) {
      const texts = {
        beginner: '入门',
        intermediate: '进阶',
        advanced: '高级'
      }
      return texts[difficulty] || difficulty
    },
    
    getProfessionalGroupText(group) {
      const texts = {
        business: '经管类',
        science: '理工科',
        humanities: '文史类',
        arts: '艺术类'
      }
      return texts[group] || group
    },
    
    getKnowledgeLevelText(level) {
      const texts = {
        beginner: '初学者',
        intermediate: '中级',
        advanced: '高级'
      }
      return texts[level] || level
    },
    
    getLearningStyleText(style) {
      const texts = {
        visual: '视觉学习者',
        auditory: '听觉学习者',
        reading: '读写学习者',
        kinesthetic: '动手实践学习者'
      }
      return texts[style] || style
    },
    
    selectNode(node) {
      this.selectedNode = node
    },
    
    showNodeTooltip(node) {
      this.selectedNode = node
    },
    
    hideNodeTooltip() {
      this.selectedNode = null
    },
    
    viewNodeDetails(node) {
      console.log('查看节点详情:', node)
    },
    
    selectPath(path) {
      console.log('选择路径:', path)
    },
    
    async startPath(path) {
      try {
        await strategyAPI.paths.start(path.id)
        this.$message.success('开始学习路径成功！')
        this.loadActivePaths()
      } catch (error) {
        console.error('开始学习路径失败:', error)
        this.$message.error('开始学习路径失败')
      }
    },
    
    viewPathDetails(path) {
      console.log('查看路径详情:', path)
    },
    
    continuePath(userPath) {
      console.log('继续学习路径:', userPath)
    },
    
    async acceptRecommendation(rec) {
      try {
        await strategyAPI.recommendations.accept(rec.id)
        this.$message.success('已接受推荐')
        this.loadRecommendations()
      } catch (error) {
        console.error('接受推荐失败:', error)
        this.$message.error('接受推荐失败')
      }
    },
    
    async rejectRecommendation(rec) {
      try {
        await strategyAPI.recommendations.reject(rec.id, { feedback: '' })
        this.$message.success('已拒绝推荐')
        this.loadRecommendations()
      } catch (error) {
        console.error('拒绝推荐失败:', error)
        this.$message.error('拒绝推荐失败')
      }
    },
    
    async saveProfile() {
      this.profileForm.interests = this.interestsInput
        .split(',')
        .map(i => i.trim())
        .filter(i => i)
      
      try {
        if (this.userProfile) {
          await strategyAPI.profile.me(this.profileForm)
          this.$message.success('更新用户画像成功')
        } else {
          await strategyAPI.profile.create(this.profileForm)
          this.$message.success('创建用户画像成功')
        }
        this.showProfileDialog = false
        this.loadUserProfile()
        this.loadRecommendedPaths()
      } catch (error) {
        console.error('保存用户画像失败:', error)
        this.$message.error('保存用户画像失败')
      }
    },
    
    refreshData() {
      this.loadGraphData()
      this.loadUserProfile()
      this.loadRecommendedPaths()
      this.loadActivePaths()
      this.loadRecommendations()
    }
  }
}
</script>

<style scoped>
.strategy-kg-learning-path {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-content h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 32px;
}

.header-subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.level-tabs {
  display: flex;
  gap: 5px;
}

.level-tab {
  padding: 8px 16px;
  border: none;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.level-tab:hover {
  background: #e6f7ff;
}

.level-tab.active {
  background: #1890ff;
  color: white;
}

.knowledge-graph-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.graph-container {
  position: relative;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.knowledge-graph {
  width: 100%;
  height: auto;
  display: block;
}

.graph-edge {
  stroke: #999;
  stroke-opacity: 0.6;
  transition: stroke-width 0.3s ease;
}

.graph-edge:hover {
  stroke-opacity: 1;
}

.edge-label {
  font-size: 11px;
  fill: #666;
  text-anchor: middle;
}

.graph-node {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.graph-node:hover {
  transform: scale(1.1);
}

.node-circle {
  transition: all 0.3s ease;
}

.node-title {
  font-size: 12px;
  fill: white;
  text-anchor: middle;
  font-weight: 500;
}

.node-level {
  font-size: 10px;
  fill: rgba(255, 255, 255, 0.8);
  text-anchor: middle;
}

.importance-star {
  fill: #ff4d4f;
}

.node-tooltip {
  position: absolute;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 200px;
}

.node-tooltip h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.node-tooltip p {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.node-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 10px;
}

.meta-item {
  font-size: 12px;
  color: #999;
}

.graph-legend {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.graph-legend h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.legend-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.learning-paths-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.paths-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.path-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.path-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #1890ff;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.path-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  flex: 1;
}

.difficulty-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.difficulty-badge.beginner {
  background: #f6ffed;
  color: #52c41a;
}

.difficulty-badge.intermediate {
  background: #fff7e6;
  color: #fa8c16;
}

.difficulty-badge.advanced {
  background: #fff1f0;
  color: #ff4d4f;
}

.path-description {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.path-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 12px;
  color: #999;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 14px;
}

.path-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.tag {
  background: #f0f0f0;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #666;
}

.path-actions {
  display: flex;
  gap: 8px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-profile-card,
.active-paths-card,
.recommendations-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-profile-card h3,
.active-paths-card h3,
.recommendations-card h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.profile-label {
  color: #666;
}

.profile-value {
  font-weight: 500;
  color: #333;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin: 10px 0;
}

.stat-box {
  text-align: center;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 11px;
  color: #999;
}

.profile-interests h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.interests-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.interest-tag {
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.no-profile,
.no-active-paths,
.no-recommendations {
  text-align: center;
  padding: 30px 10px;
  color: #999;
  font-size: 14px;
}

.active-paths-list,
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.active-path-item,
.recommendation-item {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.active-path-item h4,
.recommendation-item h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.active-path-item p,
.recommendation-item p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.progress-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1890ff, #36cfc9);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  color: #999;
}

.matching-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 12px;
}

.score-label {
  color: #666;
}

.score-value {
  font-weight: bold;
  color: #52c41a;
}

.rec-actions {
  display: flex;
  gap: 8px;
}

.dialog-overlay {
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

.dialog-content {
  background: white;
  border-radius: 12px;
  padding: 25px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dialog-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-close:hover {
  color: #333;
}

.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-success {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e6e6e6;
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-success:hover {
  background: #73d13d;
}

.btn-sm {
  padding: 5px 12px;
  font-size: 12px;
}

.btn-icon {
  font-size: 16px;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    order: -1;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .paths-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-stats {
    grid-template-columns: 1fr;
  }
}
</style>