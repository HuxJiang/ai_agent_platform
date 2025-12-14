from typing import TypedDict, Annotated, List, Dict, Any
from fastapi import FastAPI, HTTPException
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os

# 导入节点和工具
from nodes import node_llm, node_uppercase, node_lowercase, node_quadratic_equation, classify_input, decide_next_node, handle_search, handle_chat
from models import NodeConfig, EdgeConfig, WorkflowConfig, WorkflowExecutionRequest
from manager import AgentInfo, AgentManager
from manager.workflow_manager import build_graph_from_config, discover_available_agents_and_tools, create_dynamic_agent_node_config
from manager.agent_discovery import agent_discovery_service

# 导入Pydantic模型用于MCP相关API
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="LangGraph 工作流 API",
    description="接收JSON数据并生成相应的LangGraph工作流，支持MCP智能体调用",
    version="1.0.0"
)

# 全局智能体管理器实例
global_agent_manager = AgentManager()

# MCP相关的Pydantic模型
class MCPServerConfig(BaseModel):
    """MCP服务器配置模型"""
    url: str = Field(..., description="MCP服务地址")
    headers: Optional[Dict[str, str]] = Field(None, description="额外请求头")
    bearerToken: Optional[str] = Field(None, description="授权令牌")
    client: Optional[Dict[str, str]] = Field(None, description="客户端信息")
    capabilities: Optional[Dict[str, bool]] = Field(None, description="能力声明")
    sessionId: Optional[str] = Field(None, description="会话ID")
    protocolVersion: Optional[str] = Field(None, description="协议版本")

class MCPInitializeOperation(BaseModel):
    """MCP初始化操作模型"""
    type: str = Field(..., description="操作类型")
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")
    cursor: Optional[str] = Field(None, description="游标")
    name: Optional[str] = Field(None, description="工具名称")
    arguments: Optional[Dict[str, Any]] = Field(None, description="工具参数")
    uri: Optional[str] = Field(None, description="资源URI")

class MCPInitialize(BaseModel):
    """MCP初始化模型"""
    operations: List[MCPInitializeOperation] = Field(..., description="初始化操作列表")

class MCPConnectRequest(BaseModel):
    """MCP连接请求模型"""
    client_id: str = Field(..., description="客户端唯一标识")
    server_config: MCPServerConfig = Field(..., description="MCP服务器配置")
    initialize: Optional[MCPInitialize] = Field(None, description="初始化操作")

class MCPRegisterAgentRequest(BaseModel):
    """MCP智能体注册请求模型"""
    name: str = Field(..., description="智能体名称")
    description: str = Field(..., description="智能体描述")
    mcp_client_id: str = Field(..., description="MCP客户端ID")
    mcp_tool_name: str = Field(..., description="MCP工具名称")
    dependencies: Optional[List[str]] = Field(None, description="依赖的其他智能体列表")


# 动态agent发现相关的Pydantic模型
class DynamicAgentNodeRequest(BaseModel):
    """动态agent节点创建请求模型"""
    agent_id: Optional[int] = Field(None, description="agent ID")
    client_id: Optional[str] = Field(None, description="MCP客户端ID")
    tool_name: str = Field(..., description="工具名称")
    node_id: Optional[str] = Field(None, description="节点ID（可选，自动生成）")
    parameters: Optional[Dict[str, Any]] = Field(None, description="节点参数")


class AgentDiscoveryResponse(BaseModel):
    """agent发现响应模型"""
    agents: List[Dict[str, Any]] = Field(..., description="可用的agent列表")
    mcp_tools: Dict[str, List[Dict[str, Any]]] = Field(..., description="按agent分组的MCP工具列表")


# 5. API 端点

@app.get("/api/nodes", response_model=Dict[str, str])
async def get_available_nodes():
    """获取可用的节点类型"""
    node_descriptions = {
        "llm_node": "生成AI回复的LLM节点",
        "uppercase_node": "将最后一条消息转换为大写",
        "lowercase_node": "将最后一条消息转换为小写",
        "quadratic_equation_node": "解一元二次方程的节点，支持格式：a,b,c 或 ax² + bx + c = 0",
        "classify_input": "分类节点：决定用户意图（如天气查询或闲聊）",
        "handle_search": "搜索节点：处理天气查询请求",
        "handle_chat": "闲聊节点：处理普通对话请求"
    }
    return node_descriptions

# MCP相关API端点
@app.post("/api/mcp/clients/connect")
async def connect_mcp_client(request: MCPConnectRequest):
    """建立/替换与MCP的持久连接"""
    try:
        # 转换为MCP客户端需要的格式
        initialize_dict = None
        if request.initialize:
            initialize_dict = {
                "operations": [op.dict(exclude_none=True) for op in request.initialize.operations]
            }
        
        result = global_agent_manager.connect_mcp_client(
            client_id=request.client_id,
            server_config=request.server_config.dict(exclude_none=True),
            initialize=initialize_dict
        )
        
        return {"message": "MCP客户端连接成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP客户端连接失败: {str(e)}")

