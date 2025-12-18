"""
动态agent端到端集成测试
模拟实际使用场景，测试完整的动态agent集成流程
"""

import asyncio
import json
from fastapi.testclient import TestClient
from app import app
from models.workflow_models import WorkflowConfig, NodeConfig, EdgeConfig, WorkflowExecutionRequest

# 创建测试客户端
client = TestClient(app)


def test_complete_dynamic_agent_workflow():
    """测试完整的动态agent工作流集成流程"""
    
    print("=== 开始动态agent端到端集成测试 ===")
    
    # 步骤1: 发现可用的agent和工具
    print("\n1. 发现可用的agent和工具...")
    response = client.get("/api/agents/discover")
    assert response.status_code == 200
    discovery_data = response.json()
    
    print(f"发现 {len(discovery_data['agents'])} 个agent")
    print(f"发现 {len(discovery_data['mcp_tools'])} 组MCP工具")
    
    # 步骤2: 创建动态agent节点配置
    print("\n2. 创建动态agent节点配置...")
    
    # 假设我们使用deepseek agent的chat工具
    node_request = {
        "client_id": "test_client",
        "tool_name": "chat",
        "parameters": {
            "message": "Hello, this is a test message from dynamic agent workflow!"
        }
    }
    
    response = client.post("/api/nodes/dynamic-agent", json=node_request)
    assert response.status_code == 200
    node_config = response.json()
    
    print(f"创建的节点配置: {json.dumps(node_config, indent=2, ensure_ascii=False)}")
    
    # 步骤3: 构建包含动态agent节点的工作流
    print("\n3. 构建包含动态agent节点的工作流...")
    
    workflow_config = WorkflowConfig(
        nodes=[
            NodeConfig(id="input_processing", type="llm_node"),
            NodeConfig(
                id=node_config["id"],
                type="dynamic_agent",
                client_id=node_config["client_id"],
                tool_name=node_config["tool_name"],
                parameters=node_config["parameters"]
            ),
            NodeConfig(id="output_processing", type="uppercase_node")
        ],
        edges=[
            EdgeConfig(source="START", target="input_processing"),
            EdgeConfig(source="input_processing", target=node_config["id"]),
            EdgeConfig(source=node_config["id"], target="output_processing"),
            EdgeConfig(source="output_processing", target="END")
        ]
    )
    
    # 步骤4: 验证工作流配置
    print("\n4. 验证工作流配置...")
    response = client.post("/api/workflows/validate", json=workflow_config.model_dump())
    assert response.status_code == 200
    print("✓ 工作流配置验证通过")
    
    # 步骤5: 执行工作流（需要MCP客户端连接）
    print("\n5. 准备执行工作流...")
    
    # 注意：实际执行需要MCP客户端连接到plug-in-server
    # 这里我们只测试配置和验证，实际执行需要服务器运行
    
    execution_request = WorkflowExecutionRequest(
        workflow_config=workflow_config,
        initial_state={
            "messages": [("user", "Test message for dynamic agent workflow")],
            "context": {
                "params": {
                    "additional_param": "test_value"
                }
            }
        }
    )
    
    print("工作流执行配置已准备完成")
    print("注意：实际执行需要plug-in-server运行并提供MCP客户端连接")
    
    # 步骤6: 测试MCP客户端连接（可选）
    print("\n6. 测试MCP客户端连接...")
    
    try:
        connect_request = {
            "client_id": "e2e_test_client",
            "server_config": {
                "url": "http://localhost:3000",
                "headers": {},
                "bearerToken": ""
            }
        }
        
        response = client.post("/api/mcp/clients/connect", json=connect_request)
        if response.status_code == 200:
            print("✓ MCP客户端连接成功")
            
            # 列出已连接的客户端
            response = client.get("/api/mcp/clients")
            clients = response.json()
            print(f"当前连接的MCP客户端: {json.dumps(clients, indent=2, ensure_ascii=False)}")
        else:
            print("⚠ MCP客户端连接失败（可能plug-in-server未运行）")
            print(f"错误信息: {response.json()}")
            
    except Exception as e:
        print(f"⚠ MCP客户端连接测试异常: {e}")
    
    print("\n=== 动态agent端到端集成测试完成 ===")
    print("\n总结:")
    print("- Agent和工具发现功能正常")
    print("- 动态agent节点创建功能正常") 
    print("- 工作流配置验证功能正常")
    print("- 集成架构已准备就绪")
    print("\n下一步: 启动plug-in-server并测试实际执行")


