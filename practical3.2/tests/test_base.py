"""
Practical 3.2 - 基础组件测试

这个模块测试异步工具框架的基础组件，包括：
1. AsyncBaseTool的抽象基类测试
2. ToolResult的数据模型测试
3. 装饰器功能的测试
4. 异步上下文管理器的测试

学习要点：
1. 异步测试的编写方法
2. 抽象基类的测试策略
3. 装饰器测试的技巧
4. 异常处理的测试
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base import AsyncBaseTool, ToolResult, ToolResultStatus, tool_timer


class MockAsyncTool(AsyncBaseTool):
    """
    模拟异步工具类
    
    💡 对比TypeScript:
    class MockAsyncTool extends AsyncBaseTool {
        constructor() {
            super();
            this.name = 'mock_tool';
            this.description = 'A mock tool for testing';
        }
        
        getSchema(): any {
            return {
                type: 'object',
                properties: {
                    value: { type: 'string' },
                    delay: { type: 'number', default: 0 }
                },
                required: ['value']
            };
        }
        
        async executeAsync(params: any): Promise<ToolResult> {
            if (params.delay) {
                await new Promise(resolve => setTimeout(resolve, params.delay));
            }
            
            if (params.value === 'error') {
                throw new Error('Mock error');
            }
            
            return new ToolResult({
                status: ToolResultStatus.SUCCESS,
                content: `Mock result: ${params.value}`,
                metadata: { processed_at: new Date().toISOString() }
            });
        }
    }
    
    学习要点：
    - 测试用模拟类的实现
    - 异步方法的模拟
    - 错误条件的模拟
    - 测试数据的生成
    """
    
    def __init__(self):
        super().__init__()
        self.name = "mock_tool"
        self.description = "A mock tool for testing"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
                "delay": {"type": "number", "default": 0}
            },
            "required": ["value"]
        }
    
    async def _execute_async(self, **params) -> ToolResult:
        # 模拟延迟
        if params.get("delay", 0) > 0:
            await asyncio.sleep(params["delay"] / 1000)  # 转换为秒
        
        # 模拟错误
        if params.get("value") == "error":
            raise ValueError("Mock error")
        
        return ToolResult(
            status=ToolResultStatus.SUCCESS,
            content=f"Mock result: {params['value']}",
            metadata={"processed_at": time.time()}
        )


class TestToolResult:
    """
    ToolResult测试类
    
    💡 对比TypeScript:
    describe('ToolResult', () => {
        test('should create successful result', () => {
            const result = new ToolResult({
                status: ToolResultStatus.SUCCESS,
                content: 'test content',
                metadata: { key: 'value' }
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.isError()).toBe(false);
            expect(result.content).toBe('test content');
            expect(result.metadata).toEqual({ key: 'value' });
        });
        
        test('should create error result', () => {
            const result = new ToolResult({
                status: ToolResultStatus.ERROR,
                errorMessage: 'test error',
                metadata: { error_code: 500 }
            });
            
            expect(result.isSuccess()).toBe(false);
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toBe('test error');
            expect(result.metadata).toEqual({ error_code: 500 });
        });
        
        test('should convert to dictionary', () => {
            const result = new ToolResult({
                status: ToolResultStatus.SUCCESS,
                content: 'test',
                metadata: { key: 'value' }
            });
            
            const dict = result.toDict();
            expect(dict).toEqual({
                status: 'success',
                content: 'test',
                error_message: null,
                metadata: { key: 'value' },
                execution_time: expect.any(Number)
            });
        });
    });
    
    学习要点：
    - 数据模型的单元测试
    - 状态检查方法的测试
    - 序列化方法的测试
    - 边界条件的测试
    """
    
    def test_successful_result(self):
        """测试成功结果"""
        result = ToolResult(
            status=ToolResultStatus.SUCCESS,
            content="test content",
            metadata={"key": "value"}
        )
        
        assert result.is_success()
        assert not result.is_error()
        assert result.content == "test content"
        assert result.metadata == {"key": "value"}
        assert result.error_message is None
    
    def test_error_result(self):
        """测试错误结果"""
        result = ToolResult(
            status=ToolResultStatus.ERROR,
            error_message="test error",
            metadata={"error_code": 500}
        )
        
        assert not result.is_success()
        assert result.is_error()
        assert result.error_message == "test error"
        assert result.metadata == {"error_code": 500}
        assert result.content is None
    
    def test_to_dict(self):
        """测试字典转换"""
        result = ToolResult(
            status=ToolResultStatus.SUCCESS,
            content="test",
            metadata={"key": "value"}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] == "success"
        assert result_dict["content"] == "test"
        assert result_dict["error_message"] is None
        assert result_dict["metadata"] == {"key": "value"}
        assert "execution_time" in result_dict
    
    def test_pending_result(self):
        """测试待处理结果"""
        result = ToolResult(
            status=ToolResultStatus.PENDING,
            content="processing..."
        )
        
        assert not result.is_success()
        assert not result.is_error()
        assert result.status == ToolResultStatus.PENDING


class TestAsyncBaseTool:
    """
    AsyncBaseTool测试类
    
    💡 对比TypeScript:
    describe('AsyncBaseTool', () => {
        let tool: MockAsyncTool;
        
        beforeEach(() => {
            tool = new MockAsyncTool();
        });
        
        test('should have required properties', () => {
            expect(tool.name).toBe('mock_tool');
            expect(tool.description).toBe('A mock tool for testing');
            expect(typeof tool.getSchema).toBe('function');
        });
        
        test('should execute successfully', async () => {
            const result = await tool.execute({ value: 'test' });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content).toBe('Mock result: test');
            expect(result.metadata).toHaveProperty('processed_at');
        });
        
        test('should handle errors', async () => {
            const result = await tool.execute({ value: 'error' });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('Mock error');
        });
        
        test('should respect timeout', async () => {
            const startTime = Date.now();
            
            const result = await tool.execute(
                { value: 'test', delay: 2000 },
                { timeout: 1000 }
            );
            
            const duration = Date.now() - startTime;
            expect(duration).toBeLessThan(1500);
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('timeout');
        });
        
        test('should validate parameters', async () => {
            const result = await tool.execute({});
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('validation');
        });
    });
    
    学习要点：
    - 异步方法的测试
    - 错误处理的测试
    - 超时机制的测试
    - 参数验证的测试
    """
    
    @pytest.fixture
    def tool(self):
        """创建测试工具实例"""
        return MockAsyncTool()
    
    def test_tool_properties(self, tool):
        """测试工具属性"""
        assert tool.name == "mock_tool"
        assert tool.description == "A mock tool for testing"
        assert hasattr(tool, "get_schema")
        assert callable(tool.get_schema)
    
    def test_schema(self, tool):
        """测试模式定义"""
        schema = tool.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "value" in schema["properties"]
        assert "required" in schema
        assert "value" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, tool):
        """测试成功执行"""
        result = await tool.execute(value="test")
        
        assert result.is_success()
        assert result.content == "Mock result: test"
        assert "processed_at" in result.metadata
    
    @pytest.mark.asyncio
    async def test_error_handling(self, tool):
        """测试错误处理"""
        result = await tool.execute(value="error")
        
        assert result.is_error()
        assert "Mock error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_timeout(self, tool):
        """测试超时机制"""
        start_time = time.time()
        
        result = await tool.execute(
            value="test",
            delay=2000,
            timeout=1.0  # 1秒超时
        )
        
        duration = time.time() - start_time
        assert duration < 1.5  # 应该在1.5秒内完成
        assert result.is_error()
        assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, tool):
        """测试参数验证"""
        # 缺少必需参数
        result = await tool.execute()
        
        assert result.is_error()
        assert "validation" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, tool):
        """测试上下文管理器"""
        async with tool:
            result = await tool.execute(value="context_test")
            assert result.is_success()
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, tool):
        """测试并发执行"""
        tasks = [
            tool.execute(value=f"test_{i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result.is_success()
            assert result.content == f"Mock result: test_{i}"


class TestToolTimer:
    """
    工具计时器装饰器测试类
    
    💡 对比TypeScript:
    describe('toolTimer', () => {
        test('should measure execution time', async () => {
            const mockFn = jest.fn().mockImplementation(async () => {
                await new Promise(resolve => setTimeout(resolve, 100));
                return 'result';
            });
            
            const timedFn = toolTimer(mockFn);
            const result = await timedFn();
            
            expect(mockFn).toHaveBeenCalled();
            expect(result).toBe('result');
            // 验证时间测量逻辑
        });
        
        test('should handle errors', async () => {
            const mockFn = jest.fn().mockRejectedValue(new Error('test error'));
            const timedFn = toolTimer(mockFn);
            
            await expect(timedFn()).rejects.toThrow('test error');
            expect(mockFn).toHaveBeenCalled();
        });
        
        test('should preserve function metadata', () => {
            const originalFn = async function testFunction() { return 'test'; };
            const timedFn = toolTimer(originalFn);
            
            expect(timedFn.name).toBe('testFunction');
        });
    });
    
    学习要点：
    - 装饰器的测试方法
    - 时间测量的验证
    - 错误传播的测试
    - 元数据保持的测试
    """
    
    @pytest.mark.asyncio
    async def test_timer_measures_time(self):
        """测试计时器测量时间"""
        @tool_timer
        async def slow_function():
            await asyncio.sleep(0.1)  # 100ms延迟
            return "result"
        
        result = await slow_function()
        assert result == "result"
    
    @pytest.mark.asyncio
    async def test_timer_handles_errors(self):
        """测试计时器处理错误"""
        @tool_timer
        async def error_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            await error_function()
    
    @pytest.mark.asyncio
    async def test_timer_with_parameters(self):
        """测试带参数的计时器"""
        @tool_timer
        async def parameterized_function(x, y):
            await asyncio.sleep(0.05)
            return x + y
        
        result = await parameterized_function(1, 2)
        assert result == 3
    
    def test_timer_preserves_metadata(self):
        """测试计时器保持元数据"""
        @tool_timer
        async def test_function():
            """Test function docstring"""
            return "test"
        
        assert test_function.__name__ == "test_function"
        assert "Test function docstring" in test_function.__doc__


class TestAsyncContext:
    """
    异步上下文测试类
    
    💡 对比TypeScript:
    describe('AsyncContext', () => {
        test('should handle async context properly', async () => {
            const tool = new MockAsyncTool();
            let enterCalled = false;
            let exitCalled = false;
            
            // 模拟上下文管理器
            tool.__aenter__ = jest.fn().mockImplementation(async () => {
                enterCalled = true;
                return tool;
            });
            
            tool.__aexit__ = jest.fn().mockImplementation(async () => {
                exitCalled = true;
            });
            
            // 使用上下文管理器
            const result = await (async () => {
                const contextTool = await tool.__aenter__();
                try {
                    return await contextTool.execute({ value: 'test' });
                } finally {
                    await tool.__aexit__();
                }
            })();
            
            expect(enterCalled).toBe(true);
            expect(exitCalled).toBe(true);
            expect(result.isSuccess()).toBe(true);
        });
        
        test('should cleanup on exception', async () => {
            const tool = new MockAsyncTool();
            let exitCalled = false;
            
            tool.__aexit__ = jest.fn().mockImplementation(async () => {
                exitCalled = true;
            });
            
            try {
                const contextTool = await tool.__aenter__();
                try {
                    throw new Error('test error');
                } finally {
                    await tool.__aexit__();
                }
            } catch (error) {
                expect(error.message).toBe('test error');
            }
            
            expect(exitCalled).toBe(true);
        });
    });
    
    学习要点：
    - 异步上下文管理器的测试
    - 资源清理的验证
    - 异常情况下的清理测试
    - 上下文协议的实现测试
    """
    
    @pytest.mark.asyncio
    async def test_context_manager_protocol(self):
        """测试上下文管理器协议"""
        tool = MockAsyncTool()
        
        # 测试 __aenter__ 和 __aexit__ 方法存在
        assert hasattr(tool, "__aenter__")
        assert hasattr(tool, "__aexit__")
        assert callable(tool.__aenter__)
        assert callable(tool.__aexit__)
    
    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """测试上下文管理器使用"""
        tool = MockAsyncTool()
        
        async with tool as context_tool:
            assert context_tool is tool
            result = await context_tool.execute(value="context_test")
            assert result.is_success()
    
    @pytest.mark.asyncio
    async def test_context_manager_cleanup_on_exception(self):
        """测试异常时的清理"""
        tool = MockAsyncTool()
        
        with pytest.raises(RuntimeError):
            async with tool:
                # 在上下文中抛出异常
                raise RuntimeError("test exception")
        
        # 验证工具仍然可用（清理成功）
        result = await tool.execute(value="after_exception")
        assert result.is_success()


@pytest.mark.asyncio
async def test_integration():
    """
    集成测试
    
    💡 对比TypeScript:
    describe('Integration Tests', () => {
        test('should work end-to-end', async () => {
            const tool = new MockAsyncTool();
            
            // 测试完整的工作流
            const results = await Promise.all([
                tool.execute({ value: 'test1' }),
                tool.execute({ value: 'test2' }),
                tool.execute({ value: 'test3' })
            ]);
            
            results.forEach((result, index) => {
                expect(result.isSuccess()).toBe(true);
                expect(result.content).toBe(`Mock result: test${index + 1}`);
            });
            
            // 测试错误情况
            const errorResult = await tool.execute({ value: 'error' });
            expect(errorResult.isError()).toBe(true);
        });
        
        test('should handle concurrent operations', async () => {
            const tool = new MockAsyncTool();
            const concurrentTasks = 10;
            
            const tasks = Array.from({ length: concurrentTasks }, (_, i) =>
                tool.execute({ value: `concurrent_${i}` })
            );
            
            const results = await Promise.all(tasks);
            
            expect(results).toHaveLength(concurrentTasks);
            results.forEach((result, index) => {
                expect(result.isSuccess()).toBe(true);
                expect(result.content).toBe(`Mock result: concurrent_${index}`);
            });
        });
    });
    
    学习要点：
    - 端到端测试的设计
    - 并发操作的测试
    - 完整工作流的验证
    - 性能测试的考虑
    """
    print("🧪 运行基础组件集成测试...")
    
    tool = MockAsyncTool()
    
    # 测试并发执行
    tasks = [
        tool.execute(value=f"test_{i}")
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # 验证结果
    assert len(results) == 5
    for i, result in enumerate(results):
        assert result.is_success()
        assert result.content == f"Mock result: test_{i}"
    
    # 测试错误处理
    error_result = await tool.execute(value="error")
    assert error_result.is_error()
    
    print("✅ 基础组件集成测试通过")


if __name__ == "__main__":
    """
    测试运行器
    
    学习要点：
    - 测试的组织和运行
    - 异步测试的执行
    - 测试结果的报告
    """
    print("🧪 运行基础组件测试...")
    
    # 运行集成测试
    asyncio.run(test_integration())
    
    print("✅ 所有基础组件测试完成")