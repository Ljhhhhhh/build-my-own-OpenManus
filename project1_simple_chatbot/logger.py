"""
日志管理模块

提供统一的日志记录功能，支持彩色输出和不同级别的日志。
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# 初始化 colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
    }
    
    def format(self, record):
        # 获取颜色
        color = self.COLORS.get(record.levelname, '')
        
        # 格式化消息
        formatted = super().format(record)
        
        # 应用颜色
        if color:
            formatted = f"{color}{formatted}{Style.RESET_ALL}"
        
        return formatted


def setup_logger(
    name: str = "chatbot",
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        format_string: 自定义格式字符串
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(getattr(logging, level.upper()))
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # 设置格式
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = ColoredFormatter(format_string)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    return logger


# 创建默认日志记录器
logger = setup_logger()