"""
ReAct推理代理 - 核心实现

这个模块实现了ReAct（Reasoning and Acting）推理模式的智能代理。

ReAct模式的核心思想：
1. Thought（思考）：分析当前情况，决定下一步行动
2. Action（行动）：执行具体的工具调用
3. Observation（观察）：获取行动的结果，为下一轮思考提供信息

学习要点：
- 状态机设计模式
- 循环推理的实现
- 提示词工程
- 异步编程实践
- 错误处理和恢复
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import openai
from openai import AsyncOpenAI

from tools.manager import ToolManager
from tools.base import BaseTool, ToolResult
from utils.config import get_config
from utils.logger import setup_logger


class AgentState(str, Enum):
    """
    代理状态枚举
    
    定义了ReAct代理在推理过程中的不同状态。
    
    学习要点：
    - 继承str和Enum，使枚举值可以直接作为字符串使用
    - 明确的状态定义有助于调试和理解代理行为
    - 状态转换逻辑清晰，便于扩展和维护
    """
    THINKING = "thinking"      # 思考阶段：分析问题，决定下一步行动
    ACTING = "acting"          # 行动阶段：执行工具调用
    OBSERVING = "observing"    # 观察阶段：处理工具执行结果
    FINISHED = "finished"      # 完成状态：已找到最终答案
    ERROR = "error"            # 错误状态：发生不可恢复的错误


@dataclass
class ReActStep:
    """
    ReAct推理步骤数据类
    
    记录推理过程中每个步骤的完整信息，用于：
    1. 追踪推理轨迹
    2. 调试和分析
    3. 生成执行报告
    
    学习要点：
    - @dataclass装饰器简化数据类定义
    - Optional类型表示可选字段
    - field()用于设置默认值和元数据
    """
    step_number: int                    # 步骤编号（从1开始）
    thought: str                        # 思考内容
    action: Optional[Dict[str, Any]]    # 行动（工具调用），格式：{"name": "工具名", "parameters": {...}}
    observation: Optional[str]          # 观察结果（工具执行结果）
    state: AgentState                   # 当前状态
    timestamp: float = field(default_factory=time.time)  # 时间戳
    execution_time: Optional[float] = None  # 步骤执行时间（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'step_number': self.step_number,
            'thought': self.thought,
            'action': self.action,
            'observation': self.observation,
            'state': self.state.value,
            'timestamp': self.timestamp,
            'execution_time': self.execution_time
        }


class ReActAgent:
    """
    ReAct推理代理
    
    实现了完整的ReAct推理循环，能够：
    1. 接收用户问题
    2. 进行循环的思考-行动-观察
    3. 调用工具解决问题
    4. 返回最终答案和执行轨迹
    
    学习要点：
    - 状态机的实现
    - 异步编程模式
    - LLM API的集成
    - 工具系统的使用
    - 错误处理和恢复
    """
    
    def __init__(
        self,
        tool_manager: ToolManager,
        max_steps: int = 10,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.1
    ):
        """
        初始化ReAct代理
        
        Args:
            tool_manager: 工具管理器实例
            max_steps: 最大推理步数（防止无限循环）
            model: 使用的LLM模型
            temperature: 生成温度（0-1，越低越确定性）
        """
        self.tool_manager = tool_manager
        self.max_steps = max_steps
        self.model = model
        self.temperature = temperature
        
        # 状态管理
        self.state = AgentState.THINKING
        self.current_step = 0
        self.steps: List[ReActStep] = []
        
        # 配置和日志
        self.config = get_config()
        self.logger = setup_logger("practical5.ReActAgent")
        
        # OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_base_url,
            organization=self.config.openai_organization
        )
        
        self.logger.info(f"ReAct代理初始化完成，最大步数: {max_steps}, 模型: {model}")
    
    async def solve(self, user_query: str) -> Dict[str, Any]:
        """
        解决用户问题的主要方法
        
        这是ReAct代理的核心方法，实现了完整的推理循环。
        
        Args:
            user_query: 用户问题
            
        Returns:
            Dict: 包含最终答案和执行轨迹的结果
        """
        self.logger.info(f"开始解决问题: {user_query}")
        start_time = time.time()
        
        # 重置状态
        self._reset_state()
        
        try:
            # 主推理循环
            while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
                step_start_time = time.time()
                
                # 执行单个推理步骤
                await self._execute_step(user_query)
                
                # 记录步骤执行时间
                if self.steps:
                    self.steps[-1].execution_time = time.time() - step_start_time
                
                # 检查是否需要终止
                if self.state == AgentState.ERROR:
                    break
            
            # 生成最终结果
            total_time = time.time() - start_time
            result = self._generate_final_result(user_query, total_time)
            
            self.logger.info(f"问题解决完成，总耗时: {total_time:.2f}秒，步数: {self.current_step}")
            return result
            
        except Exception as e:
            self.logger.error(f"解决问题时发生异常: {e}")
            self.state = AgentState.ERROR
            return self._generate_error_result(str(e), time.time() - start_time)
    
    async def _execute_step(self, user_query: str) -> None:
        """
        执行单个ReAct推理步骤
        
        这个方法实现了ReAct的核心循环：
        1. 生成提示词
        2. 调用LLM获取响应
        3. 解析响应（思考和行动）
        4. 执行工具调用（如果有）
        5. 更新状态
        
        Args:
            user_query: 用户问题
        """
        self.current_step += 1
        self.logger.debug(f"执行第 {self.current_step} 步推理")
        
        try:
            # 1. 生成ReAct提示词
            prompt = self._get_react_prompt(user_query)
            
            # 2. 调用LLM
            response = await self._call_llm(prompt)
            
            # 3. 解析LLM响应
            thought, action, final_answer = self._parse_response(response)
            
            # 4. 创建步骤记录
            step = ReActStep(
                step_number=self.current_step,
                thought=thought,
                action=action,
                observation=None,
                state=self.state
            )
            
            # 5. 处理不同情况
            if final_answer:
                # 找到最终答案，结束推理
                step.observation = f"最终答案: {final_answer}"
                step.state = AgentState.FINISHED
                self.state = AgentState.FINISHED
                self.steps.append(step)
                
            elif action:
                # 需要执行工具调用
                step.state = AgentState.ACTING
                self.state = AgentState.ACTING
                
                # 执行工具
                tool_result = await self._execute_tool(action)
                step.observation = self._format_tool_result(tool_result)
                step.state = AgentState.OBSERVING
                self.state = AgentState.THINKING  # 准备下一轮思考
                
                self.steps.append(step)
                
            else:
                # 只有思考，没有行动，继续思考
                step.observation = "继续思考中..."
                step.state = AgentState.THINKING
                self.state = AgentState.THINKING
                self.steps.append(step)
                
        except Exception as e:
            self.logger.error(f"执行步骤 {self.current_step} 时发生错误: {e}")
            # 创建错误步骤记录
            error_step = ReActStep(
                step_number=self.current_step,
                thought=f"执行过程中发生错误: {e}",
                action=None,
                observation=f"错误: {e}",
                state=AgentState.ERROR
            )
            self.steps.append(error_step)
            self.state = AgentState.ERROR
    
    def _get_react_prompt(self, user_query: str) -> str:
        """
        生成ReAct格式的提示词
        
        这是ReAct代理的核心提示词工程，定义了：
        1. 代理的角色和能力
        2. 可用工具的信息
        3. ReAct格式的要求
        4. 历史步骤的上下文
        
        Args:
            user_query: 用户问题
            
        Returns:
            str: 格式化的提示词
        """
        # 获取工具信息
        tools_info = self._get_tools_info()
        
        # 获取历史步骤
        steps_history = self._get_steps_history()
        
        prompt = f"""你是一个使用ReAct（Reasoning and Acting）模式的智能代理。

