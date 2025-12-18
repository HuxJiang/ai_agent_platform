from typing import Dict, Any, List, Optional
import requests
import json

class MCPError(Exception):
    """MCP客户端错误类"""
    pass

class MCPAgentInfo:
    """MCP智能体信息类"""
    def __init__(self, id: int, name: str, description: Optional[str] = None, category: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.category = category

class MCPConversation:
    """MCP会话信息类"""
    def __init__(self, id: int, userId: int, model: Optional[str] = None, mainAgent: Optional[int] = None):
        self.id = id
        self.userId = userId
        self.model = model
        self.mainAgent = mainAgent

class MCPMessage:
    """MCP消息类"""
    def __init__(self, role: str, content: str, name: Optional[str] = None, tool_call_id: Optional[str] = None, to: Optional[str] = None):
        self.role = role
        self.content = content
        self.name = name
        self.tool_call_id = tool_call_id
        self.to = to

class MCPToolCall:
    """MCP工具调用类"""
    def __init__(self, id: Optional[str] = None, type: str = "function", function: Optional[Dict[str, Any]] = None):
        self.id = id
        self.type = type
        self.function = function or {}

class MCPMessageWithToolCall(MCPMessage):
    """带工具调用的MCP消息类"""
    def __init__(self, role: str, content: str, tool_calls: List[MCPToolCall], name: Optional[str] = None, tool_call_id: Optional[str] = None, to: Optional[str] = None):
        super().__init__(role, content, name, tool_call_id, to)
        self.tool_calls = tool_calls

class MCPClient:
    """MCP API客户端类"""
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        初始化MCP客户端
        
        Args:
            base_url: MCP API的基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求到MCP API
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            **kwargs: 传递给requests.request的其他参数
            
        Returns:
            API响应的JSON数据
            
        Raises:
            MCPError: 如果API调用失败
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查响应中的业务状态码
            if data.get("code") != 0:
                raise MCPError(f"MCP API调用失败: {data.get('message')}")
                
            return data.get("data", {})
            
        except requests.exceptions.RequestException as e:
            raise MCPError(f"HTTP请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise MCPError(f"响应解析失败: {str(e)}")
    
    def send_message(self, conversationId: int, userId: int, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        发送消息到MCP
        
        Args:
            conversationId: 会话ID
            userId: 用户ID
            messages: 消息列表
            
        Returns:
            API响应数据
        """
        endpoint = "/message/send"
        payload = {
            "conversationId": conversationId,
            "userId": userId,
            "messages": messages
        }
        
        return self._make_request("POST", endpoint, json=payload)
    
    def create_conversation(self, userId: int, model: str, agentIds: Optional[List[int]] = None, 
                           mainAgent: Optional[int] = None, title: Optional[str] = None, 
                           metadata: Optional[Dict[str, Any]] = None, messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        创建新会话
        
        Args:
            userId: 用户ID
            model: 模型名称
            agentIds: 智能体ID列表
            mainAgent: 主智能体ID
            title: 会话标题
            metadata: 会话元数据
            messages: 初始消息列表
            
        Returns:
            API响应数据
        """
        endpoint = "/conversation/create"
        payload = {
            "userId": userId,
            "model": model
        }
        
        if agentIds is not None:
            payload["agentIds"] = agentIds
        if mainAgent is not None:
            payload["mainAgent"] = mainAgent
        if title is not None:
            payload["title"] = title
        if metadata is not None:
            payload["metadata"] = metadata
        if messages is not None:
            payload["messages"] = messages
        
        return self._make_request("POST", endpoint, json=payload)
    
    def update_conversation(self, conversationId: int, userId: int, **kwargs) -> Dict[str, Any]:
        """
        更新会话
        
        Args:
            conversationId: 会话ID
            userId: 用户ID
            **kwargs: 要更新的会话属性
            
        Returns:
            API响应数据
        """
        endpoint = "/conversation/update"
        payload = {
            "conversationId": conversationId,
            "userId": userId
        }
        payload.update(kwargs)
        
        return self._make_request("PUT", endpoint, json=payload)
    
    def get_conversation_list(self, userId: int) -> Dict[str, Any]:
        """
        获取会话列表
        
        Args:
            userId: 用户ID
            
        Returns:
            API响应数据
        """
        endpoint = f"/conversation/list?userId={userId}"
        return self._make_request("GET", endpoint)
    
    def delete_conversation(self, conversationId: int, userId: int) -> Dict[str, Any]:
        """
        删除会话
        
        Args:
            conversationId: 会话ID
            userId: 用户ID
            
        Returns:
            API响应数据
        """
        endpoint = f"/conversation/delete?conversationId={conversationId}&userId={userId}"
        return self._make_request("DELETE", endpoint)
    
    def list_public_agents(self) -> Dict[str, Any]:
        """
        获取公开智能体列表
        
        Returns:
            API响应数据
        """
        endpoint = "/agent/public"
        return self._make_request("GET", endpoint)
    
    def list_user_agents(self, userId: int) -> Dict[str, Any]:
        """
        获取用户关联的智能体列表
        
        Args:
            userId: 用户ID
            
        Returns:
            API响应数据
        """
        endpoint = f"/agent/list?userId={userId}"
        return self._make_request("GET", endpoint)
    
    def connect_client(self, clientId: str, server: Dict[str, Any], initialize: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        建立/替换持久连接
        
        Args:
            clientId: 客户端唯一标识
            server: 服务器配置
            initialize: 初始化操作
            
        Returns:
            API响应数据
        """
        endpoint = "/mcp-client/connect"
        payload = {
            "clientId": clientId,
            "server": server
        }
        
        if initialize is not None:
            payload["initialize"] = initialize
        
        return self._make_request("POST", endpoint, json=payload)
    
    def disconnect_client(self, clientId: str) -> Dict[str, Any]:
        """
        断开持久连接
        
        Args:
            clientId: 客户端唯一标识
            
        Returns:
            API响应数据
        """
        endpoint = f"/mcp-client/{clientId}/disconnect"
        return self._make_request("POST", endpoint)
    
    def execute_mcp_operation(self, clientId: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个MCP操作
        
        Args:
            clientId: 客户端唯一标识
            operation: MCP操作
            
        Returns:
            API响应数据
        """
        endpoint = f"/mcp-client/{clientId}/operation"
        payload = {
            "operation": operation
        }
        
        return self._make_request("POST", endpoint, json=payload)
    
    def execute_mcp_operations(self, clientId: str, operations: List[Dict[str, Any]], continueOnError: bool = False) -> Dict[str, Any]:
        """
        执行多个MCP操作
        
        Args:
            clientId: 客户端唯一标识
            operations: MCP操作列表
            continueOnError: 是否在单个操作失败时继续后续操作
            
        Returns:
            API响应数据
        """
        endpoint = f"/mcp-client/{clientId}/operations"
        payload = {
            "operations": operations,
            "continueOnError": continueOnError
        }
        
        return self._make_request("POST", endpoint, json=payload)
