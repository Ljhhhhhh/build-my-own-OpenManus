#!/usr/bin/env python3
"""
项目3主程序 - 基础工具框架演示
展示如何使用工具抽象、JSON Schema验证、插件架构等核心概念
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

from tools import ToolManager, CalculatorTool, WeatherTool, ToolResult, ToolResultStatus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ToolFrameworkDemo:
    """工具框架演示类 - 展示核心概念和使用方法"""
    
    def __init__(self):
        self.manager = ToolManager()
        self._setup_tools()
    
    def _setup_tools(self):
        """设置和注册工具"""
        logger.info("正在注册工具...")
        
        # 注册计算器工具
        calculator = CalculatorTool()
        self.manager.register_tool(calculator)
        
        # 注册天气工具（使用演示API密钥）
        try:
            weather = WeatherTool(api_key="demo_key_for_testing")
            self.manager.register_tool(weather)
        except Exception as e:
            logger.warning(f"天气工具注册失败: {e}")
            logger.info("将跳过天气工具演示")
        
        logger.info(f"已注册 {len(self.manager)} 个工具")
    
    async def demo_basic_usage(self):
        """演示基础使用方法"""
        print("\n" + "="*60)
        print("🚀 基础工具框架演示")
        print("="*60)
        
        # 1. 展示已注册的工具
        print("\n📋 已注册的工具:")
        for tool_info in self.manager.list_tools():
            tool_name = tool_info['name']
            tool = self.manager.get_tool(tool_name)
            print(f"  • {tool_name}: {tool.description}")
            print(f"    Schema: {json.dumps(tool.schema, indent=2, ensure_ascii=False)}")
        
        # 2. 演示计算器工具
        print("\n🧮 计算器工具演示:")
        calc_examples = [
            {"operation": "add", "a": 10, "b": 5},
            {"operation": "subtract", "a": 20, "b": 8},
            {"operation": "multiply", "a": 6, "b": 7},
            {"operation": "divide", "a": 15, "b": 3},
            {"operation": "divide", "a": 10, "b": 0}  # 除零错误示例
        ]
        
        for example in calc_examples:
            result = await self.manager.execute_tool("calculator", **example)
            self._print_result("calculator", example, result)
        
        # 3. 演示天气工具（如果配置了API密钥）
        print("\n🌤️ 天气工具演示:")
        weather_examples = [
            {"city": "Beijing"},
            {"city": "Shanghai"},
            {"city": "InvalidCity123"}  # 错误示例
        ]
        
        if "weather" in self.manager:
            for example in weather_examples:
                result = await self.manager.execute_tool("weather", **example)
                self._print_result("weather", example, result)
        else:
            print("  ⚠️ 天气工具未注册，跳过演示")
    
    async def demo_batch_processing(self):
        """演示批量处理功能"""
        print("\n" + "="*60)
        print("⚡ 批量处理演示")
        print("="*60)
        
        # 准备批量任务
        tasks = [
            ("calculator", {"operation": "add", "a": 5, "b": 3}),
            ("calculator", {"operation": "multiply", "a": 4, "b": 6}),
            ("calculator", {"operation": "divide", "a": 20, "b": 4})
        ]
        
        # 如果天气工具可用，添加天气查询任务
        if "weather" in self.manager:
            tasks.extend([
                ("weather", {"city": "Beijing"}),
                ("weather", {"city": "Shanghai"})
            ])
        
        print(f"\n📦 执行 {len(tasks)} 个批量任务...")
        
        # 转换为正确的格式
        batch_requests = []
        for tool_name, params in tasks:
            batch_requests.append({
                'tool_name': tool_name,
                'params': params
            })
        
        results = await self.manager.execute_tools_batch(batch_requests)
        
        print("\n📊 批量处理结果:")
        for i, result in enumerate(results):
            task_name, task_params = tasks[i]
            print(f"\n任务 {i+1}: {task_name}")
            print(f"  参数: {task_params}")
            print(f"  状态: {result.status.value}")
            if result.status == ToolResultStatus.SUCCESS:
                print(f"  结果: {result.content}")
            else:
                print(f"  错误: {result.error_message}")
    
    async def demo_error_handling(self):
        """演示错误处理机制"""
        print("\n" + "="*60)
        print("🛡️ 错误处理演示")
        print("="*60)
        
        error_cases = [
            # 工具不存在
            ("nonexistent_tool", {"param": "value"}),
            # 参数验证失败
            ("calculator", {"wrong_param": "value"}),
            ("weather", {}),  # 缺少必需参数
            # 执行错误
            ("calculator", {"operation": "divide", "a": 1, "b": 0}),  # 除零错误
        ]
        
        for tool_name, params in error_cases:
            print(f"\n🔍 测试错误情况: {tool_name} with {params}")
            try:
                result = await self.manager.execute_tool(tool_name, **params)
                self._print_result(tool_name, params, result)
            except Exception as e:
                print(f"  ❌ 捕获异常: {type(e).__name__}: {e}")
    
    def demo_statistics(self):
        """演示统计功能"""
        print("\n" + "="*60)
        print("📈 工具使用统计")
        print("="*60)
        
        stats = self.manager.get_stats()
        print(f"\n📊 统计信息:")
        summary = stats.get('summary', {})
        print(f"  • 总执行次数: {summary.get('total_executions', 0)}")
        print(f"  • 成功次数: {summary.get('total_successful', 0)}")
        print(f"  • 失败次数: {summary.get('total_failed', 0)}")
        
        total_exec = summary.get('total_executions', 0)
        if total_exec > 0:
            success_rate = summary.get('total_successful', 0) / total_exec
            print(f"  • 成功率: {success_rate:.1%}")
        else:
            print(f"  • 成功率: 0.0%")
        
        tool_stats = stats.get('tools', {})
        if tool_stats:
            print(f"\n🔧 各工具使用情况:")
            for tool_name, tool_stat in tool_stats.items():
                total = tool_stat.get('total_executions', 0)
                successful = tool_stat.get('successful_executions', 0)
                print(f"  • {tool_name}: {total} 次执行，{successful} 次成功")
    
    def _print_result(self, tool_name: str, params: Dict[str, Any], result: ToolResult):
        """打印工具执行结果"""
        print(f"\n  📝 {tool_name}({params})")
        print(f"     状态: {result.status.value}")
        if hasattr(result, 'execution_time') and result.execution_time:
            print(f"     耗时: {result.execution_time:.3f}s")
        
        if result.status == ToolResultStatus.SUCCESS:
            print(f"     ✅ 结果: {result.content}")
        else:
            print(f"     ❌ 错误: {result.error_message}")
        
        if result.metadata:
            print(f"     📋 元数据: {result.metadata}")


async def main():
    """主函数 - 运行完整演示"""
    print("🎯 欢迎使用基础工具框架!")
    print("这个演示将帮助你理解:")
    print("  • 工具抽象和继承")
    print("  • JSON Schema验证")
    print("  • 插件架构设计")
    print("  • 统一错误处理")
    print("  • 异步编程模式")
    
    # 创建演示实例
    demo = ToolFrameworkDemo()
    
    try:
        # 运行各种演示
        await demo.demo_basic_usage()
        await demo.demo_batch_processing()
        await demo.demo_error_handling()
        demo.demo_statistics()
        
        print("\n" + "="*60)
        print("🎉 演示完成! 你已经掌握了基础工具框架的核心概念")
        print("="*60)
        
        # 学习要点总结
        print("\n📚 关键学习要点:")
        print("1. 抽象基类 (BaseTool): 定义统一接口")
        print("2. JSON Schema: 自动参数验证")
        print("3. 插件架构: 动态注册和管理工具")
        print("4. 错误处理: 统一的错误处理机制")
        print("5. 异步编程: 提高性能和并发能力")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}", exc_info=True)
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())