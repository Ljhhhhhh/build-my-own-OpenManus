# chatbot_v1.py
import asyncio
from pyexpat import model
import openai
from typing import List, Dict
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SimpleChatBot:
    """简单的聊天机器人类
    
    这个类演示了以下Python AI开发的核心概念：
    1. 异步编程 (async/await)
    2. OpenAI API 调用
    3. 类型注解 (Type Hints)
    4. 错误处理
    """
    
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        """初始化聊天机器人
        
        Args:
            api_key: OpenAI API密钥，如果不提供则从环境变量读取
            model: 使用的模型名称，如果不提供则从环境变量读取
            base_url: API基础URL，如果不提供则从环境变量读取
        """
        # 创建异步OpenAI客户端
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        )
        
        # 设置模型名称
        self.model = model or os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")
        
        # 对话历史列表，每个元素是包含role和content的字典
        self.conversation_history: List[Dict[str, str]] = []

    async def chat(self, user_message: str) -> str:
        """发送消息并获取回复
        
        Args:
            user_message: 用户输入的消息
            
        Returns:
            str: AI助手的回复消息
        """
        try:
            # 添加用户消息到对话历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # 调用OpenAI API - 这是异步操作
            response = await self.client.chat.completions.create(
                model=self.model,  # 使用配置的模型
                messages=self.conversation_history,  # 发送完整对话历史
                max_tokens=1000,  # 限制回复长度
                temperature=0.7   # 控制回复的创造性
            )

            # 提取AI助手的回复
            assistant_message = response.choices[0].message.content

            # 添加助手回复到对话历史
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except openai.AuthenticationError:
            return "错误：API密钥无效，请检查你的OpenAI API Key"
        except openai.RateLimitError:
            return "错误：API调用频率超限，请稍后再试"
        except openai.APIConnectionError:
            return "错误：网络连接失败，请检查网络连接"
        except Exception as e:
            return f"错误：{str(e)}"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("对话历史已清空")

    def get_history_length(self) -> int:
        """获取对话历史长度"""
        return len(self.conversation_history)

    def get_current_model(self) -> str:
        """获取当前使用的模型"""
        return self.model
    
    def set_model(self, model: str):
        """设置使用的模型
        
        Args:
            model: 新的模型名称，如 'gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo' 等
        """
        self.model = model
        print(f"✅ 模型已切换为: {model}")

# 主程序入口
async def main():
    """主程序函数 - 演示异步编程的使用"""
    # 创建聊天机器人实例
    bot = SimpleChatBot()

    print("🤖 简单聊天机器人已启动！")
    print(f"🔧 当前使用模型: {bot.get_current_model()}")
    print("💡 输入 'quit' 退出程序")
    print("💡 输入 'clear' 清空对话历史")
    print("💡 输入 'history' 查看对话历史长度")
    print("💡 输入 'model' 查看当前模型")
    print("💡 输入 'model:模型名' 切换模型 (如: model:gpt-4)")
    print("-" * 50)

    while True:
        try:
            # 获取用户输入
            user_input = input("你: ").strip()

            # 处理特殊命令
            if user_input.lower() == 'quit':
                print("👋 再见！")
                break
            elif user_input.lower() == 'clear':
                bot.clear_history()
                continue
            elif user_input.lower() == 'history':
                print(f"📊 当前对话历史长度: {bot.get_history_length()} 条消息")
                continue
            elif user_input.lower() == 'model':
                print(f"🔧 当前使用模型: {bot.get_current_model()}")
                continue
            elif user_input.lower().startswith('model:'):
                new_model = user_input[6:].strip()  # 提取模型名称
                if new_model:
                    bot.set_model(new_model)
                else:
                    print("⚠️ 请提供有效的模型名称，如: model:gpt-4")
                continue
            elif not user_input:
                print("⚠️ 请输入有效消息")
                continue

            # 发送消息并获取回复 - 这里使用await等待异步操作完成
            print("🤔 思考中...")
            response = await bot.chat(user_input)
            print(f"🤖 机器人: {response}")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 程序错误: {str(e)}")

# Python程序入口点
if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())