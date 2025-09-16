# OpenManus AI 应用开发实践指南

## 阶段一：Python 基础强化 (第 1-2 周)

### 项目 1：简单聊天机器人

#### 目标

- 掌握 OpenAI API 调用
- 理解异步编程基础
- 学会基本的错误处理

#### 核心代码实现

```python
# chatbot_v1.py
import asyncio
import openai
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class SimpleChatBot:
    def __init__(self, api_key: str = None):
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.conversation_history: List[Dict[str, str]] = []

    async def chat(self, user_message: str) -> str:
        """发送消息并获取回复"""
        try:
            # 添加用户消息到历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=1000,
                temperature=0.7
            )

            # 提取回复
            assistant_message = response.choices[0].message.content

            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"错误：{str(e)}"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

# 使用示例
async def main():
    bot = SimpleChatBot()

    print("聊天机器人已启动！输入 'quit' 退出")

    while True:
        user_input = input("你: ")

        if user_input.lower() == 'quit':
            break

        response = await bot.chat(user_input)
        print(f"机器人: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **异步编程**：理解 `async/await` 的使用
2. **API 调用**：学会处理 HTTP 请求和响应
3. **错误处理**：使用 `try/except` 处理异常
4. **类型注解**：使用 `typing` 模块提高代码可读性

### 项目 2：配置驱动助手

#### 目标

- 学会使用 Pydantic 进行数据验证
- 掌握 TOML 配置文件处理
- 理解配置驱动开发模式

#### 核心代码实现

```python
# config_driven_assistant.py
from pydantic import BaseModel, Field
from typing import Optional, List
import toml
import asyncio
import openai

class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
    api_key: str = Field(description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    max_tokens: int = Field(default=1000, description="最大token数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")

class AssistantConfig(BaseModel):
    """助手配置模型"""
    name: str = Field(description="助手名称")
    description: str = Field(description="助手描述")
    system_prompt: str = Field(description="系统提示词")
    llm: LLMConfig = Field(description="LLM配置")
    max_history: int = Field(default=10, description="最大历史记录数")

class ConfigDrivenAssistant:
    def __init__(self, config_path: str):
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = toml.load(f)

        # 验证配置
        self.config = AssistantConfig(**config_data)

        # 初始化LLM客户端
        self.client = openai.AsyncOpenAI(
            api_key=self.config.llm.api_key,
            base_url=self.config.llm.base_url
        )

        # 初始化对话历史
        self.conversation_history = [
            {"role": "system", "content": self.config.system_prompt}
        ]

    async def process_message(self, user_message: str) -> str:
        """处理用户消息"""
        try:
            # 添加用户消息
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # 限制历史记录长度
            if len(self.conversation_history) > self.config.max_history + 1:
                # 保留系统提示词，删除最旧的对话
                self.conversation_history = (
                    [self.conversation_history[0]] +
                    self.conversation_history[-(self.config.max_history):]
                )

            # 调用LLM
            response = await self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=self.conversation_history,
                max_tokens=self.config.llm.max_tokens,
                temperature=self.config.llm.temperature
            )

            assistant_message = response.choices[0].message.content

            # 添加助手回复
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"处理消息时出错：{str(e)}"

    def get_info(self) -> dict:
        """获取助手信息"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "model": self.config.llm.model,
            "provider": self.config.llm.provider
        }

# 配置文件示例 (assistant_config.toml)
"""
name = "Python编程助手"
description = "专门帮助Python开发的AI助手"
system_prompt = "你是一个专业的Python编程助手，擅长解答Python相关问题，提供代码示例和最佳实践建议。"
max_history = 15

[llm]
provider = "openai"
model = "gpt-3.5-turbo"
api_key = "your-api-key-here"
max_tokens = 1500
temperature = 0.3
"""

# 使用示例
async def main():
    try:
        assistant = ConfigDrivenAssistant("assistant_config.toml")

        print(f"助手信息：{assistant.get_info()}")
        print("助手已启动！输入 'quit' 退出")

        while True:
            user_input = input("\n你: ")

            if user_input.lower() == 'quit':
                break

            response = await assistant.process_message(user_input)
            print(f"助手: {response}")

    except Exception as e:
        print(f"启动助手失败：{e}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **Pydantic 模型**：数据验证和序列化
2. **TOML 配置**：配置文件的读取和解析
3. **配置驱动**：通过配置控制程序行为
4. **错误处理**：配置验证和运行时错误处理

---

## 阶段二：工具系统开发 (第 3-5 周)

### 项目 3：基础工具框架

#### 目标

- 设计抽象基类和接口
- 实现插件架构
- 学会使用 JSON Schema

#### 核心代码实现

```python
# tools/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json
from enum import Enum

class ToolResultStatus(Enum):
    """工具执行结果状态"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

class ToolResult(BaseModel):
    """工具执行结果"""
    status: ToolResultStatus
    content: Any = Field(description="结果内容")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class BaseTool(ABC):
    """工具基类"""

    def __init__(self):
        self._name = self.__class__.__name__.lower().replace('tool', '')
        self._description = self.__doc__ or "No description available"

    @property
    def name(self) -> str:
        """工具名称"""
        return self._name

    @property
    def description(self) -> str:
        """工具描述"""
        return self._description

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的JSON Schema"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数"""
        try:
            # 这里可以使用jsonschema库进行验证
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.get_schema()
        }

# tools/calculator.py
class CalculatorTool(BaseTool):
    """计算器工具，支持基本数学运算"""

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，如 '2 + 3 * 4'"
                }
            },
            "required": ["expression"]
        }

    async def execute(self, expression: str) -> ToolResult:
        """执行计算"""
        try:
            # 安全的数学表达式计算
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return ToolResult(
                    status=ToolResultStatus.ERROR,
                    content=None,
                    error_message="表达式包含不允许的字符"
                )

            result = eval(expression)
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                content=result,
                metadata={"expression": expression}
            )

        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                content=None,
                error_message=f"计算错误：{str(e)}"
            )

# tools/weather.py
import aiohttp

class WeatherTool(BaseTool):
    """天气查询工具"""

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称"
                },
                "country": {
                    "type": "string",
                    "description": "国家代码，如 'CN' 表示中国",
                    "default": "CN"
                }
            },
            "required": ["city"]
        }

    async def execute(self, city: str, country: str = "CN") -> ToolResult:
        """查询天气"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": f"{city},{country}",
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_info = {
                            "city": data["name"],
                            "temperature": data["main"]["temp"],
                            "description": data["weather"][0]["description"],
                            "humidity": data["main"]["humidity"],
                            "pressure": data["main"]["pressure"]
                        }

                        return ToolResult(
                            status=ToolResultStatus.SUCCESS,
                            content=weather_info
                        )
                    else:
                        return ToolResult(
                            status=ToolResultStatus.ERROR,
                            content=None,
                            error_message=f"API请求失败：{response.status}"
                        )

        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                content=None,
                error_message=f"查询天气失败：{str(e)}"
            )

# tools/manager.py
class ToolManager:
    """工具管理器"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [tool.to_dict() for tool in self.tools.values()]

    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                content=None,
                error_message=f"工具 '{name}' 不存在"
            )

        if not tool.validate_parameters(kwargs):
            return ToolResult(
                status=ToolResultStatus.ERROR,
                content=None,
                error_message="参数验证失败"
            )

        return await tool.execute(**kwargs)

