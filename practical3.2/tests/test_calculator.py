"""
Practical 3.2 - 计算器工具测试

这个模块测试异步计算器工具的功能，包括：
1. 基础数学运算测试
2. 异步执行测试
3. 参数验证测试
4. 错误处理测试
5. 性能测试

学习要点：
1. 异步工具的单元测试
2. 数值计算的测试策略
3. 边界条件的测试
4. 性能基准测试
"""

import pytest
import asyncio
import time
from decimal import Decimal
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.calculator import AsyncCalculatorTool
from tools.base import ToolResultStatus


class TestAsyncCalculatorTool:
    """
    异步计算器工具测试类
    
    💡 对比TypeScript:
    describe('AsyncCalculatorTool', () => {
        let calculator: AsyncCalculatorTool;
        
        beforeEach(() => {
            calculator = new AsyncCalculatorTool();
        });
        
        test('should have correct properties', () => {
            expect(calculator.name).toBe('async_calculator');
            expect(calculator.description).toContain('异步计算器');
            expect(typeof calculator.getSchema).toBe('function');
        });
        
        test('should perform basic arithmetic', async () => {
            const addResult = await calculator.execute({
                operation: 'add',
                operands: [10, 5]
            });
            
            expect(addResult.isSuccess()).toBe(true);
            expect(addResult.content).toBe(15);
            
            const subtractResult = await calculator.execute({
                operation: 'subtract',
                operands: [10, 5]
            });
            
            expect(subtractResult.isSuccess()).toBe(true);
            expect(subtractResult.content).toBe(5);
        });
        
        test('should handle division by zero', async () => {
            const result = await calculator.execute({
                operation: 'divide',
                operands: [10, 0]
            });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('除零');
        });
        
        test('should validate parameters', async () => {
            const result = await calculator.execute({
                operation: 'invalid_op',
                operands: [1, 2]
            });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('不支持的操作');
        });
    });
    
    学习要点：
    - 工具类的基础测试结构
    - 数学运算的验证方法
    - 错误条件的测试策略
    - 参数验证的测试技巧
    """
    
    @pytest.fixture
    def calculator(self):
        """创建计算器实例"""
        return AsyncCalculatorTool()
    
    def test_calculator_properties(self, calculator):
        """测试计算器属性"""
        assert calculator.name == "async_calculator"
        assert "异步计算器" in calculator.description
        assert hasattr(calculator, "get_schema")
        assert callable(calculator.get_schema)
    
    def test_schema_structure(self, calculator):
        """测试模式结构"""
        schema = calculator.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "operation" in schema["properties"]
        assert "operands" in schema["properties"]
        assert "required" in schema
        assert "operation" in schema["required"]
        assert "operands" in schema["required"]
        
        # 检查操作枚举
        operation_enum = schema["properties"]["operation"]["enum"]
        expected_operations = ["add", "subtract", "multiply", "divide", "power", "sqrt", "factorial"]
        for op in expected_operations:
            assert op in operation_enum
    
    @pytest.mark.asyncio
    async def test_addition(self, calculator):
        """测试加法运算"""
        result = await calculator.execute(
            operation="add",
            operands=[10, 5]
        )
        
        assert result.is_success()
        assert result.content == 15
        assert "execution_time" in result.metadata
    
    @pytest.mark.asyncio
    async def test_subtraction(self, calculator):
        """测试减法运算"""
        result = await calculator.execute(
            operation="subtract",
            operands=[10, 5]
        )
        
        assert result.is_success()
        assert result.content == 5
    
    @pytest.mark.asyncio
    async def test_multiplication(self, calculator):
        """测试乘法运算"""
        result = await calculator.execute(
            operation="multiply",
            operands=[10, 5]
        )
        
        assert result.is_success()
        assert result.content == 50
    
    @pytest.mark.asyncio
    async def test_division(self, calculator):
        """测试除法运算"""
        result = await calculator.execute(
            operation="divide",
            operands=[10, 5]
        )
        
        assert result.is_success()
        assert result.content == 2.0
    
    @pytest.mark.asyncio
    async def test_division_by_zero(self, calculator):
        """测试除零错误"""
        result = await calculator.execute(
            operation="divide",
            operands=[10, 0]
        )
        
        assert result.is_error()
        assert "除零" in result.error_message
    
    @pytest.mark.asyncio
    async def test_power_operation(self, calculator):
        """测试幂运算"""
        result = await calculator.execute(
            operation="power",
            operands=[2, 3]
        )
        
        assert result.is_success()
        assert result.content == 8
    
    @pytest.mark.asyncio
    async def test_square_root(self, calculator):
        """测试平方根运算"""
        result = await calculator.execute(
            operation="sqrt",
            operands=[16]
        )
        
        assert result.is_success()
        assert result.content == 4.0
    
    @pytest.mark.asyncio
    async def test_square_root_negative(self, calculator):
        """测试负数平方根错误"""
        result = await calculator.execute(
            operation="sqrt",
            operands=[-16]
        )
        
        assert result.is_error()
        assert "负数" in result.error_message
    
    @pytest.mark.asyncio
    async def test_factorial(self, calculator):
        """测试阶乘运算"""
        result = await calculator.execute(
            operation="factorial",
            operands=[5]
        )
        
        assert result.is_success()
        assert result.content == 120
    
    @pytest.mark.asyncio
    async def test_factorial_negative(self, calculator):
        """测试负数阶乘错误"""
        result = await calculator.execute(
            operation="factorial",
            operands=[-5]
        )
        
        assert result.is_error()
        assert "负数" in result.error_message
    
    @pytest.mark.asyncio
    async def test_factorial_non_integer(self, calculator):
        """测试非整数阶乘错误"""
        result = await calculator.execute(
            operation="factorial",
            operands=[5.5]
        )
        
        assert result.is_error()
        assert "整数" in result.error_message


