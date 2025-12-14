from typing import Dict, Any, List, Callable, Optional, Union
import asyncio

# 导入MCP客户端
from clients import MCPClient, MCPError


class AgentInfo:
    """智能体信息类，存储智能体的元数据和功能"""
    def __init__(
        self,
        name: str,
        description: str,
        func: Union[Callable, Dict[str, Any]],  # func可以是本地函数或MCP智能体配置
        is_async: bool = False,
        input_schema: Optional[Any] = None,
        output_schema: Optional[Any] = None,
        dependencies: Optional[List[str]] = None,
        is_mcp_agent: bool = False,
        mcp_client_id: Optional[str] = None
    ):
        """
        初始化智能体信息
        
        Args:
            name: 智能体名称
            description: 智能体描述
            func: 智能体执行函数或MCP智能体配置
            is_async: 是否为异步函数
            input_schema: 输入参数模式（可选）
            output_schema: 输出结果模式（可选）
            dependencies: 依赖的其他智能体列表（可选）
            is_mcp_agent: 是否为MCP智能体
            mcp_client_id: MCP客户端ID
        """
        self.name = name
        self.description = description
        self.func = func
        self.is_async = is_async
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.dependencies = dependencies or []
        self.is_mcp_agent = is_mcp_agent
        self.mcp_client_id = mcp_client_id


