"""
项目4工具包 - 工具调用代理的工具系统

这个包包含了工具调用代理所需的所有工具组件：
- BaseTool: 抽象基类
- ToolResult: 结果数据模型
- ToolManager: 工具管理器
- CalculatorTool: 计算器工具
- TextProcessorTool: 文本处理工具

学习重点：
- LLM与工具系统的集成
- 智能工具选择和调用
- 异步工具执行
"""

from .base import BaseTool, ToolResult, ToolResultStatus
from .manager import ToolManager
from .calculator import CalculatorTool
from .text_processor import TextProcessorTool

# 导出主要类，方便外部导入
__all__ = [
    'BaseTool',
    'ToolResult', 
    'ToolResultStatus',
    'ToolManager',
    'CalculatorTool',
    'TextProcessorTool'
]

# 版本信息
__version__ = '1.0.0'