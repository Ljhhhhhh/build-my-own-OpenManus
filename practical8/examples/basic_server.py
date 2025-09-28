"""
基础MCP服务器使用示例

这个示例展示了如何创建和使用MCP服务器和客户端。

对于JavaScript开发者的说明：
- 这里展示了完整的MCP服务器-客户端通信流程
- 使用了Python的asyncio.create_task，类似于JavaScript的Promise.resolve()
- 演示了如何在同一个程序中运行服务器和客户端（通常它们在不同进程中）
"""

import asyncio
import sys
import os
import tempfile
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.client import MCPClient
from utils.logger import setup_logging


async def run_server_subprocess():
    """
    在子进程中运行MCP服务器
    
    Returns:
        subprocess.Popen: 服务器进程
    
    类似于JavaScript中的:
    function runServerSubprocess(): ChildProcess {
        const serverScript = path.join(__dirname, '..', 'servers', 'calculator_server.py');
        return spawn('python', [serverScript], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
    }
    """
    server_script = project_root / "servers" / "calculator_server.py"
    
    # 启动服务器进程
    process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    return process


async def demo_basic_usage():
    """
    演示基础MCP使用
    
    类似于JavaScript中的:
    async function demoBasicUsage(): Promise<void> {
        const logger = setupLogging();
        logger.info("Starting MCP Basic Usage Demo");
        
        // 创建客户端
        const client = new MCPClient();
        
        try {
            // 添加服务器
            const serverCommand = ['python', 'servers/calculator_server.py'];
            const connected = await client.addServer('calculator', serverCommand);
            
            if (!connected) {
                throw new Error("Failed to connect to calculator server");
            }
            
            // 列出工具
            const tools = await client.listAllTools();
            logger.info("Available tools:", tools);
            
            // 调用工具
            const result = await client.callTool('calculator', 'calculator', {
                expression: '2 + 3 * 4'
            });
            logger.info("Calculation result:", result);
            
        } finally {
            await client.disconnectAll();
        }
    }
    """
    logger = setup_logging(log_level="INFO")
    logger.info("=== MCP Basic Usage Demo ===")
    
    # 创建MCP客户端
    client = MCPClient()
    
    try:
        # 添加计算器服务器
        server_command = [sys.executable, str(project_root / "servers" / "calculator_server.py")]
        logger.info(f"Connecting to calculator server: {' '.join(server_command)}")
        
        connected = await client.add_server("calculator", server_command)
        
        if not connected:
            logger.error("Failed to connect to calculator server")
            return
        
        logger.info("✅ Successfully connected to calculator server")
        
        # 等待一下确保连接稳定
        await asyncio.sleep(1)
        
        # 获取客户端状态
        status = client.get_status()
        logger.info(f"Client status: {status}")
        
        # 列出所有可用工具
        logger.info("📋 Listing available tools...")
        all_tools = await client.list_all_tools()
        
        for server_name, tools in all_tools.items():
            logger.info(f"Server '{server_name}' has {len(tools)} tools:")
            for tool in tools:
                logger.info(f"  - {tool['name']}: {tool['description']}")
        
        # 演示基础计算
        logger.info("🧮 Testing basic calculator...")
        
        test_expressions = [
            "2 + 3",
            "10 * 5 - 3",
            "sqrt(16)",
            "sin(pi/2)",
            "2**8"
        ]
        
        for expression in test_expressions:
            try:
                result = await client.call_tool("calculator", "calculator", {
                    "expression": expression
                })
                
                if result and "content" in result:
                    content = result["content"][0]["text"] if result["content"] else "No result"
                    logger.info(f"  {expression} = {content}")
                else:
                    logger.info(f"  {expression} = {result}")
                    
            except Exception as e:
                logger.error(f"  {expression} -> Error: {e}")
        
        # 演示高级计算器
        logger.info("📊 Testing advanced calculator...")
        
        # 统计计算
        try:
            stats_result = await client.call_tool("calculator", "advanced_calculator", {
                "operation": "statistics",
                "data": {
                    "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                }
            })
            
            if stats_result and "content" in stats_result:
                logger.info(f"Statistics result: {stats_result['content'][0]['text']}")
            else:
                logger.info(f"Statistics result: {stats_result}")
                
        except Exception as e:
            logger.error(f"Statistics calculation error: {e}")
        
        # 数列计算
        try:
            sequence_result = await client.call_tool("calculator", "advanced_calculator", {
                "operation": "sequence",
                "data": {
                    "type": "fibonacci",
                    "count": 10
                }
            })
            
            if sequence_result and "content" in sequence_result:
                logger.info(f"Fibonacci sequence: {sequence_result['content'][0]['text']}")
            else:
                logger.info(f"Fibonacci sequence: {sequence_result}")
                
        except Exception as e:
            logger.error(f"Sequence calculation error: {e}")
        
        logger.info("✅ Demo completed successfully!")
    
    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        logger.info("🧹 Cleaning up...")
        await client.disconnect_all()
        logger.info("Demo finished")


async def demo_error_handling():
    """
    演示错误处理
    
    类似于JavaScript中的:
    async function demoErrorHandling(): Promise<void> {
        const logger = setupLogging();
        logger.info("Testing error handling...");
        
        const client = new MCPClient();
        
        try {
            // 测试连接不存在的服务器
            const connected = await client.addServer('nonexistent', ['nonexistent-command']);
            logger.info(`Connection result: ${connected}`);
            
            // 测试调用不存在的工具
            try {
                await client.callTool('calculator', 'nonexistent_tool', {});
            } catch (error) {
                logger.info(`Expected error: ${error.message}`);
            }
            
        } finally {
            await client.disconnectAll();
        }
    }
    """
    logger = setup_logging(log_level="INFO")
    logger.info("=== Error Handling Demo ===")
    
    client = MCPClient()
    
    try:
        # 测试1: 连接不存在的服务器
        logger.info("🔍 Testing connection to non-existent server...")
        try:
            connected = await client.add_server("nonexistent", ["nonexistent-command"])
            logger.info(f"Connection result: {connected}")
        except Exception as e:
            logger.info(f"Expected connection error: {e}")
        
        # 测试2: 连接到真实服务器，然后测试错误情况
        server_command = [sys.executable, str(project_root / "servers" / "calculator_server.py")]
        connected = await client.add_server("calculator", server_command)
        
        if connected:
            logger.info("✅ Connected to calculator server for error testing")
            
            # 测试调用不存在的工具
            logger.info("🔍 Testing call to non-existent tool...")
            try:
                await client.call_tool("calculator", "nonexistent_tool", {})
            except Exception as e:
                logger.info(f"Expected tool error: {e}")
            
            # 测试无效参数
            logger.info("🔍 Testing invalid parameters...")
            try:
                await client.call_tool("calculator", "calculator", {})  # 缺少expression参数
            except Exception as e:
                logger.info(f"Expected parameter error: {e}")
            
            # 测试无效表达式
            logger.info("🔍 Testing invalid expression...")
            try:
                await client.call_tool("calculator", "calculator", {
                    "expression": "invalid_function(123)"
                })
            except Exception as e:
                logger.info(f"Expected expression error: {e}")
        
        logger.info("✅ Error handling demo completed!")
    
    except Exception as e:
        logger.error(f"Unexpected error in error handling demo: {e}")
    
    finally:
        await client.disconnect_all()


async def main():
    """
    主函数 - 运行所有演示
    
    类似于JavaScript中的:
    async function main(): Promise<void> {
        console.log("Starting MCP Examples...");
        
        try {
            await demoBasicUsage();
            await demoErrorHandling();
        } catch (error) {
            console.error("Demo failed:", error);
        }
        
        console.log("All demos completed!");
    }
    """
    print("🚀 Starting MCP Examples...")
    print("=" * 50)
    
    try:
        # 运行基础使用演示
        await demo_basic_usage()
        
        print("\n" + "=" * 50)
        
        # 运行错误处理演示
        await demo_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All demos completed successfully!")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    程序入口点
    
    类似于JavaScript中的:
    if (require.main === module) {
        main().catch((error) => {
            console.error("Fatal error:", error);
            process.exit(1);
        });
    }
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)