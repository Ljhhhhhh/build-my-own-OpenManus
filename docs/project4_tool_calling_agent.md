### 项目 4：工具调用代理

#### 目标

- 集成 LLM 和工具系统
- 实现智能工具选择
- 学会处理工具调用结果

#### 核心代码实现

```python
# agent/tool_calling_agent.py
import json
import asyncio
from typing import List, Dict, Any, Optional
import openai
from tools.manager import ToolManager, ToolResult, ToolResultStatus
from tools.calculator import CalculatorTool
from tools.weather import WeatherTool

class ToolCallingAgent:
    """工具调用代理"""

    def __init__(self, api_key: str, weather_api_key: str = None):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.tool_manager = ToolManager()

        # 注册基础工具
        self.tool_manager.register_tool(CalculatorTool())
        if weather_api_key:
            self.tool_manager.register_tool(WeatherTool(weather_api_key))

        self.conversation_history = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        tools_info = self.tool_manager.list_tools()
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tools_info
        ])

        return f"""
你是一个智能助手，可以使用以下工具来帮助用户：

{tools_desc}

当用户的请求需要使用工具时，请按照以下格式回复：

json
{{
    "tool_call": {{
        "name": "工具名称",
        "parameters": {{
            "参数名": "参数值"
        }}
    }}
}}


如果不需要使用工具，请直接回复用户的问题。
"""

    async def process_message(self, user_message: str) -> str:
        """处理用户消息"""
        # 添加用户消息
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # 获取LLM响应
        response = await self._get_llm_response()

        # 检查是否需要工具调用
        tool_call = self._extract_tool_call(response)

        if tool_call:
            # 执行工具调用
            tool_result = await self._execute_tool_call(tool_call)

            # 将工具结果添加到对话历史
            self.conversation_history.append({
                "role": "assistant",
                "content": f"我使用了{tool_call['name']}工具，结果是：{tool_result.content}"
            })

            # 让LLM基于工具结果生成最终回复
            final_response = await self._get_llm_response()
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })

            return final_response
        else:
            # 直接回复
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response

    async def _get_llm_response(self) -> str:
        """获取LLM响应"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM调用失败：{str(e)}"

    def _extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """从响应中提取工具调用"""
        try:
            # 查找JSON代码块
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()

                data = json.loads(json_str)
                if "tool_call" in data:
                    return data["tool_call"]
            return None
        except Exception:
            return None

    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> ToolResult:
        """执行工具调用"""
        tool_name = tool_call.get("name")
        parameters = tool_call.get("parameters", {})

        return await self.tool_manager.execute_tool(tool_name, **parameters)

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return self.tool_manager.list_tools()

# 使用示例
async def main():
    agent = ToolCallingAgent(
        api_key="your-openai-api-key",
        weather_api_key="your-weather-api-key"
    )

    print("工具调用代理已启动！")
    print("可用工具：")
    for tool in agent.get_available_tools():
        print(f"- {tool['name']}: {tool['description']}")

    print("\n输入 'quit' 退出")

    while True:
        user_input = input("\n你: ")

        if user_input.lower() == 'quit':
            break

        response = await agent.process_message(user_input)
        print(f"代理: {response}")

if __name__ == "__main__":
    asyncio.run(main())
````

#### 学习要点

1. **工具集成**：LLM 与工具系统的集成
2. **智能选择**：让 LLM 决定何时使用工具
3. **结果处理**：处理工具执行结果并生成回复
4. **对话管理**：维护包含工具调用的对话历史