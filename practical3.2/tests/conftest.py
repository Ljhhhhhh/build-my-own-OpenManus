"""
Practical 3.2 - Pytest 配置文件

这个文件包含pytest的全局配置和共享fixtures，用于：
1. 异步测试配置
2. 测试环境设置
3. 共享测试数据和工具
4. 测试钩子和插件配置

学习要点：
1. pytest配置的最佳实践
2. 异步测试环境的设置
3. 测试fixtures的设计
4. 测试环境的隔离和清理
"""

import pytest
import asyncio
import os
import sys
from typing import Generator, AsyncGenerator
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from tools.manager import AsyncToolManager
from tools.calculator import AsyncCalculatorTool
from tools.weather import AsyncWeatherTool


# Pytest配置
def pytest_configure(config):
    """
    Pytest配置钩子
    
    💡 对比TypeScript (Jest):
    // jest.config.js
    module.exports = {
        preset: 'ts-jest',
        testEnvironment: 'node',
        setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
        testMatch: ['**/__tests__/**/*.test.ts', '**/?(*.)+(spec|test).ts'],
        collectCoverageFrom: [
            'src/**/*.ts',
            '!src/**/*.d.ts',
            '!src/tests/**'
        ],
        coverageDirectory: 'coverage',
        coverageReporters: ['text', 'lcov', 'html'],
        testTimeout: 10000,
        maxWorkers: 4,
        globals: {
            'ts-jest': {
                tsconfig: 'tsconfig.json'
            }
        }
    };
    
    // tests/setup.ts
    import { jest } from '@jest/globals';
    
    // 全局测试设置
    beforeAll(async () => {
        // 设置测试环境
        process.env.NODE_ENV = 'test';
        process.env.API_KEY = 'test_api_key';
    });
    
    afterAll(async () => {
        // 清理测试环境
        jest.clearAllMocks();
    });
    
    beforeEach(() => {
        // 每个测试前的设置
        jest.clearAllMocks();
    });
    
    学习要点：
    - 测试配置的集中管理
    - 环境变量的测试设置
    - 全局钩子的使用
    - 测试隔离的实现
    """
    # 设置测试环境变量
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["OPENWEATHER_API_KEY"] = "test_api_key_12345"
    os.environ["WEATHER_CACHE_TTL"] = "300"
    os.environ["MAX_CONCURRENT_REQUESTS"] = "5"
    
    # 配置pytest标记
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )


def pytest_collection_modifyitems(config, items):
    """
    修改测试收集项
    
    💡 对比TypeScript (Jest):
    // jest.config.js
    module.exports = {
        testMatch: ['**/__tests__/**/*.test.ts'],
        testPathIgnorePatterns: ['/node_modules/', '/dist/'],
        setupFilesAfterEnv: ['<rootDir>/tests/jest.setup.ts'],
        
        // 自定义测试运行器
        runner: '@jest/runner',
        
        // 测试环境配置
        testEnvironment: 'node',
        
        // 全局设置
        globals: {
            'ts-jest': {
                tsconfig: 'tsconfig.json'
            }
        }
    };
    
    学习要点：
    - 测试收集的自定义逻辑
    - 测试标记的自动添加
    - 测试分类和过滤
    - 测试执行顺序的控制
    """
    # 为异步测试添加asyncio标记
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # 为包含"integration"的测试添加integration标记
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # 为包含"slow"的测试添加slow标记
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # 为包含"network"或"weather"的测试添加network标记
        if any(keyword in item.name.lower() for keyword in ["network", "weather", "api"]):
            item.add_marker(pytest.mark.network)


