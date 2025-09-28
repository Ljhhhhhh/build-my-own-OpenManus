"""
配置管理模块

这个模块负责管理应用程序的配置，包括环境变量加载、配置验证等。

对于JavaScript开发者的说明：
- 这里使用了Python的os.environ来访问环境变量，类似于Node.js中的process.env
- dataclass用于定义配置结构，类似于TypeScript的interface
- python-dotenv库用于加载.env文件，类似于Node.js的dotenv包
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class MCPConfig:
    """
    MCP服务器配置类
    
    对应JavaScript中的:
    interface MCPConfig {
        openai_api_key: string;
        log_level: string;
        log_file: string;
        server_timeout: number;
        max_concurrent_requests: number;
        debug: boolean;
    }
    """
    # OpenAI API配置
    openai_api_key: str
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/mcp_server.log"
    
    # 服务器配置
    server_timeout: int = 30
    max_concurrent_requests: int = 10
    
    # 开发配置
    debug: bool = False
    
    def validate(self) -> None:
        """
        验证配置的有效性
        
        类似于JavaScript中的:
        validate(): void {
            if (!this.openai_api_key) {
                throw new Error("OpenAI API key is required");
            }
            // ... 其他验证逻辑
        }
        """
        # 对于演示项目，我们不强制要求真实的API key
        if not self.openai_api_key or self.openai_api_key == "":
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        
        if self.server_timeout <= 0:
            raise ValueError("Server timeout must be positive")
        
        if self.max_concurrent_requests <= 0:
            raise ValueError("Max concurrent requests must be positive")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")


def load_config(env_file: Optional[str] = None) -> MCPConfig:
    """
    加载配置
    
    这个函数从环境变量和.env文件中加载配置
    
    Args:
        env_file: .env文件路径，如果为None则使用默认路径
    
    Returns:
        MCPConfig: 配置对象
    
    对应JavaScript中的:
    function loadConfig(envFile?: string): MCPConfig {
        // 加载.env文件
        require('dotenv').config({ path: envFile });
        
        return {
            openai_api_key: process.env.OPENAI_API_KEY || '',
            log_level: process.env.LOG_LEVEL || 'INFO',
            // ... 其他配置
        };
    }
    """
    # 加载.env文件
    if env_file:
        load_dotenv(env_file)
    else:
        # 尝试加载当前目录下的.env文件
        load_dotenv()
    
    # 从环境变量创建配置对象
    config = MCPConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", "demo-key-not-required"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "logs/mcp_server.log"),
        server_timeout=int(os.getenv("MCP_SERVER_TIMEOUT", "30")),
        max_concurrent_requests=int(os.getenv("MCP_MAX_CONCURRENT_REQUESTS", "10")),
        debug=os.getenv("DEBUG", "False").lower() in ("true", "1", "yes", "on")
    )
    
    # 验证配置
    config.validate()
    
    return config


def get_default_config() -> MCPConfig:
    """
    获取默认配置
    
    用于测试或开发环境，提供合理的默认值
    
    类似于JavaScript中的:
    function getDefaultConfig(): MCPConfig {
        return {
            openai_api_key: 'test-key',
            log_level: 'DEBUG',
            // ... 其他默认值
        };
    }
    """
    return MCPConfig(
        openai_api_key="test-key-for-development",
        log_level="DEBUG",
        log_file="logs/mcp_server_dev.log",
        server_timeout=30,
        max_concurrent_requests=5,
        debug=True
    )


# 全局配置实例
# 这是一个单例模式的实现，确保整个应用程序使用同一个配置
_config_instance: Optional[MCPConfig] = None


def get_config() -> MCPConfig:
    """
    获取全局配置实例
    
    这是一个单例模式的实现，类似于JavaScript中的:
    
    let configInstance: MCPConfig | null = null;
    
    function getConfig(): MCPConfig {
        if (!configInstance) {
            configInstance = loadConfig();
        }
        return configInstance;
    }
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance


def set_config(config: MCPConfig) -> None:
    """
    设置全局配置实例
    
    主要用于测试环境，允许注入自定义配置
    """
    global _config_instance
    _config_instance = config


def reset_config() -> None:
    """
    重置全局配置实例
    
    主要用于测试环境，清理配置状态
    """
    global _config_instance
    _config_instance = None


# 导出主要的类和函数
__all__ = [
    "MCPConfig",
    "load_config", 
    "get_default_config",
    "get_config",
    "set_config",
    "reset_config"
]