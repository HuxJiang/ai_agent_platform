"""
Agent和MCP工具发现服务
用于动态发现plug-in-service提供的agent和MCP工具
"""
import httpx
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

class AgentDiscoveryService:
    """Agent和MCP工具发现服务"""
    
    def __init__(self, plugin_server_url: str = "http://localhost:3000"):
        self.plugin_server_url = plugin_server_url
        self.client = httpx.AsyncClient()
    
    async def discover_agents(self) -> List[Dict[str, Any]]:
        """
        发现所有可用的agent
        
        Returns:
            List[Dict]: agent列表，包含id、name、category等信息
        """
        try:
            # 获取公开agent列表
            response = await self.client.get(f"{self.plugin_server_url}/agent/public")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("agents", [])
            else:
                raise HTTPException(response.status_code, f"获取agent列表失败: {response.text}")
        except Exception as e:
            raise HTTPException(500, f"发现agent失败: {str(e)}")
    
    async def discover_mcp_tools(self, client_id: str) -> List[Dict[str, Any]]:
        """
        发现指定MCP客户端的所有可用工具
        
        Args:
            client_id: MCP客户端ID
            
        Returns:
            List[Dict]: 工具列表，包含name、description、inputSchema等信息
        """
        try:
            # 执行listTools操作
            operation = {
                "type": "listTools"
            }
            
            response = await self.client.post(
                f"{self.plugin_server_url}/mcp-client/{client_id}/operation",
                json={"operation": operation}
            )
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("data", {}).get("result", {}).get("tools", [])
                return tools
            else:
                raise HTTPException(response.status_code, f"获取MCP工具列表失败: {response.text}")
        except Exception as e:
            raise HTTPException(500, f"发现MCP工具失败: {str(e)}")
    
    async def get_agent_tools(self, agent_id: int) -> List[Dict[str, Any]]:
        """
        获取指定agent的所有可用工具
        
        Args:
            agent_id: agent ID
            
        Returns:
            List[Dict]: 工具列表
        """
        # 这里需要根据agent的具体实现来获取工具
        # 目前假设每个agent都通过MCP客户端提供工具
        try:
            # 首先尝试连接到agent对应的MCP客户端
            client_id = f"agent_{agent_id}"
            
            # 这里需要根据agent的类型和配置来构建MCP连接
            # 暂时返回空列表，实际实现需要根据agent配置来连接
            return []
        except Exception as e:
            raise HTTPException(500, f"获取agent工具失败: {str(e)}")
    
    async def discover_all_available_tools(self) -> Dict[str, Any]:
        """
        发现所有可用的工具（包括agent工具和MCP工具）
        
        Returns:
            Dict: 包含agents和mcp_tools的工具字典
        """
        try:
            agents = await self.discover_agents()
            
            # 获取所有已连接的MCP客户端
            response = await self.client.get(f"{self.plugin_server_url}/mcp-client")
            mcp_clients = []
            
            if response.status_code == 200:
                data = response.json()
                mcp_clients = data.get("data", {}).get("clients", [])
            
            # 为每个MCP客户端获取工具
            mcp_tools = {}
            for client in mcp_clients:
                if client.get("connected"):
                    client_id = client.get("clientId")
                    try:
                        tools = await self.discover_mcp_tools(client_id)
                        mcp_tools[client_id] = {
                            "client_id": client_id,
                            "tools": tools
                        }
                    except Exception as e:
                        print(f"获取MCP客户端 {client_id} 的工具失败: {e}")
            
            return {
                "agents": agents,
                "mcp_tools": mcp_tools
            }
        except Exception as e:
            raise HTTPException(500, f"发现所有可用工具失败: {str(e)}")
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

# 全局agent发现服务实例
# 在Docker环境中使用容器名，本地开发使用localhost
import os
plugin_server_host = os.getenv("PLUGIN_SERVER_URL")
if not plugin_server_host:
    # 检查是否在Docker环境中（通过检查环境变量或文件系统）
    if os.path.exists("/.dockerenv"):
        plugin_server_host = "http://plugin-server:3000"
    else:
        plugin_server_host = "http://localhost:3000"

agent_discovery_service = AgentDiscoveryService(plugin_server_url=plugin_server_host)