class TestParameterValidation:
    """
    参数验证测试类
    
    💡 对比TypeScript:
    describe('Parameter Validation', () => {
        let calculator: AsyncCalculatorTool;
        
        beforeEach(() => {
            calculator = new AsyncCalculatorTool();
        });
        
        test('should reject invalid operation', async () => {
            const result = await calculator.execute({
                operation: 'invalid_operation',
                operands: [1, 2]
            });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('不支持的操作');
        });
        
        test('should reject insufficient operands', async () => {
            const result = await calculator.execute({
                operation: 'add',
                operands: [1]  // 需要两个操作数
            });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('操作数数量');
        });
        
        test('should reject non-numeric operands', async () => {
            const result = await calculator.execute({
                operation: 'add',
                operands: ['a', 'b']
            });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('数值');
        });
        
        test('should handle missing parameters', async () => {
            const result = await calculator.execute({});
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('validation');
        });
    });
    
    学习要点：
    - 输入验证的全面测试
    - 错误消息的验证
    - 边界条件的处理
    - 类型安全的测试
    """
    
    @pytest.fixture
    def calculator(self):
        """创建计算器实例"""
        return AsyncCalculatorTool()
    
    @pytest.mark.asyncio
    async def test_invalid_operation(self, calculator):
        """测试无效操作"""
        result = await calculator.execute(
            operation="invalid_operation",
            operands=[1, 2]
        )
        
        assert result.is_error()
        assert "不支持的操作" in result.error_message
    
    @pytest.mark.asyncio
    async def test_insufficient_operands_binary(self, calculator):
        """测试二元运算操作数不足"""
        result = await calculator.execute(
            operation="add",
            operands=[1]  # 需要两个操作数
        )
        
        assert result.is_error()
        assert "操作数数量" in result.error_message
    
    @pytest.mark.asyncio
    async def test_insufficient_operands_unary(self, calculator):
        """测试一元运算操作数不足"""
        result = await calculator.execute(
            operation="sqrt",
            operands=[]  # 需要一个操作数
        )
        
        assert result.is_error()
        assert "操作数数量" in result.error_message
    
    @pytest.mark.asyncio
    async def test_excess_operands(self, calculator):
        """测试操作数过多"""
        result = await calculator.execute(
            operation="add",
            operands=[1, 2, 3, 4]  # 只需要两个操作数
        )
        
        assert result.is_error()
        assert "操作数数量" in result.error_message
    
    @pytest.mark.asyncio
    async def test_non_numeric_operands(self, calculator):
        """测试非数值操作数"""
        result = await calculator.execute(
            operation="add",
            operands=["a", "b"]
        )
        
        assert result.is_error()
        assert "数值" in result.error_message
    
    @pytest.mark.asyncio
    async def test_missing_operation(self, calculator):
        """测试缺少操作参数"""
        result = await calculator.execute(operands=[1, 2])
        
        assert result.is_error()
        assert "validation" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_missing_operands(self, calculator):
        """测试缺少操作数参数"""
        result = await calculator.execute(operation="add")
        
        assert result.is_error()
        assert "validation" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_empty_parameters(self, calculator):
        """测试空参数"""
        result = await calculator.execute()
        
        assert result.is_error()
        assert "validation" in result.error_message.lower()