用户问题：{user_query}

可用工具：
{tools_info}

你需要按照以下格式进行推理和行动：

Thought: [你的思考过程，分析当前情况，决定下一步行动]
Action: {{"name": "工具名称", "parameters": {{"参数名": "参数值"}}}}
Observation: [工具执行结果，由系统自动填入]

如果你认为已经获得了足够的信息来回答用户问题，请输出：
Thought: [最终思考过程]
Final Answer: [最终答案]

重要规则：
1. 每次只能输出一个Thought和一个Action（或Final Answer）
2. Action必须是有效的JSON格式
3. 只能使用上面列出的工具
4. 仔细分析每个Observation的结果
5. 如果遇到错误，要分析原因并尝试其他方法

历史步骤：
{steps_history}

请继续下一步推理："""
        
        return prompt
    
    def _get_tools_info(self) -> str:
        """
        获取工具信息的格式化字符串
        
        Returns:
            str: 工具信息
        """
        tools = self.tool_manager.list_tools()
        if not tools:
            return "暂无可用工具"
        
        tools_info = []
        for tool in tools:
            info = f"- {tool['name']}: {tool['description']}"
            # 添加参数信息
            schema = tool.get('schema', {})
            if 'properties' in schema:
                params = []
                required = schema.get('required', [])
                for param_name, param_info in schema['properties'].items():
                    param_desc = param_info.get('description', '')
                    param_type = param_info.get('type', 'any')
                    is_required = param_name in required
                    req_mark = "*" if is_required else ""
                    params.append(f"{param_name}{req_mark}({param_type}): {param_desc}")
                
                if params:
                    info += f"\n  参数: {', '.join(params)}"
            
            tools_info.append(info)
        
        return "\n".join(tools_info)
    
    def _get_steps_history(self) -> str:
        """
        获取历史步骤的格式化字符串
        
        Returns:
            str: 历史步骤信息
        """
        if not self.steps:
            return "暂无历史步骤"
        
        history = []
        for step in self.steps:
            history.append(f"步骤 {step.step_number}:")
            history.append(f"Thought: {step.thought}")
            
            if step.action:
                action_str = json.dumps(step.action, ensure_ascii=False)
                history.append(f"Action: {action_str}")
            
            if step.observation:
                history.append(f"Observation: {step.observation}")
            
            history.append("")  # 空行分隔
        
        return "\n".join(history)
    
    async def _call_llm(self, prompt: str) -> str:
        """
        调用LLM获取响应
        
        Args:
            prompt: 提示词
            
        Returns:
            str: LLM响应
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"调用LLM时发生错误: {e}")
            raise
    
    def _parse_response(self, response: str) -> tuple[str, Optional[Dict[str, Any]], Optional[str]]:
        """
        解析LLM响应，提取思考、行动和最终答案
        
        Args:
            response: LLM响应文本
            
        Returns:
            tuple: (思考内容, 行动字典, 最终答案)
        """
        thought = ""
        action = None
        final_answer = None
        
        try:
            # 提取Thought
            thought_match = re.search(r'Thought:\s*(.*?)(?=\n(?:Action|Final Answer):|$)', response, re.DOTALL)
            if thought_match:
                thought = thought_match.group(1).strip()
            
            # 检查是否有Final Answer
            final_answer_match = re.search(r'Final Answer:\s*(.*?)$', response, re.DOTALL)
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                return thought, None, final_answer
            
            # 提取Action
            action_match = re.search(r'Action:\s*(\{.*?\})', response, re.DOTALL)
            if action_match:
                try:
                    action_str = action_match.group(1).strip()
                    # 处理可能的换行符和多余空格
                    action_str = re.sub(r'\s+', ' ', action_str)
                    action = json.loads(action_str)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"解析Action JSON失败: {e}, 原文: {action_str}")
                    # 尝试修复常见的JSON格式问题
                    try:
                        # 如果缺少结束括号，尝试添加
                        if action_str.count('{') > action_str.count('}'):
                            action_str += '}'
                        action = json.loads(action_str)
                    except json.JSONDecodeError:
                        action = None
            
            return thought, action, final_answer
            
        except Exception as e:
            self.logger.error(f"解析LLM响应时发生错误: {e}")
            return f"解析错误: {e}", None, None
    
    async def _execute_tool(self, action: Dict[str, Any]) -> ToolResult:
        """
        执行工具调用
        
        Args:
            action: 工具调用信息
            
        Returns:
            ToolResult: 工具执行结果
        """
        try:
            tool_name = action.get('name')
            parameters = action.get('parameters', {})
            
            if not tool_name:
                return ToolResult.error("工具名称不能为空")
            
            self.logger.debug(f"执行工具: {tool_name}, 参数: {parameters}")
            
            result = await self.tool_manager.execute_tool(tool_name, **parameters)
            return result
            
        except Exception as e:
            self.logger.error(f"执行工具时发生错误: {e}")
            return ToolResult.error(f"工具执行异常: {e}")
    
    def _format_tool_result(self, result: ToolResult) -> str:
        """
        格式化工具执行结果
        
        Args:
            result: 工具执行结果
            
        Returns:
            str: 格式化的结果字符串
        """
        if result.is_success:
            content = result.content
            if isinstance(content, dict):
                # 格式化字典内容
                formatted_content = json.dumps(content, ensure_ascii=False, indent=2)
                return f"工具执行成功:\n{formatted_content}"
            else:
                return f"工具执行成功: {content}"
        else:
            return f"工具执行失败: {result.error_message}"
    
    def _reset_state(self) -> None:
        """重置代理状态"""
        self.state = AgentState.THINKING
        self.current_step = 0
        self.steps = []
    
    def _generate_final_result(self, user_query: str, total_time: float) -> Dict[str, Any]:
        """
        生成最终结果
        
        Args:
            user_query: 用户问题
            total_time: 总执行时间
            
        Returns:
            Dict: 最终结果
        """
        # 提取最终答案
        final_answer = "未找到答案"
        if self.steps and self.state == AgentState.FINISHED:
            last_step = self.steps[-1]
            if "最终答案:" in last_step.observation:
                final_answer = last_step.observation.replace("最终答案:", "").strip()
        
        return {
            'success': self.state == AgentState.FINISHED,
            'final_answer': final_answer,
            'user_query': user_query,
            'total_steps': self.current_step,
            'total_time': total_time,
            'final_state': self.state.value,
            'execution_trace': [step.to_dict() for step in self.steps],
            'summary': {
                'max_steps_reached': self.current_step >= self.max_steps,
                'tools_used': list(set(
                    step.action['name'] for step in self.steps 
                    if step.action and 'name' in step.action
                )),
                'average_step_time': total_time / max(self.current_step, 1)
            }
        }
    
    def _generate_error_result(self, error_message: str, total_time: float) -> Dict[str, Any]:
        """
        生成错误结果
        
        Args:
            error_message: 错误信息
            total_time: 总执行时间
            
        Returns:
            Dict: 错误结果
        """
        return {
            'success': False,
            'final_answer': f"执行过程中发生错误: {error_message}",
            'user_query': "",
            'total_steps': self.current_step,
            'total_time': total_time,
            'final_state': AgentState.ERROR.value,
            'execution_trace': [step.to_dict() for step in self.steps],
            'error': error_message
        }
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """
        获取执行轨迹
        
        Returns:
            List[Dict]: 执行轨迹列表
        """
        return [step.to_dict() for step in self.steps]