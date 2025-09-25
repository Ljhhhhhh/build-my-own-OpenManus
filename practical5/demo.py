"""
项目5：ReAct推理代理 - 交互式演示

这个文件提供了一个交互式的命令行界面，让用户可以：
1. 与ReAct代理进行对话
2. 实时查看推理过程
3. 测试不同类型的问题

学习要点：
- 交互式程序设计
- 用户输入处理
- 实时结果展示
- 异常处理和用户体验
"""

import asyncio
import json
import sys
from pathlib import Path

from agent.react_agent import ReActAgent, AgentState
from tools.manager import ToolManager
from tools.calculator import CalculatorTool
from tools.text_processor import TextProcessorTool
from utils.config import get_config
from utils.logger import setup_logger


class ReActDemo:
    """ReAct代理演示类"""
    
    def __init__(self):
        """初始化演示程序"""
        self.logger = setup_logger("practical5.demo", level="INFO")
        self.config = None
        self.agent = None
        self.tool_manager = None
        
    async def initialize(self) -> bool:
        """
        初始化代理和工具
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 加载配置
            self.config = get_config()
            
            # 检查API密钥
            if not self.config.openai_api_key:
                print("❌ 错误：未设置OpenAI API密钥")
                print("请按以下步骤设置：")
                print("1. 复制 .env.example 为 .env")
                print("2. 在 .env 文件中设置 OPENAI_API_KEY=your_api_key")
                return False
            
            # 创建工具管理器
            self.tool_manager = ToolManager()
            
            # 注册工具
            calculator = CalculatorTool()
            self.tool_manager.register_tool(calculator)
            
            text_processor = TextProcessorTool()
            self.tool_manager.register_tool(text_processor)
            
            # 创建代理
            self.agent = ReActAgent(
                tool_manager=self.tool_manager,
                max_steps=10,
                model=self.config.openai_model,
                temperature=0.1
            )
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def show_welcome(self):
        """显示欢迎信息"""
        print("🤖 ReAct推理代理演示程序")
        print("=" * 60)
        print("这是一个基于ReAct模式的智能代理，能够：")
        print("• 进行循环的思考-行动-观察推理")
        print("• 调用工具解决复杂问题")
        print("• 展示完整的推理过程")
        print()
        print("可用工具：")
        tools = self.tool_manager.list_tools()
        for tool in tools:
            print(f"• {tool['name']}: {tool['description']}")
        print()
        print("💡 示例问题：")
        print("• 计算 25 * 4 + 15 的结果")
        print("• 将文本'hello world'转换为大写并统计字符数")
        print("• 如果一个圆的半径是5，计算它的面积（使用π=3.14159）")
        print()
        print("输入 'quit' 或 'exit' 退出程序")
        print("输入 'help' 查看帮助信息")
        print("=" * 60)
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息")
        print("-" * 40)
        print("命令：")
        print("• quit/exit - 退出程序")
        print("• help - 显示此帮助信息")
        print("• clear - 清屏")
        print("• stats - 显示工具使用统计")
        print()
        print("使用技巧：")
        print("• 尽量描述清楚你的问题")
        print("• 可以要求代理执行多个步骤")
        print("• 代理会自动选择合适的工具")
        print("• 推理过程会实时显示")
        print("-" * 40)
    
    def show_stats(self):
        """显示工具使用统计"""
        stats = self.tool_manager.get_stats()
        print("\n📊 工具使用统计")
        print("-" * 40)
        print(f"总工具数: {stats['summary']['total_tools']}")
        print(f"总执行次数: {stats['summary']['total_executions']}")
        print(f"成功次数: {stats['summary']['total_successful']}")
        print(f"失败次数: {stats['summary']['total_failed']}")
        
        if stats['summary']['total_executions'] > 0:
            success_rate = stats['summary']['total_successful'] / stats['summary']['total_executions'] * 100
            print(f"总成功率: {success_rate:.1f}%")
        
        print("\n各工具详情:")
        for tool_name, tool_stats in stats['tools'].items():
            if tool_stats['total_executions'] > 0:
                print(f"\n{tool_name}:")
                print(f"  执行次数: {tool_stats['total_executions']}")
                print(f"  成功次数: {tool_stats['successful_executions']}")
                print(f"  失败次数: {tool_stats['failed_executions']}")
                print(f"  平均耗时: {tool_stats['average_execution_time']:.3f}秒")
        print("-" * 40)
    
    async def process_query(self, query: str):
        """
        处理用户查询
        
        Args:
            query: 用户问题
        """
        print(f"\n🤔 正在思考问题: {query}")
        print("=" * 60)
        
        try:
            # 执行推理
            result = await self.agent.solve(query)
            
            # 显示推理过程
            print("\n🧠 推理过程:")
            print("-" * 40)
            
            for step in result['execution_trace']:
                state_emoji = {
                    'thinking': '💭',
                    'acting': '⚡',
                    'observing': '👀',
                    'finished': '✅',
                    'error': '❌'
                }
                
                emoji = state_emoji.get(step['state'], '🔄')
                print(f"\n{emoji} 步骤 {step['step_number']} ({step['state']}):")
                print(f"   思考: {step['thought']}")
                
                if step['action']:
                    action_str = json.dumps(step['action'], ensure_ascii=False)
                    print(f"   行动: {action_str}")
                
                if step['observation']:
                    print(f"   观察: {step['observation']}")
                
                if step['execution_time']:
                    print(f"   耗时: {step['execution_time']:.3f}秒")
            
            # 显示最终结果
            print("\n" + "=" * 60)
            if result['success']:
                print(f"✅ 最终答案: {result['final_answer']}")
            else:
                print(f"❌ 执行失败: {result['final_answer']}")
            
            print(f"\n📈 执行统计:")
            print(f"   推理步数: {result['total_steps']}")
            print(f"   总耗时: {result['total_time']:.2f}秒")
            print(f"   平均每步: {result['summary']['average_step_time']:.2f}秒")
            print(f"   使用工具: {', '.join(result['summary']['tools_used']) if result['summary']['tools_used'] else '无'}")
            
            if result['summary']['max_steps_reached']:
                print("⚠️  注意: 已达到最大步数限制")
            
        except Exception as e:
            print(f"❌ 处理查询时发生错误: {e}")
            self.logger.error(f"处理查询失败: {e}")
    
    async def run(self):
        """运行演示程序"""
        # 初始化
        if not await self.initialize():
            return
        
        # 显示欢迎信息
        self.show_welcome()
        
        # 主循环
        while True:
            try:
                # 获取用户输入
                query = input("\n🗣️  请输入您的问题: ").strip()
                
                # 处理特殊命令
                if query.lower() in ['quit', 'exit']:
                    print("\n👋 再见！感谢使用ReAct推理代理！")
                    break
                
                elif query.lower() == 'help':
                    self.show_help()
                    continue
                
                elif query.lower() == 'clear':
                    # 清屏
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_welcome()
                    continue
                
                elif query.lower() == 'stats':
                    self.show_stats()
                    continue
                
                elif not query:
                    print("⚠️  请输入有效的问题")
                    continue
                
                # 处理用户问题
                await self.process_query(query)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  程序被中断")
                break
            except EOFError:
                print("\n\n👋 程序结束")
                break
            except Exception as e:
                print(f"\n❌ 发生未知错误: {e}")
                self.logger.error(f"主循环错误: {e}")


async def main():
    """主函数"""
    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)
    
    # 创建并运行演示程序
    demo = ReActDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())