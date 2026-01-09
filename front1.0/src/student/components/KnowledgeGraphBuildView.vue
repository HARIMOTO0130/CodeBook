<template>
  <div class="knowledge-graph-build-view">
    <h2>🔨 知识图谱构建过程可视化</h2>
    
    <!-- 构建步骤导航 -->
    <div class="build-steps-navigation">
      <div 
        v-for="step in buildSteps" 
        :key="step.id"
        class="step-nav-item"
        :class="{ active: currentStep === step.id }"
        @click="goToStep(step.id)"
      >
        <div class="step-number">{{ step.id }}</div>
        <div class="step-title">{{ step.title }}</div>
      </div>
    </div>
    
    <!-- 构建进度条 -->
    <div class="build-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="progress-text">{{ progress }}% 完成</div>
    </div>
    
    <!-- 构建过程可视化区域 -->
    <div class="build-visualization-container">
      <!-- 步骤1：知识点提取 -->
      <div v-if="currentStep === 1" class="step-content">
        <h3>1. 知识点提取</h3>
        <div class="step-description">
          <p>从教材内容中提取知识点，使用NLP技术和大模型进行分类和标注</p>
        </div>
        <div class="extraction-visualization">
          <div class="source-content">
            <h4>📚 教材内容</h4>
            <div class="content-text">
              <p>{{ sourceContent }}</p>
            </div>
          </div>
          <div class="extracted-knowledge-points">
            <h4>🔍 提取的知识点</h4>
            <div class="knowledge-points-list">
              <div 
                v-for="(point, index) in extractedKnowledgePoints" 
                :key="index"
                class="knowledge-point-item"
                :class="{ animated: animationStep > index }"
              >
                <div class="point-icon">📌</div>
                <div class="point-content">
                  <div class="point-title">{{ point.title }}</div>
                  <div class="point-type">{{ point.type }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn-primary" @click="startExtractionAnimation">开始提取动画</button>
          <button class="btn-secondary" @click="nextStep">下一步</button>
        </div>
      </div>
      
      <!-- 步骤2：关系识别 -->
      <div v-if="currentStep === 2" class="step-content">
        <h3>2. 关系识别</h3>
        <div class="step-description">
          <p>识别知识点之间的关系，包括规则匹配、大模型推断和上下文分析</p>
        </div>
        <div class="relation-recognition-visualization">
          <div class="graph-container">
            <svg class="relation-graph" :viewBox="`0 0 800 600`">
              <!-- 绘制知识点节点 -->
              <g class="knowledge-nodes">
                <g
                  v-for="(node, index) in extractedKnowledgePoints"
                  :key="index"
                  :transform="`translate(${node.x || 100 + index * 150}, ${node.y || 300})`"
                  class="knowledge-node"
                >
                  <circle r="40" fill="#1890ff" stroke="#fff" stroke-width="2" />
                  <text x="0" y="0" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-size="14">
                    {{ node.title.length > 8 ? node.title.substring(0, 8) + '...' : node.title }}
                  </text>
                </g>
              </g>
              <!-- 绘制关系线 -->
              <g class="relation-edges">
                <g
                  v-for="(relation, index) in identifiedRelations"
                  :key="index"
                  class="relation-edge"
                  :class="{ animated: animationStep > index }"
                >
                  <line
                    :x1="getRelationNodePosition(relation.source).x"
                    :y1="getRelationNodePosition(relation.source).y"
                    :x2="getRelationNodePosition(relation.target).x"
                    :y2="getRelationNodePosition(relation.target).y"
                    :stroke="getRelationColor(relation.type)"
                    :stroke-width="2"
                    :opacity="0.8"
                  />
                  <text
                    :x="(getRelationNodePosition(relation.source).x + getRelationNodePosition(relation.target).x) / 2"
                    :y="(getRelationNodePosition(relation.source).y + getRelationNodePosition(relation.target).y) / 2 - 10"
                    text-anchor="middle"
                    fill="#333"
                    font-size="12"
                    font-weight="bold"
                  >
                    {{ relation.type }}
                  </text>
                </g>
              </g>
            </svg>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn-primary" @click="startRelationAnimation">开始关系识别动画</button>
          <button class="btn-secondary" @click="previousStep">上一步</button>
          <button class="btn-primary" @click="nextStep">下一步</button>
        </div>
      </div>
      
      <!-- 步骤3：关系强度计算 -->
      <div v-if="currentStep === 3" class="step-content">
        <h3>3. 关系强度计算</h3>
        <div class="step-description">
          <p>计算知识点之间的关系强度，包括结构强度、语义强度和行为强度</p>
        </div>
        <div class="strength-calculation-visualization">
          <div class="strength-formula">
            <h4>📐 关系强度计算公式</h4>
            <div class="formula-text">
              关系强度 = α×结构强度 + β×语义强度 + γ×行为强度
            </div>
            <div class="formula-params">
              <div class="param-item">
                <span class="param-name">α</span>
                <span class="param-description">结构强度权重 (0.4)</span>
              </div>
              <div class="param-item">
                <span class="param-name">β</span>
                <span class="param-description">语义强度权重 (0.3)</span>
              </div>
              <div class="param-item">
                <span class="param-name">γ</span>
                <span class="param-description">行为强度权重 (0.3)</span>
              </div>
            </div>
          </div>
          <div class="strength-visualization">
            <h4>💪 关系强度可视化</h4>
            <div class="graph-container">
              <svg class="strength-graph" :viewBox="`0 0 800 600`">
                <!-- 绘制知识点节点 -->
                <g class="knowledge-nodes">
                  <g
                    v-for="(node, index) in extractedKnowledgePoints"
                    :key="index"
                    :transform="`translate(${node.x || 100 + index * 150}, ${node.y || 300})`"
                    class="knowledge-node"
                  >
                    <circle r="40" fill="#1890ff" stroke="#fff" stroke-width="2" />
                    <text x="0" y="0" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-size="14">
                      {{ node.title.length > 8 ? node.title.substring(0, 8) + '...' : node.title }}
                    </text>
                  </g>
                </g>
                <!-- 绘制关系线（根据强度调整粗细） -->
                <g class="relation-edges">
                  <line
                    v-for="(relation, index) in identifiedRelations"
                    :key="index"
                    :x1="getRelationNodePosition(relation.source).x"
                    :y1="getRelationNodePosition(relation.source).y"
                    :x2="getRelationNodePosition(relation.target).x"
                    :y2="getRelationNodePosition(relation.target).y"
                    :stroke="getRelationColor(relation.type)"
                    :stroke-width="relation.strength * 3"
                    :opacity="0.8"
                  />
                  <text
                    v-for="(relation, index) in identifiedRelations"
                    :key="index"
                    :x="(getRelationNodePosition(relation.source).x + getRelationNodePosition(relation.target).x) / 2"
                    :y="(getRelationNodePosition(relation.source).y + getRelationNodePosition(relation.target).y) / 2 - 10"
                    text-anchor="middle"
                    fill="#333"
                    font-size="12"
                    font-weight="bold"
                  >
                    {{ relation.strength.toFixed(2) }}
                  </text>
                </g>
              </svg>
            </div>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn-primary" @click="calculateStrengths">计算关系强度</button>
          <button class="btn-secondary" @click="previousStep">上一步</button>
          <button class="btn-primary" @click="nextStep">下一步</button>
        </div>
      </div>
      
      <!-- 步骤4：知识节点嵌入生成 -->
      <div v-if="currentStep === 4" class="step-content">
        <h3>4. 知识节点嵌入生成</h3>
        <div class="step-description">
          <p>使用图神经网络（GNN）学习节点表示，融合多模态信息生成专业组特异性嵌入</p>
        </div>
        <div class="embedding-visualization">
          <div class="embedding-model">
            <h4>🧠 图神经网络模型</h4>
            <div class="model-diagram">
              <div class="model-layer input-layer">输入层</div>
              <div class="model-layer hidden-layer">隐藏层1</div>
              <div class="model-layer hidden-layer">隐藏层2</div>
              <div class="model-layer output-layer">输出层</div>
              <div class="model-connections">
                <div class="connection-line"></div>
                <div class="connection-line"></div>
                <div class="connection-line"></div>
              </div>
            </div>
          </div>
          <div class="embedding-result">
            <h4>📊 节点嵌入结果</h4>
            <div class="embedding-space">
              <svg class="embedding-graph" :viewBox="`0 0 800 600`">
                <!-- 绘制嵌入空间坐标轴 -->
                <line x1="100" y1="500" x2="700" y2="500" stroke="#333" stroke-width="2" />
                <line x1="100" y1="500" x2="100" y2="100" stroke="#333" stroke-width="2" />
                <text x="720" y="510" fill="#333" font-size="14">维度1</text>
                <text x="80" y="80" fill="#333" font-size="14">维度2</text>
                
                <!-- 绘制节点嵌入 -->
                <g class="embedding-nodes">
                  <circle
                    v-for="(node, index) in embeddedNodes"
                    :key="index"
                    :cx="node.embedding[0]"
                    :cy="node.embedding[1]"
                    r="15"
                    :fill="getNodeColorByType(node.type)"
                    stroke="#fff"
                    stroke-width="2"
                  />
                  <text
                    v-for="(node, index) in embeddedNodes"
                    :key="index"
                    :x="node.embedding[0]"
                    :y="node.embedding[1]"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    fill="#fff"
                    font-size="12"
                    font-weight="bold"
                  >
                    {{ node.title.substring(0, 2) }}
                  </text>
                </g>
              </svg>
            </div>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn-primary" @click="generateEmbeddings">生成节点嵌入</button>
          <button class="btn-secondary" @click="previousStep">上一步</button>
          <button class="btn-success" @click="completeBuild">完成构建</button>
        </div>
      </div>
      
      <!-- 构建完成 -->
      <div v-if="currentStep === 5" class="step-content">
        <h3>✅ 知识图谱构建完成</h3>
        <div class="build-complete">
          <div class="complete-icon">🎉</div>
          <h4>知识图谱构建成功！</h4>
          <p>知识图谱已成功构建完成，包含 {{ extractedKnowledgePoints.length }} 个知识点和 {{ identifiedRelations.length }} 条关系。</p>
          <div class="complete-stats">
            <div class="stat-item">
              <div class="stat-label">知识点数量</div>
              <div class="stat-value">{{ extractedKnowledgePoints.length }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">关系数量</div>
              <div class="stat-value">{{ identifiedRelations.length }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">构建时间</div>
              <div class="stat-value">{{ buildTime }} 秒</div>
            </div>
          </div>
          <div class="complete-actions">
            <button class="btn-primary" @click="goToStep(1)">重新查看构建过程</button>
            <button class="btn-success" @click="viewKnowledgeGraph">查看生成的知识图谱</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KnowledgeGraphBuildView',
  data() {
    return {
      currentStep: 1,
      buildSteps: [
        { id: 1, title: '知识点提取' },
        { id: 2, title: '关系识别' },
        { id: 3, title: '关系强度计算' },
        { id: 4, title: '节点嵌入生成' },
        { id: 5, title: '构建完成' }
      ],
      progress: 0,
      // 构建数据
      sourceContent: '机器学习是人工智能的一个分支，它允许计算机从数据中学习而不需要明确的编程。深度学习是机器学习的一个子集，它使用人工神经网络来模拟人类大脑的工作方式。神经网络是由多层神经元组成的，每一层都从前一层接收输入并产生输出。',
      extractedKnowledgePoints: [
        { id: 1, title: '机器学习', type: '概念', x: 150, y: 200 },
        { id: 2, title: '人工智能', type: '概念', x: 350, y: 150 },
        { id: 3, title: '深度学习', type: '概念', x: 550, y: 200 },
        { id: 4, title: '人工神经网络', type: '概念', x: 350, y: 350 }
      ],
      identifiedRelations: [
        { source: 1, target: 2, type: 'prerequisite', strength: 0 },
        { source: 3, target: 1, type: 'prerequisite', strength: 0 },
        { source: 3, target: 4, type: 'related', strength: 0 }
      ],
      embeddedNodes: [],
      // 动画相关
      animationStep: 0,
      buildTime: 0,
      startTime: 0
    };
  },
  mounted() {
    this.startTime = Date.now();
  },
  methods: {
    // 步骤导航
    goToStep(stepId) {
      this.currentStep = stepId;
      this.updateProgress();
    },
    nextStep() {
      if (this.currentStep < this.buildSteps.length) {
        this.currentStep++;
        this.updateProgress();
      }
    },
    previousStep() {
      if (this.currentStep > 1) {
        this.currentStep--;
        this.updateProgress();
      }
    },
    updateProgress() {
      this.progress = ((this.currentStep - 1) / (this.buildSteps.length - 1)) * 100;
    },
    
    // 步骤1：知识点提取动画
    startExtractionAnimation() {
      this.animationStep = 0;
      const timer = setInterval(() => {
        this.animationStep++;
        if (this.animationStep >= this.extractedKnowledgePoints.length) {
          clearInterval(timer);
        }
      }, 500);
    },
    
    // 步骤2：关系识别动画
    startRelationAnimation() {
      this.animationStep = 0;
      const timer = setInterval(() => {
        this.animationStep++;
        if (this.animationStep >= this.identifiedRelations.length) {
          clearInterval(timer);
        }
      }, 800);
    },
    
    // 获取关系节点位置
    getRelationNodePosition(nodeId) {
      const node = this.extractedKnowledgePoints.find(n => n.id === nodeId);
      return node ? { x: node.x, y: node.y } : { x: 0, y: 0 };
    },
    
    // 获取关系颜色
    getRelationColor(type) {
      const colorMap = {
        prerequisite: '#1890ff',
        related: '#52c41a',
        resource: '#faad14',
        recommend: '#722ed1'
      };
      return colorMap[type] || '#8c8c8c';
    },
    
    // 步骤3：计算关系强度
    calculateStrengths() {
      this.identifiedRelations.forEach(relation => {
        // 模拟计算关系强度
        const structuralStrength = Math.random() * 0.4;
        const semanticStrength = Math.random() * 0.3;
        const behavioralStrength = Math.random() * 0.3;
        relation.strength = structuralStrength + semanticStrength + behavioralStrength;
      });
    },
    
    // 步骤4：生成节点嵌入
    generateEmbeddings() {
      this.embeddedNodes = this.extractedKnowledgePoints.map((node, index) => {
        // 模拟生成嵌入向量
        return {
          ...node,
          embedding: [
            100 + Math.random() * 600, // 维度1
            100 + Math.random() * 400  // 维度2
          ]
        };
      });
    },
    
    // 根据节点类型获取颜色
    getNodeColorByType(type) {
      const colorMap = {
        concept: '#1890ff',
        skill: '#52c41a',
        professional: '#faad14',
        resource: '#722ed1'
      };
      return colorMap[type] || '#8c8c8c';
    },
    
    // 完成构建
    completeBuild() {
      this.buildTime = Math.round((Date.now() - this.startTime) / 1000);
      this.nextStep();
    },
    
    // 查看生成的知识图谱
    viewKnowledgeGraph() {
      // 跳转到知识图谱视图
      this.$router.push('/learning-path');
    }
  }
};
</script>

<style scoped>
.knowledge-graph-build-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

/* 步骤导航 */
.build-steps-navigation {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 8px;
}

.step-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.step-nav-item.active {
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: bold;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #d9d9d9;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 5px;
  transition: all 0.3s ease;
}

.step-nav-item.active .step-number {
  background-color: #1890ff;
  color: #fff;
}

.step-title {
  font-size: 14px;
  text-align: center;
}

/* 进度条 */
.build-progress {
  margin-bottom: 30px;
}

.progress-bar {
  height: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #1890ff;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  margin-top: 5px;
  font-size: 14px;
  color: #666;
}

/* 构建内容区域 */
.build-visualization-container {
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  min-height: 500px;
}

.step-content {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-content h3 {
  color: #333;
  margin-bottom: 15px;
}

.step-description {
  background-color: #fafafa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #1890ff;
}

/* 步骤1：知识点提取 */
.extraction-visualization {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.source-content, .extracted-knowledge-points {
  flex: 1;
  background-color: #fafafa;
  padding: 15px;
  border-radius: 8px;
}

.source-content h4, .extracted-knowledge-points h4 {
  color: #333;
  margin-bottom: 10px;
}

.content-text {
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  max-height: 200px;
  overflow-y: auto;
}

.knowledge-points-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.knowledge-point-item {
  display: flex;
  align-items: center;
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  opacity: 0;
  transform: translateX(-20px);
  transition: all 0.5s ease;
}

.knowledge-point-item.animated {
  opacity: 1;
  transform: translateX(0);
}

.point-icon {
  font-size: 20px;
  margin-right: 10px;
}

.point-content {
  flex: 1;
}

.point-title {
  font-weight: bold;
  color: #333;
}

.point-type {
  font-size: 12px;
  color: #666;
}

/* 步骤2和3：关系可视化 */
.graph-container {
  width: 100%;
  height: 400px;
  background-color: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  margin: 20px 0;
}

.relation-graph, .strength-graph {
  width: 100%;
  height: 100%;
}

.relation-edge {
  opacity: 0;
  transition: opacity 0.5s ease;
}

.relation-edge.animated {
  opacity: 1;
}

/* 步骤3：关系强度计算 */
.strength-calculation-visualization {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.strength-formula, .strength-visualization {
  flex: 1;
}

.strength-formula h4, .strength-visualization h4 {
  color: #333;
  margin-bottom: 15px;
}

.formula-text {
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 15px;
  text-align: center;
}

.formula-params {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.param-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.param-name {
  font-weight: bold;
  font-size: 20px;
  color: #1890ff;
}

.param-description {
  font-size: 12px;
  color: #666;
}

/* 步骤4：节点嵌入 */
.embedding-visualization {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.embedding-model, .embedding-result {
  flex: 1;
}

.embedding-model h4, .embedding-result h4 {
  color: #333;
  margin-bottom: 15px;
}

.model-diagram {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  background-color: #fafafa;
  padding: 20px;
  border-radius: 8px;
  position: relative;
}

.model-layer {
  width: 100px;
  padding: 10px;
  text-align: center;
  border-radius: 4px;
  color: #fff;
  font-weight: bold;
}

.input-layer {
  background-color: #1890ff;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hidden-layer {
  background-color: #52c41a;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.output-layer {
  background-color: #faad14;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.connection-line {
  position: absolute;
  height: 2px;
  background-color: #d9d9d9;
  top: 50%;
  transform: translateY(-50%);
}

.connection-line:nth-child(1) {
  left: 150px;
  right: 450px;
}

.connection-line:nth-child(2) {
  left: 350px;
  right: 250px;
}

.connection-line:nth-child(3) {
  left: 550px;
  right: 50px;
}

.embedding-space {
  width: 100%;
  height: 300px;
  background-color: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

/* 步骤5：构建完成 */
.build-complete {
  text-align: center;
  padding: 40px;
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
}

.complete-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.complete-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #52c41a;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.btn-primary, .btn-secondary, .btn-success {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #1890ff;
  color: #fff;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #d9d9d9;
}

.btn-secondary:hover {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.btn-success {
  background-color: #52c41a;
  color: #fff;
}

.btn-success:hover {
  background-color: #73d13d;
}
</script>
