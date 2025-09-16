"""
简单聊天机器人包

提供与 OpenAI API 交互的聊天机器人功能。
"""

from .chatbot import SimpleChatBot, Message, ConversationHistory
from .config import ChatBotConfig
from .exceptions import (
    ChatBotError,
    APIError,
    ConfigurationError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
)
from .logger import logger, setup_logger

__version__ = "1.0.0"
__author__ = "OpenManus Project"

__all__ = [
    # 核心类
    "SimpleChatBot",
    "Message", 
    "ConversationHistory",
    "ChatBotConfig",
    
    # 异常类
    "ChatBotError",
    "APIError",
    "ConfigurationError", 
    "ValidationError",
    "RateLimitError",
    "AuthenticationError",
    
    # 日志
    "logger",
    "setup_logger",
]