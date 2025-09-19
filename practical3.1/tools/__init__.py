"""
基础工具包 - Practical3.1

这个包包含了基础工具系统的核心组件：
- BaseTool: 抽象基类
- ToolResult: 结果数据模型
- CalculatorTool: 示例工具实现

学习重点：
- Python包的组织结构
- 模块导入和导出
- 抽象基类的使用
"""

from .base import BaseTool, ToolResult, ToolResultStatus
from .calculator import CalculatorTool
from .manager import ToolManager

# 导出主要类，方便外部导入
__all__ = [
    'BaseTool',
    'ToolResult', 
    'ToolResultStatus',
    'CalculatorTool',
    'ToolManager'
]

# 版本信息
__version__ = '1.0.0'