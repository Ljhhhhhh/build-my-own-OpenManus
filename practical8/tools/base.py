"""
基础工具类

这个模块定义了工具的基础类和接口，为具体工具实现提供统一的框架。

对于JavaScript开发者的说明：
- 这里使用了Python的ABC (Abstract Base Class)，类似于TypeScript的abstract class
- dataclass用于定义数据结构，类似于TypeScript的interface
- 类型注解提供了类似TypeScript的类型检查
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import json


@dataclass
class ToolParameter:
    """
    工具参数定义
    
    对应JavaScript中的:
    interface ToolParameter {
        name: string;
        type: "string" | "number" | "boolean" | "object" | "array";
        description: string;
        required?: boolean;
        default?: any;
    }
    """
    name: str                           # 参数名称
    type: str                          # 参数类型
    description: str                   # 参数描述
    required: bool = True              # 是否必需
    default: Optional[Any] = None      # 默认值


@dataclass
class ToolResult:
    """
    工具执行结果
    
    统一的工具执行结果格式
    
    对应JavaScript中的:
    interface ToolResult {
        success: boolean;
        data?: any;
        error?: string;
        metadata?: Record<string, any>;
    }
    """
    success: bool                      # 是否执行成功
    data: Optional[Any] = None         # 结果数据
    error: Optional[str] = None        # 错误信息
    metadata: Optional[Dict[str, Any]] = None  # 元数据


class BaseTool(ABC):
    """
    工具基类
    
    所有工具都应该继承这个基类并实现相应的抽象方法
    
    类似于TypeScript中的:
    abstract class BaseTool {
        abstract name: string;
        abstract description: string;
        abstract parameters: ToolParameter[];
        
        abstract async execute(args: Record<string, any>): Promise<ToolResult>;
    }
    """
    
    def __init__(self):
        """初始化工具"""
        self._validate_tool_definition()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """工具参数列表"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行工具
        
        Args:
            arguments: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        验证工具参数
        
        Args:
            arguments: 要验证的参数
            
        Returns:
            ToolResult: 验证结果，如果验证失败则包含错误信息
        
        类似于JavaScript中的:
        validateArguments(arguments: Record<string, any>): ToolResult {
            for (const param of this.parameters) {
                if (param.required && !(param.name in arguments)) {
                    return {
                        success: false,
                        error: `Missing required parameter: ${param.name}`
                    };
                }
                // ... 其他验证逻辑
            }
            return { success: true };
        }
        """
        for param in self.parameters:
            # 检查必需参数
            if param.required and param.name not in arguments:
                return ToolResult(
                    success=False,
                    error=f"Missing required parameter: {param.name}"
                )
            
            # 如果参数不存在但有默认值，使用默认值
            if param.name not in arguments and param.default is not None:
                arguments[param.name] = param.default
            
            # 类型验证（简单实现）
            if param.name in arguments:
                value = arguments[param.name]
                if not self._validate_parameter_type(value, param.type):
                    return ToolResult(
                        success=False,
                        error=f"Invalid type for parameter {param.name}: expected {param.type}"
                    )
        
        return ToolResult(success=True)
    
    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """
        验证参数类型
        
        Args:
            value: 参数值
            expected_type: 期望的类型
            
        Returns:
            bool: 是否类型匹配
        """
        type_mapping = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # 未知类型，跳过验证
        
        return isinstance(value, expected_python_type)
    
    def _validate_tool_definition(self) -> None:
        """
        验证工具定义的完整性
        
        确保工具的基本信息都已正确定义
        """
        if not self.name:
            raise ValueError("Tool name cannot be empty")
        
        if not self.description:
            raise ValueError("Tool description cannot be empty")
        
        if not isinstance(self.parameters, list):
            raise ValueError("Tool parameters must be a list")
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的JSON Schema
        
        Returns:
            Dict: 工具的JSON Schema定义
        
        类似于JavaScript中的:
        getSchema(): object {
            return {
                name: this.name,
                description: this.description,
                parameters: {
                    type: "object",
                    properties: this.parameters.reduce((props, param) => {
                        props[param.name] = {
                            type: param.type,
                            description: param.description
                        };
                        return props;
                    }, {}),
                    required: this.parameters.filter(p => p.required).map(p => p.name)
                }
            };
        }
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            
            if param.default is not None:
                properties[param.name]["default"] = param.default
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Tool({self.name}): {self.description}"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class SyncTool(BaseTool):
    """
    同步工具基类
    
    对于不需要异步操作的工具，可以继承这个类并实现sync_execute方法
    
    类似于JavaScript中的:
    abstract class SyncTool extends BaseTool {
        abstract syncExecute(args: Record<string, any>): ToolResult;
        
        async execute(args: Record<string, any>): Promise<ToolResult> {
            return this.syncExecute(args);
        }
    }
    """
    
    @abstractmethod
    def sync_execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        同步执行工具
        
        Args:
            arguments: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        异步包装器，调用同步执行方法
        
        Args:
            arguments: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        # 先验证参数
        validation_result = self.validate_arguments(arguments)
        if not validation_result.success:
            return validation_result
        
        # 执行同步方法
        try:
            return self.sync_execute(arguments)
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )


def create_simple_tool(
    name: str,
    description: str,
    parameters: List[ToolParameter],
    execute_func: callable
) -> BaseTool:
    """
    创建简单工具的工厂函数
    
    这是一个便利函数，用于快速创建简单的工具
    
    Args:
        name: 工具名称
        description: 工具描述
        parameters: 参数列表
        execute_func: 执行函数
        
    Returns:
        BaseTool: 创建的工具实例
    
    类似于JavaScript中的:
    function createSimpleTool(
        name: string,
        description: string,
        parameters: ToolParameter[],
        executeFunc: (args: Record<string, any>) => ToolResult
    ): BaseTool {
        return new class extends SyncTool {
            name = name;
            description = description;
            parameters = parameters;
            
            syncExecute(args: Record<string, any>): ToolResult {
                return executeFunc(args);
            }
        }();
    }
    """
    
    class SimpleTool(SyncTool):
        def __init__(self):
            self._name = name
            self._description = description
            self._parameters = parameters
            self._execute_func = execute_func
            super().__init__()
        
        @property
        def name(self) -> str:
            return self._name
        
        @property
        def description(self) -> str:
            return self._description
        
        @property
        def parameters(self) -> List[ToolParameter]:
            return self._parameters
        
        def sync_execute(self, arguments: Dict[str, Any]) -> ToolResult:
            return self._execute_func(arguments)
    
    return SimpleTool()


# 导出主要的类和函数
__all__ = [
    "ToolParameter",
    "ToolResult",
    "BaseTool",
    "SyncTool",
    "create_simple_tool"
]