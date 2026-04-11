# 数据采集系统使用指南

## 1. 系统架构概览

### 1.1 整体架构

数据采集系统采用模块化设计，主要包含以下组件：

- **数据采集模块**：负责从各个数据源获取原始数据
  - MOOCCube数据集采集
  - Wikidata和DBpedia数据采集
  - 在线教育平台API数据采集
  - 教材与文档数据抽取爬虫

- **数据处理模块**：负责数据清洗、验证和标准化
  - 数据质量控制
  - 实体对齐和融合

- **数据存储模块**：负责数据的存储和管理
  - 原始数据存储
  - 处理后数据存储
  - 整合数据存储

- **数据整合模块**：负责将不同数据源的数据融合成统一的知识图谱

### 1.2 目录结构

```
data_collection/
├── config/            # 配置文件
├── mooccube/          # MOOCCube数据集采集
├── wikidata/          # Wikidata数据采集
├── dbpedia/           # DBpedia数据采集
├── education_platforms/ # 在线教育平台数据采集
├── textbooks/         # 教材与文档数据采集
├── spiders/           # 爬虫相关代码
├── utils/             # 工具函数
│   ├── data_models.py      # 数据模型
│   ├── quality_control.py  # 数据质量控制
│   └── data_integration.py # 数据整合
├── storage/           # 存储管理
└── logs/              # 日志文件
```

## 2. 环境准备

### 2.1 依赖安装

```bash
# 安装所需Python包
pip install requests scrapy tqdm
```

### 2.2 配置文件

配置文件位于 `data_collection/config/config.py`，可根据需要修改以下参数：

- 数据源配置
- 存储路径配置
- 处理参数配置
- 数据质量控制配置

## 3. 使用步骤

### 3.1 采集MOOCCube数据集

```bash
# 进入数据采集目录
cd data_collection

# 运行MOOCCube采集器
python mooccube/collector.py
```

### 3.2 采集Wikidata和DBpedia数据

```bash
# 运行Wikidata采集器
python wikidata/collector.py

# 运行DBpedia采集器
python dbpedia/collector.py
```

### 3.3 采集在线教育平台数据

```bash
# 运行教育平台采集器
python education_platforms/collector.py
```

### 3.4 运行教材与文档爬虫

```bash
# 运行教材爬虫
python textbooks/spiders.py
```

### 3.5 整合数据

```bash
# 运行数据整合
python utils/data_integration.py
```

### 3.6 导出到StrategyKG

```bash
# 在数据整合脚本中已经包含了导出功能
# 运行数据整合后会自动导出到StrategyKG格式
```

## 4. 数据格式说明

### 4.1 知识节点格式

```json
{
  "concept_id": "CS101",
  "concept_name": "Binary Search",
  "course_id": "C_Algorithm",
  "prerequisites": ["Array", "Time Complexity"],
  "successors": ["Binary Search Tree", "Graph Search"],
  "level": 2,
  "category": "algorithm",
  "description": "Binary search is an efficient algorithm for finding an item from a sorted list of items.",
  "source": "MOOCCube",
  "depth": 0,
  "parent_concept": null,
  "keywords": ["Binary Search", "algorithm"],
  "difficulty": 1,
  "importance": 1
}
```

### 4.2 课程格式

```json
{
  "course_id": "C001",
  "course_name": "Introduction to Computer Science",
  "description": "An introduction to the fundamentals of computer science.",
  "instructor": "John Doe",
  "institution": "Stanford University",
  "duration": "10 weeks",
  "difficulty": "beginner",
  "rating": 4.5,
  "enrollment_count": 100000,
  "start_date": "2024-01-01",
  "source": "Coursera",
  "concepts": ["Algorithm", "Data Structure"]
}
```

### 4.3 资源格式

```json
{
  "resource_id": "R001",
  "title": "Python Tutorial for Beginners",
  "url": "https://www.example.com/python-tutorial",
  "type": "video",
  "source": "Bilibili",
  "author": "Python Expert",
  "publish_date": "2024-01-01",
  "duration": "10:30",
  "language": "zh",
  "concepts": ["Python", "Programming"]
}
```

### 4.4 关系格式

