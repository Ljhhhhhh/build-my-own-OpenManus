"""
基础工具框架 - 核心基类和数据模型

这个模块定义了工具系统的核心抽象：
1. BaseTool: 所有工具的抽象基类
2. ToolResult: 统一的工具执行结果格式
3. ToolResultStatus: 执行状态枚举

学习要点：
- 抽象基类(ABC)的使用
- 枚举类型的定义
- Pydantic模型的数据验证
- 类型注解的最佳实践
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field


class ToolResultStatus(str, Enum):
    """
    工具执行结果状态枚举
    
    学习要点：
    - 继承str和Enum，使枚举值可以直接作为字符串使用
    - 明确的状态定义有助于错误处理和调试
    """
    SUCCESS = "success"      # 执行成功
    ERROR = "error"          # 执行失败
    TIMEOUT = "timeout"      # 执行超时
    INVALID_INPUT = "invalid_input"  # 输入参数无效


class ToolResult(BaseModel):
    """
    统一的工具执行结果模型
    
    学习要点：
    - 使用Pydantic进行数据验证
    - Optional类型表示可选字段
    - Field用于添加字段描述和验证规则
    """
    status: ToolResultStatus = Field(
        description="执行状态"
    )
    
    content: Any = Field(
        default=None,
        description="执行结果内容，可以是任何类型的数据"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        description="错误信息，仅在status为ERROR时有值"
    )
    
    execution_time: Optional[float] = Field(
        default=None,
        description="执行耗时（秒）"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="额外的元数据信息"
    )
    
    @property
    def is_success(self) -> bool:
        """
        判断执行是否成功的便捷属性
        
        Returns:
            bool: True表示执行成功，False表示失败
        """
        return self.status == ToolResultStatus.SUCCESS
    
    @classmethod
    def success(cls, content: Any, execution_time: Optional[float] = None, 
                metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        创建成功结果的便捷方法
        
        学习要点：
        - 类方法(@classmethod)的使用
        - 工厂方法模式
        """
        return cls(
            status=ToolResultStatus.SUCCESS,
            content=content,
            execution_time=execution_time,
            metadata=metadata or {}
        )
    
    @classmethod
    def error(cls, error_message: str, execution_time: Optional[float] = None,
              metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        创建错误结果的便捷方法
        """
        return cls(
            status=ToolResultStatus.ERROR,
            error_message=error_message,
            execution_time=execution_time,
            metadata=metadata or {}
        )
    
    @classmethod
    def timeout(cls, execution_time: Optional[float] = None,
                metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        创建超时结果的便捷方法
        """
        return cls(
            status=ToolResultStatus.TIMEOUT,
            error_message="工具执行超时",
            execution_time=execution_time,
            metadata=metadata or {}
        )
    
    @classmethod
    def invalid_input(cls, error_message: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        创建输入无效结果的便捷方法
        """
        return cls(
            status=ToolResultStatus.INVALID_INPUT,
            error_message=error_message,
            metadata=metadata or {}
        )


class BaseTool(ABC):
    """
    所有工具的抽象基类
    
    学习要点：
    - 抽象基类(ABC)强制子类实现必要方法
    - 抽象方法(@abstractmethod)定义接口规范
    - 属性和方法的命名约定
    """
    
    def __init__(self, name: str, description: str):
        """
        初始化工具基本信息
        
        Args:
            name: 工具名称，应该是唯一的标识符
            description: 工具描述，说明工具的功能和用途
        """
        self.name = name
        self.description = description
    
    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """
        返回工具的JSON Schema定义
        
        学习要点：
        - @property装饰器将方法转换为属性
        - JSON Schema用于定义和验证工具参数
        - 抽象属性强制子类提供具体实现
        
        Returns:
            Dict: JSON Schema格式的参数定义
        """
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具的核心方法
        
        学习要点：
        - 异步方法(async)支持并发执行
        - **kwargs接收任意关键字参数
        - 返回统一的ToolResult格式
        
        Args:
            **kwargs: 工具执行所需的参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        验证输入参数（可选重写）
        
        学习要点：
        - Union类型表示多种可能的返回类型
        - 基类提供默认实现，子类可以重写
        
        Args:
            **kwargs: 待验证的参数
            
        Returns:
            bool: True表示验证通过
            str: 错误信息表示验证失败
        """
        # 默认实现：简单检查必需参数
        if hasattr(self, 'schema') and 'required' in self.schema:
            required_params = self.schema.get('required', [])
            for param in required_params:
                if param not in kwargs:
                    return f"缺少必需参数: {param}"
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取工具的基本信息
        
        Returns:
            Dict: 包含工具名称、描述和schema的字典
        """
        return {
            'name': self.name,
            'description': self.description,
            'schema': self.schema
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Tool({self.name}): {self.description}"
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示"""
        return f"<{self.__class__.__name__}(name='{self.name}')>"