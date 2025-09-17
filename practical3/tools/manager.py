"""
工具管理器 - 工具的注册、管理和执行

这个模块实现了工具管理器，负责：
1. 工具的注册和注销
2. 工具的发现和查找
3. 工具的执行和结果处理
4. 批量工具操作

学习要点：
1. 管理器模式的实现
2. 字典作为注册表的使用
3. 异步并发执行
4. 错误处理和日志记录
5. 类型注解和文档字符串
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from .base import BaseTool, ToolResult, ToolResultStatus


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolManager:
    """
    工具管理器类
    
    负责管理所有注册的工具，提供统一的接口来执行工具操作。
    
    学习要点：
    - 单例模式的简单实现（可选）
    - 工具注册表的管理
    - 异步方法的组织
    """
    
    def __init__(self):
        """
        初始化工具管理器
        
        学习要点：
        - 使用字典作为工具注册表
        - 初始化统计信息
        """
        self._tools: Dict[str, BaseTool] = {}
        self._execution_stats: Dict[str, Dict[str, Any]] = {}
        logger.info("工具管理器初始化完成")
    
    def register_tool(self, tool: BaseTool) -> bool:
        """
        注册一个工具
        
        学习要点：
        - 参数类型检查
        - 重复注册的处理
        - 返回值的语义化
        
        Args:
            tool: 要注册的工具实例
            
        Returns:
            bool: 注册是否成功
        """
        if not isinstance(tool, BaseTool):
            logger.error(f"注册失败：{tool} 不是 BaseTool 的实例")
            return False
        
        if tool.name in self._tools:
            logger.warning(f"工具 '{tool.name}' 已存在，将被覆盖")
        
        self._tools[tool.name] = tool
        self._execution_stats[tool.name] = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
        
        logger.info(f"工具 '{tool.name}' 注册成功")
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销一个工具
        
        Args:
            tool_name: 要注销的工具名称
            
        Returns:
            bool: 注销是否成功
        """
        if tool_name not in self._tools:
            logger.warning(f"工具 '{tool_name}' 不存在，无法注销")
            return False
        
        del self._tools[tool_name]
        del self._execution_stats[tool_name]
        logger.info(f"工具 '{tool_name}' 注销成功")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取指定名称的工具
        
        学习要点：
        - Optional类型的使用
        - 字典的get方法
        
        Args:
            tool_name: 工具名称
            
        Returns:
            BaseTool或None: 找到的工具实例，如果不存在则返回None
        """
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的工具信息
        
        学习要点：
        - 列表推导式的使用
        - 字典的values()方法
        
        Returns:
            List[Dict]: 工具信息列表
        """
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'schema': tool.schema,
                'stats': self._execution_stats.get(tool.name, {})
            }
            for tool in self._tools.values()
        ]
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定工具的JSON Schema
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Dict或None: 工具的schema，如果工具不存在则返回None
        """
        tool = self.get_tool(tool_name)
        return tool.schema if tool else None
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        执行指定的工具
        
        学习要点：
        - 异步方法的实现
        - 统计信息的更新
        - 完整的错误处理
        
        Args:
            tool_name: 要执行的工具名称
            **kwargs: 传递给工具的参数
            
        Returns:
            ToolResult: 工具执行结果
        """
        start_time = time.time()
        
        # 检查工具是否存在
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult.error(
                error_message=f"工具 '{tool_name}' 不存在",
                metadata={'available_tools': list(self._tools.keys())}
            )
        
        try:
            logger.info(f"开始执行工具 '{tool_name}'，参数: {kwargs}")
            
            # 执行工具
            result = await tool.execute(**kwargs)
            
            # 更新统计信息
            execution_time = time.time() - start_time
            self._update_stats(tool_name, result.status, execution_time)
            
            logger.info(f"工具 '{tool_name}' 执行完成，状态: {result.status}")
            return result
            
        except Exception as e:
            # 处理未捕获的异常
            execution_time = time.time() - start_time
            self._update_stats(tool_name, ToolResultStatus.ERROR, execution_time)
            
            logger.error(f"工具 '{tool_name}' 执行时发生异常: {e}")
            return ToolResult.error(
                error_message=f"工具执行异常: {e}",
                execution_time=execution_time
            )
    
    async def execute_tools_batch(self, tool_requests: List[Dict[str, Any]], 
                                  max_concurrent: int = 5) -> List[ToolResult]:
        """
        批量执行多个工具
        
        学习要点：
        - asyncio.Semaphore控制并发数
        - asyncio.gather并发执行
        - 批量操作的实现
        
        Args:
            tool_requests: 工具请求列表，每个请求包含tool_name和参数
            max_concurrent: 最大并发数
            
        Returns:
            List[ToolResult]: 执行结果列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(request: Dict[str, Any]) -> ToolResult:
            """带信号量控制的工具执行"""
            async with semaphore:
                tool_name = request.get('tool_name')
                params = request.get('params', {})
                
                if not tool_name:
                    return ToolResult.invalid_input("缺少tool_name参数")
                
                return await self.execute_tool(tool_name, **params)
        
        logger.info(f"开始批量执行 {len(tool_requests)} 个工具，最大并发数: {max_concurrent}")
        
        # 并发执行所有工具
        results = await asyncio.gather(
            *[execute_with_semaphore(request) for request in tool_requests],
            return_exceptions=True
        )
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ToolResult.error(f"批量执行异常: {result}")
                )
            else:
                processed_results.append(result)
        
        logger.info(f"批量执行完成，成功: {sum(1 for r in processed_results if r.status == ToolResultStatus.SUCCESS)}")
        return processed_results
    
    def _update_stats(self, tool_name: str, status: ToolResultStatus, 
                      execution_time: float) -> None:
        """
        更新工具执行统计信息
        
        学习要点：
        - 私有方法的命名约定（下划线开头）
        - 统计信息的计算和更新
        
        Args:
            tool_name: 工具名称
            status: 执行状态
            execution_time: 执行时间
        """
        if tool_name not in self._execution_stats:
            return
        
        stats = self._execution_stats[tool_name]
        stats['total_executions'] += 1
        stats['total_execution_time'] += execution_time
        
        if status == ToolResultStatus.SUCCESS:
            stats['successful_executions'] += 1
        else:
            stats['failed_executions'] += 1
        
        # 计算平均执行时间
        if stats['total_executions'] > 0:
            stats['average_execution_time'] = (
                stats['total_execution_time'] / stats['total_executions']
            )
    
    def get_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取工具执行统计信息
        
        Args:
            tool_name: 工具名称，如果为None则返回所有工具的统计
            
        Returns:
            Dict: 统计信息
        """
        if tool_name:
            return self._execution_stats.get(tool_name, {})
        else:
            return {
                'tools': dict(self._execution_stats),
                'summary': {
                    'total_tools': len(self._tools),
                    'total_executions': sum(
                        stats['total_executions'] 
                        for stats in self._execution_stats.values()
                    ),
                    'total_successful': sum(
                        stats['successful_executions'] 
                        for stats in self._execution_stats.values()
                    ),
                    'total_failed': sum(
                        stats['failed_executions'] 
                        for stats in self._execution_stats.values()
                    )
                }
            }
    
    def clear_stats(self, tool_name: Optional[str] = None) -> None:
        """
        清除统计信息
        
        Args:
            tool_name: 工具名称，如果为None则清除所有统计
        """
        if tool_name and tool_name in self._execution_stats:
            self._execution_stats[tool_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_execution_time': 0.0,
                'average_execution_time': 0.0
            }
            logger.info(f"已清除工具 '{tool_name}' 的统计信息")
        elif tool_name is None:
            for name in self._execution_stats:
                self._execution_stats[name] = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'total_execution_time': 0.0,
                    'average_execution_time': 0.0
                }
            logger.info("已清除所有工具的统计信息")
    
    def __len__(self) -> int:
        """返回已注册工具的数量"""
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """检查工具是否已注册"""
        return tool_name in self._tools
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ToolManager(tools={len(self._tools)})"
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示"""
        tool_names = list(self._tools.keys())
        return f"<ToolManager(tools={tool_names})>"


# 使用示例和测试代码
if __name__ == "__main__":
    """
    模块测试代码
    """
    import asyncio
    from .calculator import CalculatorTool
    
    async def test_tool_manager():
        """测试工具管理器的各种功能"""
        # 创建管理器和工具
        manager = ToolManager()
        calc_tool = CalculatorTool()
        
        print("=== 工具管理器测试 ===")
        
        # 测试工具注册
        print(f"注册计算器工具: {manager.register_tool(calc_tool)}")
        print(f"工具数量: {len(manager)}")
        print(f"包含calculator: {'calculator' in manager}")
        
        # 测试工具列表
        print("\n已注册的工具:")
        for tool_info in manager.list_tools():
            print(f"- {tool_info['name']}: {tool_info['description']}")
        
        # 测试单个工具执行
        print("\n=== 单个工具执行测试 ===")
        result = await manager.execute_tool('calculator', expression='2 + 3 * 4')
        print(f"计算结果: {result}")
        
        # 测试批量执行
        print("\n=== 批量执行测试 ===")
        batch_requests = [
            {'tool_name': 'calculator', 'params': {'expression': '1 + 1'}},
            {'tool_name': 'calculator', 'params': {'expression': '2 * 3'}},
            {'tool_name': 'calculator', 'params': {'expression': '10 / 2'}},
            {'tool_name': 'nonexistent', 'params': {}},  # 测试不存在的工具
        ]
        
        batch_results = await manager.execute_tools_batch(batch_requests)
        for i, result in enumerate(batch_results):
            print(f"批量结果 {i+1}: {result.status} - {result.content or result.error_message}")
        
        # 测试统计信息
        print("\n=== 统计信息 ===")
        stats = manager.get_stats()
        print(f"总体统计: {stats['summary']}")
        print(f"计算器统计: {stats['tools'].get('calculator', {})}")
    
    # 运行测试
    asyncio.run(test_tool_manager())