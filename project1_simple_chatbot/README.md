# 项目1：简单聊天机器人

一个优雅、可维护的 OpenAI 聊天机器人实现，展示了异步编程、错误处理和代码架构的最佳实践。

## ✨ 特性

- 🤖 **异步 OpenAI API 集成** - 高效的异步 API 调用
- 💬 **对话历史管理** - 智能的对话上下文保持
- 🎨 **彩色命令行界面** - 友好的用户交互体验
- 📡 **流式输出支持** - 实时显示 AI 回复
- ⚙️ **灵活配置管理** - 环境变量和配置文件支持
- 🛡️ **完善错误处理** - 优雅的异常处理和用户提示
- 📝 **详细日志记录** - 彩色日志输出，便于调试
- 🧪 **单元测试覆盖** - 确保代码质量和可靠性
- 🎯 **类型注解完整** - 提高代码可读性和 IDE 支持

## 🏗️ 项目结构

```
project1_simple_chatbot/
├── __init__.py              # 包初始化文件
├── main.py                  # 主程序入口
├── cli.py                   # 命令行界面
├── chatbot.py              # 核心聊天机器人类
├── config.py               # 配置管理
├── exceptions.py           # 自定义异常
├── logger.py               # 日志管理
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略文件
├── README.md              # 项目文档
└── tests/                 # 测试目录
    ├── __init__.py
    └── test_chatbot.py    # 单元测试
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.8 或更高版本：

```bash
python --version
```

### 2. 安装依赖

```bash
# 进入项目目录
cd project1_simple_chatbot

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制环境变量示例文件并配置您的 OpenAI API 密钥：

```bash
# 复制配置文件
copy .env.example .env

# 编辑 .env 文件，设置您的 API 密钥
# OPENAI_API_KEY=your_openai_api_key_here
```

或者直接设置环境变量：

```bash
set OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 运行程序

```bash
python main.py
```

## 🎮 使用指南

### 基本对话

启动程序后，直接输入消息即可与 AI 对话：

```
💬 你: 你好，请介绍一下自己
🤖 机器人: 你好！我是一个AI助手，基于OpenAI的语言模型...
```

### 可用命令

程序支持以下命令（以 `/` 开头）：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/clear` | 清空对话历史 |
| `/status` | 显示机器人状态和配置 |
| `/system` | 设置系统消息（角色设定） |
| `/stream` | 切换流式输出模式 |
| `/quit` | 退出程序 |

### 流式输出模式

使用 `/stream` 命令可以切换到流式输出模式，AI 的回复将实时显示：

```
💬 你: /stream
🔄 已切换到流式输出模式

📡 你: 请写一首关于春天的诗
🤖 机器人: 春风轻拂柳絮飞，
桃花满树映朝晖。
绿草如茵铺大地，
燕子归来话春归。
```

### 系统消息设置

使用 `/system` 命令可以设置 AI 的角色和行为：

```
💬 你: /system
🔧 设置系统消息（角色设定）:
请输入系统消息，用于设定机器人的角色和行为:
系统消息: 你是一个专业的 Python 编程助手，总是提供清晰、实用的代码示例。
✅ 系统消息已设置，对话历史已清空
```

## ⚙️ 配置选项

### 环境变量

在 `.env` 文件中可以配置以下选项：

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，自定义 API 端点

# 模型配置
DEFAULT_MODEL=gpt-3.5-turbo    # 默认模型
MAX_TOKENS=1000                # 最大令牌数
TEMPERATURE=0.7                # 温度参数（0-2）

# 应用配置
LOG_LEVEL=INFO                 # 日志级别
MAX_HISTORY_LENGTH=50          # 最大历史记录长度
```

### 支持的模型

- `gpt-3.5-turbo` (默认)
- `gpt-4`
- `gpt-4-turbo`
- 其他 OpenAI 兼容模型

## 🧪 运行测试

项目包含完整的单元测试：

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_chatbot.py

# 运行测试并显示覆盖率
python -m pytest tests/ --cov=.
```

## 🏗️ 代码架构

### 核心组件

1. **SimpleChatBot** - 主要的聊天机器人类
   - 异步 API 调用
   - 对话历史管理
   - 错误处理和重试

2. **ConversationHistory** - 对话历史管理器
   - 消息存储和检索
   - 历史长度限制
   - 消息格式转换

3. **ChatBotConfig** - 配置管理
   - 环境变量加载
   - 配置验证
   - 默认值处理

4. **自定义异常系统**
   - 分层异常处理
   - 详细错误信息
   - 用户友好的错误提示

### 设计原则

- **单一职责原则** - 每个类都有明确的职责
- **开闭原则** - 易于扩展，无需修改现有代码
- **依赖注入** - 通过配置对象注入依赖
- **异步优先** - 全面使用异步编程模式
- **类型安全** - 完整的类型注解

## 🔧 开发指南

### 代码风格

项目遵循 PEP 8 代码风格，使用以下工具：

```bash
# 代码格式化
black .

# 代码检查
flake8 .
```

### 添加新功能

1. 在相应模块中添加功能
2. 编写单元测试
3. 更新文档
4. 确保所有测试通过

### 错误处理

使用项目的自定义异常系统：

```python
from exceptions import ValidationError, APIError

# 输入验证
if not user_input.strip():
    raise ValidationError("输入不能为空")

# API 错误
try:
    response = await api_call()
except Exception as e:
    raise APIError(f"API 调用失败: {e}")
```

## 🐛 故障排除

### 常见问题

1. **API 密钥错误**
   ```
   ❌ API 认证失败: Invalid API key
   ```
   - 检查 `.env` 文件中的 `OPENAI_API_KEY` 设置
   - 确认 API 密钥有效且有足够余额

2. **网络连接问题**
   ```
   ❌ API 错误: Connection timeout
   ```
   - 检查网络连接
   - 考虑设置代理或使用自定义 API 端点

3. **依赖包问题**
   ```
   ModuleNotFoundError: No module named 'openai'
   ```
   - 运行 `pip install -r requirements.txt` 安装依赖

### 调试模式

设置日志级别为 DEBUG 以获取详细信息：

```bash
# 在 .env 文件中设置
LOG_LEVEL=DEBUG
```

## 📚 学习要点

通过这个项目，您将学习到：

1. **异步编程** - `async/await` 的正确使用
2. **API 集成** - 与第三方 API 的交互
3. **错误处理** - 优雅的异常处理策略
4. **配置管理** - 环境变量和配置文件的使用
5. **代码组织** - 模块化和面向对象设计
6. **测试驱动开发** - 单元测试的编写和运行
7. **用户体验** - 命令行界面的设计

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。

---

**Happy Coding! 🚀**