"""
异步计算器工具

这个模块实现了一个简化的异步计算器工具，支持基础数学运算。
专注于异步编程的核心概念，移除了复杂的数学运算和高级特性。

学习要点：
1. 异步工具的具体实现
2. 基础输入验证
3. 简单的数学运算处理
4. 错误处理的基础实践
"""

import asyncio
from typing import Dict, Any, Union

from .base import AsyncBaseTool, ToolResult


class AsyncCalculatorTool(AsyncBaseTool):
    """
    异步计算器工具
    
    💡 对比TypeScript:
    class AsyncCalculatorTool extends AsyncBaseTool {
        constructor() {
            super("async_calculator", "异步计算器工具", 10.0);
        }
        
        get schema(): object {
            return {
                type: "object",
                properties: {
                    operation: {
                        type: "string",
                        enum: ["add", "subtract", "multiply", "divide"],
                        description: "要执行的数学运算"
                    },
                    a: { type: "number", description: "第一个数" },
                    b: { type: "number", description: "第二个数" }
                },
                required: ["operation", "a", "b"]
            };
        }
        
        async validateInput(params: any): Promise<boolean | string> {
            const { operation, a, b } = params;
            
            if (!["add", "subtract", "multiply", "divide"].includes(operation)) {
                return "不支持的运算类型";
            }
            
            if (typeof a !== "number" || typeof b !== "number") {
                return "操作数必须是数字";
            }
            
            if (operation === "divide" && b === 0) {
                return "除数不能为零";
            }
            
            return true;
        }
        
        async execute(params: any): Promise<ToolResult> {
            const { operation, a, b } = params;
            
            // 模拟异步操作
            await new Promise(resolve => setTimeout(resolve, 100));
            
            let result: number;
            
            switch (operation) {
                case "add":
                    result = a + b;
                    break;
                case "subtract":
                    result = a - b;
                    break;
                case "multiply":
                    result = a * b;
                    break;
                case "divide":
                    result = a / b;
                    break;
                default:
                    return ToolResult.error(`不支持的运算: ${operation}`);
            }
            
            return ToolResult.success({
                operation,
                operands: [a, b],
                result,
                expression: `${a} ${operation} ${b} = ${result}`
            });
        }
    }
    
    学习要点：
    - 异步工具的完整实现
    - 基础业务逻辑的处理
    - 简单的数学运算实现
    - 错误处理的基础实践
    """
    
    def __init__(self):
        """
        初始化异步计算器工具
        
        学习要点：
        - 继承基类的正确方式
        - 工具属性的设置
        - 超时时间的合理配置
        """
        super().__init__(
            name="async_calculator",
            description="异步计算器工具，支持基础四则运算",
            timeout=10.0
        )
        
        # 支持的运算类型
        self.supported_operations = {
            "add": self._add,
            "subtract": self._subtract,
            "multiply": self._multiply,
            "divide": self._divide
        }
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        定义工具的输入参数模式
        
        学习要点：
        - JSON Schema 的基础使用
        - 枚举类型的定义
        - 必需参数的指定
        - 参数描述的重要性
        
        Returns:
            Dict[str, Any]: JSON Schema 格式的参数定义
        """
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "要执行的数学运算类型"
                },
                "a": {
                    "type": "number",
                    "description": "第一个操作数"
                },
                "b": {
                    "type": "number",
                    "description": "第二个操作数"
                }
            },
            "required": ["operation", "a", "b"]
        }
    
    async def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        验证输入参数
        
        学习要点：
        - 异步验证方法的实现
        - 参数存在性检查
        - 参数类型验证
        - 业务逻辑验证（如除零检查）
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            Union[bool, str]: True表示验证通过，字符串表示错误信息
        """
        # 调用基类的基础验证
        base_validation = await super().validate_input(**kwargs)
        if base_validation is not True:
            return base_validation
        
        operation = kwargs.get("operation")
        a = kwargs.get("a")
        b = kwargs.get("b")
        
        # 验证运算类型
        if operation not in self.supported_operations:
            return f"不支持的运算类型: {operation}。支持的运算: {list(self.supported_operations.keys())}"
        
        # 验证操作数类型
        if not isinstance(a, (int, float)):
            return "参数 'a' 必须是数字类型"
        
        if not isinstance(b, (int, float)):
            return "参数 'b' 必须是数字类型"
        
        # 特殊情况验证：除零检查
        if operation == "divide" and b == 0:
            return "除数不能为零"
        
        return True
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行计算操作
        
        学习要点：
        - 异步方法的实现
        - 参数提取和处理
        - 业务逻辑的执行
        - 结果的构建和返回
        - 异常处理的实现
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        try:
            operation = kwargs["operation"]
            a = kwargs["a"]
            b = kwargs["b"]
            
            # 模拟异步操作（实际场景中可能是数据库查询、网络请求等）
            await asyncio.sleep(0.1)
            
            # 获取对应的运算函数
            operation_func = self.supported_operations[operation]
            
            # 执行运算
            result = await operation_func(a, b)
            
            # 构建返回结果
            return ToolResult.success({
                "operation": operation,
                "operands": [a, b],
                "result": result,
                "expression": f"{a} {operation} {b} = {result}",
                "formatted": self._format_result(operation, a, b, result)
            })
            
        except ZeroDivisionError:
            return ToolResult.error("除数不能为零")
        except Exception as e:
            return ToolResult.error(f"计算过程中发生错误: {str(e)}")
    
    async def _add(self, a: float, b: float) -> float:
        """加法运算"""
        return a + b
    
    async def _subtract(self, a: float, b: float) -> float:
        """减法运算"""
        return a - b
    
    async def _multiply(self, a: float, b: float) -> float:
        """乘法运算"""
        return a * b
    
    async def _divide(self, a: float, b: float) -> float:
        """除法运算"""
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return a / b
    
    def _format_result(self, operation: str, a: float, b: float, result: float) -> str:
        """
        格式化计算结果
        
        学习要点：
        - 字符串格式化的使用
        - 运算符映射
        - 结果展示的优化
        
        Args:
            operation: 运算类型
            a: 第一个操作数
            b: 第二个操作数
            result: 计算结果
            
        Returns:
            str: 格式化后的结果字符串
        """
        operation_symbols = {
            "add": "+",
            "subtract": "-",
            "multiply": "×",
            "divide": "÷"
        }
        
        symbol = operation_symbols.get(operation, operation)
        
        # 格式化数字显示（去除不必要的小数点）
        def format_number(num):
            if isinstance(num, float) and num.is_integer():
                return str(int(num))
            return str(num)
        
        formatted_a = format_number(a)
        formatted_b = format_number(b)
        formatted_result = format_number(result)
        
        return f"{formatted_a} {symbol} {formatted_b} = {formatted_result}"


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_async_calculator():
        """
        测试异步计算器功能
        
        学习要点：
        - 异步测试的编写
        - 多种测试用例的设计
        - 错误情况的测试
        - 结果验证的方法
        """
        print("🧮 测试异步计算器工具")
        print("=" * 40)
        
        # 创建计算器实例
        calculator = AsyncCalculatorTool()
        print(f"工具信息: {calculator}")
        print(f"支持的运算: {list(calculator.supported_operations.keys())}")
        
        # 测试用例
        test_cases = [
            {"operation": "add", "a": 10, "b": 5, "expected": 15},
            {"operation": "subtract", "a": 10, "b": 3, "expected": 7},
            {"operation": "multiply", "a": 4, "b": 6, "expected": 24},
            {"operation": "divide", "a": 15, "b": 3, "expected": 5},
            {"operation": "divide", "a": 10, "b": 3, "expected": 3.3333333333333335},
        ]
        
        print("\n🧪 测试正常运算:")
        for i, test_case in enumerate(test_cases, 1):
            operation = test_case["operation"]
            a = test_case["a"]
            b = test_case["b"]
            expected = test_case["expected"]
            
            result = await calculator.execute_with_timeout(
                operation=operation, a=a, b=b
            )
            
            if result.is_success():
                actual = result.content["result"]
                formatted = result.content["formatted"]
                status = "✅" if abs(actual - expected) < 1e-10 else "❌"
                print(f"  {i}. {formatted} {status}")
                if abs(actual - expected) >= 1e-10:
                    print(f"     期望: {expected}, 实际: {actual}")
            else:
                print(f"  {i}. 错误: {result.error_message} ❌")
        
        # 测试错误情况
        print("\n🚫 测试错误情况:")
        
        error_cases = [
            {"operation": "divide", "a": 10, "b": 0, "description": "除零错误"},
            {"operation": "invalid", "a": 1, "b": 2, "description": "无效运算"},
            {"operation": "add", "a": "not_number", "b": 2, "description": "无效操作数类型"},
        ]
        
        for i, error_case in enumerate(error_cases, 1):
            try:
                # 先测试输入验证
                validation_result = await calculator.validate_input(**error_case)
                if validation_result is not True:
                    print(f"  {i}. {error_case['description']}: 输入验证失败 - {validation_result} ✅")
                    continue
                
                # 如果验证通过，测试执行
                result = await calculator.execute_with_timeout(**error_case)
                if result.is_error():
                    print(f"  {i}. {error_case['description']}: 执行失败 - {result.error_message} ✅")
                else:
                    print(f"  {i}. {error_case['description']}: 意外成功 ❌")
                    
            except Exception as e:
                print(f"  {i}. {error_case['description']}: 异常 - {str(e)} ✅")
        
        # 测试性能
        print("\n⚡ 测试执行性能:")
        import time
        
        start_time = time.time()
        tasks = []
        
        # 并发执行多个计算任务
        for i in range(10):
            task = calculator.execute_with_timeout(
                operation="multiply", a=i, b=i+1
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        successful_count = sum(1 for r in results if r.is_success())
        total_time = end_time - start_time
        
        print(f"  并发执行10个任务:")
        print(f"  - 成功: {successful_count}/10")
        print(f"  - 总时间: {total_time:.3f}秒")
        print(f"  - 平均时间: {total_time/10:.3f}秒/任务")
        
        print("\n✅ 异步计算器测试完成!")
    
    # 运行测试
    asyncio.run(test_async_calculator())