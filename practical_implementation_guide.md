# OpenManus AI应用开发实践指南

## 阶段一：Python基础强化 (第1-2周)

### 项目1：简单聊天机器人

#### 目标
- 掌握OpenAI API调用
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
2. **API调用**：学会处理HTTP请求和响应
3. **错误处理**：使用 `try/except` 处理异常
4. **类型注解**：使用 `typing` 模块提高代码可读性

### 项目2：配置驱动助手

#### 目标
- 学会使用Pydantic进行数据验证
- 掌握TOML配置文件处理
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
1. **Pydantic模型**：数据验证和序列化
2. **TOML配置**：配置文件的读取和解析
3. **配置驱动**：通过配置控制程序行为
4. **错误处理**：配置验证和运行时错误处理

---

## 阶段二：工具系统开发 (第3-5周)

### 项目3：基础工具框架

#### 目标
- 设计抽象基类和接口
- 实现插件架构
- 学会使用JSON Schema

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
1. **抽象基类**：使用ABC定义接口
2. **JSON Schema**：定义工具参数结构
3. **插件架构**：动态注册和管理工具
4. **错误处理**：统一的结果格式和错误处理

### 项目4：工具调用代理

#### 目标
- 集成LLM和工具系统
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

```json
{{
    "tool_call": {{
        "name": "工具名称",
        "parameters": {{
            "参数名": "参数值"
        }}
    }}
}}
```

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
```

#### 学习要点
1. **工具集成**：LLM与工具系统的集成
2. **智能选择**：让LLM决定何时使用工具
3. **结果处理**：处理工具执行结果并生成回复
4. **对话管理**：维护包含工具调用的对话历史

---

## 阶段三：ReAct模式实现 (第6-8周)

### 项目5：思考-行动循环

#### 目标
- 实现ReAct推理模式
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
1. **ReAct模式**：思考-行动-观察的循环
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
- 尝试集成其他API和服务
- 优化错误处理和用户体验

### 4. 测试和调试
- 编写单元测试
- 使用调试器逐步执行
- 处理各种边界情况

通过这些实践项目，你将逐步掌握AI应用开发的核心技能，为后续的高级功能开发打下坚实基础。