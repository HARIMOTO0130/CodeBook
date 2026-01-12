# 教师报告API文档

## 1. 报告生成API

### 1.1 生成报告

**接口地址**：`POST /teacher/reports/`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| report_type | string | 是 | 报告类型：student（学生个人报告）、class（班级整体报告）、comparison（对比分析报告） |
| class_id | integer | 是 | 班级ID |
| student_id | integer | 否 | 学生ID，当report_type为student时必填 |
| start_date | string | 是 | 开始日期，格式：YYYY-MM-DD |
| end_date | string | 是 | 结束日期，格式：YYYY-MM-DD |
| include_progress | boolean | 否 | 是否包含学习进度，默认：true |
| include_homework | boolean | 否 | 是否包含作业完成情况，默认：true |
| include_attendance | boolean | 否 | 是否包含出勤统计，默认：false |
| include_performance | boolean | 否 | 是否包含成绩分析，默认：true |
| export_format | string | 否 | 导出格式：pdf、excel、word，默认：pdf |

**返回格式**：

```json
{
    "id": 1,
    "title": "班级学习报告",
    "report_type": "class",
    "class_obj": 1,
    "class_name": "2024级计算机科学1班",
    "student": null,
    "student_name": "",
    "student_no": "",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "include_progress": true,
    "include_homework": true,
    "include_attendance": false,
    "include_performance": true,
    "export_format": "pdf",
    "report_data": {
        "title": "班级学习报告",
        "generated_at": "2024-02-01 14:30:00",
        "report_type": "class",
        "progress": {
            "totalChapters": 20,
            "completedChapters": 15,
            "completionRate": 75,
            "totalTime": 120.5,
            "avgLearnTime": 6.0
        },
        "homework": {
            "total": 10,
            "submitted": 9,
            "avgScore": 85,
            "submissionRate": 90
        },
        "student_performances": [
            {
                "student_name": "张三",
                "student_no": "20240101",
                "completed_chapters": 18,
                "total_learn_time": 1440,
                "avg_score": 92
            },
            // 更多学生表现数据...
        ]
    },
    "file_path": null,
    "status": 2,
    "generated_at": "2024-02-01T14:30:00Z",
    "updated_at": "2024-02-01T14:30:00Z"
}
```

**响应状态码**：

| 状态码 | 描述 |
|--------|------|
| 201 | 报告生成成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

## 2. 报告管理API

### 2.1 获取报告列表

**接口地址**：`GET /teacher/reports/`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| class_obj | integer | 否 | 班级ID，用于筛选特定班级的报告 |
| report_type | string | 否 | 报告类型，用于筛选特定类型的报告 |
| status | integer | 否 | 报告状态，用于筛选特定状态的报告 |
| search | string | 否 | 搜索关键字，用于搜索报告标题 |
| ordering | string | 否 | 排序字段，支持：generated_at、title |

**返回格式**：

```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "班级学习报告",
            "report_type": "class",
            "class_obj": 1,
            "class_name": "2024级计算机科学1班",
            "student": null,
            "student_name": "",
            "student_no": "",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "include_progress": true,
            "include_homework": true,
            "include_attendance": false,
            "include_performance": true,
            "export_format": "pdf",
            "report_data": {},
            "file_path": null,
            "status": 2,
            "generated_at": "2024-02-01T14:30:00Z",
            "updated_at": "2024-02-01T14:30:00Z"
        },
        // 更多报告数据...
    ]
}
```

**响应状态码**：

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 401 | 未授权 |

### 2.2 获取报告详情

**接口地址**：`GET /teacher/reports/{report_id}/`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| report_id | integer | 是 | 报告ID |

**返回格式**：

