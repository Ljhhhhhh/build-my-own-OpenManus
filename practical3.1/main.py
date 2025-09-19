"""
Practical 3.1 - 基础工具系统演示

这是一个专为前端开发者设计的Python学习项目，专注于Python基础概念。
通过构建一个简单的工具系统，学习Python的核心特性。

学习目标：
1. Python类和继承
2. 抽象基类的使用
3. 类型注解
4. 异常处理
5. 模块和包的组织

运行方式：
python main.py
"""

from tools import ToolManager, CalculatorTool


class ToolFrameworkDemo:
    """
    工具框架演示类
    
    💡 对比TypeScript:
    class ToolFrameworkDemo {
        private manager: ToolManager;
        
        constructor() {
            this.manager = new ToolManager();
            this.setupTools();
        }
        
        setupTools(): void { ... }
        runBasicDemo(): void { ... }
    }
    
    学习要点：
    - 类的设计和组织
    - 实例属性的管理
    - 方法的分工和协作
    """
    
    def __init__(self):
        """
        初始化演示程序
        
        学习要点：
        - 构造函数的使用
        - 实例属性的初始化
        - 方法调用的顺序
        """
        print("🚀 初始化工具框架演示程序")
        print("=" * 50)
        
        # 创建工具管理器
        self.manager = ToolManager()
        
        # 设置工具
        self._setup_tools()
        
        print("✅ 初始化完成！")
    
    def _setup_tools(self):
        """
        设置和注册所有工具
        
        学习要点：
        - 私有方法的使用
        - 工具的创建和注册
        - 错误处理
        """
        print("\n🔧 注册工具...")
        
        try:
            # 注册计算器工具
            calculator = CalculatorTool()
            success = self.manager.register_tool(calculator)
            
            if success:
                print(f"✅ 成功注册工具: {calculator.name}")
            else:
                print(f"❌ 注册工具失败: {calculator.name}")
                
        except Exception as e:
            print(f"💥 注册工具时发生错误: {str(e)}")
    
    def run_basic_demo(self):
        """
        运行基础演示
        
        学习要点：
        - 工具的基本使用
        - 结果的处理和展示
        - 循环和条件判断
        """
        print("\n" + "=" * 50)
        print("📚 基础演示 - 计算器工具使用")
        print("=" * 50)
        
        # 演示用例
        demo_cases = [
            {
                'name': '加法运算',
                'tool': 'calculator',
                'params': {'operation': 'add', 'a': 15, 'b': 25}
            },
            {
                'name': '减法运算',
                'tool': 'calculator', 
                'params': {'operation': 'subtract', 'a': 50, 'b': 18}
            },
            {
                'name': '乘法运算',
                'tool': 'calculator',
                'params': {'operation': 'multiply', 'a': 8, 'b': 9}
            },
            {
                'name': '除法运算',
                'tool': 'calculator',
                'params': {'operation': 'divide', 'a': 84, 'b': 12}
            }
        ]
        
        for i, case in enumerate(demo_cases, 1):
            print(f"\n{i}. {case['name']}")
            print(f"   参数: {case['params']}")
            
            # 执行工具
            result = self.manager.execute_tool(case['tool'], **case['params'])
            
            # 显示结果
            if result.status == 'success':
                expression = result.content.get('expression', '未知')
                print(f"   结果: {expression}")
            else:
                print(f"   错误: {result.error_message}")
    
    def run_error_handling_demo(self):
        """
        运行错误处理演示
        
        学习要点：
        - 错误情况的处理
        - 输入验证的重要性
        - 异常处理的实践
        """
        print("\n" + "=" * 50)
        print("🚨 错误处理演示")
        print("=" * 50)
        
        error_cases = [
            {
                'name': '除零错误',
                'tool': 'calculator',
                'params': {'operation': 'divide', 'a': 10, 'b': 0}
            },
            {
                'name': '无效操作',
                'tool': 'calculator',
                'params': {'operation': 'power', 'a': 2, 'b': 3}
            },
            {
                'name': '缺少参数',
                'tool': 'calculator',
                'params': {'operation': 'add', 'a': 5}  # 缺少参数b
            },
            {
                'name': '不存在的工具',
                'tool': 'nonexistent_tool',
                'params': {'test': 'data'}
            }
        ]
        
        for i, case in enumerate(error_cases, 1):
            print(f"\n{i}. {case['name']}")
            print(f"   参数: {case['params']}")
            
            # 执行工具（预期会出错）
            result = self.manager.execute_tool(case['tool'], **case['params'])
            
            # 显示错误信息
            print(f"   状态: {result.status}")
            if result.status != 'success':
                print(f"   错误信息: {result.error_message}")
            else:
                print(f"   意外成功: {result.content}")
    
    def run_interactive_demo(self):
        """
        运行交互式演示
        
        学习要点：
        - 用户输入的处理
        - 循环控制
        - 字符串处理
        - 异常处理
        """
        print("\n" + "=" * 50)
        print("🎮 交互式演示 - 计算器")
        print("=" * 50)
        print("输入 'quit' 或 'exit' 退出")
        print("支持的操作: add, subtract, multiply, divide")
        
        while True:
            try:
                print("\n" + "-" * 30)
                
                # 获取用户输入
                operation = input("请输入操作类型 (add/subtract/multiply/divide): ").strip().lower()
                
                if operation in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if operation not in ['add', 'subtract', 'multiply', 'divide']:
                    print("❌ 无效的操作类型")
                    continue
                
                # 获取数字
                try:
                    a = float(input("请输入第一个数字: "))
                    b = float(input("请输入第二个数字: "))
                except ValueError:
                    print("❌ 请输入有效的数字")
                    continue
                
                # 执行计算
                result = self.manager.execute_tool('calculator', 
                                                 operation=operation, a=a, b=b)
                
                # 显示结果
                if result.status == 'success':
                    print(f"✅ 结果: {result.content['expression']}")
                else:
                    print(f"❌ 错误: {result.error_message}")
                    
            except KeyboardInterrupt:
                print("\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"💥 发生未预期的错误: {str(e)}")
    
    def show_tool_info(self):
        """
        显示工具信息
        
        学习要点：
        - 信息的格式化展示
        - 字典数据的处理
        - 条件判断和循环
        """
        print("\n" + "=" * 50)
        print("ℹ️  工具信息")
        print("=" * 50)
        
        tools = self.manager.list_tools()
        print(f"已注册工具数量: {len(tools)}")
        
        for tool_name in tools:
            info = self.manager.get_tool_info(tool_name)
            if info:
                print(f"\n🔧 工具: {info['name']}")
                print(f"   描述: {info['description']}")
                print(f"   参数要求:")
                
                # 显示schema信息
                schema = info['schema']
                if 'properties' in schema:
                    for prop_name, prop_info in schema['properties'].items():
                        required = prop_name in schema.get('required', [])
                        req_mark = " (必需)" if required else " (可选)"
                        print(f"     - {prop_name}: {prop_info.get('type', 'unknown')}{req_mark}")
                        if 'description' in prop_info:
                            print(f"       {prop_info['description']}")
    
    def run_all_demos(self):
        """
        运行所有演示
        
        学习要点：
        - 程序流程的组织
        - 方法的调用顺序
        - 用户交互的设计
        """
        try:
            # 显示工具信息
            self.show_tool_info()
            
            # 基础演示
            self.run_basic_demo()
            
            # 错误处理演示
            self.run_error_handling_demo()
            
            # 询问是否运行交互式演示
            print("\n" + "=" * 50)
            response = input("是否运行交互式演示？(y/n): ").strip().lower()
            if response in ['y', 'yes', '是']:
                self.run_interactive_demo()
            
        except Exception as e:
            print(f"💥 运行演示时发生错误: {str(e)}")
        finally:
            print("\n🎉 演示程序结束")


def main():
    """
    主函数
    
    学习要点：
    - 程序入口点的设计
    - 异常处理的最佳实践
    - 程序的整体结构
    """
    try:
        # 创建并运行演示
        demo = ToolFrameworkDemo()
        demo.run_all_demos()
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"💥 程序运行时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    程序入口点
    
    学习要点：
    - if __name__ == "__main__": 的作用
    - 模块的执行方式
    - 程序的启动流程
    """
    print("🐍 欢迎来到 Python 工具框架学习项目！")
    print("这是Python基础学习项目")
    print()
    
    main()