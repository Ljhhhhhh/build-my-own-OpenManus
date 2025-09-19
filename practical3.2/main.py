"""
Practical 3.2 - 高级异步工具框架演示

这个模块演示了高级异步工具框架的使用，包括：
1. 异步工具的并发执行
2. 外部API的集成和调用
3. 配置管理和环境变量
4. 缓存机制和性能优化
5. 错误处理和重试机制
6. 实时监控和统计

学习要点：
1. 异步编程的实际应用
2. 并发控制和任务管理
3. 外部服务的集成
4. 性能监控和优化
5. 生产级代码的设计模式
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import AsyncToolManager, AsyncCalculatorTool, AsyncWeatherTool
from config import Config


class AdvancedToolFrameworkDemo:
    """
    高级工具框架演示类
    
    💡 对比TypeScript:
    class AdvancedToolFrameworkDemo {
        private toolManager: AsyncToolManager;
        private config: Config;
        private isRunning: boolean = false;
        
        constructor() {
            this.config = new Config();
            this.toolManager = new AsyncToolManager({
                maxConcurrentTasks: 5,
                defaultTimeout: 30.0,
                enableMetrics: true
            });
            
            this.initializeTools();
        }
        
        private async initializeTools(): Promise<void> {
            // 注册工具
            await this.toolManager.registerTool(new AsyncCalculatorTool());
            await this.toolManager.registerTool(new AsyncWeatherTool());
            
            console.log(`✅ 已注册 ${this.toolManager.getToolCount()} 个工具`);
        }
        
        async runBasicDemo(): Promise<void> {
            console.log("🚀 基础异步工具演示");
            console.log("=".repeat(40));
            
            // 并发执行多个任务
            const tasks = [
                this.toolManager.executeTool("async_calculator", {
                    operation: "add",
                    operands: [10, 20, 30]
                }),
                this.toolManager.executeTool("async_weather", {
                    city: "Beijing",
                    country: "CN"
                })
            ];
            
            const results = await Promise.allSettled(tasks);
            
            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    console.log(`✅ 任务 ${index + 1} 成功: ${result.value.content}`);
                } else {
                    console.log(`❌ 任务 ${index + 1} 失败: ${result.reason}`);
                }
            });
        }
        
        async runConcurrencyDemo(): Promise<void> {
            // 并发控制演示
        }
        
        async runPerformanceDemo(): Promise<void> {
            // 性能测试演示
        }
        
        async runInteractiveDemo(): Promise<void> {
            // 交互式演示
        }
        
        async runAllDemos(): Promise<void> {
            await this.runBasicDemo();
            await this.runConcurrencyDemo();
            await this.runPerformanceDemo();
            await this.runInteractiveDemo();
        }
    }
    
    学习要点：
    - 异步工具框架的完整应用
    - 并发控制和任务管理
    - 性能监控和优化
    - 交互式用户界面
    - 生产级代码的组织结构
    """
    
    def __init__(self):
        """
        初始化高级工具框架演示
        
        学习要点：
        - 异步组件的初始化
        - 配置管理的集成
        - 工具管理器的设置
        """
        self.config = Config()
        self.tool_manager = AsyncToolManager(
            concurrency_limit=5,
            enable_logging=True
        )
        self.is_running = False
        
        # 初始化工具
        asyncio.create_task(self._initialize_tools())
    
    async def _initialize_tools(self):
        """
        初始化和注册工具
        
        学习要点：
        - 异步初始化的模式
        - 工具注册的流程
        - 错误处理的实现
        """
        try:
            # 注册计算器工具
            calculator = AsyncCalculatorTool()
            await self.tool_manager.register_tool(calculator)
            
            # 注册天气工具
            weather = AsyncWeatherTool()
            await self.tool_manager.register_tool(weather)
            
            print(f"✅ 已注册 {len(self.tool_manager.tools)} 个工具")
            
        except Exception as e:
            print(f"❌ 工具初始化失败: {e}")
    
    async def run_basic_demo(self):
        """
        基础异步工具演示
        
        💡 对比TypeScript:
        async runBasicDemo(): Promise<void> {
            console.log("🚀 基础异步工具演示");
            console.log("=".repeat(40));
            
            // 单个工具执行
            console.log("\n1. 单个工具执行:");
            
            const calcResult = await this.toolManager.executeTool("async_calculator", {
                operation: "power",
                operands: [2, 10]
            });
            
            if (calcResult.isSuccess()) {
                console.log(`✅ 计算结果: ${calcResult.content}`);
            } else {
                console.log(`❌ 计算失败: ${calcResult.errorMessage}`);
            }
            
            // 并发执行
            console.log("\n2. 并发执行:");
            
            const tasks = [
                this.toolManager.executeTool("async_calculator", {
                    operation: "factorial",
                    operands: [10]
                }),
                this.toolManager.executeTool("async_calculator", {
                    operation: "sqrt",
                    operands: [144]
                })
            ];
            
            const results = await Promise.allSettled(tasks);
            
            results.forEach((result, index) => {
                if (result.status === 'fulfilled' && result.value.isSuccess()) {
                    console.log(`✅ 并发任务 ${index + 1}: ${result.value.content}`);
                } else {
                    console.log(`❌ 并发任务 ${index + 1} 失败`);
                }
            });
        }
        
        学习要点：
        - 异步工具的基础使用
        - 单个任务和并发任务的执行
        - 结果处理和错误处理
        - 性能对比和分析
        
        Returns:
            None
        """
        print("🚀 基础异步工具演示")
        print("=" * 40)
        
        # 1. 单个工具执行
        print("\n1. 单个工具执行:")
        print("-" * 20)
        
        # 计算器演示
        calc_result = await self.tool_manager.execute_tool(
            "async_calculator",
            operation="power",
            operands=[2, 10]
        )
        
        if calc_result.is_success():
            print(f"✅ 计算 2^10 = {calc_result.content}")
        else:
            print(f"❌ 计算失败: {calc_result.error_message}")
        
        # 天气查询演示（如果配置了API密钥）
        if self.config.get('OPENWEATHER_API_KEY'):
            weather_result = await self.tool_manager.execute_tool(
                "async_weather",
                city="Beijing",
                country="CN",
                lang="zh_cn"
            )
            
            if weather_result.is_success():
                print("✅ 天气查询成功:")
                print(weather_result.content[:200] + "..." if len(weather_result.content) > 200 else weather_result.content)
            else:
                print(f"❌ 天气查询失败: {weather_result.error_message}")
        else:
            print("⚠️  跳过天气查询（未配置API密钥）")
        
        # 2. 并发执行演示
        print("\n2. 并发执行演示:")
        print("-" * 20)
        
        # 创建多个计算任务
        tasks = [
            self.tool_manager.execute_tool(
                "async_calculator",
                operation="factorial",
                operands=[10]
            ),
            self.tool_manager.execute_tool(
                "async_calculator",
                operation="sqrt",
                operands=[144]
            ),
            self.tool_manager.execute_tool(
                "async_calculator",
                operation="power",
                operands=[3, 4]
            )
        ]
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 计算执行时间
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 处理结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ 并发任务 {i+1} 异常: {result}")
            elif result.is_success():
                print(f"✅ 并发任务 {i+1}: {result.content}")
            else:
                print(f"❌ 并发任务 {i+1} 失败: {result.error_message}")
        
        print(f"⏱️  并发执行总耗时: {execution_time:.2f}秒")
    
    async def run_concurrency_demo(self):
        """
        并发控制演示
        
        💡 对比TypeScript:
        async runConcurrencyDemo(): Promise<void> {
            console.log("\n🔄 并发控制演示");
            console.log("=".repeat(40));
            
            // 测试并发限制
            console.log("\n1. 测试并发限制:");
            
            const heavyTasks = Array.from({ length: 10 }, (_, i) => 
                this.toolManager.executeTool("async_calculator", {
                    operation: "factorial",
                    operands: [15 + i]
                })
            );
            
            const startTime = Date.now();
            const results = await Promise.allSettled(heavyTasks);
            const endTime = Date.now();
            
            const successCount = results.filter(r => 
                r.status === 'fulfilled' && r.value.isSuccess()
            ).length;
            
            console.log(`✅ 成功执行: ${successCount}/10 个任务`);
            console.log(`⏱️  总耗时: ${(endTime - startTime) / 1000}秒`);
            
            // 显示并发统计
            const stats = this.toolManager.getStats();
            console.log("\n📊 并发统计:");
            Object.entries(stats).forEach(([key, value]) => {
                console.log(`  ${key}: ${value}`);
            });
        }
        
        学习要点：
        - 并发限制的测试和验证
        - 任务队列的管理
        - 性能统计的收集
        - 资源使用的监控
        
        Returns:
            None
        """
        print("\n🔄 并发控制演示")
        print("=" * 40)
        
        # 1. 测试并发限制
        print("\n1. 测试并发限制:")
        print("-" * 20)
        
        # 创建大量计算任务
        heavy_tasks = []
        for i in range(10):
            task = self.tool_manager.execute_tool(
                "async_calculator",
                operation="factorial",
                operands=[15 + i]
            )
            heavy_tasks.append(task)
        
        print(f"📝 创建了 {len(heavy_tasks)} 个计算任务")
        print("🚀 开始并发执行...")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 并发执行所有任务
        results = await asyncio.gather(*heavy_tasks, return_exceptions=True)
        
        # 计算执行时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 统计结果
        success_count = 0
        error_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_count += 1
                print(f"❌ 任务 {i+1} 异常: {result}")
            elif result.is_success():
                success_count += 1
                print(f"✅ 任务 {i+1}: {result.content}")
            else:
                error_count += 1
                print(f"❌ 任务 {i+1} 失败: {result.error_message}")
        
        print(f"\n📊 执行统计:")
        print(f"  ✅ 成功: {success_count}/{len(heavy_tasks)} 个任务")
        print(f"  ❌ 失败: {error_count}/{len(heavy_tasks)} 个任务")
        print(f"  ⏱️  总耗时: {execution_time:.2f}秒")
        print(f"  📈 平均耗时: {execution_time/len(heavy_tasks):.2f}秒/任务")
        
        # 2. 显示工具管理器统计
        print("\n2. 工具管理器统计:")
        print("-" * 20)
        
        stats = self.tool_manager.get_execution_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 3. 测试超时处理
        print("\n3. 测试超时处理:")
        print("-" * 20)
        
        try:
            # 创建一个会超时的任务（设置很短的超时时间）
            timeout_result = await self.tool_manager.execute_tool_with_timeout(
                "async_calculator",
                timeout=0.001,  # 1毫秒超时
                operation="factorial",
                operands=[100]
            )
            
            if timeout_result.is_success():
                print("✅ 任务在超时前完成")
            else:
                print(f"❌ 任务失败: {timeout_result.error_message}")
                
        except asyncio.TimeoutError:
            print("⏰ 任务超时（符合预期）")
        except Exception as e:
            print(f"❌ 超时测试异常: {e}")
    
    async def run_performance_demo(self):
        """
        性能测试演示
        
        💡 对比TypeScript:
        async runPerformanceDemo(): Promise<void> {
            console.log("\n⚡ 性能测试演示");
            console.log("=".repeat(40));
            
            // 性能基准测试
            console.log("\n1. 性能基准测试:");
            
            const benchmarks = [
                { name: "简单计算", operation: "add", operands: [1, 2, 3, 4, 5] },
                { name: "复杂计算", operation: "factorial", operands: [20] },
                { name: "数学函数", operation: "sin", operands: [Math.PI / 2] }
            ];
            
            for (const benchmark of benchmarks) {
                const iterations = 100;
                const startTime = performance.now();
                
                const tasks = Array.from({ length: iterations }, () =>
                    this.toolManager.executeTool("async_calculator", benchmark)
                );
                
                await Promise.all(tasks);
                
                const endTime = performance.now();
                const totalTime = endTime - startTime;
                const avgTime = totalTime / iterations;
                
                console.log(`📊 ${benchmark.name}:`);
                console.log(`  迭代次数: ${iterations}`);
                console.log(`  总耗时: ${totalTime.toFixed(2)}ms`);
                console.log(`  平均耗时: ${avgTime.toFixed(2)}ms`);
                console.log(`  吞吐量: ${(1000 / avgTime).toFixed(2)} ops/sec`);
            }
        }
        
        学习要点：
        - 性能基准测试的设计
        - 吞吐量和延迟的测量
        - 性能瓶颈的识别
        - 优化效果的验证
        
        Returns:
            None
        """
        print("\n⚡ 性能测试演示")
        print("=" * 40)
        
        # 1. 性能基准测试
        print("\n1. 性能基准测试:")
        print("-" * 20)
        
        benchmarks = [
            {
                "name": "简单加法",
                "params": {"operation": "add", "operands": [1, 2, 3, 4, 5]}
            },
            {
                "name": "复杂阶乘",
                "params": {"operation": "factorial", "operands": [20]}
            },
            {
                "name": "数学函数",
                "params": {"operation": "sin", "operands": [3.14159 / 2]}
            }
        ]
        
        for benchmark in benchmarks:
            print(f"\n📊 测试: {benchmark['name']}")
            
            iterations = 50
            start_time = datetime.now()
            
            # 创建多个相同的任务
            tasks = []
            for _ in range(iterations):
                task = self.tool_manager.execute_tool(
                    "async_calculator",
                    **benchmark['params']
                )
                tasks.append(task)
            
            # 并发执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000  # 转换为毫秒
            
            # 统计成功率
            success_count = sum(1 for r in results 
                              if not isinstance(r, Exception) and r.is_success())
            
            avg_time = total_time / iterations
            throughput = 1000 / avg_time if avg_time > 0 else 0
            
            print(f"  迭代次数: {iterations}")
            print(f"  成功率: {success_count}/{iterations} ({success_count/iterations*100:.1f}%)")
            print(f"  总耗时: {total_time:.2f}ms")
            print(f"  平均耗时: {avg_time:.2f}ms")
            print(f"  吞吐量: {throughput:.2f} ops/sec")
        
        # 2. 缓存性能测试（如果有天气工具）
        if self.config.get('OPENWEATHER_API_KEY'):
            print("\n2. 缓存性能测试:")
            print("-" * 20)
            
            city = "Shanghai"
            
            # 第一次查询（无缓存）
            start_time = datetime.now()
            result1 = await self.tool_manager.execute_tool(
                "async_weather",
                city=city,
                use_cache=True
            )
            time1 = (datetime.now() - start_time).total_seconds() * 1000
            
            if result1.is_success():
                print(f"✅ 首次查询耗时: {time1:.2f}ms")
                
                # 第二次查询（使用缓存）
                start_time = datetime.now()
                result2 = await self.tool_manager.execute_tool(
                    "async_weather",
                    city=city,
                    use_cache=True
                )
                time2 = (datetime.now() - start_time).total_seconds() * 1000
                
                print(f"✅ 缓存查询耗时: {time2:.2f}ms")
                
                if time2 < time1:
                    speedup = time1 / time2
                    print(f"🚀 缓存加速比: {speedup:.1f}x")
                else:
                    print("⚠️  缓存未生效或网络波动")
            else:
                print(f"❌ 天气查询失败: {result1.error_message}")
        
        # 3. 内存使用统计
        print("\n3. 资源使用统计:")
        print("-" * 20)
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        print(f"  内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")
        print(f"  CPU使用率: {process.cpu_percent():.1f}%")
        
        # 获取工具管理器统计
        manager_stats = self.tool_manager.get_execution_stats()
        print(f"  活跃任务: {manager_stats.get('active_tasks', 0)}")
        print(f"  总执行次数: {manager_stats.get('total_executions', 0)}")
        print(f"  成功率: {manager_stats.get('success_rate', 0):.1f}%")
    
    async def run_interactive_demo(self):
        """
        交互式演示
        
        💡 对比TypeScript:
        async runInteractiveDemo(): Promise<void> {
            console.log("\n🎮 交互式演示");
            console.log("=".repeat(40));
            
            const readline = require('readline');
            const rl = readline.createInterface({
                input: process.stdin,
                output: process.stdout
            });
            
            const question = (prompt: string): Promise<string> => {
                return new Promise((resolve) => {
                    rl.question(prompt, resolve);
                });
            };
            
            console.log("\n可用工具:");
            this.toolManager.listTools().forEach((tool, index) => {
                console.log(`  ${index + 1}. ${tool.name} - ${tool.description}`);
            });
            
            while (true) {
                console.log("\n选择操作:");
                console.log("1. 执行计算器工具");
                console.log("2. 执行天气查询工具");
                console.log("3. 查看工具统计");
                console.log("4. 退出");
                
                const choice = await question("请输入选择 (1-4): ");
                
                switch (choice.trim()) {
                    case '1':
                        await this.handleCalculatorInteraction(question);
                        break;
                    case '2':
                        await this.handleWeatherInteraction(question);
                        break;
                    case '3':
                        this.showToolStats();
                        break;
                    case '4':
                        console.log("👋 再见！");
                        rl.close();
                        return;
                    default:
                        console.log("❌ 无效选择，请重试");
                }
            }
        }
        
        学习要点：
        - 交互式用户界面的设计
        - 用户输入的处理和验证
        - 动态工具调用的实现
        - 用户体验的优化
        
        Returns:
            None
        """
        print("\n🎮 交互式演示")
        print("=" * 40)
        
        print("\n可用工具:")
        tools = list(self.tool_manager.tools.values())
        for i, tool in enumerate(tools):
            print(f"  {i+1}. {tool.name} - {tool.description}")
        
        while True:
            print("\n" + "=" * 30)
            print("选择操作:")
            print("1. 执行计算器工具")
            print("2. 执行天气查询工具")
            print("3. 查看工具统计")
            print("4. 查看工具详情")
            print("5. 退出")
            
            try:
                choice = input("\n请输入选择 (1-5): ").strip()
                
                if choice == '1':
                    await self._handle_calculator_interaction()
                elif choice == '2':
                    await self._handle_weather_interaction()
                elif choice == '3':
                    self._show_tool_stats()
                elif choice == '4':
                    self._show_tool_details()
                elif choice == '5':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"❌ 交互异常: {e}")
    
    async def _handle_calculator_interaction(self):
        """处理计算器交互"""
        print("\n🧮 计算器工具")
        print("-" * 20)
        
        # 显示可用操作
        operations = [
            "add", "subtract", "multiply", "divide", "power", 
            "sqrt", "factorial", "sin", "cos", "tan", "log", "ln"
        ]
        
        print("可用操作:")
        for i, op in enumerate(operations):
            print(f"  {i+1}. {op}")
        
        try:
            operation = input("\n请输入操作名称: ").strip()
            if operation not in operations:
                print("❌ 无效操作")
                return
            
            operands_str = input("请输入操作数（用逗号分隔）: ").strip()
            operands = [float(x.strip()) for x in operands_str.split(',')]
            
            precision = input("精度（小数位数，默认2）: ").strip()
            precision = int(precision) if precision else 2
            
            print("\n🚀 执行计算...")
            result = await self.tool_manager.execute_tool(
                "async_calculator",
                operation=operation,
                operands=operands,
                precision=precision
            )
            
            if result.is_success():
                print(f"✅ 计算结果: {result.content}")
                if result.metadata:
                    print(f"📊 元数据: {json.dumps(result.metadata, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ 计算失败: {result.error_message}")
                
        except ValueError as e:
            print(f"❌ 输入格式错误: {e}")
        except Exception as e:
            print(f"❌ 计算异常: {e}")
    
    async def _handle_weather_interaction(self):
        """处理天气查询交互"""
        print("\n🌤️ 天气查询工具")
        print("-" * 20)
        
        if not self.config.get('OPENWEATHER_API_KEY'):
            print("❌ 未配置OpenWeather API密钥")
            print("请在.env文件中设置OPENWEATHER_API_KEY")
            return
        
        try:
            city = input("请输入城市名称: ").strip()
            if not city:
                print("❌ 城市名称不能为空")
                return
            
            country = input("请输入国家代码（可选，如CN、US）: ").strip()
            country = country.upper() if country else None
            
            units = input("温度单位（metric/imperial/kelvin，默认metric）: ").strip()
            units = units if units in ['metric', 'imperial', 'kelvin'] else 'metric'
            
            include_forecast = input("是否包含预报（y/n，默认n）: ").strip().lower()
            include_forecast = include_forecast == 'y'
            
            print("\n🚀 查询天气...")
            result = await self.tool_manager.execute_tool(
                "async_weather",
                city=city,
                country=country,
                units=units,
                include_forecast=include_forecast
            )
            
            if result.is_success():
                print("✅ 天气查询成功:")
                print(result.content)
                if result.metadata:
                    print(f"\n📊 查询信息:")
                    for key, value in result.metadata.items():
                        if key not in ['coordinates']:  # 跳过复杂对象
                            print(f"  {key}: {value}")
            else:
                print(f"❌ 天气查询失败: {result.error_message}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")
    
    def _show_tool_stats(self):
        """显示工具统计"""
        print("\n📊 工具统计")
        print("-" * 20)
        
        # 工具管理器统计
        manager_stats = self.tool_manager.get_execution_stats()
        print("工具管理器统计:")
        for key, value in manager_stats.items():
            print(f"  {key}: {value}")
        
        # 各个工具的统计
        print("\n各工具统计:")
        for tool_name, tool in self.tool_manager.tools.items():
            tool_stats = tool.get_stats()
            print(f"  {tool_name}:")
            for key, value in tool_stats.items():
                print(f"    {key}: {value}")
    
    def _show_tool_details(self):
        """显示工具详情"""
        print("\n🔍 工具详情")
        print("-" * 20)
        
        for tool_name, tool in self.tool_manager.tools.items():
            print(f"\n📋 {tool_name}:")
            print(f"  名称: {tool.name}")
            print(f"  描述: {tool.description}")
            print(f"  超时时间: {tool.timeout}秒")
            print(f"  最大重试: {tool.max_retries}次")
            
            # 显示Schema（简化版）
            schema = tool.schema
            print(f"  参数:")
            if 'properties' in schema:
                for prop_name, prop_info in schema['properties'].items():
                    required = prop_name in schema.get('required', [])
                    prop_type = prop_info.get('type', 'unknown')
                    description = prop_info.get('description', '无描述')
                    required_mark = " *" if required else ""
                    print(f"    {prop_name}{required_mark} ({prop_type}): {description}")
    
    async def run_all_demos(self):
        """
        运行所有演示
        
        学习要点：
        - 演示流程的组织
        - 异常处理的完整性
        - 资源清理的重要性
        
        Returns:
            None
        """
        print("🎯 Practical 3.2 - 高级异步工具框架演示")
        print("=" * 50)
        
        try:
            self.is_running = True
            
            # 等待工具初始化完成
            await asyncio.sleep(0.1)
            
            # 运行各个演示
            await self.run_basic_demo()
            await self.run_concurrency_demo()
            await self.run_performance_demo()
            await self.run_interactive_demo()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断演示")
        except Exception as e:
            print(f"\n❌ 演示异常: {e}")
        finally:
            self.is_running = False
            await self._cleanup()
    
    async def _cleanup(self):
        """
        清理资源
        
        学习要点：
        - 异步资源的清理
        - 优雅关闭的实现
        - 内存泄漏的防止
        """
        print("\n🧹 清理资源...")
        
        try:
            # 清理工具管理器
            await self.tool_manager.cleanup()
            
            # 清理各个工具
            for tool in self.tool_manager.tools.values():
                if hasattr(tool, 'cleanup'):
                    await tool.cleanup()
            
            print("✅ 资源清理完成")
            
        except Exception as e:
            print(f"⚠️  资源清理异常: {e}")


async def main():
    """
    主函数
    
    💡 对比TypeScript:
    async function main(): Promise<void> {
        console.log("🚀 启动 Practical 3.2 演示");
        
        // 检查环境配置
        const config = new Config();
        if (!config.isValid()) {
            console.log("❌ 配置验证失败，请检查.env文件");
            return;
        }
        
        // 创建并运行演示
        const demo = new AdvancedToolFrameworkDemo();
        await demo.runAllDemos();
        
        console.log("✅ 演示完成");
    }
    
    // 错误处理
    main().catch(error => {
        console.error("❌ 程序异常:", error);
        process.exit(1);
    });
    
    学习要点：
    - 程序入口的设计
    - 配置验证的重要性
    - 全局异常处理
    - 优雅退出的实现
    
    Returns:
        None
    """
    print("🚀 启动 Practical 3.2 - 高级异步工具框架演示")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return
    
    # 检查配置
    config = Config()
    print(f"📋 配置状态: {'✅ 有效' if config.is_api_configured() else '⚠️  部分配置缺失'}")
    
    if not config.get('OPENWEATHER_API_KEY'):
        print("⚠️  未配置OpenWeather API密钥，天气功能将被跳过")
        print("   可在.env文件中设置OPENWEATHER_API_KEY")
    
    # 创建并运行演示
    demo = AdvancedToolFrameworkDemo()
    
    try:
        await demo.run_all_demos()
        print("\n✅ 演示完成")
        
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 感谢使用 Practical 3.2 演示！")


if __name__ == "__main__":
    """
    程序入口点
    
    学习要点：
    - 异步程序的启动方式
    - 事件循环的管理
    - 平台兼容性的考虑
    """
    try:
        # 在Windows上设置事件循环策略
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # 运行主程序
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"❌ 启动异常: {e}")
        sys.exit(1)