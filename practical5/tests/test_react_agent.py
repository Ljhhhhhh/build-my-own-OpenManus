"""
ReAct代理测试模块

这个模块包含了ReAct代理的单元测试和集成测试。

学习要点：
- 异步测试的编写
- Mock对象的使用
- 测试用例的设计
- 断言和验证
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent.react_agent import ReActAgent, AgentState, ReActStep
from tools.manager import ToolManager
from tools.calculator import CalculatorTool
from tools.base import ToolResult


class TestReActStep:
    """ReActStep数据类测试"""
    
    def test_react_step_creation(self):
        """测试ReActStep的创建"""
        step = ReActStep(
            step_number=1,
            thought="这是一个测试思考",
            action={"name": "calculator", "parameters": {"operation": "add", "a": 1, "b": 2}},
            observation="计算结果: 3",
            state=AgentState.THINKING
        )
        
        assert step.step_number == 1
        assert step.thought == "这是一个测试思考"
        assert step.action["name"] == "calculator"
        assert step.observation == "计算结果: 3"
        assert step.state == AgentState.THINKING
    
    def test_react_step_to_dict(self):
        """测试ReActStep转换为字典"""
        step = ReActStep(
            step_number=1,
            thought="测试思考",
            action=None,
            observation=None,
            state=AgentState.THINKING
        )
        
        step_dict = step.to_dict()
        
        assert isinstance(step_dict, dict)
        assert step_dict['step_number'] == 1
        assert step_dict['thought'] == "测试思考"
        assert step_dict['state'] == "thinking"
        assert 'timestamp' in step_dict


class TestReActAgent:
    """ReAct代理测试"""
    
    @pytest.fixture
    def tool_manager(self):
        """创建测试用的工具管理器"""
        manager = ToolManager()
        calculator = CalculatorTool()
        manager.register_tool(calculator)
        return manager
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = MagicMock()
        config.openai_api_key = "test-key"
        config.openai_base_url = None
        config.openai_organization = None
        return config
    
    @pytest.fixture
    def agent(self, tool_manager, mock_config):
        """创建测试用的ReAct代理"""
        with patch('agent.react_agent.get_config', return_value=mock_config):
            with patch('agent.react_agent.AsyncOpenAI') as mock_openai:
                mock_client = AsyncMock()
                mock_openai.return_value = mock_client
                
                agent = ReActAgent(
                    tool_manager=tool_manager,
                    max_steps=5,
                    model="gpt-3.5-turbo",
                    temperature=0.1
                )
                agent.client = mock_client
                return agent
    
    def test_agent_initialization(self, agent):
        """测试代理初始化"""
        assert agent.max_steps == 5
        assert agent.model == "gpt-3.5-turbo"
        assert agent.temperature == 0.1
        assert agent.state == AgentState.THINKING
        assert agent.current_step == 0
        assert len(agent.steps) == 0
    
    def test_reset_state(self, agent):
        """测试状态重置"""
        # 修改状态
        agent.state = AgentState.FINISHED
        agent.current_step = 3
        agent.steps = [MagicMock()]
        
        # 重置状态
        agent._reset_state()
        
        assert agent.state == AgentState.THINKING
        assert agent.current_step == 0
        assert len(agent.steps) == 0
    
    def test_parse_response_with_final_answer(self, agent):
        """测试解析包含最终答案的响应"""
        response = """
        Thought: 我已经得到了足够的信息来回答问题。
        Final Answer: 答案是42。
        """
        
        thought, action, final_answer = agent._parse_response(response)
        
        assert "我已经得到了足够的信息" in thought
        assert action is None
        assert final_answer == "答案是42。"
    
    def test_parse_response_with_action(self, agent):
        """测试解析包含行动的响应"""
        response = """
        Thought: 我需要计算两个数的和。
        Action: {"name": "calculator", "parameters": {"operation": "add", "a": 5, "b": 3}}
        """
        
        thought, action, final_answer = agent._parse_response(response)
        
        assert "我需要计算" in thought
        assert action["name"] == "calculator"
        assert action["parameters"]["operation"] == "add"
        assert final_answer is None
    
    def test_format_tool_result_success(self, agent):
        """测试格式化成功的工具结果"""
        result = ToolResult.success(
            content={"operation": "add", "result": 8},
            execution_time=0.1
        )
        
        formatted = agent._format_tool_result(result)
        
        assert "工具执行成功" in formatted
        assert "8" in formatted
    
    def test_format_tool_result_error(self, agent):
        """测试格式化错误的工具结果"""
        result = ToolResult.error("计算失败")
        
        formatted = agent._format_tool_result(result)
        
        assert "工具执行失败" in formatted
        assert "计算失败" in formatted
    
    def test_get_tools_info(self, agent):
        """测试获取工具信息"""
        tools_info = agent._get_tools_info()
        
        assert "calculator" in tools_info
        assert "简单的计算器工具" in tools_info
        assert "operation" in tools_info
    
    def test_get_steps_history_empty(self, agent):
        """测试获取空的步骤历史"""
        history = agent._get_steps_history()
        
        assert "暂无历史步骤" in history
    
    def test_get_steps_history_with_steps(self, agent):
        """测试获取包含步骤的历史"""
        step = ReActStep(
            step_number=1,
            thought="测试思考",
            action={"name": "calculator", "parameters": {"operation": "add", "a": 1, "b": 2}},
            observation="结果: 3",
            state=AgentState.THINKING
        )
        agent.steps = [step]
        
        history = agent._get_steps_history()
        
        assert "步骤 1" in history
        assert "测试思考" in history
        assert "calculator" in history
        assert "结果: 3" in history
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, agent):
        """测试成功执行工具"""
        action = {
            "name": "calculator",
            "parameters": {"operation": "add", "a": 5, "b": 3}
        }
        
        result = await agent._execute_tool(action)
        
        assert result.is_success
        assert result.content["result"] == 8
    
    @pytest.mark.asyncio
    async def test_execute_tool_invalid_name(self, agent):
        """测试执行不存在的工具"""
        action = {
            "name": "nonexistent_tool",
            "parameters": {}
        }
        
        result = await agent._execute_tool(action)
        
        assert not result.is_success
        assert "不存在" in result.error_message
    
    def test_generate_final_result_success(self, agent):
        """测试生成成功的最终结果"""
        # 设置成功状态
        agent.state = AgentState.FINISHED
        agent.current_step = 2
        
        # 添加最终步骤
        final_step = ReActStep(
            step_number=2,
            thought="找到答案了",
            action=None,
            observation="最终答案: 42",
            state=AgentState.FINISHED
        )
        agent.steps = [final_step]
        
        result = agent._generate_final_result("测试问题", 1.5)
        
        assert result['success'] is True
        assert result['final_answer'] == "42"
        assert result['total_steps'] == 2
        assert result['total_time'] == 1.5
    
    def test_generate_error_result(self, agent):
        """测试生成错误结果"""
        result = agent._generate_error_result("测试错误", 0.5)
        
        assert result['success'] is False
        assert "测试错误" in result['final_answer']
        assert result['total_time'] == 0.5
        assert result['final_state'] == AgentState.ERROR.value


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def setup_environment(self):
        """设置测试环境"""
        # 这里可以设置更复杂的测试环境
        pass
    
    @pytest.mark.asyncio
    async def test_simple_calculation_flow(self, setup_environment):
        """测试简单计算流程"""
        # 创建工具管理器
        tool_manager = ToolManager()
        calculator = CalculatorTool()
        tool_manager.register_tool(calculator)
        
        # 模拟配置
        mock_config = MagicMock()
        mock_config.openai_api_key = "test-key"
        mock_config.openai_base_url = None
        mock_config.openai_organization = None
        
        with patch('agent.react_agent.get_config', return_value=mock_config):
            with patch('agent.react_agent.AsyncOpenAI') as mock_openai:
                # 模拟LLM响应
                mock_client = AsyncMock()
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = """
                Thought: 我需要计算5加3的结果。
                Action: {"name": "calculator", "parameters": {"operation": "add", "a": 5, "b": 3}}
                """
                
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client
                
                # 创建代理
                agent = ReActAgent(
                    tool_manager=tool_manager,
                    max_steps=3,
                    model="gpt-3.5-turbo"
                )
                
                # 执行单步推理（模拟）
                await agent._execute_step("计算5+3")
                
                # 验证结果
                assert len(agent.steps) == 1
                step = agent.steps[0]
                assert step.step_number == 1
                assert "计算" in step.thought
                assert step.action["name"] == "calculator"
                assert "8" in step.observation


# 运行测试的辅助函数
def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()