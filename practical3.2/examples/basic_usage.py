"""
Practical 3.2 - 基础使用示例

这个示例展示了如何使用高级异步工具框架的基本功能。

学习要点：
1. 异步工具的基本使用
2. 工具管理器的配置
3. 错误处理的最佳实践
4. 异步编程的基础模式
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import AsyncToolManager, AsyncCalculatorTool, AsyncWeatherTool
from config import Config


async def basic_calculator_example():
    """
    基础计算器示例
    
    💡 对比TypeScript:
    async function basicCalculatorExample(): Promise<void> {
        console.log("🧮 基础计算器示例");
        console.log("=".repeat(30));
        
        // 创建工具管理器
        const toolManager = new AsyncToolManager({
            maxConcurrentTasks: 3,
            defaultTimeout: 10.0
        });
        
        // 注册计算器工具
        const calculator = new AsyncCalculatorTool();
        await toolManager.registerTool(calculator);
        
        // 执行基础计算
        const operations = [
            { name: "加法", operation: "add", operands: [10, 20, 30] },
            { name: "乘法", operation: "multiply", operands: [5, 6] },
            { name: "幂运算", operation: "power", operands: [2, 8] },
            { name: "平方根", operation: "sqrt", operands: [144] }
        ];
        
        for (const op of operations) {
            try {
                const result = await toolManager.executeTool("async_calculator", {
                    operation: op.operation,
                    operands: op.operands
                });
                
                if (result.isSuccess()) {
                    console.log(`✅ ${op.name}: ${result.content}`);
                } else {
                    console.log(`❌ ${op.name} 失败: ${result.errorMessage}`);
                }
            } catch (error) {
                console.log(`❌ ${op.name} 异常: ${error.message}`);
            }
        }
        
        // 清理资源
        await toolManager.cleanup();
    }
    
    学习要点：
    - 异步工具的基本使用流程
    - 错误处理的完整性
    - 资源管理的重要性
    
    Returns:
        None
    """
    print("🧮 基础计算器示例")
    print("=" * 30)
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=3,
        default_timeout=10.0
    )
    
    try:
        # 注册计算器工具
        calculator = AsyncCalculatorTool()
        await tool_manager.register_tool(calculator)
        
        print("✅ 计算器工具已注册")
        
        # 定义测试操作
        operations = [
            {"name": "加法", "operation": "add", "operands": [10, 20, 30]},
            {"name": "乘法", "operation": "multiply", "operands": [5, 6]},
            {"name": "幂运算", "operation": "power", "operands": [2, 8]},
            {"name": "平方根", "operation": "sqrt", "operands": [144]},
            {"name": "阶乘", "operation": "factorial", "operands": [5]},
            {"name": "正弦", "operation": "sin", "operands": [3.14159 / 2]}
        ]
        
        print("\n🚀 执行计算操作:")
        print("-" * 20)
        
        # 逐个执行操作
        for op in operations:
            try:
                result = await tool_manager.execute_tool(
                    "async_calculator",
                    operation=op["operation"],
                    operands=op["operands"]
                )
                
                if result.is_success():
                    print(f"✅ {op['name']}: {result.content}")
                else:
                    print(f"❌ {op['name']} 失败: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ {op['name']} 异常: {e}")
        
        # 显示统计信息
        print("\n📊 执行统计:")
        stats = tool_manager.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    finally:
        # 清理资源
        await tool_manager.cleanup()
        print("\n🧹 资源已清理")


async def concurrent_calculation_example():
    """
    并发计算示例
    
    💡 对比TypeScript:
    async function concurrentCalculationExample(): Promise<void> {
        console.log("\n🔄 并发计算示例");
        console.log("=".repeat(30));
        
        const toolManager = new AsyncToolManager({
            maxConcurrentTasks: 5,
            defaultTimeout: 15.0
        });
        
        const calculator = new AsyncCalculatorTool();
        await toolManager.registerTool(calculator);
        
        // 创建多个并发任务
        const tasks = [
            toolManager.executeTool("async_calculator", {
                operation: "factorial", operands: [10]
            }),
            toolManager.executeTool("async_calculator", {
                operation: "power", operands: [3, 5]
            }),
            toolManager.executeTool("async_calculator", {
                operation: "sqrt", operands: [256]
            }),
            toolManager.executeTool("async_calculator", {
                operation: "add", operands: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            })
        ];
        
        console.log(`🚀 启动 ${tasks.length} 个并发任务...`);
        
        const startTime = Date.now();
        const results = await Promise.allSettled(tasks);
        const endTime = Date.now();
        
        console.log(`⏱️  并发执行耗时: ${endTime - startTime}ms`);
        
        // 处理结果
        results.forEach((result, index) => {
            if (result.status === 'fulfilled' && result.value.isSuccess()) {
                console.log(`✅ 任务 ${index + 1}: ${result.value.content}`);
            } else {
                console.log(`❌ 任务 ${index + 1} 失败`);
            }
        });
        
        await toolManager.cleanup();
    }
    
    学习要点：
    - 并发任务的创建和管理
    - Promise.allSettled的使用
    - 性能测量的方法
    - 结果处理的模式
    
    Returns:
        None
    """
    print("\n🔄 并发计算示例")
    print("=" * 30)
    
    # 创建工具管理器（支持更多并发任务）
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=5,
        default_timeout=15.0
    )
    
    try:
        # 注册计算器工具
        calculator = AsyncCalculatorTool()
        await tool_manager.register_tool(calculator)
        
        # 创建多个并发任务
        tasks = [
            tool_manager.execute_tool(
                "async_calculator",
                operation="factorial",
                operands=[10]
            ),
            tool_manager.execute_tool(
                "async_calculator",
                operation="power",
                operands=[3, 5]
            ),
            tool_manager.execute_tool(
                "async_calculator",
                operation="sqrt",
                operands=[256]
            ),
            tool_manager.execute_tool(
                "async_calculator",
                operation="add",
                operands=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            ),
            tool_manager.execute_tool(
                "async_calculator",
                operation="multiply",
                operands=[7, 8, 9]
            )
        ]
        
        print(f"🚀 启动 {len(tasks)} 个并发任务...")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 记录结束时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        print(f"⏱️  并发执行耗时: {execution_time:.2f}ms")
        
        # 处理结果
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ 任务 {i+1} 异常: {result}")
            elif result.is_success():
                print(f"✅ 任务 {i+1}: {result.content}")
                success_count += 1
            else:
                print(f"❌ 任务 {i+1} 失败: {result.error_message}")
        
        print(f"\n📊 成功率: {success_count}/{len(tasks)} ({success_count/len(tasks)*100:.1f}%)")
        
    finally:
        await tool_manager.cleanup()


async def weather_api_example():
    """
    天气API示例
    
    💡 对比TypeScript:
    async function weatherApiExample(): Promise<void> {
        console.log("\n🌤️ 天气API示例");
        console.log("=".repeat(30));
        
        // 检查API密钥
        const config = new Config();
        if (!config.get('OPENWEATHER_API_KEY')) {
            console.log("⚠️  跳过天气示例（未配置API密钥）");
            return;
        }
        
        const toolManager = new AsyncToolManager({
            maxConcurrentTasks: 3,
            defaultTimeout: 30.0
        });
        
        const weather = new AsyncWeatherTool();
        await toolManager.registerTool(weather);
        
        // 查询多个城市的天气
        const cities = [
            { city: "Beijing", country: "CN" },
            { city: "Shanghai", country: "CN" },
            { city: "New York", country: "US" }
        ];
        
        for (const location of cities) {
            try {
                console.log(`🌍 查询 ${location.city} 天气...`);
                
                const result = await toolManager.executeTool("async_weather", {
                    city: location.city,
                    country: location.country,
                    units: "metric",
                    lang: "zh_cn"
                });
                
                if (result.isSuccess()) {
                    console.log(`✅ ${location.city} 天气信息:`);
                    console.log(result.content.substring(0, 200) + "...");
                } else {
                    console.log(`❌ ${location.city} 查询失败: ${result.errorMessage}`);
                }
                
                // 避免API限制，添加延迟
                await new Promise(resolve => setTimeout(resolve, 1000));
                
            } catch (error) {
                console.log(`❌ ${location.city} 查询异常: ${error.message}`);
            }
        }
        
        await toolManager.cleanup();
    }
    
    学习要点：
    - 外部API的集成和调用
    - API限制的处理
    - 异步延迟的实现
    - 配置检查的重要性
    
    Returns:
        None
    """
    print("\n🌤️ 天气API示例")
    print("=" * 30)
    
    # 检查API密钥
    config = Config()
    if not config.get('OPENWEATHER_API_KEY'):
        print("⚠️  跳过天气示例（未配置API密钥）")
        print("   请在.env文件中设置OPENWEATHER_API_KEY")
        return
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=3,
        default_timeout=30.0
    )
    
    try:
        # 注册天气工具
        weather = AsyncWeatherTool()
        await tool_manager.register_tool(weather)
        
        print("✅ 天气工具已注册")
        
        # 定义要查询的城市
        cities = [
            {"city": "Beijing", "country": "CN", "name": "北京"},
            {"city": "Shanghai", "country": "CN", "name": "上海"},
            {"city": "Guangzhou", "country": "CN", "name": "广州"},
            {"city": "Tokyo", "country": "JP", "name": "东京"}
        ]
        
        print("\n🌍 查询城市天气:")
        print("-" * 20)
        
        # 逐个查询城市天气
        for location in cities:
            try:
                print(f"🔍 正在查询 {location['name']} 天气...")
                
                result = await tool_manager.execute_tool(
                    "async_weather",
                    city=location["city"],
                    country=location["country"],
                    units="metric",
                    lang="zh_cn"
                )
                
                if result.is_success():
                    print(f"✅ {location['name']} 天气信息:")
                    # 只显示前200个字符，避免输出过长
                    content = result.content
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"   {content}")
                    
                    # 显示元数据
                    if result.metadata:
                        print(f"   查询时间: {result.metadata.get('timestamp', 'N/A')}")
                        print(f"   缓存状态: {result.metadata.get('cached', 'N/A')}")
                else:
                    print(f"❌ {location['name']} 查询失败: {result.error_message}")
                
                # 避免API限制，添加延迟
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ {location['name']} 查询异常: {e}")
        
        # 测试缓存功能
        print("\n🗄️ 测试缓存功能:")
        print("-" * 20)
        
        city = "Beijing"
        
        # 第一次查询
        start_time = datetime.now()
        result1 = await tool_manager.execute_tool(
            "async_weather",
            city=city,
            country="CN",
            use_cache=True
        )
        time1 = (datetime.now() - start_time).total_seconds() * 1000
        
        if result1.is_success():
            print(f"✅ 首次查询耗时: {time1:.2f}ms")
            
            # 第二次查询（应该使用缓存）
            start_time = datetime.now()
            result2 = await tool_manager.execute_tool(
                "async_weather",
                city=city,
                country="CN",
                use_cache=True
            )
            time2 = (datetime.now() - start_time).total_seconds() * 1000
            
            print(f"✅ 缓存查询耗时: {time2:.2f}ms")
            
            if time2 < time1:
                speedup = time1 / time2
                print(f"🚀 缓存加速比: {speedup:.1f}x")
            else:
                print("⚠️  缓存未生效或网络波动")
        
    finally:
        await tool_manager.cleanup()


async def error_handling_example():
    """
    错误处理示例
    
    💡 对比TypeScript:
    async function errorHandlingExample(): Promise<void> {
        console.log("\n⚠️  错误处理示例");
        console.log("=".repeat(30));
        
        const toolManager = new AsyncToolManager({
            maxConcurrentTasks: 2,
            defaultTimeout: 5.0
        });
        
        const calculator = new AsyncCalculatorTool();
        await toolManager.registerTool(calculator);
        
        // 测试各种错误情况
        const errorCases = [
            {
                name: "无效操作",
                params: { operation: "invalid_op", operands: [1, 2] }
            },
            {
                name: "除零错误",
                params: { operation: "divide", operands: [10, 0] }
            },
            {
                name: "参数不足",
                params: { operation: "add", operands: [] }
            },
            {
                name: "负数平方根",
                params: { operation: "sqrt", operands: [-1] }
            }
        ];
        
        for (const errorCase of errorCases) {
            try {
                console.log(`🧪 测试: ${errorCase.name}`);
                
                const result = await toolManager.executeTool("async_calculator", errorCase.params);
                
                if (result.isSuccess()) {
                    console.log(`  ✅ 意外成功: ${result.content}`);
                } else {
                    console.log(`  ❌ 预期失败: ${result.errorMessage}`);
                }
            } catch (error) {
                console.log(`  ❌ 异常捕获: ${error.message}`);
            }
        }
        
        await toolManager.cleanup();
    }
    
    学习要点：
    - 各种错误情况的测试
    - 异常处理的完整性
    - 错误信息的有用性
    - 系统健壮性的验证
    
    Returns:
        None
    """
    print("\n⚠️  错误处理示例")
    print("=" * 30)
    
    # 创建工具管理器
    tool_manager = AsyncToolManager(
        max_concurrent_tasks=2,
        default_timeout=5.0
    )
    
    try:
        # 注册计算器工具
        calculator = AsyncCalculatorTool()
        await tool_manager.register_tool(calculator)
        
        # 定义各种错误情况
        error_cases = [
            {
                "name": "无效操作",
                "params": {"operation": "invalid_operation", "operands": [1, 2]}
            },
            {
                "name": "除零错误",
                "params": {"operation": "divide", "operands": [10, 0]}
            },
            {
                "name": "参数不足",
                "params": {"operation": "add", "operands": []}
            },
            {
                "name": "负数平方根",
                "params": {"operation": "sqrt", "operands": [-1]}
            },
            {
                "name": "阶乘负数",
                "params": {"operation": "factorial", "operands": [-5]}
            },
            {
                "name": "对数零值",
                "params": {"operation": "log", "operands": [0]}
            }
        ]
        
        print("🧪 测试错误处理:")
        print("-" * 20)
        
        # 测试各种错误情况
        for error_case in error_cases:
            try:
                print(f"\n🔍 测试: {error_case['name']}")
                
                result = await tool_manager.execute_tool(
                    "async_calculator",
                    **error_case["params"]
                )
                
                if result.is_success():
                    print(f"  ⚠️  意外成功: {result.content}")
                else:
                    print(f"  ✅ 预期失败: {result.error_message}")
                    
            except Exception as e:
                print(f"  ❌ 异常捕获: {e}")
        
        # 测试超时处理
        print("\n⏰ 测试超时处理:")
        print("-" * 20)
        
        try:
            # 创建一个会超时的任务
            result = await tool_manager.execute_tool_with_timeout(
                "async_calculator",
                timeout=0.001,  # 1毫秒超时
                operation="factorial",
                operands=[50]
            )
            
            if result.is_success():
                print("  ⚠️  任务在超时前完成")
            else:
                print(f"  ✅ 任务失败: {result.error_message}")
                
        except asyncio.TimeoutError:
            print("  ✅ 超时处理正常")
        except Exception as e:
            print(f"  ❌ 超时测试异常: {e}")
        
        # 测试工具不存在的情况
        print("\n🔍 测试不存在的工具:")
        print("-" * 20)
        
        try:
            result = await tool_manager.execute_tool(
                "nonexistent_tool",
                some_param="value"
            )
            
            if result.is_success():
                print("  ⚠️  意外成功")
            else:
                print(f"  ✅ 预期失败: {result.error_message}")
                
        except Exception as e:
            print(f"  ✅ 异常捕获: {e}")
        
    finally:
        await tool_manager.cleanup()


async def main():
    """
    主函数 - 运行所有示例
    
    💡 对比TypeScript:
    async function main(): Promise<void> {
        console.log("🎯 Practical 3.2 - 基础使用示例");
        console.log("=".repeat(50));
        
        try {
            await basicCalculatorExample();
            await concurrentCalculationExample();
            await weatherApiExample();
            await errorHandlingExample();
            
            console.log("\n✅ 所有示例执行完成");
        } catch (error) {
            console.error("❌ 示例执行异常:", error);
        }
    }
    
    学习要点：
    - 示例程序的组织结构
    - 异步函数的顺序执行
    - 全局异常处理
    - 程序完整性的保证
    
    Returns:
        None
    """
    print("🎯 Practical 3.2 - 基础使用示例")
    print("=" * 50)
    
    try:
        # 运行各个示例
        await basic_calculator_example()
        await concurrent_calculation_example()
        await weather_api_example()
        await error_handling_example()
        
        print("\n✅ 所有示例执行完成")
        print("🎓 学习要点总结:")
        print("  1. 异步工具的基本使用模式")
        print("  2. 并发任务的创建和管理")
        print("  3. 外部API的集成方法")
        print("  4. 错误处理的最佳实践")
        print("  5. 资源管理的重要性")
        
    except Exception as e:
        print(f"❌ 示例执行异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    程序入口点
    
    学习要点：
    - 异步程序的启动方式
    - 平台兼容性的处理
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