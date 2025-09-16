"""
自定义异常模块

定义聊天机器人应用程序的自定义异常类。
"""

from typing import Optional


class ChatBotError(Exception):
    """聊天机器人基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class APIError(ChatBotError):
    """API 调用相关错误"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, "API_ERROR")
        self.status_code = status_code


class ConfigurationError(ChatBotError):
    """配置相关错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class ValidationError(ChatBotError):
    """数据验证错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class RateLimitError(APIError):
    """API 速率限制错误"""
    
    def __init__(self, message: str = "API 请求频率过高，请稍后重试"):
        super().__init__(message, 429)
        self.error_code = "RATE_LIMIT_ERROR"


class AuthenticationError(APIError):
    """API 认证错误"""
    
    def __init__(self, message: str = "API 密钥无效或已过期"):
        super().__init__(message, 401)
        self.error_code = "AUTH_ERROR"