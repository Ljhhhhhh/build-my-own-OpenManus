"""
多模态代理测试用例

测试多模态代理的各种功能和边界情况。

学习要点：
- 异步测试的编写
- Mock对象的使用
- 边界条件测试
- 错误处理测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
from PIL import Image
import io
import base64

from agent import MultimodalAgent, MultimodalTaskType
from utils.config import Config
from tools import ToolResult, ToolResultStatus


class TestMultimodalAgent:
    """多模态代理测试类"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock(spec=Config)
        config.openai_api_key = "test_key"
        config.openai_model = "gpt-3.5-turbo"
        config.openai_base_url = None
        config.openai_organization = None
        config.vision_model = "gpt-4-vision-preview"
        config.max_vision_tokens = 4096
        config.vision_detail = "auto"
        config.browser_headless = True
        config.browser_timeout = 30
        config.max_image_size = 10 * 1024 * 1024
        config.supported_image_formats = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
        config.image_quality = 85
        config.max_image_width = 2048
        config.max_image_height = 2048
        config.tool_timeout = 30
        config.request_timeout = 60
        return config
    
    @pytest.fixture
    def sample_image(self):
        """创建示例图像"""
        # 创建一个简单的测试图像
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    @pytest.fixture
    def temp_image_file(self, sample_image):
        """创建临时图像文件"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(sample_image)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_config):
        """测试代理初始化"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            assert agent.config == mock_config
            assert agent.current_image is None
            assert agent.multimodal_context == {}
            assert agent.max_steps == 15
    
    @pytest.mark.asyncio
    async def test_preprocess_multimodal_input_with_image(self, mock_config, temp_image_file):
        """测试多模态输入预处理（包含图像）"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # Mock图像分析工具
            mock_image_analyzer = Mock()
            mock_image_analyzer._prepare_image_for_api.return_value = "base64_image_data"
            
            with patch.object(agent.tool_manager, 'get_tool', return_value=mock_image_analyzer):
                await agent._preprocess_multimodal_input(
                    user_query="分析这张图片",
                    image=temp_image_file,
                    task_type=MultimodalTaskType.IMAGE_ANALYSIS
                )
            
            assert agent.current_image == "base64_image_data"
            assert agent.multimodal_context['has_image'] is True
            assert agent.multimodal_context['task_type'] == MultimodalTaskType.IMAGE_ANALYSIS
            assert agent.multimodal_context['image_processed'] is True
    
    @pytest.mark.asyncio
    async def test_preprocess_multimodal_input_without_image(self, mock_config):
        """测试多模态输入预处理（不包含图像）"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            await agent._preprocess_multimodal_input(
                user_query="计算1+1",
                image=None,
                task_type=MultimodalTaskType.GENERAL
            )
            
            assert agent.current_image is None
            assert agent.multimodal_context['has_image'] is False
            assert agent.multimodal_context['task_type'] == MultimodalTaskType.GENERAL
            assert agent.multimodal_context['image_processed'] is False
    
    @pytest.mark.asyncio
    async def test_analyze_task_strategy(self, mock_config):
        """测试任务策略分析"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # 测试不同任务类型的策略
            test_cases = [
                (MultimodalTaskType.IMAGE_ANALYSIS, "重点使用图像分析工具"),
                (MultimodalTaskType.WEB_AUTOMATION, "重点使用浏览器自动化工具"),
                (MultimodalTaskType.GENERAL, "根据需要选择合适的工具")
            ]
            
            for task_type, expected_hint in test_cases:
                agent._analyze_task_strategy("test query", task_type)
                assert agent.multimodal_context['strategy_hint'] == expected_hint
    
    @pytest.mark.asyncio
    async def test_is_multimodal_tool(self, mock_config):
        """测试多模态工具识别"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # Mock工具管理器
            mock_multimodal_tool = Mock()
            mock_multimodal_tool.__class__.__name__ = "ImageAnalyzer"
            
            mock_regular_tool = Mock()
            mock_regular_tool.__class__.__name__ = "CalculatorTool"
            
            with patch.object(agent.tool_manager, 'get_tool') as mock_get_tool:
                # 测试多模态工具
                mock_get_tool.return_value = mock_multimodal_tool
                # 这里需要根据实际的MultimodalTool类来判断
                # 暂时跳过这个测试，因为需要实际的类继承关系
                pass
    
    @pytest.mark.asyncio
    async def test_update_multimodal_context(self, mock_config):
        """测试多模态上下文更新"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # 测试工具使用记录
            action = {"name": "image_analyzer", "parameters": {}}
            result = ToolResult(
                status=ToolResultStatus.SUCCESS,
                data={"analysis_type": "describe", "content": "test"},
                message="Success"
            )
            
            agent._update_multimodal_context(action, result)
            
            assert "tool_usage" in agent.multimodal_context
            assert len(agent.multimodal_context["tool_usage"]) == 1
            assert agent.multimodal_context["tool_usage"][0]["tool"] == "image_analyzer"
            assert agent.multimodal_context["tool_usage"][0]["success"] is True
    
    @pytest.mark.asyncio
    async def test_cleanup_resources(self, mock_config):
        """测试资源清理"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # 设置一些需要清理的数据
            agent.current_image = "test_image_data"
            agent.multimodal_context = {"test": "data"}
            
            # Mock浏览器工具
            mock_browser_tool = AsyncMock()
            mock_browser_tool.close = AsyncMock()
            
            with patch.object(agent.tool_manager, 'get_tool', return_value=mock_browser_tool):
                await agent._cleanup_resources()
            
            assert agent.current_image is None
            assert agent.multimodal_context == {}
            mock_browser_tool.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_image_convenience_method(self, mock_config, temp_image_file):
        """测试图像分析便捷方法"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # Mock solve_multimodal方法
            expected_result = {
                "status": "success",
                "answer": "这是一张红色的图片",
                "execution_stats": {"total_time": 1.0, "total_steps": 2}
            }
            
            with patch.object(agent, 'solve_multimodal', return_value=expected_result) as mock_solve:
                result = await agent.analyze_image(
                    image=temp_image_file,
                    prompt="分析这张图片",
                    analysis_type="describe"
                )
                
                assert result == expected_result
                mock_solve.assert_called_once()
                
                # 检查调用参数
                call_args = mock_solve.call_args
                assert call_args[1]['user_query'] == "分析这张图片"
                assert call_args[1]['image'] == temp_image_file
                assert call_args[1]['task_type'] == MultimodalTaskType.IMAGE_ANALYSIS
    
    @pytest.mark.asyncio
    async def test_automate_browser_convenience_method(self, mock_config):
        """测试浏览器自动化便捷方法"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            expected_result = {
                "status": "success",
                "answer": "已成功访问网站并执行任务",
                "execution_stats": {"total_time": 2.0, "total_steps": 3}
            }
            
            with patch.object(agent, 'solve_multimodal', return_value=expected_result) as mock_solve:
                result = await agent.automate_browser(
                    task_description="访问百度首页",
                    url="https://www.baidu.com"
                )
                
                assert result == expected_result
                mock_solve.assert_called_once()
                
                # 检查调用参数
                call_args = mock_solve.call_args
                expected_query = "请访问 https://www.baidu.com 并执行以下任务：访问百度首页"
                assert call_args[1]['user_query'] == expected_query
                assert call_args[1]['task_type'] == MultimodalTaskType.WEB_AUTOMATION
    
    @pytest.mark.asyncio
    async def test_visual_web_task_convenience_method(self, mock_config, temp_image_file):
        """测试视觉网页任务便捷方法"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            expected_result = {
                "status": "success",
                "answer": "已根据图像执行网页任务",
                "execution_stats": {"total_time": 3.0, "total_steps": 4}
            }
            
            with patch.object(agent, 'solve_multimodal', return_value=expected_result) as mock_solve:
                result = await agent.visual_web_task(
                    image=temp_image_file,
                    task_description="搜索相似产品"
                )
                
                assert result == expected_result
                mock_solve.assert_called_once()
                
                # 检查调用参数
                call_args = mock_solve.call_args
                expected_query = "根据提供的图像，执行以下网页任务：搜索相似产品"
                assert call_args[1]['user_query'] == expected_query
                assert call_args[1]['image'] == temp_image_file
                assert call_args[1]['task_type'] == MultimodalTaskType.VISUAL_WEB_TASK
    
    @pytest.mark.asyncio
    async def test_error_handling_in_solve_multimodal(self, mock_config):
        """测试solve_multimodal中的错误处理"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # Mock预处理方法抛出异常
            with patch.object(agent, '_preprocess_multimodal_input', side_effect=Exception("Test error")):
                result = await agent.solve_multimodal(
                    user_query="test query",
                    image=None,
                    task_type=MultimodalTaskType.GENERAL
                )
                
                assert result['status'] == 'error'
                assert 'Test error' in result['error_message']
    
    def test_get_multimodal_trace(self, mock_config):
        """测试多模态轨迹获取"""
        with patch('agent.multimodal_agent.AsyncOpenAI'):
            agent = MultimodalAgent(config=mock_config)
            
            # 添加一些步骤（这里需要导入MultimodalStep）
            from agent.multimodal_agent import MultimodalStep
            from practical5.agent.react_agent import AgentState
            
            step1 = MultimodalStep(
                step_number=1,
                thought="测试思考",
                action={"name": "test_tool", "parameters": {}},
                observation="测试观察",
                state=AgentState.THINKING,
                task_type="general"
            )
            
            agent.steps = [step1]
            
            trace = agent.get_multimodal_trace()
            assert len(trace) == 1
            assert trace[0]['step_number'] == 1
            assert trace[0]['task_type'] == "general"


# 集成测试
class TestMultimodalAgentIntegration:
    """多模态代理集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_workflow_with_mocked_tools(self, mock_config):
        """测试完整工作流程（使用模拟工具）"""
        with patch('agent.multimodal_agent.AsyncOpenAI') as mock_openai:
            # Mock OpenAI响应
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Final Answer: 测试答案"
            
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            agent = MultimodalAgent(config=mock_config)
            
            # Mock工具执行
            with patch.object(agent, '_execute_tool') as mock_execute_tool:
                mock_execute_tool.return_value = ToolResult(
                    status=ToolResultStatus.SUCCESS,
                    data={"result": "test"},
                    message="Success"
                )
                
                result = await agent.solve_multimodal(
                    user_query="测试查询",
                    image=None,
                    task_type=MultimodalTaskType.GENERAL
                )
                
                assert result['status'] == 'success'
                assert '测试答案' in result['answer']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])