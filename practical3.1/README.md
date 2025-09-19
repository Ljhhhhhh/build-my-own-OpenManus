# Practical3.1 - 基础工具系统

## 🎯 学习目标

这是从practical3拆分出来的第一个学习项目，专注于Python基础概念和面向对象编程。作为前端开发者，你会发现这些概念与TypeScript非常相似！

### 核心学习重点
- 🏗️ **抽象基类 (ABC)** - 类似TypeScript的interface
- 📝 **类型注解** - 类似TypeScript的类型系统  
- 🔧 **基础工具实现** - 简单的业务逻辑
- ✅ **数据验证** - 使用Pydantic（类似Zod）
- 🎨 **枚举类型** - 类似TypeScript的enum

## 🌟 项目特色

### 与前端开发的对比
```typescript
// TypeScript 接口
interface Tool {
  name: string;
  execute(params: any): Promise<Result>;
}

// Python 抽象基类
class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass
```

## 📁 项目结构

```
practical3.1/
├── README.md           # 项目说明
├── requirements.txt    # 依赖包
├── main.py            # 主程序入口
├── tools/             # 工具模块
│   ├── __init__.py    # 包初始化
│   ├── base.py        # 基础抽象类
│   └── calculator.py  # 计算器工具
└── examples/          # 学习示例
    └── basic_usage.py # 基础用法演示
```

## 🚀 快速开始

### 1. 安装依赖
```bash
cd practical3.1
pip install -r requirements.txt
```

### 2. 运行基础演示
```bash
python main.py
```

### 3. 学习示例
```bash
python examples/basic_usage.py
```

## 📚 学习路径

### 第一步：理解抽象基类
- 查看 `tools/base.py` 中的 `BaseTool` 类
- 理解抽象方法的概念
- 对比TypeScript的interface

### 第二步：实现具体工具
- 查看 `tools/calculator.py` 的实现
- 理解继承和方法重写
- 学习JSON Schema的使用

### 第三步：运行和测试
- 运行 `main.py` 查看完整演示
- 修改计算器逻辑，添加新的运算
- 尝试创建自己的工具

## 🎓 学习要点详解

### 1. 抽象基类 vs TypeScript接口
```python
# Python抽象基类
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs):
        pass
```

```typescript
// TypeScript接口
interface BaseTool {
  execute(params: any): Promise<any>;
}
```

### 2. 类型注解 vs TypeScript类型
```python
# Python类型注解
def calculate(a: int, b: int) -> int:
    return a + b
```

```typescript
// TypeScript类型
function calculate(a: number, b: number): number {
  return a + b;
}
```

### 3. 枚举类型对比
```python
# Python枚举
from enum import Enum

class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
```

```typescript
// TypeScript枚举
enum Status {
  SUCCESS = "success",
  ERROR = "error"
}
```

## 🔧 实践练习

1. **扩展计算器**：添加更多运算（幂运算、取模等）
2. **创建新工具**：实现一个字符串处理工具
3. **改进验证**：添加更复杂的参数验证逻辑

## 📖 相关概念

- **抽象基类 (ABC)**：强制子类实现特定方法
- **类型注解**：提供代码可读性和IDE支持
- **Pydantic**：数据验证和序列化库
- **枚举类型**：定义一组命名常量

## ➡️ 下一步

完成practical3.1后，继续学习practical3.2，那里会涉及：
- 异步编程和并发
- 外部API集成
- 批量处理和性能优化
- 更复杂的错误处理机制