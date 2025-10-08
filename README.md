# 求职者智能代理（Agent-Vue & Backend）

一个面向求职场景的端到端智能代理系统：前端 `agent-vue` 提供简历上传、岗位推荐与匹配报告的交互界面，后端 `backend` 负责简历解析、向量检索、岗位匹配与报告生成，底层集成了阿里云百炼大模型、Chroma 向量库与 LangChain。

---

## ✨ 核心能力
- **多格式简历处理**：支持 PDF / DOCX / TXT 上传，自动解析为结构化 JSON。
- **岗位知识库与匹配**：ETL 脚本清洗岗位数据并写入 Chroma，实时向量检索与余弦相似度计算。
- **LLM 智能分析**：调用 DashScope 模型生成推荐摘要、单岗深度分析及 HTML 报告。
- **易用的前端界面**：基于 Vue 3 + Naive UI，提供多语言、岗位推荐及报告预览。
- **健壮性保障**：统一的重试与 TTL 缓存组件、缓存诊断接口、可执行的单元测试。

---

## 📁 仓库结构
```text
.
├── agent-vue/          # 前端应用（Vue 3 + Vite + Naive UI）
│   ├── src/api         # 调用后端的 Axios 封装
│   ├── src/pages       # 上传、推荐、报告页面
│   ├── src/store       # Pinia 状态管理（简历 / 推荐缓存）
│   └── docs/           # UI 设计与说明文档
└── backend/            # 后端服务（FastAPI + LangChain + Chroma）
    ├── app/api         # FastAPI 路由（简历、知识库、匹配等）
    ├── app/services    # 解析、向量、报告等业务逻辑
    ├── app/utils       # 缓存、重试等通用工具
    ├── scripts/ETL.py  # 岗位数据清洗与向量化脚本
    ├── data/           # 原始数据、Chroma 持久化、上传与报告目录
    └── docs/           # 更详细的后端文档与 API 描述
```

---

## 🚀 快速开始

### 0. 前置依赖
- Python 3.10+（建议 3.11）
- Node.js 18+（建议使用 `npm` 或 `pnpm`）
- 本地已安装 `git`、`pip`、`npm`

---

### 1. 后端（`backend/`）

#### 安装依赖
```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 环境变量
在 `backend/.env` 中至少配置百炼接口密钥（`app/core/config.py` 会自动读取并创建必要目录）：
```bash
DASHSCOPE_API_KEY=your-dashscope-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# 可选：覆盖默认模型、端口、缓存 TTL、数据路径等
```

#### 准备岗位知识库（可选但推荐）
`scripts/ETL.py` 会读取 `data/raw/data_2026信息表.csv`，清洗后写入持久化 Chroma 向量库，并备份旧数据：
```bash
python scripts/ETL.py
```

#### 启动服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
访问 `http://localhost:8000/docs` 查看 Swagger，`/ping` 为健康检查，`/diagnostics/cache` 可查看缓存命中率。

#### 运行测试
```bash
pytest
```

---

### 2. 前端（`agent-vue/`）

#### 安装依赖
```bash
cd agent-vue
npm install
```

#### 本地开发
```bash
npm run dev
```
- 默认通过 Vite 代理将 `/resume` 与 `/match` 请求转发到 `http://localhost:8000`。
- 若后端部署在其他地址，可在根目录创建 `.env.local` 设置：
  ```bash
  VITE_API_BASE_URL=http://your-backend-host
  VITE_API_TIMEOUT=60000
  ```

#### 构建与预览
```bash
npm run build
npm run preview
```

---

## 🔄 端到端流程
1. 启动后端，确保 `.env` 配置正确且知识库已准备（或先运行 ETL）。
2. 启动前端开发服务器，访问 `http://localhost:5173`（默认端口）。
3. 上传 PDF/DOCX/TXT 简历 → 后端解析并结构化 → 自动获取岗位推荐与摘要。
4. 在“岗位推荐”页查看匹配列表，进入详情生成单岗匹配分析与 HTML 报告。
5. 报告文件默认生成在 `backend/data/reports/`，前端通过嵌入式查看器展示。

---

## 🧩 关键模块速览
- `backend/app/api/routes_resume.py`：文件上传、调用解析服务与 LLM 抽取。
- `backend/app/api/routes_match.py`：自动推荐与单岗匹配接口、缓存与报告生成。
- `backend/app/services/embedding_utils.py`：DashScope Embedding 封装与缓存。
- `backend/scripts/ETL.py`：岗位数据清洗、分块与向量化入库。
- `agent-vue/src/store/resume.js`：Pinia 状态，负责上传、推荐、报告请求与缓存。
- `agent-vue/src/components/ReportViewer.vue`：报告抓取、Markdown/HTML 渲染与刷新逻辑。

更多后端设计说明可参考 `backend/docs/`，前端界面原型位于 `agent-vue/docs/`。

---

## ✅ 常用命令速查
```bash
# Backend
uvicorn app.main:app --reload         # 开发模式启动
python scripts/ETL.py                 # 更新岗位向量库
pytest                                # 运行单元测试

# Frontend
npm run dev                           # 启动本地开发服务
npm run build                         # 生成生产构建
```

---

## 🤝 贡献与后续规划
- 欢迎提交 Issue / PR，补充测试与文档。
- 计划支持多维匹配评分、批量处理与 Docker 化部署。
- 计划将要新增对话流模式，进行多轮对话与更复杂的交互。
- 若需部署到生产环境，请根据实际需求加固鉴权、文件存储与日志系统。

---

MIT License © 2025 BeiYuii
