# API 参考文档

## 📋 概述

本文档提供了Practical 3.2异步工具框架的完整API参考。所有的类和方法都包含详细的类型注解和使用示例。

## 🏗️ 核心架构

### 模块结构
```
practical3.2/
├── tools/
│   ├── __init__.py          # 包导出
│   ├── base.py              # 基础抽象类
│   ├── manager.py           # 工具管理器
│   ├── calculator.py        # 计算器工具
│   └── weather.py           # 天气API工具
├── config.py                # 配置管理
└── main.py                  # 主程序入口
```

## 🔧 核心类和接口

### AsyncBaseTool

异步工具的抽象基类，定义了所有工具必须实现的接口。

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from tools.base import AsyncBaseTool, ToolResult

class AsyncBaseTool(ABC):
    """异步工具抽象基类"""
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """执行工具操作"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    def description(self) -> str:
        """工具描述"""
        return f"异步工具: {self.name}"
```

#### 方法详解

##### `execute(**kwargs: Any) -> ToolResult`
- **描述**: 执行工具的主要操作
- **参数**: 
  - `**kwargs`: 工具特定的参数
- **返回**: `ToolResult` 对象
- **异常**: 可能抛出 `ToolExecutionError`

##### `name` (属性)
- **描述**: 工具的唯一标识名称
- **类型**: `str`
- **必需**: 是

##### `description` (属性)
- **描述**: 工具的详细描述
- **类型**: `str`
- **默认**: 基于工具名称生成

#### 使用示例

```python
class CustomTool(AsyncBaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"
    
    async def execute(self, data: str) -> ToolResult:
        # 实现自定义逻辑
        result = await self._process_data(data)
        return ToolResult(
            success=True,
            data=result,
            message="处理完成"
        )
    
    async def _process_data(self, data: str) -> str:
        await asyncio.sleep(0.1)  # 模拟异步操作
        return data.upper()
```

### ToolResult

工具执行结果的标准化数据结构。

```python
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum

class ToolResultStatus(Enum):
    """工具结果状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    TIMEOUT = "timeout"

@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    message: str = ""
    status: ToolResultStatus = ToolResultStatus.SUCCESS
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
```

#### 字段说明

- **success** (`bool`): 操作是否成功
- **data** (`Any`): 返回的数据，可以是任何类型
- **message** (`str`): 描述性消息
- **status** (`ToolResultStatus`): 详细的状态信息
- **execution_time** (`Optional[float]`): 执行时间（秒）
- **metadata** (`Optional[Dict[str, Any]]`): 额外的元数据

#### 使用示例

```python
# 成功结果
result = ToolResult(
    success=True,
    data={"result": 42},
    message="计算完成",
    status=ToolResultStatus.SUCCESS,
    execution_time=0.05
)

