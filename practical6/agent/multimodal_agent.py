"""
多模态代理 - 核心实现

基于ReAct推理模式的多模态智能代理，扩展支持图像处理和浏览器自动化。

扩展功能：
1. 多模态输入处理（文本+图像）
2. 智能任务分解和工具选择
3. 图像分析和浏览器自动化
4. 多模态上下文管理

学习要点：
- 继承和扩展现有类
- 多模态数据处理
- 复杂任务的分解策略
- 工具协调和结果整合
"""

import asyncio
import json
import re
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
from PIL import Image
import openai
from openai import AsyncOpenAI

# 导入practical5的基础组件
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'practical5'))

from practical5.agent.react_agent import ReActAgent, AgentState, ReActStep
from practical5.tools.manager import ToolManager
from practical5.tools.base import BaseTool, ToolResult

# 导入多模态工具
from ..tools.multimodal_base import MultimodalTool, MultimodalInput
from ..tools.image_analyzer import ImageAnalyzer
from ..tools.browser_automation import BrowserTool
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = logging.getLogger(__name__)


class MultimodalTaskType(str, Enum):
    """多模态任务类型"""
    IMAGE_ANALYSIS = "image_analysis"           # 纯图像分析
    WEB_AUTOMATION = "web_automation"           # 纯网页自动化
    MULTIMODAL_SEARCH = "multimodal_search"     # 图像+网页搜索
    VISUAL_WEB_TASK = "visual_web_task"         # 视觉引导的网页操作
    GENERAL = "general"                         # 通用任务


@dataclass
class MultimodalStep(ReActStep):
    """
    多模态推理步骤
    
    扩展ReActStep以支持多模态信息。
    """
    image_data: Optional[str] = None            # 图像数据（Base64）
    task_type: str = "general"                  # 任务类型
    multimodal_context: Dict[str, Any] = field(default_factory=dict)  # 多模态上下文
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        base_dict = super().to_dict()
        base_dict.update({
            'image_data': self.image_data,
            'task_type': self.task_type,
            'multimodal_context': self.multimodal_context
        })
        return base_dict


