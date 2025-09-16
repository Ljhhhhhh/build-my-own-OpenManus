### 项目 5：思考-行动循环

#### 目标

- 实现 ReAct 推理模式
- 设计状态机管理
- 学会循环控制和终止条件

#### 核心代码实现

```python
# agent/react_agent.py
from enum import Enum
from typing import List, Dict, Any, Optional
import asyncio
import json
import openai
from tools.manager import ToolManager
from dataclasses import dataclass

class AgentState(Enum):
    """代理状态"""
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    FINISHED = "finished"
    ERROR = "error"

@dataclass
class ReActStep:
    """ReAct步骤"""
    step_number: int
    thought: str
    action: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    state: AgentState = AgentState.THINKING

class ReActAgent:
    """ReAct推理代理"""

    def __init__(self, api_key: str, max_steps: int = 10):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.tool_manager = ToolManager()
        self.max_steps = max_steps
        self.current_step = 0
        self.steps: List[ReActStep] = []
        self.state = AgentState.THINKING

        # 注册工具（这里可以扩展）
        from tools.calculator import CalculatorTool
        from tools.weather import WeatherTool
        self.tool_manager.register_tool(CalculatorTool())

    def _get_react_prompt(self, user_query: str) -> str:
        """获取ReAct提示词"""
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tool_manager.list_tools()
        ])

        steps_history = ""
        for step in self.steps:
            steps_history += f"\nStep {step.step_number}:\n"
            steps_history += f"Thought: {step.thought}\n"
            if step.action:
                steps_history += f"Action: {json.dumps(step.action, ensure_ascii=False)}\n"
            if step.observation:
                steps_history += f"Observation: {step.observation}\n"

        return f"""
你是一个使用ReAct（Reasoning and Acting）模式的智能代理。

用户问题：{user_query}

可用工具：
{tools_info}

你需要按照以下格式进行推理和行动：

Thought: [你的思考过程]
Action: {{"name": "工具名称", "parameters": {{"参数名": "参数值"}}}}
Observation: [工具执行结果]

如果你认为已经获得了足够的信息来回答用户问题，请输出：
Thought: [最终思考]
Final Answer: [最终答案]

历史步骤：{steps_history}

请继续下一步：
        """

    async def solve(self, user_query: str) -> str:
        """解决用户问题"""
        self.current_step = 0
        self.steps = []
        self.state = AgentState.THINKING

        while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
            try:
                await self._execute_step(user_query)
            except Exception as e:
                self.state = AgentState.ERROR
                return f"执行过程中出错：{str(e)}"

        if self.state == AgentState.FINISHED:
            return self._get_final_answer()
        else:
            return "达到最大步数限制，未能完成任务"

    async def _execute_step(self, user_query: str):
        """执行一个ReAct步骤"""
        self.current_step += 1

        # 获取LLM响应
        prompt = self._get_react_prompt(user_query)
        response = await self._get_llm_response(prompt)

        # 解析响应
        step = self._parse_response(response)
        self.steps.append(step)

        # 根据步骤类型执行相应操作
        if "Final Answer" in response:
            self.state = AgentState.FINISHED
        elif step.action:
            # 执行工具调用
            self.state = AgentState.ACTING
            result = await self.tool_manager.execute_tool(
                step.action["name"],
                **step.action.get("parameters", {})
            )

            # 记录观察结果
            step.observation = str(result.content) if result.status.value == "success" else result.error_message
            step.state = AgentState.OBSERVING

            # 回到思考状态
            self.state = AgentState.THINKING

    def _parse_response(self, response: str) -> ReActStep:
        """解析LLM响应"""
        lines = response.strip().split('\n')
        thought = ""
        action = None

        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                try:
                    action_str = line[7:].strip()
                    action = json.loads(action_str)
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试简单解析
                    pass

        return ReActStep(
            step_number=self.current_step,
            thought=thought,
            action=action,
            state=self.state
        )

    async def _get_llm_response(self, prompt: str) -> str:
        """获取LLM响应"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM调用失败：{str(e)}")

    def _get_final_answer(self) -> str:
        """获取最终答案"""
        if self.steps:
            last_step = self.steps[-1]
            # 从最后一步的思考中提取最终答案
            # 这里可以进一步优化解析逻辑
            return last_step.thought
        return "未找到答案"

    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        return [
            {
                "step": step.step_number,
                "thought": step.thought,
                "action": step.action,
                "observation": step.observation,
                "state": step.state.value
            }
            for step in self.steps
        ]

# 使用示例
async def main():
    agent = ReActAgent(api_key="your-openai-api-key")

    print("ReAct代理已启动！")

    # 测试问题
    queries = [
        "计算 (15 + 25) * 3 的结果",
        "如果一个正方形的面积是 64，那么它的周长是多少？",
        "帮我计算复利：本金1000元，年利率5%，投资3年的最终金额"
    ]

    for query in queries:
        print(f"\n问题：{query}")
        print("=" * 50)

        answer = await agent.solve(query)
        print(f"答案：{answer}")

        print("\n执行轨迹：")
        for trace in agent.get_execution_trace():
            print(f"步骤 {trace['step']}: {trace['thought']}")
            if trace['action']:
                print(f"  行动: {trace['action']}")
            if trace['observation']:
                print(f"  观察: {trace['observation']}")

        print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **ReAct 模式**：思考-行动-观察的循环
2. **状态机**：管理代理的不同状态
3. **步骤追踪**：记录推理过程
4. **循环控制**：设置最大步数和终止条件

---

## 实践建议

### 1. 循序渐进

- 每个项目都要完全理解后再进入下一个
- 多写注释，理解每行代码的作用
- 遇到问题及时查阅文档和资料

### 2. 动手实践

- 不要只看代码，一定要亲自运行
- 尝试修改参数，观察不同的效果
- 添加日志输出，理解程序执行流程

### 3. 扩展练习

- 为每个项目添加新功能
- 尝试集成其他 API 和服务