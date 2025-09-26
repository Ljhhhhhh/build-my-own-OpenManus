"""
多模态工具基类

这个模块定义了多模态工具的抽象基类，为处理文本和图像输入提供统一接口。

学习要点：
- 抽象基类的设计模式
- 多模态数据处理
- 图像编码/解码
- 异步编程模式
- 类型注解和验证
"""

import base64
import io
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Union, Dict, Any, List
from pathlib import Path
from PIL import Image
import logging

from .base import BaseTool, ToolResult, ToolResultStatus
from ..utils.config import Config

logger = logging.getLogger(__name__)


class MultimodalInput:
    """
    多模态输入数据类
    
    封装文本和图像输入，提供统一的数据接口。
    
    学习要点：
    - 数据封装的重要性
    - 类型验证和转换
    - 图像数据的多种表示形式
    """
    
    def __init__(
        self,
        text: str,
        image: Optional[Union[str, Path, Image.Image, bytes]] = None,
        task_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.image = image
        self.task_type = task_type
        self.metadata = metadata or {}
        
        # 验证输入
        self._validate_input()
    
    def _validate_input(self) -> None:
        """验证输入数据的有效性"""
        if not isinstance(self.text, str):
            raise ValueError("文本输入必须是字符串类型")
        
        if self.image is not None:
            if not isinstance(self.image, (str, Path, Image.Image, bytes)):
                raise ValueError("图像输入必须是文件路径、PIL图像对象或字节数据")
    
    def has_image(self) -> bool:
        """检查是否包含图像数据"""
        return self.image is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "text": self.text,
            "has_image": self.has_image(),
            "task_type": self.task_type,
            "metadata": self.metadata
        }


