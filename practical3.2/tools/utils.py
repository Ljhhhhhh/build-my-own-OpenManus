"""
工具函数模块

提供基础的日志设置和时间格式化等通用工具函数。
移除了复杂的重试机制、性能监控等高级特性，专注于核心功能。

学习要点:
1. Python日志系统的基础配置
2. 时间格式化的实现
3. 配置验证的基础方法
4. 类型转换的安全处理

💡 对比TypeScript:
// TypeScript版本的工具函数
export class Utils {
    static setupLogging(level: string = 'INFO'): void {
        console.log(`Logging level set to: ${level}`);
    }
    
    static formatDuration(seconds: number): string {
        if (seconds < 1) {
            return `${Math.round(seconds * 1000)}ms`;
        } else if (seconds < 60) {
            return `${seconds.toFixed(2)}s`;
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${minutes}m ${remainingSeconds}s`;
        }
    }
    
    static validateConfig(config: object, requiredKeys: string[]): boolean {
        return requiredKeys.every(key => key in config);
    }
    
    static safeCast<T>(value: any, defaultValue: T): T {
        try {
            return value as T;
        } catch {
            return defaultValue;
        }
    }
}

学习要点：
- Python日志系统与JavaScript console的对比
- 时间格式化的不同实现方式
- 配置验证的基础模式
- 类型安全的处理方法
"""

import logging
import sys
from typing import Any, Union, Optional
from pathlib import Path


def setup_logging(
    level: Union[str, int] = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    设置基础日志配置
    
    学习要点：
    - Python日志系统的基础使用
    - 日志格式化字符串
    - 控制台和文件输出的配置
    - Logger实例的创建和配置
    
    Args:
        level: 日志级别（INFO, DEBUG, WARNING, ERROR）
        format_string: 自定义日志格式字符串
        log_file: 可选的日志文件路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
        
    Examples:
        >>> logger = setup_logging(logging.INFO)
        >>> logger.info("这是一条信息日志")
        
        >>> logger = setup_logging(logging.DEBUG, log_file="app.log")
        >>> logger.debug("这是一条调试日志")
    """
    # 设置默认日志格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建或获取logger实例
    logger = logging.getLogger('async_tools')
    logger.setLevel(level)
    
    # 避免重复添加handler（如果已经配置过）
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(format_string)
    
    # 添加控制台输出handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件输出handler
    if log_file:
        try:
            # 确保日志文件的目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件 {log_file}: {e}")
    
    return logger


def format_duration(seconds: float) -> str:
    """
    格式化时间持续时间为易读的字符串
    
    学习要点：
    - 数值的条件判断和格式化
    - 字符串格式化的不同方法
    - 时间单位的转换逻辑
    - f-string的使用
    
    Args:
        seconds: 时间长度（秒）
        
    Returns:
        str: 格式化后的时间字符串
        
    Examples:
        >>> format_duration(0.123)
        '123ms'
        >>> format_duration(1.5)
        '1.50s'
        >>> format_duration(65)
        '1m 5s'
        >>> format_duration(3661)
        '1h 1m'
    """
    if seconds < 0:
        return "0ms"
    
    # 小于1秒，显示毫秒
    if seconds < 1:
        milliseconds = int(seconds * 1000)
        return f"{milliseconds}ms"
    
    # 小于1分钟，显示秒
    elif seconds < 60:
        return f"{seconds:.2f}s"
    
    # 小于1小时，显示分钟和秒
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{minutes}m"
    
    # 1小时以上，显示小时和分钟
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if minutes > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{hours}h"


def validate_config(config: dict, required_keys: list) -> bool:
    """
    验证配置字典是否包含所有必需的键
    
    学习要点：
    - 字典键的存在性检查
    - 列表推导式的使用
    - all()函数的应用
    - 配置验证的基础模式
    
    Args:
        config: 要验证的配置字典
        required_keys: 必需的键列表
        
    Returns:
        bool: 如果所有必需键都存在则返回True，否则返回False
        
    Examples:
        >>> config = {"host": "localhost", "port": 8080, "debug": True}
        >>> validate_config(config, ["host", "port"])
        True
        >>> validate_config(config, ["host", "port", "database"])
        False
    """
    if not isinstance(config, dict):
        return False
    
    if not isinstance(required_keys, list):
        return False
    
    # 检查所有必需的键是否都存在
    return all(key in config for key in required_keys)


def safe_cast(value: Any, target_type: type, default: Any = None) -> Any:
    """
    安全地将值转换为指定类型
    
    学习要点：
    - 类型转换的异常处理
    - try-except的基础使用
    - 默认值的处理
    - 类型安全的编程实践
    
    Args:
        value: 要转换的值
        target_type: 目标类型（如int, float, str, bool）
        default: 转换失败时的默认值
        
    Returns:
        Any: 转换后的值，或默认值
        
    Examples:
        >>> safe_cast("123", int, 0)
        123
        >>> safe_cast("abc", int, 0)
        0
        >>> safe_cast("3.14", float, 0.0)
        3.14
        >>> safe_cast("true", bool, False)
        True
    """
    try:
        # 特殊处理布尔类型
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            else:
                return bool(value)
        
        # 其他类型的直接转换
        return target_type(value)
    
    except (ValueError, TypeError, AttributeError):
        return default


def create_cache_key(*args, **kwargs) -> str:
    """
    创建缓存键字符串
    
    学习要点：
    - 可变参数的处理
    - 字符串拼接和格式化
    - 哈希值的使用
    - 缓存键生成的基础模式
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        str: 生成的缓存键
        
    Examples:
        >>> create_cache_key("user", 123, action="login")
        'user_123_action:login'
        >>> create_cache_key("data", format="json")
        'data_format:json'
    """
    # 处理位置参数
    key_parts = [str(arg) for arg in args]
    
    # 处理关键字参数（按键排序以确保一致性）
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        kwargs_parts = [f"{k}:{v}" for k, v in sorted_kwargs]
        key_parts.extend(kwargs_parts)
    
    # 如果没有任何参数，返回默认键
    if not key_parts:
        return "default"
    
    # 拼接所有部分
    return "_".join(key_parts)


def get_file_size_str(file_path: str) -> str:
    """
    获取文件大小的易读字符串表示
    
    学习要点：
    - 文件系统操作
    - 数值的单位转换
    - Path对象的使用
    - 异常处理的实践
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件大小的字符串表示
        
    Examples:
        >>> get_file_size_str("small.txt")
        '1.2KB'
        >>> get_file_size_str("large.zip")
        '15.6MB'
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return "文件不存在"
        
        if not path.is_file():
            return "不是文件"
        
        size_bytes = path.stat().st_size
        
        # 转换为易读的单位
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f}MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"
    
    except Exception as e:
        return f"错误: {e}"


