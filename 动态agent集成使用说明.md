# 动态Agent集成使用说明

## 概述

本系统实现了在workflow中动态集成plug-in-service提供的agent与MCP接口的功能。用户可以在构建工作流时动态地将agent与tools作为节点构建工作流，无需硬编码在代码中。

## 核心功能

### 1. Agent发现服务
- **API端点**: `GET /api/agents/discover`
- **功能**: 自动发现所有可用的agent和MCP工具
- **返回数据**: 
  - `agents`: 可用agent列表
  - `mcp_tools`: 按agent分组的MCP工具列表

### 2. 动态Agent节点创建
- **API端点**: `POST /api/nodes/dynamic-agent`
- **请求参数**:
  ```json
  {
    "client_id": "客户端标识",
    "tool_name": "工具名称",
    "parameters": {
      "参数1": "值1",
      "参数2": "值2"
    }
  }
  ```
- **功能**: 创建动态agent节点配置，用于工作流构建

### 3. MCP客户端连接
- **API端点**: `POST /api/mcp/clients/connect`
- **功能**: 建立与plug-in-server的MCP客户端连接

## 使用流程

### 步骤1: 启动服务

1. **启动plug-in-server** (端口3000):
   ```bash
   cd plug-in-server
   npm start
   ```

2. **启动work-stream** (端口8000):
   ```bash
   cd work_stream
   python app.py
   ```

### 步骤2: 发现可用Agent和工具

```bash
curl -X GET http://localhost:8000/api/agents/discover
```

**响应示例**:
```json
{
  "agents": [
    {
      "id": "deepseek",
      "name": "DeepSeek Agent",
      "description": "DeepSeek智能助手"
    }
  ],
  "mcp_tools": {
    "deepseek": [
      {
        "name": "chat",
        "description": "对话功能",
        "parameters": {
          "message": "string"
        }
      }
    ]
  }
}
```

### 步骤3: 创建动态Agent节点

```bash
curl -X POST http://localhost:8000/api/nodes/dynamic-agent \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test_client",
    "tool_name": "chat",
    "parameters": {
      "message": "Hello from dynamic agent!"
    }
  }'
```

**响应示例**:
```json
{
  "id": "dynamic_agent_12345",
  "type": "dynamic_agent",
  "client_id": "test_client",
  "tool_name": "chat",
  "parameters": {
    "message": "Hello from dynamic agent!"
  }
}
```

### 步骤4: 构建包含动态节点的工作流

使用返回的节点配置构建工作流：

```json
{
  "nodes": [
    {
      "id": "input_processing",
      "type": "llm_node"
    },
    {
      "id": "dynamic_agent_12345",
      "type": "dynamic_agent",
      "client_id": "test_client",
      "tool_name": "chat",
      "parameters": {
        "message": "Hello from dynamic agent!"
      }
    },
    {
      "id": "output_processing",
      "type": "uppercase_node"
    }
  ],
  "edges": [
    {
      "source": "START",
      "target": "input_processing"
    },
    {
      "source": "input_processing",
      "target": "dynamic_agent_12345"
    },
    {
      "source": "dynamic_agent_12345",
      "target": "output_processing"
    },
    {
      "source": "output_processing",
      "target": "END"
    }
  ]
}
```

### 步骤5: 验证和执行工作流

1. **验证工作流**:
   ```bash
   curl -X POST http://localhost:8000/api/workflows/validate \
     -H "Content-Type: application/json" \
     -d '工作流配置JSON'
   ```

2. **执行工作流**:
   ```bash
   curl -X POST http://localhost:8000/api/workflows/execute \
     -H "Content-Type: application/json" \
     -d '{
       "workflow_config": 工作流配置JSON,
       "initial_state": {
         "messages": [["user", "测试消息"]]
       }
     }'
   ```

## 支持的Agent和工具

### DeepSeek Agent
- **工具**: `chat` - 对话功能
- **参数**: `message` - 对话消息

### Sensor Agent
- **工具**: `getSensorData` - 获取传感器数据
- **参数**: 
  - `uuid` - 传感器UUID
  - `sensor` - 传感器类型

## 测试工具

### 自动测试脚本
```bash
cd work_stream
python run_dynamic_agent_test.py
```

### 端到端测试
```bash
cd work_stream
python test_dynamic_agent_e2e.py
```

## 技术架构

### 核心组件
1. **agent_discovery_service**: Agent发现服务
2. **workflow_manager**: 工作流管理器，支持动态agent节点
3. **MCPClient**: MCP客户端，与plug-in-server通信
4. **API端点**: 提供RESTful接口

### 数据流
1. 用户通过API发现可用agent和工具
2. 创建动态agent节点配置
3. 构建包含动态节点的工作流
4. 执行工作流时动态连接MCP客户端
5. 调用agent工具并返回结果

## 注意事项

1. **依赖服务**: 需要plug-in-server正常运行在端口3000
2. **MCP连接**: 执行工作流前需要建立MCP客户端连接
3. **参数验证**: 动态节点参数需要符合工具要求
4. **错误处理**: 系统包含完善的错误处理和日志记录

## 扩展性

系统设计为可扩展架构，支持：
- 新的agent类型自动发现
- 自定义工具参数验证
- 多客户端并发连接
- 工作流状态持久化

## 故障排除

### 常见问题
1. **plug-in-server连接失败**: 检查端口3000是否被占用
2. **agent发现失败**: 确认plug-in-server正常运行
3. **工作流验证失败**: 检查节点配置和参数格式
4. **执行超时**: 检查MCP客户端连接状态

### 日志查看
- work-stream日志: 控制台输出或日志文件
- plug-in-server日志: npm start输出

---

**版本**: 1.0  
**最后更新**: 2024年  
**维护者**: 开发团队