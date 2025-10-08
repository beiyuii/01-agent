# 📘 Backend Summary

职位智能 Agent 后端基于 FastAPI 构建，聚合 DashScope LLM、LangChain 与 ChromaDB，围绕岗位知识库与候选人简历匹配提供一整套服务。本摘要用于帮助团队快速理解系统架构、模块职责与数据流向。

## 目录
- [系统概览](#系统概览)
- [技术栈](#技术栈)
- [模块职责](#模块职责)
- [数据流说明](#数据流说明)
- [运行形态](#运行形态)
- [运维要点](#运维要点)

## 系统概览
- 框架：FastAPI 提供 REST 接口，Pydantic Settings 管理配置。
- 核心流程：简历上传解析 → LLM 结构化抽取 → 向量检索岗位 → 智能推荐/报告输出。
- 组件配合：LangChain 封装 Chroma 向量库访问；DashScope 提供嵌入与生成模型；Jinja2 负责报告模板渲染。

## 技术栈
| 分类 | 依赖 |
| ---- | ---- |
| Web 服务 | FastAPI, uvicorn |
| RAG / 向量库 | LangChain, ChromaDB, OpenAI SDK (DashScope) |
| 数据解析 | pdfminer.six, python-docx |
| 模板与渲染 | Jinja2 |
| 配置与验证 | pydantic, pydantic-settings |
| 稳定性组件 | tenacity, 自定义 TTLCache |
| 数据处理 | pandas, scikit-learn, numpy |
| 测试 | pytest |

## 模块职责
- `app/main.py`：统一加载路由 (`/kb`, `/resume`, `/match`) 与调试端点。
- `app/core/config.py`：读取 `.env`，初始化 DashScope/Chroma 路径、缓存 TTL、上传目录等。
- `app/api/routes_kb.py`：岗位检索与列表接口，直接面向向量库。
- `app/api/routes_resume.py`：处理文件上传、文本解析、调用 LLM 抽取结构化简历并落盘。
- `app/api/routes_match.py`：完成向量匹配、简历摘要、单岗位深度分析与报告生成。
- `app/services/langchain_clients.py`：封装 DashScope Embeddings 适配 LangChain，并暴露持久化 Chroma store。
- `app/services/resume_parser.py` / `resume_extractor.py` / `resume_loader.py`：简历解析、结构化抽取、JSON 读取。
- `app/services/report_generator.py`：渲染 HTML 报告。
- `app/utils/cache.py`、`app/utils/retry.py`：分别提供线程安全 TTL 缓存与统一重试封装。
- `scripts/ETL.py`：清洗岗位数据、分块向量化并写入 Chroma。
- `tests/test_cache.py`：覆盖缓存的命中、过期与清理逻辑。

## 数据流说明
```mermaid
graph TD
  subgraph 数据准备
    D[原始岗位 CSV/Excel] -->|scripts/ETL.py| E[Chroma 向量库]
  end
  subgraph 简历处理
    R[POST /resume/upload] --> P[resume_parser]
    P --> X[extract_resume_info (LLM)]
    X --> J[(uploads JSON)]
  end
  J --> L[get_embedding]
  L --> E
  E --> M[匹配服务 routes_match]
  M --> S[DashScope Chat 摘要/分析]
  M --> H[generate_report HTML]
  M -->|GET /match/auto & /match/single| C[客户端]
```

## 运行形态
1. **岗位知识库构建**：执行 `python scripts/ETL.py` 读取 `data/raw` 原始表格，清洗并写入 Chroma 持久化存储目录。
2. **服务启动**：`uvicorn app.main:app --reload` 启动 FastAPI，路由下沉到各功能模块。
3. **简历流程**：上传文件 → 解析原文 → LLM 抽取结构化 JSON → 存储于 `data/uploads`。
4. **匹配流程**：读取简历 JSON → Embedding → Chroma 检索匹配岗位 → 计算余弦相似度 → LLM 生成推荐摘要或深度分析 → 可选的 HTML 报告输出到 `data/reports`。

## 运维要点
- `app/core/config.py` 会在初始化时自动创建 `data/chroma`、`data/uploads`、`data/reports` 等目录。
- DashScope API Key 必须配置在 `.env`：`DASHSCOPE_API_KEY`。
- `app/utils/cache.TTLCache` 与 `/diagnostics/cache` 路由帮助监控缓存命中情况，可根据 QPS 调整 TTL。
- 建议在生产环境切换 `settings.environment` 为 `production`，并在 uvicorn 中增加 `--workers`。
- 报告文件与上传 JSON 建议定期归档或清理，防止磁盘膨胀。
