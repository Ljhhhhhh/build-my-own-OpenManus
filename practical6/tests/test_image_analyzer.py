"""
图像分析工具测试用例

测试ImageAnalyzer工具的各种功能。

学习要点：
- 异步工具测试
- 图像处理测试
- API调用模拟
- 错误场景测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import tempfile
from pathlib import Path
from PIL import Image
import io
import base64

from tools import ImageAnalyzer, ImageAnalysisType, MultimodalInput, ToolResultStatus
from utils.config import Config


class TestImageAnalyzer:
    """图像分析工具测试类"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock(spec=Config)
        config.openai_api_key = "test_key"
        config.openai_base_url = None
        config.openai_organization = None
        config.vision_model = "gpt-4-vision-preview"
        config.max_vision_tokens = 4096
        config.vision_detail = "auto"
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
        img = Image.new('RGB', (100, 100), color='blue')
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
    
    def test_analyzer_initialization(self, mock_config):
        """测试分析器初始化"""
        analyzer = ImageAnalyzer(mock_config)
        
        assert analyzer.name == "image_analyzer"
        assert analyzer.config == mock_config
        assert analyzer.client is not None
        assert len(analyzer.analysis_prompts) > 0
    
    def test_get_supported_analysis_types(self, mock_config):
        """测试获取支持的分析类型"""
        analyzer = ImageAnalyzer(mock_config)
        
        supported_types = analyzer.get_supported_analysis_types()
        
        assert ImageAnalysisType.DESCRIBE in supported_types
        assert ImageAnalysisType.OCR in supported_types
        assert ImageAnalysisType.OBJECTS in supported_types
        assert ImageAnalysisType.SCENE in supported_types
        assert ImageAnalysisType.DETAILED in supported_types
        assert ImageAnalysisType.CUSTOM in supported_types
    
    def test_get_supported_task_types(self, mock_config):
        """测试获取支持的任务类型"""
        analyzer = ImageAnalyzer(mock_config)
        
        supported_types = analyzer.get_supported_task_types()
        
        assert "image_analysis" in supported_types
        assert "ocr" in supported_types
        assert "object_detection" in supported_types
        assert "scene_understanding" in supported_types
        assert "general" in supported_types
    
    def test_build_analysis_prompt_describe(self, mock_config):
        """测试构建描述分析提示"""
        analyzer = ImageAnalyzer(mock_config)
        
        prompt = analyzer._build_analysis_prompt(
            user_text="请分析这张图片",
            analysis_type=ImageAnalysisType.DESCRIBE
        )
        
        assert "详细描述这张图片的内容" in prompt
        assert "请分析这张图片" in prompt
    
    def test_build_analysis_prompt_ocr(self, mock_config):
        """测试构建OCR分析提示"""
        analyzer = ImageAnalyzer(mock_config)
        
        prompt = analyzer._build_analysis_prompt(
            user_text="",
            analysis_type=ImageAnalysisType.OCR
        )
        
        assert "识别并提取图片中的所有文字内容" in prompt
        assert "文字内容：" in prompt
        assert "位置信息：" in prompt
    
    def test_build_analysis_prompt_custom(self, mock_config):
        """测试构建自定义分析提示"""
        analyzer = ImageAnalyzer(mock_config)
        
        custom_prompt = "请识别图片中的动物种类"
        prompt = analyzer._build_analysis_prompt(
            user_text="额外要求：注意细节",
            analysis_type=ImageAnalysisType.CUSTOM,
            custom_prompt=custom_prompt
        )
        
        assert custom_prompt in prompt
        assert "额外要求：注意细节" in prompt
    
    @pytest.mark.asyncio
    async def test_call_vision_api_success(self, mock_config):
        """测试成功调用Vision API"""
        analyzer = ImageAnalyzer(mock_config)
        
        # Mock OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是一张蓝色的图片"
        
        with patch.object(analyzer.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            result = await analyzer._call_vision_api(
                prompt="请描述这张图片",
                image_base64="fake_base64_data",
                max_tokens=1000,
                detail="auto"
            )
            
            assert result == "这是一张蓝色的图片"
            mock_create.assert_called_once()
            
            # 检查调用参数
            call_args = mock_create.call_args
            messages = call_args[1]['messages']
            assert len(messages) == 1
            assert messages[0]['role'] == 'user'
            assert len(messages[0]['content']) == 2  # text + image
    
    @pytest.mark.asyncio
    async def test_call_vision_api_error(self, mock_config):
        """测试Vision API调用错误"""
        analyzer = ImageAnalyzer(mock_config)
        
        with patch.object(analyzer.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(Exception) as exc_info:
                await analyzer._call_vision_api(
                    prompt="test",
                    image_base64="fake_data",
                    max_tokens=1000,
                    detail="auto"
                )
            
            assert "API Error" in str(exc_info.value)
    
    def test_parse_ocr_result(self, mock_config):
        """测试解析OCR结果"""
        analyzer = ImageAnalyzer(mock_config)
        
        ocr_content = """
        文字内容：Hello World
        位置信息：图片中央
        文字内容：测试文本
        位置信息：图片底部
        """
        
        result = analyzer._parse_ocr_result(ocr_content)
        
        assert "extracted_text" in result
        assert "positions" in result
        assert "full_text" in result
        assert len(result["extracted_text"]) == 2
        assert "Hello World" in result["extracted_text"]
        assert "测试文本" in result["extracted_text"]
        assert "Hello World 测试文本" == result["full_text"]
    
    def test_parse_objects_result(self, mock_config):
        """测试解析对象识别结果"""
        analyzer = ImageAnalyzer(mock_config)
        
        objects_content = """
        对象列表：
        1. 汽车 - 图片左侧 - 红色轿车
        2. 树木 - 图片右侧 - 绿色大树
        3. 建筑物 - 图片背景 - 高层建筑
        """
        
        result = analyzer._parse_objects_result(objects_content)
        
        assert "objects" in result
        assert "object_count" in result
        assert "object_names" in result
        assert result["object_count"] == 3
        assert "汽车" in result["object_names"]
        assert "树木" in result["object_names"]
        assert "建筑物" in result["object_names"]
    
    def test_parse_scene_result(self, mock_config):
        """测试解析场景分析结果"""
        analyzer = ImageAnalyzer(mock_config)
        
        scene_content = """
        场景类型：城市街道
        环境特征：繁忙的商业区，有很多车辆和行人
        其他信息：白天，晴朗天气
        """
        
        result = analyzer._parse_scene_result(scene_content)
        
        assert result["scene_type"] == "城市街道"
        assert result["environment"] == "繁忙的商业区，有很多车辆和行人"
        assert result["additional_info"] == "白天，晴朗天气"
    
    @pytest.mark.asyncio
    async def test_execute_multimodal_without_image(self, mock_config):
        """测试执行多模态分析（无图像）"""
        analyzer = ImageAnalyzer(mock_config)
        
        multimodal_input = MultimodalInput(
            text="请分析图片",
            image=None,
            task_type="image_analysis"
        )
        
        result = await analyzer.execute_multimodal(multimodal_input)
        
        assert result.status == ToolResultStatus.ERROR
        assert "图像分析工具需要图像输入" in result.data["error"]
    
    @pytest.mark.asyncio
    async def test_execute_multimodal_with_image(self, mock_config, temp_image_file):
        """测试执行多模态分析（有图像）"""
        analyzer = ImageAnalyzer(mock_config)
        
        multimodal_input = MultimodalInput(
            text="请描述这张图片",
            image=temp_image_file,
            task_type="image_analysis"
        )
        
        # Mock Vision API调用
        with patch.object(analyzer, '_call_vision_api', return_value="这是一张蓝色的图片") as mock_api:
            result = await analyzer.execute_multimodal(
                multimodal_input,
                analysis_type=ImageAnalysisType.DESCRIBE
            )
            
            assert result.status == ToolResultStatus.SUCCESS
            assert result.message == "图像分析完成"
            assert "analysis_type" in result.data
            assert "raw_content" in result.data
            assert "processed_data" in result.data
            
            mock_api.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_image_convenience_method(self, mock_config, temp_image_file):
        """测试图像分析便捷方法"""
        analyzer = ImageAnalyzer(mock_config)
        
        with patch.object(analyzer, 'execute_multimodal') as mock_execute:
            mock_execute.return_value = Mock(status=ToolResultStatus.SUCCESS)
            
            result = await analyzer.analyze_image(
                image=temp_image_file,
                analysis_type=ImageAnalysisType.DESCRIBE,
                prompt="请分析这张图片"
            )
            
            mock_execute.assert_called_once()
            
            # 检查调用参数
            call_args = mock_execute.call_args
            multimodal_input = call_args[0][0]
            assert multimodal_input.text == "请分析这张图片"
            assert multimodal_input.image == temp_image_file
            assert multimodal_input.task_type == "image_analysis"
    
    @pytest.mark.asyncio
    async def test_image_processing_error_handling(self, mock_config):
        """测试图像处理错误处理"""
        analyzer = ImageAnalyzer(mock_config)
        
        # 测试不存在的图像文件
        multimodal_input = MultimodalInput(
            text="分析图片",
            image="nonexistent_file.jpg",
            task_type="image_analysis"
        )
        
        result = await analyzer.execute_multimodal(multimodal_input)
        
        assert result.status == ToolResultStatus.ERROR
        assert "error" in result.data
    
    def test_process_analysis_result_with_parse_error(self, mock_config):
        """测试分析结果处理（解析错误）"""
        analyzer = ImageAnalyzer(mock_config)
        
        # Mock解析方法抛出异常
        with patch.object(analyzer, '_parse_ocr_result', side_effect=Exception("Parse error")):
            result = analyzer._process_analysis_result(
                raw_result="invalid ocr result",
                analysis_type=ImageAnalysisType.OCR
            )
            
            assert "parse_error" in result["processed_data"]
            assert result["processed_data"]["parse_error"] == "Parse error"
            assert "description" in result["processed_data"]


# 集成测试
class TestImageAnalyzerIntegration:
    """图像分析工具集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_image_analysis_workflow(self, mock_config, temp_image_file):
        """测试完整的图像分析工作流程"""
        analyzer = ImageAnalyzer(mock_config)
        
        # Mock完整的API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是一张100x100像素的蓝色正方形图片"
        
        with patch.object(analyzer.client.chat.completions, 'create', return_value=mock_response):
            result = await analyzer.analyze_image(
                image=temp_image_file,
                prompt="请详细分析这张图片",
                analysis_type=ImageAnalysisType.DESCRIBE
            )
            
            assert result.status == ToolResultStatus.SUCCESS
            assert "这是一张100x100像素的蓝色正方形图片" in result.data["raw_content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])