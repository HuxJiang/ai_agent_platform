"""
动态agent集成测试启动脚本
用于测试完整的动态agent集成功能
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, cwd=cwd, shell=shell, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_server_health(url, timeout=30):
    """检查服务器健康状态"""
    import requests
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False

def main():
    print("=== 动态agent集成测试启动脚本 ===\n")
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    plug_in_server_dir = project_root.parent / "plug-in-server"
    work_stream_dir = project_root
    
    print(f"项目根目录: {project_root}")
    print(f"plug-in-server目录: {plug_in_server_dir}")
    print(f"work-stream目录: {work_stream_dir}")
    
    # 检查目录是否存在
    if not plug_in_server_dir.exists():
        print("❌ plug-in-server目录不存在")
        return
    
    if not work_stream_dir.exists():
        print("❌ work-stream目录不存在")
        return
    
    # 步骤1: 检查plug-in-server依赖
    print("\n1. 检查plug-in-server依赖...")
    returncode, stdout, stderr = run_command("npm list", cwd=plug_in_server_dir)
    if returncode != 0:
        print("⚠ plug-in-server依赖可能未安装，尝试安装...")
        returncode, stdout, stderr = run_command("npm install", cwd=plug_in_server_dir)
        if returncode == 0:
            print("✓ plug-in-server依赖安装成功")
        else:
            print(f"❌ plug-in-server依赖安装失败: {stderr}")
    else:
        print("✓ plug-in-server依赖已安装")
    
    # 步骤2: 检查work-stream依赖
    print("\n2. 检查work-stream依赖...")
    returncode, stdout, stderr = run_command("pip list", cwd=work_stream_dir)
    if returncode != 0:
        print("⚠ work-stream依赖可能未安装，尝试安装...")
        returncode, stdout, stderr = run_command("pip install -r requirements.txt", cwd=work_stream_dir)
        if returncode == 0:
            print("✓ work-stream依赖安装成功")
        else:
            print(f"❌ work-stream依赖安装失败: {stderr}")
    else:
        print("✓ work-stream依赖已安装")
    
    # 步骤3: 启动plug-in-server
    print("\n3. 启动plug-in-server...")
    
    # 检查是否已运行
    returncode, stdout, stderr = run_command("netstat -an | findstr :3000", shell=True)
    if "3000" in stdout:
        print("✓ plug-in-server已在端口3000运行")
        plug_in_server_running = True
    else:
        print("启动plug-in-server...")
        # 使用非阻塞方式启动
        plug_in_server_process = subprocess.Popen(
            ["npm", "start"],
            cwd=plug_in_server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("等待plug-in-server启动...")
        time.sleep(5)
        
        # 检查是否启动成功
        if plug_in_server_process.poll() is None:
            print("✓ plug-in-server启动成功")
            plug_in_server_running = True
        else:
            print("❌ plug-in-server启动失败")
            plug_in_server_running = False
    
    # 步骤4: 启动work-stream
    print("\n4. 启动work-stream...")
    
    # 检查是否已运行
    returncode, stdout, stderr = run_command("netstat -an | findstr :8000", shell=True)
    if "8000" in stdout:
        print("✓ work-stream已在端口8000运行")
        work_stream_running = True
    else:
        print("启动work-stream...")
        # 使用非阻塞方式启动
        work_stream_process = subprocess.Popen(
            ["python", "app.py"],
            cwd=work_stream_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("等待work-stream启动...")
        time.sleep(3)
        
        # 检查是否启动成功
        if work_stream_process.poll() is None:
            print("✓ work-stream启动成功")
            work_stream_running = True
        else:
            print("❌ work-stream启动失败")
            work_stream_running = False
    
    # 步骤5: 运行集成测试
    print("\n5. 运行集成测试...")
    
    if plug_in_server_running and work_stream_running:
        print("运行端到端集成测试...")
        returncode, stdout, stderr = run_command(
            "python test_dynamic_agent_e2e.py",
            cwd=work_stream_dir
        )
        
        if returncode == 0:
            print("\n✓ 集成测试执行成功")
            print("测试输出:")
            print(stdout)
        else:
            print("\n❌ 集成测试执行失败")
            print("错误信息:")
            print(stderr)
    else:
        print("❌ 无法运行集成测试，服务器未完全启动")
    
    # 步骤6: 提供测试API端点
    print("\n6. 测试API端点信息:")
    print("   - Agent发现API: GET http://localhost:8000/api/agents/discover")
    print("   - 动态节点创建: POST http://localhost:8000/api/nodes/dynamic-agent")
    print("   - MCP客户端连接: POST http://localhost:8000/api/mcp/clients/connect")
    print("   - 工作流验证: POST http://localhost:8000/api/workflows/validate")
    print("   - 工作流执行: POST http://localhost:8000/api/workflows/execute")
    
    print("\n=== 动态agent集成测试启动脚本完成 ===")
    print("\n下一步操作:")
    print("1. 手动测试API端点")
    print("2. 构建包含动态agent节点的工作流")
    print("3. 执行工作流验证功能")

if __name__ == "__main__":
    main()