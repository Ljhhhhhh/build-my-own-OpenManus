"""
计算器工具 - 基础工具实现示例

这个模块演示如何基于BaseTool创建具体的工具实现。
专注于Python基础概念，避免复杂的异步编程。

学习要点：
1. 继承抽象基类
2. 实现抽象方法
3. JSON Schema的定义
4. 基础的错误处理
5. 方法重写
"""

from typing import Any, Dict
from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """
    简单的计算器工具
    
    支持基本的两数运算：加、减、乘、除
    
    💡 对比TypeScript:
    class CalculatorTool extends BaseTool {
        execute(params: {operation: string, a: number, b: number}): ToolResult {
            // 实现计算逻辑
        }
    }
    
    学习要点：
    - 继承BaseTool并实现所有抽象方法
    - 简单直接的业务逻辑实现
    - 基础的参数验证和错误处理
    """
    
    def __init__(self):
        """
        初始化计算器工具
        
        学习要点：
        - 调用父类构造函数 super().__init__()
        - 设置工具的基本信息
        """
        super().__init__(
            name="calculator",
            description="简单的计算器工具，支持两个数字的基本运算（加减乘除）"
        )
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回工具的JSON Schema
        
        💡 对比TypeScript:
        get schema() {
            return {
                type: "object",
                properties: {
                    operation: { type: "string", enum: ["add", "subtract", "multiply", "divide"] },
                    a: { type: "number" },
                    b: { type: "number" }
                },
                required: ["operation", "a", "b"]
            };
        }
        
        学习要点：
        - @property装饰器将方法转换为属性
        - JSON Schema的基本结构
        - 如何定义参数类型和验证规则
        - enum约束可选值
        """
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "要执行的运算类型：add(加), subtract(减), multiply(乘), divide(除)"
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
            "additionalProperties": False  # 不允许额外的属性
        }
    
    def validate_input(self, **kwargs) -> bool | str:
        """
        验证输入参数
        
        💡 对比TypeScript:
        validate_input(params: any): boolean | string {
            // 先调用父类验证
            const baseResult = super.validate_input(params);
            if (baseResult !== true) return baseResult;
            
            // 添加自定义验证逻辑
            if (params.operation === 'divide' && params.b === 0) {
                return "除数不能为零";
            }
            return true;
        }
        
        学习要点：
        - 重写父类的验证方法
        - 先调用父类验证，再添加自定义逻辑
        - 返回True表示验证通过，返回字符串表示错误信息
        """
        # 调用父类的基本验证
        base_result = super().validate_input(**kwargs)
        if base_result is not True:
            return base_result
        
        # 添加自定义验证：检查除零情况
        if kwargs.get('operation') == 'divide' and kwargs.get('b') == 0:
            return "除数不能为零"
        
        # 验证operation是否有效
        valid_operations = ["add", "subtract", "multiply", "divide"]
        if kwargs.get('operation') not in valid_operations:
            return f"无效的运算类型，支持的运算: {', '.join(valid_operations)}"
        
        return True
    
    def execute(self, **kwargs) -> ToolResult:
        """
        执行计算器工具
        
        💡 对比TypeScript:
        execute(params: {operation: string, a: number, b: number}): ToolResult {
            // 验证输入
            const validation = this.validate_input(params);
            if (validation !== true) {
                return ToolResult.invalid_input(validation);
            }
            
            // 执行计算
            const {operation, a, b} = params;
            let result: number;
            
            switch(operation) {
                case 'add': result = a + b; break;
                case 'subtract': result = a - b; break;
                // ...
            }
            
            return ToolResult.success({operation, a, b, result});
        }
        
        学习要点：
        - 实现抽象方法
        - 基本的业务逻辑处理
        - 统一的结果返回格式
        - 错误处理模式
        
        Args:
            **kwargs: 包含operation, a, b参数的字典
            
        Returns:
            ToolResult: 计算结果
        """
        try:
            # 1. 验证输入
            validation_result = self.validate_input(**kwargs)
            if validation_result is not True:
                return ToolResult.invalid_input(validation_result)
            
            # 2. 获取参数
            operation = kwargs['operation']
            a = kwargs['a']
            b = kwargs['b']
            
            # 3. 执行计算
            if operation == 'add':
                result = a + b
            elif operation == 'subtract':
                result = a - b
            elif operation == 'multiply':
                result = a * b
            elif operation == 'divide':
                result = a / b
            else:
                return ToolResult.error(f"不支持的运算类型: {operation}")
            
            # 4. 返回成功结果
            return ToolResult.success(
                content={
                    'operation': operation,
                    'a': a,
                    'b': b,
                    'result': result,
                    'expression': f"{a} {self._get_operation_symbol(operation)} {b} = {result}"
                },
                metadata={
                    'tool': self.name,
                    'operation_type': operation
                }
            )
            
        except Exception as e:
            # 5. 处理未预期的错误
            return ToolResult.error(
                error_message=f"计算过程中发生错误: {str(e)}",
                metadata={'tool': self.name}
            )
    
    def _get_operation_symbol(self, operation: str) -> str:
        """
        获取运算符号
        
        学习要点：
        - 私有方法命名约定（以_开头）
        - 字典映射的使用
        
        Args:
            operation: 运算类型
            
        Returns:
            str: 对应的数学符号
        """
        symbols = {
            'add': '+',
            'subtract': '-', 
            'multiply': '×',
            'divide': '÷'
        }
        return symbols.get(operation, '?')


# 测试代码（当直接运行此文件时执行）
if __name__ == "__main__":
    """
    测试计算器工具的基本功能
    
    学习要点：
    - if __name__ == "__main__": 的用法
    - 简单的测试用例编写
    """
    print("🧮 测试计算器工具")
    print("=" * 40)
    
    # 创建计算器实例
    calculator = CalculatorTool()
    
    # 测试用例
    test_cases = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "subtract", "a": 20, "b": 8},
        {"operation": "multiply", "a": 6, "b": 7},
        {"operation": "divide", "a": 15, "b": 3},
        {"operation": "divide", "a": 10, "b": 0},  # 除零错误测试
        {"operation": "invalid", "a": 1, "b": 2},  # 无效操作测试
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case}")
        result = calculator.execute(**test_case)
        print(f"状态: {result.status}")
        
        if result.status == "success":
            print(f"结果: {result.content['expression']}")
        else:
            print(f"错误: {result.error_message}")
    
    print("\n" + "=" * 40)
    print("✅ 测试完成！")