# Practical 3.2: 异步工具系统基础

## 🎯 项目概述

Practical 3.2是一个简化的异步工具系统，专为学习Python异步编程基础而设计。本项目通过实际的工具实现，展示了异步编程的核心概念和基础模式。

### 🌟 核心特性

- **异步编程基础**: 基于`asyncio`的异步架构
- **工具管理**: 简单的工具注册和执行系统
- **外部API集成**: 天气API集成示例
- **错误处理**: 基础的异常处理机制
- **配置管理**: 环境变量管理
- **类型注解**: 现代Python类型系统的使用

### 🎓 学习目标

通过本项目，你将学习到：

1. **异步编程基础**
   - `async`/`await` 语法的使用
   - 异步函数的定义和调用
   - 基础的并发任务管理
   - 异步上下文管理器

2. **Python基础特性**
   - 抽象基类 (ABC) 的使用
   - 类型注解的应用
   - 单例模式的实现
   - 基础的面向对象编程

3. **外部API集成**
   - HTTP客户端的基础使用
   - API调用和错误处理
   - JSON数据的处理
   - 环境变量的管理

4. **软件工程基础**
   - 项目结构的组织
   - 模块化设计
   - 基础的测试编写
   - 文档的编写

## 🏗️ 项目结构

```
practical3.2/
├── 📁 tools/                    # 工具模块
│   ├── __init__.py             # 包初始化
│   ├── base.py                 # 基础工具类
│   ├── manager.py              # 工具管理器
│   ├── calculator.py           # 计算器工具
│   ├── weather.py              # 天气查询工具
│   └── utils.py                # 工具函数
├── 📄 config.py                 # 配置管理
├── 📄 main.py                   # 主程序
├── 📄 requirements.txt          # 依赖列表
├── 📄 .env.example             # 环境变量模板
└── 📄 README.md                # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的API密钥
# OPENWEATHER_API_KEY=your_api_key_here
```

### 3. 运行程序

```bash
# 运行主程序
python main.py
```

## 📚 核心概念

### 异步编程基础

```python
# 异步函数定义
async def async_function():
    await some_async_operation()

# 异步函数调用
result = await async_function()

# 并发执行
tasks = [async_function() for _ in range(3)]
results = await asyncio.gather(*tasks)
```

### 工具系统架构

```python
# 基础工具类
class AsyncBaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs):
        pass

# 工具管理器
class AsyncToolManager:
    def register_tool(self, name: str, tool: AsyncBaseTool):
        self.tools[name] = tool
    
    async def execute_tool(self, name: str, **kwargs):
        return await self.tools[name].execute(**kwargs)
```

### 配置管理

```python
# 单例模式配置类
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
```

## 🔧 主要组件

### 1. AsyncBaseTool (基础工具类)
- 定义工具的基础接口
- 提供异步执行方法
- 包含基础的错误处理

### 2. AsyncToolManager (工具管理器)
- 管理工具的注册和执行
- 提供统一的工具调用接口
- 处理工具执行的错误

### 3. AsyncCalculatorTool (计算器工具)
- 实现基础的数学运算
- 展示异步工具的实现模式
- 包含输入验证和错误处理

### 4. AsyncWeatherTool (天气工具)
- 集成外部天气API
- 展示HTTP客户端的使用
- 演示JSON数据的处理

### 5. Config (配置管理)
- 管理应用程序配置
- 处理环境变量
- 实现单例模式

## 💡 学习要点

### 异步编程
- 理解`async`/`await`的工作原理
- 学习异步函数的定义和调用
- 掌握基础的并发执行模式

### 面向对象编程
- 抽象基类的使用
- 继承和多态的应用
- 单例模式的实现

### 外部API集成
- HTTP客户端的基础使用
- API调用的错误处理
- 环境变量的安全管理

### 类型注解
- 基础类型注解的使用
- 泛型类型的应用
- 类型检查的好处

## 🧪 测试运行

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_calculator.py

# 查看测试覆盖率
pytest --cov=tools
```

## 📖 进一步学习

1. **异步编程深入**
   - 学习更多asyncio模块的功能
   - 理解事件循环的工作原理
   - 掌握异步生成器的使用

2. **API集成进阶**
   - 学习更多HTTP客户端功能
   - 掌握API认证的各种方式
   - 了解缓存和重试机制

3. **Python进阶特性**
   - 深入学习装饰器模式
   - 掌握上下文管理器
   - 了解元类和描述符

## 🤝 贡献指南

欢迎提交问题和改进建议！请确保：
- 代码符合项目的编码规范
- 添加适当的测试用例
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

---

**Happy Learning! 🎉**