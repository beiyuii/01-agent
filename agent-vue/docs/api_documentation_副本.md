# ⚙️ API Documentation

本文档汇总职位智能 Agent 后端的公开接口，涵盖路由说明、请求与响应示例、异常处理及核心调用链，便于前端集成与测试验证。

## 目录
- [全局信息](#全局信息)
- [公共路由](#公共路由)
- [知识库接口](#知识库接口)
- [简历接口](#简历接口)
- [匹配接口](#匹配接口)
- [错误码约定](#错误码约定)
- [调用链分析](#调用链分析)

## 全局信息
- 根路径：`/`
- 文档入口：`/docs` (Swagger UI) / `/redoc`
- 默认返回格式：`application/json`
- 鉴权：当前环境未启用，需要时可通过 FastAPI 依赖注入扩展

## 公共路由
### `GET /ping`
- 说明：服务健康检查
- 请求参数：无
- 成功响应
  ```json
  {"status": "ok"}
  ```

### `GET /diagnostics/cache`
- 说明：返回服务器缓存命中情况，观察 embedding 与匹配摘要缓存效果
- 请求参数：无
- 成功响应
  ```json
  {
    "embedding": {"ttl": 3600, "size": 12, "hits": 58, "misses": 7},
    "match": {"ttl": 3600, "size": 4, "hits": 20, "misses": 3}
  }
  ```

## 知识库接口
### `GET /kb/query`
- 功能：根据关键词检索岗位信息
- 查询参数
  | 名称 | 类型 | 必填 | 说明 |
  | ---- | ---- | ---- | ---- |
  | `q` | string | 是 | 搜索关键词 |
  | `top_k` | int | 否 | 返回岗位数（默认 5） |
- 成功响应
  ```json
  {
    "query": "数据分析",
    "results": [
      {
        "job_id": "job_101",
        "company": "ACME",
        "title": "数据分析师",
        "location": "上海",
        "deadline": "2025-01-10",
        "batch": "秋招二批",
        "industry": "互联网",
        "document": "公司名称: ACME..."
      }
    ]
  }
  ```
- 异常：Chroma 检索失败时返回 `502`，`detail` 包含错误信息

### `GET /kb/list`
- 功能：列出向量库中的岗位元数据
- 查询参数：`limit`（默认 10）
- 成功响应
  ```json
  [
    {"id": "job_101", "meta": {"title": "数据分析师", "company": "ACME"}},
    {"id": "job_102", "meta": {"title": "算法工程师", "company": "Beta"}}
  ]
  ```
- 异常：Chroma 读取失败返回 `502`

## 简历接口
### `POST /resume/upload`
- 功能：上传简历文件，解析并生成结构化 JSON
- 请求体：`multipart/form-data`，字段 `file`（允许类型 pdf/docx/txt，≤10MB）
- 成功响应
  ```json
  {
    "filename": "resume_张三.pdf",
    "json_file": "data/uploads/resume_张三.json",
    "resume_data": {
      "basic_info": {"name": "张三", "email": "zhang@example.com"},
      "skills": ["Python", "SQL"],
      "experience": [{"company": "ACME", "role": "数据分析师", "...": "..."}]
    }
  }
  ```
- 异常
  - `400`：文件类型不受支持
  - `500`：解析或 LLM 抽取失败，`detail` 带具体错误

## 匹配接口
### `GET /match/auto`
- 功能：对指定简历 JSON 自动匹配推荐岗位并生成摘要
- 查询参数
  | 名称 | 类型 | 必填 | 说明 |
  | ---- | ---- | ---- | ---- |
  | `resume_file` | string | 是 | 简历 JSON 文件名（位于 `data/uploads`） |
  | `top_k` | int | 否 | 推荐岗位数量（默认 5） |
- 成功响应
  ```json
  {
    "resume_name": "张三",
    "recommendations": [
      {
        "score": 0.87,
        "job_id": "job_101",
        "title": "数据分析师",
        "company": "ACME",
        "location": "上海",
        "deadline": "2025-01-10",
        "snippet": "公司名称: ACME..."
      }
    ],
    "summary": "候选人与岗位高度匹配..."
  }
  ```
- 异常
  - `404`：简历文件不存在
  - `502`：嵌入生成、向量检索或摘要生成失败

### `GET /match/single`
- 功能：对单个岗位进行深度匹配分析并生成 HTML 报告
- 查询参数
  | 名称 | 类型 | 必填 | 说明 |
  | ---- | ---- | ---- | ---- |
  | `resume_file` | string | 是 | 简历 JSON 文件名 |
  | `job_id` | string | 是 | 目标岗位 ID（对应 Chroma 元数据 `job_id`） |
- 成功响应
  ```json
  {
    "resume_name": "张三",
    "job_title": "数据分析师",
    "company": "ACME",
    "location": "上海",
    "similarity_score": 0.83,
    "analysis": "匹配度评分：85...",
    "report_path": "data/reports/张三_数据分析师_匹配报告.html"
  }
  ```
- 异常
  - `404`：岗位未找到或缺少 embedding
  - `502`：向量检索或 LLM 分析失败

## 错误码约定
| 状态码 | 场景 |
| ------ | ---- |
| 200 | 请求成功 |
| 400 | 入参错误（如上传文件类型不支持） |
| 404 | 资源不存在（简历 JSON / 岗位向量缺失） |
| 500 | 文件解析或内部异常 |
| 502 | 外部依赖失败（Chroma、DashScope API 调用） |

## 调用链分析
- `/kb/*`：FastAPI → `get_vector_store()` → Chroma → 返回元数据/文档。
- `/resume/upload`：FastAPI → `parse_resume()` → LLM (`extract_resume_info`) → `save_resume_json()`。
- `/match/auto`：FastAPI → `load_resume_json()` → `get_embedding()`(TTL 缓存) → Chroma 向量查询 → LLM 摘要（缓存） → 返回推荐列表。
- `/match/single`：FastAPI → `load_resume_json()` → Chroma `collection.get()` → 余弦相似度计算 → LLM 深度分析（缓存） → `generate_report()` → 返回报告路径。
