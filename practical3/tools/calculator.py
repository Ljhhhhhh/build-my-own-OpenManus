"""
计算器工具 - 安全的数学表达式计算

这个模块实现了一个安全的计算器工具，支持基本的数学运算。

学习要点：
1. 继承抽象基类的具体实现
2. 安全的表达式求值（避免eval的安全风险）
3. 错误处理和输入验证
4. JSON Schema的实际应用
5. 异步方法的实现
"""

import ast
import operator
import time
from typing import Any, Dict, Union
from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """
    安全的数学计算器工具
    
    支持基本的数学运算：+, -, *, /, //, %, **
    使用AST（抽象语法树）进行安全的表达式求值
    
    学习要点：
    - 继承BaseTool并实现所有抽象方法
    - 使用AST模块安全地解析和执行数学表达式
    - 运算符映射和白名单机制
    """
    
    # 支持的运算符映射
    # 学习要点：类属性用于定义常量和配置
    OPERATORS = {
        ast.Add: operator.add,          # +
        ast.Sub: operator.sub,          # -
        ast.Mult: operator.mul,         # *
        ast.Div: operator.truediv,      # /
        ast.FloorDiv: operator.floordiv, # //
        ast.Mod: operator.mod,          # %
        ast.Pow: operator.pow,          # **
        ast.USub: operator.neg,         # 负号
        ast.UAdd: operator.pos,         # 正号
    }
    
    def __init__(self):
        """
        初始化计算器工具
        
        学习要点：
        - 调用父类构造函数
        - 设置工具的基本信息
        """
        super().__init__(
            name="calculator",
            description="安全的数学计算器，支持基本的数学运算"
        )
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回计算器工具的JSON Schema
        
        学习要点：
        - @property装饰器的使用
        - JSON Schema的结构和字段定义
        - 参数验证规则的设置
        """
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，支持 +, -, *, /, //, %, ** 运算符",
                    "examples": [
                        "2 + 3",
                        "10 * (5 - 2)",
                        "2 ** 3",
                        "15 / 3",
                        "17 % 5"
                    ]
                }
            },
            "required": ["expression"],
            "additionalProperties": False
        }
    
    def _safe_eval(self, expression: str) -> Union[float, int]:
        """
        安全地计算数学表达式
        
        学习要点：
        - 使用AST而不是eval()来避免安全风险
        - 递归处理AST节点
        - 白名单机制限制允许的操作
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            计算结果
            
        Raises:
            ValueError: 表达式无效或包含不支持的操作
            ZeroDivisionError: 除零错误
        """
        try:
            # 解析表达式为AST
            # 学习要点：AST模块用于安全地解析Python代码
            node = ast.parse(expression, mode='eval')
            return self._eval_node(node.body)
        except SyntaxError as e:
            raise ValueError(f"表达式语法错误: {e}")
    
    def _eval_node(self, node: ast.AST) -> Union[float, int]:
        """
        递归计算AST节点
        
        学习要点：
        - 递归算法的应用
        - 模式匹配（通过isinstance）
        - 运算符的动态调用
        
        Args:
            node: AST节点
            
        Returns:
            节点计算结果
        """
        if isinstance(node, ast.Constant):
            # 常量节点（数字）
            # 学习要点：Python 3.8+使用ast.Constant替代ast.Num
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError(f"不支持的常量类型: {type(node.value)}")
        
        elif isinstance(node, ast.BinOp):
            # 二元运算节点
            # 学习要点：递归处理左右操作数
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            
            if type(node.op) in self.OPERATORS:
                try:
                    return self.OPERATORS[type(node.op)](left, right)
                except ZeroDivisionError:
                    raise ZeroDivisionError("除零错误")
                except Exception as e:
                    raise ValueError(f"运算错误: {e}")
            else:
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
        
        elif isinstance(node, ast.UnaryOp):
            # 一元运算节点（如负号）
            operand = self._eval_node(node.operand)
            
            if type(node.op) in self.OPERATORS:
                return self.OPERATORS[type(node.op)](operand)
            else:
                raise ValueError(f"不支持的一元运算符: {type(node.op).__name__}")
        
        else:
            # 不支持的节点类型
            raise ValueError(f"不支持的表达式类型: {type(node).__name__}")
    
    def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        验证输入参数
        
        学习要点：
        - 重写父类方法
        - 输入验证的最佳实践
        - 早期错误检测
        """
        # 调用父类的基本验证
        base_result = super().validate_input(**kwargs)
        if base_result is not True:
            return base_result
        
        expression = kwargs.get('expression', '').strip()
        
        # 检查表达式是否为空
        if not expression:
            return "表达式不能为空"
        
        # 检查表达式长度（防止过长的表达式）
        if len(expression) > 1000:
            return "表达式过长，最大支持1000个字符"
        
        # 检查是否包含危险字符
        # 学习要点：安全编程的重要性
        dangerous_chars = ['import', 'exec', 'eval', '__', 'open', 'file']
        expression_lower = expression.lower()
        for char in dangerous_chars:
            if char in expression_lower:
                return f"表达式包含不安全的内容: {char}"
        
        return True
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行计算器工具
        
        学习要点：
        - 异步方法的实现
        - 完整的错误处理流程
        - 执行时间统计
        - 统一的结果格式
        
        Args:
            **kwargs: 包含expression参数的字典
            
        Returns:
            ToolResult: 计算结果
        """
        start_time = time.time()
        
        try:
            # 验证输入
            validation_result = self.validate_input(**kwargs)
            if validation_result is not True:
                return ToolResult.invalid_input(validation_result)
            
            expression = kwargs['expression'].strip()
            
            # 执行计算
            # 学习要点：在异步方法中执行同步操作
            result = self._safe_eval(expression)
            
            execution_time = time.time() - start_time
            
            # 返回成功结果
            return ToolResult.success(
                content={
                    'expression': expression,
                    'result': result,
                    'result_type': type(result).__name__
                },
                execution_time=execution_time,
                metadata={
                    'tool': self.name,
                    'operation_count': expression.count('+') + expression.count('-') + 
                                     expression.count('*') + expression.count('/') + 
                                     expression.count('**') + expression.count('%')
                }
            )
            
        except ZeroDivisionError as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=str(e),
                execution_time=execution_time
            )
            
        except ValueError as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=str(e),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=f"计算过程中发生未知错误: {e}",
                execution_time=execution_time
            )


# 使用示例和测试代码
if __name__ == "__main__":
    """
    模块测试代码
    
    学习要点：
    - __name__ == "__main__" 的用法
    - 异步代码的测试方法
    """
    import asyncio
    
    async def test_calculator():
        """测试计算器工具的各种功能"""
        calc = CalculatorTool()
        
        # 测试用例
        test_cases = [
            "2 + 3",
            "10 * (5 - 2)",
            "2 ** 3",
            "15 / 3",
            "17 % 5",
            "1 / 0",  # 除零测试
            "invalid expression",  # 无效表达式测试
        ]
        
        print(f"=== {calc.name} 工具测试 ===")
        print(f"描述: {calc.description}")
        print(f"Schema: {calc.schema}")
        print()
        
        for expression in test_cases:
            print(f"测试表达式: {expression}")
            result = await calc.execute(expression=expression)
            print(f"结果: {result}")
            print("-" * 50)
    
    # 运行测试
    asyncio.run(test_calculator())