"""
聊天机器人单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from chatbot import SimpleChatBot, Message, ConversationHistory
from config import ChatBotConfig
from exceptions import ValidationError, APIError, AuthenticationError


class TestMessage:
    """测试 Message 类"""
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)
    
    def test_message_to_dict(self):
        """测试消息转换为字典"""
        msg = Message(role="assistant", content="Hi there!")
        result = msg.to_dict()
        expected = {"role": "assistant", "content": "Hi there!"}
        assert result == expected
    
    def test_message_str(self):
        """测试消息字符串表示"""
        msg = Message(role="user", content="Test message")
        str_repr = str(msg)
        assert "user" in str_repr
        assert "Test message" in str_repr


class TestConversationHistory:
    """测试 ConversationHistory 类"""
    
    def test_add_message(self):
        """测试添加消息"""
        history = ConversationHistory(max_length=5)
        history.add_message("user", "Hello")
        
        assert history.message_count == 1
        assert len(history) == 1
    
    def test_add_empty_message_raises_error(self):
        """测试添加空消息抛出错误"""
        history = ConversationHistory()
        
        with pytest.raises(ValidationError):
            history.add_message("user", "")
        
        with pytest.raises(ValidationError):
            history.add_message("user", "   ")
    
    def test_max_length_limit(self):
        """测试最大长度限制"""
        history = ConversationHistory(max_length=3)
        
        # 添加超过限制的消息
        for i in range(5):
            history.add_message("user", f"Message {i}")
        
        assert history.message_count == 3
        # 应该保留最后3条消息
        messages = history.get_messages_for_api()
        assert messages[-1]["content"] == "Message 4"
        assert messages[-2]["content"] == "Message 3"
        assert messages[-3]["content"] == "Message 2"
    
    def test_clear_history(self):
        """测试清空历史"""
        history = ConversationHistory()
        history.add_message("user", "Hello")
        history.add_message("assistant", "Hi")
        
        assert history.message_count == 2
        
        history.clear()
        assert history.message_count == 0
    
    def test_get_last_messages(self):
        """测试获取最后N条消息"""
        history = ConversationHistory()
        history.add_message("user", "Message 1")
        history.add_message("assistant", "Response 1")
        history.add_message("user", "Message 2")
        
        last_two = history.get_last_messages(2)
        assert len(last_two) == 2
        assert last_two[0].content == "Response 1"
        assert last_two[1].content == "Message 2"


class TestSimpleChatBot:
    """测试 SimpleChatBot 类"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置"""
        return ChatBotConfig(
            api_key="test-key",
            model="gpt-3.5-turbo",
            max_tokens=100,
            temperature=0.7
        )
    
    @pytest.fixture
    def chatbot(self, mock_config):
        """创建聊天机器人实例"""
        with patch('chatbot.AsyncOpenAI') as mock_client:
            bot = SimpleChatBot(mock_config)
            bot.client = AsyncMock()
            return bot
    
    def test_chatbot_initialization(self, mock_config):
        """测试聊天机器人初始化"""
        with patch('chatbot.AsyncOpenAI') as mock_client:
            bot = SimpleChatBot(mock_config)
            assert bot.config == mock_config
            assert isinstance(bot.history, ConversationHistory)
    
    def test_empty_message_validation(self, chatbot):
        """测试空消息验证"""
        with pytest.raises(ValidationError):
            asyncio.run(chatbot.chat(""))
        
        with pytest.raises(ValidationError):
            asyncio.run(chatbot.chat("   "))
    
    @pytest.mark.asyncio
    async def test_successful_chat(self, chatbot):
        """测试成功的聊天"""
        # 模拟 API 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        
        chatbot.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        response = await chatbot.chat("Hello")
        
        assert response == "Hello! How can I help you?"
        assert chatbot.history.message_count == 2  # 用户消息 + 助手回复
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, chatbot):
        """测试 API 错误处理"""
        import openai
        
        # 模拟认证错误
        chatbot.client.chat.completions.create = AsyncMock(
            side_effect=openai.AuthenticationError("Invalid API key")
        )
        
        with pytest.raises(AuthenticationError):
            await chatbot.chat("Hello")
    
    def test_clear_history(self, chatbot):
        """测试清空历史"""
        chatbot.history.add_message("user", "Hello")
        chatbot.history.add_message("assistant", "Hi")
        
        assert chatbot.history.message_count == 2
        
        chatbot.clear_history()
        assert chatbot.history.message_count == 0
    
    def test_set_system_message(self, chatbot):
        """测试设置系统消息"""
        chatbot.set_system_message("You are a helpful assistant.")
        
        assert chatbot.history.message_count == 1
        messages = chatbot.history.get_messages_for_api()
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant."
    
    def test_set_empty_system_message_raises_error(self, chatbot):
        """测试设置空系统消息抛出错误"""
        with pytest.raises(ValidationError):
            chatbot.set_system_message("")
    
    def test_get_conversation_summary(self, chatbot):
        """测试获取对话摘要"""
        chatbot.history.add_message("user", "Hello")
        chatbot.history.add_message("assistant", "Hi there!")
        
        summary = chatbot.get_conversation_summary()
        
        assert summary["message_count"] == 2
        assert summary["model"] == chatbot.config.model
        assert summary["max_tokens"] == chatbot.config.max_tokens
        assert summary["temperature"] == chatbot.config.temperature
        assert len(summary["last_messages"]) <= 3


if __name__ == "__main__":
    pytest.main([__file__])