# 使用示例
async def main():
    # 创建工具管理器
    manager = ToolManager()

    # 注册工具
    manager.register_tool(CalculatorTool())
    manager.register_tool(WeatherTool("your-weather-api-key"))

    # 列出工具
    print("可用工具：")
    for tool_info in manager.list_tools():
        print(f"- {tool_info['name']}: {tool_info['description']}")

    # 执行计算
    result = await manager.execute_tool("calculator", expression="2 + 3 * 4")
    print(f"\n计算结果：{result.content}")

    # 执行天气查询
    result = await manager.execute_tool("weather", city="北京")
    if result.status == ToolResultStatus.SUCCESS:
        print(f"\n天气信息：{result.content}")
    else:
        print(f"\n查询失败：{result.error_message}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### 学习要点

1. **抽象基类**：使用 ABC 定义接口
2. **JSON Schema**：定义工具参数结构
3. **插件架构**：动态注册和管理工具
4. **错误处理**：统一的结果格式和错误处理

### 项目 4：工具调用代理

#### 目标

- 集成 LLM 和工具系统
- 实现智能工具选择
- 学会处理工具调用结果

#### 核心代码实现

````python
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

---

## 阶段三：ReAct 模式实现 (第 6-8 周)

### 项目 5：思考-行动循环

#### 目标

- 实现 ReAct 推理模式
- 设计状态机管理
- 学会循环控制和终止条件

#### 核心代码实现

```python
# agent/react_agent.py
from enum import Enum
from typing import List, Dict, Any, Optional
import asyncio
import json
import openai
from tools.manager import ToolManager
from dataclasses import dataclass

class AgentState(Enum):
    """代理状态"""
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    FINISHED = "finished"
    ERROR = "error"

@dataclass
class ReActStep:
    """ReAct步骤"""
    step_number: int
    thought: str
    action: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    state: AgentState = AgentState.THINKING

class ReActAgent:
    """ReAct推理代理"""

    def __init__(self, api_key: str, max_steps: int = 10):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.tool_manager = ToolManager()
        self.max_steps = max_steps
        self.current_step = 0
        self.steps: List[ReActStep] = []
        self.state = AgentState.THINKING

        # 注册工具（这里可以扩展）
        from tools.calculator import CalculatorTool
        from tools.weather import WeatherTool
        self.tool_manager.register_tool(CalculatorTool())

    def _get_react_prompt(self, user_query: str) -> str:
        """获取ReAct提示词"""
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tool_manager.list_tools()
        ])

        steps_history = ""
        for step in self.steps:
            steps_history += f"\nStep {step.step_number}:\n"
            steps_history += f"Thought: {step.thought}\n"
            if step.action:
                steps_history += f"Action: {json.dumps(step.action, ensure_ascii=False)}\n"
            if step.observation:
                steps_history += f"Observation: {step.observation}\n"

        return f"""
你是一个使用ReAct（Reasoning and Acting）模式的智能代理。

用户问题：{user_query}

可用工具：
{tools_info}

你需要按照以下格式进行推理和行动：

Thought: [你的思考过程]
Action: {{"name": "工具名称", "parameters": {{"参数名": "参数值"}}}}
Observation: [工具执行结果]

如果你认为已经获得了足够的信息来回答用户问题，请输出：
Thought: [最终思考]
Final Answer: [最终答案]

历史步骤：{steps_history}

请继续下一步：
        """

    async def solve(self, user_query: str) -> str:
        """解决用户问题"""
        self.current_step = 0
        self.steps = []
        self.state = AgentState.THINKING

        while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
            try:
                await self._execute_step(user_query)
            except Exception as e:
                self.state = AgentState.ERROR
                return f"执行过程中出错：{str(e)}"

        if self.state == AgentState.FINISHED:
            return self._get_final_answer()
        else:
            return "达到最大步数限制，未能完成任务"

    async def _execute_step(self, user_query: str):
        """执行一个ReAct步骤"""
        self.current_step += 1

        # 获取LLM响应
        prompt = self._get_react_prompt(user_query)
        response = await self._get_llm_response(prompt)

        # 解析响应
        step = self._parse_response(response)
        self.steps.append(step)

        # 根据步骤类型执行相应操作
        if "Final Answer" in response:
            self.state = AgentState.FINISHED
        elif step.action:
            # 执行工具调用
            self.state = AgentState.ACTING
            result = await self.tool_manager.execute_tool(
                step.action["name"],
                **step.action.get("parameters", {})
            )

            # 记录观察结果
            step.observation = str(result.content) if result.status.value == "success" else result.error_message
            step.state = AgentState.OBSERVING

            # 回到思考状态
            self.state = AgentState.THINKING

    def _parse_response(self, response: str) -> ReActStep:
        """解析LLM响应"""
        lines = response.strip().split('\n')
        thought = ""
        action = None

        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                try:
                    action_str = line[7:].strip()
                    action = json.loads(action_str)
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试简单解析
                    pass

        return ReActStep(
            step_number=self.current_step,
            thought=thought,
            action=action,
            state=self.state
        )

    async def _get_llm_response(self, prompt: str) -> str:
        """获取LLM响应"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM调用失败：{str(e)}")

    def _get_final_answer(self) -> str:
        """获取最终答案"""
        if self.steps:
            last_step = self.steps[-1]
            # 从最后一步的思考中提取最终答案
            # 这里可以进一步优化解析逻辑
            return last_step.thought
        return "未找到答案"

    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        return [
            {
                "step": step.step_number,
                "thought": step.thought,
                "action": step.action,
                "observation": step.observation,
                "state": step.state.value
            }
            for step in self.steps
        ]

# 使用示例
async def main():
    agent = ReActAgent(api_key="your-openai-api-key")

    print("ReAct代理已启动！")

    # 测试问题
    queries = [
        "计算 (15 + 25) * 3 的结果",
        "如果一个正方形的面积是 64，那么它的周长是多少？",
        "帮我计算复利：本金1000元，年利率5%，投资3年的最终金额"
    ]

    for query in queries:
        print(f"\n问题：{query}")
        print("=" * 50)

        answer = await agent.solve(query)
        print(f"答案：{answer}")

        print("\n执行轨迹：")
        for trace in agent.get_execution_trace():
            print(f"步骤 {trace['step']}: {trace['thought']}")
            if trace['action']:
                print(f"  行动: {trace['action']}")
            if trace['observation']:
                print(f"  观察: {trace['observation']}")

        print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **ReAct 模式**：思考-行动-观察的循环
2. **状态机**：管理代理的不同状态
3. **步骤追踪**：记录推理过程
4. **循环控制**：设置最大步数和终止条件

---

## 实践建议

### 1. 循序渐进

- 每个项目都要完全理解后再进入下一个
- 多写注释，理解每行代码的作用
- 遇到问题及时查阅文档和资料

### 2. 动手实践

- 不要只看代码，一定要亲自运行
- 尝试修改参数，观察不同的效果
- 添加日志输出，理解程序执行流程

### 3. 扩展练习

- 为每个项目添加新功能
- 尝试集成其他 API 和服务

---

## 阶段四：高级功能集成

### 项目 6: 多模态代理

#### 项目目标

- 集成图像处理和浏览器自动化功能
- 实现多模态输入处理（文本+图像）
- 构建能够理解和操作网页的智能代理

#### 核心代码实现

**1. 多模态工具基类**

```python
# src/tools/multimodal_base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import base64
import io

class MultimodalTool(ABC):
    """多模态工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self,
                     text_input: Optional[str] = None,
                     image_input: Optional[Union[str, Image.Image]] = None,
                     **kwargs) -> Dict[str, Any]:
        """执行多模态工具"""
        pass

    def encode_image(self, image: Union[str, Image.Image]) -> str:
        """将图像编码为base64字符串"""
        if isinstance(image, str):
            # 如果是文件路径
            with open(image, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        elif isinstance(image, Image.Image):
            # 如果是PIL图像对象
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            raise ValueError("不支持的图像格式")

    def decode_image(self, base64_string: str) -> Image.Image:
        """将base64字符串解码为PIL图像"""
        image_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(image_data))
```

**2. 图像分析工具**

```python
# src/tools/image_analyzer.py
import openai
from typing import Dict, Any, Optional, Union
from PIL import Image
from .multimodal_base import MultimodalTool

class ImageAnalyzer(MultimodalTool):
    """图像分析工具"""

    def __init__(self, api_key: str):
        super().__init__(
            name="image_analyzer",
            description="分析图像内容，提取文字、识别对象、描述场景"
        )
        self.client = openai.OpenAI(api_key=api_key)

    async def execute(self,
                     text_input: Optional[str] = None,
                     image_input: Optional[Union[str, Image.Image]] = None,
                     analysis_type: str = "describe",
                     **kwargs) -> Dict[str, Any]:
        """执行图像分析"""
        if not image_input:
            return {"error": "需要提供图像输入"}

        try:
            # 编码图像
            base64_image = self.encode_image(image_input)

            # 构建提示词
            if analysis_type == "describe":
                prompt = text_input or "请详细描述这张图片的内容"
            elif analysis_type == "ocr":
                prompt = "请提取图片中的所有文字内容"
            elif analysis_type == "objects":
                prompt = "请识别图片中的所有对象和物品"
            else:
                prompt = text_input or "请分析这张图片"

            # 调用GPT-4V
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            result = response.choices[0].message.content

            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": result,
                "prompt_used": prompt
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

**3. 浏览器自动化工具**

```python
# src/tools/browser_automation.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import io
from typing import Dict, Any, Optional, List
from .multimodal_base import MultimodalTool

class BrowserTool(MultimodalTool):
    """浏览器自动化工具"""

    def __init__(self, headless: bool = False):
        super().__init__(
            name="browser_tool",
            description="自动化浏览器操作：导航、点击、输入、截图等"
        )
        self.headless = headless
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        """设置浏览器驱动"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    async def execute(self,
                     text_input: Optional[str] = None,
                     image_input: Optional[Image.Image] = None,
                     action: str = "navigate",
                     **kwargs) -> Dict[str, Any]:
        """执行浏览器操作"""
        try:
            if action == "navigate":
                return await self._navigate(kwargs.get('url', text_input))
            elif action == "click":
                return await self._click(kwargs.get('selector', text_input))
            elif action == "input":
                return await self._input(
                    kwargs.get('selector'),
                    kwargs.get('text', text_input)
                )
            elif action == "screenshot":
                return await self._screenshot()
            elif action == "get_text":
                return await self._get_text(kwargs.get('selector', text_input))
            elif action == "scroll":
                return await self._scroll(kwargs.get('direction', 'down'))
            else:
                return {"error": f"不支持的操作: {action}"}

        except Exception as e:
            return {"error": str(e)}

    async def _navigate(self, url: str) -> Dict[str, Any]:
        """导航到指定URL"""
        self.driver.get(url)
        time.sleep(2)  # 等待页面加载
        return {
            "success": True,
            "action": "navigate",
            "url": url,
            "title": self.driver.title
        }

    async def _click(self, selector: str) -> Dict[str, Any]:
        """点击元素"""
        element = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()
        return {
            "success": True,
            "action": "click",
            "selector": selector
        }

    async def _input(self, selector: str, text: str) -> Dict[str, Any]:
        """输入文本"""
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.clear()
        element.send_keys(text)
        return {
            "success": True,
            "action": "input",
            "selector": selector,
            "text": text
        }

    async def _screenshot(self) -> Dict[str, Any]:
        """截取屏幕截图"""
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        base64_image = self.encode_image(image)

        return {
            "success": True,
            "action": "screenshot",
            "image": base64_image,
            "size": image.size
        }

    async def _get_text(self, selector: str) -> Dict[str, Any]:
        """获取元素文本"""
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        text = element.text
        return {
            "success": True,
            "action": "get_text",
            "selector": selector,
            "text": text
        }

    async def _scroll(self, direction: str) -> Dict[str, Any]:
        """滚动页面"""
        if direction == "down":
            self.driver.execute_script("window.scrollBy(0, 500);")
        elif direction == "up":
            self.driver.execute_script("window.scrollBy(0, -500);")
        elif direction == "top":
            self.driver.execute_script("window.scrollTo(0, 0);")
        elif direction == "bottom":
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        return {
            "success": True,
            "action": "scroll",
            "direction": direction
        }

    def close(self):
         """关闭浏览器"""
         if self.driver:
             self.driver.quit()
