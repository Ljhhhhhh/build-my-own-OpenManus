"""
图像分析工具

基于OpenAI GPT-4V的图像分析工具，支持图像内容描述、OCR、对象识别等功能。

学习要点：
- OpenAI Vision API的使用
- 多模态API调用
- 错误处理和重试机制
- 结构化输出处理
- 异步编程实践
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from PIL import Image
import openai
from openai import AsyncOpenAI

from .multimodal_base import MultimodalTool, MultimodalInput, ToolResult, ToolResultStatus
from ..utils.config import Config

logger = logging.getLogger(__name__)


class ImageAnalysisType:
    """图像分析类型常量"""
    DESCRIBE = "describe"           # 图像内容描述
    OCR = "ocr"                    # 文字识别
    OBJECTS = "objects"            # 对象识别
    SCENE = "scene"                # 场景理解
    DETAILED = "detailed"          # 详细分析
    CUSTOM = "custom"              # 自定义分析


class ImageAnalyzer(MultimodalTool):
    """
    图像分析工具
    
    使用OpenAI GPT-4V进行图像分析，支持多种分析类型。
    
    学习要点：
    - Vision API的正确使用方式
    - 提示工程在视觉任务中的应用
    - 异步API调用的最佳实践
    - 结果解析和结构化
    """
    
    name = "image_analyzer"
    description = "基于GPT-4V的图像分析工具，支持图像描述、OCR、对象识别等功能"
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # 初始化OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            organization=config.openai_organization
        )
        
        # 分析类型到提示的映射
        self.analysis_prompts = {
            ImageAnalysisType.DESCRIBE: "请详细描述这张图片的内容，包括主要对象、场景、颜色、构图等。",
            ImageAnalysisType.OCR: "请识别并提取图片中的所有文字内容，保持原有的格式和布局。",
            ImageAnalysisType.OBJECTS: "请识别图片中的所有对象，列出它们的名称、位置和特征。",
            ImageAnalysisType.SCENE: "请分析图片的场景类型、环境特征、时间、天气等背景信息。",
            ImageAnalysisType.DETAILED: "请对这张图片进行全面详细的分析，包括内容描述、对象识别、场景理解、文字提取等所有方面。",
        }
    
    async def execute_multimodal(
        self,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> ToolResult:
        """
        执行图像分析
        
        Args:
            multimodal_input: 多模态输入数据
            **kwargs: 额外参数，包括：
                - analysis_type: 分析类型
                - custom_prompt: 自定义提示（当analysis_type为custom时使用）
                - max_tokens: 最大token数
                - detail: 图像分析详细程度
                
        Returns:
            分析结果
        """
        try:
            # 验证输入
            self._validate_multimodal_input(multimodal_input)
            
            if not multimodal_input.has_image():
                return ToolResult(
                    status=ToolResultStatus.ERROR,
                    data={"error": "图像分析工具需要图像输入"},
                    message="请提供要分析的图像"
                )
            
            # 获取分析参数
            analysis_type = kwargs.get("analysis_type", ImageAnalysisType.DESCRIBE)
            custom_prompt = kwargs.get("custom_prompt")
            max_tokens = kwargs.get("max_tokens", self.config.max_vision_tokens)
            detail = kwargs.get("detail", self.config.vision_detail)
            
            # 处理图像
            image_base64 = self._prepare_image_for_api(multimodal_input.image)
            
            # 构建提示
            prompt = self._build_analysis_prompt(
                multimodal_input.text,
                analysis_type,
                custom_prompt
            )
            
            # 调用GPT-4V API
            result = await self._call_vision_api(
                prompt=prompt,
                image_base64=image_base64,
                max_tokens=max_tokens,
                detail=detail
            )
            
            # 处理结果
            analysis_result = self._process_analysis_result(result, analysis_type)
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=analysis_result,
                message="图像分析完成"
            )
            
        except Exception as e:
            logger.error(f"图像分析失败: {e}")
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data={"error": str(e)},
                message=f"图像分析失败: {e}"
            )
    
    def _build_analysis_prompt(
        self,
        user_text: str,
        analysis_type: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        构建分析提示
        
        Args:
            user_text: 用户输入的文本
            analysis_type: 分析类型
            custom_prompt: 自定义提示
            
        Returns:
            构建好的提示文本
        """
        if analysis_type == ImageAnalysisType.CUSTOM and custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.analysis_prompts.get(
                analysis_type,
                self.analysis_prompts[ImageAnalysisType.DESCRIBE]
            )
        
        # 如果用户提供了额外的文本指令，将其合并
        if user_text.strip():
            if analysis_type == ImageAnalysisType.CUSTOM:
                prompt = f"{user_text}\n\n{base_prompt}"
            else:
                prompt = f"{base_prompt}\n\n用户补充要求：{user_text}"
        else:
            prompt = base_prompt
        
        # 添加输出格式指导
        if analysis_type == ImageAnalysisType.OCR:
            prompt += "\n\n请按照以下格式输出：\n文字内容：[提取的文字]\n位置信息：[文字在图片中的大致位置]"
        elif analysis_type == ImageAnalysisType.OBJECTS:
            prompt += "\n\n请按照以下格式输出：\n对象列表：\n1. [对象名称] - [位置] - [特征描述]"
        elif analysis_type == ImageAnalysisType.SCENE:
            prompt += "\n\n请按照以下格式输出：\n场景类型：[场景分类]\n环境特征：[环境描述]\n其他信息：[时间、天气等]"
        
        return prompt
    
    async def _call_vision_api(
        self,
        prompt: str,
        image_base64: str,
        max_tokens: int,
        detail: str
    ) -> str:
        """
        调用OpenAI Vision API
        
        Args:
            prompt: 分析提示
            image_base64: Base64编码的图像
            max_tokens: 最大token数
            detail: 分析详细程度
            
        Returns:
            API响应内容
        """
        try:
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ]
            
            # 调用API
            logger.info(f"调用GPT-4V API，模型: {self.config.vision_model}")
            
            response = await self._handle_timeout(
                self.client.chat.completions.create(
                    model=self.config.vision_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.1  # 使用较低的温度以获得更一致的结果
                ),
                timeout=self.config.request_timeout
            )
            
            # 提取响应内容
            content = response.choices[0].message.content
            
            if not content:
                raise ValueError("API返回空内容")
            
            logger.info("GPT-4V API调用成功")
            return content
            
        except openai.APIError as e:
            logger.error(f"OpenAI API错误: {e}")
            raise ValueError(f"API调用失败: {e}")
        except Exception as e:
            logger.error(f"Vision API调用失败: {e}")
            raise
    
    def _process_analysis_result(
        self,
        raw_result: str,
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        处理分析结果
        
        Args:
            raw_result: API原始响应
            analysis_type: 分析类型
            
        Returns:
            结构化的分析结果
        """
        result = {
            "analysis_type": analysis_type,
            "raw_content": raw_result,
            "processed_data": {}
        }
        
        try:
            # 根据分析类型进行结构化处理
            if analysis_type == ImageAnalysisType.OCR:
                result["processed_data"] = self._parse_ocr_result(raw_result)
            elif analysis_type == ImageAnalysisType.OBJECTS:
                result["processed_data"] = self._parse_objects_result(raw_result)
            elif analysis_type == ImageAnalysisType.SCENE:
                result["processed_data"] = self._parse_scene_result(raw_result)
            else:
                # 对于描述类型，直接使用原始内容
                result["processed_data"] = {
                    "description": raw_result.strip()
                }
            
        except Exception as e:
            logger.warning(f"结果结构化处理失败: {e}")
            # 如果结构化失败，至少保留原始内容
            result["processed_data"] = {
                "description": raw_result.strip(),
                "parse_error": str(e)
            }
        
        return result
    
    def _parse_ocr_result(self, content: str) -> Dict[str, Any]:
        """解析OCR结果"""
        lines = content.strip().split('\n')
        text_content = []
        position_info = []
        
        current_text = ""
        current_position = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("文字内容："):
                current_text = line.replace("文字内容：", "").strip()
            elif line.startswith("位置信息："):
                current_position = line.replace("位置信息：", "").strip()
                if current_text:
                    text_content.append(current_text)
                    position_info.append(current_position)
                    current_text = ""
                    current_position = ""
        
        return {
            "extracted_text": text_content,
            "positions": position_info,
            "full_text": " ".join(text_content)
        }
    
    def _parse_objects_result(self, content: str) -> Dict[str, Any]:
        """解析对象识别结果"""
        lines = content.strip().split('\n')
        objects = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(tuple('123456789')) or line.startswith('-')):
                # 解析对象信息
                parts = line.split(' - ')
                if len(parts) >= 2:
                    name = parts[0].strip('123456789.- ')
                    position = parts[1] if len(parts) > 1 else "未知位置"
                    description = parts[2] if len(parts) > 2 else ""
                    
                    objects.append({
                        "name": name,
                        "position": position,
                        "description": description
                    })
        
        return {
            "objects": objects,
            "object_count": len(objects),
            "object_names": [obj["name"] for obj in objects]
        }
    
    def _parse_scene_result(self, content: str) -> Dict[str, Any]:
        """解析场景分析结果"""
        lines = content.strip().split('\n')
        scene_data = {
            "scene_type": "",
            "environment": "",
            "additional_info": ""
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith("场景类型："):
                scene_data["scene_type"] = line.replace("场景类型：", "").strip()
            elif line.startswith("环境特征："):
                scene_data["environment"] = line.replace("环境特征：", "").strip()
            elif line.startswith("其他信息："):
                scene_data["additional_info"] = line.replace("其他信息：", "").strip()
        
        return scene_data
    
    def get_supported_task_types(self) -> List[str]:
        """获取支持的任务类型"""
        return ["image_analysis", "ocr", "object_detection", "scene_understanding", "general"]
    
    def get_supported_analysis_types(self) -> List[str]:
        """获取支持的分析类型"""
        return [
            ImageAnalysisType.DESCRIBE,
            ImageAnalysisType.OCR,
            ImageAnalysisType.OBJECTS,
            ImageAnalysisType.SCENE,
            ImageAnalysisType.DETAILED,
            ImageAnalysisType.CUSTOM
        ]
    
    async def analyze_image(
        self,
        image: Union[str, Path, Image.Image, bytes],
        analysis_type: str = ImageAnalysisType.DESCRIBE,
        prompt: str = "",
        **kwargs
    ) -> ToolResult:
        """
        便捷的图像分析方法
        
        Args:
            image: 图像输入
            analysis_type: 分析类型
            prompt: 分析提示
            **kwargs: 额外参数
            
        Returns:
            分析结果
        """
        multimodal_input = MultimodalInput(
            text=prompt,
            image=image,
            task_type="image_analysis"
        )
        
        return await self.execute_multimodal(
            multimodal_input,
            analysis_type=analysis_type,
            **kwargs
        )