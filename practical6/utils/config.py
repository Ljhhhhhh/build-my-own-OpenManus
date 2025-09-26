"""
配置管理模块

这个模块负责管理应用程序的配置，包括：
1. 环境变量的读取和验证
2. .env文件的支持
3. 配置的类型检查和验证

学习要点：
- 环境变量的最佳实践
- python-dotenv的使用
- 配置类的设计模式
- 类型注解和验证
- 单例模式的应用
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
import logging
from dotenv import load_dotenv, dotenv_values
@dataclass
class Config:
    """
    应用程序配置类
    
    使用dataclass装饰器简化配置类的定义，
    支持从环境变量、.env文件和默认值加载配置。
    
    学习要点：
    - @dataclass装饰器的使用
    - 类型注解的重要性
    - 配置验证的实现
    """
    
    # OpenAI API配置
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_base_url: Optional[str] = None
    openai_organization: Optional[str] = None
    
    # 应用程序配置
    log_level: str = "INFO"
    max_conversation_history: int = 50
    tool_timeout: int = 30
    
    # 性能配置
    max_concurrent_tools: int = 5
    request_timeout: int = 60
    
    # 高级功能配置
    enable_telemetry: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 3600
    
    # 安全配置
    allowed_hosts: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    rate_limit_per_minute: int = 60
    
    # 多模态功能配置
    # 图像处理配置
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    supported_image_formats: List[str] = field(default_factory=lambda: ["jpg", "jpeg", "png", "gif", "bmp", "webp"])
    image_quality: int = 85  # JPEG压缩质量
    max_image_width: int = 2048
    max_image_height: int = 2048
    
    # GPT-4V配置
    vision_model: str = "gpt-4-vision-preview"
    max_vision_tokens: int = 4096
    vision_detail: str = "auto"  # "low", "high", "auto"
    
    # 浏览器自动化配置
    browser_type: str = "chrome"  # "chrome", "firefox", "edge"
    browser_headless: bool = True
    browser_timeout: int = 30
    browser_window_width: int = 1920
    browser_window_height: int = 1080
    browser_user_agent: Optional[str] = None
    browser_download_dir: Optional[str] = None
    
    # WebDriver配置
    webdriver_auto_install: bool = True
    webdriver_path: Optional[str] = None
    webdriver_log_level: str = "WARNING"  # "DEBUG", "INFO", "WARNING", "ERROR"
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'Config':
        """
        从环境变量和.env文件创建配置实例
        
        配置优先级：
        1. 环境变量（最高优先级）
        2. .env文件
        3. 默认值（最低优先级）
        
        Args:
            env_file: .env文件路径，如果为None则使用根目录的.env文件
            
        Returns:
            Config: 配置实例
        """
        # 加载.env文件
        env_vars = cls._load_env_file(env_file)
        
        # 打印环境变量配置
        print("加载的环境变量配置:")
        print("-" * 50)
        for key, value in env_vars.items():
            # 对敏感信息进行脱敏处理
            if "key" in key.lower() or "secret" in key.lower() or "password" in key.lower():
                value = f"***{value[-4:]}" if value else "***"
            print(f"{key}: {value}")
        print("-" * 50)
        
        return cls(
            # OpenAI API配置
            openai_api_key=cls._get_env_value("OPENAI_API_KEY", env_vars, ""),
            openai_model=cls._get_env_value("OPENAI_MODEL", env_vars, "gpt-3.5-turbo"),
            openai_base_url=cls._get_env_value("OPENAI_BASE_URL", env_vars),
            openai_organization=cls._get_env_value("OPENAI_ORGANIZATION", env_vars),
            
            # 应用程序配置
            log_level=cls._get_env_value("LOG_LEVEL", env_vars, "INFO"),
            max_conversation_history=cls._get_int_value("MAX_CONVERSATION_HISTORY", env_vars, 50),
            tool_timeout=cls._get_int_value("TOOL_TIMEOUT", env_vars, 30),
            
            # 性能配置
            max_concurrent_tools=cls._get_int_value("MAX_CONCURRENT_TOOLS", env_vars, 5),
            request_timeout=cls._get_int_value("REQUEST_TIMEOUT", env_vars, 60),
            
            # 高级配置
            enable_telemetry=cls._get_bool_value("ENABLE_TELEMETRY", env_vars, False),
            cache_enabled=cls._get_bool_value("CACHE_ENABLED", env_vars, True),
            cache_ttl=cls._get_int_value("CACHE_TTL", env_vars, 3600),
            
            # 安全配置
            allowed_hosts=cls._get_list_value("ALLOWED_HOSTS", env_vars, ["localhost", "127.0.0.1"]),
            rate_limit_per_minute=cls._get_int_value("RATE_LIMIT_PER_MINUTE", env_vars, 60),
            
            # 多模态功能配置
            # 图像处理配置
            max_image_size=cls._get_int_value("MAX_IMAGE_SIZE", env_vars, 10 * 1024 * 1024),
            supported_image_formats=cls._get_list_value("SUPPORTED_IMAGE_FORMATS", env_vars, ["jpg", "jpeg", "png", "gif", "bmp", "webp"]),
            image_quality=cls._get_int_value("IMAGE_QUALITY", env_vars, 85),
            max_image_width=cls._get_int_value("MAX_IMAGE_WIDTH", env_vars, 2048),
            max_image_height=cls._get_int_value("MAX_IMAGE_HEIGHT", env_vars, 2048),
            
            # GPT-4V配置
            vision_model=cls._get_env_value("VISION_MODEL", env_vars, "gpt-4-vision-preview"),
            max_vision_tokens=cls._get_int_value("MAX_VISION_TOKENS", env_vars, 4096),
            vision_detail=cls._get_env_value("VISION_DETAIL", env_vars, "auto"),
            
            # 浏览器自动化配置
            browser_type=cls._get_env_value("BROWSER_TYPE", env_vars, "chrome"),
            browser_headless=cls._get_bool_value("BROWSER_HEADLESS", env_vars, True),
            browser_timeout=cls._get_int_value("BROWSER_TIMEOUT", env_vars, 30),
            browser_window_width=cls._get_int_value("BROWSER_WINDOW_WIDTH", env_vars, 1920),
            browser_window_height=cls._get_int_value("BROWSER_WINDOW_HEIGHT", env_vars, 1080),
            browser_user_agent=cls._get_env_value("BROWSER_USER_AGENT", env_vars),
            browser_download_dir=cls._get_env_value("BROWSER_DOWNLOAD_DIR", env_vars),
            
            # WebDriver配置
            webdriver_auto_install=cls._get_bool_value("WEBDRIVER_AUTO_INSTALL", env_vars, True),
            webdriver_path=cls._get_env_value("WEBDRIVER_PATH", env_vars),
            webdriver_log_level=cls._get_env_value("WEBDRIVER_LOG_LEVEL", env_vars, "WARNING")
        )
    
    @staticmethod
    def _load_env_file(env_file: Optional[str] = None) -> Dict[str, str]:
        """
        加载.env文件
        
        Args:
            env_file: 指定的.env文件路径，如果为None则使用根目录的.env文件
            
        Returns:
            Dict[str, str]: 环境变量字典
        """
        env_vars = {}
        
        # 确定要加载的.env文件路径
        if env_file:
            env_file_path = Path(env_file)
        else:
            # 默认使用根目录的.env文件
            env_file_path = Path.cwd() / ".env"
        
        # 加载.env文件
        if env_file_path.exists():
            try:
                env_vars = dotenv_values(str(env_file_path))
                logging.info(f"Loaded environment variables from {env_file_path}")
            except Exception as e:
                logging.warning(f"Failed to load {env_file_path}: {e}")
        else:
            logging.info(f"No .env file found at {env_file_path}")
        
        return env_vars
    
    @staticmethod
    def _get_env_value(key: str, env_vars: Dict[str, str], default: Optional[str] = None) -> Optional[str]:
        """获取环境变量值，优先级：环境变量 > .env文件 > 默认值"""
        return os.getenv(key) or env_vars.get(key) or default
    
    @staticmethod
    def _get_int_value(key: str, env_vars: Dict[str, str], default: int) -> int:
        """获取整数类型的环境变量值"""
        value = Config._get_env_value(key, env_vars)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logging.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    @staticmethod
    def _get_bool_value(key: str, env_vars: Dict[str, str], default: bool) -> bool:
        """获取布尔类型的环境变量值"""
        value = Config._get_env_value(key, env_vars)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    @staticmethod
    def _get_list_value(key: str, env_vars: Dict[str, str], default: List[str]) -> List[str]:
        """获取列表类型的环境变量值（逗号分隔）"""
        value = Config._get_env_value(key, env_vars)
        if value is None:
            return default
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def validate(self) -> None:
        """
        验证配置的有效性
        
        Raises:
            ValueError: 当配置无效时
        """
        # 验证数值配置
        if self.max_conversation_history <= 0:
            raise ValueError("Max conversation history must be positive")
        
        if self.tool_timeout <= 0:
            raise ValueError("Tool timeout must be positive")
        
        if self.max_concurrent_tools <= 0:
            raise ValueError("Max concurrent tools must be positive")
        
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
        
        if self.cache_ttl <= 0:
            raise ValueError("Cache TTL must be positive")
        
        if self.rate_limit_per_minute <= 0:
            raise ValueError("Rate limit per minute must be positive")
        
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {valid_log_levels}")
        
        # 验证主机列表
        if not self.allowed_hosts:
            raise ValueError("Allowed hosts cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典
        
        Returns:
            Dict[str, Any]: 配置字典（隐藏敏感信息）
        """
        config_dict = {
            "openai_model": self.openai_model,
            "openai_base_url": self.openai_base_url,
            "openai_organization": self.openai_organization,
            "log_level": self.log_level,
            "max_conversation_history": self.max_conversation_history,
            "tool_timeout": self.tool_timeout,
            "max_concurrent_tools": self.max_concurrent_tools,
            "request_timeout": self.request_timeout,
            "enable_telemetry": self.enable_telemetry,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "allowed_hosts": self.allowed_hosts,
            "rate_limit_per_minute": self.rate_limit_per_minute
        }
        
        # 隐藏API密钥
        if self.openai_api_key:
            config_dict["openai_api_key"] = f"sk-...{self.openai_api_key[-4:]}"
        else:
            config_dict["openai_api_key"] = "Not set"
        
        return config_dict


