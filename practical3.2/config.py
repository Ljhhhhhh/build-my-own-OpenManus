"""
配置管理模块

这个模块负责管理应用程序的配置，包括环境变量的加载、验证和默认值设置。

学习要点：
1. 环境变量的管理
2. 配置验证和默认值
3. 类型注解的使用
4. 单例模式的实现
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    应用配置类
    
    💡 对比TypeScript:
    class Config {
        private static instance: Config;
        
        public readonly openweatherApiKey: string;
        public readonly requestTimeout: number;
        public readonly maxRetries: number;
        
        private constructor() {
            // 加载环境变量
            this.openweatherApiKey = process.env.OPENWEATHER_API_KEY || '';
            this.requestTimeout = parseInt(process.env.REQUEST_TIMEOUT || '10');
            this.maxRetries = parseInt(process.env.MAX_RETRIES || '3');
        }
        
        public static getInstance(): Config {
            if (!Config.instance) {
                Config.instance = new Config();
            }
            return Config.instance;
        }
    }
    
    学习要点：
    - 单例模式的Python实现
    - 环境变量的读取和类型转换
    - 配置验证和错误处理
    """
    
    _instance: Optional['Config'] = None
    
    def __new__(cls) -> 'Config':
        """
        单例模式实现
        
        学习要点：
        - __new__ 方法的使用
        - 单例模式的实现方式
        - 类属性的管理
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化配置
        
        学习要点：
        - 避免重复初始化
        - 环境变量的加载
        - 配置验证
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        # 加载.env文件
        load_dotenv()
        
        # API配置
        self.openweather_api_key: str = os.getenv('OPENWEATHER_API_KEY', '')
        
        # 请求配置
        self.request_timeout: int = int(os.getenv('REQUEST_TIMEOUT', '10'))
        self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay: float = float(os.getenv('RETRY_DELAY', '1.0'))
        
        # 日志配置
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_format: str = os.getenv('LOG_FORMAT', 'colored').lower()
        
        # 应用配置
        self.app_name: str = os.getenv('APP_NAME', 'Practical3.2')
        self.debug_mode: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # 标记已初始化
        self._initialized = True
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """
        验证配置的有效性
        
        学习要点：
        - 配置验证的重要性
        - 错误处理和用户友好的提示
        - 条件判断和异常抛出
        """
        errors = []
        
        # 验证API密钥
        if not self.openweather_api_key:
            errors.append("OPENWEATHER_API_KEY 未设置。请在.env文件中配置API密钥。")
        
        # 验证数值配置
        if self.request_timeout <= 0:
            errors.append("REQUEST_TIMEOUT 必须大于0")
        
        if self.max_retries < 0:
            errors.append("MAX_RETRIES 必须大于等于0")
        
        if self.retry_delay < 0:
            errors.append("RETRY_DELAY 必须大于等于0")
        
        # 验证日志级别
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if self.log_level not in valid_log_levels:
            errors.append(f"LOG_LEVEL 必须是以下之一: {', '.join(valid_log_levels)}")
        
        # 如果有错误，显示警告但不中断程序
        if errors:
            print("⚠️  配置警告:")
            for error in errors:
                print(f"   - {error}")
            print("   程序将使用默认值继续运行，但某些功能可能不可用。")
    
    def get_openweather_url(self, endpoint: str = 'weather') -> str:
        """
        获取OpenWeather API的完整URL
        
        学习要点：
        - 字符串格式化
        - 方法的参数默认值
        - URL构建的最佳实践
        
        Args:
            endpoint: API端点名称
            
        Returns:
            str: 完整的API URL
        """
        base_url = "https://api.openweathermap.org/data/2.5"
        return f"{base_url}/{endpoint}"
    
    def get_request_headers(self) -> dict:
        """
        获取HTTP请求头
        
        学习要点：
        - 字典的构建和返回
        - HTTP请求头的标准设置
        
        Returns:
            dict: 请求头字典
        """
        return {
            'User-Agent': f'{self.app_name}/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def is_api_configured(self) -> bool:
        """
        检查API是否已正确配置
        
        学习要点：
        - 布尔方法的命名约定
        - 配置状态的检查
        
        Returns:
            bool: API是否已配置
        """
        return bool(self.openweather_api_key and self.openweather_api_key != 'your_openweather_api_key_here')
    
    def get(self, key: str, default=None):
        """
        获取配置值的通用方法
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        # 将键名转换为属性名
        attr_map = {
            'OPENWEATHER_API_KEY': 'openweather_api_key',
            'REQUEST_TIMEOUT': 'request_timeout',
            'MAX_RETRIES': 'max_retries',
            'RETRY_DELAY': 'retry_delay',
            'LOG_LEVEL': 'log_level',
            'LOG_FORMAT': 'log_format',
            'APP_NAME': 'app_name',
            'DEBUG_MODE': 'debug_mode'
        }
        
        attr_name = attr_map.get(key, key.lower())
        return getattr(self, attr_name, default)
    
    def print_config_summary(self):
        """
        打印配置摘要
        
        学习要点：
        - 信息的格式化输出
        - 敏感信息的隐藏处理
        - 配置状态的展示
        """
        print("\n" + "=" * 50)
        print("⚙️  配置信息")
        print("=" * 50)
        
        # 基本信息
        print(f"应用名称: {self.app_name}")
        print(f"调试模式: {'开启' if self.debug_mode else '关闭'}")
        print(f"日志级别: {self.log_level}")
        print(f"日志格式: {self.log_format}")
        
        # API配置
        api_status = "✅ 已配置" if self.is_api_configured() else "❌ 未配置"
        api_key_display = f"{self.openweather_api_key[:8]}..." if self.is_api_configured() else "未设置"
        print(f"OpenWeather API: {api_status}")
        print(f"API密钥: {api_key_display}")
        
        # 请求配置
        print(f"请求超时: {self.request_timeout}秒")
        print(f"最大重试: {self.max_retries}次")
        print(f"重试延迟: {self.retry_delay}秒")
        
        print("=" * 50)


# 全局配置实例
config = Config()


# 便捷函数
def get_config() -> Config:
    """
    获取配置实例
    
    学习要点：
    - 全局变量的使用
    - 便捷函数的设计
    
    Returns:
        Config: 配置实例
    """
    return config


# 测试代码
if __name__ == "__main__":
    """
    测试配置模块
    
    学习要点：
    - 模块的独立测试
    - 配置的验证和展示
    """
    print("🔧 测试配置模块")
    
    # 获取配置实例
    cfg = get_config()
    
    # 显示配置摘要
    cfg.print_config_summary()
    
    # 测试配置方法
    print(f"\nOpenWeather URL: {cfg.get_openweather_url()}")
    print(f"API已配置: {cfg.is_api_configured()}")
    print(f"请求头: {cfg.get_request_headers()}")
    
    print("\n✅ 配置模块测试完成！")