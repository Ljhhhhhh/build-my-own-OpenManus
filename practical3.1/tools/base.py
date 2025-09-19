"""
基础工具框架 - 核心抽象类和数据模型

这个模块是practical3.1的核心，专注于Python基础概念：
1. 抽象基类 (ABC) - 类似TypeScript的interface
2. 枚举类型 - 类似TypeScript的enum  
3. 数据模型 - 使用Pydantic进行验证
4. 类型注解 - 类似TypeScript的类型系统

学习重点：
- 面向对象编程的基础概念
- 抽象和继承
- 类型系统的使用
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolResultStatus(str, Enum):
    """
    工具执行结果状态枚举
    
    💡 对比TypeScript:
    enum ToolResultStatus {
        SUCCESS = "success",
        ERROR = "error"
    }
    
    学习要点：
    - 继承str和Enum，让枚举值可以直接当字符串用
    - 明确的状态定义，便于错误处理
    """
    SUCCESS = "success"      # 执行成功
    ERROR = "error"          # 执行失败
    INVALID_INPUT = "invalid_input"  # 输入参数无效


class ToolResult(BaseModel):
    """
    统一的工具执行结果模型
    
    💡 对比TypeScript:
    interface ToolResult {
        status: ToolResultStatus;
        content?: any;
        error_message?: string;
    }
    
    学习要点：
    - Pydantic提供数据验证，类似Zod库
    - Optional表示可选字段，类似TypeScript的?
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
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="额外的元数据信息"
    )
    
    @classmethod
    def success(cls, content: Any, metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        创建成功结果的便捷方法
        
        💡 对比TypeScript:
        static success(content: any, metadata?: any): ToolResult {
            return new ToolResult({ status: "success", content, metadata });
        }
        
        学习要点：
        - @classmethod装饰器创建类方法
        - 工厂方法模式，简化对象创建
        """
        return cls(
            status=ToolResultStatus.SUCCESS,
            content=content,
            metadata=metadata or {}
        )
    
    @classmethod
    def error(cls, error_message: str, metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        创建错误结果的便捷方法
        """
        return cls(
            status=ToolResultStatus.ERROR,
            error_message=error_message,
            metadata=metadata or {}
        )
    
    @classmethod
    def invalid_input(cls, error_message: str, metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
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
    
    💡 对比TypeScript:
    abstract class BaseTool {
        abstract name: string;
        abstract description: string;
        abstract execute(params: any): Promise<ToolResult>;
    }
    
    学习要点：
    - ABC (Abstract Base Class) 强制子类实现必要方法
    - @abstractmethod 定义必须实现的方法
    - 类似TypeScript的abstract class
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
        
        💡 对比TypeScript:
        abstract get schema(): object;
        
        学习要点：
        - @property装饰器将方法转换为属性
        - JSON Schema用于定义和验证工具参数
        - 抽象属性强制子类提供具体实现
        
        Returns:
            Dict: JSON Schema格式的参数定义
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        执行工具的核心方法
        
        💡 对比TypeScript:
        abstract execute(params: any): ToolResult;
        
        学习要点：
        - **kwargs接收任意关键字参数，类似...args
        - 返回统一的ToolResult格式
        - 这里简化为同步方法，practical3.2会介绍异步
        
        Args:
            **kwargs: 工具执行所需的参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    def validate_input(self, **kwargs) -> bool | str:
        """
        验证输入参数（可选重写）
        
        💡 对比TypeScript:
        validate_input(params: any): boolean | string {
            // 返回true表示验证通过，返回string表示错误信息
        }
        
        学习要点：
        - Union类型 (bool | str) 表示多种可能的返回类型
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
        获取工具信息
        
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
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示"""
        return f"<{self.__class__.__name__}(name='{self.name}')>"