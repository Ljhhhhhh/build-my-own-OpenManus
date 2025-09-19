"""
集成测试脚本 - 项目4系统测试

这个脚本用于测试整个工具调用代理系统的集成功能：
1. 测试各个组件的独立功能
2. 测试组件之间的集成
3. 测试LLM与工具系统的交互
4. 验证错误处理机制

学习要点：
- 集成测试的设计思路
- 异步测试的实现
- 测试用例的组织
- 测试结果的验证
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import ToolCallingAgent
from tools import CalculatorTool, TextProcessorTool, ToolManager, BaseTool
from utils import setup_logger


class IntegrationTester:
    """
    集成测试类
    
    负责执行各种测试用例，验证系统功能的正确性。
    
    学习要点：
    - 测试类的设计模式
    - 测试结果的收集和分析
    - 异步测试的组织
    """
    
    def __init__(self):
        """初始化测试器"""
        self.logger = setup_logger("integration_test", level="DEBUG")
        self.test_results = []
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.logger.info(f"{status} - {test_name}: {message}")
        print(f"{status} - {test_name}: {message}")
    
    async def test_tool_manager(self) -> bool:
        """测试工具管理器功能"""
        print("\n🔧 测试工具管理器...")
        
        try:
            # 创建工具管理器
            manager = ToolManager()
            
            # 测试工具注册
            calc_tool = CalculatorTool()
            text_tool = TextProcessorTool()
            
            manager.register_tool(calc_tool)
            manager.register_tool(text_tool)
            
            # 验证工具列表
            tools = manager.list_tools()
            if len(tools) != 2:
                self.log_test_result("工具注册", False, f"期望2个工具，实际{len(tools)}个")
                return False
            
            self.log_test_result("工具注册", True, f"成功注册{len(tools)}个工具")
            
            # 测试工具获取
            retrieved_calc = manager.get_tool("calculator")
            if retrieved_calc is None:
                self.log_test_result("工具获取", False, "无法获取计算器工具")
                return False
            
            self.log_test_result("工具获取", True, "成功获取工具")
            
            # 测试工具执行
            result = await manager.execute_tool("calculator", operation="add", a=2, b=3)
            if not result.is_success or result.content['result'] != 5:
                self.log_test_result("工具执行", False, f"计算结果错误: {result.content}")
                return False
            
            self.log_test_result("工具执行", True, f"计算结果正确: {result.content['result']}")
            
            return True
            
        except Exception as e:
            self.log_test_result("工具管理器测试", False, f"异常: {str(e)}")
            return False
    
    async def test_individual_tools(self) -> bool:
        """测试各个工具的独立功能"""
        print("\n🛠️ 测试各个工具...")
        
        try:
            # 测试计算器工具
            calc_tool = CalculatorTool()
            
            test_cases = [
                ({"operation": "add", "a": 2, "b": 3}, 5),
                ({"operation": "multiply", "a": 10, "b": 5}, 50),
                ({"operation": "divide", "a": 100, "b": 4}, 25),
                ({"operation": "subtract", "a": 8, "b": 5}, 3)
            ]
            
            for params, expected in test_cases:
                result = await calc_tool.execute(**params)
                if not result.is_success or result.content['result'] != expected:
                    self.log_test_result(f"计算器-{params['operation']}", False, 
                                       f"期望{expected}，得到{result.content}")
                    return False
                
                self.log_test_result(f"计算器-{params['operation']}", True, 
                                   f"结果正确: {result.content['result']}")
            
            # 测试文本处理工具
            text_tool = TextProcessorTool()
            
            text_cases = [
                ({"text": "Hello World", "operation": "uppercase"}, "HELLO WORLD"),
                ({"text": "PYTHON", "operation": "lowercase"}, "python"),
                ({"text": "hello world", "operation": "title"}, "Hello World"),
                ({"text": "Python is great", "operation": "word_count"}, 3)
            ]
            
            for params, expected in text_cases:
                result = await text_tool.execute(**params)
                if not result.is_success or result.content['result'] != expected:
                    self.log_test_result(f"文本处理-{params['operation']}", False,
                                       f"期望{expected}，得到{result.content['result']}")
                    return False
                
                self.log_test_result(f"文本处理-{params['operation']}", True,
                                   f"结果正确: {result.content['result']}")
            
            return True
            
        except Exception as e:
            self.log_test_result("工具功能测试", False, f"异常: {str(e)}")
            return False
    
    async def test_agent_without_llm(self) -> bool:
        """测试代理的基础功能（不涉及LLM调用）"""
        print("\n🤖 测试代理基础功能...")
        
        try:
            if not self.api_key:
                self.log_test_result("代理初始化", True, "缺少API密钥，跳过LLM测试")
                return True  # 不算失败，只是跳过
            
            # 创建代理
            agent = ToolCallingAgent(self.api_key)
            
            # 注册工具
            agent.register_tool(CalculatorTool())
            agent.register_tool(TextProcessorTool())
            
            # 测试工具schema生成
            schemas = agent.get_tools_schema()
            if len(schemas) != 2:
                self.log_test_result("工具Schema生成", False, 
                                   f"期望2个schema，得到{len(schemas)}个")
                return False
            
            self.log_test_result("工具Schema生成", True, f"生成{len(schemas)}个工具schema")
            
            # 验证schema格式
            for schema in schemas:
                if "type" not in schema or schema["type"] != "function":
                    self.log_test_result("Schema格式验证", False, "Schema格式不正确")
                    return False
                
                if "function" not in schema:
                    self.log_test_result("Schema格式验证", False, "缺少function字段")
                    return False
            
            self.log_test_result("Schema格式验证", True, "Schema格式正确")
            
            # 测试统计功能
            stats = agent.get_stats()
            if "available_tools" not in stats or stats["available_tools"] != 2:
                self.log_test_result("统计功能", False, "统计信息不正确")
                return False
            
            self.log_test_result("统计功能", True, "统计信息正确")
            
            return True
            
        except Exception as e:
            self.log_test_result("代理基础功能测试", False, f"异常: {str(e)}")
            return False
    
    async def test_agent_with_llm(self) -> bool:
        """测试代理与LLM的集成（需要API密钥）"""
        print("\n🧠 测试代理与LLM集成...")
        
        if not self.api_key:
            self.log_test_result("LLM集成测试", True, "缺少OPENAI_API_KEY，跳过LLM测试")
            return True  # 不算失败，只是跳过
        
        try:
            # 创建代理
            agent = ToolCallingAgent(self.api_key)
            agent.register_tool(CalculatorTool())
            agent.register_tool(TextProcessorTool())
            
            # 简单的测试用例（不依赖具体的LLM响应）
            test_cases = [
                "计算 2 + 3",
                "将 'hello' 转换为大写"
            ]
            
            for test_case in test_cases:
                try:
                    response = await agent.process_request(test_case)
                    if response and len(response) > 0:
                        self.log_test_result(f"LLM处理-{test_case[:10]}...", True, 
                                           "获得有效响应")
                    else:
                        self.log_test_result(f"LLM处理-{test_case[:10]}...", False, 
                                           "响应为空")
                        return False
                        
                except Exception as e:
                    self.log_test_result(f"LLM处理-{test_case[:10]}...", False, 
                                       f"处理失败: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test_result("LLM集成测试", False, f"异常: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """测试错误处理机制"""
        print("\n⚠️ 测试错误处理...")
        
        try:
            # 测试工具管理器错误处理
            manager = ToolManager()
            
            # 测试执行不存在的工具
            result = await manager.execute_tool("nonexistent")
            if result.is_success:
                self.log_test_result("不存在工具处理", False, "应该返回失败")
                return False
            
            self.log_test_result("不存在工具处理", True, f"正确处理错误: {result.error_message}")
            
            # 测试工具参数错误
            calc_tool = CalculatorTool()
            result = await calc_tool.execute(operation="divide", a=10, b=0)
            if result.is_success:
                self.log_test_result("无效参数处理", False, "应该返回失败")
                return False
            
            self.log_test_result("无效参数处理", True, "正确处理无效参数")
            
            return True
            
        except Exception as e:
            self.log_test_result("错误处理测试", False, f"异常: {str(e)}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("🎯 测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test_name']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        return failed_tests == 0
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始集成测试...")
        print("=" * 60)
        
        # 检查环境
        if not self.api_key:
            print("⚠️ 警告: 未设置OPENAI_API_KEY，将跳过LLM相关测试")
        
        # 运行测试
        tests = [
            self.test_tool_manager(),
            self.test_individual_tools(),
            self.test_agent_without_llm(),
            self.test_agent_with_llm(),
            self.test_error_handling()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # 检查是否有异常
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.log_test_result(f"测试{i+1}", False, f"测试异常: {str(result)}")
        
        # 打印总结
        return self.print_summary()


async def main():
    """主函数"""
    tester = IntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("🎉 所有测试通过！系统集成正常。")
        sys.exit(0)
    else:
        print("💥 部分测试失败，请检查系统配置。")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())