# 项目8: MCP服务器实现

## 项目概述

本项目实现了一个完整的MCP（模型通信协议）服务器系统，支持工具注册、发现和调用，为分布式AI工具架构奠定基础。

### 核心功能

- **MCP协议实现** - 标准化的消息格式和通信协议
- **服务器端** - 工具注册、请求处理、响应生成
- **客户端** - 服务器连接、工具调用、错误处理
- **工具系统** - 可扩展的工具框架
- **异步通信** - 基于asyncio的高性能异步处理

## 项目结构

```
practical8/
├── README.md                    # 项目说明文档
├── requirements.txt             # 依赖包列表
├── .env.example                # 环境变量示例
├── demo.py                     # 完整演示程序
├── mcp/                        # MCP协议核心模块
│   ├── __init__.py
│   ├── protocol.py             # 协议定义（请求、响应、工具信息）
│   ├── server.py               # MCP服务器实现
│   └── client.py               # MCP客户端实现
├── servers/                    # 具体的MCP服务器实现
│   ├── __init__.py
│   └── calculator_server.py    # 计算器工具服务器
├── tools/                      # 工具实现
│   ├── __init__.py
│   ├── base.py                 # 工具基类
│   └── calculator.py           # 计算器工具
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   └── logger.py               # 日志管理
├── tests/                      # 测试模块
│   └── __init__.py
└── examples/                   # 使用示例
    ├── __init__.py
    └── basic_server.py         # 基础服务器示例
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，设置必要的配置
# 注意：OPENAI_API_KEY在本项目中主要用于配置验证，实际计算器工具不需要API调用
```

### 3. 运行演示

```bash
# 运行完整演示程序
python demo.py

# 或运行基础示例
python examples/basic_server.py
```

## 核心概念

### MCP协议

MCP（模型通信协议）是一个基于JSON-RPC 2.0的协议，用于AI代理与工具服务器之间的通信。

#### 消息格式

**请求消息**:
```json
{
    "jsonrpc": "2.0",
    "id": "request-1",
    "method": "tools/call",
    "params": {
        "name": "calculator",
        "arguments": {
            "expression": "2 + 3"
        }
    }
}
```

**响应消息**:
```json
{
    "jsonrpc": "2.0",
    "id": "request-1",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "5"
            }
        ]
    }
}
```

### 工具系统

工具系统采用插件化架构，每个工具都继承自`BaseTool`基类：

```python
from tools.base import SyncTool, ToolParameter, ToolResult

class MyTool(SyncTool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "My custom tool"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="input",
                type="string",
                description="Input parameter",
                required=True
            )
        ]
    
    def sync_execute(self, arguments: Dict[str, Any]) -> ToolResult:
        # 工具逻辑实现
        return ToolResult(success=True, data={"result": "processed"})
```

## 使用指南

### 创建MCP服务器

```python
import asyncio
from mcp.server import MCPServer, MCPTool
from tools.calculator import CalculatorTool

# 创建服务器
server = MCPServer("My-MCP-Server")

# 注册工具
calculator_tool = CalculatorMCPTool()
server.register_tool(calculator_tool)

# 启动服务器
asyncio.run(server.start())
```

### 使用MCP客户端

```python
import asyncio
from mcp.client import MCPClient

async def main():
    client = MCPClient()
    
    # 连接服务器
    await client.add_server("calculator", ["python", "servers/calculator_server.py"])
    
    # 列出工具
    tools = await client.list_all_tools()
    print("Available tools:", tools)
    
    # 调用工具
    result = await client.call_tool("calculator", "calculator", {
        "expression": "2 + 3 * 4"
    })
    print("Result:", result)
    
    # 清理
    await client.disconnect_all()

asyncio.run(main())
```

## 可用工具

### 计算器工具 (calculator)

基础数学计算工具，支持：
- 基本算术运算 (+, -, *, /, **)
- 数学函数 (sin, cos, tan, log, sqrt, etc.)
- 数学常数 (pi, e)

**使用示例**:
```python
result = await client.call_tool("calculator", "calculator", {
    "expression": "sin(pi/2) + sqrt(16)"
})
```

### 高级计算器工具 (advanced_calculator)

高级数学计算工具，支持：
- 统计计算 (均值、中位数、标准差等)
- 数列生成 (等差、等比、斐波那契)

**统计计算示例**:
```python
result = await client.call_tool("calculator", "advanced_calculator", {
    "operation": "statistics",
    "data": {
        "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
})
```

**数列生成示例**:
```python
result = await client.call_tool("calculator", "advanced_calculator", {
    "operation": "sequence",
    "data": {
        "type": "fibonacci",
        "count": 10
    }
})
```