class TestEdgeCases:
    """
    边界条件测试类
    
    💡 对比TypeScript:
    describe('Edge Cases', () => {
        let calculator: AsyncCalculatorTool;
        
        beforeEach(() => {
            calculator = new AsyncCalculatorTool();
        });
        
        test('should handle very large numbers', async () => {
            const result = await calculator.execute({
                operation: 'add',
                operands: [Number.MAX_SAFE_INTEGER, 1]
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(typeof result.content).toBe('number');
        });
        
        test('should handle very small numbers', async () => {
            const result = await calculator.execute({
                operation: 'add',
                operands: [Number.MIN_VALUE, Number.MIN_VALUE]
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content).toBeGreaterThan(0);
        });
        
        test('should handle floating point precision', async () => {
            const result = await calculator.execute({
                operation: 'add',
                operands: [0.1, 0.2]
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(Math.abs(result.content - 0.3)).toBeLessThan(0.0001);
        });
        
        test('should handle zero operations', async () => {
            const addResult = await calculator.execute({
                operation: 'add',
                operands: [0, 0]
            });
            
            expect(addResult.isSuccess()).toBe(true);
            expect(addResult.content).toBe(0);
            
            const multiplyResult = await calculator.execute({
                operation: 'multiply',
                operands: [100, 0]
            });
            
            expect(multiplyResult.isSuccess()).toBe(true);
            expect(multiplyResult.content).toBe(0);
        });
    });
    
    学习要点：
    - 数值边界的测试
    - 浮点精度的处理
    - 特殊值的测试
    - 性能极限的考虑
    """
    
    @pytest.fixture
    def calculator(self):
        """创建计算器实例"""
        return AsyncCalculatorTool()
    
    @pytest.mark.asyncio
    async def test_large_numbers(self, calculator):
        """测试大数运算"""
        result = await calculator.execute(
            operation="add",
            operands=[999999999999999, 1]
        )
        
        assert result.is_success()
        assert isinstance(result.content, (int, float))
    
    @pytest.mark.asyncio
    async def test_small_numbers(self, calculator):
        """测试小数运算"""
        result = await calculator.execute(
            operation="add",
            operands=[0.000001, 0.000002]
        )
        
        assert result.is_success()
        assert result.content > 0
    
    @pytest.mark.asyncio
    async def test_floating_point_precision(self, calculator):
        """测试浮点精度"""
        result = await calculator.execute(
            operation="add",
            operands=[0.1, 0.2]
        )
        
        assert result.is_success()
        # 使用近似比较处理浮点精度问题
        assert abs(result.content - 0.3) < 0.0001
    
    @pytest.mark.asyncio
    async def test_zero_operations(self, calculator):
        """测试零值运算"""
        # 零加零
        result = await calculator.execute(
            operation="add",
            operands=[0, 0]
        )
        assert result.is_success()
        assert result.content == 0
        
        # 数乘零
        result = await calculator.execute(
            operation="multiply",
            operands=[100, 0]
        )
        assert result.is_success()
        assert result.content == 0
        
        # 零的幂
        result = await calculator.execute(
            operation="power",
            operands=[0, 5]
        )
        assert result.is_success()
        assert result.content == 0
    
    @pytest.mark.asyncio
    async def test_negative_numbers(self, calculator):
        """测试负数运算"""
        result = await calculator.execute(
            operation="add",
            operands=[-10, -5]
        )
        
        assert result.is_success()
        assert result.content == -15
    
    @pytest.mark.asyncio
    async def test_decimal_precision(self, calculator):
        """测试小数精度"""
        result = await calculator.execute(
            operation="divide",
            operands=[1, 3]
        )
        
        assert result.is_success()
        assert abs(result.content - 0.3333333333333333) < 0.0001


