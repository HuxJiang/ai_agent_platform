# Online RAG Service

在线检索增强生成（Retrieval-Augmented Generation, RAG）服务，提供高效的知识检索与问答能力。

## 项目简介

Online RAG Service 是一个基于向量检索的知识库问答系统，支持多用户空间隔离，提供文本嵌入、向量存储、相似性搜索等核心功能。系统采用Docker容器化部署，集成了MySQL、Qdrant等组件，可快速构建企业级知识库应用。

## 核心特性

- **多用户隔离**：为每个用户创建独立的向量集合，确保数据隔离
- **文本嵌入**：基于DashScope API的高效文本向量化
- **向量存储**：使用Qdrant作为高性能向量数据库
- **混合搜索**：结合关键词搜索和向量搜索优势
- **多源数据导入**：支持直接导入文本或从数据库同步数据
- **Docker化部署**：一键启动完整服务栈
- **RESTful API**：标准化的接口设计，便于集成

## 技术栈

- **Web框架**：FastAPI
- **向量数据库**：Qdrant
- **嵌入模型**：DashScope text-embedding-v1
- **关系数据库**：MySQL 8.0
- **数据库管理**：phpMyAdmin
- **容器化**：Docker & Docker Compose
- **编程语言**：Python 3.10+

## 快速开始

### 前提条件

- Docker 和 Docker Compose 已安装
- 有效的阿里云DashScope API密钥

### 部署步骤

1. **克隆项目**

```bash
git clone https://your-repo-url/online-rag-service.git
cd online-rag-service
```

2. **配置环境变量**

创建 `.env` 文件（参考 `.env.example`）：

```bash
# DashScope API密钥
DASHSCOPE_API_KEY=your_dashscope_api_key

# 数据库配置
RAG_DB_HOST=rag-mysql
RAG_DB_PORT=3306
RAG_DB_USER=demo_user
RAG_DB_PASS=demo_pass_123
RAG_DB_NAME=demo_db

# Qdrant配置
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

3. **启动服务**

```bash
docker compose up -d
```

服务启动后，可通过以下地址访问：
- RAG服务：http://localhost:8000
- API文档：http://localhost:8000/docs
- phpMyAdmin：http://localhost:8081

## 服务架构

系统包含以下核心组件：

1. **rag-service**：主服务，提供API接口和业务逻辑
2. **qdrant**：向量数据库，存储和检索向量嵌入
3. **rag-mysql**：关系数据库，存储结构化知识数据
4. **phpmyadmin-demo**：数据库管理界面

## API文档

服务启动后，访问 http://localhost:8000/docs 可查看完整的API文档。

### 主要接口

#### 1. 知识导入

**导入原始文本**
- URL: `/rag/ingest-raw`
- Method: `POST`
- 请求体：
  ```json
  {
    "source": "raw",
    "title": "文档标题",
    "category": "文档类别",
    "text": "文档内容...",
    "keywords": "关键词1,关键词2",
    "chunkSize": 500,
    "chunkOverlap": 50,
    "user": "username"
  }
  ```

**从数据库同步**
- URL: `/rag/sync-db`
- Method: `POST`
- 请求体：
  ```json
  {
    "source": "db",
    "ids": [1, 2, 3],
    "user": "username"
  }
  ```

#### 2. 知识检索

**向量检索**
- URL: `/rag/search`
- Method: `POST`
- 请求体：
  ```json
  {
    "q": "查询文本",
    "topK": 5,
    "category": "可选的分类过滤"
  }
  ```

**混合检索**
- URL: `/rag/hybrid-search`
- Method: `POST`
- 请求体：
  ```json
  {
    "q": "查询文本",
    "topK": 5,
    "category": "可选的分类过滤",
    "alpha": 0.7,
    "beta": 0.3
  }
  ```

#### 3. 知识管理

**根据标题删除**
- URL: `/rag/delete-by-title`
- Method: `POST`

**根据类别删除**
- URL: `/rag/delete-by-category`
- Method: `POST`

## 配置说明

### 环境变量

主要配置项通过环境变量控制：

- `DASHSCOPE_API_KEY`：DashScope API密钥（必需）
- `RAG_DATA_DIR`：数据存储目录
- `RAG_MODEL_NAME`：嵌入模型名称
- `QDRANT_HOST`：Qdrant服务地址
- `QDRANT_PORT`：Qdrant服务端口
- `QDRANT_COLLECTION_NAME`：向量集合基础名称

### 数据库配置

MySQL数据库配置：

- 主机：rag-mysql (容器名称)
- 端口：3306
- 用户：demo_user
- 密码：demo_pass_123
- 数据库：demo_db

### 向量维度

系统使用DashScope text-embedding-v1模型，生成的向量维度为1536。

## 开发说明

### 本地开发

1. **安装依赖**

```bash
pip install -r requirements.txt
```

2. **配置环境变量**

创建 `.env` 文件并设置必要的环境变量。

3. **启动开发服务**

```bash
python app.py
```

### 项目结构

```
online-rag-service/
├── app.py              # FastAPI应用主入口
├── config.py           # 配置管理
├── services/           # 核心服务层
│   ├── embedder.py     # 文本嵌入服务
│   ├── vector_store.py # 向量存储服务
│   ├── db.py           # 数据库服务
│   └── hybrid_search.py # 混合搜索服务
├── data/               # 数据存储目录
├── model/              # 模型目录
└── docker-compose.yml  # Docker配置
```

## 故障排除

### 常见问题

1. **Qdrant连接失败**
   - 检查Qdrant服务是否正常运行
   - 确认环境变量 `QDRANT_HOST` 和 `QDRANT_PORT` 设置正确

2. **DashScope API错误**
   - 验证API密钥是否有效
   - 检查网络连接是否正常

3. **向量检索失败**
   - 确认向量集合已正确创建
   - 检查向量维度是否匹配（应为1536）

## 安全注意事项

1. 在生产环境中，建议修改默认的数据库密码
2. 配置CORS时，应设置具体的域名而非使用通配符 `*`
3. API密钥等敏感信息应通过环境变量管理，避免硬编码

## 许可证

本项目采用 [MIT License](LICENSE)。
