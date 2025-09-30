"""
简化版 ReAct 代理 - 用于学习核心概念

这是一个精简的 ReAct 实现，专注于核心概念的理解。
剥离了所有复杂的错误处理、日志、状态管理等，只保留最本质的逻辑。

核心概念：
1. ReAct = Reasoning (思考) + Acting (行动)
2. 循环模式：Think → Act → Observe → Think → ...
3. 提示词工程：告诉 LLM 如何按格式输出
4. 响应解析：从文本中提取结构化信息
5. 工具执行：将 LLM 的意图转化为实际行动
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from openai import AsyncOpenAI


class SimpleReActAgent:
    """
    简化版 ReAct 代理
    
    核心思想：
    让 LLM 在解决问题时，不是一次性给出答案，而是：
    1. 思考（Thought）：分析当前情况，决定下一步做什么
    2. 行动（Action）：调用工具获取信息
    3. 观察（Observation）：查看工具返回的结果
    4. 重复上述过程，直到找到答案
    
    类比：就像你做数学题时的过程
    - 思考："我需要先算出 x 的值"
    - 行动：用计算器算 x = 10
    - 观察：看到结果是 10
    - 思考："现在我可以算 y = x + 5"
    - 行动：用计算器算 10 + 5
    - 观察：看到结果是 15
    - 思考："答案就是 15"
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        tools: List[Any],
        model: str = "gpt-3.5-turbo",
        max_steps: int = 5
    ):
        """
        初始化简化版 ReAct 代理
        
        Args:
            api_key: OpenAI API 密钥
            base_url: API 基础URL
            tools: 可用的工具列表
            model: 使用的模型
            max_steps: 最大思考步数（防止无限循环）
        """
        # 1️⃣ 核心组件：LLM 客户端
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        
        # 2️⃣ 核心组件：工具系统
        self.tools = {tool.name: tool for tool in tools}
        
        # 3️⃣ 核心配置：防止无限循环
        self.max_steps = max_steps
        
        # 4️⃣ 历史记录：供 LLM 查看之前的思考过程
        self.history: List[Dict[str, str]] = []
    
    async def solve(self, question: str) -> str:
        """
        解决用户问题的主函数
        
        这是整个 ReAct 循环的入口，核心流程：
        
        ┌─────────────────────────────────────────┐
        │  while 还没找到答案 and 步数 < 最大步数  │
        │      ↓                                   │
        │  1. 调用 LLM 思考                        │
        │      ↓                                   │
        │  2. 解析 LLM 的输出                      │
        │      ↓                                   │
        │  3. 如果是 Final Answer → 返回答案       │
        │     如果是 Action → 执行工具 → 继续循环  │
        └─────────────────────────────────────────┘
        
        Args:
            question: 用户问题
            
        Returns:
            str: 最终答案
        """
        print(f"\n{'='*60}")
        print(f"🤔 开始思考问题: {question}")
        print(f"{'='*60}\n")
        
        # 重置历史记录
        self.history = []
        
        # 主循环：重复 Think-Act-Observe 直到找到答案
        for step in range(1, self.max_steps + 1):
            print(f"\n📍 第 {step} 步推理")
            print(f"{'-'*60}")
            
            # ===== 步骤1: 调用 LLM 获取思考和行动 =====
            llm_response = await self._call_llm(question)
            
            # ===== 步骤2: 解析 LLM 的响应 =====
            thought, action, final_answer = self._parse_llm_response(llm_response)
            
            # 打印思考过程
            print(f"💭 Thought: {thought}")
            
            # ===== 步骤3: 判断是否完成 =====
            if final_answer:
                # 找到最终答案，结束循环
                print(f"✅ Final Answer: {final_answer}\n")
                return final_answer
            
            elif action:
                # 需要执行工具
                print(f"🔧 Action: {action}")
                
                # 执行工具
                observation = await self._execute_action(action)
                print(f"👀 Observation: {observation}")
                
                # 保存到历史记录（供下一轮 LLM 参考）
                self.history.append({
                    "thought": thought,
                    "action": json.dumps(action, ensure_ascii=False),
                    "observation": observation
                })
            
            else:
                # 既没有答案，也没有行动（异常情况）
                print(f"⚠️  LLM 输出格式错误，没有给出 Action 或 Final Answer")
                break
        
        # 达到最大步数还没找到答案
        return f"抱歉，在 {self.max_steps} 步内没有找到答案"
    
    async def _call_llm(self, question: str) -> str:
        """
        调用 LLM 进行思考
        
        关键点：通过精心设计的提示词（prompt），告诉 LLM：
        1. 你是一个使用 ReAct 模式的代理
        2. 你有哪些工具可以使用
        3. 你之前的思考历史是什么
        4. 你需要按照特定格式输出（Thought + Action 或 Final Answer）
        
        Args:
            question: 用户问题
            
        Returns:
            str: LLM 的原始文本响应
        """
        # 构建提示词
        prompt = self._build_prompt(question)
        
        # 调用 LLM（这是整个系统中唯一的"智能"来源）
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # 低温度 = 更确定性的输出
        )
        
        return response.choices[0].message.content.strip()
    
    def _build_prompt(self, question: str) -> str:
        """
        构建 ReAct 提示词
        
        这是 ReAct 的核心：通过提示词工程，让 LLM 学会：
        1. 逐步思考问题
        2. 主动使用工具
        3. 根据工具结果继续推理
        
        提示词结构：
        ┌────────────────────────────┐
        │ 1. 角色定义（你是谁）      │
        │ 2. 用户问题                │
        │ 3. 可用工具列表            │
        │ 4. 输出格式要求            │
        │ 5. 历史思考记录            │
        │ 6. 引导下一步思考          │
        └────────────────────────────┘
        
        Args:
            question: 用户问题
            
        Returns:
            str: 完整的提示词
        """
        # 1. 工具信息（告诉 LLM 有哪些工具可用）
        tools_desc = self._format_tools_description()
        
        # 2. 历史记录（告诉 LLM 之前发生了什么）
        history_desc = self._format_history()
        
        # 3. 组装完整提示词
        prompt = f"""你是一个使用 ReAct（Reasoning and Acting）模式的智能代理。

用户问题：{question}

可用工具：
{tools_desc}

你的输出格式必须是以下两种之一：

格式1 - 需要使用工具时：
Thought: [你的思考过程，分析当前情况，决定使用什么工具]
Action: {{"name": "工具名", "parameters": {{"参数名": "参数值"}}}}

格式2 - 找到最终答案时：
Thought: [你的最终思考]
Final Answer: [最终答案]

重要规则：
1. 每次只输出一个 Thought 和一个 Action（或 Final Answer）
2. Action 必须是有效的 JSON 格式
3. 只能使用上面列出的工具
4. 仔细分析工具返回的结果

历史记录：
{history_desc}

请继续下一步推理："""
        
        return prompt
    
    def _format_tools_description(self) -> str:
        """
        格式化工具描述
        
        将工具列表转换为 LLM 可以理解的文本描述
        
        Returns:
            str: 工具描述文本
        """
        if not self.tools:
            return "暂无可用工具"
        
        descriptions = []
        for name, tool in self.tools.items():
            # 获取工具的基本信息
            desc = f"- {name}: {tool.description}"
            
            # 添加参数说明
            schema = tool.schema
            if 'properties' in schema:
                params = []
                required = schema.get('required', [])
                
                for param_name, param_info in schema['properties'].items():
                    param_type = param_info.get('type', 'any')
                    param_desc = param_info.get('description', '')
                    is_required = param_name in required
                    
                    req_mark = "[必需]" if is_required else "[可选]"
                    params.append(f"{param_name}{req_mark}({param_type}): {param_desc}")
                
                if params:
                    desc += f"\n  参数: {', '.join(params)}"
            
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def _format_history(self) -> str:
        """
        格式化历史记录
        
        将之前的思考-行动-观察转换为文本，让 LLM 了解上下文
        
        Returns:
            str: 历史记录文本
        """
        if not self.history:
            return "暂无历史记录（这是第一步）"
        
        formatted = []
        for i, record in enumerate(self.history, 1):
            formatted.append(f"步骤 {i}:")
            formatted.append(f"  Thought: {record['thought']}")
            formatted.append(f"  Action: {record['action']}")
            formatted.append(f"  Observation: {record['observation']}")
            formatted.append("")  # 空行分隔
        
        return "\n".join(formatted)
    
    def _parse_llm_response(self, response: str) -> Tuple[str, Optional[Dict], Optional[str]]:
        """
        解析 LLM 的响应
        
        LLM 返回的是纯文本，我们需要从中提取结构化信息：
        1. Thought（思考内容）
        2. Action（要执行的动作）或 Final Answer（最终答案）
        
        示例输入：
        "Thought: 我需要计算 5+3
         Action: {"name": "calculator", "parameters": {"operation": "add", "a": 5, "b": 3}}"
        
        示例输出：
        ("我需要计算 5+3", {"name": "calculator", ...}, None)
        
        Args:
            response: LLM 的原始文本响应
            
        Returns:
            tuple: (思考内容, 行动字典或None, 最终答案或None)
        """
        thought = ""
        action = None
        final_answer = None
        
        try:
            # 1️⃣ 提取 Thought（几乎总是有）
            thought_match = re.search(
                r'Thought:\s*(.*?)(?=\n(?:Action|Final Answer):|$)',
                response,
                re.DOTALL
            )
            if thought_match:
                thought = thought_match.group(1).strip()
            
            # 2️⃣ 检查是否有 Final Answer
            final_answer_match = re.search(
                r'Final Answer:\s*(.*?)$',
                response,
                re.DOTALL
            )
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                return thought, None, final_answer  # 有答案就直接返回
            
            # 3️⃣ 提取 Action（JSON格式）
            action_match = re.search(r'Action:\s*(\{.*\})', response, re.DOTALL)
            if action_match:
                action_str = action_match.group(1).strip()
                # 清理多余空白
                action_str = re.sub(r'\s+', ' ', action_str)
                # 解析 JSON
                action = json.loads(action_str)
            
            return thought, action, final_answer
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 解析失败: {e}")
            return thought, None, None
        except Exception as e:
            print(f"⚠️  解析响应时出错: {e}")
            return f"解析错误: {e}", None, None
    
    async def _execute_action(self, action: Dict[str, Any]) -> str:
        """
        执行工具调用
        
        将 LLM 的"意图"转化为实际的"行动"
        
        流程：
        1. 从 action 字典中提取工具名和参数
        2. 找到对应的工具实例
        3. 调用工具的 execute 方法
        4. 格式化返回结果
        
        Args:
            action: 动作字典，格式：{"name": "工具名", "parameters": {...}}
            
        Returns:
            str: 格式化的工具执行结果
        """
        try:
            tool_name = action.get('name')
            parameters = action.get('parameters', {})
            
            # 查找工具
            if tool_name not in self.tools:
                return f"错误：工具 '{tool_name}' 不存在"
            
            tool = self.tools[tool_name]
            
            # 执行工具
            result = await tool.execute(**parameters)
            
            # 格式化结果
            if result.is_success:
                if isinstance(result.content, dict):
                    return json.dumps(result.content, ensure_ascii=False)
                else:
                    return str(result.content)
            else:
                return f"工具执行失败: {result.error_message}"
        
        except Exception as e:
            return f"执行工具时出错: {e}"


# ============================================================================
# 使用示例
# ============================================================================

async def demo():
    """
    演示如何使用简化版 ReAct 代理
    """
    from tools.calculator import CalculatorTool
    from tools.text_processor import TextProcessorTool
    from utils.config import get_config
    
    # 1. 准备工具
    tools = [
        CalculatorTool(),
        TextProcessorTool()
    ]
    
    # 2. 获取配置
    config = get_config()
    
    # 3. 创建代理
    agent = SimpleReActAgent(
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
        tools=tools,
        max_steps=5
    )
    
    # 4. 解决问题
    question = "计算 (15 + 25) × 2 的结果"
    answer = await agent.solve(question)
    
    print(f"\n{'='*60}")
    print(f"最终答案: {answer}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
