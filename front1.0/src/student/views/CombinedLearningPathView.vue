<template>
  <div class="combined-learning-path">
    <!-- 顶部导航 -->
    <div class="path-header">
      <div class="header-left">
        <h1>
          <span class="title-icon">🧠</span>
          <span class="title-text">智能学习路径</span>
        </h1>
        <p class="header-subtitle">基于知识图谱和AI的个性化学习路径推荐系统</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="generateSmartPath" :disabled="generatingSmartPath">
          <span class="btn-icon">✨</span>
          {{ generatingSmartPath ? '生成中...' : '智能推荐' }}
        </button>
        <button class="btn-secondary" @click="openPreferenceDialog">
          <span class="btn-icon">⚙️</span>
          学习偏好
        </button>
        <button class="btn-secondary" @click="showProfileDialog = true">
          <span class="btn-icon">👤</span>
          用户画像
        </button>
      </div>
    </div>

    <div class="content-grid">
      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 功能标签页 -->
        <div class="feature-tabs">
          <div class="tab-item" :class="{ active: activeTab === 'graph' }" @click="activeTab = 'graph'">
            <span class="tab-icon">📊</span>
            <span class="tab-label">知识图谱</span>
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'records' }" @click="activeTab = 'records'">
            <span class="tab-icon">📋</span>
            <span class="tab-label">学习记录</span>
          </div>
        </div>

        <!-- 知识图谱可视化 -->
        <div v-if="activeTab === 'graph'" class="knowledge-graph-section">
          <div class="section-header">
            <h2>{{ getProfessionalTitle('graph') }}</h2>
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

        <!-- 智能推荐学习路径 -->
        <div class="smart-path-section">
          <div class="section-header">
            <h2>{{ getProfessionalTitle('smartPath') }}</h2>
            <button class="btn-sm btn-secondary" @click="generateSmartPath">
              重新生成
            </button>
          </div>

          <div v-if="smartPathData && smartPathData.nodes && smartPathData.nodes.length > 0" class="smart-path-container">
            <div class="smart-path-explanation" v-if="smartPathData.explanation">
              <p v-html="formatExplanation(smartPathData.explanation)" @click="optimizeExplanation"></p>
              <button class="btn-sm btn-secondary" @click="optimizeExplanation" title="优化解释">
                ✨ 优化解释
              </button>
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
            <div v-if="smartPathData.suggestions && smartPathData.suggestions.length > 0" class="smart-path-suggestions" @click="optimizeSuggestions">
              <h3>{{ getProfessionalTitle('suggestions') }}</h3>
              <ul>
                <li v-for="(suggestion, index) in smartPathData.suggestions" :key="index">{{ suggestion }}</li>
              </ul>
              <button class="btn-sm btn-secondary" @click="optimizeSuggestions" title="优化建议">
                ✨ 优化建议
              </button>
            </div>
          </div>
          <!-- 未生成路径时的提示 -->
          <div v-else class="no-path">
            <p>点击"智能推荐"按钮生成您的个性化学习路径</p>
          </div>
        </div>

        <!-- 推荐学习路径 -->
        <div class="learning-paths-section">
          <div class="section-header">
            <h2>{{ getProfessionalTitle('recommendedPaths') }}</h2>
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

        <!-- 学习路径可视化图表 -->
        <div class="learning-path-visualization" v-if="selectedRoadmap && selectedRoadmap.stages.length > 0">
          <div class="visualization-header">
            <h3>{{ getProfessionalTitle('visualization') }}</h3>
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
              </div>
            </div>
          </div>
        </div>

        <!-- 学习记录标签页内容 -->
        <div v-if="activeTab === 'records'" class="learning-records-section">
          <RecordsView />
        </div>
      </div>

      <!-- 侧边栏 -->
      <div class="sidebar">
        <!-- 用户画像卡片 -->
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

        <!-- 进行中的学习路径 -->
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

        <!-- 个性化推荐 -->
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

    <!-- 学习偏好设置对话框 -->
    <div v-if="showPreferenceDialog" class="dialog-overlay" @click="showPreferenceDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>⚙️ 学习偏好设置</h3>
          <button class="dialog-close" @click="showPreferenceDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>学习风格：</label>
            <select v-model="learningPreferences.style" class="form-input">
              <option value="visual">视觉型</option>
              <option value="auditory">听觉型</option>
              <option value="reading">读写型</option>
              <option value="kinesthetic">动手实践型</option>
            </select>
          </div>
          <div class="form-group">
            <label>学习节奏：</label>
            <select v-model="learningPreferences.pace" class="form-input">
              <option value="fast">快速</option>
              <option value="moderate">适中</option>
              <option value="slow">慢速</option>
            </select>
          </div>
          <div class="form-group">
            <label>难度偏好：</label>
            <select v-model="learningPreferences.difficulty" class="form-input">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
          <div class="form-group">
            <label>每天学习时间（分钟）：</label>
            <input 
              type="number" 
              v-model.number="learningPreferences.dailyMinutes" 
              min="15" 
              max="360"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>感兴趣的领域：</label>
            <input 
              type="text" 
              v-model="learningPreferences.interests" 
              placeholder="例如：Python, 数据分析, 机器学习"
              class="form-input"
            />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showPreferenceDialog = false">取消</button>
          <button class="btn-primary" @click="saveLearningPreferences">保存</button>
        </div>
      </div>
    </div>

    <!-- 用户画像设置对话框 -->
    <div v-if="showProfileDialog" class="dialog-overlay" @click="showProfileDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>👤 用户画像设置</h3>
          <button class="dialog-close" @click="showProfileDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>专业:</label>
            <select v-model="profileForm.professional_group" class="form-input">
              <option value="science">理工类</option>
              <option value="business">经管类</option>
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
import { api } from '../api/api.js'
import strategyAPI from '../api/strategy_kg_api.js'
import RecordsView from './RecordsView.vue'