## 架构设计

### 分层架构

1. **协议层** (`mcp/protocol.py`) - 定义MCP协议的数据结构和消息格式
2. **服务器层** (`mcp/server.py`) - 实现MCP服务器核心功能
3. **客户端层** (`mcp/client.py`) - 实现MCP客户端通信逻辑
4. **工具层** (`tools/`) - 提供可扩展的工具框架
5. **应用层** (`servers/`) - 具体的服务器实现

### 通信模式

- **进程间通信**: 通过stdin/stdout进行JSON消息交换
- **异步处理**: 基于asyncio的非阻塞I/O
- **错误处理**: 完整的错误传播和处理机制

## 扩展开发

### 添加新工具

1. 创建工具类：
```python
# tools/my_tool.py
from .base import SyncTool, ToolParameter, ToolResult

class MyTool(SyncTool):
    # 实现必要的方法
    pass
```

2. 创建MCP包装器：
```python
# servers/my_server.py
from mcp.server import MCPTool

class MyMCPTool(MCPTool):
    def __init__(self):
        self.tool = MyTool()
    
    def get_info(self):
        # 返回工具信息
        pass
    
    async def execute(self, arguments):
        # 执行工具
        pass
```

3. 创建服务器：
```python
# 注册工具到服务器
server = MCPServer("My-Server")
server.register_tool(MyMCPTool())
await server.start()
```

### 自定义协议扩展

可以通过扩展`MCPMethod`枚举来添加新的协议方法：

```python
class CustomMCPMethod(Enum):
    CUSTOM_METHOD = "custom/method"

# 在服务器中处理自定义方法
async def handle_custom_method(self, request):
    # 自定义处理逻辑
    pass
```

## 测试

```bash
# 运行基础示例测试
python examples/basic_server.py

# 运行完整演示（包含性能测试）
python demo.py
```

## 性能特性

- **并发处理**: 支持多个并发工具调用
- **连接池**: 高效的服务器连接管理
- **异步I/O**: 非阻塞的网络通信
- **资源管理**: 自动的连接清理和错误恢复

## 错误处理

系统提供完整的错误处理机制：

- **协议错误**: JSON解析错误、无效请求等
- **工具错误**: 工具执行失败、参数错误等
- **连接错误**: 服务器连接失败、超时等
- **系统错误**: 内部错误、资源不足等

## 日志系统

支持结构化日志记录：

```python
from utils.logger import get_logger

logger = get_logger("my_component")
logger.info("Operation completed", operation="test", result="success")
```

日志输出格式：
- **控制台**: 人类可读的格式
- **文件**: JSON格式，便于分析

## 配置管理

通过环境变量和配置文件管理系统设置：

```python
from utils.config import get_config

config = get_config()
print(f"Log level: {config.log_level}")
print(f"Server timeout: {config.server_timeout}")
```

## 对JavaScript开发者的说明

本项目的设计理念和模式与现代JavaScript/Node.js开发非常相似：

### 异步编程对比

**Python (asyncio)**:
```python
async def fetch_data():
    result = await some_async_operation()
    return result
```

**JavaScript (Promise)**:
```javascript
async function fetchData() {
    const result = await someAsyncOperation();
    return result;
}
```

### 模块系统对比

**Python**:
```python
from mcp.client import MCPClient
from utils.logger import get_logger
```

**JavaScript (ES6)**:
```javascript
import { MCPClient } from './mcp/client.js';
import { getLogger } from './utils/logger.js';
```

### 类定义对比

**Python**:
```python
class MCPClient:
    def __init__(self):
        self.connections = {}
    
    async def connect(self):
        # 连接逻辑
        pass
```

**JavaScript (ES6)**:
```javascript
class MCPClient {
    constructor() {
        this.connections = new Map();
    }
    
    async connect() {
        // 连接逻辑
    }
}
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查服务器命令是否正确
   - 确认Python路径和模块导入
   - 查看日志文件获取详细错误信息

2. **工具调用失败**
   - 验证工具参数格式
   - 检查工具是否正确注册
   - 确认服务器连接状态

3. **性能问题**
   - 调整并发连接数限制
   - 检查系统资源使用情况
   - 优化工具执行逻辑

### 调试技巧

1. **启用详细日志**:
```python
logger = setup_logging(log_level="DEBUG")
```

2. **检查连接状态**:
```python
status = client.get_status()
print(f"Connected servers: {status['connected_servers']}")
```

3. **测试单个工具**:
```python
# 直接测试工具而不通过MCP
tool = CalculatorTool()
result = await tool.execute({"expression": "2+2"})
```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 实现基础MCP协议
- 提供计算器工具示例
- 完整的文档和示例