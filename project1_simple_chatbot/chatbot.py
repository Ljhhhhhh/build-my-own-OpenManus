"""
聊天机器人核心模块

实现与 OpenAI API 交互的聊天机器人类，提供优雅的接口和完善的错误处理。
"""

import asyncio
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

import openai
from openai import AsyncOpenAI

from config import ChatBotConfig
from exceptions import (
    APIError, 
    RateLimitError, 
    AuthenticationError, 
    ValidationError
)
from logger import logger


@dataclass
class Message:
    """消息数据类"""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        """转换为 OpenAI API 格式"""
        return {"role": self.role, "content": self.content}
    
    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.role}: {self.content}"


class ConversationHistory:
    """对话历史管理器"""
    
    def __init__(self, max_length: int = 50):
        self.max_length = max_length
        self._messages: List[Message] = []
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到历史记录"""
        if not content.strip():
            raise ValidationError("消息内容不能为空")
        
        message = Message(role=role, content=content.strip())
        self._messages.append(message)
        
        # 保持历史记录在限制范围内
        if len(self._messages) > self.max_length:
            self._messages = self._messages[-self.max_length:]
        
        logger.debug(f"添加消息: {message}")
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """获取用于 API 调用的消息格式"""
        return [msg.to_dict() for msg in self._messages]
    
    def clear(self) -> None:
        """清空历史记录"""
        self._messages.clear()
        logger.info("对话历史已清空")
    
    def get_last_messages(self, count: int) -> List[Message]:
        """获取最后 N 条消息"""
        return self._messages[-count:] if count > 0 else []
    
    @property
    def message_count(self) -> int:
        """获取消息总数"""
        return len(self._messages)
    
    def __len__(self) -> int:
        return len(self._messages)
    
    def __iter__(self):
        return iter(self._messages)


class SimpleChatBot:
    """简单聊天机器人类
    
    提供与 OpenAI API 交互的功能，支持对话历史管理和错误处理。
    """
    
    def __init__(self, config: Optional[ChatBotConfig] = None):
        """
        初始化聊天机器人
        
        Args:
            config: 配置对象，如果为 None 则使用默认配置
        """
        from config import config as default_config
        
        self.config = config or default_config
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        self.history = ConversationHistory(self.config.max_history_length)
        
        logger.info(f"聊天机器人已初始化，使用模型: {self.config.model}")
    
    async def chat(self, user_message: str) -> str:
        """
        发送消息并获取回复
        
        Args:
            user_message: 用户消息
            
        Returns:
            助手回复
            
        Raises:
            ValidationError: 消息验证失败
            APIError: API 调用失败
        """
        if not user_message.strip():
            raise ValidationError("用户消息不能为空")
        
        try:
            # 添加用户消息到历史
            self.history.add_message("user", user_message)
            
            # 调用 OpenAI API
            logger.debug(f"发送 API 请求，消息数量: {self.history.message_count}")
            
            response = await self._make_api_request()
            assistant_message = self._extract_message_content(response)
            
            # 添加助手回复到历史
            self.history.add_message("assistant", assistant_message)
            
            logger.info(f"成功获取回复，长度: {len(assistant_message)} 字符")
            return assistant_message
            
        except Exception as e:
            logger.error(f"聊天过程中发生错误: {e}")
            # 如果是我们的自定义异常，直接抛出
            if isinstance(e, (ValidationError, APIError)):
                raise
            # 否则包装为 APIError
            raise APIError(f"聊天过程中发生未知错误: {str(e)}")
    
    async def chat_stream(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        流式聊天，逐步返回回复内容
        
        Args:
            user_message: 用户消息
            
        Yields:
            助手回复的片段
        """
        if not user_message.strip():
            raise ValidationError("用户消息不能为空")
        
        try:
            # 添加用户消息到历史
            self.history.add_message("user", user_message)
            
            # 流式 API 调用
            full_response = ""
            async for chunk in await self._make_stream_api_request():
                if chunk:
                    full_response += chunk
                    yield chunk
            
            # 添加完整回复到历史
            if full_response:
                self.history.add_message("assistant", full_response)
                
        except Exception as e:
            logger.error(f"流式聊天过程中发生错误: {e}")
            if isinstance(e, (ValidationError, APIError)):
                raise
            raise APIError(f"流式聊天过程中发生未知错误: {str(e)}")
    
    async def _make_api_request(self):
        """执行 API 请求"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=self.history.get_messages_for_api(),
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response
            
        except openai.AuthenticationError as e:
            raise AuthenticationError(f"API 认证失败: {str(e)}")
        except openai.RateLimitError as e:
            raise RateLimitError(f"API 请求频率限制: {str(e)}")
        except openai.APIError as e:
            raise APIError(f"OpenAI API 错误: {str(e)}")
        except Exception as e:
            raise APIError(f"API 请求失败: {str(e)}")
    
    async def _make_stream_api_request(self):
        """执行流式 API 请求"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=self.history.get_messages_for_api(),
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except openai.AuthenticationError as e:
            raise AuthenticationError(f"API 认证失败: {str(e)}")
        except openai.RateLimitError as e:
            raise RateLimitError(f"API 请求频率限制: {str(e)}")
        except openai.APIError as e:
            raise APIError(f"OpenAI API 错误: {str(e)}")
        except Exception as e:
            raise APIError(f"流式 API 请求失败: {str(e)}")
    
    def _extract_message_content(self, response) -> str:
        """从 API 响应中提取消息内容"""
        try:
            content = response.choices[0].message.content
            if content is None:
                raise APIError("API 返回的消息内容为空")
            return content.strip()
        except (IndexError, AttributeError) as e:
            raise APIError(f"无法解析 API 响应: {str(e)}")
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.history.clear()
    
    def get_conversation_summary(self) -> Dict[str, any]:
        """获取对话摘要信息"""
        return {
            "message_count": self.history.message_count,
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "last_messages": [str(msg) for msg in self.history.get_last_messages(3)]
        }
    
    def set_system_message(self, system_message: str) -> None:
        """设置系统消息（需要清空历史后重新开始对话）"""
        if not system_message.strip():
            raise ValidationError("系统消息不能为空")
        
        self.clear_history()
        self.history.add_message("system", system_message)
        logger.info("系统消息已设置")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.client.close()
        logger.info("聊天机器人客户端已关闭")