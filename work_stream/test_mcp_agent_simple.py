from models.workflow_models import WorkflowConfig, NodeConfig, EdgeConfig
from manager.workflow_manager import build_graph_from_config
from manager.agent_manager import agent_manager

async def test_build_workflow_with_mcp_node():
    """测试构建包含MCP Agent节点的工作流"""
    # 首先，建立一个模拟的MCP客户端连接
    try:
        agent_manager.connect_mcp_client(
            client_id="test_client",
            server_config={"base_url": "http://localhost:3000", "api_key": "test_api_key"}
        )
        print("成功建立MCP客户端连接")
    except Exception as e:
        print(f"建立MCP客户端连接失败: {e}")
        return False
    
    # 创建工作流配置，包含一个MCP Agent节点
    # 使用 deepseek agent 提供的 chat 工具
    workflow_config = WorkflowConfig(
        nodes=[
            NodeConfig(id="start_node", type="llm_node"),
            NodeConfig(id="mcp://test_client/chat", type="mcp_agent"),
            NodeConfig(id="end_node", type="handle_chat")
        ],
        edges=[
            EdgeConfig(source="start_node", target="mcp://test_client/chat"),
            EdgeConfig(source="mcp://test_client/chat", target="end_node")
        ]
    )
    
    # 构建工作流
    try:
        workflow = await build_graph_from_config(workflow_config)
        print("成功构建包含MCP Agent节点的工作流")
        print(f"工作流类型: {type(workflow)}")
        return True
    except Exception as e:
        print(f"构建工作流失败: {e}")
        return False
    finally:
        # 断开MCP客户端连接
        try:
            agent_manager.disconnect_mcp_client(client_id="test_client")
            print("成功断开MCP客户端连接")
        except Exception as e:
            print(f"断开MCP客户端连接失败: {e}")

if __name__ == "__main__":
    test_build_workflow_with_mcp_node()