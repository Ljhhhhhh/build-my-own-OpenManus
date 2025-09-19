"""
异步工具管理器

这个模块实现了异步工具的基础管理和执行功能。专注于异步编程的核心概念

学习要点：
1. 异步编程基础 (async/await)
2. 基础并发控制 (asyncio.Semaphore)
3. 异步工具的注册和管理
4. 简单的错误处理
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from .base import AsyncBaseTool, ToolResult


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncToolManager:
    """
    异步工具管理器
    
    💡 对比TypeScript:
    class AsyncToolManager {
        private tools: Map<string, AsyncBaseTool> = new Map();
        private concurrencyLimit: number;
        private semaphore: Semaphore;
        
        constructor(concurrencyLimit: number = 5) {
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
                return await tool.execute(params);
            } finally {
                this.semaphore.release();
            }
        }
    }
    
    学习要点：
    - 异步工具的注册和管理
    - 基础并发控制
    - 简单的错误处理
    """
    
    def __init__(self, concurrency_limit: int = 5):
        """
        初始化异步工具管理器
        
        学习要点：
        - 并发控制的基础概念
        - 数据结构的选择
        
        Args:
            concurrency_limit: 并发执行限制
        """
        self.tools: Dict[str, AsyncBaseTool] = {}
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)
    
    def register_tool(self, tool: AsyncBaseTool) -> None:
        """
        注册工具
        
        学习要点：
        - 工具的注册机制
        - 字典的使用
        
        Args:
            tool: 要注册的异步工具
        """
        if not isinstance(tool, AsyncBaseTool):
            raise TypeError("工具必须继承自 AsyncBaseTool")
        
        self.tools[tool.name] = tool
        logger.info(f"✅ 已注册工具: {tool.name}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否成功注销
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"🗑️ 已注销工具: {tool_name}")
            return True
        return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的工具
        
        Returns:
            List[Dict]: 工具信息列表
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "timeout": tool.timeout
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        执行指定工具
        
        学习要点：
        - 异步方法的实现
        - 并发控制的使用
        - 错误处理
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        # 检查工具是否存在
        if tool_name not in self.tools:
            return ToolResult.error(f"工具 '{tool_name}' 未找到")
        
        tool = self.tools[tool_name]
        
        # 使用信号量控制并发
        async with self.semaphore:
            try:
                logger.info(f"🚀 开始执行工具: {tool_name}")
                
                # 验证输入
                validation_result = await tool.validate_input(**kwargs)
                if validation_result is not True:
                    return ToolResult.invalid_input(str(validation_result))
                
                # 执行工具
                result = await tool.execute(**kwargs)
                
                if result.is_success():
                    logger.info(f"✅ 工具执行成功: {tool_name}")
                else:
                    logger.warning(f"⚠️ 工具执行失败: {tool_name} - {result.error_message}")
                
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"工具 '{tool_name}' 执行超时"
                logger.error(error_msg)
                return ToolResult.timeout(error_msg)
                
            except Exception as e:
                error_msg = f"工具 '{tool_name}' 执行异常: {str(e)}"
                logger.error(error_msg)
                return ToolResult.error(error_msg)
    
    async def execute_multiple(self, requests: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        并发执行多个工具
        
        学习要点：
        - asyncio.gather 的使用
        - 并发任务的管理
        
        Args:
            requests: 工具执行请求列表，格式: [{"tool_name": "xxx", "params": {...}}]
            
        Returns:
            List[ToolResult]: 执行结果列表
        """
        tasks = []
        for request in requests:
            tool_name = request.get("tool_name")
            params = request.get("params", {})
            
            if not tool_name:
                tasks.append(self._create_error_result("缺少工具名称"))
                continue
            
            task = self.execute_tool(tool_name, **params)
            tasks.append(task)
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(ToolResult.error(str(result)))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_tool_count(self) -> int:
        """获取已注册工具数量"""
        return len(self.tools)
    
    def has_tool(self, tool_name: str) -> bool:
        """检查是否有指定工具"""
        return tool_name in self.tools
    
    def get_tool(self, tool_name: str) -> Optional[AsyncBaseTool]:
        """获取指定工具实例"""
        return self.tools.get(tool_name)
    
    async def cleanup(self) -> None:
        """
        清理资源
        
        学习要点：
        - 资源清理的重要性
        - 异步清理操作
        """
        logger.info("🧹 开始清理工具管理器...")
        
        # 清理所有工具
        for tool in self.tools.values():
            if hasattr(tool, 'cleanup'):
                try:
                    await tool.cleanup()
                except Exception as e:
                    logger.warning(f"清理工具 {tool.name} 时出错: {e}")
        
        self.tools.clear()
        logger.info("✅ 工具管理器清理完成")
    
    def _create_error_result(self, error_message: str) -> ToolResult:
        """创建错误结果"""
        return ToolResult.error(error_message)


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    # 简单的测试工具
    class TestTool(AsyncBaseTool):
        def __init__(self, name: str, delay: float = 1.0):
            super().__init__(name, f"测试工具 {name}")
            self.delay = delay
        
        @property
        def schema(self) -> Dict[str, Any]:
            return {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "测试消息"}
                }
            }
        
        async def execute(self, **kwargs) -> ToolResult:
            message = kwargs.get("message", "Hello")
            await asyncio.sleep(self.delay)  # 模拟异步操作
            return ToolResult.success(f"{self.name}: {message}")
    
    async def test_async_manager():
        """测试异步工具管理器"""
        print("🧪 测试异步工具管理器")
        print("=" * 40)
        
        # 创建管理器
        manager = AsyncToolManager(concurrency_limit=3)
        
        # 注册工具
        manager.register_tool(TestTool("fast", 0.5))
        manager.register_tool(TestTool("slow", 2.0))
        
        print(f"已注册工具数量: {manager.get_tool_count()}")
        print("工具列表:", manager.list_tools())
        
        # 单个工具执行
        print("\n🚀 测试单个工具执行:")
        result = await manager.execute_tool("fast", message="单个测试")
        print(f"结果: {result.content}")
        
        # 并发执行
        print("\n🚀 测试并发执行:")
        requests = [
            {"tool_name": "fast", "params": {"message": "并发1"}},
            {"tool_name": "slow", "params": {"message": "并发2"}},
            {"tool_name": "fast", "params": {"message": "并发3"}}
        ]
        
        results = await manager.execute_multiple(requests)
        for i, result in enumerate(results):
            print(f"任务 {i+1}: {result.content}")
        
        # 清理
        await manager.cleanup()
        print("\n✅ 测试完成!")
    
    # 运行测试
    asyncio.run(test_async_manager())