#!/usr/bin/env python3
"""
交互式工具框架演示
让用户通过命令行界面体验工具框架的功能
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional

from tools import ToolManager, CalculatorTool, WeatherTool, ToolResult, ToolResultStatus


class InteractiveDemo:
    """交互式演示类"""
    
    def __init__(self):
        self.manager = ToolManager()
        self.running = True
        self._setup_tools()
    
    def _setup_tools(self):
        """设置工具"""
        calculator = CalculatorTool()
        weather = WeatherTool()
        
        self.manager.register_tool("calculator", calculator)
        self.manager.register_tool("weather", weather)
    
    def show_welcome(self):
        """显示欢迎信息"""
        print("\n" + "="*60)
        print("🎯 交互式工具框架演示")
        print("="*60)
        print("这是一个交互式演示，你可以:")
        print("  • 查看可用工具")
        print("  • 执行工具命令")
        print("  • 查看工具统计")
        print("  • 学习框架概念")
        print("\n输入 'help' 查看所有命令")
        print("输入 'quit' 退出程序")
        print("="*60)
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📋 可用命令:")
        print("  help              - 显示此帮助信息")
        print("  list              - 列出所有可用工具")
        print("  info <tool_name>  - 显示工具详细信息")
        print("  calc <expression> - 使用计算器工具")
        print("  weather <city>    - 查询天气信息")
        print("  stats             - 显示使用统计")
        print("  concepts          - 学习框架核心概念")
        print("  quit              - 退出程序")
        print("\n💡 示例:")
        print("  calc 2 + 3 * 4")
        print("  weather Beijing")
        print("  info calculator")
    
    def list_tools(self):
        """列出所有工具"""
        print("\n🔧 可用工具:")
        for tool_name in self.manager.list_tools():
            tool = self.manager.get_tool(tool_name)
            print(f"  • {tool_name}: {tool.description}")
    
    def show_tool_info(self, tool_name: str):
        """显示工具详细信息"""
        tool = self.manager.get_tool(tool_name)
        if not tool:
            print(f"❌ 工具 '{tool_name}' 不存在")
            return
        
        print(f"\n🔍 工具信息: {tool_name}")
        print(f"  名称: {tool.name}")
        print(f"  描述: {tool.description}")
        print(f"  版本: {tool.version}")
        print(f"  Schema:")
        schema = tool.get_schema()
        print(json.dumps(schema, indent=4, ensure_ascii=False))
    
    async def execute_calculator(self, expression: str):
        """执行计算器工具"""
        if not expression.strip():
            print("❌ 请提供计算表达式")
            return
        
        params = {"expression": expression}
        result = await self.manager.execute_tool("calculator", **params)
        self._print_result("calculator", params, result)
    
    async def execute_weather(self, city: str):
        """执行天气工具"""
        if not city.strip():
            print("❌ 请提供城市名称")
            return
        
        params = {"city": city}
        result = await self.manager.execute_tool("weather", **params)
        self._print_result("weather", params, result)
    
    def show_statistics(self):
        """显示统计信息"""
        stats = self.manager.get_statistics()
        print("\n📈 使用统计:")
        print(f"  总执行次数: {stats['total_executions']}")
        print(f"  成功次数: {stats['successful_executions']}")
        print(f"  失败次数: {stats['failed_executions']}")
        print(f"  成功率: {stats['success_rate']:.1%}")
        
        if stats['tool_usage']:
            print("\n🔧 各工具使用情况:")
            for tool_name, count in stats['tool_usage'].items():
                print(f"  • {tool_name}: {count} 次")
    
    def show_concepts(self):
        """显示框架核心概念"""
        print("\n📚 基础工具框架核心概念:")
        print("\n1. 🏗️ 抽象基类 (BaseTool)")
        print("   • 定义统一的工具接口")
        print("   • 强制子类实现必要方法")
        print("   • 提供通用功能和属性")
        
        print("\n2. 📋 JSON Schema 验证")
        print("   • 自动验证输入参数")
        print("   • 提供清晰的参数文档")
        print("   • 防止无效输入导致错误")
        
        print("\n3. 🔌 插件架构")
        print("   • 动态注册和注销工具")
        print("   • 松耦合的组件设计")
        print("   • 易于扩展和维护")
        
        print("\n4. 🛡️ 统一错误处理")
        print("   • 标准化的错误响应格式")
        print("   • 详细的错误信息和上下文")
        print("   • 优雅的异常处理机制")
        
        print("\n5. ⚡ 异步编程")
        print("   • 提高并发处理能力")
        print("   • 非阻塞的I/O操作")
        print("   • 更好的资源利用率")
        
        print("\n💡 学习建议:")
        print("   • 先理解抽象基类的概念")
        print("   • 学习JSON Schema的基本语法")
        print("   • 掌握Python异步编程基础")
        print("   • 实践创建自己的工具类")
    
    def _print_result(self, tool_name: str, params: Dict[str, Any], result: ToolResult):
        """打印执行结果"""
        print(f"\n📝 执行结果:")
        print(f"  工具: {tool_name}")
        print(f"  参数: {params}")
        print(f"  状态: {result.status.value}")
        print(f"  耗时: {result.execution_time:.3f}s")
        
        if result.status == ToolResultStatus.SUCCESS:
            print(f"  ✅ 结果: {result.data}")
        else:
            print(f"  ❌ 错误: {result.error}")
        
        if result.metadata:
            print(f"  📋 元数据: {result.metadata}")
    
    async def process_command(self, command: str):
        """处理用户命令"""
        parts = command.strip().split(None, 1)
        if not parts:
            return
        
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if cmd == "help":
            self.show_help()
        elif cmd == "list":
            self.list_tools()
        elif cmd == "info":
            if not arg:
                print("❌ 请指定工具名称，例如: info calculator")
            else:
                self.show_tool_info(arg)
        elif cmd == "calc":
            if not arg:
                print("❌ 请提供计算表达式，例如: calc 2 + 3")
            else:
                await self.execute_calculator(arg)
        elif cmd == "weather":
            if not arg:
                print("❌ 请提供城市名称，例如: weather Beijing")
            else:
                await self.execute_weather(arg)
        elif cmd == "stats":
            self.show_statistics()
        elif cmd == "concepts":
            self.show_concepts()
        elif cmd == "quit":
            self.running = False
            print("👋 再见!")
        else:
            print(f"❌ 未知命令: {cmd}")
            print("输入 'help' 查看可用命令")
    
    async def run(self):
        """运行交互式演示"""
        self.show_welcome()
        
        while self.running:
            try:
                command = input("\n🎯 请输入命令: ").strip()
                if command:
                    await self.process_command(command)
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见!")
                break
            except EOFError:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 处理命令时发生错误: {e}")


async def main():
    """主函数"""
    demo = InteractiveDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())