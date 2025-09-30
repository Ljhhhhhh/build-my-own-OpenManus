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
        # 让logger同时记录INFO和DEBUG级别日志到react_agent.log
        self.logger = setup_logger("practical5.ReActAgent", level="DEBUG", log_file="logs/react_agent.log")
        
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
        self.logger.info(f"{'='*60}")
        self.logger.info(f"开始执行第 {self.current_step} 步推理")
        self.logger.info(f"当前状态: {self.state.value}")
        self.logger.info(f"用户问题: {user_query}")
        
        try:
            # ===== 阶段1: 生成ReAct提示词 =====
            self.logger.info(f"[阶段1] 开始生成ReAct提示词")
            self.logger.debug(f"  - 当前已有步骤数: {len(self.steps)}")
            self.logger.debug(f"  - 可用工具数: {len(self.tool_manager.list_tools())}")
            
            prompt = self._get_react_prompt(user_query)
            
            self.logger.debug(f"  - 提示词生成完成，长度: {len(prompt)} 字符")
            self.logger.debug(f"  - 提示词预览: {prompt}...")
            
            # ===== 阶段2: 调用LLM =====
            self.logger.info(f"[阶段2] 开始调用LLM")
            self.logger.debug(f"  - 使用模型: {self.model}")
            self.logger.debug(f"  - 温度参数: {self.temperature}")
            
            llm_start_time = time.time()
            response = await self._call_llm(prompt)
            llm_duration = time.time() - llm_start_time
            
            self.logger.info(f"  - LLM响应完成，耗时: {llm_duration:.2f}秒")
            self.logger.debug(f"  - 响应长度: {len(response)} 字符")
            self.logger.debug(f"  - 完整响应内容:\n{response}")
            
            # ===== 阶段3: 解析LLM响应 =====
            self.logger.info(f"[阶段3] 开始解析LLM响应")
            
            thought, action, final_answer = self._parse_response(response)
            
            self.logger.info(f"  - 解析完成")
            self.logger.info(f"  - Thought: {thought}")
            
            if final_answer:
                self.logger.info(f"  - 找到最终答案: {final_answer}")
            elif action:
                self.logger.info(f"  - 需要执行Action: {json.dumps(action, ensure_ascii=False)}")
            else:
                self.logger.info(f"  - 仅有思考，无具体行动")
            
            # ===== 阶段4: 创建步骤记录 =====
            self.logger.info(f"[阶段4] 创建步骤记录")
            
            step = ReActStep(
                step_number=self.current_step,
                thought=thought,
                action=action,
                observation=None,
                state=self.state
            )
            
            self.logger.debug(f"  - 步骤记录创建完成: Step #{step.step_number}")
            
            # ===== 阶段5: 处理不同情况 =====
            self.logger.info(f"[阶段5] 根据解析结果处理不同分支")
            
            if final_answer:
                # 分支A: 找到最终答案，结束推理
                self.logger.info(f"  >>> 分支A: 检测到最终答案，准备结束推理")
                self.logger.info(f"      最终答案内容: {final_answer}")
                
                step.observation = f"最终答案: {final_answer}"
                step.state = AgentState.FINISHED
                self.state = AgentState.FINISHED
                self.steps.append(step)
                
                self.logger.info(f"      状态更新: {AgentState.THINKING.value} -> {AgentState.FINISHED.value}")
                self.logger.info(f"      推理完成！总步数: {self.current_step}")
                
            elif action:
                # 分支B: 需要执行工具调用
                self.logger.info(f"  >>> 分支B: 需要执行工具调用")
                
                tool_name = action.get('name', 'unknown')
                tool_params = action.get('parameters', {})
                
                self.logger.info(f"      工具名称: {tool_name}")
                self.logger.info(f"      工具参数: {json.dumps(tool_params, ensure_ascii=False)}")
                
                step.state = AgentState.ACTING
                self.state = AgentState.ACTING
                
                self.logger.debug(f"      状态更新: -> {AgentState.ACTING.value}")
                
                # 执行工具
                self.logger.info(f"      [5.1] 开始执行工具调用")
                tool_start_time = time.time()
                
                tool_result = await self._execute_tool(action)
                
                tool_duration = time.time() - tool_start_time
                self.logger.info(f"      [5.1] 工具执行完成，耗时: {tool_duration:.2f}秒")
                self.logger.info(f"      工具执行结果: 成功={tool_result.is_success}")
                
                if tool_result.is_success:
                    self.logger.debug(f"      返回内容: {str(tool_result.content)[:200]}...")
                else:
                    self.logger.warning(f"      错误信息: {tool_result.error_message}")
                
                step.observation = self._format_tool_result(tool_result)
                step.state = AgentState.OBSERVING
                self.state = AgentState.THINKING  # 准备下一轮思考
                
                self.logger.debug(f"      状态更新: {AgentState.ACTING.value} -> {AgentState.OBSERVING.value} -> {AgentState.THINKING.value}")
                
                self.steps.append(step)
                
                self.logger.info(f"      步骤记录已保存，进入下一轮推理")
                
            else:
                # 分支C: 只有思考，没有行动，继续思考
                self.logger.info(f"  >>> 分支C: 仅有思考，无具体行动")
                self.logger.warning(f"      注意: LLM未给出Action或Final Answer，可能需要引导")
                
                step.observation = "继续思考中..."
                step.state = AgentState.THINKING
                self.state = AgentState.THINKING
                self.steps.append(step)
                
                self.logger.debug(f"      保持思考状态，进入下一轮")
            
            self.logger.info(f"第 {self.current_step} 步执行完成")
            self.logger.info(f"{'='*60}\n")
                
        except Exception as e:
            self.logger.error(f"{'!'*60}")
            self.logger.error(f"执行步骤 {self.current_step} 时发生错误")
            self.logger.error(f"错误类型: {type(e).__name__}")
            self.logger.error(f"错误信息: {str(e)}")
            self.logger.error(f"错误位置: ", exc_info=True)
            
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
            
            self.logger.error(f"状态更新为: {AgentState.ERROR.value}")
            self.logger.error(f"{'!'*60}\n")
    
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
        获取详细工具信息
        
        Returns:
            str: 工具信息
        """
        tools = self.tool_manager.list_tools()
        if not tools:
            return "暂无可用工具"
        
        tools_info = []
        for tool in tools:
            # 工具名称和描述
            info_lines = [f"\n【工具】{tool['name']}"]
            info_lines.append(f"  描述: {tool['description']}")
            
            # 添加参数信息
            schema = tool.get('schema', {})
            if 'properties' in schema:
                info_lines.append(f"  参数:")
                required = schema.get('required', [])
                
                for param_name, param_info in schema['properties'].items():
                    param_desc = param_info.get('description', '无描述')
                    param_type = param_info.get('type', 'any')
                    is_required = param_name in required
                    req_mark = "[必需]" if is_required else "[可选]"
                    
                    # 基本参数信息
                    param_line = f"    - {param_name} {req_mark} ({param_type}): {param_desc}"
                    
                    # 特别处理：如果参数有枚举值，显示所有可选值
                    if 'enum' in param_info:
                        enum_values = param_info['enum']
                        param_line += f"\n      可选值: {', '.join(map(str, enum_values))}"
                        
                        # 如果工具实例有获取操作描述的方法，使用它
                        tool_instance = self._get_tool_instance(tool['name'])
                        if tool_instance and hasattr(tool_instance, 'get_operation_description'):
                            # 为每个操作添加详细说明
                            operation_details = []
                            for op in enum_values:
                                op_desc = tool_instance.get_operation_description(op)
                                if op_desc:
                                    operation_details.append(f"'{op}': {op_desc}")
                            
                            if operation_details:
                                param_line += f"\n      操作说明:"
                                for detail in operation_details:
                                    param_line += f"\n        • {detail}"
                    
                    # 处理其他约束
                    if 'minimum' in param_info:
                        param_line += f" (最小值: {param_info['minimum']})"
                    if 'maximum' in param_info:
                        param_line += f" (最大值: {param_info['maximum']})"
                    if 'default' in param_info:
                        param_line += f" (默认: {param_info['default']})"
                    
                    info_lines.append(param_line)
            
            tools_info.append('\n'.join(info_lines))
        
        return '\n'.join(tools_info)
    
    def _get_tool_instance(self, tool_name: str):
        """
        获取工具实例
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例，如果不存在则返回None
        """
        try:
            # 从工具管理器获取工具实例
            if hasattr(self.tool_manager, '_tools'):
                return self.tool_manager._tools.get(tool_name)
            return None
        except Exception as e:
            self.logger.debug(f"获取工具实例失败: {e}")
            return None
    
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
            
            # 提取Action - 使用改进的方法处理嵌套JSON
            action_str = self._extract_action_json(response)
            if action_str:
                try:
                    # 处理可能的换行符和多余空格
                    action_str_cleaned = re.sub(r'\s+', ' ', action_str)
                    action = json.loads(action_str_cleaned)
                    self.logger.debug(f"成功解析Action JSON: {action}")
                except json.JSONDecodeError as e:
                    self.logger.warning(f"解析Action JSON失败: {e}")
                    self.logger.debug(f"原始字符串: {action_str}")
                    self.logger.debug(f"清理后字符串: {action_str_cleaned}")
                    
                    # 尝试修复常见的JSON格式问题
                    action = self._try_fix_json(action_str_cleaned)
                    if action:
                        self.logger.info(f"JSON修复成功: {action}")
            
            return thought, action, final_answer
            
        except Exception as e:
            self.logger.error(f"解析LLM响应时发生错误: {e}")
            return f"解析错误: {e}", None, None
    
    def _extract_action_json(self, response: str) -> Optional[str]:
        """
        从响应中提取Action的JSON字符串（支持嵌套JSON）
        
        使用括号计数法来正确处理嵌套的JSON对象
        
        Args:
            response: LLM响应文本
            
        Returns:
            Optional[str]: 提取的JSON字符串，如果没找到则返回None
        """
        # 查找Action:的位置
        action_match = re.search(r'Action:\s*', response)
        if not action_match:
            return None
        
        start_pos = action_match.end()
        
        # 跳过Action:后面的空白字符，找到{的位置
        while start_pos < len(response) and response[start_pos].isspace():
            start_pos += 1
        
        if start_pos >= len(response) or response[start_pos] != '{':
            self.logger.warning(f"Action后面没有找到JSON对象起始符 '{{' ")
            return None
        
        # 使用括号计数法提取完整的JSON对象
        brace_count = 0
        in_string = False
        escape_next = False
        json_start = start_pos
        
        for i in range(start_pos, len(response)):
            char = response[i]
            
            # 处理字符串中的转义字符
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            # 处理字符串边界（只在非转义的引号时切换）
            if char == '"':
                in_string = not in_string
                continue
            
            # 只在字符串外部计数括号
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    
                    # 当括号计数回到0时，说明找到了完整的JSON对象
                    if brace_count == 0:
                        json_str = response[json_start:i+1]
                        self.logger.debug(f"提取的JSON字符串长度: {len(json_str)}")
                        return json_str
        
        # 如果循环结束还没找到完整的JSON，返回已找到的部分
        partial_json = response[json_start:]
        self.logger.warning(f"未找到完整的JSON对象，括号不匹配，缺少 {brace_count} 个 '}}'")
        self.logger.debug(f"部分JSON: {partial_json[:200]}...")
        return partial_json
    
    def _try_fix_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """
        尝试修复常见的JSON格式问题
        
        Args:
            json_str: 可能有问题的JSON字符串
            
        Returns:
            Optional[Dict]: 修复后的JSON对象，如果无法修复则返回None
        """
        fixes_attempted = []
        
        try:
            # 修复1: 补全缺失的结束括号
            open_braces = json_str.count('{')
            close_braces = json_str.count('}')
            if open_braces > close_braces:
                missing = open_braces - close_braces
                fixed_str = json_str + '}' * missing
                fixes_attempted.append(f"添加 {missing} 个缺失的 '}}'")
                
                try:
                    result = json.loads(fixed_str)
                    self.logger.info(f"修复成功（{', '.join(fixes_attempted)}）")
                    return result
                except json.JSONDecodeError:
                    pass
            
            # 修复2: 移除末尾可能的多余字符
            json_str_stripped = json_str.rstrip()
            if json_str_stripped != json_str:
                fixes_attempted.append("移除末尾空白")
                try:
                    result = json.loads(json_str_stripped)
                    self.logger.info(f"修复成功（{', '.join(fixes_attempted)}）")
                    return result
                except json.JSONDecodeError:
                    pass
            
            # 修复3: 尝试找到最后一个有效的JSON结构
            for i in range(len(json_str) - 1, -1, -1):
                if json_str[i] == '}':
                    test_str = json_str[:i+1]
                    try:
                        result = json.loads(test_str)
                        fixes_attempted.append(f"截断到位置 {i+1}")
                        self.logger.info(f"修复成功（{', '.join(fixes_attempted)}）")
                        return result
                    except json.JSONDecodeError:
                        continue
            
            self.logger.warning(f"所有JSON修复尝试均失败: {fixes_attempted}")
            return None
            
        except Exception as e:
            self.logger.error(f"修复JSON时发生异常: {e}")
            return None
    
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