"""
配置管理模块

提供统一的配置管理功能，支持环境变量和默认值。
对于JavaScript开发者：类似于dotenv + config对象的组合。
"""

import os
from typing import Any, Dict


class SandboxConfig:
    """沙箱配置管理类"""
    
    def __init__(self):
        """初始化配置，加载环境变量和默认值"""
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置
        
        类似JavaScript中的：
        const config = {
            timeout: process.env.SANDBOX_TIMEOUT || 30,
            memoryLimit: process.env.SANDBOX_MEMORY_LIMIT || 128
        }
        """
        return {
            # 基础沙箱配置
            'timeout': int(os.getenv('SANDBOX_TIMEOUT', 30)),
            'memory_limit': int(os.getenv('SANDBOX_MEMORY_LIMIT', 128)),
            
            # Docker配置
            'docker_memory_limit': os.getenv('DOCKER_MEMORY_LIMIT', '128m'),
            'docker_network_disabled': os.getenv('DOCKER_NETWORK_DISABLED', 'true').lower() == 'true',
            'docker_auto_remove': os.getenv('DOCKER_AUTO_REMOVE', 'true').lower() == 'true',
            
            # 日志配置
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', 'logs/sandbox.log'),
            
            # 安全配置
            'enable_code_validation': os.getenv('ENABLE_CODE_VALIDATION', 'true').lower() == 'true',
            'dangerous_keywords_file': os.getenv('DANGEROUS_KEYWORDS_FILE', 'config/dangerous_keywords.txt'),
            
            # 支持的语言
            'supported_languages': ['python', 'javascript'],
            
            # 语言扩展名映射
            'language_extensions': {
                'python': 'py',
                'javascript': 'js'
            },
            
            # 语言执行命令映射
            'language_commands': {
                'python': 'python',
                'javascript': 'node'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置
        
        Args:
            config_dict: 配置字典
        """
        self._config.update(config_dict)


# 全局配置实例
config = SandboxConfig()


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置的便捷函数"""
    return config.get(key, default)


def set_config(key: str, value: Any) -> None:
    """设置配置的便捷函数"""
    config.set(key, value)


if __name__ == "__main__":
    # 配置使用示例
    print("=== 沙箱配置示例 ===")
    print(f"超时时间: {get_config('timeout')}秒")
    print(f"内存限制: {get_config('memory_limit')}MB")
    print(f"支持的语言: {get_config('supported_languages')}")
    print(f"Docker内存限制: {get_config('docker_memory_limit')}")
    
    # 动态修改配置
    set_config('timeout', 60)
    print(f"修改后的超时时间: {get_config('timeout')}秒")