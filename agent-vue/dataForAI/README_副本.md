# 职位智能 Agent Backend

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-0.3.x-1C3A70)
![ChromaDB](https://img.shields.io/badge/Vectorstore-ChromaDB-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

基于 FastAPI、DashScope LLM 与 Chroma 向量库的岗位推荐与简历分析后端，支持智能匹配、自动摘要与 HTML 报告生成，可作为招聘场景下的 AI Agent 服务端。

## 📑 目录
- [架构概览](#架构概览)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [运行与测试](#运行与测试)
- [API 速览](#api-速览)
- [数据流](#数据流)
- [未来规划](#未来规划)
- [许可证](#许可证)

## 架构概览
```mermaid
flowchart LR
  subgraph API
    R1[/GET \/kb\/query/]
    R2[/POST \/resume\/upload/]
    R3[/GET \/match\/auto/]
    R4[/GET \/match\/single/]
  end
  R2 --> P[resume_parser]
  P --> X[extract_resume_info (LLM)]
  X --> J[(uploads JSON)]
  R1 & R3 & R4 --> C[langchain_clients.Chroma]
  J --> L[get_embedding]
  L --> C
  C --> M[匹配服务 routes_match]
  M --> S[DashScope Chat 模型]
  M --> H[generate_report → HTML]
```

## 功能特性
- 多格式简历解析：支持 PDF/DOCX/TXT，自动抽取结构化字段。
- 职位知识库检索：LangChain + Chroma 持久化向量库，关键词检索与列表。
- 智能匹配与报告：相似度计算、LLM 推荐摘要、岗位详细分析与 HTML 报告。
- 稳定性增强：统一重试、线程安全 TTL 缓存、缓存命中统计。
- 数据 ETL：脚本化清洗岗位数据，分块向量化并持久化写入 Chroma。

## 快速开始
```bash
git clone <repo-url>
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
```

## 配置说明
1. 在根目录创建 `.env`：  
   ```bash
   DASHSCOPE_API_KEY=your-dashscope-key
   DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   ```
2. 可选参数（`app/core/config.py`）：服务端口、缓存 TTL、Chroma 存储路径、允许的上传格式等。
3. 确认数据目录：`data/raw`、`data/chroma`、`data/uploads`、`data/reports` 会自动创建。

## 运行与测试
- 预处理岗位库（可选）：  
  ```bash
  python scripts/ETL.py
  ```
- 启动开发服务：  
  ```bash
  uvicorn app.main:app --reload
  ```
- 打开交互文档：浏览 `http://localhost:8000/docs`。
- 运行测试：  
  ```bash
  pytest
  ```

## API 速览
| 方法 | 路径 | 描述 |
| --- | --- | --- |
| GET | `/ping` | 健康检查 |
| GET | `/diagnostics/cache` | 缓存命中统计 |
| GET | `/kb/query` | 岗位关键词检索 |
| GET | `/kb/list` | 向量库岗位列表 |
| POST | `/resume/upload` | 简历上传解析与结构化输出 |
| GET | `/match/auto` | 简历-岗位自动匹配与摘要 |
| GET | `/match/single` | 单岗位深度分析与报告生成 |

更多示例见 `docs/api_documentation.md` 或 Swagger UI。

## 数据流
1. `scripts/ETL.py` 将原始岗位 CSV/Excel 清洗、分块写入 Chroma。  
2. `/resume/upload` 解析简历原文并调用 DashScope LLM 提取结构化 JSON。  
3. `/match/auto` 以技能向量查询向量库返回匹配岗位并生成摘要。  
4. `/match/single` 对指定岗位 chunk 计算余弦相似度，生成深度分析与 HTML 报告。  
5. `TTLCache` 对 embedding 与 LLM 摘要结果做缓存；`/diagnostics/cache` 可观测状态。

## 未来规划
- 扩展匹配指标（多维评分、权重配置）。
- 引入批量简历处理与队列调度。
- 增加更多自动化测试（服务层、端到端）。
- 提供 Docker 镜像与部署脚本。

## 许可证
MIT License © 2024