# 全局配置实例（单例模式）
_config_instance: Optional[Config] = None


def get_config(env_file: Optional[str] = None, force_reload: bool = False) -> Config:
    """
    获取全局配置实例（单例模式）
    
    Args:
        env_file: .env文件路径
        force_reload: 是否强制重新加载配置
    
    Returns:
        Config: 配置实例
    """
    global _config_instance
    
    if _config_instance is None or force_reload:
        _config_instance = Config.from_env(env_file)
        _config_instance.validate()
    
    return _config_instance


def reset_config() -> None:
    """重置配置实例（主要用于测试）"""
    global _config_instance
    _config_instance = None


def create_sample_env_file(file_path: str = ".env.example") -> None:
    """
    创建示例.env文件
    
    Args:
        file_path: 文件路径
    """
    sample_content = """# OpenManus 配置示例文件
# 复制此文件为 .env 并填入实际值

# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_ORGANIZATION=your_org_id

# 应用程序配置
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=50
TOOL_TIMEOUT=30

# 性能配置
MAX_CONCURRENT_TOOLS=5
REQUEST_TIMEOUT=60

# 高级配置
ENABLE_TELEMETRY=false
CACHE_ENABLED=true
CACHE_TTL=3600

# 安全配置
ALLOWED_HOSTS=localhost,127.0.0.1
RATE_LIMIT_PER_MINUTE=60
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"示例配置文件已创建: {file_path}")


# 使用示例和测试
if __name__ == "__main__":
    try:
        # 创建示例配置文件
        create_sample_env_file()
        
        # 测试配置加载
        config = get_config()
        print("配置加载成功:")
        print("=" * 50)
        
        # 显示配置信息
        config_dict = config.to_dict()
        for key, value in config_dict.items():
            print(f"{key}: {value}")
        
        print("=" * 50)
        
        # 测试配置验证
        print("\n配置验证通过 ✓")
        
    except ValueError as e:
        print(f"配置错误: {e}")
        print("\n请检查以下事项:")
        print("1. 确保设置了必需的环境变量")
        print("2. 运行以下命令安装 python-dotenv:")
        print("   pip install python-dotenv")
        print("3. 创建 .env 文件并填入配置值")
    except Exception as e:
        print(f"未知错误: {e}")