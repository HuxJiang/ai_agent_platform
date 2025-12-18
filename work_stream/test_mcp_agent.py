import asyncio
from fastapi.testclient import TestClient
from app import app
from models.workflow_models import WorkflowConfig, NodeConfig, EdgeConfig
from manager.workflow_manager import build_graph_from_config

# 创建测试客户端
client = TestClient(app)

async def test_mcp_agent_node():
    """测试动态创建的MCP Agent节点"""
    # 首先，建立一个MCP客户端连接
    mcp_server_config = {
        "base_url": "http://plugin-server:3000",
        "api_key": "test_api_key"
    }
    
    connect_response = client.post(
        "/mcp/connect",
        json={
            "client_id": "1",
            "server_config": mcp_server_config
        }
    )
    print("连接MCP客户端响应:", connect_response.json())
    
    # 创建工作流配置，包含一个MCP Agent节点
    workflow_config = WorkflowConfig(
        nodes=[
            NodeConfig(id="start_node", type="llm_node"),
            NodeConfig(id="mcp://1/weather_tool", type="mcp_agent"),
            NodeConfig(id="end_node", type="handle_chat")
        ],
        edges=[
            EdgeConfig(source="START", target="start_node"),
            EdgeConfig(source="start_node", target="mcp://1/weather_tool"),
            EdgeConfig(source="mcp://1/weather_tool", target="end_node"),   
            EdgeConfig(source="end_node", target="END")
        ]
    )
    
    # 构建工作流
    try:
        workflow = await build_graph_from_config(workflow_config)
        print("工作流构建成功!")
        
        # 测试执行工作流
        initial_state = {
            "messages": [],
            "context": {
                "params": {
                    "city": "北京",
                    "date": "2024-07-15"
                }
            },
            "intent": "weather"
        }
        
        result = await workflow.ainvoke(initial_state)
        print("工作流执行结果:", result)
        
    except Exception as e:
        print("工作流构建或执行失败:", str(e))
    
    # 断开MCP客户端连接
    disconnect_response = client.post(
        "/mcp/disconnect",
        json={"client_id": "test_client"}
    )
    print("断开MCP客户端响应:", disconnect_response.json())

if __name__ == "__main__":
    asyncio.run(test_mcp_agent_node())