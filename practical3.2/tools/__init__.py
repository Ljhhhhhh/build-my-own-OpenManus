"""
Practical 3.2 工具包 - 高级工具集成系统

这个包包含了异步工具框架的实现，专注于高级Python特性和实际应用场景。

主要模块：
- base: 异步工具基类和数据模型
- manager: 异步工具管理器
- calculator: 异步计算器工具
- weather: 天气查询工具
- utils: 工具函数和辅助类

学习要点：
1. 异步编程模式
2. 外部API集成
3. 并发处理和性能优化
4. 错误处理和重试机制
5. 配置管理和环境变量

💡 对比TypeScript:
// 包的导出和模块管理
export { AsyncBaseTool, ToolResult, ToolResultStatus } from './base';
export { AsyncToolManager } from './manager';
export { AsyncCalculatorTool } from './calculator';
export { WeatherTool } from './weather';
export * as utils from './utils';

// 版本和元信息
export const VERSION = '1.0.0';
export const DESCRIPTION = '高级工具集成系统';
"""

# 导入核心类和函数
from .base import AsyncBaseTool, ToolResult, ToolResultStatus
from .manager import AsyncToolManager
from .calculator import AsyncCalculatorTool
from .weather import AsyncWeatherTool
from .utils import setup_logging, format_duration, retry_async

# 包信息
__version__ = "1.0.0"
__description__ = "高级工具集成系统 - 异步工具框架"
__author__ = "Practical Learning Project"

# 导出的主要类和函数
__all__ = [
    # 核心基类
    'AsyncBaseTool',
    'ToolResult', 
    'ToolResultStatus',
    
    # 管理器
    'AsyncToolManager',
    
    # 具体工具
    'AsyncCalculatorTool',
    'AsyncWeatherTool',
    
    # 工具函数
    'setup_logging',
    'format_duration',
    'retry_async',
    
    # 包信息
    '__version__',
    '__description__',
    '__author__'
]

# 包级别的初始化
print(f"🔧 {__description__} v{__version__} 已加载")
print("   支持异步工具执行、外部API集成和并发处理")