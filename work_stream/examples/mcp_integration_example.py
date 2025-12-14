#!/usr/bin/env python3
"""
MCP集成示例脚本

这个脚本演示了如何在workstream中使用MCP客户端与智能体进行交互。
"""

import asyncio
from typing import Dict, Any
from manager import AgentManager

async def main():
    """主函数，演示MCP集成功能"""
    print("=== MCP集成示例 ===")
    
    # 1. 初始化智能体管理器，指定MCP API的基础URL
    # 注意：这里的URL应该是MCP服务的实际地址
    mcp_base_url = "http://localhost:3000"
    agent_manager = AgentManager(mcp_base_url)
    
    print(f"1. 初始化AgentManager，连接到MCP服务器: {mcp_base_url}")
    
    # 2. 建立与MCP的持久连接
    try:
        client_id = "workstream-client-001"
        
        # MCP服务器配置
        server_config = {
            "url": "https://mcp.example.com/api",  # 替换为实际的MCP服务地址
            "headers": {
                "Content-Type": "application/json"
            },
            # 如果需要认证，可以添加bearerToken
            # "bearerToken": "your-auth-token",
            "client": {
                "name": "workstream",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": True,
                "prompts": True,
                "resources": True
            }
        }
        
        # 初始化操作（可选）
        initialize = {
            "operations": [
                {
                    "type": "ping"
                },
                {
                    "type": "listTools"
                }
            ]
        }
        
        print(f"2. 建立MCP客户端连接，客户端ID: {client_id}")
        connect_result = agent_manager.connect_mcp_client(client_id, server_config, initialize)
        print(f"   连接成功: {connect_result.get('message', 'Success')}")
        
    except Exception as e:
        print(f"   连接失败: {str(e)}")
        print("   注意：如果MCP服务未运行，这个步骤会失败")
        return
    
    # 3. 注册MCP智能体
    try:
        # 假设MCP服务提供了一个名为"weather_tool"的工具
        agent_name = "mcp_weather_tool"
        agent_manager.register_mcp_agent(
            name=agent_name,
            description="通过MCP调用天气查询工具",
            mcp_client_id=client_id,
            mcp_tool_name="weather_tool",
            dependencies=[]
        )
        
        print(f"3. 注册MCP智能体: {agent_name}")
        
    except Exception as e:
        print(f"   注册失败: {str(e)}")
        return
    
    # 4. 调用MCP智能体
    try:
        print(f"4. 调用MCP智能体: {agent_name}")
        
        # 异步调用示例
        result = await agent_manager.invoke_agent(
            agent_name,
            city="北京",
            date="2024-01-01"
        )
        
        print(f"   调用结果: {result}")
        
    except Exception as e:
        print(f"   调用失败: {str(e)}")
        print("   注意：如果MCP服务未运行或工具不可用，这个步骤会失败")
    
    # 5. 列出所有注册的智能体
    print("5. 列出所有注册的智能体:")
    for agent in agent_manager.list_agents():
        agent_type = "MCP智能体" if agent["is_mcp_agent"] else "本地智能体"
        print(f"   - {agent['name']} ({agent_type}): {agent['description']}")
    
    # 6. 列出所有MCP客户端连接
    print("6. 列出所有MCP客户端连接:")
    for connection in agent_manager.list_mcp_connections():
        print(f"   - {connection['client_id']}: {connection['server_config']['url']}")
    
    # 7. 断开MCP客户端连接
    try:
        print(f"7. 断开MCP客户端连接: {client_id}")
        disconnect_result = agent_manager.disconnect_mcp_client(client_id)
        print(f"   断开成功: {disconnect_result.get('message', 'Success')}")
        
    except Exception as e:
        print(f"   断开失败: {str(e)}")
    
    print("\n=== MCP集成示例结束 ===")

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