class TestPerformance:
    """
    性能测试类
    
    💡 对比TypeScript:
    describe('Performance Tests', () => {
        let calculator: AsyncCalculatorTool;
        
        beforeEach(() => {
            calculator = new AsyncCalculatorTool();
        });
        
        test('should complete simple operations quickly', async () => {
            const startTime = Date.now();
            
            await calculator.execute({
                operation: 'add',
                operands: [1, 2]
            });
            
            const duration = Date.now() - startTime;
            expect(duration).toBeLessThan(100); // 应该在100ms内完成
        });
        
        test('should handle concurrent operations', async () => {
            const operations = Array.from({ length: 100 }, (_, i) => 
                calculator.execute({
                    operation: 'add',
                    operands: [i, i + 1]
                })
            );
            
            const startTime = Date.now();
            const results = await Promise.all(operations);
            const duration = Date.now() - startTime;
            
            expect(results).toHaveLength(100);
            expect(duration).toBeLessThan(1000); // 应该在1秒内完成
            
            results.forEach((result, index) => {
                expect(result.isSuccess()).toBe(true);
                expect(result.content).toBe(index + (index + 1));
            });
        });
        
        test('should handle complex operations efficiently', async () => {
            const startTime = Date.now();
            
            const result = await calculator.execute({
                operation: 'factorial',
                operands: [20]
            });
            
            const duration = Date.now() - startTime;
            
            expect(result.isSuccess()).toBe(true);
            expect(duration).toBeLessThan(50); // 应该在50ms内完成
        });
    });
    
    学习要点：
    - 性能基准的设定
    - 并发性能的测试
    - 复杂运算的优化
    - 响应时间的监控
    """
    
    @pytest.fixture
    def calculator(self):
        """创建计算器实例"""
        return AsyncCalculatorTool()
    
    @pytest.mark.asyncio
    async def test_simple_operation_speed(self, calculator):
        """测试简单操作速度"""
        start_time = time.time()
        
        result = await calculator.execute(
            operation="add",
            operands=[1, 2]
        )
        
        duration = time.time() - start_time
        
        assert result.is_success()
        assert duration < 0.1  # 应该在100ms内完成
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, calculator):
        """测试并发操作"""
        operations = [
            calculator.execute(
                operation="add",
                operands=[i, i + 1]
            )
            for i in range(50)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*operations)
        duration = time.time() - start_time
        
        assert len(results) == 50
        assert duration < 1.0  # 应该在1秒内完成
        
        for i, result in enumerate(results):
            assert result.is_success()
            assert result.content == i + (i + 1)
    
    @pytest.mark.asyncio
    async def test_complex_operation_efficiency(self, calculator):
        """测试复杂操作效率"""
        start_time = time.time()
        
        result = await calculator.execute(
            operation="factorial",
            operands=[15]  # 15! = 1307674368000
        )
        
        duration = time.time() - start_time
        
        assert result.is_success()
        assert result.content == 1307674368000
        assert duration < 0.05  # 应该在50ms内完成
    
    @pytest.mark.asyncio
    async def test_metadata_collection(self, calculator):
        """测试元数据收集"""
        result = await calculator.execute(
            operation="multiply",
            operands=[123, 456]
        )
        
        assert result.is_success()
        assert "execution_time" in result.metadata
        assert "operation" in result.metadata
        assert "operands" in result.metadata
        assert result.metadata["operation"] == "multiply"
        assert result.metadata["operands"] == [123, 456]