# 全局Fixtures
@pytest.fixture(scope="session")
def event_loop():
    """
    会话级别的事件循环
    
    💡 对比TypeScript (Jest):
    // tests/setup.ts
    import { beforeAll, afterAll } from '@jest/globals';
    
    let globalSetup: any;
    
    beforeAll(async () => {
        // 全局设置
        globalSetup = await initializeTestEnvironment();
    });
    
    afterAll(async () => {
        // 全局清理
        if (globalSetup) {
            await globalSetup.cleanup();
        }
    });
    
    学习要点：
    - 会话级别资源的管理
    - 异步测试环境的设置
    - 资源的生命周期管理
    - 测试隔离的实现
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """
    测试配置fixture
    
    💡 对比TypeScript:
    // tests/fixtures/config.ts
    export const testConfig = {
        apiKey: 'test_api_key',
        baseUrl: 'http://localhost:3000',
        timeout: 5000,
        retries: 3,
        environment: 'test'
    };
    
    export function createTestConfig(overrides: Partial<typeof testConfig> = {}) {
        return { ...testConfig, ...overrides };
    }
    
    学习要点：
    - 测试配置的集中管理
    - 配置的可重用性
    - 环境特定的配置
    - 配置的类型安全
    """
    # 创建测试专用配置
    config = Config()
    
    # 确保使用测试环境配置
    config._openweather_api_key = "test_api_key_12345"
    config._weather_cache_ttl = 300
    config._max_concurrent_requests = 5
    config._log_level = "DEBUG"
    
    return config


@pytest.fixture
async def async_tool_manager():
    """
    异步工具管理器fixture
    
    💡 对比TypeScript:
    // tests/fixtures/toolManager.ts
    import { AsyncToolManager } from '../src/tools/manager';
    import { MockAsyncTool } from './mockTools';
    
    export async function createTestToolManager() {
        const manager = new AsyncToolManager({
            maxConcurrentTasks: 3,
            defaultTimeout: 5000
        });
        
        // 注册测试工具
        const mockTool = new MockAsyncTool('test_tool');
        manager.registerTool(mockTool);
        
        return manager;
    }
    
    export async function cleanupToolManager(manager: AsyncToolManager) {
        await manager.cleanup();
    }
    
    学习要点：
    - 异步资源的fixture管理
    - 测试工具的预配置
    - 资源的自动清理
    - 测试隔离的保证
    """
    manager = AsyncToolManager(max_concurrent_tasks=3, default_timeout=5.0)
    yield manager
    await manager.cleanup()


@pytest.fixture
def mock_calculator_tool():
    """
    模拟计算器工具fixture
    
    💡 对比TypeScript:
    // tests/fixtures/mockTools.ts
    import { AsyncCalculatorTool } from '../src/tools/calculator';
    import { ToolResult } from '../src/tools/base';
    
    export class MockCalculatorTool extends AsyncCalculatorTool {
        private mockResults: Map<string, any> = new Map();
        
        setMockResult(operation: string, operands: number[], result: number) {
            const key = `${operation}_${operands.join('_')}`;
            this.mockResults.set(key, result);
        }
        
        async execute(params: any): Promise<ToolResult> {
            const key = `${params.operation}_${params.operands.join('_')}`;
            const mockResult = this.mockResults.get(key);
            
            if (mockResult !== undefined) {
                return ToolResult.success({
                    operation: params.operation,
                    operands: params.operands,
                    result: mockResult
                });
            }
            
            return super.execute(params);
        }
    }
    
    学习要点：
    - 工具的模拟和存根
    - 可控的测试行为
    - 测试数据的管理
    - 依赖注入的测试
    """
    return AsyncCalculatorTool()


@pytest.fixture
def mock_weather_tool():
    """
    模拟天气工具fixture
    
    💡 对比TypeScript:
    // tests/fixtures/weatherTool.ts
    import { AsyncWeatherTool } from '../src/tools/weather';
    import { ToolResult } from '../src/tools/base';
    
    export class MockWeatherTool extends AsyncWeatherTool {
        private mockWeatherData: Map<string, any> = new Map();
        
        setMockWeatherData(city: string, data: any) {
            this.mockWeatherData.set(city.toLowerCase(), data);
        }
        
        async execute(params: { city: string }): Promise<ToolResult> {
            const mockData = this.mockWeatherData.get(params.city.toLowerCase());
            
            if (mockData) {
                return ToolResult.success({
                    city: params.city,
                    ...mockData
                });
            }
            
            // 返回默认模拟数据
            return ToolResult.success({
                city: params.city,
                temperature: 20,
                humidity: 65,
                description: 'clear sky',
                weather: 'Clear'
            });
        }
    }
    
    学习要点：
    - 外部API的模拟
    - 网络请求的存根
    - 测试数据的预设
    - 错误场景的模拟
    """
    tool = AsyncWeatherTool()
    
    # 模拟HTTP客户端
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 20, "humidity": 65},
            "name": "Test City"
        })
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        yield tool


@pytest.fixture
def sample_test_data():
    """
    示例测试数据fixture
    
    💡 对比TypeScript:
    // tests/fixtures/testData.ts
    export const sampleTestData = {
        calculations: [
            { operation: 'add', operands: [10, 20], expected: 30 },
            { operation: 'subtract', operands: [30, 10], expected: 20 },
            { operation: 'multiply', operands: [5, 6], expected: 30 },
            { operation: 'divide', operands: [20, 4], expected: 5 }
        ],
        
        weatherData: [
            { city: 'Beijing', temp: 20, humidity: 65 },
            { city: 'Shanghai', temp: 25, humidity: 70 },
            { city: 'Guangzhou', temp: 28, humidity: 80 }
        ],
        
        errorCases: [
            { operation: 'divide', operands: [10, 0], error: 'Division by zero' },
            { operation: 'invalid', operands: [1, 2], error: 'Invalid operation' }
        ]
    };
    
    export function getCalculationTestCase(index: number) {
        return sampleTestData.calculations[index];
    }
    
    export function getWeatherTestCase(city: string) {
        return sampleTestData.weatherData.find(data => data.city === city);
    }
    
    学习要点：
    - 测试数据的组织和管理
    - 参数化测试的数据源
    - 边界条件的测试数据
    - 错误场景的测试数据
    """
    return {
        "calculations": [
            {"operation": "add", "operands": [10, 20], "expected": 30},
            {"operation": "subtract", "operands": [30, 10], "expected": 20},
            {"operation": "multiply", "operands": [5, 6], "expected": 30},
            {"operation": "divide", "operands": [20, 4], "expected": 5.0}
        ],
        
        "weather_data": [
            {"city": "Beijing", "temp": 20, "humidity": 65, "description": "clear sky"},
            {"city": "Shanghai", "temp": 25, "humidity": 70, "description": "partly cloudy"},
            {"city": "Guangzhou", "temp": 28, "humidity": 80, "description": "light rain"}
        ],
        
        "error_cases": [
            {"operation": "divide", "operands": [10, 0], "error": "除零错误"},
            {"operation": "invalid", "operands": [1, 2], "error": "不支持的操作"},
            {"city": "", "error": "城市名称不能为空"}
        ],
        
        "performance_data": [
            {"concurrent_tasks": 1, "expected_time_range": (0.1, 0.5)},
            {"concurrent_tasks": 3, "expected_time_range": (0.1, 0.3)},
            {"concurrent_tasks": 5, "expected_time_range": (0.1, 0.4)}
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    自动使用的测试环境设置fixture
    
    💡 对比TypeScript:
    // tests/setup.ts
    import { beforeEach, afterEach } from '@jest/globals';
    
    beforeEach(() => {
        // 每个测试前的设置
        process.env.NODE_ENV = 'test';
        
        // 清理模拟
        jest.clearAllMocks();
        
        // 重置全局状态
        resetGlobalState();
    });
    
    afterEach(() => {
        // 每个测试后的清理
        cleanupTestResources();
        
        // 恢复模拟
        jest.restoreAllMocks();
    });
    
    学习要点：
    - 自动测试环境设置
    - 测试隔离的实现
    - 全局状态的管理
    - 资源的自动清理
    """
    # 测试前设置
    original_env = os.environ.copy()
    
    # 设置测试环境变量
    os.environ.update({
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "OPENWEATHER_API_KEY": "test_api_key_12345",
        "WEATHER_CACHE_TTL": "300"
    })
    
    yield
    
    # 测试后清理
    os.environ.clear()
    os.environ.update(original_env)


