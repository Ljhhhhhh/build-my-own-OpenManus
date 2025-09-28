"""
MCP系统完整演示程序

这个程序展示了完整的MCP（模型通信协议）系统，包括：
- 服务器启动和工具注册
- 客户端连接和工具调用
- 错误处理和资源管理
- 实际使用场景演示

对于JavaScript开发者的说明：
- 这是一个完整的演示程序，类似于Node.js的demo应用
- 展示了异步编程的最佳实践
- 包含了完整的错误处理和资源清理
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp.client import MCPClient, MCPClientError
from utils.logger import setup_logging
from utils.config import get_config


class MCPDemo:
    """
    MCP演示类
    
    封装了所有演示功能，提供清晰的演示流程
    
    类似于JavaScript中的:
    class MCPDemo {
        private client: MCPClient;
        private logger: Logger;
        
        constructor() {
            this.client = new MCPClient();
            this.logger = setupLogging();
        }
        
        async runDemo(): Promise<void> {
            // 演示逻辑
        }
    }
    """
    
    def __init__(self):
        """初始化演示"""
        self.client = MCPClient()
        self.logger = setup_logging(log_level="INFO")
        self.config = get_config()
        
        # 演示统计
        self.stats = {
            "servers_connected": 0,
            "tools_discovered": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def run_complete_demo(self):
        """
        运行完整演示
        
        类似于JavaScript中的:
        async runCompleteDemo(): Promise<void> {
            this.logger.info("🚀 Starting Complete MCP Demo");
            this.stats.start_time = Date.now();
            
            try {
                await this.setupServers();
                await this.discoverTools();
                await this.demonstrateCalculations();
                await this.demonstrateErrorHandling();
                await this.showPerformanceMetrics();
            } finally {
                await this.cleanup();
                this.stats.end_time = Date.now();
                this.showFinalStats();
            }
        }
        """
        self.logger.info("🚀 Starting Complete MCP System Demo")
        self.logger.info("=" * 60)
        self.stats["start_time"] = time.time()
        
        try:
            # 1. 设置服务器连接
            await self._setup_servers()
            
            # 2. 发现可用工具
            await self._discover_tools()
            
            # 3. 演示计算功能
            await self._demonstrate_calculations()
            
            # 4. 演示高级功能
            await self._demonstrate_advanced_features()
            
            # 5. 演示错误处理
            await self._demonstrate_error_handling()
            
            # 6. 性能测试
            await self._performance_test()
            
        except Exception as e:
            self.logger.error(f"Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理资源
            await self._cleanup()
            self.stats["end_time"] = time.time()
            self._show_final_stats()
    
    async def _setup_servers(self):
        """设置MCP服务器连接"""
        self.logger.info("🔧 Setting up MCP servers...")
        
        # 计算器服务器
        calculator_command = [
            sys.executable,
            str(project_root / "servers" / "calculator_server.py")
        ]
        
        try:
            connected = await self.client.add_server("calculator", calculator_command)
            if connected:
                self.stats["servers_connected"] += 1
                self.logger.info("✅ Calculator server connected")
            else:
                self.logger.error("❌ Failed to connect calculator server")
        except Exception as e:
            self.logger.error(f"❌ Calculator server connection error: {e}")
        
        # 等待连接稳定
        await asyncio.sleep(1)
        
        # 显示连接状态
        status = self.client.get_status()
        self.logger.info(f"📊 Client status: {status['servers_count']} servers, "
                        f"{len(status['connected_servers'])} connected")
    
    async def _discover_tools(self):
        """发现可用工具"""
        self.logger.info("🔍 Discovering available tools...")
        
        try:
            all_tools = await self.client.list_all_tools()
            
            for server_name, tools in all_tools.items():
                self.logger.info(f"📋 Server '{server_name}' provides {len(tools)} tools:")
                
                for tool in tools:
                    self.stats["tools_discovered"] += 1
                    self.logger.info(f"  🔧 {tool['name']}: {tool['description']}")
                    
                    # 显示工具参数
                    if tool.get('parameters'):
                        for param in tool['parameters']:
                            required = "required" if param.get('required', False) else "optional"
                            self.logger.info(f"    - {param['name']} ({param['type']}, {required}): {param['description']}")
        
        except Exception as e:
            self.logger.error(f"Tool discovery error: {e}")
    
    async def _demonstrate_calculations(self):
        """演示基础计算功能"""
        self.logger.info("🧮 Demonstrating basic calculations...")
        
        test_cases = [
            ("Basic arithmetic", "2 + 3 * 4"),
            ("Square root", "sqrt(144)"),
            ("Trigonometry", "sin(pi/2)"),
            ("Logarithm", "log(100, 10)"),
            ("Power", "2**10"),
            ("Complex expression", "(3 + 4) * (5 - 2) / sqrt(9)")
        ]
        
        for description, expression in test_cases:
            await self._test_calculation(description, expression)
    
    async def _test_calculation(self, description: str, expression: str):
        """测试单个计算"""
        try:
            self.logger.info(f"  📝 {description}: {expression}")
            
            result = await self.client.call_tool("calculator", "calculator", {
                "expression": expression
            })
            
            if result and "content" in result:
                content = result["content"][0]["text"] if result["content"] else str(result)
                self.logger.info(f"    ✅ Result: {content}")
                self.stats["successful_calls"] += 1
            else:
                self.logger.info(f"    ✅ Result: {result}")
                self.stats["successful_calls"] += 1
        
        except Exception as e:
            self.logger.error(f"    ❌ Error: {e}")
            self.stats["failed_calls"] += 1
    
    async def _demonstrate_advanced_features(self):
        """演示高级功能"""
        self.logger.info("📊 Demonstrating advanced features...")
        
        # 统计计算
        await self._test_statistics()
        
        # 数列计算
        await self._test_sequences()
    
    async def _test_statistics(self):
        """测试统计功能"""
        self.logger.info("  📈 Testing statistics calculations...")
        
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25]
        
        try:
            result = await self.client.call_tool("calculator", "advanced_calculator", {
                "operation": "statistics",
                "data": {"numbers": test_data}
            })
            
            if result and "content" in result:
                content = result["content"][0]["text"]
                self.logger.info(f"    ✅ Statistics: {content}")
                self.stats["successful_calls"] += 1
            else:
                # 解析结果数据
                if isinstance(result, dict):
                    data = json.loads(result) if isinstance(result, str) else result
                    self.logger.info(f"    ✅ Mean: {data.get('mean', 'N/A'):.2f}")
                    self.logger.info(f"    ✅ Median: {data.get('median', 'N/A'):.2f}")
                    self.logger.info(f"    ✅ Std Dev: {data.get('standard_deviation', 'N/A'):.2f}")
                    self.stats["successful_calls"] += 1
        
        except Exception as e:
            self.logger.error(f"    ❌ Statistics error: {e}")
            self.stats["failed_calls"] += 1
    
    async def _test_sequences(self):
        """测试数列功能"""
        self.logger.info("  🔢 Testing sequence calculations...")
        
        sequences = [
            ("Fibonacci", {"type": "fibonacci", "count": 10}),
            ("Arithmetic", {"type": "arithmetic", "start": 2, "step": 3, "count": 8}),
            ("Geometric", {"type": "geometric", "start": 1, "step": 2, "count": 8})
        ]
        
        for seq_name, seq_params in sequences:
            try:
                self.logger.info(f"    🔢 {seq_name} sequence...")
                
                result = await self.client.call_tool("calculator", "advanced_calculator", {
                    "operation": "sequence",
                    "data": seq_params
                })
                
                if result and "content" in result:
                    content = result["content"][0]["text"]
                    self.logger.info(f"      ✅ {content}")
                    self.stats["successful_calls"] += 1
                else:
                    if isinstance(result, dict):
                        data = json.loads(result) if isinstance(result, str) else result
                        sequence = data.get('sequence', [])
                        self.logger.info(f"      ✅ {seq_name}: {sequence}")
                        self.stats["successful_calls"] += 1
            
            except Exception as e:
                self.logger.error(f"      ❌ {seq_name} error: {e}")
                self.stats["failed_calls"] += 1
    
    async def _demonstrate_error_handling(self):
        """演示错误处理"""
        self.logger.info("⚠️  Demonstrating error handling...")
        
        error_tests = [
            ("Invalid expression", "calculator", {"expression": "invalid_function(123)"}),
            ("Division by zero", "calculator", {"expression": "1/0"}),
            ("Missing parameters", "calculator", {}),
            ("Non-existent tool", "nonexistent_tool", {"param": "value"})
        ]
        
        for test_name, tool_name, params in error_tests:
            try:
                self.logger.info(f"  🧪 Testing {test_name}...")
                
                result = await self.client.call_tool("calculator", tool_name, params)
                self.logger.warning(f"    ⚠️  Unexpected success: {result}")
                
            except MCPClientError as e:
                self.logger.info(f"    ✅ Expected MCP error: {e}")
            except Exception as e:
                self.logger.info(f"    ✅ Expected error: {e}")
    
    async def _performance_test(self):
        """性能测试"""
        self.logger.info("⚡ Running performance tests...")
        
        # 并发计算测试
        await self._concurrent_calculations_test()
        
        # 大数据统计测试
        await self._large_data_test()
    
    async def _concurrent_calculations_test(self):
        """并发计算测试"""
        self.logger.info("  🚀 Testing concurrent calculations...")
        
        expressions = [
            "2 + 3",
            "sqrt(16)",
            "sin(pi/4)",
            "log(100)",
            "2**8",
            "factorial(5)",
            "abs(-42)",
            "max(1, 2, 3, 4, 5)"
        ]
        
        start_time = time.time()
        
        # 创建并发任务
        tasks = []
        for i, expr in enumerate(expressions):
            task = self.client.call_tool("calculator", "calculator", {"expression": expr})
            tasks.append(task)
        
        # 等待所有任务完成
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            self.logger.info(f"    ✅ Concurrent test: {successful}/{len(expressions)} successful")
            self.logger.info(f"    ⏱️  Duration: {duration:.2f} seconds")
            self.logger.info(f"    📊 Rate: {len(expressions)/duration:.1f} calculations/second")
            
            self.stats["successful_calls"] += successful
            self.stats["failed_calls"] += failed
        
        except Exception as e:
            self.logger.error(f"    ❌ Concurrent test error: {e}")
    
    async def _large_data_test(self):
        """大数据测试"""
        self.logger.info("  📊 Testing large dataset statistics...")
        
        # 生成大数据集
        import random
        large_dataset = [random.randint(1, 1000) for _ in range(1000)]
        
        start_time = time.time()
        
        try:
            result = await self.client.call_tool("calculator", "advanced_calculator", {
                "operation": "statistics",
                "data": {"numbers": large_dataset}
            })
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(f"    ✅ Large dataset processed: 1000 numbers")
            self.logger.info(f"    ⏱️  Processing time: {duration:.2f} seconds")
            
            self.stats["successful_calls"] += 1
        
        except Exception as e:
            self.logger.error(f"    ❌ Large data test error: {e}")
            self.stats["failed_calls"] += 1
    
    async def _cleanup(self):
        """清理资源"""
        self.logger.info("🧹 Cleaning up resources...")
        
        try:
            await self.client.disconnect_all()
            self.logger.info("✅ All connections closed")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def _show_final_stats(self):
        """显示最终统计"""
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        self.logger.info("📈 Final Demo Statistics")
        self.logger.info("=" * 40)
        self.logger.info(f"⏱️  Total duration: {duration:.2f} seconds")
        self.logger.info(f"🔗 Servers connected: {self.stats['servers_connected']}")
        self.logger.info(f"🔧 Tools discovered: {self.stats['tools_discovered']}")
        self.logger.info(f"✅ Successful calls: {self.stats['successful_calls']}")
        self.logger.info(f"❌ Failed calls: {self.stats['failed_calls']}")
        
        total_calls = self.stats['successful_calls'] + self.stats['failed_calls']
        if total_calls > 0:
            success_rate = (self.stats['successful_calls'] / total_calls) * 100
            self.logger.info(f"📊 Success rate: {success_rate:.1f}%")
            
            if duration > 0:
                call_rate = total_calls / duration
                self.logger.info(f"⚡ Average call rate: {call_rate:.1f} calls/second")
        
        self.logger.info("=" * 40)
        self.logger.info("🎉 MCP Demo completed successfully!")


async def main():
    """
    主函数
    
    类似于JavaScript中的:
    async function main(): Promise<void> {
        console.log("🚀 Starting MCP System Demo");
        
        const demo = new MCPDemo();
        
        try {
            await demo.runCompleteDemo();
        } catch (error) {
            console.error("Demo failed:", error);
            process.exit(1);
        }
    }
    """
    print("🚀 MCP System Complete Demo")
    print("=" * 60)
    print("This demo showcases the complete MCP (Model Communication Protocol) system")
    print("including servers, clients, tools, and error handling.")
    print("=" * 60)
    
    demo = MCPDemo()
    
    try:
        await demo.run_complete_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


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
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)