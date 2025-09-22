"""
工具调用代理 - 项目4的核心代理类

这个模块实现了一个能够智能调用工具的AI代理。
代理能够理解用户请求，选择合适的工具，并执行相应的操作。

学习要点：
1. LLM集成 - 如何与OpenAI API交互
2. 工具调用 - 如何让LLM选择和使用工具
3. JSON解析 - 处理LLM的结构化输出
4. 异步编程 - 提高性能的异步操作
5. 错误处理 - 健壮的异常处理机制
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from tools import ToolManager, BaseTool, ToolResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolCallingAgent:
    """
    工具调用代理类
    
    这个类是项目4的核心，它集成了LLM和工具系统，
    能够理解用户请求并智能地调用相应的工具。
    
    主要功能：
    1. 与OpenAI GPT模型交互
    2. 管理和调用各种工具
    3. 解析LLM的工具调用请求
    4. 处理工具执行结果
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        """
        初始化工具调用代理
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的GPT模型名称
            base_url: 自定义API端点（可选）
        """
        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.tool_manager = ToolManager()
        self.conversation_history = []
        
        logger.info(f"ToolCallingAgent initialized with model: {model}, base_url: {base_url}")
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        注册一个工具到代理
        
        Args:
            tool: 要注册的工具实例
        """
        self.tool_manager.register_tool(tool)
        logger.info(f"Tool registered: {tool.name}")
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的schema，用于LLM的function calling
        
        Returns:
            工具schema列表，符合OpenAI function calling格式
        """
        tools_schema = []
        for tool_info in self.tool_manager.list_tools():
            # tool_info 是一个字典，包含 name, description, schema, stats
            schema = tool_info['schema']
            # 转换为OpenAI function calling格式
            function_schema = {
                "type": "function",
                "function": {
                    "name": tool_info['name'],
                    "description": tool_info['description'],
                    "parameters": schema
                }
            }
            tools_schema.append(function_schema)
        
        return tools_schema
    
    async def process_request(self, user_message: str) -> str:
        """
        处理用户请求的主要方法
        
        Args:
            user_message: 用户的输入消息
            
        Returns:
            代理的响应消息
        """
        try:
            # 添加用户消息到对话历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # 准备系统提示
            system_prompt = self._get_system_prompt()
            
            # 准备消息列表
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history
            ]
            
            # 获取工具schema
            tools_schema = self.get_tools_schema()
            
            # 调用LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_schema if tools_schema else None,
                tool_choice="auto" if tools_schema else None,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # 检查是否有工具调用
            if message.tool_calls:
                return await self._handle_tool_calls(message)
            else:
                # 没有工具调用，直接返回LLM的回复
                assistant_message = message.content
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": assistant_message
                })
                return assistant_message
                
        except Exception as e:
            error_msg = f"处理请求时发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _handle_tool_calls(self, message) -> str:
        """
        处理LLM的工具调用请求
        
        Args:
            message: 包含工具调用的LLM消息
            
        Returns:
            处理结果的响应消息
        """
        # 添加助手消息到历史
        self.conversation_history.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                } for call in message.tool_calls
            ]
        })
        
        # 执行工具调用
        tool_results = []
        for tool_call in message.tool_calls:
            try:
                # 解析工具调用参数
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Calling tool: {function_name} with args: {function_args}")
                
                # 执行工具 - 使用**解包字典参数为关键字参数
                result = await self.tool_manager.execute_tool(function_name, **function_args)
                
                # 添加工具结果到历史
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": json.dumps({
                        "success": result.is_success,
                        "result": result.content,
                        "error": result.error_message
                    }, ensure_ascii=False)
                })
                
            except Exception as e:
                error_msg = f"工具调用失败: {str(e)}"
                logger.error(error_msg)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": json.dumps({
                        "success": False,
                        "result": None,
                        "error": error_msg
                    }, ensure_ascii=False)
                })
        
        # 添加工具结果到对话历史
        self.conversation_history.extend(tool_results)
        
        # 再次调用LLM获取最终回复
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            *self.conversation_history
        ]
        
        final_response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        final_message = final_response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": final_message
        })
        
        return final_message
    
    def _get_system_prompt(self) -> str:
        """
        获取系统提示词
        
        Returns:
            系统提示词字符串
        """
        available_tools = self.tool_manager.list_tools()
        tools_info = []
        
        for tool_info in available_tools:
            # tool_info 是一个字典，包含 name, description, schema, stats
            tools_info.append(f"- {tool_info['name']}: {tool_info['description']}")
        
        tools_description = "\n".join(tools_info) if tools_info else "当前没有可用的工具"
        
        return """你是一个智能助手，能够使用各种工具来帮助用户完成任务。

可用工具：
{tools_description}

请根据用户的请求，选择合适的工具来完成任务。如果需要使用工具，请调用相应的函数。
如果不需要使用工具，请直接回答用户的问题。

重要指导原则：
1. 仔细分析用户的需求
2. 选择最合适的工具
3. 正确传递参数
4. 当工具执行完成后，基于工具返回的结果直接给出最终答案
5. 绝对不要生成任何代码、函数调用或代码块
6. 不要使用```符号包围任何内容
7. 如果是计算问题，直接说出计算结果，例如："计算结果是 6"
8. 如果是文本处理，直接展示处理后的结果
9. 用自然语言描述结果，不要使用技术术语或代码格式

示例：
- 用户问："帮我计算 1 + 2"
- 工具返回：result: 3
- 正确回答："计算结果是 3"
- 错误回答：不要生成任何包含代码的内容

记住：你的回答应该是纯文本，面向普通用户，不包含任何代码或技术格式。
"""
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取代理统计信息
        
        Returns:
            包含统计信息的字典
        """
        return {
            "conversation_length": len(self.conversation_history),
            "available_tools": len(self.tool_manager.list_tools()),
            "tool_stats": self.tool_manager.get_stats()
        }


# 使用示例和测试代码
async def test_tool_calling_agent():
    """测试工具调用代理的功能"""
    import os
    from tools import CalculatorTool, TextProcessorTool
    
    # 从环境变量获取API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置OPENAI_API_KEY环境变量")
        return
    
    # 创建代理
    agent = ToolCallingAgent(api_key)
    
    # 注册工具
    agent.register_tool(CalculatorTool())
    agent.register_tool(TextProcessorTool())
    
    # 测试用例
    test_cases = [
        "用计算工具计算 15 * 23 + 45",
        "用文本处理工具将文本 'Hello World' 转换为大写",
        "用文本处理工具分析这段文本的单词数量：'Python is a great programming language'"
    ]
    
    print("=== 工具调用代理测试 ===")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case}")
        print("-" * 50)
        
        try:
            response = await agent.process_request(test_case)
            print(f"回复: {response}")
        except Exception as e:
            print(f"错误: {e}")
    
    # 显示统计信息
    print(f"\n=== 统计信息 ===")
    stats = agent.get_stats()
    print(f"对话轮数: {stats['conversation_length']}")
    print(f"可用工具: {stats['available_tools']}")
    print(f"工具统计: {stats['tool_stats']}")


if __name__ == "__main__":
    asyncio.run(test_tool_calling_agent())