# 自定义标记
pytest_plugins = ["pytest_asyncio"]

# 异步测试配置
@pytest.fixture(scope="session")
def anyio_backend():
    """
    配置anyio后端
    
    学习要点：
    - 异步测试框架的配置
    - 事件循环的管理
    - 异步资源的生命周期
    """
    return "asyncio"


# 测试工具函数
def assert_tool_result_success(result, expected_content=None):
    """
    断言工具结果成功
    
    💡 对比TypeScript:
    // tests/utils/assertions.ts
    export function assertToolResultSuccess(
        result: ToolResult,
        expectedContent?: any
    ): void {
        expect(result.isSuccess()).toBe(true);
        expect(result.status).toBe(ToolResultStatus.SUCCESS);
        
        if (expectedContent) {
            expect(result.content).toMatchObject(expectedContent);
        }
    }
    
    export function assertToolResultError(
        result: ToolResult,
        expectedError?: string
    ): void {
        expect(result.isError()).toBe(true);
        expect(result.status).toBe(ToolResultStatus.ERROR);
        
        if (expectedError) {
            expect(result.errorMessage).toContain(expectedError);
        }
    }
    
    学习要点：
    - 自定义断言函数
    - 测试工具的封装
    - 可重用的验证逻辑
    - 错误消息的验证
    """
    assert result.is_success(), f"Expected success but got: {result.error_message}"
    assert result.status.value == "success"
    
    if expected_content:
        for key, value in expected_content.items():
            assert key in result.content
            assert result.content[key] == value