# 错误结果
error_result = ToolResult(
    success=False,
    message="参数验证失败",
    status=ToolResultStatus.ERROR,
    metadata={"error_code": "INVALID_INPUT"}
)
```

### AsyncToolManager

异步工具管理器，负责工具的注册、执行和生命周期管理。

```python
class AsyncToolManager:
    """异步工具管理器"""
    
    def __init__(self, max_concurrent: int = 10):
        """初始化管理器"""
        
    async def register_tool(self, tool: AsyncBaseTool) -> None:
        """注册工具"""
        
    async def execute_tool(self, tool_name: str, **kwargs: Any) -> ToolResult:
        """执行单个工具"""
        
    async def execute_batch(self, tasks: List[Dict[str, Any]]) -> List[ToolResult]:
        """批量执行工具"""
        
    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息"""
        
    def get_registered_tools(self) -> List[str]:
        """获取已注册的工具列表"""
```

#### 方法详解

##### `__init__(max_concurrent: int = 10)`
- **描述**: 初始化工具管理器
- **参数**:
  - `max_concurrent`: 最大并发执行数量

##### `register_tool(tool: AsyncBaseTool) -> None`
- **描述**: 注册一个新工具
- **参数**:
  - `tool`: 要注册的工具实例
- **异常**: 如果工具名称已存在，抛出 `ValueError`

##### `execute_tool(tool_name: str, **kwargs: Any) -> ToolResult`
- **描述**: 执行指定的工具
- **参数**:
  - `tool_name`: 工具名称
  - `**kwargs`: 传递给工具的参数
- **返回**: 工具执行结果
- **异常**: 如果工具不存在，抛出 `KeyError`

##### `execute_batch(tasks: List[Dict[str, Any]]) -> List[ToolResult]`
- **描述**: 并发执行多个工具任务
- **参数**:
  - `tasks`: 任务列表，每个任务包含工具名称和参数
- **返回**: 结果列表，与任务列表顺序对应

#### 使用示例

```python
# 创建管理器
manager = AsyncToolManager(max_concurrent=5)

# 注册工具
calculator = AsyncCalculatorTool()
await manager.register_tool(calculator)

# 执行单个工具
result = await manager.execute_tool(
    "calculator", 
    operation="add", 
    a=10, 
    b=20
)

# 批量执行
tasks = [
    {"tool_name": "calculator", "operation": "add", "a": 1, "b": 2},
    {"tool_name": "calculator", "operation": "multiply", "a": 3, "b": 4},
]
results = await manager.execute_batch(tasks)
```

## 🧮 具体工具实现

### AsyncCalculatorTool

异步计算器工具，支持基本数学运算。

```python
class AsyncCalculatorTool(AsyncBaseTool):
    """异步计算器工具"""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    async def execute(self, operation: str, a: float, b: float) -> ToolResult:
        """执行数学运算"""
        
    async def add(self, a: float, b: float) -> float:
        """加法运算"""
        
    async def subtract(self, a: float, b: float) -> float:
        """减法运算"""
        
    async def multiply(self, a: float, b: float) -> float:
        """乘法运算"""
        
    async def divide(self, a: float, b: float) -> float:
        """除法运算"""
```

#### 支持的操作

| 操作 | 参数 | 描述 |
|------|------|------|
| `add` | `a: float, b: float` | 加法运算 |
| `subtract` | `a: float, b: float` | 减法运算 |
| `multiply` | `a: float, b: float` | 乘法运算 |
| `divide` | `a: float, b: float` | 除法运算 |
| `power` | `a: float, b: float` | 幂运算 |
| `sqrt` | `a: float` | 平方根 |
| `factorial` | `n: int` | 阶乘 |

#### 使用示例

```python
calculator = AsyncCalculatorTool()

# 基本运算
result = await calculator.execute(operation="add", a=10, b=5)
print(f"10 + 5 = {result.data}")  # 输出: 10 + 5 = 15

# 复杂运算
result = await calculator.execute(operation="power", a=2, b=8)
print(f"2^8 = {result.data}")  # 输出: 2^8 = 256

# 错误处理
try:
    result = await calculator.execute(operation="divide", a=10, b=0)
except Exception as e:
    print(f"错误: {e}")
```

### AsyncWeatherTool

异步天气查询工具，集成OpenWeather API。

```python
class AsyncWeatherTool(AsyncBaseTool):
    """异步天气查询工具"""
    
    def __init__(self, api_key: str, cache_ttl: int = 300):
        """初始化天气工具"""
        
    @property
    def name(self) -> str:
        return "weather"
    
    async def execute(self, city: str, country: Optional[str] = None) -> ToolResult:
        """查询天气信息"""
        
    async def get_current_weather(self, city: str, country: Optional[str] = None) -> Dict[str, Any]:
        """获取当前天气"""
        
    async def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """获取天气预报"""
        
    def _parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析天气数据"""