@app.post("/api/mcp/clients/{client_id}/disconnect")
async def disconnect_mcp_client(client_id: str):
    """断开与MCP的持久连接"""
    try:
        result = global_agent_manager.disconnect_mcp_client(client_id)
        return {"message": "MCP客户端断开成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP客户端断开失败: {str(e)}")

@app.get("/api/mcp/clients")
async def list_mcp_clients():
    """列出所有MCP客户端连接"""
    try:
        connections = global_agent_manager.list_mcp_connections()
        return {"message": "获取MCP客户端列表成功", "data": connections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取MCP客户端列表失败: {str(e)}")

@app.post("/api/mcp/agents/register")
async def register_mcp_agent(request: MCPRegisterAgentRequest):
    """注册一个MCP智能体"""
    try:
        global_agent_manager.register_mcp_agent(
            name=request.name,
            description=request.description,
            mcp_client_id=request.mcp_client_id,
            mcp_tool_name=request.mcp_tool_name,
            dependencies=request.dependencies
        )
        return {"message": "MCP智能体注册成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP智能体注册失败: {str(e)}")

@app.get("/api/agents")
async def list_agents():
    """列出所有注册的智能体"""
    try:
        agents = global_agent_manager.list_agents()
        return {"message": "获取智能体列表成功", "data": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取智能体列表失败: {str(e)}")


# 动态agent发现相关API端点
@app.get("/api/agents/discover", response_model=AgentDiscoveryResponse)
async def discover_agents_and_tools():
    """发现所有可用的agent和MCP工具"""
    try:
        result = await discover_available_agents_and_tools()
        return AgentDiscoveryResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发现agent和工具失败: {str(e)}")


@app.post("/api/nodes/dynamic-agent", response_model=NodeConfig)
async def create_dynamic_agent_node(request: DynamicAgentNodeRequest):
    """创建动态agent节点配置"""
    try:
        node_config = create_dynamic_agent_node_config(
            agent_id=request.agent_id,
            client_id=request.client_id,
            tool_name=request.tool_name,
            node_id=request.node_id,
            parameters=request.parameters
        )
        return node_config
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建动态agent节点失败: {str(e)}")

@app.post("/api/workflows/validate")
async def validate_workflow(workflow_config: WorkflowConfig):
    """验证工作流配置"""
    try:
        # 尝试构建工作流以验证配置
        await build_graph_from_config(workflow_config)
        return {"message": "工作流配置有效"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"工作流配置无效: {str(e)}")

@app.post("/api/workflows/execute", response_model=Dict[str, Any])
async def execute_workflow(execution_request: WorkflowExecutionRequest):
    """执行工作流"""
    try:
        # 构建工作流
        app_workflow = await build_graph_from_config(execution_request.workflow_config)
        
        # 执行工作流（使用异步API）
        result = await app_workflow.ainvoke(execution_request.initial_state)
        
        return {
            "message": "工作流执行成功",
            "result": result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工作流执行失败: {str(e)}")

@app.post("/api/workflows/test", response_model=Dict[str, Any])
async def test_simple_workflow():
    """测试简单工作流的执行（包含动态agent集成）"""
    
    # 首先发现可用的agent
    try:
        discovery_result = await discover_available_agents_and_tools()
        agents = discovery_result.get("agents", [])
        
        # 检查是否有deepseek-chat agent
        deepseek_agent = None
        for agent in agents:
            if agent.get("name") == "deepseek-chat":
                deepseek_agent = agent
                break
        
        # 创建工作流配置
        if deepseek_agent:
            # 使用动态agent的工作流配置
            simple_config = WorkflowConfig(
                nodes=[
                    NodeConfig(id="step1", type="dynamic_agent", 
                             agent_id=deepseek_agent["id"], tool_name="deepseek-chat"),
                    NodeConfig(id="step2", type="uppercase_node")
                ],
                edges=[
                    EdgeConfig(source="START", target="step1"),
                    EdgeConfig(source="step1", target="step2"),
                    EdgeConfig(source="step2", target="END")
                ],
                dynamic_agents=[deepseek_agent]
            )
        else:
            # 如果没有找到deepseek-chat，使用默认配置
            simple_config = WorkflowConfig(
                nodes=[
                    NodeConfig(id="step1", type="llm_node"),
                    NodeConfig(id="step2", type="uppercase_node")
                ],
                edges=[
                    EdgeConfig(source="START", target="step1"),
                    EdgeConfig(source="step1", target="step2"),
                    EdgeConfig(source="step2", target="END")
                ]
            )
        
        # 执行工作流
        app_workflow = await build_graph_from_config(simple_config)
        initial_state = {"messages": [("user", "hello world")]}
        result = await app_workflow.ainvoke(initial_state)
        
        return {
            "message": "测试工作流执行成功",
            "workflow_config": simple_config.model_dump(),
            "initial_state": initial_state,
            "result": result,
            "agent_discovery": {
                "found_deepseek_agent": deepseek_agent is not None,
                "agent_details": deepseek_agent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试工作流执行失败: {str(e)}")

# 6. 主程序入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
