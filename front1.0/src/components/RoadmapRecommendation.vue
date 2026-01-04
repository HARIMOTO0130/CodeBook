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
      currentMajor: this.major,
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
            tags: ['Excel高级', '数据分析', '办公自动化'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#f6ffed', rx: 8 },
              paths: [
                { d: 'M50,75 L100,75 L150,75 L200,75 L250,75', stroke: '#52c41a', strokeWidth: 3 }
              ],
              nodes: [
                { x: 50, y: 75, r: 15, fill: '#52c41a', text: '1' },
                { x: 100, y: 75, r: 15, fill: '#52c41a', text: '2' },
                { x: 150, y: 75, r: 15, fill: '#52c41a', text: '3' },
                { x: 200, y: 75, r: 15, fill: '#52c41a', text: '4' },
                { x: 250, y: 75, r: 15, fill: '#52c41a', text: '5' }
              ]
            }
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
            tags: ['电子商务', '网络营销', '数据分析'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#e6f7ff', rx: 8 },
              paths: [
                { d: 'M50,100 L100,50 L150,100 L200,50 L250,100', stroke: '#1890ff', strokeWidth: 3 }
              ],
              nodes: [
                { x: 50, y: 100, r: 15, fill: '#1890ff', text: '1' },
                { x: 100, y: 50, r: 15, fill: '#1890ff', text: '2' },
                { x: 150, y: 100, r: 15, fill: '#1890ff', text: '3' },
                { x: 200, y: 50, r: 15, fill: '#1890ff', text: '4' },
                { x: 250, y: 100, r: 15, fill: '#1890ff', text: '5' }
              ]
            }
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
            tags: ['信息检索', '文献管理', '数字人文'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#fff7e6', rx: 8 },
              paths: [
                { d: 'M50,40 L150,40 L150,110 L250,110', stroke: '#fa8c16', strokeWidth: 3 }
              ],
              nodes: [
                { x: 50, y: 40, r: 15, fill: '#fa8c16', text: '1' },
                { x: 150, y: 40, r: 15, fill: '#fa8c16', text: '2' },
                { x: 150, y: 110, r: 15, fill: '#fa8c16', text: '3' },
                { x: 250, y: 110, r: 15, fill: '#fa8c16', text: '4' }
              ]
            }
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
            tags: ['数字写作', '多媒体', '内容创作'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#f9f0ff', rx: 8 },
              paths: [
                { d: 'M50,75 L150,30 L150,120 L250,75', stroke: '#722ed1', strokeWidth: 3 }
              ],
              nodes: [
                { x: 50, y: 75, r: 15, fill: '#722ed1', text: '1' },
                { x: 150, y: 30, r: 15, fill: '#722ed1', text: '2' },
                { x: 150, y: 120, r: 15, fill: '#722ed1', text: '3' },
                { x: 250, y: 75, r: 15, fill: '#722ed1', text: '4' }
              ]
            }
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
            tags: ['Photoshop', '数字设计', '创意软件'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#fff2e8', rx: 8 },
              paths: [
                { d: 'M50,100 C100,30 200,30 250,100', stroke: '#fa541c', strokeWidth: 3, fill: 'none' }
              ],
              nodes: [
                { x: 50, y: 100, r: 15, fill: '#fa541c', text: '1' },
                { x: 100, y: 50, r: 15, fill: '#fa541c', text: '2' },
                { x: 200, y: 50, r: 15, fill: '#fa541c', text: '3' },
                { x: 250, y: 100, r: 15, fill: '#fa541c', text: '4' }
              ]
            }
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
            tags: ['UI设计', '数字排版', '互动媒体'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#f0f5ff', rx: 8 },
              paths: [
                { d: 'M50,50 L50,100 L125,100 L125,50 L200,50 L200,100 L275,100', stroke: '#40a9ff', strokeWidth: 3 }
              ],
              nodes: [
                { x: 50, y: 50, r: 15, fill: '#40a9ff', text: '1' },
                { x: 50, y: 100, r: 15, fill: '#40a9ff', text: '2' },
                { x: 125, y: 100, r: 15, fill: '#40a9ff', text: '3' },
                { x: 125, y: 50, r: 15, fill: '#40a9ff', text: '4' },
                { x: 200, y: 50, r: 15, fill: '#40a9ff', text: '5' },
                { x: 200, y: 100, r: 15, fill: '#40a9ff', text: '6' }
              ]
            }
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
            tags: ['Python', '编程入门', '实用技能'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#f0fdf4', rx: 8 },
              paths: [
                { d: 'M50,75 L100,75 L150,30 L150,120 L200,75 L250,75', stroke: '#22c55e', strokeWidth: 3 }
              ],
              nodes: [
                { x: 50, y: 75, r: 15, fill: '#22c55e', text: '1' },
                { x: 100, y: 75, r: 15, fill: '#22c55e', text: '2' },
                { x: 150, y: 30, r: 15, fill: '#22c55e', text: '3' },
                { x: 150, y: 120, r: 15, fill: '#22c55e', text: '4' },
                { x: 200, y: 75, r: 15, fill: '#22c55e', text: '5' },
                { x: 250, y: 75, r: 15, fill: '#22c55e', text: '6' }
              ]
            }
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
            tags: ['数据科学', '数据可视化', 'Python应用'],
            svg: {
              viewBox: '0 0 300 150',
              background: { fill: '#f0f9ff', rx: 8 },
              paths: [
                { d: 'M75,30 L150,30 L150,90 L225,90 L225,120', stroke: '#06b6d4', strokeWidth: 3 }
              ],
              nodes: [
                { x: 75, y: 30, r: 15, fill: '#06b6d4', text: '1' },
                { x: 150, y: 30, r: 15, fill: '#06b6d4', text: '2' },
                { x: 150, y: 90, r: 15, fill: '#06b6d4', text: '3' },
                { x: 225, y: 90, r: 15, fill: '#06b6d4', text: '4' },
                { x: 225, y: 120, r: 15, fill: '#06b6d4', text: '5' }
              ]
            }
          }
        ]
      }
    }
  },
  watch: {
    major: function(newVal) {
      this.currentMajor = newVal
      this.loadStaticRoadmaps()
    }
  },
  mounted() {
    this.loadStaticRoadmaps()
  },
  methods: {
    loadStaticRoadmaps() {
      this.loading = true
      
      // 使用setTimeout模拟异步加载
      setTimeout(() => {
        // 获取当前专业的静态路线图数据，如果没有则使用默认数据
        this.roadmaps = this.staticRoadmaps[this.currentMajor] || 
                        this.staticRoadmaps.business || 
                        []
        this.loading = false
        console.log(`Loaded static roadmaps for major: ${this.currentMajor}`, this.roadmaps)
      }, 300)
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
      // 可以根据需要实现详情页跳转逻辑
      console.log('Navigate to roadmap detail:', roadmapId)
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