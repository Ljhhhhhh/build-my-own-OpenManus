# 项目5：ReAct推理代理

## 🎯 项目概述

这是一个基于ReAct（Reasoning and Acting）模式的智能推理代理实现。ReAct是一种先进的AI推理方法，通过循环的"思考-行动-观察"过程来解决复杂问题。

### 🌟 核心特性

- **🧠 ReAct推理模式**：实现完整的思考-行动-观察循环
- **🔧 工具系统集成**：支持多种工具的动态调用
- **📊 执行轨迹追踪**：完整记录推理过程，便于调试和分析
- **⚡ 异步执行**：高性能的异步编程实现
- **🛡️ 错误处理**：完善的异常处理和恢复机制
- **📈 统计分析**：详细的执行统计和性能监控

### 🏗️ 技术架构

```
ReActAgent (主代理)
├── 状态管理 (AgentState)
├── 步骤追踪 (ReActStep)
├── 循环控制 (solve方法)
├── 工具系统 (复用项目4)
│   ├── ToolManager
│   ├── BaseTool
│   └── 具体工具 (Calculator, TextProcessor等)
└── LLM集成 (OpenAI API)
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果需要）
cd practical5

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置你的 OpenAI API 密钥
# OPENAI_API_KEY=your_api_key_here
```

### 3. 运行程序

#### 方式一：运行预设测试用例
```bash
python main.py
```

#### 方式二：交互式演示
```bash
python demo.py
```

#### 方式三：运行测试
```bash
python -m pytest tests/ -v
```

## 📖 使用指南

### 基本使用

```python
import asyncio
from agent.react_agent import ReActAgent
from tools.manager import ToolManager
from tools.calculator import CalculatorTool

# 创建工具管理器
tool_manager = ToolManager()
calculator = CalculatorTool()
tool_manager.register_tool(calculator)

# 创建ReAct代理
agent = ReActAgent(
    tool_manager=tool_manager,
    max_steps=10,
    model="gpt-3.5-turbo"
)

# 解决问题
async def solve_problem():
    result = await agent.solve("计算 15 + 27 的结果")
    print(f"答案: {result['final_answer']}")
    print(f"推理步数: {result['total_steps']}")

asyncio.run(solve_problem())
```

### 高级配置

```python
# 自定义代理配置
agent = ReActAgent(
    tool_manager=tool_manager,
    max_steps=15,           # 最大推理步数
    model="gpt-4",          # 使用GPT-4模型
    temperature=0.2         # 降低随机性
)
```

## 🔧 可用工具

### 计算器工具 (Calculator)
- **功能**：基本数学运算（加、减、乘、除）
- **示例**：`{"name": "calculator", "parameters": {"operation": "add", "a": 5, "b": 3}}`

### 文本处理工具 (TextProcessor)
- **功能**：文本转换、分析、格式化
- **支持操作**：
  - 大小写转换：`uppercase`, `lowercase`, `capitalize`, `title`
  - 文本分析：`word_count`, `char_count`, `word_frequency`
  - 格式化：`remove_spaces`, `remove_newlines`
  - 提取：`extract_emails`, `extract_urls`
  - 替换：`replace`

## 📊 示例问题

### 简单计算
```
问题：计算 25 * 4 + 15 的结果
```

### 复杂推理
```
问题：如果一个长方形的长是12，宽是8，那么它的面积是多少？周长又是多少？
```

### 文本处理
```
问题：将文本'Hello World'转换为大写，然后统计字符数量
```

### 综合任务
```
问题：我有一段文本'The quick brown fox jumps over the lazy dog'，请帮我：
1）统计单词数量
2）转换为大写
3）计算如果每个单词价值5元，总价值是多少？
```

## 🏃‍♂️ 推理过程示例

```
🤔 正在思考问题: 计算 15 + 27 的结果
============================================================

🧠 推理过程:
----------------------------------------

💭 步骤 1 (thinking):
   思考: 用户要求计算15加27的结果，我需要使用计算器工具来完成这个计算。
   行动: {"name": "calculator", "parameters": {"operation": "add", "a": 15, "b": 27}}
   观察: 工具执行成功: {"operation": "add", "a": 15, "b": 27, "result": 42}
   耗时: 0.156秒

✅ 步骤 2 (finished):
   思考: 我已经使用计算器工具成功计算出15 + 27 = 42。
   观察: 最终答案: 15 + 27 = 42
   耗时: 0.089秒

============================================================
✅ 最终答案: 15 + 27 = 42

📈 执行统计:
   推理步数: 2
   总耗时: 0.67秒
   平均每步: 0.34秒
   使用工具: calculator
```