def test_dynamic_agent_with_sensor_tools():
    """测试使用sensor agent工具的动态agent集成"""
    
    print("\n=== 测试Sensor Agent工具集成 ===")
    
    # 创建使用sensor工具的动态agent节点
    sensor_node_request = {
        "client_id": "sensor_client",
        "tool_name": "getSensorData",
        "parameters": {
            "uuid": "test_sensor_uuid",
            "sensor": "temperature"
        }
    }
    
    response = client.post("/api/nodes/dynamic-agent", json=sensor_node_request)
    assert response.status_code == 200
    sensor_node_config = response.json()
    
    print(f"Sensor Agent节点配置: {json.dumps(sensor_node_config, indent=2, ensure_ascii=False)}")
    
    # 构建传感器数据获取工作流
    sensor_workflow = WorkflowConfig(
        nodes=[
            NodeConfig(id="sensor_query", type="llm_node"),
            NodeConfig(
                id=sensor_node_config["id"],
                type="dynamic_agent",
                client_id=sensor_node_config["client_id"],
                tool_name=sensor_node_config["tool_name"],
                parameters=sensor_node_config["parameters"]
            )
        ],
        edges=[
            EdgeConfig(source="START", target="sensor_query"),
            EdgeConfig(source="sensor_query", target=sensor_node_config["id"]),
            EdgeConfig(source=sensor_node_config["id"], target="END")
        ]
    )
    
    # 验证工作流
    response = client.post("/api/workflows/validate", json=sensor_workflow.model_dump())
    assert response.status_code == 200
    print("✓ Sensor Agent工作流验证通过")
    
    print("\n=== Sensor Agent工具集成测试完成 ===")


def test_dynamic_agent_discovery_api():
    """测试动态agent发现API的详细功能"""
    
    print("\n=== 测试动态agent发现API ===")
    
    # 测试发现API
    response = client.get("/api/agents/discover")
    assert response.status_code == 200
    data = response.json()
    
    # 分析返回的数据结构
    print("发现API返回数据结构:")
    print(f"- Agents数量: {len(data['agents'])}")
    print(f"- MCP工具组数量: {len(data['mcp_tools'])}")
    
    # 显示发现的agent信息
    if data['agents']:
        print("\n发现的Agent:")
        for agent in data['agents']:
            print(f"  - ID: {agent.get('id', 'N/A')}, Name: {agent.get('name', 'N/A')}")
    
    # 显示发现的MCP工具
    if data['mcp_tools']:
        print("\n发现的MCP工具:")
        for agent_name, tools in data['mcp_tools'].items():
            print(f"  - {agent_name}:")
            for tool in tools:
                print(f"    - {tool.get('name', 'N/A')}: {tool.get('description', 'No description')}")
    
    print("\n=== 动态agent发现API测试完成 ===")


if __name__ == "__main__":
    print("运行动态agent端到端集成测试...\n")
    
    try:
        test_complete_dynamic_agent_workflow()
    except Exception as e:
        print(f"端到端测试失败: {e}")
    
    try:
        test_dynamic_agent_with_sensor_tools()
    except Exception as e:
        print(f"Sensor工具测试失败: {e}")
    
    try:
        test_dynamic_agent_discovery_api()
    except Exception as e:
        print(f"发现API测试失败: {e}")
    
    print("\n所有测试执行完成！")