### 项目9: OpenManus简化版

#### 项目目标
- 构建完整的AI代理系统
- 集成所有前面学到的技术
- 实现类似OpenManus的核心功能
- 提供可扩展的架构设计

#### 核心代码实现

**1. 主代理系统**

```python
# src/agents/openmanus_agent.py
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..llm.openai_client import OpenAIClient
from ..tools.base import BaseTool, ToolResult
from ..tools.registry import ToolRegistry
from ..memory.conversation import ConversationMemory
from ..mcp.client import MCPClient
from ..sandbox.docker_sandbox import DockerSandbox

class OpenManusAgent:
    """OpenManus简化版代理"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("openmanus.agent")
        
        # 初始化组件
        self.llm_client = OpenAIClient(config['openai'])
        self.tool_registry = ToolRegistry()
        self.memory = ConversationMemory()
        self.sandbox = DockerSandbox(config.get('sandbox', {}))
        
        # MCP客户端
        self.mcp_clients: Dict[str, MCPClient] = {}
        
        # 执行状态
        self.execution_trace: List[Dict[str, Any]] = []
        self.current_step = 0
        self.max_steps = config.get('max_steps', 10)
        
        # 初始化工具
        self._initialize_tools()
    
    def _initialize_tools(self):
        """初始化内置工具"""
        from ..tools.file_tools import FileReadTool, FileWriteTool
        from ..tools.web_tools import WebSearchTool, WebScrapeTool
        from ..tools.code_tools import CodeExecuteTool
        
        # 注册内置工具
        self.tool_registry.register(FileReadTool())
        self.tool_registry.register(FileWriteTool())
        self.tool_registry.register(WebSearchTool(self.config.get('web_search', {})))
        self.tool_registry.register(WebScrapeTool())
        self.tool_registry.register(CodeExecuteTool(self.sandbox))
    
    async def initialize_mcp_servers(self, mcp_configs: List[Dict[str, Any]]):
        """初始化MCP服务器"""
        for mcp_config in mcp_configs:
            server_name = mcp_config['name']
            server_command = mcp_config['command']
            
            try:
                client = MCPClient(server_command)
                await client.connect()
                
                self.mcp_clients[server_name] = client
                
                # 注册MCP工具
                for tool in client.list_tools():
                    mcp_tool = MCPToolWrapper(client, tool, server_name)
                    self.tool_registry.register(mcp_tool)
                
                self.logger.info(f"已连接MCP服务器: {server_name}")
                
            except Exception as e:
                self.logger.error(f"连接MCP服务器失败 {server_name}: {e}")
    
    async def process_request(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        self.logger.info(f"处理用户请求: {user_input}")
        
        # 重置执行状态
        self.execution_trace = []
        self.current_step = 0
        
        # 添加到对话记忆
        self.memory.add_message("user", user_input)
        
        # 构建系统提示
        system_prompt = self._build_system_prompt()
        
        # 构建对话历史
        conversation_history = self.memory.get_recent_messages(10)
        
        try:
            # 开始ReAct循环
            final_answer = await self._react_loop(system_prompt, conversation_history, context)
            
            # 添加到对话记忆
            self.memory.add_message("assistant", final_answer)
            
            return {
                "success": True,
                "answer": final_answer,
                "execution_trace": self.execution_trace,
                "steps_used": self.current_step
            }
            
        except Exception as e:
            self.logger.error(f"请求处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_trace": self.execution_trace
            }
    
    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        available_tools = self.tool_registry.list_tools()
        tool_descriptions = []
        
        for tool in available_tools:
            tool_descriptions.append(
                f"- {tool.name}: {tool.description}\n"
                f"  参数: {tool.get_schema()}"
            )
        
        tools_text = "\n".join(tool_descriptions)
        
        return f"""
你是OpenManus AI代理，一个强大的AI助手，能够使用各种工具来帮助用户完成任务。

## 可用工具
{tools_text}

## 工作模式
你使用ReAct（Reasoning and Acting）模式工作：
1. **思考（Think）**: 分析当前情况，决定下一步行动
2. **行动（Act）**: 使用工具执行具体操作
3. **观察（Observe）**: 分析工具执行结果
4. **重复**: 直到完成任务或达到最大步数

## 响应格式
每一步都要包含：
- **思考**: 你的分析和计划
- **行动**: 要使用的工具和参数（如果需要）
- **观察**: 对结果的分析（在工具执行后）

## 重要规则
1. 始终先思考再行动
2. 一次只使用一个工具
3. 仔细分析工具执行结果
4. 如果遇到错误，尝试其他方法
5. 完成任务后给出最终答案

现在开始处理用户的请求。
"""
    
    async def _react_loop(self, system_prompt: str, conversation_history: List[Dict], 
                         context: Optional[Dict] = None) -> str:
        """ReAct循环执行"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加对话历史
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        while self.current_step < self.max_steps:
            self.current_step += 1
            
            # 获取LLM响应
            response = await self.llm_client.chat_completion(
                messages=messages,
                temperature=0.1
            )
            
            assistant_message = response.choices[0].message.content
            
            # 解析响应
            thought, action, tool_call = self._parse_response(assistant_message)
            
            # 记录执行轨迹
            trace_entry = {
                "step": self.current_step,
                "thought": thought,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
            
            # 如果没有工具调用，说明任务完成
            if not tool_call:
                trace_entry["final_answer"] = assistant_message
                self.execution_trace.append(trace_entry)
                return assistant_message
            
            # 执行工具
            try:
                tool_result = await self._execute_tool(tool_call)
                observation = f"工具执行结果: {tool_result.content}"
                
                if not tool_result.success:
                    observation += f"\n错误: {tool_result.error}"
                
            except Exception as e:
                observation = f"工具执行失败: {str(e)}"
            
            trace_entry["observation"] = observation
            self.execution_trace.append(trace_entry)
            
            # 添加到对话历史
            messages.append({"role": "assistant", "content": assistant_message})
            messages.append({"role": "user", "content": observation})
        
        return "抱歉，已达到最大执行步数，无法完成任务。"
    
    def _parse_response(self, response: str) -> tuple[str, str, Optional[Dict]]:
        """解析LLM响应"""
        # 简化的解析逻辑，实际应该更复杂
        lines = response.strip().split('\n')
        
        thought = ""
        action = ""
        tool_call = None
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("**思考") or line.startswith("思考:"):
                current_section = "thought"
                continue
            elif line.startswith("**行动") or line.startswith("行动:"):
                current_section = "action"
                continue
            elif line.startswith("**观察") or line.startswith("观察:"):
                current_section = "observation"
                continue
            
            if current_section == "thought":
                thought += line + "\n"
            elif current_section == "action":
                action += line + "\n"
                
                # 尝试解析工具调用
                if "工具:" in line or "tool:" in line.lower():
                    tool_call = self._extract_tool_call(action)
        
        return thought.strip(), action.strip(), tool_call
    
    def _extract_tool_call(self, action_text: str) -> Optional[Dict]:
        """从行动文本中提取工具调用"""
        # 简化的工具调用提取逻辑
        # 实际实现应该更加健壮
        import re
        
        # 查找工具名称
        tool_match = re.search(r'工具[：:]\s*(\w+)', action_text)
        if not tool_match:
            return None
        
        tool_name = tool_match.group(1)
        
        # 查找参数（简化版）
        params = {}
        param_matches = re.findall(r'(\w+)[：:]\s*([^\n]+)', action_text)
        
        for key, value in param_matches:
            if key != '工具' and key != 'tool':
                params[key] = value.strip()
        
        return {
            "tool_name": tool_name,
            "parameters": params
        }
    
    async def _execute_tool(self, tool_call: Dict) -> ToolResult:
        """执行工具调用"""
        tool_name = tool_call["tool_name"]
        parameters = tool_call["parameters"]
        
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                content="",
                error=f"未找到工具: {tool_name}"
            )
        
        return await tool.execute(**parameters)
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        return self.execution_trace
    
    async def cleanup(self):
        """清理资源"""
        # 断开MCP连接
        for client in self.mcp_clients.values():
            await client.disconnect()
        
        # 清理沙箱
        if self.sandbox:
            # 这里应该有沙箱清理逻辑
            pass


class MCPToolWrapper(BaseTool):
    """MCP工具包装器"""
    
    def __init__(self, client: MCPClient, tool_info, server_name: str):
        self.client = client
        self.tool_info = tool_info
        self.server_name = server_name
        
        super().__init__(
            name=f"{server_name}_{tool_info.name}",
            description=f"[{server_name}] {tool_info.description}"
        )
    
    async def _execute(self, **kwargs) -> ToolResult:
        try:
            result = await self.client.call_tool(self.tool_info.name, kwargs)
            return ToolResult(
                success=True,
                content=str(result)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return self.tool_info.input_schema
```

