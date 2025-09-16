### 项目 3：基础工具框架

#### 目标

- 学习如何为 AI 代理构建可扩展的工具系统
- 掌握工具的抽象、注册和执行
- 理解工具的输入输出规范

#### 核心代码实现

```python
# tools/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
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