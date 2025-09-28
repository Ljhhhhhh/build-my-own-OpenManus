"""
日志工具模块

提供统一的日志记录功能，支持文件和控制台输出。
对于JavaScript开发者：类似于winston或pino日志库的功能。
"""

import logging
import os
from datetime import datetime
from typing import Optional


class SandboxLogger:
    """沙箱日志记录器"""
    
    def __init__(self, name: str = "sandbox", log_file: Optional[str] = None, level: str = "INFO"):
        """初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """设置日志处理器"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """记录一般信息"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误信息"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, **kwargs)
    
    def log_execution(self, stage: str, code: str, result: dict):
        """记录代码执行信息
        
        Args:
            stage: 执行阶段（stage1/stage2/stage3）
            code: 执行的代码
            result: 执行结果
        """
        success_status = "成功" if result.get('success') else "失败"
        execution_time = result.get('execution_time', 0)
        
        self.info(f"[{stage}] 代码执行{success_status} - 耗时: {execution_time:.3f}秒")
        
        if result.get('success'):
            self.debug(f"[{stage}] 输出: {result.get('output', '')[:100]}...")
        else:
            self.error(f"[{stage}] 错误: {result.get('error', '')}")
    
    def log_security_check(self, code: str, is_safe: bool, reason: str = ""):
        """记录安全检查信息
        
        Args:
            code: 检查的代码
            is_safe: 是否安全
            reason: 不安全的原因
        """
        status = "通过" if is_safe else "拒绝"
        code_preview = code[:50].replace('\n', ' ') + "..." if len(code) > 50 else code
        
        if is_safe:
            self.info(f"安全检查{status}: {code_preview}")
        else:
            self.warning(f"安全检查{status}: {code_preview} - 原因: {reason}")
    
    def log_docker_operation(self, operation: str, container_id: str = "", status: str = ""):
        """记录Docker操作信息
        
        Args:
            operation: 操作类型
            container_id: 容器ID
            status: 操作状态
        """
        if container_id:
            self.info(f"Docker操作: {operation} - 容器: {container_id[:12]} - 状态: {status}")
        else:
            self.info(f"Docker操作: {operation} - 状态: {status}")


# 创建默认日志记录器实例
def get_logger(name: str = "sandbox", log_file: Optional[str] = None, level: str = "INFO") -> SandboxLogger:
    """获取日志记录器实例
    
    类似JavaScript中的：
    const logger = require('./logger')('sandbox');
    """
    return SandboxLogger(name, log_file, level)


# 全局默认日志记录器
default_logger = get_logger()


# 便捷函数
def log_info(message: str, **kwargs):
    """记录信息的便捷函数"""
    default_logger.info(message, **kwargs)


def log_error(message: str, **kwargs):
    """记录错误的便捷函数"""
    default_logger.error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """记录警告的便捷函数"""
    default_logger.warning(message, **kwargs)


if __name__ == "__main__":
    # 日志使用示例
    print("=== 日志工具示例 ===")
    
    # 创建日志记录器
    logger = get_logger("test", "logs/test.log", "DEBUG")
    
    # 记录不同级别的日志
    logger.debug("这是调试信息")
    logger.info("这是一般信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    # 记录执行结果
    test_result = {
        'success': True,
        'output': 'Hello World!',
        'execution_time': 0.123
    }
    logger.log_execution("stage1", "print('Hello World!')", test_result)
    
    # 记录安全检查
    logger.log_security_check("print('safe code')", True)
    logger.log_security_check("import os; os.system('rm -rf /')", False, "包含危险操作")
    
    # 记录Docker操作
    logger.log_docker_operation("容器启动", "abc123def456", "成功")