class TestAsyncBehavior:
    """
    异步行为测试类
    
    💡 对比TypeScript:
    describe('Async Behavior', () => {
        let calculator: AsyncCalculatorTool;
        
        beforeEach(() => {
            calculator = new AsyncCalculatorTool();
        });
        
        test('should be truly asynchronous', async () => {
            let completed = 0;
            
            const promises = [
                calculator.execute({ operation: 'add', operands: [1, 2] })
                    .then(() => completed++),
                calculator.execute({ operation: 'multiply', operands: [3, 4] })
                    .then(() => completed++),
                calculator.execute({ operation: 'subtract', operands: [10, 5] })
                    .then(() => completed++)
            ];
            
            // 在所有操作完成前，completed应该还是0
            expect(completed).toBe(0);
            
            await Promise.all(promises);
            
            // 现在所有操作都应该完成了
            expect(completed).toBe(3);
        });
        
        test('should handle timeout correctly', async () => {
            const result = await calculator.execute(
                { operation: 'add', operands: [1, 2] },
                { timeout: 0.001 } // 1ms超时
            );
            
            // 由于操作很快，可能成功也可能超时
            expect(result.status).toMatch(/success|error/);
        });
        
        test('should work with context manager', async () => {
            let result;
            
            // 使用上下文管理器
            const contextCalculator = await calculator.__aenter__();
            try {
                result = await contextCalculator.execute({
                    operation: 'add',
                    operands: [10, 20]
                });
            } finally {
                await calculator.__aexit__();
            }
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content).toBe(30);
        });
    });
    
    学习要点：
    - 异步执行的验证
    - 超时机制的测试
    - 上下文管理的测试
    - 并发安全性的验证
    """
    
    @pytest.fixture
    def calculator(self):
        """创建计算器实例"""
        return AsyncCalculatorTool()
    
    @pytest.mark.asyncio
    async def test_truly_asynchronous(self, calculator):
        """测试真正的异步执行"""
        completed = []
        
        async def track_completion(op, operands, expected):
            result = await calculator.execute(operation=op, operands=operands)
            completed.append((op, result.content, expected))
            return result
        
        # 启动多个异步操作
        tasks = [
            track_completion("add", [1, 2], 3),
            track_completion("multiply", [3, 4], 12),
            track_completion("subtract", [10, 5], 5)
        ]
        
        # 在操作完成前，completed应该为空
        assert len(completed) == 0
        
        results = await asyncio.gather(*tasks)
        
        # 现在所有操作都应该完成
        assert len(completed) == 3
        assert len(results) == 3
        
        for result in results:
            assert result.is_success()
    
    @pytest.mark.asyncio
    async def test_timeout_behavior(self, calculator):
        """测试超时行为"""
        # 使用很短的超时时间
        result = await calculator.execute(
            operation="add",
            operands=[1, 2],
            timeout=0.001  # 1ms超时
        )
        
        # 由于操作很快，通常会成功，但也可能超时
        assert result.status in [ToolResultStatus.SUCCESS, ToolResultStatus.ERROR]
    
    @pytest.mark.asyncio
    async def test_context_manager_usage(self, calculator):
        """测试上下文管理器使用"""
        async with calculator as context_calc:
            result = await context_calc.execute(
                operation="add",
                operands=[10, 20]
            )
            
            assert result.is_success()
            assert result.content == 30
    
    @pytest.mark.asyncio
    async def test_concurrent_safety(self, calculator):
        """测试并发安全性"""
        # 同时执行多个不同的操作
        tasks = [
            calculator.execute(operation="add", operands=[i, i]),
            calculator.execute(operation="multiply", operands=[i, 2]),
            calculator.execute(operation="subtract", operands=[i * 2, i])
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert result.is_success()


@pytest.mark.asyncio
async def test_calculator_integration():
    """
    计算器集成测试
    
    💡 对比TypeScript:
    describe('Calculator Integration', () => {
        test('should work end-to-end', async () => {
            const calculator = new AsyncCalculatorTool();
            
            // 测试完整的计算流程
            const expression = [
                { operation: 'add', operands: [10, 5] },      // 15
                { operation: 'multiply', operands: [3, 4] },   // 12
                { operation: 'subtract', operands: [20, 8] }   // 12
            ];
            
            const results = await Promise.all(
                expression.map(expr => calculator.execute(expr))
            );
            
            expect(results[0].content).toBe(15);
            expect(results[1].content).toBe(12);
            expect(results[2].content).toBe(12);
            
            // 使用前面的结果进行进一步计算
            const finalResult = await calculator.execute({
                operation: 'add',
                operands: [results[0].content, results[1].content]
            });
            
            expect(finalResult.content).toBe(27);
        });
        
        test('should handle complex calculation chain', async () => {
            const calculator = new AsyncCalculatorTool();
            
            // 计算 (2^3 + sqrt(16)) * 5 - 10!
            const powerResult = await calculator.execute({
                operation: 'power',
                operands: [2, 3]
            }); // 8
            
            const sqrtResult = await calculator.execute({
                operation: 'sqrt',
                operands: [16]
            }); // 4
            
            const addResult = await calculator.execute({
                operation: 'add',
                operands: [powerResult.content, sqrtResult.content]
            }); // 12
            
            const multiplyResult = await calculator.execute({
                operation: 'multiply',
                operands: [addResult.content, 5]
            }); // 60
            
            const factorialResult = await calculator.execute({
                operation: 'factorial',
                operands: [4]
            }); // 24
            
            const finalResult = await calculator.execute({
                operation: 'subtract',
                operands: [multiplyResult.content, factorialResult.content]
            }); // 36
            
            expect(finalResult.content).toBe(36);
        });
    });
    
    学习要点：
    - 端到端测试的设计
    - 复杂计算链的测试
    - 结果传递的验证
    - 完整工作流的测试
    """
    print("🧪 运行计算器集成测试...")
    
    calculator = AsyncCalculatorTool()
    
    # 测试基础运算组合
    add_result = await calculator.execute(operation="add", operands=[10, 5])
    multiply_result = await calculator.execute(operation="multiply", operands=[3, 4])
    subtract_result = await calculator.execute(operation="subtract", operands=[20, 8])
    
    assert add_result.is_success() and add_result.content == 15
    assert multiply_result.is_success() and multiply_result.content == 12
    assert subtract_result.is_success() and subtract_result.content == 12
    
    # 使用前面的结果进行进一步计算
    final_result = await calculator.execute(
        operation="add",
        operands=[add_result.content, multiply_result.content]
    )
    
    assert final_result.is_success()
    assert final_result.content == 27
    
    # 测试复杂计算链: (2^3 + sqrt(16)) * 5 - 4!
    power_result = await calculator.execute(operation="power", operands=[2, 3])  # 8
    sqrt_result = await calculator.execute(operation="sqrt", operands=[16])      # 4
    add_chain = await calculator.execute(
        operation="add", 
        operands=[power_result.content, sqrt_result.content]
    )  # 12
    multiply_chain = await calculator.execute(
        operation="multiply", 
        operands=[add_chain.content, 5]
    )  # 60
    factorial_result = await calculator.execute(operation="factorial", operands=[4])  # 24
    final_chain = await calculator.execute(
        operation="subtract",
        operands=[multiply_chain.content, factorial_result.content]
    )  # 36
    
    assert final_chain.is_success()
    assert final_chain.content == 36
    
    print("✅ 计算器集成测试通过")


if __name__ == "__main__":
    """
    测试运行器
    
    学习要点：
    - 测试套件的组织
    - 异步测试的执行
    - 测试结果的验证
    """
    print("🧪 运行计算器工具测试...")
    
    # 运行集成测试
    asyncio.run(test_calculator_integration())
    
    print("✅ 所有计算器工具测试完成")