class MultimodalAgent(ReActAgent):
    """
    多模态代理
    
    继承ReAct代理，扩展多模态处理能力。
    
    学习要点：
    - 类的继承和方法重写
    - 多模态数据的统一处理
    - 复杂系统的架构设计
    - 异步编程的高级应用
    """
    
    def __init__(
        self,
        config: Config,
        max_steps: int = 15,  # 多模态任务可能需要更多步骤
        temperature: float = 0.1
    ):
        # 创建工具管理器并注册多模态工具
        tool_manager = self._create_multimodal_tool_manager(config)
        
        # 初始化父类
        super().__init__(
            tool_manager=tool_manager,
            max_steps=max_steps,
            model=config.openai_model,
            temperature=temperature
        )
        
        self.config = config
        self.current_image: Optional[str] = None  # 当前处理的图像
        self.multimodal_context: Dict[str, Any] = {}  # 多模态上下文
        
        # 重新初始化OpenAI客户端以使用配置
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            organization=config.openai_organization
        )
        
        logger.info("多模态代理初始化完成")
    
    def _create_multimodal_tool_manager(self, config: Config) -> ToolManager:
        """创建包含多模态工具的工具管理器"""
        tool_manager = ToolManager()
        
        # 注册基础工具（从practical5复制）
        from ..tools.calculator import CalculatorTool
        from ..tools.text_processor import TextProcessorTool
        
        tool_manager.register_tool(CalculatorTool())
        tool_manager.register_tool(TextProcessorTool())
        
        # 注册多模态工具
        tool_manager.register_tool(ImageAnalyzer(config))
        tool_manager.register_tool(BrowserTool(config))
        
        logger.info(f"注册了 {len(tool_manager.get_available_tools())} 个工具")
        return tool_manager
    
    async def solve_multimodal(
        self,
        user_query: str,
        image: Optional[Union[str, Path, Image.Image, bytes]] = None,
        task_type: str = MultimodalTaskType.GENERAL
    ) -> Dict[str, Any]:
        """
        解决多模态问题
        
        Args:
            user_query: 用户查询文本
            image: 图像输入（可选）
            task_type: 任务类型
            
        Returns:
            解决方案和执行轨迹
        """
        start_time = time.time()
        
        try:
            # 预处理多模态输入
            await self._preprocess_multimodal_input(user_query, image, task_type)
            
            # 执行ReAct循环
            result = await self.solve(user_query)
            
            # 后处理结果
            result = self._postprocess_multimodal_result(result, start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"多模态问题解决失败: {e}")
            return self._generate_error_result(str(e), time.time() - start_time)
        finally:
            # 清理资源
            await self._cleanup_resources()
    
    async def _preprocess_multimodal_input(
        self,
        user_query: str,
        image: Optional[Union[str, Path, Image.Image, bytes]],
        task_type: str
    ) -> None:
        """预处理多模态输入"""
        # 处理图像输入
        if image is not None:
            try:
                # 获取图像分析工具
                image_analyzer = self.tool_manager.get_tool("image_analyzer")
                if image_analyzer:
                    # 处理图像为Base64格式
                    self.current_image = image_analyzer._prepare_image_for_api(image)
                    logger.info("图像预处理完成")
            except Exception as e:
                logger.warning(f"图像预处理失败: {e}")
        
        # 设置多模态上下文
        self.multimodal_context = {
            "has_image": image is not None,
            "task_type": task_type,
            "image_processed": self.current_image is not None,
            "available_tools": self.tool_manager.get_available_tools()
        }
        
        # 分析任务类型并设置策略
        self._analyze_task_strategy(user_query, task_type)
    
    def _analyze_task_strategy(self, user_query: str, task_type: str) -> None:
        """分析任务策略"""
        strategy_hints = {
            MultimodalTaskType.IMAGE_ANALYSIS: "重点使用图像分析工具",
            MultimodalTaskType.WEB_AUTOMATION: "重点使用浏览器自动化工具",
            MultimodalTaskType.MULTIMODAL_SEARCH: "结合图像分析和网页搜索",
            MultimodalTaskType.VISUAL_WEB_TASK: "先分析图像，再执行网页操作",
            MultimodalTaskType.GENERAL: "根据需要选择合适的工具"
        }
        
        self.multimodal_context["strategy_hint"] = strategy_hints.get(
            task_type, 
            strategy_hints[MultimodalTaskType.GENERAL]
        )
    
    def _get_react_prompt(self, user_query: str) -> str:
        """
        重写ReAct提示，添加多模态支持
        
        扩展原有提示以支持：
        1. 多模态工具的使用
        2. 图像分析策略
        3. 浏览器自动化指导
        """
        base_prompt = f"""你是一个智能的多模态代理，能够处理文本和图像输入，并使用各种工具来解决问题。

你需要使用ReAct（Reasoning and Acting）模式来解决用户的问题：
1. Thought: 分析当前情况，思考下一步应该做什么
2. Action: 选择并执行一个工具
3. Observation: 观察工具执行的结果
4. 重复上述过程直到找到最终答案

多模态处理指导：
- 如果用户提供了图像，优先使用image_analyzer工具分析图像内容
- 对于网页相关任务，使用browser_tool进行自动化操作
- 可以结合多个工具来完成复杂任务
- 注意保持上下文的连贯性

当前上下文信息：
- 是否有图像输入: {self.multimodal_context.get('has_image', False)}
- 任务类型: {self.multimodal_context.get('task_type', 'general')}
- 策略提示: {self.multimodal_context.get('strategy_hint', '')}

可用工具：
{self._get_tools_info()}

用户问题: {user_query}

请按照以下格式回答：

Thought: [你的思考过程]
Action: {{"name": "工具名称", "parameters": {{参数字典}}}}
Observation: [等待工具执行结果]

如果你已经有了最终答案，请使用：
Thought: [总结思考]
Final Answer: [最终答案]

{self._get_steps_history()}

现在开始解决问题："""

        return base_prompt
    
    def _get_tools_info(self) -> str:
        """获取工具信息，重点突出多模态工具"""
        tools_info = []
        
        for tool_name in self.tool_manager.get_available_tools():
            tool = self.tool_manager.get_tool(tool_name)
            if tool:
                # 为多模态工具添加特殊标记
                if isinstance(tool, MultimodalTool):
                    marker = "🔥 [多模态工具]"
                else:
                    marker = "📋 [基础工具]"
                
                tools_info.append(f"{marker} {tool.name}: {tool.description}")
                
                # 为特殊工具添加使用提示
                if tool.name == "image_analyzer":
                    tools_info.append("   💡 支持图像描述、OCR、对象识别等功能")
                elif tool.name == "browser_tool":
                    tools_info.append("   💡 支持网页导航、元素操作、截图等功能")
        
        return "\n".join(tools_info)
    
    async def _execute_step(self, user_query: str) -> None:
        """
        重写步骤执行，支持多模态步骤记录
        """
        step_start_time = time.time()
        
        # 构建提示
        prompt = self._get_react_prompt(user_query)
        
        # 调用LLM
        response = await self._call_llm(prompt)
        
        # 解析响应
        thought, action, final_answer = self._parse_response(response)
        
        # 创建多模态步骤记录
        current_step = MultimodalStep(
            step_number=len(self.steps) + 1,
            thought=thought,
            action=action,
            observation=None,
            state=AgentState.THINKING,
            image_data=self.current_image,
            task_type=self.multimodal_context.get('task_type', 'general'),
            multimodal_context=self.multimodal_context.copy()
        )
        
        # 如果有最终答案，直接完成
        if final_answer:
            current_step.observation = final_answer
            current_step.state = AgentState.FINISHED
            current_step.execution_time = time.time() - step_start_time
            self.steps.append(current_step)
            self.state = AgentState.FINISHED
            self.final_answer = final_answer
            return
        
        # 如果没有行动，进入错误状态
        if not action:
            current_step.observation = "无法解析出有效的行动"
            current_step.state = AgentState.ERROR
            current_step.execution_time = time.time() - step_start_time
            self.steps.append(current_step)
            self.state = AgentState.ERROR
            return
        
        # 执行工具
        current_step.state = AgentState.ACTING
        try:
            # 为多模态工具添加图像参数
            if self._is_multimodal_tool(action["name"]) and self.current_image:
                if "parameters" not in action:
                    action["parameters"] = {}
                action["parameters"]["image"] = self.current_image
            
            tool_result = await self._execute_tool(action)
            observation = self._format_tool_result(tool_result)
            
            current_step.observation = observation
            current_step.state = AgentState.OBSERVING
            
            # 更新多模态上下文
            self._update_multimodal_context(action, tool_result)
            
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            current_step.observation = f"工具执行失败: {str(e)}"
            current_step.state = AgentState.ERROR
            self.state = AgentState.ERROR
        
        current_step.execution_time = time.time() - step_start_time
        self.steps.append(current_step)
    
    def _is_multimodal_tool(self, tool_name: str) -> bool:
        """检查是否为多模态工具"""
        tool = self.tool_manager.get_tool(tool_name)
        return isinstance(tool, MultimodalTool)
    
    def _update_multimodal_context(self, action: Dict[str, Any], result: ToolResult) -> None:
        """更新多模态上下文"""
        tool_name = action.get("name", "")
        
        # 记录工具使用历史
        if "tool_usage" not in self.multimodal_context:
            self.multimodal_context["tool_usage"] = []
        
        self.multimodal_context["tool_usage"].append({
            "tool": tool_name,
            "success": result.status.value == "success",
            "timestamp": time.time()
        })
        
        # 特殊处理图像分析结果
        if tool_name == "image_analyzer" and result.data:
            self.multimodal_context["image_analysis"] = result.data
        
        # 特殊处理浏览器操作结果
        if tool_name == "browser_tool" and result.data:
            if "browser_state" not in self.multimodal_context:
                self.multimodal_context["browser_state"] = {}
            
            self.multimodal_context["browser_state"].update({
                "last_action": result.data.get("action"),
                "current_url": result.data.get("current_url"),
                "page_title": result.data.get("page_title")
            })
    
    def _postprocess_multimodal_result(
        self,
        result: Dict[str, Any],
        start_time: float
    ) -> Dict[str, Any]:
        """后处理多模态结果"""
        # 添加多模态特定信息
        result["multimodal_info"] = {
            "had_image_input": self.multimodal_context.get("has_image", False),
            "task_type": self.multimodal_context.get("task_type", "general"),
            "tools_used": [
                usage["tool"] for usage in 
                self.multimodal_context.get("tool_usage", [])
            ],
            "image_analysis_performed": "image_analysis" in self.multimodal_context,
            "browser_automation_used": "browser_state" in self.multimodal_context
        }
        
        # 添加执行统计
        multimodal_steps = [step for step in self.steps if isinstance(step, MultimodalStep)]
        result["execution_stats"]["multimodal_steps"] = len(multimodal_steps)
        
        return result
    
    async def _cleanup_resources(self) -> None:
        """清理多模态资源"""
        try:
            # 清理浏览器资源
            browser_tool = self.tool_manager.get_tool("browser_tool")
            if browser_tool and hasattr(browser_tool, 'close'):
                await browser_tool.close()
            
            # 清理图像数据
            self.current_image = None
            self.multimodal_context.clear()
            
            logger.info("多模态资源清理完成")
            
        except Exception as e:
            logger.warning(f"资源清理时出现异常: {e}")
    
    def get_multimodal_trace(self) -> List[Dict[str, Any]]:
        """获取多模态执行轨迹"""
        return [
            step.to_dict() for step in self.steps 
            if isinstance(step, MultimodalStep)
        ]
    
    async def analyze_image(
        self,
        image: Union[str, Path, Image.Image, bytes],
        prompt: str = "请分析这张图片的内容",
        analysis_type: str = "describe"
    ) -> Dict[str, Any]:
        """
        便捷的图像分析方法
        
        Args:
            image: 图像输入
            prompt: 分析提示
            analysis_type: 分析类型
            
        Returns:
            分析结果
        """
        return await self.solve_multimodal(
            user_query=prompt,
            image=image,
            task_type=MultimodalTaskType.IMAGE_ANALYSIS
        )
    
    async def automate_browser(
        self,
        task_description: str,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        便捷的浏览器自动化方法
        
        Args:
            task_description: 任务描述
            url: 起始URL（可选）
            
        Returns:
            自动化结果
        """
        query = task_description
        if url:
            query = f"请访问 {url} 并执行以下任务：{task_description}"
        
        return await self.solve_multimodal(
            user_query=query,
            task_type=MultimodalTaskType.WEB_AUTOMATION
        )
    
    async def visual_web_task(
        self,
        image: Union[str, Path, Image.Image, bytes],
        task_description: str
    ) -> Dict[str, Any]:
        """
        视觉引导的网页任务
        
        Args:
            image: 参考图像
            task_description: 任务描述
            
        Returns:
            任务结果
        """
        query = f"根据提供的图像，执行以下网页任务：{task_description}"
        
        return await self.solve_multimodal(
            user_query=query,
            image=image,
            task_type=MultimodalTaskType.VISUAL_WEB_TASK
        )