def assert_tool_result_error(result, expected_error=None):
    """
    断言工具结果错误
    
    学习要点：
    - 错误场景的验证
    - 错误消息的检查
    - 异常处理的测试
    """
    assert result.is_error(), f"Expected error but got success: {result.content}"
    assert result.status.value == "error"
    
    if expected_error:
        assert expected_error in result.error_message


# 性能测试工具
class PerformanceTimer:
    """
    性能测试计时器
    
    💡 对比TypeScript:
    // tests/utils/performance.ts
    export class PerformanceTimer {
        private startTime: number = 0;
        private endTime: number = 0;
        
        start(): void {
            this.startTime = performance.now();
        }
        
        stop(): number {
            this.endTime = performance.now();
            return this.getElapsedTime();
        }
        
        getElapsedTime(): number {
            return this.endTime - this.startTime;
        }
        
        assertExecutionTime(
            maxTime: number,
            message?: string
        ): void {
            const elapsed = this.getElapsedTime();
            const msg = message || `Execution took ${elapsed}ms, expected < ${maxTime}ms`;
            expect(elapsed).toBeLessThan(maxTime);
        }
    }
    
    学习要点：
    - 性能测试的工具类
    - 执行时间的测量
    - 性能断言的实现
    - 基准测试的支持
    """
    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
    
    def start(self):
        """开始计时"""
        self.start_time = asyncio.get_event_loop().time()
    
    def stop(self):
        """停止计时并返回耗时"""
        self.end_time = asyncio.get_event_loop().time()
        return self.get_elapsed_time()
    
    def get_elapsed_time(self):
        """获取耗时（秒）"""
        return self.end_time - self.start_time
    
    def assert_execution_time(self, max_time, message=None):
        """断言执行时间"""
        elapsed = self.get_elapsed_time()
        msg = message or f"执行耗时 {elapsed:.3f}s，期望 < {max_time}s"
        assert elapsed < max_time, msg


@pytest.fixture
def performance_timer():
    """性能计时器fixture"""
    return PerformanceTimer()


# 测试数据生成器
def generate_test_cases(count=10):
    """
    生成测试用例
    
    💡 对比TypeScript:
    // tests/utils/generators.ts
    export function generateTestCases(count: number = 10) {
        return Array.from({ length: count }, (_, index) => ({
            id: index,
            input: `test_input_${index}`,
            expected: `expected_output_${index}`,
            metadata: {
                timestamp: Date.now(),
                index
            }
        }));
    }
    
    export function generateCalculationCases() {
        const operations = ['add', 'subtract', 'multiply', 'divide'];
        const cases = [];
        
        for (const operation of operations) {
            for (let i = 1; i <= 5; i++) {
                cases.push({
                    operation,
                    operands: [i, i + 1],
                    expected: calculateExpected(operation, i, i + 1)
                });
            }
        }
        
        return cases;
    }
    
    学习要点：
    - 测试数据的自动生成
    - 参数化测试的数据源
    - 大量测试用例的创建
    - 边界条件的覆盖
    """
    import random
    
    test_cases = []
    operations = ["add", "subtract", "multiply", "divide"]
    
    for i in range(count):
        operation = random.choice(operations)
        operand1 = random.randint(1, 100)
        operand2 = random.randint(1, 100) if operation != "divide" else random.randint(1, 10)
        
        test_cases.append({
            "id": i,
            "operation": operation,
            "operands": [operand1, operand2],
            "input": f"test_input_{i}",
            "metadata": {
                "timestamp": asyncio.get_event_loop().time(),
                "index": i
            }
        })
    
    return test_cases