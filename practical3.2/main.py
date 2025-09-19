"""
Practical 3.2 - 异步工具框架基础演示 

这个模块演示了异步工具框架的基础使用，专注于核心概念：
1. 异步工具的基本执行
2. 简单的并发操作
3. 基础的错误处理
4. 异步编程的核心模式

学习要点：
1. 异步编程的基础概念（async/await）
2. 异步工具的注册和执行
3. 简单的并发控制
4. 基础的异常处理
5. 异步上下文管理

💡 对比TypeScript:
// TypeScript版本的异步工具框架
class AsyncToolFramework {
    private toolManager: AsyncToolManager;
    
    constructor() {
        this.toolManager = new AsyncToolManager();
    }
    
    async initializeTools(): Promise<void> {
        // 注册工具
        await this.toolManager.registerTool(new AsyncCalculatorTool());
        await this.toolManager.registerTool(new AsyncWeatherTool());
        
        console.log(`✅ 已注册 ${this.toolManager.getToolCount()} 个工具`);
    }
    
    async runBasicDemo(): Promise<void> {
        console.log("🚀 基础异步工具演示");
        
        // 单个工具执行
        const result = await this.toolManager.executeTool("calculator", {
            operation: "add",
            operands: [10, 20]
        });
        
        console.log(`计算结果: ${result.content}`);
        
        // 并发执行
        const tasks = [
            this.toolManager.executeTool("calculator", { operation: "multiply", operands: [5, 6] }),
            this.toolManager.executeTool("weather", { city: "Beijing" })
        ];
        
        const results = await Promise.allSettled(tasks);
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                console.log(`任务 ${index + 1} 成功: ${result.value.content}`);
            } else {
                console.log(`任务 ${index + 1} 失败: ${result.reason}`);
            }
        });
    }
}

学习要点：
- Python异步编程与JavaScript Promise的对比
- 异步工具管理的基础模式
- 并发执行的简单实现
- 错误处理的基础方法
"""

import asyncio
import sys
import os
from typing import List, Dict, Any
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import AsyncToolManager, AsyncCalculatorTool, AsyncWeatherTool
from config import Config