export default {
  name: 'CombinedLearningPathView',
  data() {
    return {
      // 标签页相关
      activeTab: 'graph',
      
      // 知识图谱相关
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
      selectedNode: null,
      tooltipStyle: {},
      
      // 学习路径相关
      roadmaps: [],
      selectedRoadmap: null,
      userPath: null,
      userPathStages: [],
      generatingSmartPath: false,
      smartPathData: null,
      smartPathWidth: 800,
      smartPathHeight: 400,
      
      // 推荐路径相关
      recommendedPaths: [],
      activePaths: [],
      recommendations: [],
      learnedConcepts: [],
      
      // 用户画像相关
      userProfile: null,
      showProfileDialog: false,
      profileForm: {
        professional_group: 'business',
        knowledge_level: 'beginner',
        learning_style: 'visual',
        interests: []
      },
      interestsInput: '',
      
      // 学习偏好相关
      showPreferenceDialog: false,
      learningPreferences: {
        style: 'visual',
        pace: 'moderate',
        difficulty: 'medium',
        dailyMinutes: 60,
        interests: ''
      },
      
      // 个性化建议相关
      generatingSuggestions: false,
      personalizedSuggestions: [],
      suggestionCategories: {
        learning_method: [],
        time_management: [],
        resource_recommendation: [],
        practice_suggestion: [],
        motivation: []
      },
      
      // 知识图谱可视化相关
      knowledgeGraphNodes: [],
      knowledgeGraphRelations: [],
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
      visualizationType: 'timeline',
      graphLayout: 'hierarchical',
      visibleLayers: ['concept', 'professional', 'skill', 'resource'],
      showKnowledgeGraphExplanation: false,
      generatingGraphExplanation: false,
      knowledgeGraphExplanation: null,
      
      // 个性化路径生成相关
      showPersonalizedPathDialog: false,
      personalizedPathGoal: '',
      personalizedPathMaxNodes: 10,
      generatingPath: false,
      personalizedPathResult: null
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
    // 知识图谱相关方法
    async loadGraphData() {
      this.loading = true
      try {
        // 根据用户专业和兴趣加载差异化知识图谱
        this.nodes = this.getProfessionalGraphNodes()
        this.edges = this.getProfessionalGraphEdges()
        
        // 计算节点位置
        this.nodes = this.nodes.map(node => ({
          ...node,
          x: this.calculateNodeX(node),
          y: this.calculateNodeY(node)
        }))
      } catch (error) {
        console.error('加载知识图谱数据失败:', error)
        // 加载失败时使用默认数据
        this.nodes = this.getDefaultGraphNodes()
        this.edges = this.getDefaultGraphEdges()
        this.nodes = this.nodes.map(node => ({
          ...node,
          x: this.calculateNodeX(node),
          y: this.calculateNodeY(node)
        }))
      } finally {
        this.loading = false
      }
    },
    
    // 根据专业获取知识图谱节点
    getProfessionalGraphNodes() {
      const professionalGroup = this.userProfile?.professional_group || 'science'
      const interests = this.userProfile?.interests || []
      
      // 不同专业的知识图谱节点
      const professionalNodes = {
        // 理工类（默认使用计算机科学）
        science: [
          { id: 1, title: '人工智能', level: 0, node_type: 'concept', difficulty: 4.5, importance: 5.0, description: '人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学' },
          { id: 2, title: '机器学习', level: 1, node_type: 'category', difficulty: 4.0, importance: 4.8, description: '机器学习是人工智能的一个分支，通过算法让计算机从数据中学习规律' },
          { id: 3, title: '深度学习', level: 2, node_type: 'entity', difficulty: 4.5, importance: 4.6, description: '深度学习是机器学习的一个分支，通过模拟人脑的神经网络结构进行学习' },
          { id: 4, title: '神经网络', level: 3, node_type: 'dynamic', difficulty: 4.8, importance: 4.7, description: '神经网络是深度学习的核心模型，由大量的神经元相互连接组成' },
          { id: 5, title: '监督学习', level: 1, node_type: 'category', difficulty: 3.5, importance: 4.5, description: '监督学习是机器学习的一种方法，通过已标记的训练数据学习模型' },
          { id: 6, title: '无监督学习', level: 1, node_type: 'category', difficulty: 4.0, importance: 4.2, description: '无监督学习是机器学习的一种方法，通过未标记的数据学习模型' },
          { id: 7, title: '强化学习', level: 1, node_type: 'category', difficulty: 4.2, importance: 4.3, description: '强化学习是机器学习的一种方法，通过与环境的交互学习最优策略' },
          { id: 8, title: '计算机视觉', level: 2, node_type: 'entity', difficulty: 4.3, importance: 4.4, description: '计算机视觉是人工智能的一个分支，让计算机能够理解和解释图像' },
          { id: 9, title: '自然语言处理', level: 2, node_type: 'entity', difficulty: 4.4, importance: 4.5, description: '自然语言处理是人工智能的一个分支，让计算机能够理解和处理人类语言' },
          { id: 10, title: '算法设计', level: 1, node_type: 'skill', difficulty: 3.8, importance: 4.6, description: '算法设计是计算机科学的核心，涉及设计高效的问题解决方法' }
        ],
        // 经管类
        business: [
          { id: 1, title: '管理学', level: 0, node_type: 'concept', difficulty: 3.5, importance: 4.5, description: '管理学是研究人类管理活动规律及其应用的科学' },
          { id: 2, title: '经济学', level: 1, node_type: 'category', difficulty: 4.0, importance: 4.3, description: '经济学是研究人类经济活动规律的科学' },
          { id: 3, title: '市场营销', level: 1, node_type: 'category', difficulty: 3.8, importance: 4.2, description: '市场营销是研究企业如何满足消费者需求的学科' },
          { id: 4, title: '计算机基础', level: 0, node_type: 'concept', difficulty: 3.0, importance: 4.8, description: '计算机基础是学习计算机相关知识的入门课程，包括计算机硬件、软件和操作系统等' },
          { id: 5, title: '数据分析', level: 1, node_type: 'category', difficulty: 3.5, importance: 4.7, description: '数据分析是通过收集、处理和分析数据来提取有价值信息的过程' },
          { id: 6, title: '商业智能', level: 2, node_type: 'entity', difficulty: 3.8, importance: 4.6, description: '商业智能是利用技术和工具来分析商业数据，支持决策制定的过程' },
          { id: 7, title: '人工智能应用', level: 2, node_type: 'entity', difficulty: 4.0, importance: 4.5, description: '人工智能在商业领域的应用，如客户服务、市场预测、风险管理等' },
          { id: 8, title: '办公自动化', level: 1, node_type: 'skill', difficulty: 2.5, importance: 4.4, description: '利用计算机技术提高办公效率的方法和工具' },
          { id: 9, title: '数据可视化', level: 1, node_type: 'skill', difficulty: 3.2, importance: 4.3, description: '将数据转化为视觉形式，便于理解和分析的技术' },
          { id: 10, title: '电子商务', level: 2, node_type: 'entity', difficulty: 3.6, importance: 4.2, description: '利用互联网进行商业活动的模式和技术' }
        ],
        // 文史类
        humanities: [
          { id: 1, title: '文学', level: 0, node_type: 'concept', difficulty: 3.5, importance: 4.5, description: '文学是研究人类语言艺术的学科' },
          { id: 2, title: '历史', level: 1, node_type: 'category', difficulty: 3.8, importance: 4.3, description: '历史是研究人类社会发展过程的学科' },
          { id: 3, title: '计算机基础', level: 0, node_type: 'concept', difficulty: 3.0, importance: 4.8, description: '计算机基础是学习计算机相关知识的入门课程，包括计算机硬件、软件和操作系统等' },
          { id: 4, title: '文本分析', level: 1, node_type: 'category', difficulty: 3.5, importance: 4.7, description: '文本分析是利用计算机技术对文本数据进行处理和分析的方法' },
          { id: 5, title: '自然语言处理', level: 2, node_type: 'entity', difficulty: 4.0, importance: 4.6, description: '自然语言处理是让计算机能够理解和处理人类语言的技术' },
          { id: 6, title: '数字人文', level: 2, node_type: 'entity', difficulty: 3.8, importance: 4.5, description: '数字人文是利用数字技术研究人文学科的方法和领域' },
          { id: 7, title: '内容管理', level: 1, node_type: 'skill', difficulty: 3.2, importance: 4.4, description: '利用计算机技术管理和组织信息内容的方法' },
          { id: 8, title: '信息检索', level: 1, node_type: 'skill', difficulty: 3.3, importance: 4.3, description: '利用计算机技术从大量信息中获取所需信息的方法' },
          { id: 9, title: '数字档案管理', level: 2, node_type: 'entity', difficulty: 3.6, importance: 4.2, description: '利用数字技术管理和保存档案资料的方法' },
          { id: 10, title: 'AI伦理', level: 1, node_type: 'skill', difficulty: 3.7, importance: 4.1, description: '人工智能发展中的伦理问题和社会影响' }
        ],
        // 艺术类
        arts: [
          { id: 1, title: '艺术', level: 0, node_type: 'concept', difficulty: 3.5, importance: 4.5, description: '艺术是人类创造的审美产品和审美活动的总和' },
          { id: 2, title: '音乐', level: 1, node_type: 'category', difficulty: 4.0, importance: 4.3, description: '音乐是通过声音表达情感和思想的艺术形式' },
          { id: 3, title: '计算机基础', level: 0, node_type: 'concept', difficulty: 3.0, importance: 4.8, description: '计算机基础是学习计算机相关知识的入门课程，包括计算机硬件、软件和操作系统等' },
          { id: 4, title: '创意编程', level: 1, node_type: 'category', difficulty: 3.8, importance: 4.7, description: '利用编程技术进行创意表达和艺术创作的方法' },
          { id: 5, title: '数字媒体', level: 2, node_type: 'entity', difficulty: 3.6, importance: 4.6, description: '利用数字技术创作和传播媒体内容的领域' },
          { id: 6, title: '生成式AI', level: 2, node_type: 'entity', difficulty: 4.0, importance: 4.5, description: '利用人工智能技术生成创意内容的方法和工具' },
          { id: 7, title: '交互设计', level: 1, node_type: 'skill', difficulty: 3.5, importance: 4.4, description: '设计用户与计算机系统交互方式的方法' },
          { id: 8, title: '数字艺术', level: 2, node_type: 'entity', difficulty: 3.9, importance: 4.3, description: '利用数字技术创作的艺术作品和艺术形式' },
          { id: 9, title: '设计工具', level: 1, node_type: 'skill', difficulty: 3.2, importance: 4.2, description: '用于艺术设计和创作的计算机工具和软件' },
          { id: 10, title: '多媒体制作', level: 2, node_type: 'entity', difficulty: 3.7, importance: 4.1, description: '利用计算机技术制作多媒体内容的方法' }
        ]
      }
      
      // 获取对应专业的节点
      let nodes = professionalNodes[professionalGroup] || professionalNodes.science
      
      // 根据兴趣调整节点重要性
      if (interests.length > 0) {
        nodes = nodes.map(node => {
          let importance = node.importance
          // 根据兴趣调整重要性
          if (interests.some(interest => 
            node.title.toLowerCase().includes(interest.toLowerCase()) ||
            node.description.toLowerCase().includes(interest.toLowerCase())
          )) {
            importance = Math.min(5.0, importance + 0.5)
          }
          return { ...node, importance }
        })
      }
      
      return nodes
    },
    
    // 根据专业获取知识图谱边
    getProfessionalGraphEdges() {
      const professionalGroup = this.userProfile?.professional_group || 'science'
      
      // 不同专业的知识图谱边
      const professionalEdges = {
        // 理工类
        science: [
          { source: 1, target: 2, relation_type: 'includes', strength: 0.9 },
          { source: 2, target: 3, relation_type: 'includes', strength: 0.8 },
          { source: 3, target: 4, relation_type: 'requires', strength: 0.9 },
          { source: 2, target: 5, relation_type: 'includes', strength: 0.8 },
          { source: 2, target: 6, relation_type: 'includes', strength: 0.7 },
          { source: 2, target: 7, relation_type: 'includes', strength: 0.7 },
          { source: 1, target: 8, relation_type: 'includes', strength: 0.8 },
          { source: 1, target: 9, relation_type: 'includes', strength: 0.8 },
          { source: 2, target: 10, relation_type: 'requires', strength: 0.6 }
        ],
        // 经管类
        business: [
          { source: 1, target: 2, relation_type: 'includes', strength: 0.9 },
          { source: 1, target: 3, relation_type: 'includes', strength: 0.8 },
          { source: 4, target: 5, relation_type: 'requires', strength: 0.9 },
          { source: 5, target: 6, relation_type: 'includes', strength: 0.8 },
          { source: 5, target: 9, relation_type: 'includes', strength: 0.7 },
          { source: 6, target: 7, relation_type: 'requires', strength: 0.8 },
          { source: 3, target: 7, relation_type: 'applies', strength: 0.7 },
          { source: 4, target: 8, relation_type: 'enables', strength: 0.9 },
          { source: 8, target: 10, relation_type: 'supports', strength: 0.8 }
        ],
        // 文史类
        humanities: [
          { source: 1, target: 2, relation_type: 'includes', strength: 0.9 },
          { source: 3, target: 4, relation_type: 'requires', strength: 0.9 },
          { source: 4, target: 5, relation_type: 'includes', strength: 0.8 },
          { source: 5, target: 6, relation_type: 'applies', strength: 0.7 },
          { source: 1, target: 4, relation_type: 'applies', strength: 0.7 },
          { source: 2, target: 9, relation_type: 'supports', strength: 0.8 },
          { source: 3, target: 7, relation_type: 'enables', strength: 0.8 },
          { source: 3, target: 8, relation_type: 'enables', strength: 0.9 },
          { source: 5, target: 10, relation_type: 'raises', strength: 0.7 }
        ],
        // 艺术类
        arts: [
          { source: 1, target: 2, relation_type: 'includes', strength: 0.9 },
          { source: 3, target: 4, relation_type: 'requires', strength: 0.9 },
          { source: 4, target: 5, relation_type: 'includes', strength: 0.8 },
          { source: 5, target: 8, relation_type: 'includes', strength: 0.9 },
          { source: 4, target: 6, relation_type: 'uses', strength: 0.8 },
          { source: 6, target: 8, relation_type: 'creates', strength: 0.7 },
          { source: 3, target: 7, relation_type: 'enables', strength: 0.8 },
          { source: 3, target: 9, relation_type: 'enables', strength: 0.9 },
          { source: 5, target: 10, relation_type: 'includes', strength: 0.8 }
        ]
      }
      
      return professionalEdges[professionalGroup] || professionalEdges.science
    },
    
    // 默认知识图谱节点
    getDefaultGraphNodes() {
      return [
        { id: 1, title: '人工智能', level: 0, node_type: 'concept', difficulty: 4.5, importance: 5.0, description: '人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学' },
        { id: 2, title: '机器学习', level: 1, node_type: 'category', difficulty: 4.0, importance: 4.8, description: '机器学习是人工智能的一个分支，通过算法让计算机从数据中学习规律' },
        { id: 3, title: '深度学习', level: 2, node_type: 'entity', difficulty: 4.5, importance: 4.6, description: '深度学习是机器学习的一个分支，通过模拟人脑的神经网络结构进行学习' },
        { id: 4, title: '神经网络', level: 3, node_type: 'dynamic', difficulty: 4.8, importance: 4.7, description: '神经网络是深度学习的核心模型，由大量的神经元相互连接组成' }
      ]
    },
    
    // 默认知识图谱边
    getDefaultGraphEdges() {
      return [
        { source: 1, target: 2, relation_type: 'includes', strength: 0.9 },
        { source: 2, target: 3, relation_type: 'includes', strength: 0.8 },
        { source: 3, target: 4, relation_type: 'requires', strength: 0.9 }
      ]
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
    
    // 用户画像相关方法
    async loadUserProfile() {
      try {
        // 模拟数据，解决用户画像加载错误
        this.userProfile = {
          professional_group: 'science',
          knowledge_level: 'intermediate',
          learning_style: 'visual',
          interests: ['人工智能', '机器学习', '深度学习'],
          total_learning_minutes: 1200,
          completed_practices: 25,
          avg_practice_score: 85.5
        }
        
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
        // 加载失败时使用默认数据
        this.userProfile = {
          professional_group: 'business',
          knowledge_level: 'beginner',
          learning_style: 'visual',
          interests: ['编程', '数据科学'],
          total_learning_minutes: 0,
          completed_practices: 0,
          avg_practice_score: 0
        }
      }
    },
    
    async saveProfile() {
      this.profileForm.interests = this.interestsInput
        .split(',')
        .map(i => i.trim())
        .filter(i => i)
      
      try {
        // 模拟保存用户画像
        this.userProfile = {
          ...this.profileForm,
          total_learning_minutes: this.userProfile?.total_learning_minutes || 0,
          completed_practices: this.userProfile?.completed_practices || 0,
          avg_practice_score: this.userProfile?.avg_practice_score || 0
        }
        // 重新加载知识图谱和推荐路径，以反映新的专业类别
        await this.loadGraphData()
        await this.loadRecommendedPaths()
        alert('保存用户画像成功')
        this.showProfileDialog = false
      } catch (error) {
        console.error('保存用户画像失败:', error)
        alert('保存用户画像失败')
      }
    },
    
    // 推荐路径相关方法
    async loadRecommendedPaths() {
      this.pathsLoading = true
      try {
        // 根据用户专业和兴趣生成差异化推荐路径
        this.recommendedPaths = this.getProfessionalRecommendedPaths()
      } catch (error) {
        console.error('加载推荐路径失败:', error)
        // 加载失败时使用默认数据
        this.recommendedPaths = this.getDefaultRecommendedPaths()
      } finally {
        this.pathsLoading = false
      }
    },
    
    // 根据专业获取推荐路径
    getProfessionalRecommendedPaths() {
      const professionalGroup = this.userProfile?.professional_group || 'science'
      const interests = this.userProfile?.interests || []
      const knowledgeLevel = this.userProfile?.knowledge_level || 'beginner'
      
      // 不同专业的推荐路径
      const professionalPaths = {
        // 理工类
        science: [
          {
            id: 1,
            title: '人工智能入门路径',
            description: '从基础概念到实践应用的完整学习路径',
            difficulty_level: 'beginner',
            estimated_hours: 40,
            path_nodes: [1, 2, 5, 6],
            tags: ['人工智能', '机器学习', '入门'],
            professional_focus: '理工类',
            match_score: 0.95
          },
          {
            id: 2,
            title: '算法与数据结构进阶',
            description: '深入学习计算机科学核心算法与数据结构',
            difficulty_level: 'intermediate',
            estimated_hours: 60,
            path_nodes: [2, 3, 4, 10],
            tags: ['算法', '数据结构', '进阶'],
            professional_focus: '理工类',
            match_score: 0.9
          },
          {
            id: 3,
            title: '计算机视觉专业路径',
            description: '专注于计算机视觉领域的专业学习路径',
            difficulty_level: 'advanced',
            estimated_hours: 80,
            path_nodes: [2, 3, 8, 9],
            tags: ['计算机视觉', '深度学习', '高级'],
            professional_focus: '理工类',
            match_score: 0.85
          }
        ],
        // 经管类
        business: [
          {
            id: 1,
            title: '管理学基础路径',
            description: '从管理学基础到实践应用的完整学习路径',
            difficulty_level: 'beginner',
            estimated_hours: 40,
            path_nodes: [1, 2, 3, 5],
            tags: ['管理学', '经济学', '入门'],
            professional_focus: '经管类',
            match_score: 0.95
          },
          {
            id: 2,
            title: '财务管理进阶',
            description: '深入学习财务管理的核心概念和实践',
            difficulty_level: 'intermediate',
            estimated_hours: 60,
            path_nodes: [1, 4, 8, 6],
            tags: ['财务管理', '会计学', '进阶'],
            professional_focus: '经管类',
            match_score: 0.9
          },
          {
            id: 3,
            title: '战略管理专业路径',
            description: '专注于企业战略管理的专业学习路径',
            difficulty_level: 'advanced',
            estimated_hours: 80,
            path_nodes: [1, 6, 7, 10],
            tags: ['战略管理', '运营管理', '高级'],
            professional_focus: '经管类',
            match_score: 0.85
          }
        ],
        // 文史类
        humanities: [
          {
            id: 1,
            title: '文学基础路径',
            description: '从文学基础到文学批评的完整学习路径',
            difficulty_level: 'beginner',
            estimated_hours: 40,
            path_nodes: [1, 2, 4, 10],
            tags: ['文学', '历史', '入门'],
            professional_focus: '文史类',
            match_score: 0.95
          },
          {
            id: 2,
            title: '哲学与伦理学进阶',
            description: '深入学习哲学和伦理学的核心概念',
            difficulty_level: 'intermediate',
            estimated_hours: 60,
            path_nodes: [1, 3, 10, 6],
            tags: ['哲学', '伦理学', '进阶'],
            professional_focus: '文史类',
            match_score: 0.9
          },
          {
            id: 3,
            title: '社会科学专业路径',
            description: '专注于社会学和政治学的专业学习路径',
            difficulty_level: 'advanced',
            estimated_hours: 80,
            path_nodes: [1, 6, 7, 8],
            tags: ['社会学', '政治学', '高级'],
            professional_focus: '文史类',
            match_score: 0.85
          }
        ],
        // 艺术类
        arts: [
          {
            id: 1,
            title: '艺术基础路径',
            description: '从艺术基础到艺术欣赏的完整学习路径',
            difficulty_level: 'beginner',
            estimated_hours: 40,
            path_nodes: [1, 2, 3, 10],
            tags: ['艺术', '音乐', '绘画', '入门'],
            professional_focus: '艺术类',
            match_score: 0.95
          },
          {
            id: 2,
            title: '设计与创意进阶',
            description: '深入学习设计原理和创意表达',
            difficulty_level: 'intermediate',
            estimated_hours: 60,
            path_nodes: [1, 8, 9, 3],
            tags: ['设计', '摄影', '进阶'],
            professional_focus: '艺术类',
            match_score: 0.9
          },
          {
            id: 3,
            title: '表演艺术专业路径',
            description: '专注于戏剧和舞蹈的专业学习路径',
            difficulty_level: 'advanced',
            estimated_hours: 80,
            path_nodes: [1, 5, 6, 7],
            tags: ['戏剧', '舞蹈', '电影', '高级'],
            professional_focus: '艺术类',
            match_score: 0.85
          }
        ]
      }
      
      // 获取对应专业的路径
      let paths = professionalPaths[professionalGroup] || professionalPaths.science
      
      // 根据知识水平过滤路径
      paths = paths.filter(path => {
        if (knowledgeLevel === 'beginner') {
          return path.difficulty_level === 'beginner'
        } else if (knowledgeLevel === 'intermediate') {
          return path.difficulty_level === 'beginner' || path.difficulty_level === 'intermediate'
        } else {
          return true
        }
      })
      
      // 根据兴趣调整匹配分数
      if (interests.length > 0) {
        paths = paths.map(path => {
          let matchScore = path.match_score
          // 根据兴趣调整匹配分数
          if (interests.some(interest => 
            path.title.toLowerCase().includes(interest.toLowerCase()) ||
            path.description.toLowerCase().includes(interest.toLowerCase()) ||
            path.tags.some(tag => tag.toLowerCase().includes(interest.toLowerCase()))
          )) {
            matchScore = Math.min(1.0, matchScore + 0.1)
          }
          return { ...path, match_score: matchScore }
        })
      }
      
      // 按匹配分数排序
      paths.sort((a, b) => b.match_score - a.match_score)
      
      return paths
    },
    
    // 默认推荐路径
    getDefaultRecommendedPaths() {
      return [
        {
          id: 1,
          title: '人工智能入门路径',
          description: '从基础概念到实践应用的完整学习路径',
          difficulty_level: 'beginner',
          estimated_hours: 40,
          path_nodes: [1, 2],
          tags: ['人工智能', '机器学习', '入门'],
          professional_focus: '通用',
          match_score: 0.8
        },
        {
          id: 2,
          title: '数据科学基础路径',
          description: '从数据基础到分析应用的学习路径',
          difficulty_level: 'beginner',
          estimated_hours: 45,
          path_nodes: [1, 2],
          tags: ['数据科学', '统计分析', '入门'],
          professional_focus: '通用',
          match_score: 0.75
        },
        {
          id: 3,
          title: '软件工程基础路径',
          description: '从软件工程基础到实践的学习路径',
          difficulty_level: 'beginner',
          estimated_hours: 40,
          path_nodes: [1, 2],
          tags: ['软件工程', '需求分析', '入门'],
          professional_focus: '通用',
          match_score: 0.7
        }
      ]
    },
    
    async loadActivePaths() {
      try {
        // 模拟数据，解决进行中路径加载错误
        this.activePaths = [
          {
            id: 1,
            path_data: {
              title: '人工智能入门路径'
            },
            progress: 30
          }
        ]
      } catch (error) {
        console.error('加载进行中的路径失败:', error)
        this.activePaths = []
      }
    },
    
    async loadRecommendations() {
      try {
        // 模拟数据，解决推荐加载错误
        this.recommendations = [
          {
            id: 1,
            recommendation_type_display: '学习资源',
            recommendation_reason: '推荐学习《人工智能导论》课程，适合您的知识水平',
            matching_score: 0.9
          },
          {
            id: 2,
            recommendation_type_display: '学习方法',
            recommendation_reason: '建议采用项目式学习方法，结合理论和实践',
            matching_score: 0.85
          }
        ]
      } catch (error) {
        console.error('加载推荐失败:', error)
        this.recommendations = []
      }
    },
    
    selectPath(path) {
      console.log('选择路径:', path)
      this.selectedRoadmap = {
        id: path.id,
        title: path.title,
        description: path.description,
        difficulty_level: path.difficulty_level,
        estimated_hours: path.estimated_hours,
        stages: [
          {
            id: 1,
            stage_order: 1,
            title: '基础概念',
            description: '学习人工智能的基本概念和发展历史',
            estimated_duration: 10,
            books: [
              { id: 1, title: '人工智能导论', author: '斯图尔特·罗素' }
            ],
            learning_goals: ['理解人工智能的基本概念', '了解人工智能的发展历史', '掌握人工智能的主要分支']
          },
          {
            id: 2,
            stage_order: 2,
            title: '机器学习基础',
            description: '学习机器学习的基本原理和算法',
            estimated_duration: 15,
            books: [
              { id: 2, title: '机器学习', author: '周志华' }
            ],
            learning_goals: ['掌握机器学习的基本原理', '了解常用的机器学习算法', '能够应用机器学习解决简单问题']
          },
          {
            id: 3,
            stage_order: 3,
            title: '实践应用',
            description: '通过项目实践应用所学知识',
            estimated_duration: 15,
            books: [
              { id: 3, title: '人工智能实践', author: '李开复' }
            ],
            learning_goals: ['完成至少一个人工智能项目', '掌握人工智能开发工具', '了解人工智能的实际应用场景']
          }
        ]
      }
    },
    
    async startPath(path) {
      try {
        // 模拟开始学习路径
        alert('开始学习路径成功！')
        this.activePath = path
      } catch (error) {
        console.error('开始学习路径失败:', error)
        alert('开始学习路径失败')
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
        // 模拟接受推荐
        alert('已接受推荐')
        this.loadRecommendations()
      } catch (error) {
        console.error('接受推荐失败:', error)
        alert('接受推荐失败')
      }
    },
    
    async rejectRecommendation(rec) {
      try {
        // 模拟拒绝推荐
        alert('已拒绝推荐')
        this.loadRecommendations()
      } catch (error) {
        console.error('拒绝推荐失败:', error)
        alert('拒绝推荐失败')
      }
    },
    
    // 智能路径生成相关方法
    async generateSmartPath() {
      this.generatingSmartPath = true
      try {
        // 收集用户历史交互数据
        const userContext = this.collectUserContext()
        
        // 生成智能路径提示词
        const prompt = `基于用户的学习历史和偏好，生成一条个性化的学习路径。
        用户信息：
        - 专业领域: ${this.getProfessionalGroupText(this.userProfile?.professional_group || 'science')}
        - 学习目标: ${this.userProfile?.learning_goals || '未设置'}
        - 知识水平: ${this.userProfile?.knowledge_level || '初级'}
        - 学习风格: ${this.userProfile?.learning_style || '视觉型'}
        - 兴趣方向: ${this.userProfile?.interests?.join(', ') || '未设置'}
        - 已学概念: ${this.learnedConcepts?.join(', ') || '无'}
        - 学习偏好: ${this.formatLearningPreferences() || '未设置'}
        
        请生成：
        1. 一条从基础到高级的学习路径，包含4-5个核心节点，要体现${this.getProfessionalGroupText(this.userProfile?.professional_group || 'science')}专业的特点
        2. 对路径的详细解释，说明为什么这样设计，特别是如何适应${this.getProfessionalGroupText(this.userProfile?.professional_group || 'science')}专业的需求
        3. 针对每条路径节点的具体学习建议，要考虑${this.getProfessionalGroupText(this.userProfile?.professional_group || 'science')}专业的应用场景
        4. 学习时间安排建议
        
        格式要求：
        - 路径节点：以JSON数组格式返回，包含id、title、type、difficulty、importance、level字段
        - 路径边：以JSON数组格式返回，包含source、target、type字段
        - 解释：以字符串格式返回
        - 建议：以字符串数组格式返回`
        
        // 调用AI助手API
        const aiResponse = await api.getAIAssistantResponse(prompt, true)
        
        // 解析AI响应
        let smartPathData
        try {
          // 尝试解析AI返回的JSON
          smartPathData = JSON.parse(aiResponse.answer)
        } catch (e) {
          // 如果解析失败，使用默认路径
          console.warn('AI响应解析失败，使用默认路径:', e)
          smartPathData = this.getDefaultSmartPath()
        }
        
        this.smartPathData = smartPathData
      } catch (error) {
        console.error('生成智能路径失败:', error)
        // 使用默认路径作为 fallback
        this.smartPathData = this.getDefaultSmartPath()
        alert('生成智能路径失败，使用默认路径')
      } finally {
        this.generatingSmartPath = false
      }
    },
    
    // 默认智能路径（作为 fallback）
    getDefaultSmartPath() {
      const professionalGroup = this.userProfile?.professional_group || 'computer_science'
      
      // 不同专业的默认智能路径
      const defaultPaths = {
        // 计算机科学专业
        computer_science: {
          nodes: [
            { id: 1, title: '人工智能基础', x: 100, y: 200, type: 'concept', status: 'completed', importance: 1.0, difficulty: 1.0, level: 0 },
            { id: 2, title: '机器学习', x: 300, y: 150, type: 'skill', status: 'current', importance: 1.2, difficulty: 2.0, level: 1 },
            { id: 3, title: '深度学习', x: 500, y: 200, type: 'skill', status: 'pending', importance: 1.5, difficulty: 3.0, level: 2 },
            { id: 4, title: '神经网络', x: 700, y: 150, type: 'skill', status: 'pending', importance: 1.3, difficulty: 3.5, level: 3 },
            { id: 5, title: '算法设计', x: 300, y: 250, type: 'skill', status: 'pending', importance: 1.4, difficulty: 2.5, level: 1 }
          ],
          edges: [
            { source: 1, target: 2, type: 'requires' },
            { source: 2, target: 3, type: 'requires' },
            { source: 3, target: 4, type: 'requires' },
            { source: 1, target: 5, type: 'requires' },
            { source: 5, target: 2, type: 'requires' }
          ],
          explanation: '基于您的计算机科学专业背景，我们为您生成了这条从基础到高级的学习路径。路径包含了人工智能的核心概念和技能，同时强调算法设计的重要性，帮助您系统性地掌握相关知识。',
          suggestions: [
            '建议每天学习1-2小时，保持学习的连贯性',
            '在学习机器学习时，多做实践练习巩固知识点',
            '深度学习部分建议结合视频教程和实践项目',
            '算法设计是计算机科学的核心，建议重点学习',
            '建议每周投入10-15小时进行学习和实践'
          ]
        },
        // 数据科学专业
        data_science: {
          nodes: [
            { id: 1, title: '数据科学基础', x: 100, y: 200, type: 'concept', status: 'completed', importance: 1.0, difficulty: 1.0, level: 0 },
            { id: 2, title: '统计分析', x: 300, y: 150, type: 'skill', status: 'current', importance: 1.2, difficulty: 2.0, level: 1 },
            { id: 3, title: '数据可视化', x: 300, y: 250, type: 'skill', status: 'pending', importance: 1.1, difficulty: 1.5, level: 1 },
            { id: 4, title: '机器学习', x: 500, y: 200, type: 'skill', status: 'pending', importance: 1.5, difficulty: 3.0, level: 2 },
            { id: 5, title: '数据挖掘', x: 700, y: 150, type: 'skill', status: 'pending', importance: 1.4, difficulty: 2.5, level: 2 }
          ],
          edges: [
            { source: 1, target: 2, type: 'requires' },
            { source: 1, target: 3, type: 'requires' },
            { source: 2, target: 4, type: 'requires' },
            { source: 2, target: 5, type: 'requires' },
            { source: 3, target: 5, type: 'requires' }
          ],
          explanation: '基于您的数据科学专业背景，我们为您生成了这条从基础到高级的学习路径。路径包含了数据科学的核心概念和技能，重点培养统计分析和数据处理能力，帮助您系统性地掌握相关知识。',
          suggestions: [
            '建议每天学习1-2小时，保持学习的连贯性',
            '统计分析是数据科学的基础，建议重点学习',
            '数据可视化能力对于数据科学非常重要，建议多实践',
            '机器学习是数据科学的核心技术，要深入学习各种算法',
            '建议参与实际数据科学项目，积累实践经验'
          ]
        },
        // 软件工程专业
        software_engineering: {
          nodes: [
            { id: 1, title: '软件工程基础', x: 100, y: 200, type: 'concept', status: 'completed', importance: 1.0, difficulty: 1.0, level: 0 },
            { id: 2, title: '需求分析', x: 300, y: 150, type: 'skill', status: 'current', importance: 1.1, difficulty: 1.5, level: 1 },
            { id: 3, title: '系统设计', x: 300, y: 250, type: 'skill', status: 'pending', importance: 1.3, difficulty: 2.0, level: 1 },
            { id: 4, title: '编码实现', x: 500, y: 200, type: 'skill', status: 'pending', importance: 1.4, difficulty: 2.5, level: 2 },
            { id: 5, title: '软件架构', x: 700, y: 150, type: 'skill', status: 'pending', importance: 1.5, difficulty: 3.0, level: 2 }
          ],
          edges: [
            { source: 1, target: 2, type: 'requires' },
            { source: 1, target: 3, type: 'requires' },
            { source: 2, target: 3, type: 'requires' },
            { source: 3, target: 4, type: 'requires' },
            { source: 3, target: 5, type: 'requires' }
          ],
          explanation: '基于您的软件工程专业背景，我们为您生成了这条从基础到高级的学习路径。路径包含了软件工程的核心概念和技能，重点培养需求分析和系统设计能力，帮助您系统性地掌握相关知识。',
          suggestions: [
            '建议每天学习1-2小时，保持学习的连贯性',
            '需求分析是软件开发的起点，要重点学习',
            '系统设计能力对于软件质量至关重要，建议多实践',
            '编码实现要注重代码质量和可维护性',
            '软件架构设计是高级软件工程师的核心能力，要深入学习'
          ]
        },
        // 电子工程专业
        electrical_engineering: {
          nodes: [
            { id: 1, title: '电子工程基础', x: 100, y: 200, type: 'concept', status: 'completed', importance: 1.0, difficulty: 1.0, level: 0 },
            { id: 2, title: '电路分析', x: 300, y: 150, type: 'skill', status: 'current', importance: 1.3, difficulty: 2.0, level: 1 },
            { id: 3, title: '数字电子', x: 300, y: 250, type: 'skill', status: 'pending', importance: 1.2, difficulty: 2.0, level: 1 },
            { id: 4, title: '微处理器', x: 500, y: 200, type: 'skill', status: 'pending', importance: 1.4, difficulty: 2.5, level: 2 },
            { id: 5, title: '嵌入式系统', x: 700, y: 150, type: 'skill', status: 'pending', importance: 1.5, difficulty: 3.0, level: 3 }
          ],
          edges: [
            { source: 1, target: 2, type: 'requires' },
            { source: 1, target: 3, type: 'requires' },
            { source: 2, target: 4, type: 'requires' },
            { source: 3, target: 4, type: 'requires' },
            { source: 4, target: 5, type: 'requires' }
          ],
          explanation: '基于您的电子工程专业背景，我们为您生成了这条从基础到高级的学习路径。路径包含了电子工程的核心概念和技能，重点培养电路分析和数字电子能力，帮助您系统性地掌握相关知识。',
          suggestions: [
            '建议每天学习1-2小时，保持学习的连贯性',
            '电路分析是电子工程的基础，要重点学习',
            '数字电子技术是现代电子系统的核心，要深入理解',
            '微处理器是嵌入式系统的基础，要掌握其工作原理',
            '嵌入式系统是电子工程的重要应用领域，建议多做实践项目'
          ]
        }
      }
      
      return defaultPaths[professionalGroup] || defaultPaths.computer_science
    },
    
    // 格式化学习偏好为字符串
    formatLearningPreferences() {
      if (!this.learningPreferences) return ''
      
      const preferences = []
      if (this.learningPreferences.style) preferences.push(`学习风格: ${this.learningPreferences.style}`)
      if (this.learningPreferences.pace) preferences.push(`学习节奏: ${this.learningPreferences.pace}`)
      if (this.learningPreferences.difficulty) preferences.push(`难度偏好: ${this.learningPreferences.difficulty}`)
      if (this.learningPreferences.dailyMinutes) preferences.push(`每日学习时间: ${this.learningPreferences.dailyMinutes}分钟`)
      if (this.learningPreferences.interests) preferences.push(`兴趣: ${this.learningPreferences.interests}`)
      
      return preferences.join(', ')
    },
    
    // 收集用户上下文信息
    collectUserContext() {
      // 模拟收集用户历史交互数据
      return {
        learningHistory: {
          completedConcepts: this.learnedConcepts || [],
          learningTime: this.userProfile?.total_learning_minutes || 0,
          practiceScore: this.userProfile?.avg_practice_score || 0
        },
        preferences: {
          learningStyle: this.userProfile?.learning_style || 'visual',
          preferredResources: [
            this.learningPreferences?.style || '',
            this.learningPreferences?.pace || '',
            this.learningPreferences?.difficulty || ''
          ].filter(Boolean)
        },
        currentContext: {
          page: 'learning-paths',
          timestamp: new Date().toISOString()
        }
      }
    },
    
    // 优化学习建议
    async optimizeSuggestions() {
      if (!this.smartPathData) return
      
      try {
        // 收集用户上下文
        const userContext = this.collectUserContext()
        
        // 生成优化建议的提示词
        const prompt = `基于用户的学习历史和当前学习路径，优化以下学习建议，使其更加个性化和具体：
        
        当前学习路径：
        ${this.smartPathData.nodes.map(node => `- ${node.title} (难度: ${node.difficulty}, 重要性: ${node.importance})`).join('\n')}
        
        用户信息：
        - 学习风格: ${this.userProfile?.learning_style || '视觉型'}
        - 知识水平: ${this.userProfile?.knowledge_level || '初级'}
        - 兴趣方向: ${this.userProfile?.interests?.join(', ') || '未设置'}
        - 已学概念: ${this.learnedConcepts?.join(', ') || '无'}
        
        请优化以下建议，使其：
        1. 更加个性化，符合用户的学习风格和知识水平
        2. 更加具体，提供可操作的学习方法和资源建议
        3. 与当前学习路径高度相关
        4. 包含清晰的推荐理由
        
        原始建议：
        ${this.smartPathData.suggestions?.join('\n') || '无'}
        
        请返回优化后的建议列表，每个建议一行。`
        
        // 调用AI助手API
        const aiResponse = await api.getAIAssistantResponse(prompt, true)
        
        // 解析AI响应，提取建议列表
        const optimizedSuggestions = aiResponse.answer
          .split('\n')
          .filter(line => line.trim())
          .map(line => line.trim())
        
        if (optimizedSuggestions.length > 0) {
          this.smartPathData.suggestions = optimizedSuggestions
        }
      } catch (error) {
        console.error('优化学习建议失败:', error)
        // 保持原始建议不变
      }
    },
    
    // 优化路径解释
    async optimizeExplanation() {
      if (!this.smartPathData) return
      
      try {
        // 收集用户上下文
        const userContext = this.collectUserContext()
        
        // 生成优化解释的提示词
        const prompt = `基于用户的学习历史和当前学习路径，优化以下路径解释，使其更加个性化和详细：
        
        当前学习路径：
        ${this.smartPathData.nodes.map(node => `- ${node.title} (难度: ${node.difficulty}, 重要性: ${node.importance})`).join('\n')}
        
        用户信息：
        - 学习目标: ${this.userProfile?.learning_goals || '未设置'}
        - 学习风格: ${this.userProfile?.learning_style || '视觉型'}
        - 知识水平: ${this.userProfile?.knowledge_level || '初级'}
        - 兴趣方向: ${this.userProfile?.interests?.join(', ') || '未设置'}
        - 已学概念: ${this.learnedConcepts?.join(', ') || '无'}
        
        请优化以下解释，使其：
        1. 更加个性化，符合用户的学习目标和兴趣
        2. 更加详细，解释为什么选择这些节点和顺序
        3. 更加具体，说明每个节点的学习价值和与用户目标的关联
        4. 包含清晰的学习路径设计理由
        
        原始解释：
        ${this.smartPathData.explanation || '无'}
        
        请返回优化后的解释文本。`
        
        // 调用AI助手API
        const aiResponse = await api.getAIAssistantResponse(prompt, true)
        
        // 更新解释
        if (aiResponse.answer && aiResponse.answer.trim()) {
          this.smartPathData.explanation = aiResponse.answer.trim()
        }
      } catch (error) {
        console.error('优化路径解释失败:', error)
        // 保持原始解释不变
      }
    },
    
    selectPathNode(node) {
      console.log('选择路径节点:', node)
    },
    
    formatExplanation(explanation) {
      if (!explanation) return ''
      
      // 去除杂乱符号和多余的空白
      let formatted = explanation
        .replace(/[\u0000-\u001F\u007F]/g, '') // 去除控制字符
        .replace(/\s+/g, ' ') // 合并多余空白
        .trim()
      
      // 处理换行
      formatted = formatted.replace(/\n/g, '<br>')
      
      // 处理列表项
      formatted = formatted.replace(/\*\s+(.*?)(?=\*\s+|$)/g, '<li>$1</li>')
      if (formatted.includes('<li>')) {
        formatted = `<ul>${formatted}</ul>`
      }
      
      return formatted
    },
    
    // 学习偏好相关方法
    openPreferenceDialog() {
      this.showPreferenceDialog = true
    },
    
    saveLearningPreferences() {
      // 模拟保存学习偏好
      alert('学习偏好已保存')
      this.showPreferenceDialog = false
    },
    
    // 个性化建议相关方法
    async refreshPersonalizedSuggestions() {
      this.generatingSuggestions = true
      try {
        // 模拟生成个性化建议
        this.personalizedSuggestions = [
          '建议多使用图表和可视化工具辅助学习',
          '建议每天固定时间学习，保持学习节奏',
          '推荐使用Python进行实践练习',
          '建议多做项目实践，巩固所学知识',
          '学习进度良好，继续保持！'
        ]
        
        this.suggestionCategories = {
          learning_method: ['建议多使用图表和可视化工具辅助学习'],
          time_management: ['建议每天固定时间学习，保持学习节奏'],
          resource_recommendation: ['推荐使用Python进行实践练习'],
          practice_suggestion: ['建议多做项目实践，巩固所学知识'],
          motivation: ['学习进度良好，继续保持！']
        }
      } catch (error) {
        console.error('生成个性化建议失败:', error)
      } finally {
        this.generatingSuggestions = false
      }
    },
    
    // 学习路径可视化相关方法
    toggleVisualizationType() {
      this.visualizationType = this.visualizationType === 'timeline' ? 'graph' : 'timeline'
    },
    
    loadKnowledgeGraphData() {
      // 模拟加载知识图谱数据
      this.knowledgeGraphNodes = [
        { id: 1, title: '人工智能', layer: 'concept', type: 'concept', difficulty: 4.5, mastery_level: 60 },
        { id: 2, title: '机器学习', layer: 'skill', type: 'skill', difficulty: 4.0, mastery_level: 50 },
        { id: 3, title: '深度学习', layer: 'skill', type: 'skill', difficulty: 4.5, mastery_level: 40 },
        { id: 4, title: 'Python编程', layer: 'skill', type: 'skill', difficulty: 3.0, mastery_level: 70 },
        { id: 5, title: '数据结构', layer: 'concept', type: 'concept', difficulty: 3.5, mastery_level: 65 },
        { id: 6, title: '算法', layer: 'concept', type: 'concept', difficulty: 4.0, mastery_level: 55 }
      ]
      
      this.knowledgeGraphRelations = [
        { source: 1, target: 2, type: 'includes' },
        { source: 2, target: 3, type: 'includes' },
        { source: 2, target: 4, type: 'requires' },
        { source: 2, target: 5, type: 'requires' },
        { source: 5, target: 6, type: 'includes' }
      ]
      
      this.calculateKnowledgeGraphStats()
    },
    
    calculateKnowledgeGraphStats() {
      this.knowledgeGraphStats = {
        totalNodes: this.knowledgeGraphNodes.length,
        totalRelations: this.knowledgeGraphRelations.length,
        layerDistribution: {
          concept: this.knowledgeGraphNodes.filter(n => n.layer === 'concept').length,
          skill: this.knowledgeGraphNodes.filter(n => n.layer === 'skill').length,
          professional: 0,
          resource: 0
        },
        relationTypeDistribution: {
          includes: this.knowledgeGraphRelations.filter(r => r.type === 'includes').length,
          requires: this.knowledgeGraphRelations.filter(r => r.type === 'requires').length
        },
        masteryLevelDistribution: {
          beginner: this.knowledgeGraphNodes.filter(n => n.mastery_level < 40).length,
          intermediate: this.knowledgeGraphNodes.filter(n => n.mastery_level >= 40 && n.mastery_level < 80).length,
          advanced: this.knowledgeGraphNodes.filter(n => n.mastery_level >= 80).length
        }
      }
    },
    
    toggleGraphLayout() {
      this.graphLayout = this.graphLayout === 'hierarchical' ? 'force' : 'hierarchical'
    },
    
    toggleKnowledgeGraphExplanation() {
      this.showKnowledgeGraphExplanation = !this.showKnowledgeGraphExplanation
      if (this.showKnowledgeGraphExplanation) {
        this.generateKnowledgeGraphExplanation()
      }
    },
    
    generateKnowledgeGraphExplanation() {
      this.generatingGraphExplanation = true
      // 模拟生成知识图谱解释
      setTimeout(() => {
        this.knowledgeGraphExplanation = '基于您的知识图谱分析，您已经掌握了Python编程的基础，建议重点加强机器学习和深度学习的学习。数据结构和算法是人工智能的基础，建议继续巩固。'
        this.generatingGraphExplanation = false
      }, 1000)
    },
    
    applyLayerFilter() {
      // 应用层级筛选
      console.log('应用层级筛选:', this.visibleLayers)
    },
    
    getLayerLabel(layer) {
      const labels = {
        concept: '概念层',
        professional: '专业融合层',
        skill: '技能层',
        resource: '资源层'
      }
      return labels[layer] || layer
    },
    
    getRelationTypeLabel(type) {
      const labels = {
        includes: '包含',
        requires: '前置',
        belongs_to: '属于',
        recommends: '推荐'
      }
      return labels[type] || type
    },
    
    // 学习路径状态判断方法
    isStageCompleted(stageId) {
      return false
    },
    
    isCurrentStage(stageId) {
      return false
    },
    
    isStageLocked(stageId) {
      return false
    },
    
    selectStage(stage) {
      console.log('选择阶段:', stage)
    },
    
    showStageDetail(stage) {
      console.log('查看阶段详情:', stage)
    },
    
    // 辅助方法
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
        science: '理工类',
        business: '经管类',
        humanities: '文史类',
        arts: '艺术类'
      }
      return texts[group] || '理工类'
    },
    
    // 获取专业相关的标题
    getProfessionalTitle(key) {
      const professionalGroup = this.userProfile?.professional_group || 'science'
      const titles = {
        science: {
          graph: '📊 理工类知识图谱',
          smartPath: '🚀 理工类智能学习路径',
          suggestions: '💡 理工类学习建议',
          recommendedPaths: '🎯 理工类推荐学习路径',
          visualization: '🗺️ 理工类学习路径可视化'
        },
        business: {
          graph: '📊 经管类知识图谱',
          smartPath: '🚀 经管类智能学习路径',
          suggestions: '💡 经管类学习建议',
          recommendedPaths: '🎯 经管类推荐学习路径',
          visualization: '🗺️ 经管类学习路径可视化'
        },
        humanities: {
          graph: '📊 文史类知识图谱',
          smartPath: '🚀 文史类智能学习路径',
          suggestions: '💡 文史类学习建议',
          recommendedPaths: '🎯 文史类推荐学习路径',
          visualization: '🗺️ 文史类学习路径可视化'
        },
        arts: {
          graph: '📊 艺术类知识图谱',
          smartPath: '🚀 艺术类智能学习路径',
          suggestions: '💡 艺术类学习建议',
          recommendedPaths: '🎯 艺术类推荐学习路径',
          visualization: '🗺️ 艺术类学习路径可视化'
        }
      }
      
      return titles[professionalGroup]?.[key] || titles.science[key]
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
    
    // 获取知识水平文本
    getKnowledgeLevelText(level) {
      const texts = {
        beginner: '初学者',
        intermediate: '中级',
        advanced: '高级'
      }
      return texts[level] || level
    },
    
    // 刷新所有数据
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
/* 标签页样式 */
.feature-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 10px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e8e8e8;
  background-color: #f5f5f5;
}

.tab-item:hover {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.tab-item.active {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  font-size: 14px;
  font-weight: 500;
}

/* 学习记录区域样式 */
.learning-records-section {
  width: 100%;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.combined-learning-path {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-left h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
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

.knowledge-graph-section,
.smart-path-section,
.learning-paths-section,
.learning-path-visualization {
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

.smart-path-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.smart-path-explanation {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  line-height: 1.6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.smart-path-explanation:hover {
  background: #f0f0f0;
}

.smart-path-explanation button {
  margin-top: 10px;
  font-size: 12px;
  padding: 4px 8px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.smart-path-explanation button:hover {
  background: #40a9ff;
}

.smart-path-visualization {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.path-svg {
  width: 100%;
  height: auto;
  display: block;
}

.path-edge {
  stroke: #999;
  stroke-width: 2;
  stroke-opacity: 0.6;
}

.path-node {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.path-node:hover {
  transform: scale(1.1);
}

.smart-path-suggestions {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.smart-path-suggestions:hover {
  background: #f0f0f0;
}

.smart-path-suggestions h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.smart-path-suggestions ul {
  margin: 0;
  padding-left: 20px;
  line-height: 1.6;
}

.smart-path-suggestions button {
  margin-top: 10px;
  font-size: 12px;
  padding: 4px 8px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.smart-path-suggestions button:hover {
  background: #40a9ff;
}

.no-path {
  text-align: center;
  padding: 60px 20px;
  color: #999;
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
  background: none;
  padding: 0;
  color: inherit;
  border-radius: 0;
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
.recommendations-card,
.personalized-suggestions-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-profile-card h3,
.active-paths-card h3,
.recommendations-card h3,
.personalized-suggestions-panel h3 {
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
.no-recommendations,
.no-suggestions {
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

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.suggestions-title-section h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.suggestions-subtitle {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.refresh-suggestions-btn {
  background: none;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-suggestions-btn:hover {
  background: #f5f5f5;
}

.loading-container-small {
  text-align: center;
  padding: 30px 10px;
}

.loading-spinner-small {
  width: 30px;
  height: 30px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

.suggestions-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.suggestion-category {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  background: #fafafa;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.category-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.category-icon {
  font-size: 16px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  line-height: 1.5;
}

.suggestion-icon {
  font-size: 14px;
  margin-top: 2px;
}

.suggestion-content {
  flex: 1;
  color: #666;
}

.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.visualization-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.visualization-controls {
  display: flex;
  gap: 10px;
}

.visualization-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.timeline-view {
  overflow-x: auto;
}

.timeline-wrapper {
  min-width: 600px;
}

.timeline {
  position: relative;
  padding-left: 40px;
}

.timeline-node {
  position: relative;
  margin-bottom: 30px;
}

.timeline-node::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 20px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1890ff;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #1890ff;
}

.timeline-node.completed::before {
  background: #52c41a;
  box-shadow: 0 0 0 2px #52c41a;
}

.timeline-node.locked::before {
  background: #999;
  box-shadow: 0 0 0 2px #999;
}

.timeline-node-content {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.timeline-node-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.timeline-node-number {
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
  margin-right: 15px;
  min-width: 30px;
}

.timeline-node-main {
  flex: 1;
}

.timeline-node-main h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.timeline-node-description {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.timeline-node-status {
  min-width: 100px;
  text-align: right;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background: #f6ffed;
  color: #52c41a;
}

.status-current {
  background: #e6f7ff;
  color: #1890ff;
}

.status-locked {
  background: #f5f5f5;
  color: #999;
}

.status-pending {
  background: #fff7e6;
  color: #fa8c16;
}

.timeline-node-details {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.timeline-node-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  font-size: 13px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.meta-icon {
  font-size: 14px;
}

.learning-goals-preview {
  margin-bottom: 15px;
}

.goals-label {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.goals-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.goal-tag {
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.goal-tag.more {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: 500;
}

.timeline-node-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: #1890ff;
  color: white;
}

.action-btn.secondary {
  background: #f5f5f5;
  color: #333;
}

.timeline-connector {
  position: absolute;
  left: -14px;
  top: 32px;
  bottom: -30px;
  width: 2px;
  background: #e8e8e8;
}

.timeline-connector::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: -4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e8e8e8;
}

.timeline-connector.completed {
  background: #52c41a;
}

.timeline-connector.completed::after {
  background: #52c41a;
}

.timeline-connector.current {
  background: #1890ff;
}

.timeline-connector.current::after {
  background: #1890ff;
}

.connector-line {
  flex: 1;
  height: 2px;
  background: #e8e8e8;
}

.connector-arrow {
  font-size: 12px;
  color: #999;
  margin-left: 5px;
}

.graph-view {
  min-height: 400px;
}

.graph-placeholder {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.graph-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.graph-hint {
  font-size: 14px;
  margin-top: 10px;
  opacity: 0.8;
}

.knowledge-graph-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.graph-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.layer-filter {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.form-select {
  padding: 4px 8px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 12px;
}

.btn-xs {
  padding: 2px 8px;
  font-size: 11px;
}

.knowledge-graph-stats-panel {
  background: white;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e8e8e8;
}

.knowledge-graph-stats-panel h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.stats-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stats-overview {
  display: flex;
  gap: 20px;
}

.stats-overview .stat-item {
  flex: 1;
  text-align: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.stats-overview .stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stats-overview .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.stats-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.distribution-label {
  width: 100px;
  font-size: 12px;
  color: #666;
}

.distribution-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.distribution-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: #e8e8e8;
}

.distribution-bar.beginner {
  background: #ff4d4f;
}

.distribution-bar.intermediate {
  background: #faad14;
}

.distribution-bar.advanced {
  background: #52c41a;
}

.distribution-bar.layer-concept {
  background: #1890ff;
}

.distribution-bar.layer-skill {
  background: #52c41a;
}

.distribution-bar.layer-professional {
  background: #faad14;
}

.distribution-bar.layer-resource {
  background: #722ed1;
}

.distribution-bar.relation-includes {
  background: #1890ff;
}

.distribution-bar.relation-requires {
  background: #52c41a;
}

.distribution-count {
  font-size: 12px;
  color: #999;
  min-width: 30px;
  text-align: right;
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

.generating-status {
  text-align: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.personalized-path-result {
  margin-top: 20px;
}

.personalized-path-result h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.path-explanation {
  margin-bottom: 15px;
  line-height: 1.6;
  color: #666;
}

.path-suggestions h5 {
  margin: 0 0 10px 0;
  color: #333;
}

.path-suggestions ul {
  margin: 0;
  padding-left: 20px;
  line-height: 1.6;
  color: #666;
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
  .path-header {
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
  
  .stats-overview {
    flex-direction: column;
    gap: 10px;
  }
  
  .timeline-wrapper {
    min-width: 100%;
  }
  
  .timeline {
    padding-left: 30px;
  }
  
  .timeline-node::before {
    left: -15px;
  }
  
  .timeline-connector {
    left: -9px;
  }
}
</style>