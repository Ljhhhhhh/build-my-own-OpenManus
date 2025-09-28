"""
日志管理模块

这个模块提供了统一的日志管理功能，支持文件日志和控制台日志。

对于JavaScript开发者的说明：
- Python的logging模块类似于Node.js的winston或console
- 这里使用了结构化日志，类似于JSON格式的日志输出
- 日志级别：DEBUG < INFO < WARNING < ERROR < CRITICAL
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """
    JSON格式的日志格式化器
    
    将日志输出为JSON格式，便于日志分析和处理
    
    类似于JavaScript中的:
    class JSONFormatter {
        format(record) {
            return JSON.stringify({
                timestamp: new Date().toISOString(),
                level: record.level,
                message: record.message,
                // ... 其他字段
            });
        }
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为JSON字符串
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: JSON格式的日志字符串
        """
        # 创建日志数据字典
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 如果有异常信息，添加到日志中
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 如果有额外的字段，添加到日志中
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


class MCPLogger:
    """
    MCP项目的日志管理器
    
    提供统一的日志接口，支持文件和控制台输出
    """
    
    def __init__(self, name: str, log_file: Optional[str] = None, log_level: str = "INFO"):
        """
        初始化日志管理器
        
        Args:
            name: 日志器名称
            log_file: 日志文件路径
            log_level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 清除已有的处理器，避免重复日志
        self.logger.handlers.clear()
        
        # 设置控制台处理器
        self._setup_console_handler()
        
        # 设置文件处理器
        if log_file:
            self._setup_file_handler(log_file)
    
    def _setup_console_handler(self) -> None:
        """
        设置控制台日志处理器
        
        类似于JavaScript中的:
        setupConsoleHandler() {
            const consoleHandler = new ConsoleHandler();
            consoleHandler.setFormatter(new SimpleFormatter());
            this.logger.addHandler(consoleHandler);
        }
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self, log_file: str) -> None:
        """
        设置文件日志处理器
        
        Args:
            log_file: 日志文件路径
        """
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """
        记录DEBUG级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志数据
        """
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        记录INFO级别日志
        
        类似于JavaScript中的:
        info(message: string, extraData?: object): void {
            this.logger.info(message, extraData);
        }
        """
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录WARNING级别日志"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """记录ERROR级别日志"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """记录CRITICAL级别日志"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """
        内部日志记录方法
        
        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外的日志数据
        """
        # 创建日志记录，并添加额外数据
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        
        if kwargs:
            record.extra_data = kwargs
        
        self.logger.handle(record)


# 全局日志管理器实例
_logger_instances = {}


def get_logger(name: str, log_file: Optional[str] = None, log_level: str = "INFO") -> MCPLogger:
    """
    获取日志管理器实例
    
    这是一个工厂函数，确保相同名称的日志器只创建一次
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径
        log_level: 日志级别
    
    Returns:
        MCPLogger: 日志管理器实例
    
    类似于JavaScript中的:
    const loggerInstances = new Map();
    
    function getLogger(name: string, logFile?: string, logLevel: string = "INFO"): MCPLogger {
        if (!loggerInstances.has(name)) {
            loggerInstances.set(name, new MCPLogger(name, logFile, logLevel));
        }
        return loggerInstances.get(name);
    }
    """
    if name not in _logger_instances:
        _logger_instances[name] = MCPLogger(name, log_file, log_level)
    return _logger_instances[name]


def setup_logging(log_file: Optional[str] = None, log_level: str = "INFO") -> MCPLogger:
    """
    设置应用程序的主日志器
    
    这是一个便利函数，用于快速设置应用程序的日志系统
    
    Args:
        log_file: 日志文件路径
        log_level: 日志级别
    
    Returns:
        MCPLogger: 主日志管理器
    """
    return get_logger("mcp", log_file, log_level)


def log_function_call(func_name: str, args: dict = None, result: any = None) -> None:
    """
    记录函数调用日志
    
    这是一个便利函数，用于记录函数的调用和结果
    
    Args:
        func_name: 函数名称
        args: 函数参数
        result: 函数结果
    
    类似于JavaScript中的:
    function logFunctionCall(funcName: string, args?: object, result?: any): void {
        const logger = getLogger("function_calls");
        logger.info(`Function called: ${funcName}`, { args, result });
    }
    """
    logger = get_logger("function_calls")
    log_data = {"function": func_name}
    
    if args:
        log_data["arguments"] = args
    if result is not None:
        log_data["result"] = str(result)  # 转换为字符串避免序列化问题
    
    logger.info(f"Function called: {func_name}", **log_data)


def log_error_with_context(error: Exception, context: dict = None) -> None:
    """
    记录带上下文的错误日志
    
    Args:
        error: 异常对象
        context: 错误上下文信息
    """
    logger = get_logger("errors")
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    if context:
        log_data.update(context)
    
    logger.error(f"Error occurred: {error}", **log_data)


# 导出主要的类和函数
__all__ = [
    "MCPLogger",
    "JSONFormatter",
    "get_logger",
    "setup_logging",
    "log_function_call",
    "log_error_with_context"
]