class SimpleAsyncToolDemo:
    """
    简化的异步工具演示类
    
    学习要点：
    - 异步类的基础结构
    - 工具管理器的简单使用
    - 异步初始化的基础模式
    - 基础的错误处理
    
    💡 对比TypeScript:
    class SimpleAsyncToolDemo {
        private toolManager: AsyncToolManager;
        
        constructor() {
            this.toolManager = new AsyncToolManager();
        }
        
        async initialize(): Promise<void> {
            // 注册工具
            await this.toolManager.registerTool(new AsyncCalculatorTool());
            await this.toolManager.registerTool(new AsyncWeatherTool());
        }
        
        async runDemo(): Promise<void> {
            // 运行演示
        }
    }
    """
    
    def __init__(self):
        """
        初始化简化的工具框架演示
        
        学习要点：
        - 异步组件的基础初始化
        - 工具管理器的创建
        - 配置的基础使用
        """
        self.config = Config()
        self.tool_manager = AsyncToolManager()
        print("🔧 异步工具框架已初始化")
    
    async def initialize_tools(self):
        """
        初始化和注册工具
        
        学习要点：
        - 异步方法的定义和使用
        - 工具注册的基础流程
        - 异常处理的基础实现
        - await关键字的使用
        """
        try:
            print("\n📦 正在注册工具...")
            
            # 注册计算器工具
            calculator = AsyncCalculatorTool()
            self.tool_manager.register_tool(calculator)
            print("  ✅ 计算器工具已注册")
            
            # 注册天气工具
            weather = AsyncWeatherTool()
            self.tool_manager.register_tool(weather)
            print("  ✅ 天气工具已注册")
            
            print(f"\n🎯 总共注册了 {len(self.tool_manager.tools)} 个工具")
            
        except Exception as e:
            print(f"❌ 工具注册失败: {e}")
            raise
    
    async def run_single_tool_demo(self):
        """
        单个工具执行演示
        
        学习要点：
        - 异步工具的基础执行
        - 工具参数的传递
        - 执行结果的处理
        - 基础的错误处理
        """
        print("\n🚀 单个工具执行演示")
        print("=" * 30)
        
        try:
            # 执行计算器工具
            print("\n🧮 执行计算器工具:")
            calc_result = await self.tool_manager.execute_tool(
                "async_calculator",
                operation="add", a=10, b=20
            )
            
            if calc_result.is_success():
                print(f"  ✅ 计算结果: {calc_result.content}")
            else:
                print(f"  ❌ 计算失败: {calc_result.error_message}")
            
            # 执行天气工具
            print("\n🌤️ 天气查询演示:")
            weather_result = await self.tool_manager.execute_tool(
                "async_weather", city="北京"
            )
            
            if weather_result.is_success():
                print(f"  ✅ 天气信息: {weather_result.content}")
            else:
                print(f"  ❌ 天气查询失败: {weather_result.error_message}")
                
        except Exception as e:
            print(f"❌ 单个工具执行异常: {e}")
    
    async def run_concurrent_demo(self):
        """
        并发执行演示
        
        学习要点：
        - asyncio.gather的使用
        - 并发任务的创建和管理
        - 并发结果的处理
        - 异步编程的并发模式
        """
        print("\n🔄 并发执行演示")
        print("=" * 30)
        
        try:
            print("\n⚡ 同时执行多个计算任务:")
            
            # 创建多个并发任务
            tasks = [
                self.tool_manager.execute_tool(
                    "async_calculator",
                    operation="add", a=1, b=2
                ),
                self.tool_manager.execute_tool(
                    "async_calculator", 
                    operation="multiply", a=4, b=5
                ),
                self.tool_manager.execute_tool(
                    "async_calculator",
                    operation="subtract", a=100, b=25
                )
            ]
            
            # 并发执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(results, 1):
                if isinstance(result, Exception):
                    print(f"  ❌ 任务 {i} 异常: {result}")
                elif result.is_success():
                    print(f"  ✅ 任务 {i} 成功: {result.content}")
                else:
                    print(f"  ❌ 任务 {i} 失败: {result.error_message}")
                    
        except Exception as e:
            print(f"❌ 并发执行异常: {e}")
    
    async def run_mixed_tools_demo(self):
        """
        混合工具并发演示
        
        学习要点：
        - 不同类型工具的并发执行
        - 异步任务的组合使用
        - 复杂并发场景的处理
        - 结果聚合的基础方法
        """
        print("\n🎭 混合工具并发演示")
        print("=" * 30)
        
        try:
            print("\n🌐 同时执行计算和天气查询:")
            
            # 创建混合任务
            tasks = [
                self.tool_manager.execute_tool(
                    "async_calculator",
                    operation="divide", a=144, b=12
                ),
                self.tool_manager.execute_tool(
                    "async_weather",
                    city="上海"
                ),
                self.tool_manager.execute_tool(
                    "async_calculator",
                    operation="add", a=50, b=75
                )
            ]
            
            # 使用asyncio.gather并发执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 分类处理结果
            task_names = ["计算任务1", "天气查询", "计算任务2"]
            
            for i, (name, result) in enumerate(zip(task_names, results)):
                if isinstance(result, Exception):
                    print(f"  ❌ {name} 异常: {result}")
                elif result.is_success():
                    print(f"  ✅ {name} 成功: {result.content}")
                else:
                    print(f"  ❌ {name} 失败: {result.error_message}")
                    
        except Exception as e:
            print(f"❌ 混合工具执行异常: {e}")
    
    async def run_error_handling_demo(self):
        """
        错误处理演示
        
        学习要点：
        - 异步异常处理的模式
        - 工具执行失败的处理
        - 优雅的错误恢复
        - 异步上下文中的异常传播
        """
        print("\n🛡️ 错误处理演示")
        print("=" * 30)
        
        try:
            print("\n⚠️ 测试错误处理:")
            
            # 测试无效操作
            print("  测试无效计算操作...")
            invalid_result = await self.tool_manager.execute_tool(
                "async_calculator",
                operation="invalid_op", a=1, b=2
            )
            
            if not invalid_result.is_success():
                print(f"  ✅ 正确捕获错误: {invalid_result.error_message}")
            
            # 测试除零错误
            print("  测试除零错误...")
            zero_div_result = await self.tool_manager.execute_tool(
                "async_calculator",
                operation="divide", a=10, b=0
            )
            
            if not zero_div_result.is_success():
                print(f"  ✅ 正确处理除零: {zero_div_result.error_message}")
            
            # 测试无效城市
            print("  测试无效城市查询...")
            invalid_city_result = await self.tool_manager.execute_tool(
                "async_weather",
                city="InvalidCity123"
            )
            
            if not invalid_city_result.is_success():
                print(f"  ✅ 正确处理无效城市: {invalid_city_result.error_message}")
                
        except Exception as e:
            print(f"❌ 错误处理演示异常: {e}")
    
    def show_tool_info(self):
        """
        显示工具信息
        
        学习要点：
        - 工具管理器的查询功能
        - 工具信息的格式化输出
        - 基础的数据展示
        """
        print("\n📋 已注册工具信息")
        print("=" * 30)
        
        for tool_name, tool in self.tool_manager.tools.items():
            print(f"\n🔧 工具: {tool_name}")
            print(f"  📝 描述: {tool.description}")
            print(f"  🏷️ 类型: {type(tool).__name__}")
    
    async def run_all_demos(self):
        """
        运行所有演示
        
        学习要点：
        - 异步方法的组合调用
        - 演示流程的组织
        - 异步程序的整体结构
        """
        print("🎯 异步工具框架基础演示")
        print("=" * 40)
        
        # 显示工具信息
        self.show_tool_info()
        
        # 运行各种演示
        await self.run_single_tool_demo()
        await self.run_concurrent_demo()
        await self.run_mixed_tools_demo()
        await self.run_error_handling_demo()
        
        print("\n✅ 所有演示完成!")


async def main():
    """
    主函数 - 异步程序的入口点
    
    学习要点：
    - 异步主函数的定义
    - 异步程序的启动流程
    - 异步上下文管理
    - 程序的优雅退出
    
    💡 对比TypeScript:
    async function main(): Promise<void> {
        console.log("🚀 启动异步工具框架演示");
        
        const demo = new SimpleAsyncToolDemo();
        
        try {
            await demo.initialize();
            await demo.runAllDemos();
        } catch (error) {
            console.error(`❌ 程序执行失败: ${error}`);
            process.exit(1);
        }
        
        console.log("👋 演示结束");
    }
    
    // 启动程序
    main().catch(console.error);
    """
    print("🚀 启动异步工具框架基础演示")
    print("=" * 50)
    
    # 创建演示实例
    demo = SimpleAsyncToolDemo()
    
    try:
        # 初始化工具
        await demo.initialize_tools()
        
        # 运行所有演示
        await demo.run_all_demos()
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        raise
    finally:
        print("\n👋 演示程序结束")


if __name__ == "__main__":
    """
    程序入口点
    
    学习要点：
    - 异步程序的启动方式
    - 事件循环的配置
    - 跨平台兼容性处理
    - 异常处理的最外层
    """
    try:
        # Windows平台的事件循环策略设置
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # 运行异步主函数
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"❌ 启动异常: {e}")
        sys.exit(1)