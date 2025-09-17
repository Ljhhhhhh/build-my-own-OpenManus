# 项目 1：简单聊天机器人

## 项目目标

- 掌握 OpenAI API 调用
- 理解异步编程基础
- 学会基本的错误处理

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

1. 复制 `.env.example` 文件并重命名为 `.env`
2. 在 `.env` 文件中填入你的 OpenAI API Key

```
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. 运行程序

```bash
python chatbot_v1.py
```

## 学习要点

1. **异步编程**：理解 `async/await` 的使用
2. **API 调用**：学会处理 HTTP 请求和响应
3. **错误处理**：使用 `try/except` 处理异常
4. **类型注解**：使用 `typing` 模块提高代码可读性

## 使用说明

- 启动程序后，直接输入消息与机器人对话
- 输入 `quit` 退出程序
- 程序会保持对话历史，直到退出或清空历史