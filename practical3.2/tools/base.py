"""
异步工具基类 - 高级版本

这个模块定义了异步工具框架的核心抽象类和数据模型。
相比practical3.1，这里引入了异步编程概念和更高级的Python特性。

学习要点：
1. 异步抽象基类 (ABC + async)
2. 异步方法的定义和使用
3. 上下文管理器 (async with)
4. 高级类型注解
5. 装饰器的使用
"""

import asyncio
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Union, Callable, Awaitable
from pydantic import BaseModel, Field


class ToolResultStatus(str, Enum):
    """
    工具执行结果状态枚举
    
    💡 对比TypeScript:
    enum ToolResultStatus {
        SUCCESS = "success",
        ERROR = "error", 
        INVALID_INPUT = "invalid_input",
        TIMEOUT = "timeout",
        CANCELLED = "cancelled"
    }
    
    学习要点：
    - 枚举类的继承 (str, Enum)
    - 状态管理的设计
    - 新增异步相关状态
    """
    SUCCESS = "success"
    ERROR = "error"
    INVALID_INPUT = "invalid_input"
    TIMEOUT = "timeout"          # 新增：超时状态
    CANCELLED = "cancelled"      # 新增：取消状态


class ToolResult(BaseModel):
    """
    工具执行结果模型 - 异步增强版
    
    💡 对比TypeScript:
    interface ToolResult {
        status: ToolResultStatus;
        content?: any;
        error_message?: string;
        metadata?: Record<string, any>;
        execution_time?: number;    // 新增
        timestamp?: number;         // 新增
    }
    
    学习要点：
    - Pydantic模型的高级用法
    - 可选字段和默认值
    - 时间戳和性能监控
    - 类方法的使用
    """
    status: ToolResultStatus
    content: Optional[Any] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    execution_time: Optional[float] = None    # 执行时间(秒)
    timestamp: float = Field(default_factory=time.time)  # 时间戳
    
    @classmethod
    def success(
        cls, 
        content: Any = None, 
        metadata: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None
    ) -> 'ToolResult':
        """
        创建成功结果
        
        学习要点：
        - 类方法的使用 (@classmethod)
        - 可选参数的处理
        - 对象的构建和返回
        """
        return cls(
            status=ToolResultStatus.SUCCESS,
            content=content,
            metadata=metadata or {},
            execution_time=execution_time
        )
    
    @classmethod
    def error(
        cls, 
        error_message: str, 
        metadata: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None
    ) -> 'ToolResult':
        """创建错误结果"""
        return cls(
            status=ToolResultStatus.ERROR,
            error_message=error_message,
            metadata=metadata or {},
            execution_time=execution_time
        )
    
    @classmethod
    def invalid_input(
        cls, 
        error_message: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ToolResult':
        """创建输入无效结果"""
        return cls(
            status=ToolResultStatus.INVALID_INPUT,
            error_message=error_message,
            metadata=metadata or {}
        )
    
    @classmethod
    def timeout(
        cls, 
        error_message: str = "操作超时", 
        metadata: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None
    ) -> 'ToolResult':
        """创建超时结果"""
        return cls(
            status=ToolResultStatus.TIMEOUT,
            error_message=error_message,
            metadata=metadata or {},
            execution_time=execution_time
        )
    
    @classmethod
    def cancelled(
        cls, 
        error_message: str = "操作被取消", 
        metadata: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None
    ) -> 'ToolResult':
        """创建取消结果"""
        return cls(
            status=ToolResultStatus.CANCELLED,
            error_message=error_message,
            metadata=metadata or {},
            execution_time=execution_time
        )
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.status == ToolResultStatus.SUCCESS
    
    def is_error(self) -> bool:
        """检查是否有错误"""
        return self.status in [
            ToolResultStatus.ERROR, 
            ToolResultStatus.INVALID_INPUT,
            ToolResultStatus.TIMEOUT,
            ToolResultStatus.CANCELLED
        ]


class AsyncBaseTool(ABC):
    """
    异步工具抽象基类
    
    💡 对比TypeScript:
    abstract class AsyncBaseTool {
        protected name: string;
        protected description: string;
        protected timeout: number;
        
        constructor(name: string, description: string, timeout?: number) {
            this.name = name;
            this.description = description;
            this.timeout = timeout || 30;
        }
        
        abstract get schema(): object;
        abstract async execute(params: any): Promise<ToolResult>;
        
        async validateInput(params: any): Promise<boolean | string> {
            // 默认验证逻辑
            return true;
        }
        
        async executeWithTimeout(params: any): Promise<ToolResult> {
            // 带超时的执行逻辑
        }
    }
    
    学习要点：
    - 异步抽象基类的定义
    - 异步方法的抽象声明
    - 超时处理机制
    - 上下文管理器的实现
    """
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        timeout: float = 30.0,
        max_retries: int = 0
    ):
        """
        初始化异步工具
        
        学习要点：
        - 异步工具的基本属性
        - 超时和重试配置
        - 参数验证
        
        Args:
            name: 工具名称
            description: 工具描述
            timeout: 执行超时时间(秒)
            max_retries: 最大重试次数
        """
        self.name = name
        self.description = description
        self.timeout = timeout
        self.max_retries = max_retries
        self._execution_count = 0
        self._success_count = 0
        self._error_count = 0
    
    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """
        返回工具的JSON Schema
        
        学习要点：
        - 抽象属性的定义
        - @property + @abstractmethod 的组合使用
        
        Returns:
            Dict[str, Any]: JSON Schema
        """
        pass
    
    async def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        异步输入验证
        
        💡 对比TypeScript:
        async validateInput(params: any): Promise<boolean | string> {
            // 基础验证逻辑
            if (!params || typeof params !== 'object') {
                return "参数必须是对象";
            }
            
            // 可以在子类中重写添加更多验证
            return true;
        }
        
        学习要点：
        - 异步方法的定义 (async def)
        - Union类型注解的使用
        - 基础验证逻辑
        - 可重写的设计模式
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            Union[bool, str]: True表示验证通过，字符串表示错误信息
        """
        # 基础验证：检查是否有参数
        if not kwargs:
            return "缺少必需的参数"
        
        # 子类可以重写此方法添加更多验证
        return True
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        异步执行工具
        
        学习要点：
        - 抽象异步方法的定义
        - 统一的返回类型
        - 子类必须实现的接口
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    async def execute_with_timeout(self, **kwargs) -> ToolResult:
        """
        带超时控制的执行
        
        💡 对比TypeScript:
        async executeWithTimeout(params: any): Promise<ToolResult> {
            const timeoutPromise = new Promise<never>((_, reject) => {
                setTimeout(() => reject(new Error('Timeout')), this.timeout * 1000);
            });
            
            try {
                const result = await Promise.race([
                    this.execute(params),
                    timeoutPromise
                ]);
                return result;
            } catch (error) {
                if (error.message === 'Timeout') {
                    return ToolResult.timeout(`执行超时 (${this.timeout}秒)`);
                }
                return ToolResult.error(error.message);
            }
        }
        
        学习要点：
        - asyncio.wait_for 的使用
        - 超时异常的处理
        - 异步任务的取消
        - 执行时间的测量
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        start_time = time.time()
        
        try:
            # 使用asyncio.wait_for实现超时控制
            result = await asyncio.wait_for(
                self.execute(**kwargs), 
                timeout=self.timeout
            )
            
            # 记录执行时间
            execution_time = time.time() - start_time
            if result.execution_time is None:
                result.execution_time = execution_time
            
            # 更新统计
            self._execution_count += 1
            if result.is_success():
                self._success_count += 1
            else:
                self._error_count += 1
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self._execution_count += 1
            self._error_count += 1
            
            return ToolResult.timeout(
                error_message=f"工具 '{self.name}' 执行超时 ({self.timeout}秒)",
                metadata={'tool': self.name, 'timeout': self.timeout},
                execution_time=execution_time
            )
        
        except asyncio.CancelledError:
            execution_time = time.time() - start_time
            self._execution_count += 1
            self._error_count += 1
            
            return ToolResult.cancelled(
                error_message=f"工具 '{self.name}' 执行被取消",
                metadata={'tool': self.name},
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._execution_count += 1
            self._error_count += 1
            
            return ToolResult.error(
                error_message=f"工具 '{self.name}' 执行失败: {str(e)}",
                metadata={'tool': self.name, 'exception_type': type(e).__name__},
                execution_time=execution_time
            )
    
    async def execute_with_retry(self, **kwargs) -> ToolResult:
        """
        带重试机制的执行
        
        学习要点：
        - 重试逻辑的实现
        - 指数退避策略
        - 异步延迟 (asyncio.sleep)
        - 循环和异常处理
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        last_result = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await self.execute_with_timeout(**kwargs)
                
                # 如果成功或者是输入错误（不需要重试），直接返回
                if result.is_success() or result.status == ToolResultStatus.INVALID_INPUT:
                    return result
                
                last_result = result
                
                # 如果还有重试机会，等待后重试
                if attempt < self.max_retries:
                    delay = 2 ** attempt  # 指数退避：1s, 2s, 4s, 8s...
                    print(f"⏳ 工具 '{self.name}' 第{attempt + 1}次执行失败，{delay}秒后重试...")
                    await asyncio.sleep(delay)
                
            except Exception as e:
                last_result = ToolResult.error(
                    error_message=f"工具 '{self.name}' 执行异常: {str(e)}",
                    metadata={'tool': self.name, 'attempt': attempt + 1}
                )
                
                if attempt < self.max_retries:
                    delay = 2 ** attempt
                    print(f"⏳ 工具 '{self.name}' 第{attempt + 1}次执行异常，{delay}秒后重试...")
                    await asyncio.sleep(delay)
        
        # 所有重试都失败了
        if last_result:
            last_result.metadata = last_result.metadata or {}
            last_result.metadata['total_attempts'] = self.max_retries + 1
            last_result.error_message = f"{last_result.error_message} (重试{self.max_retries}次后仍失败)"
        
        return last_result or ToolResult.error("未知错误")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取工具统计信息
        
        学习要点：
        - 统计数据的收集和计算
        - 成功率的计算
        - 字典的构建和返回
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        success_rate = (self._success_count / self._execution_count * 100) if self._execution_count > 0 else 0
        
        return {
            'name': self.name,
            'description': self.description,
            'executions': self._execution_count,
            'successes': self._success_count,
            'errors': self._error_count,
            'success_rate': f"{success_rate:.1f}%",
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }
    
    async def __aenter__(self):
        """
        异步上下文管理器入口
        
        💡 对比TypeScript:
        // TypeScript没有直接的上下文管理器，但可以用类似模式
        class AsyncToolContext {
            private tool: AsyncBaseTool;
            
            constructor(tool: AsyncBaseTool) {
                this.tool = tool;
            }
            
            async enter(): Promise<AsyncBaseTool> {
                console.log(`🔧 开始使用工具: ${this.tool.name}`);
                return this.tool;
            }
            
            async exit(): Promise<void> {
                console.log(`✅ 完成使用工具: ${this.tool.name}`);
            }
        }
        
        // 使用方式
        const context = new AsyncToolContext(tool);
        const activeTool = await context.enter();
        try {
            // 使用工具
        } finally {
            await context.exit();
        }
        
        学习要点：
        - 异步上下文管理器的实现
        - __aenter__ 和 __aexit__ 方法
        - 资源管理的最佳实践
        
        Returns:
            AsyncBaseTool: 工具实例
        """
        print(f"🔧 开始使用工具: {self.name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器出口
        
        学习要点：
        - 异常信息的处理
        - 资源清理的实现
        - 上下文管理器的完整实现
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪
        """
        if exc_type is None:
            print(f"✅ 完成使用工具: {self.name}")
        else:
            print(f"❌ 工具使用过程中发生异常: {self.name} - {exc_val}")
        
        # 返回False表示不抑制异常
        return False


# 工具装饰器
def tool_timer(func: Callable[..., Awaitable[ToolResult]]) -> Callable[..., Awaitable[ToolResult]]:
    """
    工具执行时间装饰器
    
    💡 对比TypeScript:
    function toolTimer<T extends (...args: any[]) => Promise<ToolResult>>(
        target: any,
        propertyName: string,
        descriptor: TypedPropertyDescriptor<T>
    ): TypedPropertyDescriptor<T> {
        const method = descriptor.value!;
        
        descriptor.value = async function(...args: any[]): Promise<ToolResult> {
            const startTime = Date.now();
            try {
                const result = await method.apply(this, args);
                const executionTime = (Date.now() - startTime) / 1000;
                if (result.execution_time === undefined) {
                    result.execution_time = executionTime;
                }
                return result;
            } catch (error) {
                const executionTime = (Date.now() - startTime) / 1000;
                return ToolResult.error(error.message, undefined, executionTime);
            }
        } as T;
        
        return descriptor;
    }
    
    学习要点：
    - 异步函数装饰器的实现
    - functools.wraps 的使用
    - 执行时间的自动记录
    - 装饰器的参数处理
    
    Args:
        func: 要装饰的异步函数
        
    Returns:
        Callable: 装饰后的函数
    """
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> ToolResult:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 如果结果中没有执行时间，添加它
            if result.execution_time is None:
                result.execution_time = execution_time
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=str(e),
                execution_time=execution_time
            )
    
    return wrapper