class ImageProcessor:
    """
    图像处理工具类
    
    提供图像加载、编码、解码、压缩等功能。
    
    学习要点：
    - 图像处理的基本操作
    - Base64编码的使用
    - 错误处理和资源管理
    - 配置驱动的设计
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.supported_formats = set(config.supported_image_formats)
    
    def load_image(self, image_input: Union[str, Path, Image.Image, bytes]) -> Image.Image:
        """
        加载图像数据
        
        Args:
            image_input: 图像输入（文件路径、PIL对象或字节数据）
            
        Returns:
            PIL.Image对象
            
        Raises:
            ValueError: 不支持的图像格式
            FileNotFoundError: 图像文件不存在
        """
        try:
            if isinstance(image_input, Image.Image):
                return image_input
            elif isinstance(image_input, (str, Path)):
                path = Path(image_input)
                if not path.exists():
                    raise FileNotFoundError(f"图像文件不存在: {path}")
                
                # 检查文件格式
                if path.suffix.lower().lstrip('.') not in self.supported_formats:
                    raise ValueError(f"不支持的图像格式: {path.suffix}")
                
                return Image.open(path)
            elif isinstance(image_input, bytes):
                return Image.open(io.BytesIO(image_input))
            else:
                raise ValueError(f"不支持的图像输入类型: {type(image_input)}")
                
        except Exception as e:
            logger.error(f"加载图像失败: {e}")
            raise
    
    def resize_image(self, image: Image.Image) -> Image.Image:
        """
        调整图像尺寸
        
        根据配置的最大尺寸调整图像大小，保持宽高比。
        """
        max_width = self.config.max_image_width
        max_height = self.config.max_image_height
        
        # 如果图像尺寸在限制内，直接返回
        if image.width <= max_width and image.height <= max_height:
            return image
        
        # 计算缩放比例
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        scale_ratio = min(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(image.width * scale_ratio)
        new_height = int(image.height * scale_ratio)
        
        # 调整尺寸
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"图像尺寸调整: {image.width}x{image.height} -> {new_width}x{new_height}")
        
        return resized_image
    
    def encode_to_base64(self, image: Image.Image, format: str = "JPEG") -> str:
        """
        将图像编码为Base64字符串
        
        Args:
            image: PIL图像对象
            format: 输出格式（JPEG、PNG等）
            
        Returns:
            Base64编码的图像字符串
        """
        try:
            # 如果是RGBA模式且要保存为JPEG，需要转换为RGB
            if image.mode == "RGBA" and format.upper() == "JPEG":
                # 创建白色背景
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为mask
                image = background
            
            # 保存到内存缓冲区
            buffer = io.BytesIO()
            save_kwargs = {}
            
            if format.upper() == "JPEG":
                save_kwargs["quality"] = self.config.image_quality
                save_kwargs["optimize"] = True
            
            image.save(buffer, format=format, **save_kwargs)
            
            # 编码为Base64
            image_bytes = buffer.getvalue()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            logger.debug(f"图像编码完成: {format}, 大小: {len(image_bytes)} bytes")
            return base64_string
            
        except Exception as e:
            logger.error(f"图像编码失败: {e}")
            raise
    
    def decode_from_base64(self, base64_string: str) -> Image.Image:
        """
        从Base64字符串解码图像
        
        Args:
            base64_string: Base64编码的图像字符串
            
        Returns:
            PIL图像对象
        """
        try:
            # 解码Base64
            image_bytes = base64.b64decode(base64_string)
            
            # 加载图像
            image = Image.open(io.BytesIO(image_bytes))
            
            logger.debug(f"图像解码完成: {image.mode}, 尺寸: {image.size}")
            return image
            
        except Exception as e:
            logger.error(f"图像解码失败: {e}")
            raise
    
    def process_image(self, image_input: Union[str, Path, Image.Image, bytes]) -> str:
        """
        处理图像输入，返回Base64编码字符串
        
        这是一个便捷方法，集成了加载、调整尺寸和编码的完整流程。
        
        Args:
            image_input: 图像输入
            
        Returns:
            Base64编码的图像字符串
        """
        try:
            # 加载图像
            image = self.load_image(image_input)
            
            # 调整尺寸
            image = self.resize_image(image)
            
            # 编码为Base64
            base64_string = self.encode_to_base64(image)
            
            return base64_string
            
        except Exception as e:
            logger.error(f"图像处理失败: {e}")
            raise


class MultimodalTool(BaseTool, ABC):
    """
    多模态工具抽象基类
    
    扩展BaseTool以支持多模态输入（文本+图像）。
    所有多模态工具都应该继承这个类。
    
    学习要点：
    - 抽象基类的继承和扩展
    - 多模态数据的统一处理接口
    - 异步方法的设计
    - 配置注入和依赖管理
    """
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.image_processor = ImageProcessor(config)
    
    @abstractmethod
    async def execute_multimodal(
        self,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> ToolResult:
        """
        执行多模态工具操作
        
        这是多模态工具的核心方法，子类必须实现。
        
        Args:
            multimodal_input: 多模态输入数据
            **kwargs: 额外的参数
            
        Returns:
            工具执行结果
        """
        pass
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        实现BaseTool的execute方法
        
        这个方法将传统的参数转换为MultimodalInput格式，
        然后调用execute_multimodal方法。
        """
        try:
            # 从kwargs中提取参数
            text = kwargs.get("text", "")
            image = kwargs.get("image")
            task_type = kwargs.get("task_type", "general")
            metadata = kwargs.get("metadata", {})
            
            # 创建多模态输入
            multimodal_input = MultimodalInput(
                text=text,
                image=image,
                task_type=task_type,
                metadata=metadata
            )
            
            # 执行多模态操作
            return await self.execute_multimodal(multimodal_input, **kwargs)
            
        except Exception as e:
            logger.error(f"多模态工具执行失败 [{self.name}]: {e}")
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data={"error": str(e)},
                message=f"工具执行失败: {e}"
            )
    
    def _prepare_image_for_api(self, image_input: Union[str, Path, Image.Image, bytes]) -> str:
        """
        为API调用准备图像数据
        
        这是一个便捷方法，处理图像并返回适合API调用的格式。
        
        Args:
            image_input: 图像输入
            
        Returns:
            处理后的图像数据（通常是Base64字符串）
        """
        return self.image_processor.process_image(image_input)
    
    def _validate_multimodal_input(self, multimodal_input: MultimodalInput) -> None:
        """
        验证多模态输入的有效性
        
        子类可以重写这个方法来添加特定的验证逻辑。
        """
        if not multimodal_input.text.strip():
            raise ValueError("文本输入不能为空")
    
    async def _handle_timeout(self, coro, timeout: Optional[int] = None) -> Any:
        """
        处理异步操作的超时
        
        Args:
            coro: 协程对象
            timeout: 超时时间（秒），如果为None则使用配置中的默认值
            
        Returns:
            协程执行结果
            
        Raises:
            asyncio.TimeoutError: 操作超时
        """
        if timeout is None:
            timeout = self.config.tool_timeout
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"工具操作超时 [{self.name}]: {timeout}秒")
            raise
    
    def get_supported_task_types(self) -> List[str]:
        """
        获取工具支持的任务类型
        
        子类应该重写这个方法来指定支持的任务类型。
        
        Returns:
            支持的任务类型列表
        """
        return ["general"]
    
    def supports_task_type(self, task_type: str) -> bool:
        """
        检查工具是否支持指定的任务类型
        
        Args:
            task_type: 任务类型
            
        Returns:
            是否支持该任务类型
        """
        return task_type in self.get_supported_task_types()