```json
{
  "subject_id": "CS101",
  "subject_name": "Binary Search",
  "predicate": "requires",
  "object_id": "CS102",
  "object_name": "Array",
  "source": "MOOCCube"
}
```

## 5. 数据质量控制

### 5.1 验证规则

- **必填字段检查**：确保所有必要字段都存在
- **格式验证**：验证数据格式是否正确
- **完整性检查**：确保数据完整
- **一致性检查**：确保数据一致

### 5.2 清洗流程

1. **文本清洗**：去除多余空格、修复编码问题
2. **标准化**：统一命名规范
3. **去重**：移除重复数据
4. **类型转换**：确保数据类型正确

## 6. 常见问题解决

### 6.1 API限流问题

- 解决方案：在 `config.py` 中调整 `rate_limit` 参数，增加请求间隔

### 6.2 数据格式错误

- 解决方案：检查数据质量报告，修复错误数据

### 6.3 爬虫被封禁

- 解决方案：使用代理IP，减少请求频率，设置合理的User-Agent

### 6.4 内存不足

- 解决方案：调整 `batch_size` 参数，分批次处理数据

## 7. 示例代码

### 7.1 采集MOOCCube数据

```python
from mooccube.collector import MOOCCubeCollector

collector = MOOCCubeCollector()
data = collector.collect_all()
print(f"采集到 {len(data['concepts'])} 个知识点")
```

### 7.2 数据质量控制

```python
from utils.quality_control import DataQualityController

controller = DataQualityController()
processed_data, errors = controller.process_dataset(raw_data, 'node')
print(f"处理后数据数量: {len(processed_data)}")
print(f"错误数量: {len(errors)}")
```

### 7.3 数据整合

```python
from utils.data_integration import DataIntegrationManager

manager = DataIntegrationManager()
integrated_data = manager.integrate_data()
export_data = manager.export_to_strategy_kg()
print(f"整合后知识点数量: {len(integrated_data['concepts'])}")
```

## 8. 数据来源说明

| 数据源 | 类型 | 内容 | 规模 |
|--------|------|------|------|
| MOOCCube | 开源数据集 | 计算机科学MOOC课程数据 | 700+课程，11万+知识点 |
| Wikidata | 知识库 | 编程语言、算法等结构化数据 | 按需获取 |
| DBpedia | 知识库 | 从Wikipedia提取的结构化数据 | 按需获取 |
| Coursera | 在线教育平台 | 计算机科学课程 | 50+课程 |
| edX | 在线教育平台 | 计算机科学课程 | 50+课程 |
| Bilibili | 视频平台 | 技术教程 | 50+视频 |
| LeetCode | 编程平台 | 算法题目 | 按需获取 |
| 教材与文档 | 非结构化数据 | 经典教材、官方文档 | 按需获取 |

## 9. 性能优化

- **并行采集**：多线程同时采集不同数据源
- **增量更新**：只采集新数据，避免重复采集
- **缓存机制**：缓存已采集的数据，减少重复请求
- **分批处理**：大批次数据分小批次处理，减少内存使用

## 10. 扩展指南

### 10.1 添加新数据源

1. 在 `config.py` 中添加新数据源配置
2. 创建新的采集器模块
3. 在数据整合模块中添加新数据源的处理逻辑

### 10.2 自定义数据模型

修改 `utils/data_models.py` 中的数据模型，添加或修改字段

### 10.3 自定义数据质量规则

修改 `config.py` 中的 `QUALITY_CONFIG` 配置，调整验证规则

## 11. 监控与维护

- **日志监控**：查看 `logs` 目录下的日志文件
- **数据质量报告**：定期生成数据质量报告
- **自动更新**：设置定时任务，定期更新数据

## 12. 结论

本数据采集系统实现了多源异构数据的采集、处理和整合，为StrategyKG知识图谱提供了丰富的数据源。系统具有良好的可扩展性和可维护性，可以根据需要添加新的数据源和功能。

通过本系统采集的数据，StrategyKG知识图谱将包含：
- 计算机科学核心知识点
- 课程体系结构
- 学习资源推荐
- 知识点关联关系

这些数据将为用户提供更加个性化、全面的学习路径推荐。