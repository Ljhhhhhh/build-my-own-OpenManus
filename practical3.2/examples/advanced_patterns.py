"""
Practical 3.2 - 高级模式示例

这个示例展示了异步工具框架的高级使用模式，包括：
1. 自定义工具的创建
2. 工具链的组合使用
3. 动态工具加载
4. 性能监控和优化
5. 生产级的错误处理

学习要点：
1. 高级异步编程模式
2. 工具扩展的设计
3. 性能优化的技巧
4. 生产级代码的组织
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base import AsyncBaseTool, ToolResult, ToolResultStatus
from tools import AsyncToolManager, AsyncCalculatorTool, AsyncWeatherTool
from config import Config


@dataclass
class PerformanceMetrics:
    """
    性能指标数据类
    
    💡 对比TypeScript:
    interface PerformanceMetrics {
        toolName: string;
        operationCount: number;
        totalTime: number;
        averageTime: number;
        successRate: number;
        errorCount: number;
        minTime: number;
        maxTime: number;
        throughput: number;
    }
    
    学习要点：
    - 数据类的使用
    - 性能指标的定义
    - 类型注解的完整性
    """
    tool_name: str
    operation_count: int
    total_time: float
    average_time: float
    success_rate: float
    error_count: int
    min_time: float
    max_time: float
    throughput: float


class CustomDataProcessorTool(AsyncBaseTool):
    """
    自定义数据处理工具
    
    💡 对比TypeScript:
    class CustomDataProcessorTool extends AsyncBaseTool {
        name = "data_processor";
        description = "高级数据处理工具，支持多种数据操作";
        timeout = 20.0;
        maxRetries = 2;
        
        get schema() {
            return {
                type: "object",
                properties: {
                    operation: {
                        type: "string",
                        enum: ["sort", "filter", "map", "reduce", "group", "aggregate"],
                        description: "数据处理操作类型"
                    },
                    data: {
                        type: "array",
                        description: "要处理的数据数组"
                    },
                    condition: {
                        type: "string",
                        description: "过滤或处理条件（可选）"
                    },
                    key: {
                        type: "string",
                        description: "分组或排序的键（可选）"
                    }
                },
                required: ["operation", "data"]
            };
        }
        
        async execute(params: any): Promise<ToolResult> {
            const { operation, data, condition, key } = params;
            
            try {
                let result: any;
                
                switch (operation) {
                    case "sort":
                        result = this.sortData(data, key);
                        break;
                    case "filter":
                        result = this.filterData(data, condition);
                        break;
                    case "map":
                        result = this.mapData(data, condition);
                        break;
                    case "reduce":
                        result = this.reduceData(data, condition);
                        break;
                    case "group":
                        result = this.groupData(data, key);
                        break;
                    case "aggregate":
                        result = this.aggregateData(data, key);
                        break;
                    default:
                        throw new Error(`不支持的操作: ${operation}`);
                }
                
                return ToolResult.success(
                    JSON.stringify(result, null, 2),
                    {
                        operation,
                        inputSize: data.length,
                        outputSize: Array.isArray(result) ? result.length : 1,
                        processingTime: Date.now()
                    }
                );
            } catch (error) {
                return ToolResult.error(`数据处理失败: ${error.message}`);
            }
        }
        
        private sortData(data: any[], key?: string): any[] {
            if (key) {
                return [...data].sort((a, b) => {
                    const aVal = a[key];
                    const bVal = b[key];
                    return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
                });
            } else {
                return [...data].sort();
            }
        }
        
        private filterData(data: any[], condition: string): any[] {
            // 简单的条件过滤实现
            const func = new Function('item', `return ${condition}`);
            return data.filter(func);
        }
        
        private mapData(data: any[], condition: string): any[] {
            const func = new Function('item', `return ${condition}`);
            return data.map(func);
        }
        
        private reduceData(data: any[], condition: string): any {
            const func = new Function('acc', 'item', `return ${condition}`);
            return data.reduce(func, 0);
        }
        
        private groupData(data: any[], key: string): Record<string, any[]> {
            return data.reduce((groups, item) => {
                const groupKey = item[key];
                if (!groups[groupKey]) {
                    groups[groupKey] = [];
                }
                groups[groupKey].push(item);
                return groups;
            }, {});
        }
        
        private aggregateData(data: any[], key: string): Record<string, number> {
            const groups = this.groupData(data, key);
            const result: Record<string, number> = {};
            
            for (const [groupKey, items] of Object.entries(groups)) {
                result[groupKey] = items.length;
            }
            
            return result;
        }
    }
    
    学习要点：
    - 自定义工具的完整实现
    - 复杂业务逻辑的处理
    - 数据处理算法的实现
    - 错误处理的完整性
    """
    
    def __init__(self):
        super().__init__(
            name="data_processor",
            description="高级数据处理工具，支持多种数据操作",
            timeout=20.0,
            max_retries=2
        )
    
    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["sort", "filter", "map", "reduce", "group", "aggregate"],
                    "description": "数据处理操作类型"
                },
                "data": {
                    "type": "array",
                    "description": "要处理的数据数组"
                },
                "condition": {
                    "type": "string",
                    "description": "过滤或处理条件（可选）"
                },
                "key": {
                    "type": "string",
                    "description": "分组或排序的键（可选）"
                }
            },
            "required": ["operation", "data"]
        }
    
    async def execute(self, **params) -> ToolResult:
        """
        执行数据处理操作
        
        学习要点：
        - 复杂参数的处理
        - 多种操作的分发
        - 异步处理的实现
        - 结果封装的标准化
        """
        operation = params.get("operation")
        data = params.get("data", [])
        condition = params.get("condition")
        key = params.get("key")
        
        try:
            # 模拟异步处理时间
            await asyncio.sleep(0.1)
            
            result = None
            
            if operation == "sort":
                result = await self._sort_data(data, key)
            elif operation == "filter":
                result = await self._filter_data(data, condition)
            elif operation == "map":
                result = await self._map_data(data, condition)
            elif operation == "reduce":
                result = await self._reduce_data(data, condition)
            elif operation == "group":
                result = await self._group_data(data, key)
            elif operation == "aggregate":
                result = await self._aggregate_data(data, key)
            else:
                return ToolResult.error(f"不支持的操作: {operation}")
            
            return ToolResult.success(
                json.dumps(result, ensure_ascii=False, indent=2),
                metadata={
                    "operation": operation,
                    "input_size": len(data),
                    "output_size": len(result) if isinstance(result, (list, dict)) else 1,
                    "processing_time": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult.error(f"数据处理失败: {str(e)}")
    
    async def _sort_data(self, data: List[Any], key: Optional[str] = None) -> List[Any]:
        """排序数据"""
        if key:
            return sorted(data, key=lambda x: x.get(key, 0) if isinstance(x, dict) else x)
        else:
            return sorted(data)
    
    async def _filter_data(self, data: List[Any], condition: str) -> List[Any]:
        """过滤数据"""
        if not condition:
            return data
        
        # 简单的条件过滤（生产环境需要更安全的实现）
        try:
            if ">" in condition:
                key, value = condition.split(">")
                key, value = key.strip(), float(value.strip())
                return [item for item in data if isinstance(item, dict) and item.get(key, 0) > value]
            elif "<" in condition:
                key, value = condition.split("<")
                key, value = key.strip(), float(value.strip())
                return [item for item in data if isinstance(item, dict) and item.get(key, 0) < value]
            elif "==" in condition:
                key, value = condition.split("==")
                key, value = key.strip(), value.strip().strip('"\'')
                return [item for item in data if isinstance(item, dict) and str(item.get(key, "")) == value]
            else:
                return data
        except Exception:
            return data
    
    async def _map_data(self, data: List[Any], condition: str) -> List[Any]:
        """映射数据"""
        if not condition:
            return data
        
        # 简单的映射操作
        try:
            if condition == "square":
                return [x * x if isinstance(x, (int, float)) else x for x in data]
            elif condition == "double":
                return [x * 2 if isinstance(x, (int, float)) else x for x in data]
            elif condition == "upper":
                return [str(x).upper() if isinstance(x, str) else x for x in data]
            elif condition == "lower":
                return [str(x).lower() if isinstance(x, str) else x for x in data]
            else:
                return data
        except Exception:
            return data
    
    async def _reduce_data(self, data: List[Any], condition: str) -> Any:
        """归约数据"""
        if not condition or not data:
            return 0
        
        try:
            if condition == "sum":
                return sum(x for x in data if isinstance(x, (int, float)))
            elif condition == "avg":
                numbers = [x for x in data if isinstance(x, (int, float))]
                return sum(numbers) / len(numbers) if numbers else 0
            elif condition == "max":
                numbers = [x for x in data if isinstance(x, (int, float))]
                return max(numbers) if numbers else 0
            elif condition == "min":
                numbers = [x for x in data if isinstance(x, (int, float))]
                return min(numbers) if numbers else 0
            elif condition == "count":
                return len(data)
            else:
                return 0
        except Exception:
            return 0
    
    async def _group_data(self, data: List[Any], key: str) -> Dict[str, List[Any]]:
        """分组数据"""
        if not key:
            return {"all": data}
        
        groups = {}
        for item in data:
            if isinstance(item, dict):
                group_key = str(item.get(key, "unknown"))
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(item)
            else:
                if "other" not in groups:
                    groups["other"] = []
                groups["other"].append(item)
        
        return groups
    
    async def _aggregate_data(self, data: List[Any], key: str) -> Dict[str, int]:
        """聚合数据"""
        groups = await self._group_data(data, key)
        return {group_key: len(items) for group_key, items in groups.items()}


class PerformanceMonitor:
    """
    性能监控器
    
    💡 对比TypeScript:
    class PerformanceMonitor {
        private metrics: Map<string, PerformanceMetrics> = new Map();
        private isMonitoring: boolean = false;
        
        startMonitoring(): void {
            this.isMonitoring = true;
            console.log("🔍 开始性能监控");
        }
        
        stopMonitoring(): void {
            this.isMonitoring = false;
            console.log("⏹️  停止性能监控");
        }
        
        recordExecution(toolName: string, executionTime: number, success: boolean): void {
            if (!this.isMonitoring) return;
            
            let metric = this.metrics.get(toolName);
            if (!metric) {
                metric = {
                    toolName,
                    operationCount: 0,
                    totalTime: 0,
                    averageTime: 0,
                    successRate: 0,
                    errorCount: 0,
                    minTime: Infinity,
                    maxTime: 0,
                    throughput: 0
                };
                this.metrics.set(toolName, metric);
            }
            
            metric.operationCount++;
            metric.totalTime += executionTime;
            metric.averageTime = metric.totalTime / metric.operationCount;
            
            if (success) {
                metric.successRate = ((metric.operationCount - metric.errorCount) / metric.operationCount) * 100;
            } else {
                metric.errorCount++;
                metric.successRate = ((metric.operationCount - metric.errorCount) / metric.operationCount) * 100;
            }
            
            metric.minTime = Math.min(metric.minTime, executionTime);
            metric.maxTime = Math.max(metric.maxTime, executionTime);
            metric.throughput = 1000 / metric.averageTime; // ops per second
        }
        
        getMetrics(): PerformanceMetrics[] {
            return Array.from(this.metrics.values());
        }
        
        generateReport(): string {
            const metrics = this.getMetrics();
            let report = "📊 性能监控报告\\n";
            report += "=".repeat(50) + "\\n";
            
            for (const metric of metrics) {
                report += `\\n🔧 工具: ${metric.toolName}\\n`;
                report += `  执行次数: ${metric.operationCount}\\n`;
                report += `  总耗时: ${metric.totalTime.toFixed(2)}ms\\n`;
                report += `  平均耗时: ${metric.averageTime.toFixed(2)}ms\\n`;
                report += `  成功率: ${metric.successRate.toFixed(1)}%\\n`;
                report += `  错误次数: ${metric.errorCount}\\n`;
                report += `  最短耗时: ${metric.minTime.toFixed(2)}ms\\n`;
                report += `  最长耗时: ${metric.maxTime.toFixed(2)}ms\\n`;
                report += `  吞吐量: ${metric.throughput.toFixed(2)} ops/sec\\n`;
            }
            
            return report;
        }
        
        reset(): void {
            this.metrics.clear();
            console.log("🔄 性能指标已重置");
        }
    }
    
    学习要点：
    - 性能监控的设计模式
    - 指标收集和计算
    - 报告生成的实现
    - 状态管理的重要性
    """
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.is_monitoring = False
        self.start_time = None
    
    def start_monitoring(self):
        """开始性能监控"""
        self.is_monitoring = True
        self.start_time = datetime.now()
        print("🔍 开始性能监控")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        print("⏹️  停止性能监控")
    
    def record_execution(self, tool_name: str, execution_time: float, success: bool):
        """记录执行性能"""
        if not self.is_monitoring:
            return
        
        if tool_name not in self.metrics:
            self.metrics[tool_name] = PerformanceMetrics(
                tool_name=tool_name,
                operation_count=0,
                total_time=0.0,
                average_time=0.0,
                success_rate=0.0,
                error_count=0,
                min_time=float('inf'),
                max_time=0.0,
                throughput=0.0
            )
        
        metric = self.metrics[tool_name]
        metric.operation_count += 1
        metric.total_time += execution_time
        metric.average_time = metric.total_time / metric.operation_count
        
        if not success:
            metric.error_count += 1
        
        success_count = metric.operation_count - metric.error_count
        metric.success_rate = (success_count / metric.operation_count) * 100
        
        metric.min_time = min(metric.min_time, execution_time)
        metric.max_time = max(metric.max_time, execution_time)
        
        if metric.average_time > 0:
            metric.throughput = 1000 / metric.average_time  # ops per second
    
    def get_metrics(self) -> List[PerformanceMetrics]:
        """获取性能指标"""
        return list(self.metrics.values())
    
    def generate_report(self) -> str:
        """生成性能报告"""
        metrics = self.get_metrics()
        
        report = "📊 性能监控报告\n"
        report += "=" * 50 + "\n"
        
        if self.start_time:
            monitoring_duration = (datetime.now() - self.start_time).total_seconds()
            report += f"监控时长: {monitoring_duration:.2f}秒\n"
        
        for metric in metrics:
            report += f"\n🔧 工具: {metric.tool_name}\n"
            report += f"  执行次数: {metric.operation_count}\n"
            report += f"  总耗时: {metric.total_time:.2f}ms\n"
            report += f"  平均耗时: {metric.average_time:.2f}ms\n"
            report += f"  成功率: {metric.success_rate:.1f}%\n"
            report += f"  错误次数: {metric.error_count}\n"
            report += f"  最短耗时: {metric.min_time:.2f}ms\n"
            report += f"  最长耗时: {metric.max_time:.2f}ms\n"
            report += f"  吞吐量: {metric.throughput:.2f} ops/sec\n"
        
        return report
    
    def reset(self):
        """重置性能指标"""
        self.metrics.clear()
        self.start_time = None
        print("🔄 性能指标已重置")


class ToolChain:
    """
    工具链 - 组合多个工具的执行
    
    💡 对比TypeScript:
    class ToolChain {
        private steps: Array<{
            toolName: string;
            params: any;
            condition?: (result: ToolResult) => boolean;
        }> = [];
        
        addStep(toolName: string, params: any, condition?: (result: ToolResult) => boolean): ToolChain {
            this.steps.push({ toolName, params, condition });
            return this;
        }
        
        async execute(toolManager: AsyncToolManager): Promise<ToolResult[]> {
            const results: ToolResult[] = [];
            
            for (const step of this.steps) {
                console.log(`🔗 执行工具链步骤: ${step.toolName}`);
                
                const result = await toolManager.executeTool(step.toolName, step.params);
                results.push(result);
                
                // 检查条件，决定是否继续
                if (step.condition && !step.condition(result)) {
                    console.log(`⚠️  工具链中断: 条件不满足`);
                    break;
                }
                
                if (!result.isSuccess()) {
                    console.log(`❌ 工具链中断: ${step.toolName} 执行失败`);
                    break;
                }
            }
            
            return results;
        }
        
        clear(): void {
            this.steps = [];
        }
    }
    
    学习要点：
    - 工具链的设计模式
    - 条件执行的实现
    - 流程控制的处理
    - 结果传递的机制
    """
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, tool_name: str, params: Dict[str, Any], 
                 condition: Optional[Callable[[ToolResult], bool]] = None):
        """
        添加工具链步骤
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            condition: 继续执行的条件函数
        
        Returns:
            self: 支持链式调用
        """
        self.steps.append({
            "tool_name": tool_name,
            "params": params,
            "condition": condition
        })
        return self
    
    async def execute(self, tool_manager: AsyncToolManager) -> List[ToolResult]:
        """
        执行工具链
        
        Args:
            tool_manager: 工具管理器
        
        Returns:
            List[ToolResult]: 所有步骤的执行结果
        """
        results = []
        
        for i, step in enumerate(self.steps):
            print(f"🔗 执行工具链步骤 {i+1}/{len(self.steps)}: {step['tool_name']}")
            
            try:
                result = await tool_manager.execute_tool(
                    step["tool_name"],
                    **step["params"]
                )
                results.append(result)
                
                # 检查条件，决定是否继续
                if step["condition"] and not step["condition"](result):
                    print("⚠️  工具链中断: 条件不满足")
                    break
                
                if not result.is_success():
                    print(f"❌ 工具链中断: {step['tool_name']} 执行失败")
                    break
                
                print(f"✅ 步骤 {i+1} 完成")
                
            except Exception as e:
                error_result = ToolResult.error(f"工具链执行异常: {str(e)}")
                results.append(error_result)
                print(f"❌ 工具链异常中断: {e}")
                break
        
        return results
    
    def clear(self):
        """清空工具链"""
        self.steps = []


async def custom_tool_example():
    """
    自定义工具示例
    
    学习要点：
    - 自定义工具的创建和使用
    - 复杂数据处理的实现
    - 工具注册和调用的流程
    """
    print("🛠️  自定义工具示例")
    print("=" * 30)
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=3,
        default_timeout=15.0
    )
    
    try:
        # 注册自定义数据处理工具
        data_processor = CustomDataProcessorTool()
        await tool_manager.register_tool(data_processor)
        
        print("✅ 自定义数据处理工具已注册")
        
        # 准备测试数据
        test_data = [
            {"name": "Alice", "age": 25, "score": 85},
            {"name": "Bob", "age": 30, "score": 92},
            {"name": "Charlie", "age": 22, "score": 78},
            {"name": "Diana", "age": 28, "score": 96},
            {"name": "Eve", "age": 26, "score": 88}
        ]
        
        print(f"\n📊 测试数据: {len(test_data)} 条记录")
        
        # 测试各种数据处理操作
        operations = [
            {
                "name": "按年龄排序",
                "params": {"operation": "sort", "data": test_data, "key": "age"}
            },
            {
                "name": "过滤高分学生",
                "params": {"operation": "filter", "data": test_data, "condition": "score > 85"}
            },
            {
                "name": "按年龄分组",
                "params": {"operation": "group", "data": test_data, "key": "age"}
            },
            {
                "name": "统计年龄分布",
                "params": {"operation": "aggregate", "data": test_data, "key": "age"}
            }
        ]
        
        print("\n🚀 执行数据处理操作:")
        print("-" * 20)
        
        for op in operations:
            print(f"\n🔍 {op['name']}:")
            
            result = await tool_manager.execute_tool(
                "data_processor",
                **op["params"]
            )
            
            if result.is_success():
                print("✅ 处理成功:")
                # 限制输出长度
                content = result.content
                if len(content) > 300:
                    content = content[:300] + "..."
                print(f"   {content}")
                
                if result.metadata:
                    print(f"   输入大小: {result.metadata.get('input_size', 'N/A')}")
                    print(f"   输出大小: {result.metadata.get('output_size', 'N/A')}")
            else:
                print(f"❌ 处理失败: {result.error_message}")
        
        # 测试数值数据处理
        print("\n🔢 数值数据处理:")
        print("-" * 20)
        
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        numeric_operations = [
            {
                "name": "数据映射(平方)",
                "params": {"operation": "map", "data": numbers, "condition": "square"}
            },
            {
                "name": "数据归约(求和)",
                "params": {"operation": "reduce", "data": numbers, "condition": "sum"}
            },
            {
                "name": "数据归约(平均值)",
                "params": {"operation": "reduce", "data": numbers, "condition": "avg"}
            }
        ]
        
        for op in numeric_operations:
            print(f"\n🔍 {op['name']}:")
            
            result = await tool_manager.execute_tool(
                "data_processor",
                **op["params"]
            )
            
            if result.is_success():
                print(f"✅ 结果: {result.content}")
            else:
                print(f"❌ 失败: {result.error_message}")
        
    finally:
        await tool_manager.cleanup()


async def tool_chain_example():
    """
    工具链示例
    
    学习要点：
    - 工具链的设计和使用
    - 多工具协作的模式
    - 条件执行的实现
    """
    print("\n🔗 工具链示例")
    print("=" * 30)
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=3,
        default_timeout=20.0
    )
    
    try:
        # 注册所需工具
        calculator = AsyncCalculatorTool()
        data_processor = CustomDataProcessorTool()
        
        await tool_manager.register_tool(calculator)
        await tool_manager.register_tool(data_processor)
        
        print("✅ 工具已注册")
        
        # 创建工具链
        chain = ToolChain()
        
        # 添加工具链步骤
        chain.add_step(
            "async_calculator",
            {"operation": "add", "operands": [10, 20, 30]},
            condition=lambda result: result.is_success()
        ).add_step(
            "async_calculator",
            {"operation": "multiply", "operands": [5, 6]},
            condition=lambda result: result.is_success()
        ).add_step(
            "data_processor",
            {
                "operation": "sort",
                "data": [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
            },
            condition=lambda result: result.is_success()
        )
        
        print("\n🚀 执行工具链:")
        print("-" * 20)
        
        # 执行工具链
        results = await chain.execute(tool_manager)
        
        print(f"\n📊 工具链执行完成，共 {len(results)} 个步骤")
        
        for i, result in enumerate(results):
            if result.is_success():
                print(f"✅ 步骤 {i+1}: {result.content}")
            else:
                print(f"❌ 步骤 {i+1}: {result.error_message}")
        
        # 创建更复杂的工具链
        print("\n🔗 复杂工具链示例:")
        print("-" * 20)
        
        complex_chain = ToolChain()
        
        # 生成测试数据
        test_numbers = [random.randint(1, 100) for _ in range(10)]
        
        complex_chain.add_step(
            "data_processor",
            {"operation": "sort", "data": test_numbers}
        ).add_step(
            "data_processor",
            {"operation": "reduce", "data": test_numbers, "condition": "sum"}
        ).add_step(
            "async_calculator",
            {"operation": "sqrt", "operands": [100]}  # 使用固定值，因为上一步结果不能直接传递
        )
        
        complex_results = await complex_chain.execute(tool_manager)
        
        print(f"\n📊 复杂工具链执行完成，共 {len(complex_results)} 个步骤")
        
        for i, result in enumerate(complex_results):
            if result.is_success():
                content = result.content
                if len(content) > 100:
                    content = content[:100] + "..."
                print(f"✅ 步骤 {i+1}: {content}")
            else:
                print(f"❌ 步骤 {i+1}: {result.error_message}")
        
    finally:
        await tool_manager.cleanup()


async def performance_monitoring_example():
    """
    性能监控示例
    
    学习要点：
    - 性能监控的实现
    - 指标收集和分析
    - 性能报告的生成
    """
    print("\n📊 性能监控示例")
    print("=" * 30)
    
    # 创建性能监控器
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=5,
        default_timeout=10.0
    )
    
    try:
        # 注册工具
        calculator = AsyncCalculatorTool()
        data_processor = CustomDataProcessorTool()
        
        await tool_manager.register_tool(calculator)
        await tool_manager.register_tool(data_processor)
        
        print("✅ 工具已注册，开始性能测试")
        
        # 性能测试 1: 计算器工具
        print("\n🧮 计算器性能测试:")
        print("-" * 20)
        
        calc_operations = [
            {"operation": "add", "operands": [1, 2, 3, 4, 5]},
            {"operation": "multiply", "operands": [2, 3, 4]},
            {"operation": "power", "operands": [2, 10]},
            {"operation": "factorial", "operands": [10]},
            {"operation": "sqrt", "operands": [144]}
        ]
        
        for i in range(20):  # 执行20次测试
            for op in calc_operations:
                start_time = time.time()
                
                result = await tool_manager.execute_tool(
                    "async_calculator",
                    **op
                )
                
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                monitor.record_execution(
                    "async_calculator",
                    execution_time,
                    result.is_success()
                )
        
        print("✅ 计算器性能测试完成")
        
        # 性能测试 2: 数据处理工具
        print("\n📊 数据处理性能测试:")
        print("-" * 20)
        
        test_data = [{"id": i, "value": random.randint(1, 100)} for i in range(100)]
        
        data_operations = [
            {"operation": "sort", "data": test_data, "key": "value"},
            {"operation": "filter", "data": test_data, "condition": "value > 50"},
            {"operation": "group", "data": test_data, "key": "value"},
            {"operation": "aggregate", "data": test_data, "key": "value"}
        ]
        
        for i in range(10):  # 执行10次测试
            for op in data_operations:
                start_time = time.time()
                
                result = await tool_manager.execute_tool(
                    "data_processor",
                    **op
                )
                
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000
                
                monitor.record_execution(
                    "data_processor",
                    execution_time,
                    result.is_success()
                )
        
        print("✅ 数据处理性能测试完成")
        
        # 并发性能测试
        print("\n🔄 并发性能测试:")
        print("-" * 20)
        
        concurrent_tasks = []
        for i in range(50):
            task = tool_manager.execute_tool(
                "async_calculator",
                operation="factorial",
                operands=[random.randint(5, 15)]
            )
            concurrent_tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        end_time = time.time()
        
        concurrent_time = (end_time - start_time) * 1000
        success_count = sum(1 for r in results if not isinstance(r, Exception) and r.is_success())
        
        print(f"✅ 并发测试完成:")
        print(f"   任务数量: {len(concurrent_tasks)}")
        print(f"   成功数量: {success_count}")
        print(f"   总耗时: {concurrent_time:.2f}ms")
        print(f"   平均耗时: {concurrent_time/len(concurrent_tasks):.2f}ms/任务")
        
        # 停止监控并生成报告
        monitor.stop_monitoring()
        
        print("\n📋 性能监控报告:")
        print("-" * 30)
        print(monitor.generate_report())
        
    finally:
        await tool_manager.cleanup()


async def advanced_error_handling_example():
    """
    高级错误处理示例
    
    学习要点：
    - 复杂错误场景的处理
    - 重试机制的实现
    - 错误恢复的策略
    """
    print("\n⚠️  高级错误处理示例")
    print("=" * 30)
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=3,
        default_timeout=5.0
    )
    
    try:
        # 注册工具
        calculator = AsyncCalculatorTool()
        await tool_manager.register_tool(calculator)
        
        print("✅ 工具已注册")
        
        # 错误处理测试用例
        error_cases = [
            {
                "name": "超时处理",
                "test": lambda: tool_manager.execute_tool_with_timeout(
                    "async_calculator",
                    timeout=0.001,  # 极短超时
                    operation="factorial",
                    operands=[20]
                )
            },
            {
                "name": "无效工具",
                "test": lambda: tool_manager.execute_tool(
                    "nonexistent_tool",
                    param="value"
                )
            },
            {
                "name": "参数错误",
                "test": lambda: tool_manager.execute_tool(
                    "async_calculator",
                    operation="invalid_op",
                    operands=[1, 2]
                )
            },
            {
                "name": "除零错误",
                "test": lambda: tool_manager.execute_tool(
                    "async_calculator",
                    operation="divide",
                    operands=[10, 0]
                )
            }
        ]
        
        print("\n🧪 错误处理测试:")
        print("-" * 20)
        
        for case in error_cases:
            print(f"\n🔍 测试: {case['name']}")
            
            try:
                result = await case["test"]()
                
                if result.is_success():
                    print(f"  ⚠️  意外成功: {result.content}")
                else:
                    print(f"  ✅ 预期失败: {result.error_message}")
                    
            except asyncio.TimeoutError:
                print("  ✅ 超时处理正常")
            except Exception as e:
                print(f"  ✅ 异常捕获: {type(e).__name__}: {e}")
        
        # 重试机制测试
        print("\n🔄 重试机制测试:")
        print("-" * 20)
        
        # 模拟不稳定的操作（随机失败）
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # 模拟随机失败
                if random.random() < 0.7:  # 70%失败率
                    raise Exception("模拟网络错误")
                
                print("✅ 操作成功")
                break
                
            except Exception as e:
                retry_count += 1
                print(f"  ❌ 尝试 {retry_count}/{max_retries} 失败: {e}")
                
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # 指数退避
                    print(f"  ⏳ 等待 {wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    print("  ❌ 重试次数已用完，操作失败")
        
        # 错误恢复测试
        print("\n🔧 错误恢复测试:")
        print("-" * 20)
        
        # 尝试执行一个可能失败的操作，并提供备选方案
        primary_operations = [
            {"operation": "divide", "operands": [10, 0]},  # 会失败
            {"operation": "sqrt", "operands": [-1]},       # 会失败
            {"operation": "log", "operands": [0]}          # 会失败
        ]
        
        fallback_operations = [
            {"operation": "divide", "operands": [10, 1]},  # 备选方案
            {"operation": "sqrt", "operands": [1]},        # 备选方案
            {"operation": "log", "operands": [1]}          # 备选方案
        ]
        
        for i, (primary, fallback) in enumerate(zip(primary_operations, fallback_operations)):
            print(f"\n🔍 恢复测试 {i+1}:")
            
            # 尝试主要操作
            result = await tool_manager.execute_tool("async_calculator", **primary)
            
            if result.is_success():
                print(f"  ✅ 主要操作成功: {result.content}")
            else:
                print(f"  ❌ 主要操作失败: {result.error_message}")
                print("  🔄 尝试备选方案...")
                
                # 尝试备选操作
                fallback_result = await tool_manager.execute_tool("async_calculator", **fallback)
                
                if fallback_result.is_success():
                    print(f"  ✅ 备选方案成功: {fallback_result.content}")
                else:
                    print(f"  ❌ 备选方案也失败: {fallback_result.error_message}")
        
    finally:
        await tool_manager.cleanup()


async def main():
    """
    主函数 - 运行所有高级模式示例
    
    学习要点：
    - 高级示例的组织结构
    - 复杂功能的演示流程
    - 异常处理的完整性
    """
    print("🎯 Practical 3.2 - 高级模式示例")
    print("=" * 50)
    
    try:
        # 运行各个高级示例
        await custom_tool_example()
        await tool_chain_example()
        await performance_monitoring_example()
        await advanced_error_handling_example()
        
        print("\n✅ 所有高级模式示例执行完成")
        print("\n🎓 高级学习要点总结:")
        print("  1. 自定义工具的设计和实现")
        print("  2. 工具链的组合使用模式")
        print("  3. 性能监控和优化技巧")
        print("  4. 高级错误处理策略")
        print("  5. 生产级代码的组织方法")
        
    except Exception as e:
        print(f"❌ 高级示例执行异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    程序入口点
    
    学习要点：
    - 高级异步程序的启动
    - 复杂示例的执行管理
    - 异常处理的完整性
    """
    try:
        # Windows平台的事件循环策略
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # 运行主程序
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"❌ 程序启动异常: {e}")
        sys.exit(1)