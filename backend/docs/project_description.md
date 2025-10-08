# 🧠 Project Description

职位智能 Agent 是一套围绕岗位与简历匹配场景打造的 AI 后端，结合 LangChain、Chroma 与 DashScope LLM，实现岗位知识库检索、简历解析、智能推荐与报告生成。本说明文档覆盖项目目标、核心功能、技术亮点以及安装、配置与运行指引。

## 目录
- [项目目标](#项目目标)
- [核心功能](#核心功能)
- [技术亮点](#技术亮点)
- [系统依赖](#系统依赖)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [运行与测试](#运行与测试)
- [目录结构](#目录结构)
- [未来规划](#未来规划)

## 项目目标
- 构建一套可复用的后端服务，为招聘场景下的 AI Agent 提供岗位检索、简历解析与匹配能力。
- 在同一套架构下支持多格式简历输入、岗位知识库维护与智能报告输出。
- 通过可观测的缓存策略与重试机制，提高外部依赖（DashScope、Chroma）的稳定性。

## 核心功能
1. **简历入库**
   - 支持 PDF/DOCX/TXT 上传
   - 解析原文，调用 LLM 抽取结构化 JSON，落盘存储
2. **岗位知识库**
   - ETL 脚本清洗岗位数据
   - LangChain + ChromaDB 持久化向量库
3. **智能匹配**
   - 简历向量化 → 岗位向量检索 → 相似度评分
   - LLM 生成推荐摘要或单岗位深度分析
   - Jinja2 渲染匹配报告 HTML
4. **监控与工具**
   - TTL 缓存配合 `/diagnostics/cache` 查看命中率
   - 重试机制统一封装外部服务调用

## 技术亮点
- **DashScope 兼容层**：通过 OpenAI SDK 与自定义重试，统一 LLM / Embedding 调用。
- **LangChain 集成**：`DashscopeEmbeddings` 适配器让 LangChain 文档向量化与 Chroma 持久化无缝衔接。
- **模块化架构**：`api`、`services`、`utils` 等分层清晰，便于扩展新路由或替换底层实现。
- **缓存策略**：`app/utils/cache.TTLCache` 在嵌入和摘要层面减少重复请求，指标可观测。
- **可视化报告**：使用模板引擎输出 HTML 报告，易于定制品牌风格。

## 系统依赖
- Python 3.10+
- FastAPI, uvicorn
- LangChain, ChromaDB
- OpenAI SDK (DashScope 兼容)
- pdfminer.six, python-docx, pandas, scikit-learn, numpy
- Jinja2, tenacity, pytest

## 安装步骤
```bash
git clone <repo-url>
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
```

## 配置说明
1. 在根目录创建 `.env`，至少配置：
   ```env
   DASHSCOPE_API_KEY=your-dashscope-key
   DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   ```
2. 可根据需要调整 `app/core/config.py` 中的默认值，例如：
   - `chroma_persist_directory`
   - `reports_directory`
   - `cache_ttl`
   - `allowed_file_types`
3. 目录初始化由 `Settings` 自动完成，可确保 `data/chroma`、`data/uploads`、`data/reports` 存在。

## 运行与测试
1. **构建岗位知识库（可选）**
   ```bash
   python scripts/ETL.py
   ```
2. **启动服务**
   ```bash
   uvicorn app.main:app --reload
   ```
3. **调试接口**
   - Swagger：`http://localhost:8000/docs`
   - 健康检查：`GET /ping`
4. **运行测试**
   ```bash
   pytest
   ```

## 目录结构
```
app/
├─ api/                # FastAPI 路由 (kb, resume, match)
├─ core/               # Settings 配置
├─ services/           # 业务服务层 (解析、向量、报告)
├─ utils/              # 缓存、重试等通用工具
├─ main.py             # 应用入口
scripts/
├─ ETL.py              # 岗位数据清洗与持久化
tests/
├─ test_cache.py       # 缓存单元测试
data/
├─ raw/                # 原始岗位数据
├─ chroma/             # 向量库存储
├─ uploads/            # 简历 JSON
├─ reports/            # HTML 报告
```

## 未来规划
- 扩展匹配维度（多模型融合、权重配置）。
- 增加批量简历处理与消息队列调度。
- 引入更多端到端测试（上传→匹配→报告）。
- 补充 Docker 化部署及 CI/CD 管线。
