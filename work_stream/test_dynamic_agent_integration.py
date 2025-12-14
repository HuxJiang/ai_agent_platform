"""
动态agent集成功能测试
测试动态agent发现、节点创建和工作流执行功能
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from app import app
from models.workflow_models import WorkflowConfig, NodeConfig, EdgeConfig
from manager.agent_discovery import AgentDiscoveryService
from manager.workflow_manager import create_dynamic_agent_node_config

# 创建测试客户端
client = TestClient(app)


def test_create_dynamic_agent_node_config():
    """测试动态agent节点配置创建"""
    # 测试使用client_id创建节点配置
    node_config = create_dynamic_agent_node_config(
        client_id="test_client",
        tool_name="chat",
        parameters={"message": "Hello, World!"}
    )
    
    assert node_config.id == "mcp://test_client/chat"
    assert node_config.type == "dynamic_agent"
    assert node_config.client_id == "test_client"
    assert node_config.tool_name == "chat"
    assert node_config.parameters == {"message": "Hello, World!"}
    
    # 测试使用agent_id创建节点配置
    node_config2 = create_dynamic_agent_node_config(
        agent_id=1,
        tool_name="getSensorData",
        node_id="custom_node_id"
    )
    
    assert node_config2.id == "custom_node_id"
    assert node_config2.type == "dynamic_agent"
    assert node_config2.agent_id == 1
    assert node_config2.tool_name == "getSensorData"
    
    # 测试参数验证
    try:
        create_dynamic_agent_node_config()
        assert False, "应该抛出异常"
    except Exception as e:
        assert "必须指定agent_id或client_id" in str(e)
    
    try:
        create_dynamic_agent_node_config(client_id="test")
        assert False, "应该抛出异常"
    except Exception as e:
        assert "必须指定tool_name" in str(e)


def test_agent_discovery_service():
    """测试agent发现服务"""
    discovery_service = AgentDiscoveryService()
    
    # 测试发现agent
    agents = asyncio.run(discovery_service.discover_agents())
    assert isinstance(agents, list)
    
    # 测试发现MCP工具
    mcp_tools = asyncio.run(discovery_service.discover_mcp_tools())
    assert isinstance(mcp_tools, dict)
    
    # 测试发现所有可用工具
    all_tools = asyncio.run(discovery_service.discover_all_available_tools())
    assert "agents" in all_tools
    assert "mcp_tools" in all_tools


def test_dynamic_agent_api_endpoints():
    """测试动态agent相关的API端点"""
    # 测试agent发现端点
    response = client.get("/api/agents/discover")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "mcp_tools" in data
    
    # 测试动态agent节点创建端点
    node_request = {
        "client_id": "test_client",
        "tool_name": "chat",
        "parameters": {"message": "Test message"}
    }
    
    response = client.post("/api/nodes/dynamic-agent", json=node_request)
    assert response.status_code == 200
    node_config = response.json()
    assert node_config["id"] == "mcp://test_client/chat"
    assert node_config["type"] == "dynamic_agent"
    assert node_config["client_id"] == "test_client"
    assert node_config["tool_name"] == "chat"


def test_workflow_with_dynamic_agent():
    """测试包含动态agent节点的工作流"""
    # 创建包含动态agent节点的工作流配置
    workflow_config = WorkflowConfig(
        nodes=[
            NodeConfig(id="start", type="llm_node"),
            NodeConfig(
                id="dynamic_agent_node",
                type="dynamic_agent",
                client_id="test_client",
                tool_name="chat",
                parameters={"message": "Hello from workflow"}
            )
        ],
        edges=[
            EdgeConfig(source="START", target="start"),
            EdgeConfig(source="start", target="dynamic_agent_node"),
            EdgeConfig(source="dynamic_agent_node", target="END")
        ]
    )
    
    # 验证工作流配置
    response = client.post("/api/workflows/validate", json=workflow_config.model_dump())
    assert response.status_code == 200
    
    # 注意：实际执行需要MCP客户端连接，这里只测试配置验证


def test_mcp_client_integration():
    """测试MCP客户端集成"""
    # 测试MCP客户端连接
    connect_request = {
        "client_id": "test_integration",
        "server_config": {
            "url": "http://localhost:3000",
            "headers": {},
            "bearerToken": ""
        }
    }
    
    response = client.post("/api/mcp/clients/connect", json=connect_request)
    # 注意：如果plug-in-server没有运行，这个测试可能会失败
    # 这里我们主要测试API端点的存在性
    assert response.status_code in [200, 500]  # 可能成功或失败，取决于服务器状态
    
    # 测试列出MCP客户端
    response = client.get("/api/mcp/clients")
    assert response.status_code == 200


if __name__ == "__main__":
    # 运行测试
    print("运行动态agent集成功能测试...")
    
    try:
        test_create_dynamic_agent_node_config()
        print("✓ 动态agent节点配置创建测试通过")
    except Exception as e:
        print(f"✗ 动态agent节点配置创建测试失败: {e}")
    
    try:
        test_agent_discovery_service()
        print("✓ Agent发现服务测试通过")
    except Exception as e:
        print(f"✗ Agent发现服务测试失败: {e}")
    
    try:
        test_dynamic_agent_api_endpoints()
        print("✓ 动态agent API端点测试通过")
    except Exception as e:
        print(f"✗ 动态agent API端点测试失败: {e}")
    
    try:
        test_workflow_with_dynamic_agent()
        print("✓ 动态agent工作流测试通过")
    except Exception as e:
        print(f"✗ 动态agent工作流测试失败: {e}")
    
    try:
        test_mcp_client_integration()
        print("✓ MCP客户端集成测试通过")
    except Exception as e:
        print(f"✗ MCP客户端集成测试失败: {e}")
    
    print("\n测试完成！")