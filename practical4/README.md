# 项目4：工具调用代理

## 🎯 项目目标

基于项目3的工具框架，学习如何将LLM与工具系统集成，实现智能的工具调用代理：

- 🤖 **LLM集成**：学习如何与OpenAI API交互
- 🔧 **智能工具选择**：让LLM决定何时使用哪个工具
- 📋 **工具调用解析**：从LLM响应中提取工具调用指令
- 🔄 **对话管理**：维护包含工具调用的对话历史

## 🌟 核心特性

### 1. 工具调用代理
- `ToolCallingAgent`：集成LLM和工具系统的智能代理
- 自动工具选择和执行
- 对话历史管理

### 2. 扩展工具集
- `CalculatorTool`：数学计算工具（继承自项目3）
- `TextProcessorTool`：文本处理工具（新增）
- 可扩展的工具架构

### 3. LLM集成
- OpenAI API集成
- 异步处理支持
- 错误处理和重试机制

## 🚀 快速开始

### 1. 安装依赖
```bash
cd practical4
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的OpenAI API密钥
```

### 3. 运行演示
```bash
# 运行工具调用代理演示
python main.py
```

## 📚 学习要点

### 1. **LLM与工具集成**
- 如何设计系统提示词
- 工具调用的JSON格式规范
- 从LLM响应中解析工具调用

### 2. **异步编程**
- `async/await` 语法
- 异步API调用
- 并发处理

### 3. **对话管理**
- 对话历史的维护
- 工具调用结果的集成
- 上下文的传递

## 🔧 项目结构

```
practical4/
├── README.md              # 项目说明
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量模板
├── main.py               # 主程序入口
├── agent/                # 代理模块
│   ├── __init__.py       # 包初始化
│   └── tool_calling_agent.py  # 工具调用代理
└── tools/                # 工具模块
    ├── __init__.py       # 包初始化
    ├── base.py           # 基础抽象类
    ├── manager.py        # 工具管理器
    ├── calculator.py     # 计算器工具
    └── text_processor.py # 文本处理工具
```

## 💡 使用示例

```python
from agent import ToolCallingAgent

# 创建代理
agent = ToolCallingAgent(api_key="your-openai-api-key")

# 处理用户消息
response = await agent.process_message("帮我计算 2 + 3 * 4")
print(response)  # 代理会自动调用计算器工具

response = await agent.process_message("把'hello world'转换成大写")
print(response)  # 代理会自动调用文本处理工具
```

## 🎓 学习路径

1. **理解工具调用流程**：从用户输入到工具执行的完整流程
2. **掌握LLM集成**：如何与OpenAI API交互
3. **学习异步编程**：Python的async/await模式
4. **实践对话管理**：如何维护对话状态和历史

## 🔗 相关项目

- [项目3：基础工具框架](../practical3/) - 工具系统的基础实现
- [项目5：ReAct代理](../docs/project5_react_agent.md) - 更高级的推理-行动模式