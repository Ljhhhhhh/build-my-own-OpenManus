# 项目3：基础工具框架

## 🎯 项目目标

基于项目1和项目2的基础，学习如何为AI代理构建可扩展的工具系统：

- 🔧 **工具抽象**：学习抽象基类(ABC)和接口设计
- 📋 **JSON Schema**：掌握工具参数的结构化定义
- 🔌 **插件架构**：理解动态注册和管理工具的机制
- ⚠️ **错误处理**：统一的结果格式和异常处理

## 🌟 核心特性

### 1. 工具基类系统
- `BaseTool`：所有工具的抽象基类
- `ToolResult`：统一的工具执行结果格式
- `ToolResultStatus`：执行状态枚举

### 2. 具体工具实现
- `CalculatorTool`：安全的数学计算器
- `WeatherTool`：天气查询工具
- 可扩展的工具架构

### 3. 工具管理器
- `ToolManager`：工具的注册、管理和执行
- 动态工具发现和调用
- 参数验证和错误处理

## 🚀 快速开始

### 1. 安装依赖
```bash
cd practical3
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
```

### 3. 运行演示
```bash
# 运行基础工具演示
python tool_demo.py

# 运行完整的工具框架演示
python main.py
```

## 📚 学习要点

### 1. **抽象基类 (ABC)**
```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs):
        pass
```
- 定义接口规范
- 强制子类实现必要方法
- 提供代码结构和一致性

### 2. **JSON Schema**
```python
def get_schema(self) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式"
            }
        },
        "required": ["expression"]
    }
```
- 定义工具参数结构
- 支持自动验证和文档生成
- 标准化的接口描述

### 3. **插件架构**
```python
manager = ToolManager()
manager.register_tool(CalculatorTool())
manager.register_tool(WeatherTool(api_key))
```
- 动态注册工具
- 松耦合的设计
- 易于扩展和维护

### 4. **统一错误处理**
```python
class ToolResult(BaseModel):
    status: ToolResultStatus
    content: Any
    error_message: Optional[str]
```
- 标准化的返回格式
- 清晰的成功/失败状态
- 详细的错误信息

## 📁 文件结构

```
practical3/
├── tools/
│   ├── __init__.py          # 工具包初始化
│   ├── base.py              # 基础工具类和结果模型
│   ├── calculator.py        # 计算器工具
│   ├── weather.py           # 天气查询工具
│   └── manager.py           # 工具管理器
├── main.py                  # 主程序入口
├── tool_demo.py             # 工具演示脚本
├── requirements.txt         # 依赖文件
├── .env.example            # 环境变量示例
└── README.md               # 项目文档
```

## 🔗 与前面项目的关系

- **项目1基础**：继承基本的OpenAI客户端和环境配置
- **项目2进阶**：使用Pydantic进行数据验证和配置管理
- **项目3扩展**：在前两个项目基础上，构建可扩展的工具系统

## 💡 Python小白学习重点

1. **抽象基类**：理解接口和继承的概念
2. **异步编程**：掌握async/await的使用
3. **类型注解**：学习Python的类型系统
4. **设计模式**：理解插件模式和工厂模式
5. **错误处理**：学习异常处理的最佳实践