## 🧪 测试

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 运行特定测试
```bash
python -m pytest tests/test_react_agent.py::TestReActAgent::test_agent_initialization -v
```

### 测试覆盖率
```bash
pip install pytest-cov
python -m pytest tests/ --cov=agent --cov=tools --cov=utils
```

## 📁 项目结构

```
practical5/
├── agent/                    # 代理模块
│   ├── __init__.py
│   └── react_agent.py        # ReAct代理实现
├── tools/                    # 工具模块
│   ├── __init__.py
│   ├── base.py               # 基础工具类
│   ├── manager.py            # 工具管理器
│   ├── calculator.py         # 计算器工具
│   └── text_processor.py     # 文本处理工具
├── utils/                    # 工具类模块
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   └── logger.py             # 日志管理
├── tests/                    # 测试模块
│   ├── __init__.py
│   └── test_react_agent.py   # ReAct代理测试
├── logs/                     # 日志文件目录
├── .env.example              # 环境变量模板
├── requirements.txt          # 依赖包列表
├── main.py                   # 主程序入口
├── demo.py                   # 交互式演示
└── README.md                 # 项目文档
```

## 🔍 核心概念

### ReAct模式
ReAct（Reasoning and Acting）是一种结合推理和行动的AI方法：

1. **Thought（思考）**：分析当前情况，决定下一步行动
2. **Action（行动）**：执行具体的工具调用
3. **Observation（观察）**：获取行动结果，为下一轮思考提供信息

### 状态机设计
代理使用状态机管理推理过程：

- `THINKING`：思考阶段
- `ACTING`：行动阶段  
- `OBSERVING`：观察阶段
- `FINISHED`：完成状态
- `ERROR`：错误状态

### 提示词工程
精心设计的提示词确保LLM按照ReAct格式输出：

```
Thought: [思考过程]
Action: {"name": "工具名", "parameters": {...}}
Observation: [系统自动填入]

或者：

Thought: [最终思考]
Final Answer: [最终答案]
```

## ⚙️ 配置选项

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 必需 |
| `OPENAI_MODEL` | 使用的模型 | `gpt-3.5-turbo` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `MAX_CONCURRENT_TOOLS` | 最大并发工具数 | `5` |
| `TOOL_TIMEOUT` | 工具超时时间（秒） | `30` |

### 代理参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `max_steps` | 最大推理步数 | `10` |
| `model` | LLM模型 | `gpt-3.5-turbo` |
| `temperature` | 生成温度 | `0.1` |

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误：未设置OpenAI API密钥
   解决：在.env文件中设置OPENAI_API_KEY
   ```

2. **工具执行失败**
   ```
   检查工具参数是否正确
   查看日志文件了解详细错误信息
   ```

3. **推理循环过长**
   ```
   调整max_steps参数
   检查提示词是否清晰
   ```

### 调试技巧

1. **启用详细日志**
   ```python
   # 在.env中设置
   LOG_LEVEL=DEBUG
   ```

2. **查看执行轨迹**
   ```python
   result = await agent.solve("问题")
   for step in result['execution_trace']:
       print(f"步骤 {step['step_number']}: {step['thought']}")
   ```

3. **监控工具使用**
   ```python
   stats = tool_manager.get_stats()
   print(stats)
   ```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- OpenAI 提供的强大API
- ReAct论文的原始作者
- Python异步编程社区

## 📚 学习资源

- [ReAct论文](https://arxiv.org/abs/2210.03629)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Python异步编程指南](https://docs.python.org/3/library/asyncio.html)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)

---

**项目5完成！🎉** 

这个ReAct推理代理展示了如何构建一个能够进行复杂推理的AI系统。通过循环的思考-行动-观察过程，代理能够解决需要多步推理和工具调用的复杂问题。