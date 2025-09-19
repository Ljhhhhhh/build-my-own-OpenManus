"""
配置管理模块

这个模块负责管理应用程序的基础配置，专注于核心概念：
1. 环境变量的基础管理
2. 简单的配置验证
3. 单例模式的基础实现
4. 类型注解的使用

学习要点：
1. 环境变量的读取和使用
2. 单例模式的Python实现
3. 类型注解的基础应用
4. 配置管理的基础模式

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
    
    public get(key: string, defaultValue?: any): any {
        return process.env[key] || defaultValue;
    }
    
    public isApiConfigured(): boolean {
        return !!this.openweatherApiKey;
    }
}

学习要点：
- 单例模式的Python实现
- 环境变量的读取和类型转换
- 配置验证的基础方法
- 类型安全的配置管理
"""

import os
from typing import Optional, Any
from dotenv import load_dotenv


class Config:
    """
    简化的应用配置类
    
    学习要点：
    - 单例模式的基础实现
    - 环境变量的管理
    - 类型注解的使用
    - 配置的基础验证
    
    💡 对比TypeScript:
    class Config {
        private static instance: Config;
        
        private constructor() {
            // 初始化配置
        }
        
        public static getInstance(): Config {
            if (!Config.instance) {
                Config.instance = new Config();
            }
            return Config.instance;
        }
        
        public get(key: string, defaultValue?: any): any {
            return process.env[key] || defaultValue;
        }
    }
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
        - 基础配置的设置
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
        
        # 日志配置
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # 应用配置
        self.app_name: str = os.getenv('APP_NAME', 'Practical3.2')
        self.debug_mode: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # 标记已初始化
        self._initialized = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        学习要点：
        - 通用配置获取方法
        - 默认值的处理
        - 类型注解的使用
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        return os.getenv(key, default)
    
    def is_api_configured(self) -> bool:
        """
        检查API是否已配置
        
        学习要点：
        - 配置验证的基础方法
        - 布尔返回值的使用
        - API密钥的验证
        
        Returns:
            bool: API是否已配置
        """
        return bool(self.openweather_api_key)
    
    def get_openweather_url(self, endpoint: str = 'weather') -> str:
        """
        获取OpenWeather API URL
        
        学习要点：
        - URL构建的基础方法
        - 字符串格式化
        - 默认参数的使用
        
        Args:
            endpoint: API端点
            
        Returns:
            str: 完整的API URL
        """
        base_url = "https://api.openweathermap.org/data/2.5"
        return f"{base_url}/{endpoint}"
    
    def print_config_summary(self):
        """
        打印配置摘要
        
        学习要点：
        - 配置信息的格式化输出
        - 敏感信息的隐藏处理
        - 调试信息的展示
        """
        print("📋 配置摘要")
        print("=" * 30)
        print(f"应用名称: {self.app_name}")
        print(f"调试模式: {self.debug_mode}")
        print(f"日志级别: {self.log_level}")
        print(f"请求超时: {self.request_timeout}秒")
        print(f"最大重试: {self.max_retries}次")
        
        # 隐藏敏感信息
        if self.openweather_api_key:
            masked_key = self.openweather_api_key[:8] + "..." + self.openweather_api_key[-4:]
            print(f"天气API密钥: {masked_key}")
        else:
            print("天气API密钥: 未配置")


# 全局配置实例
config = Config()


def get_config() -> Config:
    """
    获取全局配置实例
    
    学习要点：
    - 全局配置的获取方式
    - 单例模式的使用
    - 函数返回类型注解
    
    Returns:
        Config: 配置实例
    """
    return config


if __name__ == "__main__":
    """
    配置模块测试
    
    学习要点：
    - 模块测试的基础方法
    - 配置功能的验证
    - 调试输出的使用
    """
    print("🔧 测试配置模块")
    print("=" * 30)
    
    # 获取配置实例
    cfg = get_config()
    
    # 显示配置摘要
    cfg.print_config_summary()
    
    # 测试基础功能
    print(f"\nOpenWeather URL: {cfg.get_openweather_url()}")
    print(f"API已配置: {cfg.is_api_configured()}")
    print(f"自定义配置: {cfg.get('CUSTOM_KEY', 'default_value')}")
    
    print("\n✅ 配置模块测试完成！")