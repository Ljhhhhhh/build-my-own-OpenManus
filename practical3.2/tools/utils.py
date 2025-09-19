"""
工具函数模块

提供日志设置、时间格式化、重试机制等通用工具函数。

学习要点:
1. 日志配置和管理
2. 异步重试机制
3. 时间格式化工具
4. 装饰器模式应用
5. 异常处理最佳实践

与前端开发对比:
- Python日志系统 vs JavaScript console
- 异步重试 vs Promise重试
- 装饰器 vs 高阶函数
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union
import sys
from pathlib import Path

# 类型变量
T = TypeVar('T')

def setup_logging(
    level: Union[str, int] = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        format_string: 日志格式字符串
        log_file: 日志文件路径
        
    Returns:
        配置好的logger实例
        
    学习要点:
    - Python日志系统配置
    - 日志格式化
    - 文件和控制台输出
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建logger
    logger = logging.getLogger('async_tools')
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建formatter
    formatter = logging.Formatter(format_string)
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件handler（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def format_duration(seconds: float) -> str:
    """
    格式化时间持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
        
    Examples:
        >>> format_duration(0.123)
        '123ms'
        >>> format_duration(1.5)
        '1.50s'
        >>> format_duration(65)
        '1m 5s'
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    异步重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
        
    Returns:
        装饰器函数
        
    学习要点:
    - 装饰器模式
    - 异步函数装饰
    - 指数退避算法
    - 异常处理策略
    
    与前端对比:
    JavaScript版本:
    ```javascript
    function retryAsync(maxRetries = 3, delay = 1000, backoffFactor = 2) {
        return function(target, propertyKey, descriptor) {
            const originalMethod = descriptor.value;
            descriptor.value = async function(...args) {
                let lastError;
                for (let i = 0; i <= maxRetries; i++) {
                    try {
                        return await originalMethod.apply(this, args);
                    } catch (error) {
                        lastError = error;
                        if (i < maxRetries) {
                            await new Promise(resolve => 
                                setTimeout(resolve, delay * Math.pow(backoffFactor, i))
                            );
                        }
                    }
                }
                throw lastError;
            };
        };
    }
    ```
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger = logging.getLogger('async_tools')
                        logger.warning(
                            f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}. "
                            f"将在 {current_delay:.2f}s 后重试..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger = logging.getLogger('async_tools')
                        logger.error(
                            f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败"
                        )
                        raise last_exception
            
            # 这行代码理论上不会执行到，但为了类型检查
            raise last_exception
        
        return wrapper
    return decorator

class PerformanceTimer:
    """
    性能计时器上下文管理器
    
    用于测量代码块的执行时间
    
    Examples:
        >>> async with PerformanceTimer() as timer:
        ...     await some_async_operation()
        >>> print(f"操作耗时: {timer.duration}")
    """
    
    def __init__(self, name: str = "操作"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.logger = logging.getLogger('async_tools')
    
    async def __aenter__(self):
        self.start_time = time.perf_counter()
        self.logger.debug(f"开始计时: {self.name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        
        if exc_type is None:
            self.logger.debug(
                f"完成计时: {self.name} - 耗时: {format_duration(self.duration)}"
            )
        else:
            self.logger.warning(
                f"计时中断: {self.name} - 耗时: {format_duration(self.duration)} "
                f"(由于异常: {exc_type.__name__})"
            )

def validate_config(config: dict, required_keys: list) -> bool:
    """
    验证配置字典是否包含必需的键
    
    Args:
        config: 配置字典
        required_keys: 必需的键列表
        
    Returns:
        是否验证通过
        
    Raises:
        ValueError: 当缺少必需配置时
    """
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        raise ValueError(f"缺少必需的配置项: {', '.join(missing_keys)}")
    
    return True

def safe_cast(value: Any, target_type: type, default: Any = None) -> Any:
    """
    安全类型转换
    
    Args:
        value: 要转换的值
        target_type: 目标类型
        default: 转换失败时的默认值
        
    Returns:
        转换后的值或默认值
    """
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default

def create_cache_key(*args, **kwargs) -> str:
    """
    创建缓存键
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        缓存键字符串
    """
    # 将参数转换为字符串并排序（确保一致性）
    key_parts = []
    
    # 处理位置参数
    for arg in args:
        key_parts.append(str(arg))
    
    # 处理关键字参数（按键排序）
    for key in sorted(kwargs.keys()):
        key_parts.append(f"{key}={kwargs[key]}")
    
    return "|".join(key_parts)

# 导出的工具函数
__all__ = [
    'setup_logging',
    'format_duration', 
    'retry_async',
    'PerformanceTimer',
    'validate_config',
    'safe_cast',
    'create_cache_key'
]

# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_utils():
        """测试工具函数"""
        print("🧪 测试工具函数...")
        
        # 测试日志设置
        logger = setup_logging(level=logging.INFO)
        logger.info("日志系统已设置")
        
        # 测试时间格式化
        print(f"时间格式化测试:")
        print(f"  0.123秒: {format_duration(0.123)}")
        print(f"  1.5秒: {format_duration(1.5)}")
        print(f"  65秒: {format_duration(65)}")
        print(f"  3665秒: {format_duration(3665)}")
        
        # 测试性能计时器
        async with PerformanceTimer("测试操作") as timer:
            await asyncio.sleep(0.1)
        print(f"计时器测试: {format_duration(timer.duration)}")
        
        # 测试重试装饰器
        @retry_async(max_retries=2, delay=0.1)
        async def failing_function():
            import random
            if random.random() < 0.7:  # 70%概率失败
                raise ValueError("随机失败")
            return "成功!"
        
        try:
            result = await failing_function()
            print(f"重试测试结果: {result}")
        except ValueError as e:
            print(f"重试测试最终失败: {e}")
        
        # 测试缓存键生成
        cache_key = create_cache_key("arg1", "arg2", key1="value1", key2="value2")
        print(f"缓存键测试: {cache_key}")
        
        print("✅ 工具函数测试完成!")
    
    # 运行测试
    asyncio.run(test_utils())