# 导出的公共接口
__all__ = [
    'setup_logging',
    'format_duration', 
    'validate_config',
    'safe_cast',
    'create_cache_key',
    'get_file_size_str'
]


# 测试代码
if __name__ == "__main__":
    def test_utils():
        """
        测试工具函数
        
        学习要点：
        - 单元测试的基础编写
        - 函数功能的验证
        - 边界情况的测试
        - 测试输出的格式化
        """
        print("🔧 测试工具函数模块")
        print("=" * 40)
        
        # 测试日志设置
        print("\n📝 测试日志设置:")
        logger = setup_logging(logging.INFO)
        logger.info("这是一条测试信息")
        logger.warning("这是一条测试警告")
        print("日志设置: 成功 ✅")
        
        # 测试时间格式化
        print("\n⏱️ 测试时间格式化:")
        test_times = [0.001, 0.123, 1.5, 65, 3661, 7322]
        for seconds in test_times:
            formatted = format_duration(seconds)
            print(f"  {seconds}s -> {formatted}")
        print("时间格式化: 成功 ✅")
        
        # 测试配置验证
        print("\n⚙️ 测试配置验证:")
        config = {"host": "localhost", "port": 8080, "debug": True}
        
        test_cases = [
            (["host", "port"], True),
            (["host", "port", "debug"], True),
            (["host", "database"], False),
            ([], True)
        ]
        
        for required_keys, expected in test_cases:
            result = validate_config(config, required_keys)
            status = "✅" if result == expected else "❌"
            print(f"  验证 {required_keys}: {result} {status}")
        
        print("配置验证: 成功 ✅")
        
        # 测试安全类型转换
        print("\n🔄 测试安全类型转换:")
        test_cases = [
            ("123", int, 0, 123),
            ("abc", int, 0, 0),
            ("3.14", float, 0.0, 3.14),
            ("invalid", float, 0.0, 0.0),
            ("true", bool, False, True),
            ("false", bool, True, False),
            ("hello", str, "", "hello")
        ]
        
        for value, target_type, default, expected in test_cases:
            result = safe_cast(value, target_type, default)
            status = "✅" if result == expected else "❌"
            print(f"  {value} -> {target_type.__name__}: {result} {status}")
        
        print("安全类型转换: 成功 ✅")
        
        # 测试缓存键生成
        print("\n🔑 测试缓存键生成:")
        test_cases = [
            (("user", 123), {"action": "login"}, "user_123_action:login"),
            (("data",), {"format": "json"}, "data_format:json"),
            ((), {}, "default"),
            (("simple",), {}, "simple")
        ]
        
        for args, kwargs, expected in test_cases:
            result = create_cache_key(*args, **kwargs)
            status = "✅" if result == expected else "❌"
            print(f"  {args}, {kwargs} -> {result} {status}")
        
        print("缓存键生成: 成功 ✅")
        
        # 测试文件大小格式化
        print("\n📁 测试文件大小格式化:")
        # 测试当前文件
        current_file = __file__
        size_str = get_file_size_str(current_file)
        print(f"  当前文件大小: {size_str}")
        
        # 测试不存在的文件
        nonexistent = "nonexistent_file.txt"
        size_str = get_file_size_str(nonexistent)
        print(f"  不存在文件: {size_str}")
        
        print("文件大小格式化: 成功 ✅")
        
        print("\n✅ 所有工具函数测试完成!")
    
    # 运行测试
    test_utils()