# 测试代码
if __name__ == "__main__":
    """
    测试异步基类的功能
    
    学习要点：
    - 异步测试的编写
    - 抽象类的测试方法
    - asyncio.run 的使用
    """
    
    # 创建一个简单的测试工具
    class TestAsyncTool(AsyncBaseTool):
        def __init__(self):
            super().__init__("test_tool", "测试异步工具", timeout=5.0)
        
        @property
        def schema(self) -> Dict[str, Any]:
            return {
                "type": "object",
                "properties": {
                    "delay": {"type": "number", "description": "延迟时间(秒)"}
                },
                "required": ["delay"]
            }
        
        @tool_timer
        async def execute(self, **kwargs) -> ToolResult:
            delay = kwargs.get('delay', 1.0)
            
            # 模拟异步操作
            await asyncio.sleep(delay)
            
            return ToolResult.success(
                content=f"异步操作完成，延迟了{delay}秒",
                metadata={'delay': delay}
            )
    
    async def test_async_tool():
        """测试异步工具"""
        print("🧪 测试异步工具基类")
        print("=" * 40)
        
        tool = TestAsyncTool()
        
        # 测试正常执行
        print("\n1. 测试正常执行:")
        result = await tool.execute_with_timeout(delay=1.0)
        print(f"状态: {result.status}")
        print(f"内容: {result.content}")
        print(f"执行时间: {result.execution_time:.2f}秒")
        
        # 测试超时
        print("\n2. 测试超时:")
        tool.timeout = 2.0
        result = await tool.execute_with_timeout(delay=3.0)
        print(f"状态: {result.status}")
        print(f"错误: {result.error_message}")
        
        # 测试上下文管理器
        print("\n3. 测试上下文管理器:")
        async with tool:
            result = await tool.execute(delay=0.5)
            print(f"上下文中执行结果: {result.status}")
        
        # 显示统计信息
        print("\n4. 统计信息:")
        stats = tool.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ 异步工具基类测试完成！")
    
    # 运行测试
    asyncio.run(test_async_tool())