```json
{
    "id": 1,
    "title": "班级学习报告",
    "report_type": "class",
    "class_obj": 1,
    "class_name": "2024级计算机科学1班",
    "student": null,
    "student_name": "",
    "student_no": "",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "include_progress": true,
    "include_homework": true,
    "include_attendance": false,
    "include_performance": true,
    "export_format": "pdf",
    "report_data": {
        "title": "班级学习报告",
        "generated_at": "2024-02-01 14:30:00",
        "report_type": "class",
        "progress": {
            "totalChapters": 20,
            "completedChapters": 15,
            "completionRate": 75,
            "totalTime": 120.5,
            "avgLearnTime": 6.0
        },
        "homework": {
            "total": 10,
            "submitted": 9,
            "avgScore": 85,
            "submissionRate": 90
        },
        "student_performances": [
            {
                "student_name": "张三",
                "student_no": "20240101",
                "completed_chapters": 18,
                "total_learn_time": 1440,
                "avg_score": 92
            },
            // 更多学生表现数据...
        ]
    },
    "file_path": null,
    "status": 2,
    "generated_at": "2024-02-01T14:30:00Z",
    "updated_at": "2024-02-01T14:30:00Z"
}
```

**响应状态码**：

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 404 | 报告不存在 |
| 401 | 未授权 |

### 2.3 下载报告

**接口地址**：`GET /teacher/reports/{report_id}/download/`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| report_id | integer | 是 | 报告ID |

**返回格式**：

- 返回PDF/Excel/Word文件流

**响应状态码**：

| 状态码 | 描述 |
|--------|------|
| 200 | 下载成功 |
| 404 | 报告不存在 |
| 401 | 未授权 |

### 2.4 预览报告

**接口地址**：`GET /teacher/reports/{report_id}/preview/`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| report_id | integer | 是 | 报告ID |

**返回格式**：

```json
{
    "title": "班级学习报告",
    "generated_at": "2024-02-01 14:30:00",
    "report_type": "class",
    "progress": {
        "totalChapters": 20,
        "completedChapters": 15,
        "completionRate": 75,
        "totalTime": 120.5,
        "avgLearnTime": 6.0
    },
    "homework": {
        "total": 10,
        "submitted": 9,
        "avgScore": 85,
        "submissionRate": 90
    },
    "student_performances": [
        {
            "student_name": "张三",
            "student_no": "20240101",
            "completed_chapters": 18,
            "total_learn_time": 1440,
            "avg_score": 92
        },
        // 更多学生表现数据...
    ]
}
```

**响应状态码**：

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 404 | 报告不存在 |
| 401 | 未授权 |

### 2.5 删除报告

**接口地址**：`DELETE /teacher/reports/{report_id}/`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| report_id | integer | 是 | 报告ID |

**返回格式**：

```json
{
    "detail": "报告已删除"
}
```

**响应状态码**：

| 状态码 | 描述 |
|--------|------|
| 204 | 删除成功 |
| 404 | 报告不存在 |
| 401 | 未授权 |

## 3. 报告数据结构

### 3.1 报告基本信息

```json
{
    "id": 1,
    "title": "班级学习报告",
    "report_type": "class",
    "class_obj": 1,
    "class_name": "2024级计算机科学1班",
    "student": null,
    "student_name": "",
    "student_no": "",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "include_progress": true,
    "include_homework": true,
    "include_attendance": false,
    "include_performance": true,
    "export_format": "pdf",
    "file_path": null,
    "status": 2,
    "generated_at": "2024-02-01T14:30:00Z",
    "updated_at": "2024-02-01T14:30:00Z"
}
```

### 3.2 报告数据

#### 3.2.1 学生个人报告数据

```json
{
    "title": "张三学习报告",
    "generated_at": "2024-02-01 14:30:00",
    "report_type": "student",
    "progress": {
        "totalChapters": 20,
        "completedChapters": 18,
        "completionRate": 90,
        "totalTime": 24.0
    },
    "homework": {
        "total": 10,
        "submitted": 10,
        "avgScore": 92,
        "submissionRate": 100
    }
}
```

#### 3.2.2 班级整体报告数据