**2. 主程序入口**

```python
# main.py
import asyncio
import json
import logging
from typing import Dict, Any

from src.agents.openmanus_agent import OpenManusAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """主程序"""
    
    # 加载配置
    config = {
        "openai": {
            "api_key": "your-openai-api-key",
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1"
        },
        "sandbox": {
            "timeout": 30,
            "memory_limit": 512,
            "cpu_limit": 1.0
        },
        "web_search": {
            "api_key": "your-search-api-key"
        },
        "max_steps": 15
    }
    
    # MCP服务器配置
    mcp_configs = [
        {
            "name": "filesystem",
            "command": ["python", "-m", "mcp_servers.filesystem"]
        },
        {
            "name": "browser",
            "command": ["python", "-m", "mcp_servers.browser"]
        }
    ]
    
    # 创建代理
    agent = OpenManusAgent(config)
    
    try:
        # 初始化MCP服务器
        await agent.initialize_mcp_servers(mcp_configs)
        
        print("OpenManus AI代理已启动！")
        print("输入 'quit' 或 'exit' 退出")
        print("-" * 50)
        
        # 交互循环
        while True:
            try:
                user_input = input("\n用户: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    break
                
                if not user_input:
                    continue
                
                print("\n代理正在处理...")
                
                # 处理请求
                result = await agent.process_request(user_input)
                
                if result["success"]:
                    print(f"\n代理: {result['answer']}")
                    print(f"\n执行步数: {result['steps_used']}")
                    
                    # 可选：显示执行轨迹
                    show_trace = input("\n是否显示执行轨迹？(y/n): ").lower() == 'y'
                    if show_trace:
                        print("\n=== 执行轨迹 ===")
                        for trace in result['execution_trace']:
                            print(f"\n步骤 {trace['step']}:")
                            print(f"思考: {trace['thought']}")
                            if 'action' in trace:
                                print(f"行动: {trace['action']}")
                            if 'observation' in trace:
                                print(f"观察: {trace['observation']}")
                else:
                    print(f"\n错误: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n\n用户中断，正在退出...")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
        
    finally:
        # 清理资源
        await agent.cleanup()
        print("\n再见！")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **系统集成**：将所有组件整合成完整的AI代理系统
2. **架构设计**：模块化、可扩展的系统架构
3. **错误处理**：完善的异常处理和资源清理
4. **用户体验**：友好的交互界面和反馈机制
5. **性能优化**：异步处理和资源管理