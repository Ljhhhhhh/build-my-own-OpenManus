#!/usr/bin/env python3
"""
项目2：配置驱动助手
基于项目1的基础上，使用Pydantic进行数据验证和TOML配置文件
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import toml
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 加载环境变量
load_dotenv()

class LLMConfig(BaseModel):
    """LLM配置模型 - 使用Pydantic进行数据验证"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    max_tokens: int = Field(default=1000, ge=1, le=4096, description="最大token数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    
    @validator('api_key', pre=True, always=True)
    def validate_api_key(cls, v):
        """验证API密钥，优先使用配置文件，其次使用环境变量"""
        if v is None or v == "":
            env_key = os.getenv('OPENAI_API_KEY')
            if env_key and env_key != 'your_openai_api_key_here':
                return env_key
            raise ValueError("API密钥未配置，请在配置文件中设置api_key或在环境变量中设置OPENAI_API_KEY")
        return v
    
    @validator('base_url', pre=True, always=True)
    def validate_base_url(cls, v):
        """验证基础URL"""
        if v is None or v == "":
            return os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        return v

class AssistantConfig(BaseModel):
    """助手配置模型"""
    name: str = Field(description="助手名称")
    description: str = Field(description="助手描述")
    system_prompt: str = Field(description="系统提示词")
    llm: LLMConfig = Field(description="LLM配置")
    max_history: int = Field(default=10, ge=1, le=50, description="最大历史记录数")
    
    @validator('name')
    def validate_name(cls, v):
        """验证助手名称"""
        if len(v.strip()) == 0:
            raise ValueError("助手名称不能为空")
        return v.strip()
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        """验证系统提示词"""
        if len(v.strip()) == 0:
            raise ValueError("系统提示词不能为空")
        return v.strip()

class ConfigDrivenAssistant:
    """配置驱动的AI助手"""
    
    def __init__(self, config_path: str):
        """
        初始化配置驱动助手
        
        Args:
            config_path: TOML配置文件路径
        """
        self.config_path = config_path
        self._load_config()
        self._init_client()
        self._init_conversation()
    
    def _load_config(self):
        """加载并验证配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = toml.load(f)
            
            # 使用Pydantic验证配置
            self.config = AssistantConfig(**config_data)
            print(f"✅ 配置文件加载成功: {self.config_path}")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except toml.TomlDecodeError as e:
            raise ValueError(f"TOML配置文件格式错误: {e}")
        except Exception as e:
            raise ValueError(f"配置验证失败: {e}")
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            self.client = AsyncOpenAI(
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url
            )
            print(f"✅ OpenAI客户端初始化成功")
        except Exception as e:
            raise RuntimeError(f"OpenAI客户端初始化失败: {e}")
    
    def _init_conversation(self):
        """初始化对话历史"""
        self.conversation_history = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        print(f"✅ 对话历史初始化完成")
    
    async def process_message(self, user_message: str) -> str:
        """
        处理用户消息
        
        Args:
            user_message: 用户输入的消息
            
        Returns:
            助手的回复
        """
        try:
            # 添加用户消息到历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # 限制历史记录长度（保留系统提示词）
            if len(self.conversation_history) > self.config.max_history + 1:
                # 保留系统提示词，删除最旧的对话
                self.conversation_history = (
                    [self.conversation_history[0]] +  # 系统提示词
                    self.conversation_history[-(self.config.max_history):]  # 最近的对话
                )
            
            # 调用LLM API
            response = await self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=self.conversation_history,
                max_tokens=self.config.llm.max_tokens,
                temperature=self.config.llm.temperature
            )
            
            assistant_message = response.choices[0].message.content
            
            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            error_msg = f"处理消息时出错：{str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def get_info(self) -> Dict[str, Any]:
        """获取助手信息"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "model": self.config.llm.model,
            "provider": self.config.llm.provider,
            "max_tokens": self.config.llm.max_tokens,
            "temperature": self.config.llm.temperature,
            "max_history": self.config.max_history,
            "history_length": len(self.conversation_history) - 1  # 减去系统提示词
        }
    
    def clear_history(self):
        """清空对话历史（保留系统提示词）"""
        self.conversation_history = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        print("🧹 对话历史已清空")
    
    def get_history_length(self) -> int:
        """获取当前对话历史长度"""
        return len(self.conversation_history) - 1  # 减去系统提示词
    
    def reload_config(self):
        """重新加载配置文件"""
        try:
            old_config = self.config.dict()
            self._load_config()
            self._init_client()
            
            # 如果系统提示词改变，重新初始化对话
            if old_config['system_prompt'] != self.config.system_prompt:
                self._init_conversation()
                print("🔄 系统提示词已更新，对话历史已重置")
            
            print("🔄 配置重新加载成功")
            
        except Exception as e:
            print(f"❌ 配置重新加载失败: {e}")

# 主程序入口
async def main():
    """主程序入口"""
    print("🚀 配置驱动助手 - 项目2")
    print("=" * 50)
    
    # 默认配置文件
    config_file = "assistant_config.toml"
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        print("💡 请先创建配置文件，参考 README.md")
        return
    
    try:
        # 初始化助手
        assistant = ConfigDrivenAssistant(config_file)
        
        # 显示助手信息
        info = assistant.get_info()
        print(f"\n🤖 助手名称: {info['name']}")
        print(f"📝 助手描述: {info['description']}")
        print(f"🔧 使用模型: {info['model']}")
        print(f"🌡️  温度参数: {info['temperature']}")
        print(f"📊 最大历史: {info['max_history']} 条")
        
        print("\n💡 可用命令:")
        print("  • 'quit' - 退出程序")
        print("  • 'clear' - 清空对话历史")
        print("  • 'info' - 显示助手信息")
        print("  • 'reload' - 重新加载配置")
        print("  • 'history' - 查看对话历史长度")
        print("-" * 50)
        
        # 主对话循环
        while True:
            try:
                user_input = input(f"\n你: ").strip()
                
                if not user_input:
                    print("⚠️ 请输入有效消息")
                    continue
                
                # 处理特殊命令
                if user_input.lower() == 'quit':
                    print("👋 再见！")
                    break
                elif user_input.lower() == 'clear':
                    assistant.clear_history()
                    continue
                elif user_input.lower() == 'info':
                    info = assistant.get_info()
                    print(f"📊 助手信息:")
                    for key, value in info.items():
                        print(f"   {key}: {value}")
                    continue
                elif user_input.lower() == 'reload':
                    assistant.reload_config()
                    continue
                elif user_input.lower() == 'history':
                    print(f"📊 当前对话历史: {assistant.get_history_length()} 条消息")
                    continue
                
                # 处理正常对话
                print(f"{info['name']}: ", end="", flush=True)
                response = await assistant.process_message(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                
    except Exception as e:
        print(f"❌ 助手启动失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())