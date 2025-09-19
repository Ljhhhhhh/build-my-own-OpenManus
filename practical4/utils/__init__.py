"""
工具模块 - 项目4的辅助工具

这个包包含了项目中使用的辅助工具和实用函数：
- config: 配置管理
- logger: 日志工具

学习要点：
- 配置管理的最佳实践
- 日志系统的设计
- 环境变量的处理
"""

from .config import Config
from .logger import setup_logger

# 导出主要类和函数
__all__ = [
    'Config',
    'setup_logger'
]

# 版本信息
__version__ = '1.0.0'