"""
项目4主程序 - 工具调用代理演示

这是项目4的主入口程序，展示了如何使用工具调用代理：
1. 配置和初始化系统
2. 注册各种工具
3. 与用户进行交互
4. 演示LLM的工具调用能力

学习要点：
- 应用程序的入口设计
- 异步编程的实际应用
- 用户交互界面的实现
- 错误处理和优雅退出
- 配置管理的集成
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import ToolCallingAgent
from tools import CalculatorTool, TextProcessorTool
from utils import setup_logger, Config
import logging


class ToolCallingDemo:
    """
    工具调用代理演示类
    
    这个类封装了演示程序的主要逻辑，
    提供了交互式的用户界面来测试代理功能。
    
    学习要点：
    - 类的组织和封装
    - 异步方法的设计
    - 用户输入的处理
    - 程序状态的管理
    """
    
    def __init__(self):
        """初始化演示程序"""
        # 设置日志
        self.logger = setup_logger(
            name="practical4.demo",
            level="INFO",
            log_file="logs/demo.log"
        )
        
        # 加载配置
        try:
            self.config = Config(os.getenv("OPENAI_API_KEY"))
            self.logger.info("配置加载成功")
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            print("❌ 配置加载失败，请检查环境变量设置")
            print("请确保设置了 OPENAI_API_KEY 环境变量")
            sys.exit(1)
        
        # 初始化代理
        self.agent = None
        self.running = True
    
    async def initialize_agent(self):
        """初始化工具调用代理"""
        try:
            self.logger.info("正在初始化工具调用代理...")
            
            # 创建代理
            # 打印配置信息
            print("当前配置信息:", self.config)
            
            self.agent = ToolCallingAgent(
                api_key=self.config.openai_api_key,
                model=self.config.openai_model
            )
            
            # 注册工具
            self.agent.register_tool(CalculatorTool())
            self.agent.register_tool(TextProcessorTool())
            
            self.logger.info("代理初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"代理初始化失败: {e}")
            print(f"❌ 代理初始化失败: {e}")
            return False
    
    def print_welcome(self):
        """打印欢迎信息"""
        print("🤖 欢迎使用工具调用代理演示程序！")
        print("=" * 50)
        print("这个程序展示了AI代理如何智能地调用工具来完成任务。")
        print()
        print("可用工具：")
        print("📊 计算器工具 - 执行数学计算")
        print("📝 文本处理工具 - 处理和分析文本")
        print()
        print("示例问题：")
        print("• 帮我计算 15 * 23 + 45")
        print("• 将文本 'Hello World' 转换为大写")
        print("• 计算圆的面积，半径是5")
        print("• 分析这段文本的单词数量：'Python is great'")
        print()
        print("输入 'quit' 或 'exit' 退出程序")
        print("输入 'clear' 清空对话历史")
        print("输入 'stats' 查看统计信息")
        print("=" * 50)
    
    def print_stats(self):
        """打印统计信息"""
        if self.agent:
            stats = self.agent.get_stats()
            print("\n📈 统计信息:")
            print(f"对话轮数: {stats['conversation_length']}")
            print(f"可用工具: {stats['available_tools']}")
            print("工具使用统计:")
            for tool_name, count in stats['tool_stats'].items():
                print(f"  • {tool_name}: {count} 次")
            print()
    
    async def handle_user_input(self, user_input: str) -> bool:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            bool: 是否继续运行程序
        """
        user_input = user_input.strip()
        
        # 处理特殊命令
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 再见！感谢使用工具调用代理演示程序！")
            return False
        
        elif user_input.lower() == 'clear':
            if self.agent:
                self.agent.clear_history()
                print("🧹 对话历史已清空")
            return True
        
        elif user_input.lower() == 'stats':
            self.print_stats()
            return True
        
        elif not user_input:
            return True
        
        # 处理正常的用户请求
        try:
            print("🤔 代理正在思考...")
            response = await self.agent.process_request(user_input)
            print(f"🤖 代理回复: {response}")
            
        except Exception as e:
            self.logger.error(f"处理用户请求失败: {e}")
            print(f"❌ 处理请求时发生错误: {e}")
        
        return True
    
    async def run_interactive_mode(self):
        """运行交互模式"""
        self.print_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                user_input = input("\n💬 请输入您的问题: ")
                
                # 处理用户输入
                should_continue = await self.handle_user_input(user_input)
                if not should_continue:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，正在退出...")
                break
            except EOFError:
                print("\n\n👋 输入结束，正在退出...")
                break
            except Exception as e:
                self.logger.error(f"交互模式发生错误: {e}")
                print(f"❌ 发生错误: {e}")
    
    async def run_demo_mode(self):
        """运行演示模式（自动测试）"""
        print("🎬 运行演示模式...")
        print("=" * 50)
        
        # 预定义的测试用例
        test_cases = [
            "帮我计算 15 * 23 + 45",
            "将文本 'Hello World' 转换为大写",
            "计算圆的面积，半径是5",
            "分析这段文本的单词数量：'Python is a great programming language'",
            "帮我计算 2的10次方",
            "将这段文本转换为小写：'ARTIFICIAL INTELLIGENCE'"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 测试 {i}: {test_case}")
            print("-" * 30)
            
            try:
                response = await self.agent.process_request(test_case)
                print(f"🤖 回复: {response}")
                
                # 添加延迟，让用户能够看清结果
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"演示测试失败: {e}")
                print(f"❌ 测试失败: {e}")
        
        # 显示最终统计
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        self.print_stats()
    
    async def run(self, mode: str = "interactive"):
        """
        运行演示程序
        
        Args:
            mode: 运行模式 ('interactive' 或 'demo')
        """
        # 初始化代理
        if not await self.initialize_agent():
            return
        
        # 根据模式运行
        if mode == "demo":
            await self.run_demo_mode()
        else:
            await self.run_interactive_mode()


async def main():
    """主函数"""
    # 检查命令行参数
    mode = "interactive"
    if len(sys.argv) > 1:
        if sys.argv[1] in ["demo", "interactive"]:
            mode = sys.argv[1]
        else:
            print("用法: python main.py [demo|interactive]")
            print("  demo: 运行自动演示模式")
            print("  interactive: 运行交互模式（默认）")
            return
    
    # 创建并运行演示程序
    demo = ToolCallingDemo()
    await demo.run(mode)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        logging.error(f"程序运行失败: {e}")
        print(f"程序运行失败: {e}")
        sys.exit(1)