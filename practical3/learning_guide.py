#!/usr/bin/env python3
"""
基础工具框架学习指南
专为Python小白设计，逐步讲解框架的核心概念和实现细节
"""

import asyncio
import inspect
from typing import Dict, Any

from tools import BaseTool, ToolResult, ToolManager, CalculatorTool, WeatherTool


class LearningGuide:
    """学习指南类 - 帮助理解框架核心概念"""
    
    def __init__(self):
        self.current_lesson = 0
        self.lessons = [
            self.lesson_1_abstract_base_class,
            self.lesson_2_json_schema,
            self.lesson_3_plugin_architecture,
            self.lesson_4_error_handling,
            self.lesson_5_async_programming,
            self.lesson_6_practical_examples
        ]
    
    def show_menu(self):
        """显示学习菜单"""
        print("\n" + "="*60)
        print("📚 基础工具框架学习指南")
        print("="*60)
        print("选择你想学习的内容:")
        print("1. 抽象基类 (Abstract Base Class)")
        print("2. JSON Schema 验证")
        print("3. 插件架构 (Plugin Architecture)")
        print("4. 统一错误处理")
        print("5. 异步编程 (Async Programming)")
        print("6. 实践示例")
        print("0. 退出")
        print("="*60)
    
    async def lesson_1_abstract_base_class(self):
        """第1课: 抽象基类"""
        print("\n📖 第1课: 抽象基类 (Abstract Base Class)")
        print("="*50)
        
        print("\n🎯 什么是抽象基类?")
        print("抽象基类是一个不能直接实例化的类，它定义了子类必须实现的方法。")
        print("在我们的框架中，BaseTool就是一个抽象基类。")
        
        print("\n💡 为什么使用抽象基类?")
        print("1. 统一接口: 所有工具都有相同的方法")
        print("2. 强制实现: 子类必须实现抽象方法")
        print("3. 代码复用: 提供通用功能")
        
        print("\n🔍 让我们看看BaseTool的定义:")
        print("```python")
        print(inspect.getsource(BaseTool))
        print("```")
        
        print("\n📝 关键点解释:")
        print("• @abstractmethod 装饰器标记必须实现的方法")
        print("• execute() 方法是抽象的，每个工具都必须实现")
        print("• get_schema() 方法定义工具的参数结构")
        
        input("\n按回车键继续...")
    
    async def lesson_2_json_schema(self):
        """第2课: JSON Schema验证"""
        print("\n📖 第2课: JSON Schema 验证")
        print("="*50)
        
        print("\n🎯 什么是JSON Schema?")
        print("JSON Schema是一种描述JSON数据结构的标准。")
        print("它可以验证数据格式、类型、必需字段等。")
        
        print("\n💡 在我们框架中的作用:")
        print("1. 自动验证输入参数")
        print("2. 提供清晰的API文档")
        print("3. 防止无效输入")
        
        # 展示计算器工具的Schema
        calc_tool = CalculatorTool()
        schema = calc_tool.get_schema()
        
        print("\n🔍 计算器工具的Schema示例:")
        print("```json")
        import json
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        print("```")
        
        print("\n📝 Schema解释:")
        print("• type: 'object' - 参数是一个对象")
        print("• properties - 定义对象的属性")
        print("• required - 必需的属性列表")
        print("• description - 属性的说明")
        
        print("\n🧪 让我们测试Schema验证:")
        
        # 测试有效输入
        valid_input = {"expression": "2 + 3"}
        print(f"\n✅ 有效输入: {valid_input}")
        result = await calc_tool.execute(valid_input)
        print(f"   结果: {result.data}")
        
        # 测试无效输入
        invalid_input = {"wrong_param": "value"}
        print(f"\n❌ 无效输入: {invalid_input}")
        result = await calc_tool.execute(invalid_input)
        print(f"   错误: {result.error}")
        
        input("\n按回车键继续...")
    
    async def lesson_3_plugin_architecture(self):
        """第3课: 插件架构"""
        print("\n📖 第3课: 插件架构 (Plugin Architecture)")
        print("="*50)
        
        print("\n🎯 什么是插件架构?")
        print("插件架构允许动态地添加、移除和管理功能模块。")
        print("每个工具就像一个插件，可以独立开发和部署。")
        
        print("\n💡 插件架构的优势:")
        print("1. 松耦合: 组件之间相互独立")
        print("2. 可扩展: 容易添加新功能")
        print("3. 可维护: 每个插件可以独立维护")
        
        print("\n🔍 让我们看看ToolManager如何管理插件:")
        
        # 创建管理器并注册工具
        manager = ToolManager()
        
        print("\n1. 创建工具管理器")
        print("   manager = ToolManager()")
        
        print("\n2. 注册工具 (添加插件)")
        calc_tool = CalculatorTool()
        weather_tool = WeatherTool()
        
        manager.register_tool("calculator", calc_tool)
        manager.register_tool("weather", weather_tool)
        
        print("   manager.register_tool('calculator', calc_tool)")
        print("   manager.register_tool('weather', weather_tool)")
        
        print("\n3. 查看已注册的工具")
        tools = manager.list_tools()
        print(f"   已注册工具: {tools}")
        
        print("\n4. 动态执行工具")
        result = await manager.execute_tool("calculator", expression="5 * 6")
        print(f"   执行结果: {result.data}")
        
        print("\n5. 注销工具 (移除插件)")
        manager.unregister_tool("weather")
        tools = manager.list_tools()
        print(f"   注销后的工具: {tools}")
        
        input("\n按回车键继续...")
    
    async def lesson_4_error_handling(self):
        """第4课: 统一错误处理"""
        print("\n📖 第4课: 统一错误处理")
        print("="*50)
        
        print("\n🎯 为什么需要统一错误处理?")
        print("1. 一致性: 所有错误都有相同的格式")
        print("2. 可预测: 调用者知道如何处理错误")
        print("3. 调试友好: 提供详细的错误信息")
        
        print("\n💡 我们的错误处理机制:")
        print("• ToolResult 统一返回格式")
        print("• ToolResultStatus 标准状态码")
        print("• 详细的错误信息和元数据")
        
        print("\n🔍 让我们看看不同类型的错误:")
        
        manager = ToolManager()
        calc_tool = CalculatorTool()
        manager.register_tool("calculator", calc_tool)
        
        # 1. 参数验证错误
        print("\n1. 参数验证错误:")
        result = await manager.execute_tool("calculator", wrong_param="value")
        print(f"   状态: {result.status.value}")
        print(f"   错误: {result.error}")
        
        # 2. 执行错误
        print("\n2. 执行错误:")
        result = await manager.execute_tool("calculator", expression="1/0")
        print(f"   状态: {result.status.value}")
        print(f"   错误: {result.error}")
        
        # 3. 工具不存在错误
        print("\n3. 工具不存在错误:")
        try:
            result = await manager.execute_tool("nonexistent", param="value")
        except Exception as e:
            print(f"   异常: {type(e).__name__}: {e}")
        
        # 4. 成功情况
        print("\n4. 成功执行:")
        result = await manager.execute_tool("calculator", expression="2 + 3")
        print(f"   状态: {result.status.value}")
        print(f"   结果: {result.data}")
        print(f"   耗时: {result.execution_time:.3f}s")
        
        input("\n按回车键继续...")
    
    async def lesson_5_async_programming(self):
        """第5课: 异步编程"""
        print("\n📖 第5课: 异步编程 (Async Programming)")
        print("="*50)
        
        print("\n🎯 什么是异步编程?")
        print("异步编程允许程序在等待I/O操作时执行其他任务。")
        print("这提高了程序的并发能力和响应性。")
        
        print("\n💡 异步编程的关键概念:")
        print("• async def: 定义异步函数")
        print("• await: 等待异步操作完成")
        print("• asyncio: Python的异步编程库")
        
        print("\n🔍 让我们比较同步和异步执行:")
        
        import time
        
        # 模拟同步执行
        print("\n1. 同步执行 (阻塞):")
        start_time = time.time()
        
        # 模拟耗时操作
        await asyncio.sleep(0.1)  # 模拟第一个任务
        await asyncio.sleep(0.1)  # 模拟第二个任务
        await asyncio.sleep(0.1)  # 模拟第三个任务
        
        sync_time = time.time() - start_time
        print(f"   同步执行耗时: {sync_time:.3f}s")
        
        # 异步并发执行
        print("\n2. 异步执行 (并发):")
        start_time = time.time()
        
        # 并发执行多个任务
        tasks = [
            asyncio.sleep(0.1),  # 任务1
            asyncio.sleep(0.1),  # 任务2
            asyncio.sleep(0.1),  # 任务3
        ]
        await asyncio.gather(*tasks)
        
        async_time = time.time() - start_time
        print(f"   异步执行耗时: {async_time:.3f}s")
        print(f"   性能提升: {sync_time/async_time:.1f}x")
        
        print("\n🧪 实际示例 - 批量执行工具:")
        manager = ToolManager()
        calc_tool = CalculatorTool()
        manager.register_tool("calculator", calc_tool)
        
        # 批量任务
        tasks = [
            ("calculator", {"expression": "1 + 1"}),
            ("calculator", {"expression": "2 * 3"}),
            ("calculator", {"expression": "10 / 2"}),
        ]
        
        start_time = time.time()
        results = await manager.execute_batch(tasks)
        batch_time = time.time() - start_time
        
        print(f"   批量执行 {len(tasks)} 个任务")
        print(f"   总耗时: {batch_time:.3f}s")
        print(f"   平均每任务: {batch_time/len(tasks):.3f}s")
        
        for i, (tool_name, params, result) in enumerate(results):
            print(f"   任务{i+1}: {params['expression']} = {result.data}")
        
        input("\n按回车键继续...")
    
    async def lesson_6_practical_examples(self):
        """第6课: 实践示例"""
        print("\n📖 第6课: 实践示例")
        print("="*50)
        
        print("\n🎯 现在让我们创建一个自定义工具!")
        print("我们将创建一个简单的字符串处理工具。")
        
        print("\n💡 步骤:")
        print("1. 继承BaseTool")
        print("2. 实现必需的方法")
        print("3. 定义JSON Schema")
        print("4. 注册和使用工具")
        
        # 创建自定义工具
        from tools.base import BaseTool, ToolResult, ToolResultStatus
        import time
        
        class StringTool(BaseTool):
            """字符串处理工具示例"""
            
            def __init__(self):
                super().__init__(
                    name="string_processor",
                    description="处理字符串的工具，支持大小写转换、反转等操作",
                    version="1.0.0"
                )
            
            def get_schema(self) -> Dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "要处理的文本"
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["upper", "lower", "reverse", "length"],
                            "description": "操作类型: upper(大写), lower(小写), reverse(反转), length(长度)"
                        }
                    },
                    "required": ["text", "operation"]
                }
            
            async def execute(self, params: Dict[str, Any]) -> ToolResult:
                start_time = time.time()
                
                try:
                    # 验证参数
                    if not self.validate_params(params):
                        return ToolResult(
                            status=ToolResultStatus.ERROR,
                            error="参数验证失败",
                            execution_time=time.time() - start_time
                        )
                    
                    text = params["text"]
                    operation = params["operation"]
                    
                    # 执行操作
                    if operation == "upper":
                        result = text.upper()
                    elif operation == "lower":
                        result = text.lower()
                    elif operation == "reverse":
                        result = text[::-1]
                    elif operation == "length":
                        result = len(text)
                    else:
                        raise ValueError(f"不支持的操作: {operation}")
                    
                    return ToolResult(
                        status=ToolResultStatus.SUCCESS,
                        data=result,
                        execution_time=time.time() - start_time,
                        metadata={"original_text": text, "operation": operation}
                    )
                
                except Exception as e:
                    return ToolResult(
                        status=ToolResultStatus.ERROR,
                        error=str(e),
                        execution_time=time.time() - start_time
                    )
        
        print("\n🔍 自定义工具代码:")
        print("```python")
        print("class StringTool(BaseTool):")
        print("    # ... 实现细节见上方代码 ...")
        print("```")
        
        print("\n🧪 测试自定义工具:")
        
        # 创建和注册工具
        manager = ToolManager()
        string_tool = StringTool()
        manager.register_tool("string", string_tool)
        
        # 测试不同操作
        test_cases = [
            {"text": "Hello World", "operation": "upper"},
            {"text": "Hello World", "operation": "lower"},
            {"text": "Hello World", "operation": "reverse"},
            {"text": "Hello World", "operation": "length"},
        ]
        
        for params in test_cases:
            result = await manager.execute_tool("string", **params)
            print(f"\n   输入: {params}")
            print(f"   输出: {result.data}")
            print(f"   耗时: {result.execution_time:.3f}s")
        
        print("\n🎉 恭喜! 你已经学会了:")
        print("✅ 抽象基类的使用")
        print("✅ JSON Schema验证")
        print("✅ 插件架构设计")
        print("✅ 统一错误处理")
        print("✅ 异步编程模式")
        print("✅ 创建自定义工具")
        
        print("\n📚 下一步学习建议:")
        print("• 尝试创建更复杂的工具")
        print("• 学习更多JSON Schema特性")
        print("• 深入了解Python异步编程")
        print("• 研究实际项目中的插件架构")
        
        input("\n按回车键继续...")
    
    async def run(self):
        """运行学习指南"""
        while True:
            self.show_menu()
            try:
                choice = input("\n请选择 (0-6): ").strip()
                
                if choice == "0":
                    print("👋 学习愉快!")
                    break
                elif choice in ["1", "2", "3", "4", "5", "6"]:
                    lesson_index = int(choice) - 1
                    await self.lessons[lesson_index]()
                else:
                    print("❌ 无效选择，请输入0-6之间的数字")
            
            except KeyboardInterrupt:
                print("\n\n👋 学习被中断，再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")


async def main():
    """主函数"""
    guide = LearningGuide()
    await guide.run()


if __name__ == "__main__":
    asyncio.run(main())