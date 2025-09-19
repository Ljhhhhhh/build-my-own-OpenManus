"""
异步工具管理器 - 高级版本

这个模块实现了异步工具的管理、执行和监控功能。
相比practical3.1，这里引入了异步编程、并发控制、性能监控等高级特性。

学习要点：
1. 异步编程模式
2. 并发控制 (asyncio.Semaphore)
3. 任务管理 (asyncio.Task)
4. 性能监控和统计
5. 上下文管理器
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Union, Set
from contextlib import asynccontextmanager

from .base import AsyncBaseTool, ToolResult, ToolResultStatus


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncToolManager:
    """
    异步工具管理器
    
    💡 对比TypeScript:
    class AsyncToolManager {
        private tools: Map<string, AsyncBaseTool> = new Map();
        private executionHistory: ToolResult[] = [];
        private concurrencyLimit: number;
        private semaphore: Semaphore;
        
        constructor(concurrencyLimit: number = 10) {
            this.concurrencyLimit = concurrencyLimit;
            this.semaphore = new Semaphore(concurrencyLimit);
        }
        
        async registerTool(tool: AsyncBaseTool): Promise<void> {
            this.tools.set(tool.name, tool);
        }
        
        async executeTool(toolName: string, params: any): Promise<ToolResult> {
            await this.semaphore.acquire();
            try {
                const tool = this.tools.get(toolName);
                if (!tool) {
                    throw new Error(`Tool ${toolName} not found`);
                }
                return await tool.executeWithTimeout(params);
            } finally {
                this.semaphore.release();
            }
        }
        
        async executeMultiple(requests: ToolRequest[]): Promise<ToolResult[]> {
            const promises = requests.map(req => 
                this.executeTool(req.toolName, req.params)
            );
            return await Promise.all(promises);
        }
    }
    
    学习要点：
    - 异步工具的注册和管理
    - 并发控制和资源管理
    - 批量执行和任务协调
    - 性能监控和统计分析
    """
    
    def __init__(self, concurrency_limit: int = 10, enable_logging: bool = True):
        """
        初始化异步工具管理器
        
        学习要点：
        - 并发控制的初始化
        - 数据结构的选择和初始化
        - 配置参数的处理
        
        Args:
            concurrency_limit: 并发执行限制
            enable_logging: 是否启用日志
        """
        self.tools: Dict[str, AsyncBaseTool] = {}
        self.execution_history: List[ToolResult] = []
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.enable_logging = enable_logging
        
        # 统计信息
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._total_execution_time = 0.0
        
        # 活跃任务跟踪
        self._active_tasks: Set[asyncio.Task] = set()
        
        if enable_logging:
            logger.info(f"🚀 异步工具管理器初始化完成，并发限制: {concurrency_limit}")
    
    def register_tool(self, tool: AsyncBaseTool) -> None:
        """
        注册工具
        
        💡 对比TypeScript:
        registerTool(tool: AsyncBaseTool): void {
            if (this.tools.has(tool.name)) {
                throw new Error(`Tool ${tool.name} already registered`);
            }
            
            this.tools.set(tool.name, tool);
            console.log(`✅ 工具已注册: ${tool.name}`);
        }
        
        学习要点：
        - 工具的注册和验证
        - 重复注册的处理
        - 日志记录的使用
        
        Args:
            tool: 要注册的异步工具
            
        Raises:
            ValueError: 工具名称已存在
        """
        if tool.name in self.tools:
            raise ValueError(f"工具 '{tool.name}' 已经注册")
        
        self.tools[tool.name] = tool
        
        if self.enable_logging:
            logger.info(f"✅ 工具已注册: {tool.name} - {tool.description}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具
        
        学习要点：
        - 工具的注销和清理
        - 返回值的设计
        - 异常处理的选择
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否成功注销
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            if self.enable_logging:
                logger.info(f"🗑️ 工具已注销: {tool_name}")
            return True
        return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的工具
        
        学习要点：
        - 数据的整理和格式化
        - 列表推导式的使用
        - 工具信息的提取
        
        Returns:
            List[Dict[str, Any]]: 工具信息列表
        """
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'timeout': tool.timeout,
                'max_retries': tool.max_retries,
                'schema': tool.schema
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(
        self, 
        tool_name: str, 
        use_retry: bool = False,
        **kwargs
    ) -> ToolResult:
        """
        执行单个工具
        
        💡 对比TypeScript:
        async executeTool(
            toolName: string, 
            params: any, 
            useRetry: boolean = false
        ): Promise<ToolResult> {
            // 获取信号量
            await this.semaphore.acquire();
            
            try {
                const tool = this.tools.get(toolName);
                if (!tool) {
                    return ToolResult.error(`工具 ${toolName} 未找到`);
                }
                
                // 输入验证
                const validation = await tool.validateInput(params);
                if (validation !== true) {
                    return ToolResult.invalidInput(validation as string);
                }
                
                // 执行工具
                const result = useRetry 
                    ? await tool.executeWithRetry(params)
                    : await tool.executeWithTimeout(params);
                
                // 记录历史
                this.executionHistory.push(result);
                this.updateStats(result);
                
                return result;
                
            } finally {
                this.semaphore.release();
            }
        }
        
        学习要点：
        - 异步信号量的使用
        - 工具查找和验证
        - 输入验证的处理
        - 执行结果的记录
        - 资源的正确释放
        
        Args:
            tool_name: 工具名称
            use_retry: 是否使用重试机制
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        # 使用信号量控制并发
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # 查找工具
                if tool_name not in self.tools:
                    result = ToolResult.error(f"工具 '{tool_name}' 未找到")
                    self._record_execution(result, time.time() - start_time)
                    return result
                
                tool = self.tools[tool_name]
                
                if self.enable_logging:
                    logger.info(f"🔧 开始执行工具: {tool_name}")
                
                # 输入验证
                validation_result = await tool.validate_input(**kwargs)
                if validation_result is not True:
                    result = ToolResult.invalid_input(str(validation_result))
                    self._record_execution(result, time.time() - start_time)
                    return result
                
                # 执行工具
                if use_retry and tool.max_retries > 0:
                    result = await tool.execute_with_retry(**kwargs)
                else:
                    result = await tool.execute_with_timeout(**kwargs)
                
                # 记录执行结果
                execution_time = time.time() - start_time
                self._record_execution(result, execution_time)
                
                if self.enable_logging:
                    status_emoji = "✅" if result.is_success() else "❌"
                    logger.info(f"{status_emoji} 工具执行完成: {tool_name} ({execution_time:.2f}s)")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                result = ToolResult.error(f"工具管理器执行异常: {str(e)}")
                self._record_execution(result, execution_time)
                
                if self.enable_logging:
                    logger.error(f"❌ 工具执行异常: {tool_name} - {str(e)}")
                
                return result
    
    async def execute_multiple(
        self, 
        requests: List[Dict[str, Any]], 
        fail_fast: bool = False
    ) -> List[ToolResult]:
        """
        并发执行多个工具
        
        💡 对比TypeScript:
        async executeMultiple(
            requests: Array<{toolName: string, params: any, useRetry?: boolean}>,
            failFast: boolean = false
        ): Promise<ToolResult[]> {
            const tasks = requests.map(async (request) => {
                try {
                    return await this.executeTool(
                        request.toolName, 
                        request.params, 
                        request.useRetry || false
                    );
                } catch (error) {
                    return ToolResult.error(error.message);
                }
            });
            
            if (failFast) {
                // 一旦有失败就停止所有任务
                return await Promise.all(tasks);
            } else {
                // 等待所有任务完成，不管成功失败
                return await Promise.allSettled(tasks).then(results =>
                    results.map(result => 
                        result.status === 'fulfilled' 
                            ? result.value 
                            : ToolResult.error(result.reason.message)
                    )
                );
            }
        }
        
        学习要点：
        - 并发任务的创建和管理
        - asyncio.gather 的使用
        - 异常处理策略的选择
        - 任务结果的收集和处理
        
        Args:
            requests: 请求列表，每个请求包含 tool_name, params, use_retry
            fail_fast: 是否快速失败（一个失败就停止所有）
            
        Returns:
            List[ToolResult]: 执行结果列表
        """
        if not requests:
            return []
        
        if self.enable_logging:
            logger.info(f"🚀 开始并发执行 {len(requests)} 个工具")
        
        # 创建任务
        tasks = []
        for request in requests:
            tool_name = request.get('tool_name')
            params = request.get('params', {})
            use_retry = request.get('use_retry', False)
            
            if not tool_name:
                # 如果没有工具名称，创建一个错误结果
                tasks.append(self._create_error_task("缺少工具名称"))
            else:
                task = asyncio.create_task(
                    self.execute_tool(tool_name, use_retry, **params)
                )
                tasks.append(task)
                self._active_tasks.add(task)
        
        try:
            if fail_fast:
                # 快速失败模式：一个失败就停止所有
                results = await asyncio.gather(*tasks, return_exceptions=False)
            else:
                # 容错模式：等待所有任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理异常结果
                processed_results = []
                for result in results:
                    if isinstance(result, Exception):
                        processed_results.append(
                            ToolResult.error(f"任务执行异常: {str(result)}")
                        )
                    else:
                        processed_results.append(result)
                results = processed_results
            
            if self.enable_logging:
                success_count = sum(1 for r in results if r.is_success())
                logger.info(f"✅ 并发执行完成: {success_count}/{len(results)} 成功")
            
            return results
            
        except Exception as e:
            if self.enable_logging:
                logger.error(f"❌ 并发执行失败: {str(e)}")
            
            # 取消所有未完成的任务
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            # 返回错误结果
            return [ToolResult.error(f"并发执行失败: {str(e)}") for _ in requests]
        
        finally:
            # 清理活跃任务
            for task in tasks:
                self._active_tasks.discard(task)
    
    async def execute_pipeline(
        self, 
        pipeline: List[Dict[str, Any]], 
        pass_results: bool = True
    ) -> List[ToolResult]:
        """
        顺序执行工具管道
        
        学习要点：
        - 管道模式的实现
        - 结果传递的处理
        - 顺序执行的控制
        - 错误传播的处理
        
        Args:
            pipeline: 管道配置列表
            pass_results: 是否将前一个工具的结果传递给下一个工具
            
        Returns:
            List[ToolResult]: 每个步骤的执行结果
        """
        if not pipeline:
            return []
        
        if self.enable_logging:
            logger.info(f"🔄 开始执行工具管道，共 {len(pipeline)} 个步骤")
        
        results = []
        previous_result = None
        
        for i, step in enumerate(pipeline):
            tool_name = step.get('tool_name')
            params = step.get('params', {}).copy()
            use_retry = step.get('use_retry', False)
            
            if not tool_name:
                result = ToolResult.error(f"管道步骤 {i+1} 缺少工具名称")
                results.append(result)
                break
            
            # 如果启用结果传递，将前一个结果添加到参数中
            if pass_results and previous_result and previous_result.is_success():
                params['previous_result'] = previous_result.content
            
            if self.enable_logging:
                logger.info(f"🔧 执行管道步骤 {i+1}/{len(pipeline)}: {tool_name}")
            
            # 执行当前步骤
            result = await self.execute_tool(tool_name, use_retry, **params)
            results.append(result)
            previous_result = result
            
            # 如果当前步骤失败且配置了停止条件
            if not result.is_success() and step.get('stop_on_error', True):
                if self.enable_logging:
                    logger.warning(f"⚠️ 管道在步骤 {i+1} 停止，原因: {result.error_message}")
                break
        
        if self.enable_logging:
            success_count = sum(1 for r in results if r.is_success())
            logger.info(f"✅ 管道执行完成: {success_count}/{len(results)} 步骤成功")
        
        return results
    
    async def cancel_all_tasks(self) -> int:
        """
        取消所有活跃任务
        
        学习要点：
        - 任务取消的实现
        - 异步任务的管理
        - 资源清理的处理
        
        Returns:
            int: 取消的任务数量
        """
        if not self._active_tasks:
            return 0
        
        cancelled_count = 0
        for task in self._active_tasks.copy():
            if not task.done():
                task.cancel()
                cancelled_count += 1
        
        # 等待所有任务完成取消
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)
            self._active_tasks.clear()
        
        if self.enable_logging and cancelled_count > 0:
            logger.info(f"🛑 已取消 {cancelled_count} 个活跃任务")
        
        return cancelled_count
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        获取执行统计信息
        
        学习要点：
        - 统计数据的计算和格式化
        - 性能指标的设计
        - 数据分析的基础
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        success_rate = (
            self._successful_executions / self._total_executions * 100
            if self._total_executions > 0 else 0
        )
        
        avg_execution_time = (
            self._total_execution_time / self._total_executions
            if self._total_executions > 0 else 0
        )
        
        # 工具级别的统计
        tool_stats = {}
        for tool_name, tool in self.tools.items():
            tool_stats[tool_name] = tool.get_stats()
        
        return {
            'total_executions': self._total_executions,
            'successful_executions': self._successful_executions,
            'failed_executions': self._failed_executions,
            'success_rate': f"{success_rate:.1f}%",
            'average_execution_time': f"{avg_execution_time:.3f}s",
            'total_execution_time': f"{self._total_execution_time:.3f}s",
            'registered_tools': len(self.tools),
            'active_tasks': len(self._active_tasks),
            'concurrency_limit': self.concurrency_limit,
            'tool_stats': tool_stats
        }
    
    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的执行历史
        
        学习要点：
        - 历史记录的管理
        - 数据的切片和格式化
        - 时间戳的处理
        
        Args:
            limit: 返回的记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 执行历史
        """
        recent_history = self.execution_history[-limit:] if self.execution_history else []
        
        return [
            {
                'status': result.status,
                'content': str(result.content)[:100] + '...' if result.content and len(str(result.content)) > 100 else result.content,
                'error_message': result.error_message,
                'execution_time': result.execution_time,
                'timestamp': result.timestamp
            }
            for result in recent_history
        ]
    
    def _record_execution(self, result: ToolResult, execution_time: float) -> None:
        """
        记录执行结果
        
        学习要点：
        - 私有方法的使用
        - 统计数据的更新
        - 历史记录的管理
        
        Args:
            result: 执行结果
            execution_time: 执行时间
        """
        # 更新统计
        self._total_executions += 1
        self._total_execution_time += execution_time
        
        if result.is_success():
            self._successful_executions += 1
        else:
            self._failed_executions += 1
        
        # 记录历史（限制历史记录数量）
        self.execution_history.append(result)
        if len(self.execution_history) > 1000:  # 保持最近1000条记录
            self.execution_history = self.execution_history[-500:]  # 保留最近500条
    
    async def cleanup(self) -> None:
        """
        清理资源
        
        学习要点：
        - 异步资源的清理
        - 取消所有运行中的任务
        - 清理工具实例
        """
        try:
            # 取消所有运行中的任务
            cancelled_count = await self.cancel_all_tasks()
            if cancelled_count > 0 and self.enable_logging:
                logger.info(f"🧹 取消了 {cancelled_count} 个运行中的任务")
            
            # 清理各个工具
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'cleanup'):
                    try:
                        await tool.cleanup()
                        if self.enable_logging:
                            logger.info(f"🧹 清理工具: {tool_name}")
                    except Exception as e:
                        if self.enable_logging:
                            logger.error(f"❌ 清理工具 {tool_name} 失败: {e}")
            
            # 清理统计和历史记录
            self.execution_history.clear()
            self._total_executions = 0
            self._successful_executions = 0
            self._failed_executions = 0
            self._total_execution_time = 0.0
            
            if self.enable_logging:
                logger.info("✅ 工具管理器清理完成")
                
        except Exception as e:
            if self.enable_logging:
                logger.error(f"❌ 工具管理器清理异常: {e}")
            raise
    
    async def _create_error_task(self, error_message: str) -> ToolResult:
        """
        创建错误任务
        
        学习要点：
        - 辅助方法的设计
        - 错误处理的统一化
        - 异步方法的简单实现
        
        Args:
            error_message: 错误信息
            
        Returns:
            ToolResult: 错误结果
        """
        return ToolResult.error(error_message)
    
    @asynccontextmanager
    async def batch_execution_context(self):
        """
        批量执行上下文管理器
        
        💡 对比TypeScript:
        class BatchExecutionContext {
            private manager: AsyncToolManager;
            private startTime: number;
            
            constructor(manager: AsyncToolManager) {
                this.manager = manager;
            }
            
            async enter(): Promise<AsyncToolManager> {
                console.log("🚀 开始批量执行上下文");
                this.startTime = Date.now();
                return this.manager;
            }
            
            async exit(): Promise<void> {
                const duration = (Date.now() - this.startTime) / 1000;
                console.log(`✅ 批量执行上下文结束，耗时: ${duration.toFixed(2)}秒`);
                
                // 清理资源
                await this.manager.cancelAllTasks();
            }
        }
        
        学习要点：
        - 异步上下文管理器的实现
        - @asynccontextmanager 装饰器的使用
        - 资源管理和清理
        - 性能监控的集成
        """
        start_time = time.time()
        initial_executions = self._total_executions
        
        if self.enable_logging:
            logger.info("🚀 开始批量执行上下文")
        
        try:
            yield self
        finally:
            # 取消所有活跃任务
            await self.cancel_all_tasks()
            
            # 计算统计信息
            duration = time.time() - start_time
            executions_in_context = self._total_executions - initial_executions
            
            if self.enable_logging:
                logger.info(
                    f"✅ 批量执行上下文结束，"
                    f"耗时: {duration:.2f}秒，"
                    f"执行了 {executions_in_context} 个工具"
                )