```

#### 方法详解

##### `__init__(api_key: str, cache_ttl: int = 300)`
- **参数**:
  - `api_key`: OpenWeather API密钥
  - `cache_ttl`: 缓存生存时间（秒）

##### `execute(city: str, country: Optional[str] = None) -> ToolResult`
- **参数**:
  - `city`: 城市名称
  - `country`: 国家代码（可选）
- **返回**: 包含天气信息的 `ToolResult`

##### `get_current_weather(city: str, country: Optional[str] = None) -> Dict[str, Any]`
- **描述**: 获取指定城市的当前天气
- **返回**: 天气数据字典

##### `get_forecast(city: str, days: int = 5) -> Dict[str, Any]`
- **描述**: 获取天气预报
- **参数**:
  - `days`: 预报天数（1-5天）

#### 返回数据格式

```python
{
    "city": "Beijing",
    "country": "CN",
    "temperature": 25.5,
    "feels_like": 27.2,
    "humidity": 65,
    "pressure": 1013,
    "description": "晴朗",
    "wind_speed": 3.2,
    "wind_direction": 180,
    "visibility": 10000,
    "uv_index": 6,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 使用示例

```python
# 初始化工具
weather_tool = AsyncWeatherTool(api_key="your_api_key")

# 查询当前天气
result = await weather_tool.execute(city="Beijing", country="CN")
if result.success:
    weather_data = result.data
    print(f"北京当前温度: {weather_data['temperature']}°C")
    print(f"天气描述: {weather_data['description']}")

# 查询天气预报
forecast = await weather_tool.get_forecast(city="Shanghai", days=3)
for day in forecast['daily']:
    print(f"日期: {day['date']}, 温度: {day['temp_min']}-{day['temp_max']}°C")
```

## ⚙️ 配置管理

### Config

应用程序配置管理类，支持环境变量和默认值。

```python
class Config:
    """应用程序配置管理"""
    
    def __init__(self):
        """初始化配置"""
        
    @classmethod
    def get_instance(cls) -> 'Config':
        """获取配置单例实例"""
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        
    def validate(self) -> bool:
        """验证配置完整性"""
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
```

#### 配置项

| 配置项 | 环境变量 | 默认值 | 描述 |
|--------|----------|--------|------|
| `openweather_api_key` | `OPENWEATHER_API_KEY` | `None` | OpenWeather API密钥 |
| `request_timeout` | `REQUEST_TIMEOUT` | `30` | HTTP请求超时时间 |
| `max_retries` | `MAX_RETRIES` | `3` | 最大重试次数 |
| `cache_ttl` | `CACHE_TTL` | `300` | 缓存生存时间 |
| `log_level` | `LOG_LEVEL` | `INFO` | 日志级别 |
| `max_concurrent` | `MAX_CONCURRENT` | `10` | 最大并发数 |

#### 使用示例

```python
# 获取配置实例
config = Config.get_instance()

# 获取配置值
api_key = config.get("openweather_api_key")
timeout = config.get("request_timeout", 30)

# 设置配置值
config.set("max_concurrent", 20)

# 验证配置
if not config.validate():
    raise ValueError("配置验证失败")
```

## 🎯 装饰器和工具函数

### @tool_timer

性能计时装饰器，用于测量异步函数的执行时间。

```python
from functools import wraps
from typing import Callable, Any
import time

def tool_timer(func: Callable) -> Callable:
    """异步函数执行时间装饰器"""
    
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 如果结果是ToolResult，添加执行时间
            if isinstance(result, ToolResult):
                result.execution_time = execution_time
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.4f}秒")
            raise
    
    return wrapper
```

#### 使用示例

```python
class TimedTool(AsyncBaseTool):
    @property
    def name(self) -> str:
        return "timed_tool"
    
    @tool_timer
    async def execute(self, delay: float = 1.0) -> ToolResult:
        await asyncio.sleep(delay)
        return ToolResult(
            success=True,
            data=f"等待了 {delay} 秒",
            message="操作完成"
        )

# 使用
tool = TimedTool()
result = await tool.execute(delay=2.0)
print(f"执行时间: {result.execution_time:.2f}秒")
```

### 异步上下文管理器

用于资源管理和清理的异步上下文管理器。

```python
from typing import AsyncGenerator
import aiohttp

class AsyncHTTPSession:
    """异步HTTP会话管理器"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self) -> aiohttp.ClientSession:
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
```

#### 使用示例

```python
async def fetch_data(url: str) -> Dict[str, Any]:
    async with AsyncHTTPSession(timeout=10) as session:
        async with session.get(url) as response:
            return await response.json()

# 使用
data = await fetch_data("https://api.example.com/data")
```

## 🚨 异常处理

### 自定义异常类

```python
class ToolFrameworkError(Exception):
    """工具框架基础异常"""
    pass

class ToolExecutionError(ToolFrameworkError):
    """工具执行异常"""
    
    def __init__(self, tool_name: str, message: str, original_error: Optional[Exception] = None):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"工具 '{tool_name}' 执行失败: {message}")

class ToolRegistrationError(ToolFrameworkError):
    """工具注册异常"""
    pass

class ConfigurationError(ToolFrameworkError):
    """配置异常"""
    pass

class APIError(ToolFrameworkError):
    """API调用异常"""
    
    def __init__(self, status_code: int, message: str, response_data: Optional[Dict] = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(f"API错误 {status_code}: {message}")
```

#### 异常处理示例

```python
async def safe_tool_execution():
    try:
        manager = AsyncToolManager()
        result = await manager.execute_tool("calculator", operation="divide", a=10, b=0)
    except ToolExecutionError as e:
        print(f"工具执行错误: {e}")
        print(f"原始错误: {e.original_error}")
    except APIError as e:
        print(f"API调用失败: {e}")
        print(f"状态码: {e.status_code}")
    except ConfigurationError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
```

## 📊 性能监控

### PerformanceMonitor

性能监控类，用于收集和分析工具执行性能。

```python
from dataclasses import dataclass
from typing import Dict, List
import statistics

@dataclass
class PerformanceMetrics:
    """性能指标"""
    tool_name: str
    total_executions: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    success_rate: float
    error_count: int

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._errors: Dict[str, int] = {}
        self._successes: Dict[str, int] = {}
    
    def record_execution(self, tool_name: str, execution_time: float, success: bool):
        """记录执行性能"""
        
    def get_metrics(self, tool_name: str) -> PerformanceMetrics:
        """获取工具性能指标"""
        
    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """获取所有工具的性能指标"""
        
    def reset_metrics(self, tool_name: Optional[str] = None):
        """重置性能指标"""
```

#### 使用示例

```python
# 创建性能监控器
monitor = PerformanceMonitor()

# 在工具管理器中集成监控
class MonitoredToolManager(AsyncToolManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = PerformanceMonitor()
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        start_time = time.time()
        try:
            result = await super().execute_tool(tool_name, **kwargs)
            execution_time = time.time() - start_time
            self.monitor.record_execution(tool_name, execution_time, result.success)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.monitor.record_execution(tool_name, execution_time, False)
            raise

# 查看性能报告
metrics = monitor.get_metrics("calculator")
print(f"平均执行时间: {metrics.average_time:.4f}秒")
print(f"成功率: {metrics.success_rate:.2%}")
```

## 🔍 调试和日志

### 日志配置

```python
import logging
from colorlog import ColoredFormatter

def setup_logging(level: str = "INFO") -> logging.Logger:
    """设置彩色日志"""
    
    logger = logging.getLogger("async_tools")
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
```

### 调试工具

```python
import asyncio
from typing import Any, Callable

async def debug_async_execution(func: Callable, *args: Any, **kwargs: Any):
    """调试异步函数执行"""
    
    logger = logging.getLogger("debug")
    
    logger.info(f"开始执行: {func.__name__}")
    logger.debug(f"参数: args={args}, kwargs={kwargs}")
    
    start_time = time.time()
    try:
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"执行成功: {func.__name__}, 耗时: {execution_time:.4f}秒")
        logger.debug(f"返回结果: {result}")
        
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"执行失败: {func.__name__}, 耗时: {execution_time:.4f}秒, 错误: {e}")
        raise
```

## 📝 最佳实践

### 1. 错误处理模式

```python
async def robust_tool_execution(manager: AsyncToolManager, tool_name: str, **kwargs) -> ToolResult:
    """健壮的工具执行模式"""
    
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            result = await manager.execute_tool(tool_name, **kwargs)
            if result.success:
                return result
            
            # 如果不成功但没有异常，记录警告
            logging.warning(f"工具执行不成功: {result.message}")
            
        except Exception as e:
            if attempt == max_retries - 1:
                # 最后一次尝试失败，抛出异常
                raise ToolExecutionError(tool_name, str(e), e)
            
            # 指数退避重试
            delay = base_delay * (2 ** attempt)
            logging.warning(f"工具执行失败，{delay}秒后重试: {e}")
            await asyncio.sleep(delay)
    
    # 理论上不会到达这里
    return ToolResult(success=False, message="所有重试都失败了")
```

### 2. 资源管理模式

```python
class ResourceManagedTool(AsyncBaseTool):
    """资源管理工具示例"""
    
    def __init__(self):
        self._resources: List[Any] = []
        self._cleanup_tasks: List[asyncio.Task] = []
    
    async def __aenter__(self):
        # 初始化资源
        await self._initialize_resources()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 清理资源
        await self._cleanup_resources()
    
    async def _initialize_resources(self):
        """初始化资源"""
        pass
    
    async def _cleanup_resources(self):
        """清理资源"""
        # 取消所有任务
        for task in self._cleanup_tasks:
            if not task.done():
                task.cancel()
        
        # 等待任务完成
        if self._cleanup_tasks:
            await asyncio.gather(*self._cleanup_tasks, return_exceptions=True)
```

### 3. 配置验证模式

```python
from typing import Type, get_type_hints

def validate_config_types(config_class: Type) -> Callable:
    """配置类型验证装饰器"""
    
    def decorator(cls):
        original_init = cls.__init__
        type_hints = get_type_hints(config_class)
        
        def validated_init(self, *args, **kwargs):
            # 验证类型
            for key, expected_type in type_hints.items():
                if key in kwargs:
                    value = kwargs[key]
                    if not isinstance(value, expected_type):
                        raise TypeError(f"配置项 {key} 期望类型 {expected_type}, 得到 {type(value)}")
            
            original_init(self, *args, **kwargs)
        
        cls.__init__ = validated_init
        return cls
    
    return decorator
```

## 🔗 相关资源

### 官方文档链接
- [Python asyncio文档](https://docs.python.org/3/library/asyncio.html)
- [aiohttp文档](https://docs.aiohttp.org/)
- [pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)

### 社区资源
- [Awesome Asyncio](https://github.com/timofurrer/awesome-asyncio)
- [Python异步编程最佳实践](https://github.com/python/asyncio/wiki)

### 工具和库
- [mypy](https://mypy.readthedocs.io/) - 静态类型检查
- [black](https://black.readthedocs.io/) - 代码格式化
- [flake8](https://flake8.pycqa.org/) - 代码风格检查
- [pytest](https://docs.pytest.org/) - 测试框架

---

*本文档随项目更新而持续维护。如有问题或建议，请提交Issue或Pull Request。*