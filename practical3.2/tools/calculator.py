"""
异步计算器工具 - 高级版本

这个模块实现了一个异步的计算器工具，支持基础数学运算。
相比practical3.1，这里引入了异步执行、输入验证、错误处理等高级特性。

学习要点：
1. 异步工具的具体实现
2. 复杂输入验证
3. 数学运算的安全处理
4. 结构化错误信息
5. 性能优化技巧
"""

import asyncio
import math
import operator
from typing import Dict, Any, Union, List
from decimal import Decimal, InvalidOperation

from .base import AsyncBaseTool, ToolResult, tool_timer


class AsyncCalculatorTool(AsyncBaseTool):
    """
    异步计算器工具
    
    💡 对比TypeScript:
    class AsyncCalculatorTool extends AsyncBaseTool {
        private supportedOperations: Map<string, Function>;
        
        constructor() {
            super("async_calculator", "异步计算器工具", 10.0, 2);
            
            this.supportedOperations = new Map([
                ['add', (a: number, b: number) => a + b],
                ['subtract', (a: number, b: number) => a - b],
                ['multiply', (a: number, b: number) => a * b],
                ['divide', (a: number, b: number) => {
                    if (b === 0) throw new Error("除数不能为零");
                    return a / b;
                }],
                ['power', (a: number, b: number) => Math.pow(a, b)],
                ['sqrt', (a: number) => {
                    if (a < 0) throw new Error("不能计算负数的平方根");
                    return Math.sqrt(a);
                }],
                ['factorial', (a: number) => {
                    if (a < 0 || !Number.isInteger(a)) {
                        throw new Error("阶乘只能计算非负整数");
                    }
                    let result = 1;
                    for (let i = 2; i <= a; i++) {
                        result *= i;
                    }
                    return result;
                }]
            ]);
        }
        
        get schema(): object {
            return {
                type: "object",
                properties: {
                    operation: {
                        type: "string",
                        enum: Array.from(this.supportedOperations.keys()),
                        description: "要执行的数学运算"
                    },
                    operands: {
                        type: "array",
                        items: { type: "number" },
                        description: "运算数"
                    },
                    precision: {
                        type: "integer",
                        minimum: 0,
                        maximum: 10,
                        default: 2,
                        description: "结果精度（小数位数）"
                    }
                },
                required: ["operation", "operands"]
            };
        }
        
        async validateInput(params: any): Promise<boolean | string> {
            // 验证逻辑
        }
        
        async execute(params: any): Promise<ToolResult> {
            // 执行逻辑
        }
    }
    
    学习要点：
    - 异步工具的完整实现
    - 复杂业务逻辑的处理
    - 数学运算的安全实现
    - 错误处理的最佳实践
    """
    
    def __init__(self):
        """
        初始化异步计算器工具
        
        学习要点：
        - 工具的初始化配置
        - 支持操作的定义
        - 运算符映射的设计
        """
        super().__init__(
            name="async_calculator",
            description="异步计算器工具，支持基础数学运算",
            timeout=10.0,
            max_retries=2
        )
        
        # 支持的运算操作
        self.supported_operations = {
            'add': self._add,
            'subtract': self._subtract,
            'multiply': self._multiply,
            'divide': self._divide,
            'power': self._power,
            'sqrt': self._sqrt,
            'factorial': self._factorial,
            'sin': self._sin,
            'cos': self._cos,
            'tan': self._tan,
            'log': self._log,
            'ln': self._ln,
            'abs': self._abs,
            'round': self._round,
            'ceil': self._ceil,
            'floor': self._floor
        }
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回计算器工具的JSON Schema
        
        学习要点：
        - 复杂Schema的设计
        - 枚举值的定义
        - 条件验证的表达
        - 默认值的设置
        
        Returns:
            Dict[str, Any]: JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": list(self.supported_operations.keys()),
                    "description": "要执行的数学运算"
                },
                "operands": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1,
                    "maxItems": 10,
                    "description": "运算数（根据操作类型需要不同数量的操作数）"
                },
                "precision": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 10,
                    "default": 2,
                    "description": "结果精度（小数位数）"
                },
                "use_decimal": {
                    "type": "boolean",
                    "default": False,
                    "description": "是否使用高精度小数运算"
                }
            },
            "required": ["operation", "operands"],
            "additionalProperties": False
        }
    
    async def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        异步输入验证
        
        💡 对比TypeScript:
        async validateInput(params: any): Promise<boolean | string> {
            // 基础验证
            if (!params.operation || !params.operands) {
                return "缺少必需的参数：operation 和 operands";
            }
            
            // 操作验证
            if (!this.supportedOperations.has(params.operation)) {
                return `不支持的操作: ${params.operation}`;
            }
            
            // 操作数验证
            if (!Array.isArray(params.operands) || params.operands.length === 0) {
                return "operands 必须是非空数组";
            }
            
            // 操作数数量验证
            const requiredOperands = this.getRequiredOperandCount(params.operation);
            if (params.operands.length !== requiredOperands) {
                return `操作 ${params.operation} 需要 ${requiredOperands} 个操作数`;
            }
            
            // 数值验证
            for (const operand of params.operands) {
                if (typeof operand !== 'number' || !isFinite(operand)) {
                    return `无效的操作数: ${operand}`;
                }
            }
            
            // 特殊验证
            return await this.validateSpecialCases(params);
        }
        
        学习要点：
        - 多层次的输入验证
        - 异步验证的实现
        - 特殊情况的处理
        - 详细错误信息的提供
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            Union[bool, str]: 验证结果
        """
        # 基础参数检查
        operation = kwargs.get('operation')
        operands = kwargs.get('operands')
        
        if not operation:
            return "缺少必需的参数：operation"
        
        if not operands:
            return "缺少必需的参数：operands"
        
        # 操作类型验证
        if operation not in self.supported_operations:
            return f"不支持的操作: {operation}。支持的操作: {', '.join(self.supported_operations.keys())}"
        
        # 操作数类型和格式验证
        if not isinstance(operands, list):
            return "operands 必须是数组"
        
        if len(operands) == 0:
            return "operands 不能为空"
        
        if len(operands) > 10:
            return "operands 数量不能超过10个"
        
        # 验证每个操作数
        for i, operand in enumerate(operands):
            if not isinstance(operand, (int, float)):
                return f"操作数 {i+1} 必须是数字，当前类型: {type(operand).__name__}"
            
            if not math.isfinite(operand):
                return f"操作数 {i+1} 必须是有限数字（不能是无穷大或NaN）"
        
        # 操作数数量验证
        required_count = self._get_required_operand_count(operation)
        if len(operands) != required_count:
            return f"操作 '{operation}' 需要 {required_count} 个操作数，但提供了 {len(operands)} 个"
        
        # 精度参数验证
        precision = kwargs.get('precision', 2)
        if not isinstance(precision, int) or precision < 0 or precision > 10:
            return "precision 必须是0-10之间的整数"
        
        # 特殊情况验证
        return await self._validate_special_cases(operation, operands)
    
    @tool_timer
    async def execute(self, **kwargs) -> ToolResult:
        """
        异步执行计算
        
        💡 对比TypeScript:
        @toolTimer
        async execute(params: any): Promise<ToolResult> {
            try {
                const { operation, operands, precision = 2, use_decimal = false } = params;
                
                // 获取操作函数
                const operationFunc = this.supportedOperations.get(operation);
                if (!operationFunc) {
                    return ToolResult.error(`操作 ${operation} 未实现`);
                }
                
                // 执行计算
                let result: number;
                if (use_decimal) {
                    result = await this.executeWithDecimal(operationFunc, operands);
                } else {
                    result = await operationFunc(...operands);
                }
                
                // 格式化结果
                const formattedResult = this.formatResult(result, precision);
                
                // 构建元数据
                const metadata = {
                    operation,
                    operands,
                    precision,
                    use_decimal,
                    raw_result: result
                };
                
                return ToolResult.success(formattedResult, metadata);
                
            } catch (error) {
                return ToolResult.error(`计算错误: ${error.message}`);
            }
        }
        
        学习要点：
        - 异步方法的实现
        - 装饰器的使用
        - 错误处理的完整性
        - 结果格式化的处理
        - 元数据的构建
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        try:
            operation = kwargs['operation']
            operands = kwargs['operands']
            precision = kwargs.get('precision', 2)
            use_decimal = kwargs.get('use_decimal', False)
            
            # 获取操作函数
            operation_func = self.supported_operations[operation]
            
            # 模拟异步计算（对于复杂运算可能需要时间）
            if operation in ['factorial', 'power'] and operands[0] > 1000:
                await asyncio.sleep(0.1)  # 模拟复杂计算的延迟
            
            # 执行计算
            if use_decimal:
                result = await self._execute_with_decimal(operation_func, operands)
            else:
                result = await operation_func(*operands)
            
            # 格式化结果
            formatted_result = self._format_result(result, precision)
            
            # 构建元数据
            metadata = {
                'operation': operation,
                'operands': operands,
                'precision': precision,
                'use_decimal': use_decimal,
                'raw_result': float(result) if isinstance(result, Decimal) else result,
                'formatted_result': formatted_result
            }
            
            return ToolResult.success(
                content=formatted_result,
                metadata=metadata
            )
            
        except ZeroDivisionError:
            return ToolResult.error("数学错误：除数不能为零")
        
        except ValueError as e:
            return ToolResult.error(f"数值错误：{str(e)}")
        
        except OverflowError:
            return ToolResult.error("数学错误：结果溢出")
        
        except Exception as e:
            return ToolResult.error(f"计算异常：{str(e)}")
    
    # 数学运算方法
    async def _add(self, *operands) -> float:
        """加法运算"""
        return sum(operands)
    
    async def _subtract(self, a: float, b: float) -> float:
        """减法运算"""
        return a - b
    
    async def _multiply(self, *operands) -> float:
        """乘法运算"""
        result = 1
        for operand in operands:
            result *= operand
        return result
    
    async def _divide(self, a: float, b: float) -> float:
        """除法运算"""
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return a / b
    
    async def _power(self, a: float, b: float) -> float:
        """幂运算"""
        try:
            return math.pow(a, b)
        except OverflowError:
            raise OverflowError("幂运算结果溢出")
    
    async def _sqrt(self, a: float) -> float:
        """平方根运算"""
        if a < 0:
            raise ValueError("不能计算负数的平方根")
        return math.sqrt(a)
    
    async def _factorial(self, a: float) -> float:
        """阶乘运算"""
        if a < 0:
            raise ValueError("阶乘不能计算负数")
        if not float(a).is_integer():
            raise ValueError("阶乘只能计算整数")
        if a > 170:  # 防止溢出
            raise OverflowError("阶乘输入过大，会导致溢出")
        
        return float(math.factorial(int(a)))
    
    async def _sin(self, a: float) -> float:
        """正弦函数"""
        return math.sin(a)
    
    async def _cos(self, a: float) -> float:
        """余弦函数"""
        return math.cos(a)
    
    async def _tan(self, a: float) -> float:
        """正切函数"""
        return math.tan(a)
    
    async def _log(self, a: float) -> float:
        """常用对数（以10为底）"""
        if a <= 0:
            raise ValueError("对数的真数必须大于0")
        return math.log10(a)
    
    async def _ln(self, a: float) -> float:
        """自然对数（以e为底）"""
        if a <= 0:
            raise ValueError("对数的真数必须大于0")
        return math.log(a)
    
    async def _abs(self, a: float) -> float:
        """绝对值"""
        return abs(a)
    
    async def _round(self, a: float) -> float:
        """四舍五入"""
        return round(a)
    
    async def _ceil(self, a: float) -> float:
        """向上取整"""
        return math.ceil(a)
    
    async def _floor(self, a: float) -> float:
        """向下取整"""
        return math.floor(a)
    
    def _get_required_operand_count(self, operation: str) -> int:
        """
        获取操作所需的操作数数量
        
        学习要点：
        - 操作映射的设计
        - 参数数量的验证
        - 字典查找的使用
        
        Args:
            operation: 操作名称
            
        Returns:
            int: 所需操作数数量
        """
        operand_counts = {
            'add': -1,  # -1 表示可变数量（至少1个）
            'subtract': 2,
            'multiply': -1,  # 可变数量
            'divide': 2,
            'power': 2,
            'sqrt': 1,
            'factorial': 1,
            'sin': 1,
            'cos': 1,
            'tan': 1,
            'log': 1,
            'ln': 1,
            'abs': 1,
            'round': 1,
            'ceil': 1,
            'floor': 1
        }
        
        count = operand_counts.get(operation, 1)
        return 1 if count == -1 else count  # 对于可变数量，至少需要1个
    
    async def _validate_special_cases(self, operation: str, operands: List[float]) -> Union[bool, str]:
        """
        验证特殊情况
        
        学习要点：
        - 特殊情况的识别和处理
        - 异步验证的实现
        - 业务逻辑的验证
        
        Args:
            operation: 操作名称
            operands: 操作数列表
            
        Returns:
            Union[bool, str]: 验证结果
        """
        # 除法验证
        if operation == 'divide' and operands[1] == 0:
            return "除数不能为零"
        
        # 平方根验证
        if operation == 'sqrt' and operands[0] < 0:
            return "不能计算负数的平方根"
        
        # 阶乘验证
        if operation == 'factorial':
            if operands[0] < 0:
                return "阶乘不能计算负数"
            if not float(operands[0]).is_integer():
                return "阶乘只能计算整数"
            if operands[0] > 170:
                return "阶乘输入过大（>170），会导致溢出"
        
        # 对数验证
        if operation in ['log', 'ln'] and operands[0] <= 0:
            return "对数的真数必须大于0"
        
        # 幂运算验证
        if operation == 'power':
            if operands[0] == 0 and operands[1] < 0:
                return "0不能进行负数次幂运算"
            if abs(operands[0]) > 1000 and operands[1] > 10:
                return "幂运算可能导致溢出"
        
        return True
    
    async def _execute_with_decimal(self, operation_func, operands: List[float]) -> Decimal:
        """
        使用高精度小数执行计算
        
        学习要点：
        - Decimal类的使用
        - 高精度计算的实现
        - 类型转换的处理
        
        Args:
            operation_func: 操作函数
            operands: 操作数列表
            
        Returns:
            Decimal: 高精度计算结果
        """
        try:
            # 转换为Decimal类型
            decimal_operands = [Decimal(str(op)) for op in operands]
            
            # 执行计算（注意：这里需要适配Decimal类型）
            # 简化实现，实际应该为每个操作提供Decimal版本
            result = await operation_func(*operands)
            return Decimal(str(result))
            
        except InvalidOperation as e:
            raise ValueError(f"高精度计算错误: {str(e)}")
    
    def _format_result(self, result: Union[float, Decimal], precision: int) -> str:
        """
        格式化计算结果
        
        学习要点：
        - 数值格式化的处理
        - 精度控制的实现
        - 字符串格式化技巧
        
        Args:
            result: 计算结果
            precision: 精度（小数位数）
            
        Returns:
            str: 格式化后的结果
        """
        if isinstance(result, Decimal):
            return f"{result:.{precision}f}"
        
        # 处理整数结果
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        
        # 处理小数结果
        return f"{result:.{precision}f}".rstrip('0').rstrip('.')