# 测试代码
if __name__ == "__main__":
    """
    测试异步工具管理器的功能
    
    学习要点：
    - 异步测试的组织
    - 复杂场景的测试设计
    - 性能测试的实现
    """
    
    # 创建测试工具
    class FastTool(AsyncBaseTool):
        def __init__(self):
            super().__init__("fast_tool", "快速工具", timeout=5.0)
        
        @property
        def schema(self) -> Dict[str, Any]:
            return {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "输入值"}
                },
                "required": ["value"]
            }
        
        async def execute(self, **kwargs) -> ToolResult:
            value = kwargs.get('value', 0)
            await asyncio.sleep(0.1)  # 模拟快速操作
            return ToolResult.success(f"快速处理: {value * 2}")
    
    class SlowTool(AsyncBaseTool):
        def __init__(self):
            super().__init__("slow_tool", "慢速工具", timeout=10.0)
        
        @property
        def schema(self) -> Dict[str, Any]:
            return {
                "type": "object",
                "properties": {
                    "delay": {"type": "number", "description": "延迟时间"}
                },
                "required": ["delay"]
            }
        
        async def execute(self, **kwargs) -> ToolResult:
            delay = kwargs.get('delay', 1.0)
            await asyncio.sleep(delay)
            return ToolResult.success(f"慢速处理完成，延迟: {delay}秒")
    
    async def test_async_manager():
        """测试异步工具管理器"""
        print("🧪 测试异步工具管理器")
        print("=" * 50)
        
        # 创建管理器
        manager = AsyncToolManager(concurrency_limit=3)
        
        # 注册工具
        manager.register_tool(FastTool())
        manager.register_tool(SlowTool())
        
        # 测试单个工具执行
        print("\n1. 测试单个工具执行:")
        result = await manager.execute_tool("fast_tool", value=5)
        print(f"结果: {result.content}")
        
        # 测试并发执行
        print("\n2. 测试并发执行:")
        requests = [
            {"tool_name": "fast_tool", "params": {"value": i}}
            for i in range(5)
        ]
        
        start_time = time.time()
        results = await manager.execute_multiple(requests)
        duration = time.time() - start_time
        
        print(f"并发执行 {len(results)} 个任务，耗时: {duration:.2f}秒")
        for i, result in enumerate(results):
            print(f"  任务 {i+1}: {result.content}")
        
        # 测试管道执行
        print("\n3. 测试管道执行:")
        pipeline = [
            {"tool_name": "fast_tool", "params": {"value": 10}},
            {"tool_name": "slow_tool", "params": {"delay": 0.5}},
            {"tool_name": "fast_tool", "params": {"value": 20}}
        ]
        
        pipeline_results = await manager.execute_pipeline(pipeline)
        for i, result in enumerate(pipeline_results):
            print(f"  步骤 {i+1}: {result.content}")
        
        # 测试批量执行上下文
        print("\n4. 测试批量执行上下文:")
        async with manager.batch_execution_context():
            batch_requests = [
                {"tool_name": "fast_tool", "params": {"value": i}}
                for i in range(3)
            ]
            batch_results = await manager.execute_multiple(batch_requests)
            print(f"批量上下文中执行了 {len(batch_results)} 个任务")
        
        # 显示统计信息
        print("\n5. 统计信息:")
        stats = manager.get_execution_stats()
        for key, value in stats.items():
            if key != 'tool_stats':
                print(f"  {key}: {value}")
        
        # 显示最近历史
        print("\n6. 最近执行历史:")
        history = manager.get_recent_history(5)
        for i, record in enumerate(history):
            print(f"  {i+1}. 状态: {record['status']}, 时间: {record['execution_time']:.3f}s")
        
        print("\n✅ 异步工具管理器测试完成！")
    
    # 运行测试
    asyncio.run(test_async_manager())