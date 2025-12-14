from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class NodeConfig(BaseModel):
    """节点配置模型"""
    id: str
    type: str
    # 动态agent节点配置
    agent_id: Optional[int] = None  # agent ID，用于动态agent节点
    client_id: Optional[str] = None  # MCP客户端ID，用于MCP工具节点
    tool_name: Optional[str] = None  # 工具名称，用于MCP工具节点
    # 节点参数配置
    parameters: Dict[str, Any] = {}


class EdgeConfig(BaseModel):
    """边配置模型"""
    source: str
    target: str
    is_condition: bool = False
    condition_type: str = None
    route_function: str = None
    path_map: Dict[str, str] = None


class WorkflowConfig(BaseModel):
    """工作流配置模型"""
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]
    # 动态agent配置
    dynamic_agents: List[Dict[str, Any]] = []  # 动态agent配置列表


class WorkflowExecutionRequest(BaseModel):
    """工作流执行请求模型"""
    workflow_config: WorkflowConfig
    initial_state: Dict[str, Any]


class AgentDiscoveryResponse(BaseModel):
    """Agent发现响应模型"""
    agents: List[Dict[str, Any]]
    mcp_tools: Dict[str, Any]


class DynamicAgentNode(BaseModel):
    """动态agent节点模型"""
    node_id: str
    agent_id: int
    tool_name: str
    parameters: Dict[str, Any] = {}
