"""
工具管理器 - 基础版本

这个模块实现了一个简化的工具管理系统，专注于Python基础概念。
避免复杂的异步编程，使用同步方式处理工具的注册、管理和执行。

学习要点：
1. 类的设计和实现
2. 字典的使用和管理
3. 异常处理
4. 统计和监控
5. 方法的组织和命名
"""

from typing import Dict, List, Any, Optional
from .base import BaseTool, ToolResult


class ToolManager:
    """
    工具管理器 - 简化版本
    
    负责管理所有工具的注册、执行和统计。
    
    💡 对比TypeScript:
    class ToolManager {
        private tools: Map<string, BaseTool> = new Map();
        private stats: Map<string, number> = new Map();
        
        register(tool: BaseTool): void { ... }
        execute(toolName: string, params: any): ToolResult { ... }
        getStats(): any { ... }
    }
    
    学习要点：
    - 类的属性管理
    - 字典作为数据存储
    - 方法的设计和实现
    - 统计功能的实现
    """
    
    def __init__(self):
        """
        初始化工具管理器
        
        学习要点：
        - 实例属性的初始化
        - 字典的创建和用途
        - 统计数据的设计
        """
        # 存储所有注册的工具 {工具名: 工具实例}
        self._tools: Dict[str, BaseTool] = {}
        
        # 统计信息
        self._stats = {
            'total_executions': 0,      # 总执行次数
            'successful_executions': 0,  # 成功执行次数
            'failed_executions': 0,     # 失败执行次数
            'tool_usage': {}            # 每个工具的使用统计
        }
        
        print("🔧 工具管理器已初始化")
    
    def register_tool(self, tool: BaseTool) -> bool:
        """
        注册一个工具
        
        💡 对比TypeScript:
        register(tool: BaseTool): boolean {
            if (this.tools.has(tool.name)) {
                console.warn(`工具 ${tool.name} 已存在`);
                return false;
            }
            this.tools.set(tool.name, tool);
            this.stats.set(tool.name, 0);
            return true;
        }
        
        学习要点：
        - 参数类型注解
        - 字典的键值操作
        - 条件判断和返回值
        - 基础的重复检查逻辑
        
        Args:
            tool: 要注册的工具实例
            
        Returns:
            bool: 注册是否成功
        """
        if not isinstance(tool, BaseTool):
            print(f"❌ 错误：传入的对象不是BaseTool的实例")
            return False
        
        tool_name = tool.name
        
        # 检查工具是否已存在
        if tool_name in self._tools:
            print(f"⚠️  警告：工具 '{tool_name}' 已存在，跳过注册")
            return False
        
        # 注册工具
        self._tools[tool_name] = tool
        
        # 初始化统计信息
        self._stats['tool_usage'][tool_name] = {
            'executions': 0,
            'successes': 0,
            'failures': 0
        }
        
        print(f"✅ 工具 '{tool_name}' 注册成功")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取指定名称的工具
        
        💡 对比TypeScript:
        getTool(toolName: string): BaseTool | null {
            return this.tools.get(toolName) || null;
        }
        
        学习要点：
        - Optional类型注解的使用
        - 字典的get方法
        - None的使用
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[BaseTool]: 工具实例或None
        """
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        获取所有已注册工具的名称列表
        
        💡 对比TypeScript:
        listTools(): string[] {
            return Array.from(this.tools.keys());
        }
        
        学习要点：
        - 字典的keys()方法
        - list()转换
        - 返回类型注解
        
        Returns:
            List[str]: 工具名称列表
        """
        return list(self._tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具的详细信息
        
        学习要点：
        - 字典的构建和返回
        - 条件判断
        - 信息的组织和展示
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[Dict[str, Any]]: 工具信息字典或None
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            return None
        
        return {
            'name': tool.name,
            'description': tool.description,
            'schema': tool.schema,
            'usage_stats': self._stats['tool_usage'].get(tool_name, {})
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        执行指定的工具
        
        💡 对比TypeScript:
        execute(toolName: string, params: any): ToolResult {
            const tool = this.getTool(toolName);
            if (!tool) {
                return ToolResult.error(`工具 ${toolName} 不存在`);
            }
            
            try {
                this.updateStats(toolName, 'total');
                const result = tool.execute(params);
                this.updateStats(toolName, result.status === 'success' ? 'success' : 'failure');
                return result;
            } catch (error) {
                this.updateStats(toolName, 'failure');
                return ToolResult.error(error.message);
            }
        }
        
        学习要点：
        - 工具的查找和验证
        - 异常处理机制
        - 统计信息的更新
        - 方法调用和结果处理
        
        Args:
            tool_name: 要执行的工具名称
            **kwargs: 传递给工具的参数
            
        Returns:
            ToolResult: 执行结果
        """
        # 1. 查找工具
        tool = self.get_tool(tool_name)
        if tool is None:
            error_msg = f"工具 '{tool_name}' 不存在。可用工具: {', '.join(self.list_tools())}"
            return ToolResult.error(error_msg)
        
        # 2. 更新统计 - 总执行次数
        self._update_stats(tool_name, 'execution')
        
        try:
            # 3. 执行工具
            print(f"🔧 执行工具: {tool_name}")
            result = tool.execute(**kwargs)
            
            # 4. 更新统计 - 根据结果
            if result.status == 'success':
                self._update_stats(tool_name, 'success')
                print(f"✅ 工具 '{tool_name}' 执行成功")
            else:
                self._update_stats(tool_name, 'failure')
                print(f"❌ 工具 '{tool_name}' 执行失败: {result.error_message}")
            
            return result
            
        except Exception as e:
            # 5. 处理未预期的异常
            self._update_stats(tool_name, 'failure')
            error_msg = f"执行工具 '{tool_name}' 时发生异常: {str(e)}"
            print(f"💥 {error_msg}")
            return ToolResult.error(error_msg)
    
    def _update_stats(self, tool_name: str, stat_type: str):
        """
        更新统计信息
        
        学习要点：
        - 私有方法的命名和使用
        - 统计数据的维护
        - 字典的嵌套操作
        
        Args:
            tool_name: 工具名称
            stat_type: 统计类型 ('execution', 'success', 'failure')
        """
        # 更新总体统计
        if stat_type == 'execution':
            self._stats['total_executions'] += 1
        elif stat_type == 'success':
            self._stats['successful_executions'] += 1
        elif stat_type == 'failure':
            self._stats['failed_executions'] += 1
        
        # 更新工具特定统计
        if tool_name in self._stats['tool_usage']:
            tool_stats = self._stats['tool_usage'][tool_name]
            if stat_type == 'execution':
                tool_stats['executions'] += 1
            elif stat_type == 'success':
                tool_stats['successes'] += 1
            elif stat_type == 'failure':
                tool_stats['failures'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        💡 对比TypeScript:
        getStats(): any {
            return {
                total: this.stats.get('total') || 0,
                successful: this.stats.get('successful') || 0,
                failed: this.stats.get('failed') || 0,
                toolUsage: Object.fromEntries(this.toolStats)
            };
        }
        
        学习要点：
        - 字典的复制和返回
        - 统计数据的组织
        - 计算成功率
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        total = self._stats['total_executions']
        success_rate = (self._stats['successful_executions'] / total * 100) if total > 0 else 0
        
        return {
            'summary': {
                'total_executions': total,
                'successful_executions': self._stats['successful_executions'],
                'failed_executions': self._stats['failed_executions'],
                'success_rate': f"{success_rate:.1f}%"
            },
            'registered_tools': len(self._tools),
            'tool_usage': self._stats['tool_usage'].copy()
        }
    
    def print_stats(self):
        """
        打印统计信息
        
        学习要点：
        - 格式化输出
        - 数据的展示和组织
        - 字符串格式化
        """
        stats = self.get_stats()
        
        print("\n" + "=" * 50)
        print("📊 工具管理器统计信息")
        print("=" * 50)
        
        # 总体统计
        summary = stats['summary']
        print(f"总执行次数: {summary['total_executions']}")
        print(f"成功次数: {summary['successful_executions']}")
        print(f"失败次数: {summary['failed_executions']}")
        print(f"成功率: {summary['success_rate']}")
        print(f"注册工具数: {stats['registered_tools']}")
        
        # 工具使用详情
        if stats['tool_usage']:
            print("\n🔧 工具使用详情:")
            for tool_name, usage in stats['tool_usage'].items():
                print(f"  {tool_name}:")
                print(f"    执行: {usage['executions']} 次")
                print(f"    成功: {usage['successes']} 次")
                print(f"    失败: {usage['failures']} 次")
        
        print("=" * 50)
    
    def clear_stats(self):
        """
        清空统计信息
        
        学习要点：
        - 数据的重置
        - 字典的清空和重新初始化
        """
        self._stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'tool_usage': {}
        }
        
        # 重新初始化每个工具的统计
        for tool_name in self._tools.keys():
            self._stats['tool_usage'][tool_name] = {
                'executions': 0,
                'successes': 0,
                'failures': 0
            }
        
        print("🧹 统计信息已清空")


# 测试代码
if __name__ == "__main__":
    """
    测试工具管理器的基本功能
    
    学习要点：
    - 完整的测试流程
    - 工具的注册和使用
    - 统计功能的验证
    """
    from .calculator import CalculatorTool
    
    print("🔧 测试工具管理器")
    print("=" * 40)
    
    # 创建管理器
    manager = ToolManager()
    
    # 注册工具
    calculator = CalculatorTool()
    manager.register_tool(calculator)
    
    # 测试工具列表
    print(f"\n注册的工具: {manager.list_tools()}")
    
    # 测试工具执行
    test_cases = [
        ("calculator", {"operation": "add", "a": 10, "b": 5}),
        ("calculator", {"operation": "multiply", "a": 6, "b": 7}),
        ("calculator", {"operation": "divide", "a": 10, "b": 0}),  # 错误测试
        ("nonexistent", {"test": "data"}),  # 不存在的工具
    ]
    
    for tool_name, params in test_cases:
        print(f"\n执行: {tool_name} with {params}")
        result = manager.execute_tool(tool_name, **params)
        print(f"结果状态: {result.status}")
        if result.status == "success":
            print(f"内容: {result.content}")
        else:
            print(f"错误: {result.error_message}")
    
    # 显示统计信息
    manager.print_stats()
    
    print("\n✅ 测试完成！")