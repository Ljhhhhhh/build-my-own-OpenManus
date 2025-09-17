"""
基础工具框架 - 工具包
提供可扩展的AI代理工具系统
"""

from .base import BaseTool, ToolResult, ToolResultStatus
from .manager import ToolManager
from .calculator import CalculatorTool
from .weather import WeatherTool


__all__ = [
    'BaseTool',
    'ToolResult', 
    'ToolResultStatus',
    'ToolManager',
    'CalculatorTool',
    'WeatherTool'
]

__version__ = '1.0.0'