class AgentManager:
    """智能体管理器，用于统一管理和调用多个智能体"""
    def __init__(self, mcp_base_url: str = "http://localhost:3000"):
        """
        初始化智能体管理器
        
        Args:
            mcp_base_url: MCP API的基础URL
        """
        self.agents: Dict[str, AgentInfo] = {}
        self.mcp_client = MCPClient(mcp_base_url)
        self.mcp_client_connections: Dict[str, Dict[str, Any]] = {}  # 存储MCP客户端连接信息


    def register_agent(
        self,
        name: str,
        description: str,
        func: Callable,
        is_async: bool = False,
        input_schema: Optional[Any] = None,
        output_schema: Optional[Any] = None,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """
        注册一个本地智能体
        
        Args:
            name: 智能体名称（唯一标识符）
            description: 智能体描述
            func: 智能体执行函数
            is_async: 是否为异步函数
            input_schema: 输入参数模式（可选）
            output_schema: 输出结果模式（可选）
            dependencies: 依赖的其他智能体列表（可选）
        """
        if name in self.agents:
            raise ValueError(f"智能体 '{name}' 已存在")
        
        # 验证依赖的智能体是否存在
        for dep in dependencies or []:
            if dep not in self.agents:
                raise ValueError(f"智能体 '{name}' 依赖的智能体 '{dep}' 不存在")
        
        self.agents[name] = AgentInfo(
            name=name,
            description=description,
            func=func,
            is_async=is_async,
            input_schema=input_schema,
            output_schema=output_schema,
            dependencies=dependencies
        )
        
    def register_mcp_agent(
        self,
        name: str,
        description: str,
        mcp_client_id: str,
        mcp_tool_name: str,
        input_schema: Optional[Any] = None,
        output_schema: Optional[Any] = None,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """
        注册一个MCP智能体
        
        Args:
            name: 智能体名称（唯一标识符）
            description: 智能体描述
            mcp_client_id: MCP客户端ID
            mcp_tool_name: MCP工具名称
            input_schema: 输入参数模式（可选）
            output_schema: 输出结果模式（可选）
            dependencies: 依赖的其他智能体列表（可选）
        """
        if name in self.agents:
            raise ValueError(f"智能体 '{name}' 已存在")
        
        # 验证依赖的智能体是否存在
        for dep in dependencies or []:
            if dep not in self.agents:
                raise ValueError(f"智能体 '{name}' 依赖的智能体 '{dep}' 不存在")
        
        # 验证MCP客户端连接是否存在
        if mcp_client_id not in self.mcp_client_connections:
            raise ValueError(f"MCP客户端连接 '{mcp_client_id}' 不存在")
        
        # 创建MCP智能体配置
        mcp_agent_config = {
            "mcp_tool_name": mcp_tool_name,
            "mcp_client_id": mcp_client_id
        }
        
        self.agents[name] = AgentInfo(
            name=name,
            description=description,
            func=mcp_agent_config,
            is_async=True,  # MCP调用始终是异步的
            input_schema=input_schema,
            output_schema=output_schema,
            dependencies=dependencies,
            is_mcp_agent=True,
            mcp_client_id=mcp_client_id
        )
        
    def connect_mcp_client(
        self,
        client_id: str,
        server_config: Dict[str, Any],
        initialize: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        建立/替换与MCP的持久连接
        
        Args:
            client_id: 客户端唯一标识
            server_config: MCP服务器配置
            initialize: 初始化操作（可选）
            
        Returns:
            连接结果
        """
        try:
            # 调用MCP客户端的connect_client方法
            result = self.mcp_client.connect_client(client_id, server_config, initialize)
            
            # 存储连接信息
            self.mcp_client_connections[client_id] = {
                "server_config": server_config,
                "initialize": initialize,
                "connection_info": result.get("connection", {})
            }
            
            return result
        except MCPError as e:
            raise ValueError(f"MCP客户端连接失败: {str(e)}")
    
    def disconnect_mcp_client(self, client_id: str) -> Dict[str, Any]:
        """
        断开与MCP的持久连接
        
        Args:
            client_id: 客户端唯一标识
            
        Returns:
            断开结果
        """
        if client_id not in self.mcp_client_connections:
            raise ValueError(f"MCP客户端连接 '{client_id}' 不存在")
        
        try:
            # 调用MCP客户端的disconnect_client方法
            result = self.mcp_client.disconnect_client(client_id)
            
            # 删除连接信息
            del self.mcp_client_connections[client_id]
            
            return result
        except MCPError as e:
            raise ValueError(f"MCP客户端断开失败: {str(e)}")


    async def invoke_agent(self, name: str, **kwargs) -> Any:
        """
        调用智能体（异步接口）
        
        Args:
            name: 智能体名称
            **kwargs: 智能体执行参数
            
        Returns:
            智能体执行结果
        """
        if name not in self.agents:
            raise ValueError(f"智能体 '{name}' 不存在")
        
        agent_info = self.agents[name]
        
        if agent_info.is_mcp_agent:
            # 调用MCP智能体
            mcp_config = agent_info.func
            mcp_tool_name = mcp_config["mcp_tool_name"]
            mcp_client_id = mcp_config["mcp_client_id"]
            
            try:
                # 构建MCP操作
                operation = {
                    "type": "callTool",
                    "name": mcp_tool_name,
                    "arguments": kwargs
                }
                
                # 执行MCP操作
                result = self.mcp_client.execute_mcp_operation(mcp_client_id, operation)
                return result
            except MCPError as e:
                raise ValueError(f"MCP智能体调用失败: {str(e)}")
        elif agent_info.is_async:
            # 如果是异步函数，直接调用
            return await agent_info.func(**kwargs)
        else:
            # 如果是同步函数，在事件循环中执行
            return await asyncio.to_thread(agent_info.func, **kwargs)

    def invoke_agent_sync(self, name: str, **kwargs) -> Any:
        """
        调用智能体（同步接口）
        
        Args:
            name: 智能体名称
            **kwargs: 智能体执行参数
            
        Returns:
            智能体执行结果
        """
        if name not in self.agents:
            raise ValueError(f"智能体 '{name}' 不存在")
        
        agent_info = self.agents[name]
        
        if agent_info.is_mcp_agent:
            # 调用MCP智能体（同步）
            mcp_config = agent_info.func
            mcp_tool_name = mcp_config["mcp_tool_name"]
            mcp_client_id = mcp_config["mcp_client_id"]
            
            try:
                # 构建MCP操作
                operation = {
                    "type": "callTool",
                    "name": mcp_tool_name,
                    "arguments": kwargs
                }
                
                # 执行MCP操作（同步）
                result = self.mcp_client.execute_mcp_operation(mcp_client_id, operation)
                return result
            except MCPError as e:
                raise ValueError(f"MCP智能体调用失败: {str(e)}")
        elif agent_info.is_async:
            # 如果是异步函数
            try:
                # 检查是否已经有运行中的事件循环
                loop = asyncio.get_running_loop()
                # 如果已经有事件循环，使用create_task和future
                if loop.is_running():
                    # 在运行中的事件循环中，使用asyncio.run_coroutine_threadsafe
                    # 或者使用回调的方式
                    future = asyncio.Future()
                    
                    async def run_in_loop():
                        try:
                            result = await agent_info.func(**kwargs)
                            future.set_result(result)
                        except Exception as e:
                            future.set_exception(e)
                    
                    loop.create_task(run_in_loop())
                    # 注意：在已经运行的事件循环中，我们不能阻塞等待，
                    # 所以这里我们简单地返回future，让调用者自己处理
                    # 或者我们可以使用线程池来运行
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        def run_coro():
                            return asyncio.run(agent_info.func(**kwargs))
                        return executor.submit(run_coro).result()
                else:
                    # 如果事件循环存在但没有运行
                    return loop.run_until_complete(agent_info.func(**kwargs))
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                return asyncio.run(agent_info.func(**kwargs))
        else:
            # 如果是同步函数，直接调用
            return agent_info.func(**kwargs)

    def get_agent_info(self, name: str) -> Optional[AgentInfo]:
        """
        获取智能体信息
        
        Args:
            name: 智能体名称
            
        Returns:
            智能体信息对象，如果不存在返回None
        """
        return self.agents.get(name)

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        列出所有注册的智能体
        
        Returns:
            智能体列表，每个智能体包含名称、描述等信息
        """
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "is_async": agent.is_async,
                "dependencies": agent.dependencies,
                "is_mcp_agent": agent.is_mcp_agent,
                "mcp_client_id": agent.mcp_client_id
            }
            for agent in self.agents.values()
        ]
        
    def list_mcp_connections(self) -> List[Dict[str, Any]]:
        """
        列出所有MCP客户端连接
        
        Returns:
            MCP客户端连接列表
        """
        return [
            {
                "client_id": client_id,
                "server_config": info["server_config"],
                "has_initialize": bool(info["initialize"])
            }
            for client_id, info in self.mcp_client_connections.items()
        ]

# 创建全局智能体管理器实例
agent_manager = AgentManager()
