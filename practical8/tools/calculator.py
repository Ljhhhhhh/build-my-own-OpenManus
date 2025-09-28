"""
计算器工具实现

这个模块实现了一个基础的计算器工具，支持基本的数学运算。

对于JavaScript开发者的说明：
- 这里展示了如何继承BaseTool来创建具体的工具
- 使用了Python的eval函数进行表达式计算（在生产环境中需要更安全的实现）
- 错误处理模式类似于JavaScript的try-catch
"""

import math
import operator
from typing import Dict, Any, List
from .base import SyncTool, ToolParameter, ToolResult


class CalculatorTool(SyncTool):
    """
    计算器工具
    
    支持基本的数学运算，包括加减乘除、幂运算、三角函数等
    
    类似于JavaScript中的:
    class CalculatorTool extends SyncTool {
        get name(): string { return "calculator"; }
        get description(): string { return "Perform mathematical calculations"; }
        // ... 其他实现
    }
    """
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "Perform mathematical calculations including basic arithmetic, trigonometry, and more"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sin(pi/2)', 'sqrt(16)')",
                required=True
            )
        ]
    
    def sync_execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行计算
        
        Args:
            arguments: 包含expression参数的字典
            
        Returns:
            ToolResult: 计算结果
        
        类似于JavaScript中的:
        syncExecute(arguments: Record<string, any>): ToolResult {
            try {
                const expression = arguments.expression;
                const result = this.evaluateExpression(expression);
                return {
                    success: true,
                    data: { result, expression }
                };
            } catch (error) {
                return {
                    success: false,
                    error: `Calculation error: ${error.message}`
                };
            }
        }
        """
        try:
            expression = arguments["expression"]
            
            # 安全的数学表达式计算
            result = self._safe_eval(expression)
            
            return ToolResult(
                success=True,
                data={
                    "result": result,
                    "expression": expression,
                    "formatted": f"{expression} = {result}"
                },
                metadata={
                    "tool": "calculator",
                    "operation_type": "expression_evaluation"
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Calculation error: {str(e)}"
            )
    
    def _safe_eval(self, expression: str) -> float:
        """
        安全的表达式计算
        
        使用受限的命名空间来避免安全风险
        
        Args:
            expression: 数学表达式
            
        Returns:
            float: 计算结果
        
        类似于JavaScript中的:
        private safeEval(expression: string): number {
            // 创建安全的计算环境
            const safeContext = {
                // 基本数学运算符会被JavaScript引擎处理
                Math: Math,
                sin: Math.sin,
                cos: Math.cos,
                // ... 其他安全函数
            };
            
            // 使用Function构造器或其他安全方法计算
            return new Function('Math', 'sin', 'cos', ..., `return ${expression}`)(
                Math, Math.sin, Math.cos, ...
            );
        }
        """
        # 定义安全的命名空间
        safe_dict = {
            # 基本数学函数
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            
            # 数学常数
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            
            # 三角函数
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "atan2": math.atan2,
            
            # 双曲函数
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            
            # 指数和对数函数
            "exp": math.exp,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "pow": pow,
            "sqrt": math.sqrt,
            
            # 其他数学函数
            "ceil": math.ceil,
            "floor": math.floor,
            "factorial": math.factorial,
            "gcd": math.gcd,
            
            # 基本运算符（Python内置）
            "__builtins__": {}  # 清空内置函数，提高安全性
        }
        
        try:
            # 使用eval计算表达式，但限制在安全的命名空间内
            result = eval(expression, safe_dict)
            
            # 确保结果是数字
            if isinstance(result, (int, float)):
                return float(result)
            else:
                raise ValueError(f"Expression result is not a number: {type(result)}")
        
        except ZeroDivisionError:
            raise ValueError("Division by zero")
        except OverflowError:
            raise ValueError("Result too large")
        except (SyntaxError, NameError) as e:
            raise ValueError(f"Invalid expression: {str(e)}")


class AdvancedCalculatorTool(SyncTool):
    """
    高级计算器工具
    
    支持更复杂的数学运算，包括统计函数、数列计算等
    """
    
    @property
    def name(self) -> str:
        return "advanced_calculator"
    
    @property
    def description(self) -> str:
        return "Perform advanced mathematical calculations including statistics, sequences, and complex operations"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Type of operation: 'expression', 'statistics', 'sequence'",
                required=True
            ),
            ToolParameter(
                name="data",
                type="object",
                description="Operation-specific data (expression string, numbers array, etc.)",
                required=True
            )
        ]
    
    def sync_execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行高级计算
        
        Args:
            arguments: 包含operation和data参数的字典
            
        Returns:
            ToolResult: 计算结果
        """
        try:
            operation = arguments["operation"]
            data = arguments["data"]
            
            if operation == "expression":
                return self._handle_expression(data)
            elif operation == "statistics":
                return self._handle_statistics(data)
            elif operation == "sequence":
                return self._handle_sequence(data)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Advanced calculation error: {str(e)}"
            )
    
    def _handle_expression(self, data: Dict[str, Any]) -> ToolResult:
        """处理表达式计算"""
        calculator = CalculatorTool()
        return calculator.sync_execute({"expression": data.get("expression", "")})
    
    def _handle_statistics(self, data: Dict[str, Any]) -> ToolResult:
        """
        处理统计计算
        
        Args:
            data: 包含numbers数组的字典
            
        Returns:
            ToolResult: 统计结果
        """
        numbers = data.get("numbers", [])
        if not numbers:
            return ToolResult(success=False, error="No numbers provided for statistics")
        
        # 确保所有元素都是数字
        try:
            numbers = [float(x) for x in numbers]
        except (ValueError, TypeError):
            return ToolResult(success=False, error="All elements must be numbers")
        
        # 计算统计值
        n = len(numbers)
        total = sum(numbers)
        mean = total / n
        
        # 计算方差和标准差
        variance = sum((x - mean) ** 2 for x in numbers) / n
        std_dev = math.sqrt(variance)
        
        # 计算中位数
        sorted_numbers = sorted(numbers)
        if n % 2 == 0:
            median = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
        else:
            median = sorted_numbers[n//2]
        
        return ToolResult(
            success=True,
            data={
                "count": n,
                "sum": total,
                "mean": mean,
                "median": median,
                "min": min(numbers),
                "max": max(numbers),
                "variance": variance,
                "standard_deviation": std_dev,
                "range": max(numbers) - min(numbers)
            },
            metadata={
                "tool": "advanced_calculator",
                "operation_type": "statistics"
            }
        )
    
    def _handle_sequence(self, data: Dict[str, Any]) -> ToolResult:
        """
        处理数列计算
        
        Args:
            data: 包含数列参数的字典
            
        Returns:
            ToolResult: 数列结果
        """
        sequence_type = data.get("type", "arithmetic")
        start = data.get("start", 0)
        step = data.get("step", 1)
        count = data.get("count", 10)
        
        if count > 1000:  # 限制数列长度
            return ToolResult(success=False, error="Sequence count too large (max 1000)")
        
        if sequence_type == "arithmetic":
            # 等差数列
            sequence = [start + i * step for i in range(count)]
        elif sequence_type == "geometric":
            # 等比数列
            if step == 0:
                return ToolResult(success=False, error="Geometric sequence ratio cannot be zero")
            sequence = [start * (step ** i) for i in range(count)]
        elif sequence_type == "fibonacci":
            # 斐波那契数列
            sequence = []
            a, b = 0, 1
            for _ in range(count):
                sequence.append(a)
                a, b = b, a + b
        else:
            return ToolResult(success=False, error=f"Unknown sequence type: {sequence_type}")
        
        return ToolResult(
            success=True,
            data={
                "sequence": sequence,
                "type": sequence_type,
                "count": count,
                "sum": sum(sequence) if sequence else 0
            },
            metadata={
                "tool": "advanced_calculator",
                "operation_type": "sequence"
            }
        )


# 导出工具类
__all__ = [
    "CalculatorTool",
    "AdvancedCalculatorTool"
]