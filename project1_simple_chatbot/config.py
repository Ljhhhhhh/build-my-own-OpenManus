"""
配置管理模块

提供应用程序的配置管理功能，支持环境变量和默认值。
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class ChatBotConfig:
    """聊天机器人配置类"""
    
    # OpenAI API 配置
    api_key: str
    base_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # 应用配置
    log_level: str = "INFO"
    max_history_length: int = 50
    
    @classmethod
    def from_env(cls) -> "ChatBotConfig":
        """从环境变量创建配置实例"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY 环境变量未设置。请创建 .env 文件并设置您的 API 密钥。"
            )
        
        return cls(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
            max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_history_length=int(os.getenv("MAX_HISTORY_LENGTH", "50")),
        )
    
    def validate(self) -> None:
        """验证配置的有效性"""
        if not self.api_key:
            raise ValueError("API 密钥不能为空")
        
        if not 0 <= self.temperature <= 2:
            raise ValueError("温度值必须在 0 到 2 之间")
        
        if self.max_tokens <= 0:
            raise ValueError("最大令牌数必须大于 0")
        
        if self.max_history_length <= 0:
            raise ValueError("最大历史记录长度必须大于 0")


# 全局配置实例
config = ChatBotConfig.from_env()
config.validate()