```

**4. 多模态代理主类**

```python
# src/agents/multimodal_agent.py
import asyncio
from typing import Dict, Any, List, Optional, Union
from PIL import Image
from ..tools.image_analyzer import ImageAnalyzer
from ..tools.browser_automation import BrowserTool
from ..agents.react_agent import ReActAgent

class MultimodalAgent(ReActAgent):
    """多模态智能代理"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # 初始化多模态工具
        self.image_analyzer = ImageAnalyzer(config['openai_api_key'])
        self.browser_tool = BrowserTool(headless=config.get('headless', False))

        # 注册工具
        self.tools.update({
            'analyze_image': self.image_analyzer,
            'browser_action': self.browser_tool
        })

    async def process_multimodal_input(self,
                                     text: Optional[str] = None,
                                     image: Optional[Union[str, Image.Image]] = None,
                                     task_type: str = "general") -> Dict[str, Any]:
        """处理多模态输入"""
        context = {
            "text_input": text,
            "has_image": image is not None,
            "task_type": task_type
        }

        # 如果有图像输入，先分析图像
        if image:
            image_analysis = await self.image_analyzer.execute(
                text_input="请详细分析这张图片，包括内容、文字、对象等",
                image_input=image
            )
            context["image_analysis"] = image_analysis

        # 构建任务描述
        if task_type == "web_automation":
            task_description = self._build_web_task(text, context)
        elif task_type == "image_analysis":
            task_description = self._build_image_task(text, context)
        else:
            task_description = text or "请处理提供的多模态输入"

        # 执行ReAct循环
        return await self.solve(task_description, context=context)

    def _build_web_task(self, text: str, context: Dict) -> str:
        """构建网页自动化任务描述"""
        base_task = text or "执行网页操作"

        if context.get("has_image"):
            return f"""{base_task}