```json
{
    "title": "2024级计算机科学1班学习报告",
    "generated_at": "2024-02-01 14:30:00",
    "report_type": "class",
    "progress": {
        "totalChapters": 20,
        "completedChapters": 15,
        "completionRate": 75,
        "totalTime": 120.5,
        "avgLearnTime": 6.0
    },
    "homework": {
        "total": 10,
        "submitted": 9,
        "avgScore": 85,
        "submissionRate": 90
    },
    "student_performances": [
        {
            "student_name": "张三",
            "student_no": "20240101",
            "completed_chapters": 18,
            "total_learn_time": 1440,
            "avg_score": 92
        },
        // 更多学生表现数据...
    ]
}
```

## 4. 状态码说明

| 状态码 | 描述 |
|--------|------|
| 1 | 生成中 |
| 2 | 已完成 |
| 3 | 生成失败 |

## 5. 使用示例

### 5.1 生成班级报告

```bash
curl -X POST http://localhost:8000/teacher/reports/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"report_type": "class", "class_id": 1, "start_date": "2024-01-01", "end_date": "2024-01-31"}'
```

### 5.2 生成学生个人报告

```bash
curl -X POST http://localhost:8000/teacher/reports/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"report_type": "student", "class_id": 1, "student_id": 1, "start_date": "2024-01-01", "end_date": "2024-01-31"}'
```

### 5.3 获取报告列表

```bash
curl -X GET "http://localhost:8000/teacher/reports/?class_obj=1&report_type=class" \
  -H "Authorization: Bearer <token>"
```

### 5.4 下载报告

```bash
curl -X GET http://localhost:8000/teacher/reports/1/download/ \
  -H "Authorization: Bearer <token>" \
  -o "班级学习报告.pdf"
```

## 6. 错误处理

### 6.1 常见错误返回格式

```json
{
    "error": "错误信息"
}
```

### 6.2 常见错误类型

| 错误类型 | 错误信息 | 状态码 |
|----------|----------|--------|
| 参数错误 | 缺少必要参数 | 400 |
| 参数错误 | 无效的报告类型 | 400 |
| 参数错误 | 日期格式无效，应为YYYY-MM-DD | 400 |
| 资源不存在 | 班级不存在 | 404 |
| 资源不存在 | 学生不存在或不在该班级 | 404 |
| 权限错误 | 无权限访问 | 403 |
| 服务器错误 | 生成报告失败 | 500 |

## 7. 性能优化建议

1. **报告生成异步处理**：对于大数据量的报告生成，建议使用异步任务处理，避免请求超时
2. **数据缓存**：对于频繁访问的报告数据，建议使用缓存机制，提高响应速度
3. **分页查询**：报告列表查询时，使用分页机制，减少单次返回的数据量
4. **索引优化**：在报告表的常用查询字段上建立索引，提高查询效率
5. **数据库连接池**：使用数据库连接池，减少数据库连接开销

## 8. 安全建议

1. **身份验证**：所有API接口必须进行身份验证，确保只有授权用户可以访问
2. **权限控制**：确保用户只能访问自己有权限的报告
3. **数据加密**：敏感数据传输时，使用HTTPS加密
4. **输入验证**：对所有输入参数进行严格验证，防止SQL注入和XSS攻击
5. **日志记录**：记录API访问日志，便于审计和问题排查

## 9. 版本控制

| 版本 | 日期 | 描述 |
|------|------|------|
| v1.0 | 2024-02-01 | 初始版本，实现基本报告功能 |
| v1.1 | 2024-02-15 | 优化报告生成性能，添加异步处理 |
| v1.2 | 2024-03-01 | 添加报告导出功能，支持多种格式 |

## 10. 联系方式

如有问题或建议，请联系：

- 技术支持：tech-support@codebook.com
- API文档更新时间：2024-02-01

## 11. 变更记录

| 变更日期 | 变更内容 |
|----------|----------|
| 2024-02-01 | 初始创建API文档 |
| 2024-02-05 | 补充报告生成参数说明 |
| 2024-02-10 | 添加使用示例和错误处理说明 |