"""
计算器工具 - 简单的数学运算工具

这个模块演示如何基于BaseTool创建一个简单的工具。

学习要点：
1. 继承BaseTool抽象基类
2. 实现必需的抽象方法
3. 定义JSON Schema
4. 基本的错误处理
"""

import time
from typing import Any, Dict
from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """
    简单的计算器工具
    
    支持基本的两数运算：加、减、乘、除
    
    学习要点：
    - 继承BaseTool并实现所有抽象方法
    - 简单直接的业务逻辑实现
    - 基础的参数验证和错误处理
    """
    
    def __init__(self):
        """
        初始化计算器工具
        
        学习要点：
        - 调用父类构造函数
        - 设置工具的基本信息
        """
        super().__init__(
            name="calculator",
            description="简单的计算器工具，支持两个数字的基本运算"
        )
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回工具的JSON Schema
        
        学习要点：
        - @property装饰器的使用
        - JSON Schema的基本结构
        - 如何定义参数和验证规则
        """
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "要执行的运算类型"
                },
                "a": {
                    "type": "number",
                    "description": "第一个数字"
                },
                "b": {
                    "type": "number",
                    "description": "第二个数字"
                }
            },
            "required": ["operation", "a", "b"],
            "additionalProperties": False
        }
    
    def validate_input(self, **kwargs) -> bool | str:
        """
        验证输入参数
        
        学习要点：
        - 重写父类的验证方法
        - 基本的参数检查
        - 返回True表示验证通过，返回字符串表示错误信息
        """
        # 调用父类的基本验证
        base_result = super().validate_input(**kwargs)
        if base_result is not True:
            return base_result
        
        # 检查除零情况
        if kwargs.get('operation') == 'divide' and kwargs.get('b') == 0:
            return "除数不能为零"
        
        return True
    
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行计算器工具
        
        学习要点：
        - 异步方法的实现
        - 基本的业务逻辑处理
        - 统一的结果返回格式
        
        Args:
            **kwargs: 包含operation, a, b参数的字典
            
        Returns:
            ToolResult: 计算结果
        """
        start_time = time.time()
        
        try:
            # 验证输入
            validation_result = self.validate_input(**kwargs)
            if validation_result is not True:
                return ToolResult.invalid_input(validation_result)
            
            # 获取参数
            operation = kwargs['operation']
            a = kwargs['a']
            b = kwargs['b']
            
            # 执行计算
            if operation == 'add':
                result = a + b
            elif operation == 'subtract':
                result = a - b
            elif operation == 'multiply':
                result = a * b
            elif operation == 'divide':
                result = a / b
            else:
                return ToolResult.error(
                    error_message=f"不支持的运算类型: {operation}",
                    execution_time=time.time() - start_time
                )
            
            execution_time = time.time() - start_time
            
            # 返回成功结果
            return ToolResult.success(
                content={
                    'operation': operation,
                    'a': a,
                    'b': b,
                    'result': result
                },
                execution_time=execution_time,
                metadata={
                    'tool': self.name,
                    'operation_type': operation
                }
            )
            
        except ZeroDivisionError:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message="除零错误",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=f"计算过程中发生错误: {e}",
                execution_time=execution_time
            )