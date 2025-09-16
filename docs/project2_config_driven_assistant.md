### 项目 2：配置驱动助手

#### 目标

- 学会使用 Pydantic 进行数据验证
- 掌握 TOML 配置文件处理
- 理解配置驱动开发模式

#### 核心代码实现

```python
# config_driven_assistant.py
from pydantic import BaseModel, Field
from typing import Optional, List
import toml
import asyncio
import openai

class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
    api_key: str = Field(description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    max_tokens: int = Field(default=1000, description="最大token数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")

class AssistantConfig(BaseModel):
    """助手配置模型"""
    name: str = Field(description="助手名称")
    description: str = Field(description="助手描述")
    system_prompt: str = Field(description="系统提示词")
    llm: LLMConfig = Field(description="LLM配置")
    max_history: int = Field(default=10, description="最大历史记录数")

class ConfigDrivenAssistant:
    def __init__(self, config_path: str):
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = toml.load(f)

        # 验证配置
        self.config = AssistantConfig(**config_data)

        # 初始化LLM客户端
        self.client = openai.AsyncOpenAI(
            api_key=self.config.llm.api_key,
            base_url=self.config.llm.base_url
        )

        # 初始化对话历史
        self.conversation_history = [
            {"role": "system", "content": self.config.system_prompt}
        ]

    async def process_message(self, user_message: str) -> str:
        """处理用户消息"""
        try:
            # 添加用户消息
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # 限制历史记录长度
            if len(self.conversation_history) > self.config.max_history + 1:
                # 保留系统提示词，删除最旧的对话
                self.conversation_history = (
                    [self.conversation_history[0]] +
                    self.conversation_history[-(self.config.max_history):]
                )

            # 调用LLM
            response = await self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=self.conversation_history,
                max_tokens=self.config.llm.max_tokens,
                temperature=self.config.llm.temperature
            )

            assistant_message = response.choices[0].message.content

            # 添加助手回复
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"处理消息时出错：{str(e)}"

    def get_info(self) -> dict:
        """获取助手信息"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "model": self.config.llm.model,
            "provider": self.config.llm.provider
        }

# 配置文件示例 (assistant_config.toml)
"""
name = "Python编程助手"
description = "专门帮助Python开发的AI助手"
system_prompt = "你是一个专业的Python编程助手，擅长解答Python相关问题，提供代码示例和最佳实践建议。"
max_history = 15

[llm]
provider = "openai"
model = "gpt-3.5-turbo"
api_key = "your-api-key-here"
max_tokens = 1500
temperature = 0.3
"""

# 使用示例
async def main():
    try:
        assistant = ConfigDrivenAssistant("assistant_config.toml")

        print(f"助手信息：{assistant.get_info()}")
        print("助手已启动！输入 'quit' 退出")

        while True:
            user_input = input("\n你: ")

            if user_input.lower() == 'quit':
                break

            response = await assistant.process_message(user_input)
            print(f"助手: {response}")

    except Exception as e:
        print(f"启动助手失败：{e}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **Pydantic 模型**：数据验证和序列化
2. **TOML 配置**：配置文件的读取和解析
3. **配置驱动**：通过配置控制程序行为
4. **错误处理**：配置验证和运行时错误处理