# 测试代码
if __name__ == "__main__":
    """
    测试异步计算器工具
    
    学习要点：
    - 异步工具的测试方法
    - 各种运算的测试用例
    - 错误情况的测试
    """
    
    async def test_async_calculator():
        """测试异步计算器"""
        print("🧪 测试异步计算器工具")
        print("=" * 40)
        
        calculator = AsyncCalculatorTool()
        
        # 测试用例
        test_cases = [
            # 基础运算
            {"operation": "add", "operands": [10, 20, 30], "expected": "60"},
            {"operation": "subtract", "operands": [100, 25], "expected": "75"},
            {"operation": "multiply", "operands": [6, 7], "expected": "42"},
            {"operation": "divide", "operands": [84, 12], "expected": "7"},
            
            # 高级运算
            {"operation": "power", "operands": [2, 8], "expected": "256"},
            {"operation": "sqrt", "operands": [16], "expected": "4"},
            {"operation": "factorial", "operands": [5], "expected": "120"},
            
            # 三角函数
            {"operation": "sin", "operands": [0], "expected": "0"},
            {"operation": "cos", "operands": [0], "expected": "1"},
            
            # 对数函数
            {"operation": "log", "operands": [100], "expected": "2"},
            {"operation": "ln", "operands": [math.e], "expected": "1"},
            
            # 其他函数
            {"operation": "abs", "operands": [-42], "expected": "42"},
            {"operation": "round", "operands": [3.7], "expected": "4"},
            {"operation": "ceil", "operands": [3.2], "expected": "4"},
            {"operation": "floor", "operands": [3.8], "expected": "3"}
        ]
        
        print("\n1. 测试基础运算:")
        for i, test_case in enumerate(test_cases[:4]):
            result = await calculator.execute_with_timeout(**test_case)
            status = "✅" if result.is_success() else "❌"
            print(f"  {status} {test_case['operation']}: {result.content}")
        
        print("\n2. 测试高级运算:")
        for i, test_case in enumerate(test_cases[4:7]):
            result = await calculator.execute_with_timeout(**test_case)
            status = "✅" if result.is_success() else "❌"
            print(f"  {status} {test_case['operation']}: {result.content}")
        
        print("\n3. 测试数学函数:")
        for i, test_case in enumerate(test_cases[7:]):
            result = await calculator.execute_with_timeout(**test_case)
            status = "✅" if result.is_success() else "❌"
            print(f"  {status} {test_case['operation']}: {result.content}")
        
        # 测试错误情况
        print("\n4. 测试错误处理:")
        error_cases = [
            {"operation": "divide", "operands": [10, 0], "expected_error": "除数不能为零"},
            {"operation": "sqrt", "operands": [-4], "expected_error": "负数的平方根"},
            {"operation": "factorial", "operands": [-1], "expected_error": "阶乘不能计算负数"},
            {"operation": "log", "operands": [0], "expected_error": "对数的真数必须大于0"}
        ]
        
        for error_case in error_cases:
            result = await calculator.execute_with_timeout(**error_case)
            status = "✅" if not result.is_success() else "❌"
            print(f"  {status} 错误处理 - {error_case['operation']}: {result.error_message}")
        
        # 测试输入验证
        print("\n5. 测试输入验证:")
        validation_cases = [
            {"operation": "invalid_op", "operands": [1, 2]},
            {"operation": "add", "operands": []},
            {"operation": "divide", "operands": [1]},  # 缺少操作数
            {"operation": "add", "operands": ["not_a_number", 2]}
        ]
        
        for validation_case in validation_cases:
            validation_result = await calculator.validate_input(**validation_case)
            status = "✅" if validation_result is not True else "❌"
            print(f"  {status} 验证失败: {validation_result}")
        
        # 显示工具统计
        print("\n6. 工具统计:")
        stats = calculator.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ 异步计算器工具测试完成！")
    
    # 运行测试
    asyncio.run(test_async_calculator())