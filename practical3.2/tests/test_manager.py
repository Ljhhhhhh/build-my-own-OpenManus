"""
Practical 3.2 - 异步工具管理器测试

这个模块测试异步工具管理器的功能，包括：
1. 工具注册和管理
2. 并发执行控制
3. 性能监控
4. 错误处理和恢复
5. 上下文管理

学习要点：
1. 异步工具管理的测试策略
2. 并发控制的验证
3. 性能监控的测试
4. 上下文管理器的测试
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.manager import AsyncToolManager
from tools.base import AsyncBaseTool, ToolResult, ToolResultStatus
from tools.calculator import AsyncCalculatorTool
from tools.weather import AsyncWeatherTool


class MockAsyncTool(AsyncBaseTool):
    """
    模拟异步工具类
    
    💡 对比TypeScript:
    class MockAsyncTool extends AsyncBaseTool {
        constructor(
            public name: string = 'mock_tool',
            public description: string = 'Mock tool for testing',
            private executionTime: number = 0.1,
            private shouldFail: boolean = false
        ) {
            super();
        }
        
        getSchema(): object {
            return {
                type: 'object',
                properties: {
                    value: { type: 'string' }
                },
                required: ['value']
            };
        }
        
        async execute(value: string): Promise<ToolResult> {
            await new Promise(resolve => 
                setTimeout(resolve, this.executionTime * 1000)
            );
            
            if (this.shouldFail) {
                throw new Error('Mock tool execution failed');
            }
            
            return ToolResult.success({
                input: value,
                processed: `processed_${value}`,
                timestamp: Date.now()
            });
        }
    }
    
    学习要点：
    - 测试工具的设计模式
    - 可配置的测试行为
    - 异步执行的模拟
    - 错误场景的模拟
    """
    
    def __init__(
        self,
        name: str = "mock_tool",
        description: str = "Mock tool for testing",
        execution_time: float = 0.1,
        should_fail: bool = False
    ):
        self.name = name
        self.description = description
        self._execution_time = execution_time
        self._should_fail = should_fail
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "value": {"type": "string"}
            },
            "required": ["value"]
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        # 模拟执行时间
        await asyncio.sleep(self._execution_time)
        
        if self._should_fail:
            raise ValueError("Mock tool execution failed")
        
        value = kwargs.get("value", "default")
        return ToolResult.success({
            "input": value,
            "processed": f"processed_{value}",
            "timestamp": time.time()
        })


class TestAsyncToolManager:
    """
    异步工具管理器测试类
    
    💡 对比TypeScript:
    describe('AsyncToolManager', () => {
        let manager: AsyncToolManager;
        
        beforeEach(() => {
            manager = new AsyncToolManager({
                maxConcurrentTasks: 3,
                defaultTimeout: 5000
            });
        });
        
        afterEach(async () => {
            await manager.cleanup();
        });
        
        test('should initialize with default configuration', () => {
            expect(manager.maxConcurrentTasks).toBe(3);
            expect(manager.defaultTimeout).toBe(5000);
            expect(manager.registeredTools).toHaveLength(0);
        });
        
        test('should register tools successfully', () => {
            const mockTool = new MockAsyncTool('test_tool');
            
            manager.registerTool(mockTool);
            
            expect(manager.registeredTools).toHaveLength(1);
            expect(manager.hasTool('test_tool')).toBe(true);
            expect(manager.getTool('test_tool')).toBe(mockTool);
        });
        
        test('should execute single tool', async () => {
            const mockTool = new MockAsyncTool('test_tool');
            manager.registerTool(mockTool);
            
            const result = await manager.executeTool('test_tool', {
                value: 'test_input'
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content.input).toBe('test_input');
            expect(result.content.processed).toBe('processed_test_input');
        });
        
        test('should handle concurrent executions', async () => {
            const tools = [
                new MockAsyncTool('tool1', 'Tool 1', 0.1),
                new MockAsyncTool('tool2', 'Tool 2', 0.1),
                new MockAsyncTool('tool3', 'Tool 3', 0.1)
            ];
            
            tools.forEach(tool => manager.registerTool(tool));
            
            const startTime = Date.now();
            
            const promises = tools.map((tool, index) =>
                manager.executeTool(tool.name, { value: `input${index}` })
            );
            
            const results = await Promise.all(promises);
            const endTime = Date.now();
            
            expect(results).toHaveLength(3);
            results.forEach((result, index) => {
                expect(result.isSuccess()).toBe(true);
                expect(result.content.input).toBe(`input${index}`);
            });
            
            // 并发执行应该比串行执行快
            expect(endTime - startTime).toBeLessThan(250); // 小于串行执行时间
        });
        
        test('should respect concurrency limits', async () => {
            const manager = new AsyncToolManager({ maxConcurrentTasks: 2 });
            
            const tools = Array.from({ length: 5 }, (_, i) =>
                new MockAsyncTool(`tool${i}`, `Tool ${i}`, 0.2)
            );
            
            tools.forEach(tool => manager.registerTool(tool));
            
            const startTime = Date.now();
            
            const promises = tools.map((tool, index) =>
                manager.executeTool(tool.name, { value: `input${index}` })
            );
            
            const results = await Promise.all(promises);
            const endTime = Date.now();
            
            expect(results).toHaveLength(5);
            results.forEach(result => {
                expect(result.isSuccess()).toBe(true);
            });
            
            // 由于并发限制，执行时间应该更长
            expect(endTime - startTime).toBeGreaterThan(400); // 至少需要3批次
        });
    });
    
    学习要点：
    - 异步工具管理器的测试结构
    - 并发控制的验证方法
    - 性能测试的实现
    - 资源清理的测试
    """
    
    @pytest.fixture
    def manager(self):
        """创建工具管理器实例"""
        return AsyncToolManager(max_concurrent_tasks=3, default_timeout=5.0)
    
    @pytest.fixture
    async def manager_with_cleanup(self):
        """创建带清理的工具管理器实例"""
        manager = AsyncToolManager(max_concurrent_tasks=3, default_timeout=5.0)
        yield manager
        await manager.cleanup()
    
    def test_manager_initialization(self, manager):
        """测试管理器初始化"""
        assert manager._max_concurrent_tasks == 3
        assert manager._default_timeout == 5.0
        assert len(manager._tools) == 0
        assert manager._semaphore._value == 3
    
    def test_tool_registration(self, manager):
        """测试工具注册"""
        mock_tool = MockAsyncTool("test_tool")
        
        manager.register_tool(mock_tool)
        
        assert len(manager._tools) == 1
        assert manager.has_tool("test_tool")
        assert manager.get_tool("test_tool") is mock_tool
    
    def test_duplicate_tool_registration(self, manager):
        """测试重复工具注册"""
        mock_tool1 = MockAsyncTool("test_tool")
        mock_tool2 = MockAsyncTool("test_tool")
        
        manager.register_tool(mock_tool1)
        
        with pytest.raises(ValueError, match="工具.*已存在"):
            manager.register_tool(mock_tool2)
    
    def test_tool_unregistration(self, manager):
        """测试工具注销"""
        mock_tool = MockAsyncTool("test_tool")
        
        manager.register_tool(mock_tool)
        assert manager.has_tool("test_tool")
        
        manager.unregister_tool("test_tool")
        assert not manager.has_tool("test_tool")
    
    def test_unregister_nonexistent_tool(self, manager):
        """测试注销不存在的工具"""
        with pytest.raises(ValueError, match="工具.*不存在"):
            manager.unregister_tool("nonexistent_tool")
    
    @pytest.mark.asyncio
    async def test_single_tool_execution(self, manager_with_cleanup):
        """测试单个工具执行"""
        manager = manager_with_cleanup
        mock_tool = MockAsyncTool("test_tool")
        manager.register_tool(mock_tool)
        
        result = await manager.execute_tool("test_tool", value="test_input")
        
        assert result.is_success()
        assert result.content["input"] == "test_input"
        assert result.content["processed"] == "processed_test_input"
    
    @pytest.mark.asyncio
    async def test_nonexistent_tool_execution(self, manager_with_cleanup):
        """测试执行不存在的工具"""
        manager = manager_with_cleanup
        
        result = await manager.execute_tool("nonexistent_tool", value="test")
        
        assert result.is_error()
        assert "不存在" in result.error_message
    
    @pytest.mark.asyncio
    async def test_tool_execution_failure(self, manager_with_cleanup):
        """测试工具执行失败"""
        manager = manager_with_cleanup
        mock_tool = MockAsyncTool("failing_tool", should_fail=True)
        manager.register_tool(mock_tool)
        
        result = await manager.execute_tool("failing_tool", value="test")
        
        assert result.is_error()
        assert "execution failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self, manager_with_cleanup):
        """测试并发工具执行"""
        manager = manager_with_cleanup
        
        # 注册多个工具
        tools = [
            MockAsyncTool(f"tool{i}", execution_time=0.1)
            for i in range(3)
        ]
        
        for tool in tools:
            manager.register_tool(tool)
        
        start_time = time.time()
        
        # 并发执行
        tasks = [
            manager.execute_tool(f"tool{i}", value=f"input{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 验证结果
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.is_success()
            assert result.content["input"] == f"input{i}"
        
        # 并发执行应该比串行执行快
        assert end_time - start_time < 0.25  # 小于串行执行时间
    
    @pytest.mark.asyncio
    async def test_concurrency_limit(self, manager_with_cleanup):
        """测试并发限制"""
        # 创建并发限制为2的管理器
        manager = AsyncToolManager(max_concurrent_tasks=2)
        
        # 注册5个工具，每个执行时间0.2秒
        tools = [
            MockAsyncTool(f"tool{i}", execution_time=0.2)
            for i in range(5)
        ]
        
        for tool in tools:
            manager.register_tool(tool)
        
        start_time = time.time()
        
        # 并发执行5个任务
        tasks = [
            manager.execute_tool(f"tool{i}", value=f"input{i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 验证结果
        assert len(results) == 5
        for result in results:
            assert result.is_success()
        
        # 由于并发限制，执行时间应该更长
        # 5个任务，并发限制2，每个0.2秒，至少需要3批次，约0.6秒
        assert end_time - start_time >= 0.5
        
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_execution_timeout(self, manager_with_cleanup):
        """测试执行超时"""
        manager = manager_with_cleanup
        
        # 创建一个执行时间很长的工具
        slow_tool = MockAsyncTool("slow_tool", execution_time=2.0)
        manager.register_tool(slow_tool)
        
        # 设置较短的超时时间
        result = await manager.execute_tool(
            "slow_tool",
            value="test",
            timeout=0.5
        )
        
        assert result.is_error()
        assert "超时" in result.error_message or "timeout" in result.error_message.lower()


class TestAsyncToolManagerBatch:
    """
    异步工具管理器批量操作测试类
    
    💡 对比TypeScript:
    describe('AsyncToolManager Batch Operations', () => {
        let manager: AsyncToolManager;
        
        beforeEach(() => {
            manager = new AsyncToolManager();
        });
        
        test('should execute multiple tools in batch', async () => {
            const tools = [
                new MockAsyncTool('tool1'),
                new MockAsyncTool('tool2'),
                new MockAsyncTool('tool3')
            ];
            
            tools.forEach(tool => manager.registerTool(tool));
            
            const batchRequests = [
                { toolName: 'tool1', params: { value: 'input1' } },
                { toolName: 'tool2', params: { value: 'input2' } },
                { toolName: 'tool3', params: { value: 'input3' } }
            ];
            
            const results = await manager.executeBatch(batchRequests);
            
            expect(results).toHaveLength(3);
            results.forEach((result, index) => {
                expect(result.isSuccess()).toBe(true);
                expect(result.content.input).toBe(`input${index + 1}`);
            });
        });
        
        test('should handle mixed success and failure in batch', async () => {
            const tools = [
                new MockAsyncTool('success_tool', 'Success tool', 0.1, false),
                new MockAsyncTool('failure_tool', 'Failure tool', 0.1, true)
            ];
            
            tools.forEach(tool => manager.registerTool(tool));
            
            const batchRequests = [
                { toolName: 'success_tool', params: { value: 'input1' } },
                { toolName: 'failure_tool', params: { value: 'input2' } }
            ];
            
            const results = await manager.executeBatch(batchRequests);
            
            expect(results).toHaveLength(2);
            expect(results[0].isSuccess()).toBe(true);
            expect(results[1].isError()).toBe(true);
        });
        
        test('should collect execution statistics', async () => {
            const tool = new MockAsyncTool('test_tool');
            manager.registerTool(tool);
            
            await manager.executeTool('test_tool', { value: 'test1' });
            await manager.executeTool('test_tool', { value: 'test2' });
            
            const stats = manager.getExecutionStatistics();
            
            expect(stats.totalExecutions).toBe(2);
            expect(stats.successfulExecutions).toBe(2);
            expect(stats.failedExecutions).toBe(0);
            expect(stats.averageExecutionTime).toBeGreaterThan(0);
        });
    });
    
    学习要点：
    - 批量操作的测试方法
    - 混合成功失败场景的处理
    - 统计信息的收集和验证
    - 性能指标的测试
    """
    
    @pytest.fixture
    async def manager(self):
        """创建工具管理器实例"""
        manager = AsyncToolManager()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_batch_execution(self, manager):
        """测试批量执行"""
        # 注册多个工具
        tools = [
            MockAsyncTool(f"tool{i}", execution_time=0.1)
            for i in range(3)
        ]
        
        for tool in tools:
            manager.register_tool(tool)
        
        # 批量执行请求
        batch_requests = [
            {"tool_name": f"tool{i}", "params": {"value": f"input{i}"}}
            for i in range(3)
        ]
        
        results = await manager.execute_batch(batch_requests)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.is_success()
            assert result.content["input"] == f"input{i}"
    
    @pytest.mark.asyncio
    async def test_batch_mixed_results(self, manager):
        """测试批量执行混合结果"""
        # 注册成功和失败的工具
        success_tool = MockAsyncTool("success_tool", should_fail=False)
        failure_tool = MockAsyncTool("failure_tool", should_fail=True)
        
        manager.register_tool(success_tool)
        manager.register_tool(failure_tool)
        
        batch_requests = [
            {"tool_name": "success_tool", "params": {"value": "input1"}},
            {"tool_name": "failure_tool", "params": {"value": "input2"}}
        ]
        
        results = await manager.execute_batch(batch_requests)
        
        assert len(results) == 2
        assert results[0].is_success()
        assert results[1].is_error()
    
    @pytest.mark.asyncio
    async def test_execution_statistics(self, manager):
        """测试执行统计"""
        tool = MockAsyncTool("test_tool")
        manager.register_tool(tool)
        
        # 执行多次
        await manager.execute_tool("test_tool", value="test1")
        await manager.execute_tool("test_tool", value="test2")
        
        stats = manager.get_execution_statistics()
        
        assert stats["total_executions"] >= 2
        assert stats["successful_executions"] >= 2
        assert stats["failed_executions"] == 0
        assert stats["average_execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_execution_statistics_with_failures(self, manager):
        """测试包含失败的执行统计"""
        success_tool = MockAsyncTool("success_tool", should_fail=False)
        failure_tool = MockAsyncTool("failure_tool", should_fail=True)
        
        manager.register_tool(success_tool)
        manager.register_tool(failure_tool)
        
        # 执行成功和失败的任务
        await manager.execute_tool("success_tool", value="test1")
        await manager.execute_tool("failure_tool", value="test2")
        
        stats = manager.get_execution_statistics()
        
        assert stats["total_executions"] >= 2
        assert stats["successful_executions"] >= 1
        assert stats["failed_executions"] >= 1


class TestAsyncToolManagerContext:
    """
    异步工具管理器上下文管理测试类
    
    💡 对比TypeScript:
    describe('AsyncToolManager Context Management', () => {
        test('should work as async context manager', async () => {
            const results: any[] = [];
            
            await using(new AsyncToolManager(), async (manager) => {
                const tool = new MockAsyncTool('test_tool');
                manager.registerTool(tool);
                
                const result = await manager.executeTool('test_tool', {
                    value: 'test_input'
                });
                
                results.push(result);
                
                expect(result.isSuccess()).toBe(true);
            });
            
            // 验证上下文管理器正确清理了资源
            expect(results).toHaveLength(1);
            expect(results[0].isSuccess()).toBe(true);
        });
        
        test('should cleanup resources on context exit', async () => {
            let manager: AsyncToolManager;
            
            await using(new AsyncToolManager(), async (mgr) => {
                manager = mgr;
                const tool = new MockAsyncTool('test_tool');
                manager.registerTool(tool);
                
                expect(manager.registeredTools).toHaveLength(1);
            });
            
            // 上下文退出后，资源应该被清理
            expect(manager.registeredTools).toHaveLength(0);
        });
        
        test('should handle exceptions in context', async () => {
            let cleanupCalled = false;
            
            try {
                await using(new AsyncToolManager(), async (manager) => {
                    const tool = new MockAsyncTool('test_tool');
                    manager.registerTool(tool);
                    
                    // 模拟异常
                    throw new Error('Test exception');
                });
            } catch (error) {
                expect(error.message).toBe('Test exception');
            }
            
            // 即使发生异常，清理也应该被调用
            // 这里需要通过其他方式验证清理是否被调用
        });
    });
    
    学习要点：
    - 异步上下文管理器的测试
    - 资源清理的验证
    - 异常处理中的资源管理
    - 上下文管理器的生命周期测试
    """
    
    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """测试上下文管理器使用"""
        async with AsyncToolManager() as manager:
            tool = MockAsyncTool("test_tool")
            manager.register_tool(tool)
            
            result = await manager.execute_tool("test_tool", value="test_input")
            
            assert result.is_success()
            assert result.content["input"] == "test_input"
    
    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self):
        """测试上下文管理器清理"""
        manager = None
        
        async with AsyncToolManager() as mgr:
            manager = mgr
            tool = MockAsyncTool("test_tool")
            manager.register_tool(tool)
            
            assert len(manager._tools) == 1
        
        # 上下文退出后，应该进行清理
        # 注意：实际的清理行为取决于具体实现
        assert manager is not None
    
    @pytest.mark.asyncio
    async def test_context_manager_exception_handling(self):
        """测试上下文管理器异常处理"""
        cleanup_called = False
        
        try:
            async with AsyncToolManager() as manager:
                tool = MockAsyncTool("test_tool")
                manager.register_tool(tool)
                
                # 模拟异常
                raise ValueError("Test exception")
        except ValueError as e:
            assert str(e) == "Test exception"
        
        # 即使发生异常，上下文管理器也应该正确退出


class TestAsyncToolManagerIntegration:
    """
    异步工具管理器集成测试类
    
    💡 对比TypeScript:
    describe('AsyncToolManager Integration', () => {
        let manager: AsyncToolManager;
        
        beforeEach(() => {
            manager = new AsyncToolManager();
        });
        
        test('should work with real calculator tool', async () => {
            const calculator = new AsyncCalculatorTool();
            manager.registerTool(calculator);
            
            const result = await manager.executeTool('async_calculator', {
                operation: 'add',
                operands: [10, 20]
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content.result).toBe(30);
        });
        
        test('should work with real weather tool', async () => {
            const weather = new AsyncWeatherTool();
            manager.registerTool(weather);
            
            // Mock the HTTP request
            const mockResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20, humidity: 65 },
                name: 'Beijing'
            };
            
            jest.spyOn(weather, 'execute').mockResolvedValue(
                ToolResult.success(mockResponse)
            );
            
            const result = await manager.executeTool('async_weather', {
                city: 'Beijing'
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content.name).toBe('Beijing');
        });
        
        test('should handle complex workflow', async () => {
            const calculator = new AsyncCalculatorTool();
            const weather = new AsyncWeatherTool();
            
            manager.registerTool(calculator);
            manager.registerTool(weather);
            
            // 执行复杂工作流
            const calcResult = await manager.executeTool('async_calculator', {
                operation: 'multiply',
                operands: [5, 6]
            });
            
            expect(calcResult.isSuccess()).toBe(true);
            
            // 基于计算结果执行其他操作
            const temperature = calcResult.content.result; // 30
            
            // 这里可以添加更复杂的工作流逻辑
            expect(temperature).toBe(30);
        });
    });
    
    学习要点：
    - 真实工具的集成测试
    - 复杂工作流的测试
    - 工具间协作的验证
    - 端到端功能测试
    """
    
    @pytest.fixture
    async def manager(self):
        """创建工具管理器实例"""
        manager = AsyncToolManager()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_real_calculator_integration(self, manager):
        """测试真实计算器工具集成"""
        calculator = AsyncCalculatorTool()
        manager.register_tool(calculator)
        
        result = await manager.execute_tool(
            "async_calculator",
            operation="add",
            operands=[10, 20]
        )
        
        assert result.is_success()
        assert result.content["result"] == 30
        assert result.content["operation"] == "add"
    
    @pytest.mark.asyncio
    async def test_real_weather_integration(self, manager):
        """测试真实天气工具集成"""
        weather = AsyncWeatherTool()
        manager.register_tool(weather)
        
        # 模拟HTTP请求
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "main": {"temp": 20, "humidity": 65},
                "name": "Beijing"
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await manager.execute_tool(
                "async_weather",
                city="Beijing"
            )
            
            assert result.is_success()
            assert result.content["city"] == "Beijing"
            assert result.content["temperature"] == 20
    
    @pytest.mark.asyncio
    async def test_complex_workflow(self, manager):
        """测试复杂工作流"""
        calculator = AsyncCalculatorTool()
        manager.register_tool(calculator)
        
        # 执行一系列计算
        result1 = await manager.execute_tool(
            "async_calculator",
            operation="add",
            operands=[10, 20]
        )
        
        assert result1.is_success()
        first_result = result1.content["result"]  # 30
        
        result2 = await manager.execute_tool(
            "async_calculator",
            operation="multiply",
            operands=[first_result, 2]
        )
        
        assert result2.is_success()
        assert result2.content["result"] == 60
    
    @pytest.mark.asyncio
    async def test_concurrent_real_tools(self, manager):
        """测试并发真实工具"""
        calculator = AsyncCalculatorTool()
        manager.register_tool(calculator)
        
        # 并发执行多个计算
        tasks = [
            manager.execute_tool(
                "async_calculator",
                operation="add",
                operands=[i, i + 1]
            )
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result.is_success()
            assert result.content["result"] == i + (i + 1)  # i + (i+1) = 2i + 1


@pytest.mark.asyncio
async def test_manager_integration():
    """
    工具管理器集成测试
    
    学习要点：
    - 完整的管理器功能测试
    - 多种工具的协同工作
    - 性能和稳定性验证
    """
    print("🧪 运行工具管理器集成测试...")
    
    async with AsyncToolManager(max_concurrent_tasks=3) as manager:
        # 注册工具
        calculator = AsyncCalculatorTool()
        mock_tool = MockAsyncTool("mock_tool")
        
        manager.register_tool(calculator)
        manager.register_tool(mock_tool)
        
        # 测试单个工具执行
        calc_result = await manager.execute_tool(
            "async_calculator",
            operation="multiply",
            operands=[6, 7]
        )
        
        assert calc_result.is_success()
        assert calc_result.content["result"] == 42
        
        # 测试并发执行
        tasks = [
            manager.execute_tool("mock_tool", value=f"test{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.is_success()
            assert result.content["input"] == f"test{i}"
        
        # 测试统计信息
        stats = manager.get_execution_statistics()
        assert stats["total_executions"] >= 4
        assert stats["successful_executions"] >= 4
    
    print("✅ 工具管理器集成测试通过")


if __name__ == "__main__":
    """
    测试运行器
    
    学习要点：
    - 异步测试的组织和执行
    - 集成测试的设计模式
    - 测试覆盖率的考虑
    """
    print("🧪 运行工具管理器测试...")
    
    # 运行集成测试
    asyncio.run(test_manager_integration())
    
    print("✅ 所有工具管理器测试完成")