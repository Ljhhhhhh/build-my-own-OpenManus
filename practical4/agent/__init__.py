"""
代理模块 - 项目4的智能代理系统

这个包包含了工具调用代理的核心组件：
- ToolCallingAgent: 主要的工具调用代理类

学习要点：
- LLM与工具系统的集成
- 智能代理的设计模式
- 异步编程在AI应用中的应用
"""

from .tool_calling_agent import ToolCallingAgent

# 导出主要类
__all__ = [
    'ToolCallingAgent'
]

# 版本信息
__version__ = '1.0.0'