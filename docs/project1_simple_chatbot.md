### 项目 1：简单聊天机器人

#### 目标

- 掌握 OpenAI API 调用
- 理解异步编程基础
- 学会基本的错误处理

#### 核心代码实现

```python
# chatbot_v1.py
import asyncio
import openai
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class SimpleChatBot:
    def __init__(self, api_key: str = None):
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.conversation_history: List[Dict[str, str]] = []

    async def chat(self, user_message: str) -> str:
        """发送消息并获取回复"""
        try:
            # 添加用户消息到历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=1000,
                temperature=0.7
            )

            # 提取回复
            assistant_message = response.choices[0].message.content

            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"错误：{str(e)}"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

# 使用示例
async def main():
    bot = SimpleChatBot()

    print("聊天机器人已启动！输入 'quit' 退出")

    while True:
        user_input = input("你: ")

        if user_input.lower() == 'quit':
            break

        response = await bot.chat(user_input)
        print(f"机器人: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **异步编程**：理解 `async/await` 的使用
2. **API 调用**：学会处理 HTTP 请求和响应
3. **错误处理**：使用 `try/except` 处理异常
4. **类型注解**：使用 `typing` 模块提高代码可读性