可用信息：
- 图像分析结果：{context.get('image_analysis', {}).get('result', '无')}
- 可用操作：导航、点击、输入、截图、获取文本、滚动

请根据图像内容和用户需求，制定并执行网页操作计划。"""
        else:
            return f"{base_task}\n\n请使用浏览器工具完成网页操作任务。"

    def _build_image_task(self, text: str, context: Dict) -> str:
        """构建图像分析任务描述"""
        base_task = text or "分析图像内容"

        if context.get("image_analysis"):
            analysis = context["image_analysis"].get('result', '')
            return f"""{base_task}

图像分析结果：
{analysis}

请基于以上分析结果，回答用户的问题或完成指定任务。"""
        else:
            return base_task

    async def web_screenshot_and_analyze(self, url: str,
                                       analysis_prompt: str = None) -> Dict[str, Any]:
        """访问网页并分析截图"""
        try:
            # 导航到网页
            nav_result = await self.browser_tool.execute(
                action="navigate", url=url
            )

            if not nav_result.get("success"):
                return {"error": f"无法访问网页: {nav_result.get('error')}"}

            # 截图
            screenshot_result = await self.browser_tool.execute(
                action="screenshot"
            )

            if not screenshot_result.get("success"):
                return {"error": f"截图失败: {screenshot_result.get('error')}"}

            # 分析截图
            image_base64 = screenshot_result["image"]
            image = self.image_analyzer.decode_image(image_base64)

            analysis_result = await self.image_analyzer.execute(
                text_input=analysis_prompt or "请分析这个网页的内容和布局",
                image_input=image
            )

            return {
                "success": True,
                "url": url,
                "page_title": nav_result.get("title"),
                "screenshot": image_base64,
                "analysis": analysis_result
            }

        except Exception as e:
            return {"error": str(e)}

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'browser_tool'):
            self.browser_tool.close()

# 使用示例
async def main():
    config = {
        'openai_api_key': 'your-api-key',
        'model': 'gpt-4',
        'headless': False
    }

    agent = MultimodalAgent(config)

    try:
        # 示例1：分析图像
        print("=== 图像分析示例 ===")
        result1 = await agent.process_multimodal_input(
            text="这张图片中有什么内容？请详细描述",
            image="path/to/your/image.jpg",
            task_type="image_analysis"
        )
        print(f"结果: {result1}")

        # 示例2：网页截图分析
        print("\n=== 网页分析示例 ===")
        result2 = await agent.web_screenshot_and_analyze(
            url="https://www.example.com",
            analysis_prompt="请分析这个网页的主要功能和内容结构"
        )
        print(f"结果: {result2}")

        # 示例3：基于图像的网页操作
        print("\n=== 多模态网页操作示例 ===")
        result3 = await agent.process_multimodal_input(
            text="请根据这张截图，帮我点击登录按钮",
            image="path/to/screenshot.png",
            task_type="web_automation"
        )
        print(f"结果: {result3}")

    finally:
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **多模态处理**：同时处理文本和图像输入
2. **工具集成**：将不同类型的工具整合到统一接口
3. **上下文管理**：在多模态环境中维护任务上下文
4. **资源管理**：正确管理浏览器等外部资源

---

### 项目 7: 沙箱执行环境

#### 项目目标

- 实现安全的代码执行环境
- 支持多种编程语言
- 提供资源限制和安全隔离
- 集成到 AI 代理工作流中

#### 核心代码实现

**1. 沙箱基类**

```python
# src/sandbox/base_sandbox.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import uuid

@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: str
    error: str
    execution_time: float
    memory_usage: Optional[int] = None
    exit_code: Optional[int] = None
    session_id: str = ""

@dataclass
class SandboxConfig:
    """沙箱配置"""
    timeout: int = 30  # 超时时间（秒）
    memory_limit: int = 512  # 内存限制（MB）
    cpu_limit: float = 1.0  # CPU限制
    network_access: bool = False  # 网络访问
    file_system_access: bool = False  # 文件系统访问
    allowed_imports: List[str] = None  # 允许的导入模块

class BaseSandbox(ABC):
    """沙箱基类"""

    def __init__(self, config: SandboxConfig):
        self.config = config
        self.sessions = {}  # 活跃会话

    @abstractmethod
    async def execute(self, code: str, language: str = "python",
                     session_id: Optional[str] = None) -> ExecutionResult:
        """执行代码"""
        pass

    @abstractmethod
    async def create_session(self) -> str:
        """创建新会话"""
        pass

    @abstractmethod
    async def destroy_session(self, session_id: str) -> bool:
        """销毁会话"""
        pass

    def generate_session_id(self) -> str:
        """生成会话ID"""
        return str(uuid.uuid4())
```

**2. Docker 沙箱实现**

```python
# src/sandbox/docker_sandbox.py
import docker
import asyncio
import tempfile
import os
from typing import Dict, Any, Optional
from .base_sandbox import BaseSandbox, ExecutionResult, SandboxConfig

class DockerSandbox(BaseSandbox):
    """Docker沙箱实现"""

    def __init__(self, config: SandboxConfig):
        super().__init__(config)
        self.client = docker.from_env()
        self.language_images = {
            'python': 'python:3.9-slim',
            'javascript': 'node:16-slim',
            'java': 'openjdk:11-slim',
            'go': 'golang:1.19-slim'
        }

    async def execute(self, code: str, language: str = "python",
                     session_id: Optional[str] = None) -> ExecutionResult:
        """在Docker容器中执行代码"""
        start_time = time.time()

        try:
            # 选择镜像
            image = self.language_images.get(language)
            if not image:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"不支持的语言: {language}",
                    execution_time=0
                )

            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # 运行容器
                result = await self._run_container(image, temp_file, language)
                execution_time = time.time() - start_time

                return ExecutionResult(
                    success=result['exit_code'] == 0,
                    output=result['output'],
                    error=result['error'],
                    execution_time=execution_time,
                    exit_code=result['exit_code'],
                    session_id=session_id or ""
                )

            finally:
                # 清理临时文件
                os.unlink(temp_file)

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )

    async def _run_container(self, image: str, code_file: str, language: str) -> Dict[str, Any]:
        """运行Docker容器"""
        # 构建运行命令
        command = self._get_run_command(language, os.path.basename(code_file))

        # 容器配置
        container_config = {
            'image': image,
            'command': command,
            'volumes': {os.path.dirname(code_file): {'bind': '/workspace', 'mode': 'ro'}},
            'working_dir': '/workspace',
            'mem_limit': f'{self.config.memory_limit}m',
            'cpu_period': 100000,
            'cpu_quota': int(100000 * self.config.cpu_limit),
            'network_disabled': not self.config.network_access,
            'remove': True,
            'stdout': True,
            'stderr': True
        }

        # 运行容器
        container = self.client.containers.run(**container_config, detach=True)

        try:
            # 等待执行完成
            result = container.wait(timeout=self.config.timeout)

            # 获取输出
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')

            # 分离stdout和stderr
            output_lines = []
            error_lines = []

            for line in logs.split('\n'):
                if line.strip():
                    output_lines.append(line)

            return {
                'exit_code': result['StatusCode'],
                'output': '\n'.join(output_lines),
                'error': '' if result['StatusCode'] == 0 else '\n'.join(output_lines)
            }

        except docker.errors.ContainerError as e:
            return {
                'exit_code': e.exit_status,
                'output': '',
                'error': str(e)
            }
        except Exception as e:
            return {
                'exit_code': -1,
                'output': '',
                'error': str(e)
            }

    def _get_file_extension(self, language: str) -> str:
        """获取文件扩展名"""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'go': '.go'
        }
        return extensions.get(language, '.txt')

    def _get_run_command(self, language: str, filename: str) -> List[str]:
        """获取运行命令"""
        commands = {
            'python': ['python', filename],
            'javascript': ['node', filename],
            'java': ['sh', '-c', f'javac {filename} && java {filename[:-5]}'],
            'go': ['go', 'run', filename]
        }
        return commands.get(language, ['cat', filename])

    async def create_session(self) -> str:
        """创建新会话"""
        session_id = self.generate_session_id()
        # Docker沙箱通常是无状态的，这里只是记录会话
        self.sessions[session_id] = {
            'created_at': time.time(),
            'last_used': time.time()
        }
        return session_id

    async def destroy_session(self, session_id: str) -> bool:
         """销毁会话"""
         if session_id in self.sessions:
             del self.sessions[session_id]
             return True
         return False
```

**3. 沙箱代理集成**

```python
# src/agents/sandbox_agent.py
import asyncio
from typing import Dict, Any, List, Optional
from ..sandbox.docker_sandbox import DockerSandbox, SandboxConfig
from ..agents.react_agent import ReActAgent

class SandboxAgent(ReActAgent):
    """集成沙箱执行环境的代理"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # 初始化沙箱
        sandbox_config = SandboxConfig(
            timeout=config.get('sandbox_timeout', 30),
            memory_limit=config.get('sandbox_memory_limit', 512),
            cpu_limit=config.get('sandbox_cpu_limit', 1.0),
            network_access=config.get('sandbox_network_access', False)
        )

        self.sandbox = DockerSandbox(sandbox_config)

        # 注册沙箱工具
        self.tools['execute_code'] = self._execute_code_tool
        self.tools['create_sandbox_session'] = self._create_session_tool
        self.tools['destroy_sandbox_session'] = self._destroy_session_tool

    async def _execute_code_tool(self, code: str, language: str = "python",
                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """代码执行工具"""
        try:
            result = await self.sandbox.execute(code, language, session_id)
            return {
                "tool": "execute_code",
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time,
                "language": language
            }
        except Exception as e:
            return {
                "tool": "execute_code",
                "success": False,
                "error": str(e)
            }

    async def _create_session_tool(self) -> Dict[str, Any]:
        """创建沙箱会话工具"""
        try:
            session_id = await self.sandbox.create_session()
            return {
                "tool": "create_sandbox_session",
                "success": True,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "tool": "create_sandbox_session",
                "success": False,
                "error": str(e)
            }

    async def _destroy_session_tool(self, session_id: str) -> Dict[str, Any]:
        """销毁沙箱会话工具"""
        try:
            success = await self.sandbox.destroy_session(session_id)
            return {
                "tool": "destroy_sandbox_session",
                "success": success,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "tool": "destroy_sandbox_session",
                "success": False,
                "error": str(e)
            }

    async def solve_coding_problem(self, problem_description: str) -> Dict[str, Any]:
        """解决编程问题"""
        enhanced_prompt = f"""
{problem_description}

你是一个编程助手，可以执行代码来验证解决方案。
可用工具：
1. execute_code(code, language) - 执行代码
2. create_sandbox_session() - 创建新的执行会话
3. destroy_sandbox_session(session_id) - 销毁执行会话

请分析问题，编写代码，执行验证，并提供最终解决方案。
"""

        return await self.solve(enhanced_prompt)

# 使用示例
async def main():
    config = {
        'openai_api_key': 'your-api-key',
        'model': 'gpt-4',
        'sandbox_timeout': 30,
        'sandbox_memory_limit': 256,
        'sandbox_network_access': False
    }

    agent = SandboxAgent(config)

    # 示例：解决编程问题
    problems = [
        "编写一个Python函数来计算斐波那契数列的第n项",
        "实现一个JavaScript函数来判断一个字符串是否为回文",
        "用Python编写一个简单的计算器，支持加减乘除运算"
    ]

    for i, problem in enumerate(problems, 1):
        print(f"\n=== 问题 {i} ===")
        print(f"问题：{problem}")
        print("=" * 50)

        result = await agent.solve_coding_problem(problem)
        print(f"解决方案：{result}")

        # 显示执行轨迹
        print("\n执行轨迹：")
        for trace in agent.get_execution_trace():
            print(f"步骤 {trace['step']}: {trace['thought']}")
            if trace['action']:
                print(f"  行动: {trace['action']}")
            if trace['observation']:
                print(f"  观察: {trace['observation'][:200]}...")  # 截断长输出

        print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **安全隔离**：使用 Docker 容器提供安全的执行环境
2. **资源限制**：控制 CPU、内存和执行时间
3. **多语言支持**：支持不同编程语言的执行
4. **会话管理**：管理长期的代码执行会话

---

## 阶段五：MCP 协议和分布式工具

### 项目 8: MCP 服务器实现

#### 项目目标

- 实现 Model Context Protocol (MCP) 服务器
- 提供分布式工具调用能力
- 支持工具发现和动态加载
- 集成到 AI 代理生态系统

#### 核心代码实现

**1. MCP 协议基础**

```python
# src/mcp/protocol.py
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

class MessageType(Enum):
    """消息类型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

@dataclass
class MCPMessage:
    """MCP消息基类"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

@dataclass
class MCPRequest(MCPMessage):
    """MCP请求消息"""
    method: str
    params: Optional[Dict[str, Any]] = None

@dataclass
class MCPResponse(MCPMessage):
    """MCP响应消息"""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@dataclass
class MCPNotification(MCPMessage):
    """MCP通知消息"""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None  # 通知没有ID

@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class ResourceInfo:
    """资源信息"""
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
```

**2. MCP 服务器实现**

```python
# src/mcp/server.py
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from .protocol import MCPRequest, MCPResponse, MCPNotification, ToolInfo, ResourceInfo

class MCPServer:
    """MCP服务器实现"""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: Dict[str, ToolInfo] = {}
        self.resources: Dict[str, ResourceInfo] = {}
        self.logger = logging.getLogger(f"mcp.server.{name}")

        # 注册内置方法
        self._register_builtin_methods()

    def _register_builtin_methods(self):
        """注册内置方法"""
        self.tools.update({
            'tools/list': self._list_tools,
            'tools/call': self._call_tool,
            'resources/list': self._list_resources,
            'resources/read': self._read_resource,
            'server/info': self._server_info
        })

    def register_tool(self, name: str, func: Callable, schema: Dict[str, Any],
                     description: str = ""):
        """注册工具"""
        self.tools[name] = func
        self.tool_schemas[name] = ToolInfo(
            name=name,
            description=description,
            input_schema=schema
        )
        self.logger.info(f"注册工具: {name}")

    def register_resource(self, uri: str, name: str, description: str = "",
                         mime_type: str = "text/plain"):
        """注册资源"""
        self.resources[uri] = ResourceInfo(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type
        )
        self.logger.info(f"注册资源: {uri}")

    async def _list_tools(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """列出所有工具"""
        tools = []
        for name, info in self.tool_schemas.items():
            if not name.startswith('tools/') and not name.startswith('resources/') and name != 'server/info':
                tools.append({
                    'name': info.name,
                    'description': info.description,
                    'inputSchema': info.input_schema
                })

        return {'tools': tools}

    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})

        if tool_name not in self.tools:
            raise ValueError(f"未知工具: {tool_name}")

        try:
            tool_func = self.tools[tool_name]
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                result = tool_func(**arguments)

            return {
                'content': [{
                    'type': 'text',
                    'text': str(result)
                }]
            }
        except Exception as e:
            self.logger.error(f"工具执行错误 {tool_name}: {e}")
            raise

    async def _list_resources(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """列出所有资源"""
        resources = []
        for uri, info in self.resources.items():
            resources.append({
                'uri': info.uri,
                'name': info.name,
                'description': info.description,
                'mimeType': info.mime_type
            })

        return {'resources': resources}

    async def _read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """读取资源"""
        uri = params.get('uri')

        if uri not in self.resources:
            raise ValueError(f"未知资源: {uri}")

        # 这里应该实现实际的资源读取逻辑
        # 为了示例，我们返回一个简单的响应
        return {
            'contents': [{
                'uri': uri,
                'mimeType': self.resources[uri].mime_type,
                'text': f"资源内容: {uri}"
            }]
        }

    async def _server_info(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """服务器信息"""
        return {
            'name': self.name,
            'version': self.version,
            'protocolVersion': '2024-11-05'
        }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理请求"""
        try:
            method = request.method
            params = request.params or {}

            if method in self.tools:
                result = await self.tools[method](params)
                return MCPResponse(id=request.id, result=result)
            else:
                error = {
                    'code': -32601,
                    'message': f'方法未找到: {method}'
                }
                return MCPResponse(id=request.id, error=error)

        except Exception as e:
            self.logger.error(f"请求处理错误: {e}")
            error = {
                'code': -32603,
                'message': f'内部错误: {str(e)}'
            }
            return MCPResponse(id=request.id, error=error)

    async def start_stdio_server(self):
        """启动标准输入输出服务器"""
        self.logger.info(f"启动MCP服务器: {self.name}")

        try:
            while True:
                # 从标准输入读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )

                if not line.strip():
                    continue

                try:
                    # 解析请求
                    request_data = json.loads(line)
                    request = MCPRequest(
                        id=request_data.get('id'),
                        method=request_data['method'],
                        params=request_data.get('params')
                    )

                    # 处理请求
                    response = await self.handle_request(request)

                    # 发送响应
                    print(response.to_json(), flush=True)

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析错误: {e}")
                except Exception as e:
                    self.logger.error(f"请求处理错误: {e}")

        except KeyboardInterrupt:
             self.logger.info("服务器停止")
         except EOFError:
             self.logger.info("输入流结束，服务器停止")
```

**3. MCP 客户端实现**

```python
# src/mcp/client.py
import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from .protocol import MCPRequest, MCPResponse, ToolInfo

class MCPClient:
    """MCP客户端实现"""

    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.tools: Dict[str, ToolInfo] = {}
        self.request_id = 0

    async def connect(self):
        """连接到MCP服务器"""
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )

        # 获取服务器信息
        server_info = await self.call_method('server/info')
        print(f"连接到服务器: {server_info}")

        # 获取工具列表
        await self.refresh_tools()

    async def disconnect(self):
        """断开连接"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    async def call_method(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """调用MCP方法"""
        if not self.process:
            raise RuntimeError("未连接到服务器")

        self.request_id += 1
        request = MCPRequest(
            id=self.request_id,
            method=method,
            params=params
        )

        # 发送请求
        request_json = request.to_json() + '\n'
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # 读取响应
        response_line = self.process.stdout.readline().strip()
        response_data = json.loads(response_line)

        response = MCPResponse(
            id=response_data.get('id'),
            result=response_data.get('result'),
            error=response_data.get('error')
        )

        if response.error:
            raise RuntimeError(f"MCP错误: {response.error}")

        return response.result

    async def refresh_tools(self):
        """刷新工具列表"""
        result = await self.call_method('tools/list')
        self.tools = {}

        for tool_data in result.get('tools', []):
            tool_info = ToolInfo(
                name=tool_data['name'],
                description=tool_data['description'],
                input_schema=tool_data['inputSchema']
            )
            self.tools[tool_info.name] = tool_info

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未知工具: {tool_name}")

        params = {
            'name': tool_name,
            'arguments': arguments
        }

        return await self.call_method('tools/call', params)

    def list_tools(self) -> List[ToolInfo]:
        """列出可用工具"""
        return list(self.tools.values())

# 使用示例
async def main():
    # 启动文件系统MCP服务器
    client = MCPClient(['python', '-m', 'mcp_servers.filesystem'])

    try:
        await client.connect()

        # 列出工具
        tools = client.list_tools()
        print("可用工具:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        # 调用工具
        result = await client.call_tool('read_file', {
            'path': '/path/to/file.txt'
        })
        print(f"文件内容: {result}")

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**4. 集成 MCP 的代理**

```python
# src/agents/mcp_agent.py
import asyncio
from typing import Dict, Any, List, Optional
from ..mcp.client import MCPClient
from ..agents.react_agent import ReActAgent

class MCPAgent(ReActAgent):
    """集成MCP协议的代理"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_servers = config.get('mcp_servers', [])

        # 初始化MCP客户端
        asyncio.create_task(self._initialize_mcp_clients())

    async def _initialize_mcp_clients(self):
        """初始化MCP客户端"""
        for server_config in self.mcp_servers:
            server_name = server_config['name']
            server_command = server_config['command']

            client = MCPClient(server_command)
            await client.connect()

            self.mcp_clients[server_name] = client

            # 注册MCP工具
            for tool in client.list_tools():
                tool_name = f"{server_name}_{tool.name}"
                self.tools[tool_name] = self._create_mcp_tool_wrapper(server_name, tool.name)

    def _create_mcp_tool_wrapper(self, server_name: str, tool_name: str):
        """创建MCP工具包装器"""
        async def mcp_tool_wrapper(**kwargs) -> Dict[str, Any]:
            try:
                client = self.mcp_clients[server_name]
                result = await client.call_tool(tool_name, kwargs)
                return {
                    "tool": f"{server_name}_{tool_name}",
                    "success": True,
                    "result": result
                }
            except Exception as e:
                return {
                    "tool": f"{server_name}_{tool_name}",
                    "success": False,
                    "error": str(e)
                }

        return mcp_tool_wrapper

    async def cleanup(self):
        """清理资源"""
        for client in self.mcp_clients.values():
            await client.disconnect()
```

#### 学习要点

1. **协议理解**：掌握 MCP 协议的消息格式和交互模式
2. **服务器开发**：实现工具注册、请求处理和响应生成
3. **客户端开发**：实现服务器连接、工具调用和错误处理
4. **分布式架构**：理解分布式工具系统的设计原则

---

## 阶段六：完整 AI 代理系统

### 项目 9: OpenManus 简化版

#### 项目目标

- 构建完整的 AI 代理系统
- 集成所有前面学到的技术
- 实现类似 OpenManus 的核心功能
- 提供可扩展的架构设计

#### 核心代码实现

**1. 主代理系统**

```python
# src/agents/openmanus_agent.py
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..llm.openai_client import OpenAIClient
from ..tools.base import BaseTool, ToolResult
from ..tools.registry import ToolRegistry
from ..memory.conversation import ConversationMemory
from ..mcp.client import MCPClient
from ..sandbox.docker_sandbox import DockerSandbox

class OpenManusAgent:
    """OpenManus简化版代理"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("openmanus.agent")

        # 初始化组件
        self.llm_client = OpenAIClient(config['openai'])
        self.tool_registry = ToolRegistry()
        self.memory = ConversationMemory()
        self.sandbox = DockerSandbox(config.get('sandbox', {}))

        # MCP客户端
        self.mcp_clients: Dict[str, MCPClient] = {}

        # 执行状态
        self.execution_trace: List[Dict[str, Any]] = []
        self.current_step = 0
        self.max_steps = config.get('max_steps', 10)

        # 初始化工具
        self._initialize_tools()

    def _initialize_tools(self):
        """初始化内置工具"""
        from ..tools.file_tools import FileReadTool, FileWriteTool
        from ..tools.web_tools import WebSearchTool, WebScrapeTool
        from ..tools.code_tools import CodeExecuteTool

        # 注册内置工具
        self.tool_registry.register(FileReadTool())
        self.tool_registry.register(FileWriteTool())
        self.tool_registry.register(WebSearchTool(self.config.get('web_search', {})))
        self.tool_registry.register(WebScrapeTool())
        self.tool_registry.register(CodeExecuteTool(self.sandbox))

    async def initialize_mcp_servers(self, mcp_configs: List[Dict[str, Any]]):
        """初始化MCP服务器"""
        for mcp_config in mcp_configs:
            server_name = mcp_config['name']
            server_command = mcp_config['command']

            try:
                client = MCPClient(server_command)
                await client.connect()

                self.mcp_clients[server_name] = client

                # 注册MCP工具
                for tool in client.list_tools():
                    mcp_tool = MCPToolWrapper(client, tool, server_name)
                    self.tool_registry.register(mcp_tool)

                self.logger.info(f"已连接MCP服务器: {server_name}")

            except Exception as e:
                self.logger.error(f"连接MCP服务器失败 {server_name}: {e}")

    async def process_request(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        self.logger.info(f"处理用户请求: {user_input}")

        # 重置执行状态
        self.execution_trace = []
        self.current_step = 0

        # 添加到对话记忆
        self.memory.add_message("user", user_input)

        # 构建系统提示
        system_prompt = self._build_system_prompt()

        # 构建对话历史
        conversation_history = self.memory.get_recent_messages(10)

        try:
            # 开始ReAct循环
            final_answer = await self._react_loop(system_prompt, conversation_history, context)

            # 添加到对话记忆
            self.memory.add_message("assistant", final_answer)

            return {
                "success": True,
                "answer": final_answer,
                "execution_trace": self.execution_trace,
                "steps_used": self.current_step
            }

        except Exception as e:
            self.logger.error(f"请求处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_trace": self.execution_trace
            }

    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        available_tools = self.tool_registry.list_tools()
        tool_descriptions = []

        for tool in available_tools:
            tool_descriptions.append(
                f"- {tool.name}: {tool.description}\n"
                f"  参数: {tool.get_schema()}"
            )

        tools_text = "\n".join(tool_descriptions)

        return f"""
你是OpenManus AI代理，一个强大的AI助手，能够使用各种工具来帮助用户完成任务。

## 可用工具
{tools_text}

## 工作模式
你使用ReAct（Reasoning and Acting）模式工作：
1. **思考（Think）**: 分析当前情况，决定下一步行动
2. **行动（Act）**: 使用工具执行具体操作
3. **观察（Observe）**: 分析工具执行结果
4. **重复**: 直到完成任务或达到最大步数

## 响应格式
每一步都要包含：
- **思考**: 你的分析和计划
- **行动**: 要使用的工具和参数（如果需要）
- **观察**: 对结果的分析（在工具执行后）

## 重要规则
1. 始终先思考再行动
2. 一次只使用一个工具
3. 仔细分析工具执行结果
4. 如果遇到错误，尝试其他方法
5. 完成任务后给出最终答案

现在开始处理用户的请求。
"""

    async def _react_loop(self, system_prompt: str, conversation_history: List[Dict],
                         context: Optional[Dict] = None) -> str:
        """ReAct循环执行"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 添加对话历史
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        while self.current_step < self.max_steps:
            self.current_step += 1

            # 获取LLM响应
            response = await self.llm_client.chat_completion(
                messages=messages,
                temperature=0.1
            )

            assistant_message = response.choices[0].message.content

            # 解析响应
            thought, action, tool_call = self._parse_response(assistant_message)

            # 记录执行轨迹
            trace_entry = {
                "step": self.current_step,
                "thought": thought,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }

            # 如果没有工具调用，说明任务完成
            if not tool_call:
                trace_entry["final_answer"] = assistant_message
                self.execution_trace.append(trace_entry)
                return assistant_message

            # 执行工具
            try:
                tool_result = await self._execute_tool(tool_call)
                observation = f"工具执行结果: {tool_result.content}"

                if not tool_result.success:
                    observation += f"\n错误: {tool_result.error}"

            except Exception as e:
                observation = f"工具执行失败: {str(e)}"

            trace_entry["observation"] = observation
            self.execution_trace.append(trace_entry)

            # 添加到对话历史
            messages.append({"role": "assistant", "content": assistant_message})
            messages.append({"role": "user", "content": observation})

        return "抱歉，已达到最大执行步数，无法完成任务。"

    def _parse_response(self, response: str) -> tuple[str, str, Optional[Dict]]:
        """解析LLM响应"""
        # 简化的解析逻辑，实际应该更复杂
        lines = response.strip().split('\n')

        thought = ""
        action = ""
        tool_call = None

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("**思考") or line.startswith("思考:"):
                current_section = "thought"
                continue
            elif line.startswith("**行动") or line.startswith("行动:"):
                current_section = "action"
                continue
            elif line.startswith("**观察") or line.startswith("观察:"):
                current_section = "observation"
                continue

            if current_section == "thought":
                thought += line + "\n"
            elif current_section == "action":
                action += line + "\n"

                # 尝试解析工具调用
                if "工具:" in line or "tool:" in line.lower():
                    tool_call = self._extract_tool_call(action)

        return thought.strip(), action.strip(), tool_call

    def _extract_tool_call(self, action_text: str) -> Optional[Dict]:
        """从行动文本中提取工具调用"""
        # 简化的工具调用提取逻辑
        # 实际实现应该更加健壮
        import re

        # 查找工具名称
        tool_match = re.search(r'工具[：:]\s*(\w+)', action_text)
        if not tool_match:
            return None

        tool_name = tool_match.group(1)

        # 查找参数（简化版）
        params = {}
        param_matches = re.findall(r'(\w+)[：:]\s*([^\n]+)', action_text)

        for key, value in param_matches:
            if key != '工具' and key != 'tool':
                params[key] = value.strip()

        return {
            "tool_name": tool_name,
            "parameters": params
        }

    async def _execute_tool(self, tool_call: Dict) -> ToolResult:
        """执行工具调用"""
        tool_name = tool_call["tool_name"]
        parameters = tool_call["parameters"]

        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                content="",
                error=f"未找到工具: {tool_name}"
            )

        return await tool.execute(**parameters)

    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        return self.execution_trace

    async def cleanup(self):
        """清理资源"""
        # 断开MCP连接
        for client in self.mcp_clients.values():
            await client.disconnect()

        # 清理沙箱
        if self.sandbox:
            # 这里应该有沙箱清理逻辑
            pass


class MCPToolWrapper(BaseTool):
    """MCP工具包装器"""

    def __init__(self, client: MCPClient, tool_info, server_name: str):
        self.client = client
        self.tool_info = tool_info
        self.server_name = server_name

        super().__init__(
            name=f"{server_name}_{tool_info.name}",
            description=f"[{server_name}] {tool_info.description}"
        )

    async def _execute(self, **kwargs) -> ToolResult:
        try:
            result = await self.client.call_tool(self.tool_info.name, kwargs)
            return ToolResult(
                success=True,
                content=str(result)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )

    def get_schema(self) -> Dict[str, Any]:
        return self.tool_info.input_schema
```

**2. 主程序入口**

```python
# main.py
import asyncio
import json
import logging
from typing import Dict, Any

from src.agents.openmanus_agent import OpenManusAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """主程序"""

    # 加载配置
    config = {
        "openai": {
            "api_key": "your-openai-api-key",
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1"
        },
        "sandbox": {
            "timeout": 30,
            "memory_limit": 512,
            "cpu_limit": 1.0
        },
        "web_search": {
            "api_key": "your-search-api-key"
        },
        "max_steps": 15
    }

    # MCP服务器配置
    mcp_configs = [
        {
            "name": "filesystem",
            "command": ["python", "-m", "mcp_servers.filesystem"]
        },
        {
            "name": "browser",
            "command": ["python", "-m", "mcp_servers.browser"]
        }
    ]

    # 创建代理
    agent = OpenManusAgent(config)

    try:
        # 初始化MCP服务器
        await agent.initialize_mcp_servers(mcp_configs)

        print("OpenManus AI代理已启动！")
        print("输入 'quit' 或 'exit' 退出")
        print("-" * 50)

        # 交互循环
        while True:
            try:
                user_input = input("\n用户: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出']:
                    break

                if not user_input:
                    continue

                print("\n代理正在处理...")

                # 处理请求
                result = await agent.process_request(user_input)

                if result["success"]:
                    print(f"\n代理: {result['answer']}")
                    print(f"\n执行步数: {result['steps_used']}")

                    # 可选：显示执行轨迹
                    show_trace = input("\n是否显示执行轨迹？(y/n): ").lower() == 'y'
                    if show_trace:
                        print("\n=== 执行轨迹 ===")
                        for trace in result['execution_trace']:
                            print(f"\n步骤 {trace['step']}:")
                            print(f"思考: {trace['thought']}")
                            if 'action' in trace:
                                print(f"行动: {trace['action']}")
                            if 'observation' in trace:
                                print(f"观察: {trace['observation']}")
                else:
                    print(f"\n错误: {result['error']}")

            except KeyboardInterrupt:
                print("\n\n用户中断，正在退出...")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")

    finally:
        # 清理资源
        await agent.cleanup()
        print("\n再见！")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **系统集成**：将所有组件整合成完整的 AI 代理系统
2. **架构设计**：模块化、可扩展的系统架构
3. **错误处理**：完善的异常处理和资源清理
4. **用户体验**：友好的交互界面和反馈机制
5. **性能优化**：异步处理和资源管理

---

## 实践建议

### 循序渐进的学习方法

1. **从简单开始**：先完成基础项目，理解核心概念
2. **动手实践**：每个项目都要亲自编写和运行代码
3. **逐步扩展**：在掌握基础后，逐步添加高级功能
4. **测试验证**：每个功能都要编写测试用例
5. **文档记录**：记录学习过程和遇到的问题

### 常见问题和解决方案

1. **依赖管理**：使用虚拟环境管理 Python 依赖
2. **API 配置**：正确配置 OpenAI API 密钥和其他服务
3. **错误调试**：学会使用日志和调试工具
4. **性能优化**：理解异步编程和资源管理
5. **安全考虑**：注意 API 密钥安全和代码执行安全

### 扩展方向

完成这 9 个项目后，你可以继续探索：

1. **更多工具集成**：数据库、API、云服务等
2. **高级 AI 功能**：多模态处理、知识图谱等
3. **分布式部署**：微服务架构、容器化部署
4. **用户界面**：Web 界面、移动应用等
5. **企业级功能**：权限管理、审计日志等

通过这个完整的学习路径，你将掌握构建现代 AI 应用所需的核心技能，并能够开发出类似 OpenManus 的强大 AI 代理系统。

- 使用调试器逐步执行
- 处理各种边界情况

通过这些实践项目，你将逐步掌握 AI 应用开发的核心技能，为后续的高级功能开发打下坚实基础。
