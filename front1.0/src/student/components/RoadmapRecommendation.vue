<template>
  <div class="roadmap-recommendation">
    <div class="section-header">
      <h3>推荐学习路线</h3>
      <router-link :to="'/learning-paths?major=' + currentMajor" class="view-more">
        查看全部 →
      </router-link>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="roadmaps.length === 0" class="empty">
      <p>暂无推荐的学习路线</p>
    </div>
    
    <div v-else class="roadmap-cards">
      <div
        v-for="roadmap in roadmaps"
        :key="roadmap.id"
        class="roadmap-card"
        @click="goToRoadmapDetail(roadmap.id)"
      >
        <div class="roadmap-header">
          <h4>{{ roadmap.title }}</h4>
          <span class="difficulty" :class="roadmap.difficulty_level">
            {{ getDifficultyText(roadmap.difficulty_level) }}
          </span>
        </div>
        <!-- 学习路线图SVG可视化 -->
        <div class="roadmap-svg-container">
          <svg :viewBox="roadmap.svg.viewBox" class="roadmap-svg">
            <template v-if="roadmap.svg.background">
              <rect
                x="0"
                y="0"
                width="100%"
                height="100%"
                :fill="roadmap.svg.background.fill"
                :rx="roadmap.svg.background.rx || 0"
              />
            </template>
            <!-- 路径线 -->
            <path
              v-for="(path, index) in roadmap.svg.paths"
              :key="`path-${index}`"
              :d="path.d"
              :stroke="path.stroke"
              :stroke-width="path.strokeWidth || 2"
              :fill="path.fill || 'none'"
              :stroke-dasharray="path.strokeDasharray || ''"
            />
            <!-- 节点 -->
            <g
              v-for="(node, index) in roadmap.svg.nodes"
              :key="`node-${index}`"
              :transform="`translate(${node.x}, ${node.y})`"
            >
              <circle
                  :r="node.r || 10"
                  :fill="node.fill"
                  :stroke="node.stroke || 'none'"
                  :stroke-width="node.strokeWidth || 1"
                />
              <text
                x="0"
                y="0"
                text-anchor="middle"
                dominant-baseline="middle"
                :fill="node.textFill || '#fff'"
                :font-size="node.textSize || '12px'"
              >
                {{ node.text }}
              </text>
            </g>
          </svg>
        </div>
        <p class="roadmap-description">{{ roadmap.description }}</p>
        <div class="roadmap-meta">
          <span class="meta-item">
            <i class="el-icon-time"></i>
            {{ roadmap.estimated_hours }} 小时
          </span>
          <span class="meta-item">
            <i class="el-icon-document"></i>
            {{ roadmap.stages.length }} 个阶段
          </span>
          <span class="meta-item">
            <i class="el-icon-book"></i>
            {{ getTotalBooks(roadmap) }} 本教材
          </span>
        </div>
        <div class="tags">
          <span v-for="tag in roadmap.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
          <span v-if="roadmap.tags.length > 3" class="tag more">+{{ roadmap.tags.length - 3 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 导入API模块
import { api } from '../api/api.js'

export default {
  name: 'RoadmapRecommendation',
  props: {
    major: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      roadmaps: [],
      loading: false,
      currentMajor: this.major
    }
  },
  watch: {
    major: function(newVal) {
      this.currentMajor = newVal
      this.loadRecommendedRoadmaps()
    }
  },
  mounted() {
    this.loadRecommendedRoadmaps()
  },
  methods: {
    // 从后端API获取推荐的学习路线
    async loadRecommendedRoadmaps() {
      this.loading = true
      try {
        // 调用后端API获取基于知识图谱和大模型生成的学习路线
        const response = await api.getRecommendedRoadmaps({
          major: this.currentMajor
        })
        
        // 如果API返回数据，则使用API数据，否则使用空数组
        this.roadmaps = response.roadmaps || []
        console.log(`Loaded recommended roadmaps for major: ${this.currentMajor}`, this.roadmaps)
      } catch (error) {
        console.error('Failed to load recommended roadmaps:', error)
        // 出错时使用空数组，避免显示静态数据
        this.roadmaps = []
      } finally {
        this.loading = false
      }
    },
    getDifficultyText(difficulty) {
      const difficultyMap = {
        'beginner': '入门',
        'intermediate': '进阶',
        'advanced': '高级'
      }
      return difficultyMap[difficulty] || difficulty
    },
    getTotalBooks(roadmap) {
      return roadmap.stages.reduce((total, stage) => total + (stage.books ? stage.books.length : 0), 0)
    },
    goToRoadmapDetail(roadmapId) {
      // 跳转到学习路线详情页
      this.$router.push(`/learning-paths?roadmap=${roadmapId}&major=${this.currentMajor}`)
    }
  }
}
</script>

<style scoped>
.roadmap-recommendation {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.view-more {
  color: #1890ff;
  font-size: 14px;
  text-decoration: none;
}

.view-more:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error,
.empty {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.btn-primary {
  padding: 6px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.roadmap-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.roadmap-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
  position: relative;
}

.roadmap-svg-container {
  margin: 12px 0;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.roadmap-svg {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.roadmap-card:hover .roadmap-svg {
  transform: scale(1.05);
}

.roadmap-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #1890ff;
}

.roadmap-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.roadmap-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
  flex: 1;
  margin-right: 10px;
}

.difficulty {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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

.roadmap-description {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.roadmap-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item i {
  font-size: 14px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background-color: #f0f0f0;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.tag.more {
  background-color: #e6f7ff;
  color: #1890ff;
}

@media (max-width: 768px) {
  .roadmap-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .roadmap-meta {
    gap: 10px;
    flex-wrap: wrap;
  }
}
</style>