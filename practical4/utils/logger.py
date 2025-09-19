"""
日志工具模块 - 项目4的日志系统

这个模块提供了统一的日志配置和管理功能：
1. 标准化的日志格式
2. 不同级别的日志输出
3. 文件和控制台双重输出
4. 性能友好的日志配置

学习要点：
- Python logging模块的使用
- 日志格式化和处理器
- 日志级别的管理
- 生产环境的日志最佳实践
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str = "practical4",
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置并配置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        max_file_size: 单个日志文件最大大小（字节）
        backup_count: 保留的备份文件数量
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用RotatingFileHandler实现日志轮转
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 防止日志向上传播（避免重复输出）
    logger.propagate = False
    
    return logger


def get_logger(name: str = "practical4") -> logging.Logger:
    """
    获取已配置的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    日志记录器混入类
    
    为其他类提供便捷的日志记录功能。
    
    学习要点：
    - Mixin模式的应用
    - 类属性的延迟初始化
    - 面向对象的日志设计
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取类专用的日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(f"practical4.{self.__class__.__name__}")
        return self._logger


# 预定义的日志记录器
def setup_default_logger() -> logging.Logger:
    """
    设置默认的日志记录器
    
    Returns:
        logging.Logger: 默认日志记录器
    """
    return setup_logger(
        name="practical4",
        level="INFO",
        log_file="logs/practical4.log"
    )


# 日志装饰器
def log_function_call(logger: Optional[logging.Logger] = None):
    """
    装饰器：记录函数调用
    
    Args:
        logger: 日志记录器（可选）
        
    学习要点：
    - 装饰器的实现
    - 函数元信息的保留
    - 日志在调试中的应用
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or get_logger()
            func_name = f"{func.__module__}.{func.__name__}"
            
            func_logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                func_logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                func_logger.error(f"{func_name} failed with error: {e}")
                raise
                
        return wrapper
    return decorator


# 异步日志装饰器
def log_async_function_call(logger: Optional[logging.Logger] = None):
    """
    装饰器：记录异步函数调用
    
    Args:
        logger: 日志记录器（可选）
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            func_logger = logger or get_logger()
            func_name = f"{func.__module__}.{func.__name__}"
            
            func_logger.debug(f"Calling async {func_name} with args={args}, kwargs={kwargs}")
            
            try:
                result = await func(*args, **kwargs)
                func_logger.debug(f"Async {func_name} completed successfully")
                return result
            except Exception as e:
                func_logger.error(f"Async {func_name} failed with error: {e}")
                raise
                
        return wrapper
    return decorator


# 使用示例
if __name__ == "__main__":
    # 设置日志
    logger = setup_logger(
        name="test_logger",
        level="DEBUG",
        log_file="logs/test.log"
    )
    
    # 测试不同级别的日志
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    # 测试LoggerMixin
    class TestClass(LoggerMixin):
        def test_method(self):
            self.logger.info("测试LoggerMixin功能")
    
    test_obj = TestClass()
    test_obj.test_method()
    
    # 测试装饰器
    @log_function_call(logger)
    def test_function(x, y):
        return x + y
    
    result = test_function(1, 2)
    logger.info(f"函数结果: {result}")