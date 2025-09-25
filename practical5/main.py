"""
项目5：ReAct推理代理 - 主程序

这个文件演示了如何使用ReAct代理解决复杂问题。

学习要点：
- ReAct代理的初始化和配置
- 工具的注册和管理
- 异步编程的实践
- 结果的处理和展示
"""

import asyncio
import json
from pathlib import Path

from agent.react_agent import ReActAgent
from tools.manager import ToolManager
from tools.calculator import CalculatorTool
from tools.text_processor import TextProcessorTool
from utils.config import get_config
from utils.logger import setup_logger


async def main():
    """主程序入口"""
    
    # 设置日志
    logger = setup_logger("practical5.main", level="INFO", log_file="logs/main.log")
    logger.info("=" * 60)
    logger.info("项目5：ReAct推理代理 - 启动")
    logger.info("=" * 60)
    
    try:
        # 1. 加载配置
        config = get_config()
        logger.info("配置加载完成")
        
        # 检查API密钥
        if not config.openai_api_key:
            logger.error("未设置OpenAI API密钥，请在.env文件中设置OPENAI_API_KEY")
            print("\n❌ 错误：未设置OpenAI API密钥")
            print("请按以下步骤设置：")
            print("1. 复制 .env.example 为 .env")
            print("2. 在 .env 文件中设置 OPENAI_API_KEY=your_api_key")
            return
        
        # 2. 创建工具管理器并注册工具
        tool_manager = ToolManager()
        
        # 注册计算器工具
        calculator = CalculatorTool()
        tool_manager.register_tool(calculator)
        
        # 注册文本处理工具
        text_processor = TextProcessorTool()
        tool_manager.register_tool(text_processor)
        
        logger.info(f"已注册 {len(tool_manager)} 个工具")
        
        # 3. 创建ReAct代理
        agent = ReActAgent(
            tool_manager=tool_manager,
            max_steps=8,
            model=config.openai_model,
            temperature=0.1
        )
        
        logger.info("ReAct代理创建完成")
        
        # 4. 测试用例
        test_cases = [
            {
                "name": "简单数学计算",
                "query": "计算 15 + 27 的结果",
                "description": "测试基本的工具调用能力"
            },
            {
                "name": "复杂数学问题",
                "query": "如果一个长方形的长是12，宽是8，那么它的面积是多少？周长又是多少？",
                "description": "测试多步推理和多次工具调用"
            },
            {
                "name": "文本处理任务",
                "query": "将文本'Hello World'转换为大写，然后统计字符数量",
                "description": "测试不同类型工具的组合使用"
            },
            {
                "name": "综合推理问题",
                "query": "我有一段文本'The quick brown fox jumps over the lazy dog'，请帮我：1）统计单词数量，2）转换为大写，3）计算如果每个单词价值5元，总价值是多少？",
                "description": "测试复杂的多步推理能力"
            }
        ]
        
        # 5. 执行测试用例
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"测试用例 {i}: {test_case['name']}")
            print(f"描述: {test_case['description']}")
            print(f"问题: {test_case['query']}")
            print(f"{'='*80}")
            
            logger.info(f"开始执行测试用例 {i}: {test_case['name']}")
            
            try:
                # 执行推理
                result = await agent.solve(test_case['query'])
                
                # 显示结果
                print(f"\n✅ 执行结果:")
                print(f"成功: {'是' if result['success'] else '否'}")
                print(f"最终答案: {result['final_answer']}")
                print(f"推理步数: {result['total_steps']}")
                print(f"执行时间: {result['total_time']:.2f}秒")
                print(f"使用工具: {', '.join(result['summary']['tools_used']) if result['summary']['tools_used'] else '无'}")
                
                # 显示推理轨迹
                print(f"\n📋 推理轨迹:")
                for step in result['execution_trace']:
                    print(f"\n步骤 {step['step_number']} ({step['state']}):")
                    print(f"  思考: {step['thought']}")
                    if step['action']:
                        action_str = json.dumps(step['action'], ensure_ascii=False)
                        print(f"  行动: {action_str}")
                    if step['observation']:
                        print(f"  观察: {step['observation']}")
                
                logger.info(f"测试用例 {i} 执行完成，成功: {result['success']}")
                
            except Exception as e:
                print(f"\n❌ 执行失败: {e}")
                logger.error(f"测试用例 {i} 执行失败: {e}")
            
            # 等待用户确认继续
            if i < len(test_cases):
                input("\n按回车键继续下一个测试用例...")
        
        print(f"\n{'='*80}")
        print("🎉 所有测试用例执行完成！")
        print(f"{'='*80}")
        
        # 显示工具使用统计
        stats = tool_manager.get_stats()
        print(f"\n📊 工具使用统计:")
        print(f"总工具数: {stats['summary']['total_tools']}")
        print(f"总执行次数: {stats['summary']['total_executions']}")
        print(f"成功次数: {stats['summary']['total_successful']}")
        print(f"失败次数: {stats['summary']['total_failed']}")
        
        for tool_name, tool_stats in stats['tools'].items():
            if tool_stats['total_executions'] > 0:
                print(f"\n{tool_name}:")
                print(f"  执行次数: {tool_stats['total_executions']}")
                print(f"  成功率: {tool_stats['successful_executions']/tool_stats['total_executions']*100:.1f}%")
                print(f"  平均耗时: {tool_stats['average_execution_time']:.3f}秒")
        
        logger.info("程序执行完成")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        logger.info("程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        logger.error(f"程序执行出错: {e}")


if __name__ == "__main__":
    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)
    
    # 运行主程序
    asyncio.run(main())