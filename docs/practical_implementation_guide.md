## 1. 类型注解 (Type Hints) - 类似 Java 的类型声明

**Java/JS 对比**：

- Java: `String name;` `List<String> items;`
- JavaScript: 通常无类型声明（除非用 TypeScript）
- Python: `name: str` `items: List[str]`

```python
from typing import List, Dict, Optional, Any, Union

class BaseTool(ABC, BaseModel):
    name: str                           # 必需的字符串
    description: str                    # 必需的字符串
    parameters: Optional[dict] = None   # 可选的字典，默认None

    async def execute(self, **kwargs) -> Any:  # 返回任意类型
        pass
```

**关键点**：

- `Optional[T]` = `Union[T, None]` - 可以是 T 类型或 None
- `List[str]` - 字符串列表
- `Dict[str, Any]` - 键为字符串，值为任意类型的字典
- `**kwargs` - 接收任意关键字参数（类似 JS 的解构）

## 2. 抽象基类 (ABC) - 类似 Java 的抽象类/接口

**Java 对比**：

```java
abstract class BaseTool {
    abstract String execute();
}
```

**Python 实现**：

```python
from abc import ABC, abstractmethod

class BaseTool(ABC, BaseModel):
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """子类必须实现此方法"""
        pass
```

**关键点**：

- `ABC` - Abstract Base Class，抽象基类
- `@abstractmethod` - 装饰器，标记抽象方法
- 子类必须实现所有抽象方法才能实例化

## 3. Pydantic 模型 - 数据验证和序列化

**这是 Python 特有的强大功能**，类似 TypeScript 的接口但更强大：

```python
from pydantic import BaseModel, Field

class BaseAgent(BaseModel):
    name: str = Field(..., description="代理名称")  # ... 表示必需
    max_steps: int = Field(default=10, description="最大步数")

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型
        extra = "allow"                 # 允许额外字段
```

**关键特性**：

- 自动数据验证
- JSON 序列化/反序列化
- 类型转换
- 字段描述和默认值

## 4. 异步编程 (async/await) - 类似 JavaScript 的 Promise

**JavaScript 对比**：

```javascript
async function fetchData() {
  const response = await fetch(url);
  return response.json();
}
```

**Python 实现**：

```python
async def chat(self, user_message: str) -> str:
    try:
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.conversation_history
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"错误：{str(e)}"
```

**关键点**：

- `async def` - 定义异步函数
- `await` - 等待异步操作完成
- 异步函数返回协程对象
- 需要在异步上下文中运行

## 5. 装饰器 (Decorators) - Python 独有的强大特性

**类似 Java 的注解，但更灵活**：

```python
@abstractmethod
async def execute(self, **kwargs) -> Any:
    pass

@model_validator(mode="after")
def initialize_agent(self) -> "BaseAgent":
    return self

@property
def is_running(self) -> bool:
    return self.state == AgentState.RUNNING
```

**常见装饰器**：

- `@abstractmethod` - 抽象方法
- `@property` - 将方法转为属性访问
- `@staticmethod` - 静态方法
- `@classmethod` - 类方法

## 6. 上下文管理器 - 资源管理

**类似 Java 的 try-with-resources**：

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_sandbox():
    sandbox = await create_sandbox()
    try:
        yield sandbox
    finally:
        await sandbox.cleanup()

# 使用
async with get_sandbox() as sandbox:
    result = await sandbox.execute(code)
```

## 7. 枚举类 (Enum) - 类似 Java 枚举

```python
from enum import Enum

class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    FINISHED = "finished"

# 使用
agent.state = AgentState.THINKING
```

## 8. 数据类和字段 - 简化的类定义

**Pydantic Field 的使用**：

```python
class BaseAgent(BaseModel):
    name: str = Field(..., description="代理名称")
    memory: Memory = Field(default_factory=Memory)  # 工厂函数
    max_steps: int = Field(default=10, ge=1, le=100)  # 范围验证
```

**关键概念**：

- `Field(...)` - 必需字段
- `default_factory` - 延迟初始化
- `ge`, `le` - 大于等于，小于等于验证

## 9. 异常处理 - 增强的 try/except

```python
try:
    result = await self.execute_tool(tool_call)
except TokenLimitExceeded as e:
    logger.error(f"Token限制超出: {e}")
    raise
except Exception as e:
    logger.error(f"工具执行失败: {str(e)}")
    return ToolResult(error=str(e))
finally:
    await self.cleanup()
```

## 10. 列表推导式和生成器 - Python 特色语法

```python
# 列表推导式 - 类似JS的map/filter
tool_names = [tool.name for tool in self.tools if tool.enabled]

# 字典推导式
tool_map = {tool.name: tool for tool in tools}

# 生成器表达式 - 内存高效
total = sum(len(msg.content) for msg in messages)
```

## 11. 魔术方法 (Dunder Methods) - 运算符重载

```python
class ToolResult(BaseModel):
    def __bool__(self):
        """定义布尔值转换"""
        return any(getattr(self, field) for field in self.__fields__)

    def __add__(self, other: "ToolResult"):
        """定义 + 运算符"""
        return ToolResult(
            output=self.output + other.output,
            error=self.error or other.error
        )

    def __str__(self):
        """定义字符串表示"""
        return f"Error: {self.error}" if self.error else self.output
```

## 12. 模块导入和包管理

```python
# 相对导入
from .base import BaseTool
from ..schema import Message

# 绝对导入
from app.agent.base import BaseAgent
from typing import List, Dict, Optional

# 条件导入
try:
    import uvloop
except ImportError:
    uvloop = None
```

## 学习建议

1. **从类型注解开始** - 这会让你的 Python 代码更像 Java，易于理解
2. **掌握异步编程** - 现代 Python 应用的核心
3. **理解 Pydantic** - 数据验证和 API 开发的利器
4. **熟悉装饰器** - Python 的独特优势
5. **练习上下文管理器** - 资源管理的最佳实践

这些语法特性让 Python 既有动态语言的灵活性，又有静态语言的类型安全性，特别适合构建复杂的 AI 应用系统。
