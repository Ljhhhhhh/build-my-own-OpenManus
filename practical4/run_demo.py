"""
快速演示脚本 - 项目4工具调用代理

这是一个简化的演示脚本，用于快速测试工具调用代理的功能。
适合初学者理解基本概念和快速验证系统功能。

学习要点：
- 简化的程序结构
- 基本的异步编程
- 环境变量的使用
- 错误处理的基础
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import ToolCallingAgent
from tools import CalculatorTool, TextProcessorTool


async def quick_demo():
    """快速演示函数"""
    print("🚀 工具调用代理快速演示")
    print("=" * 40)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未找到 OPENAI_API_KEY 环境变量")
        print("请设置您的OpenAI API密钥：")
        print("Windows: set OPENAI_API_KEY=your_api_key_here")
        print("Linux/Mac: export OPENAI_API_KEY=your_api_key_here")
        return
    
    try:
        # 创建代理
        print("🤖 正在初始化代理...")
        agent = ToolCallingAgent(api_key=api_key)
        
        # 注册工具
        agent.register_tool(CalculatorTool())
        agent.register_tool(TextProcessorTool())
        print("✅ 代理初始化完成")
        
        # 测试用例
        test_cases = [
            "计算 25 * 4 + 10",
            "将文本 'hello world' 转换为大写"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}: {test_case}")
            print("🤔 代理思考中...")
            
            response = await agent.process_request(test_case)
            print(f"💬 代理回复: {response}")
        
        print(f"\n🎉 演示完成！")
        
        # 显示统计
        stats = agent.get_stats()
        print(f"📊 统计: 对话 {stats['conversation_length']} 轮，工具 {stats['available_tools']} 个")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


if __name__ == "__main__":
    asyncio.run(quick_demo())