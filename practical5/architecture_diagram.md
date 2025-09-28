# Practical5 项目架构图表

## 1. 整体系统架构图

```mermaid
graph TB
subgraph "用户交互层"
UI[用户界面<br/>main.py]
Demo[交互式演示<br/>ReActDemo]
end

subgraph "ReAct推理层"
Agent[ReAct代理<br/>ReActAgent]
State[状态管理<br/>AgentState]
Steps[步骤追踪<br/>ReActStep]
Loop[推理循环<br/>solve方法]
end

subgraph "工具管理层"
TM[工具管理器<br/>ToolManager]
TR[工具注册表]
TE[工具执行器]
end

subgraph "具体工具层"
CT[计算器工具<br/>CalculatorTool]
TPT[文本处理工具<br/>TextProcessorTool]
BT[基础工具抽象<br/>BaseTool]
end

subgraph "LLM服务层"
OpenAI[OpenAI API]
LLM[大语言模型]
Prompt[ReAct提示词工程]
end

subgraph "基础设施层"
Config[配置管理<br/>Config]
Logger[日志系统<br/>Logger]
Utils[工具函数]
end

UI --> Demo
Demo --> Agent
Agent --> State
Agent --> Steps
Agent --> Loop
Agent --> TM
Agent --> OpenAI

Loop --> State
Loop --> Steps
State --> Steps

TM --> TR
TM --> TE
TE --> CT
TE --> TPT
CT --> BT
TPT --> BT

OpenAI --> LLM
OpenAI --> Prompt

Agent --> Config
Agent --> Logger
TM --> Logger
CT --> Logger
TPT --> Logger

classDef userLayer fill:#e1f5fe
classDef reactLayer fill:#f3e5f5
classDef toolLayer fill:#e8f5e8
classDef llmLayer fill:#fff3e0
classDef infraLayer fill:#fce4ec

class UI,Demo userLayer
class Agent,State,Steps,Loop reactLayer
class TM,TR,TE,CT,TPT,BT toolLayer
class OpenAI,LLM,Prompt llmLayer
class Config,Logger,Utils infraLayer
```

## 2. ReAct 推理流程图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Demo as 演示程序
    participant Agent as ReAct代理
    participant State as 状态管理
    participant TM as 工具管理器
    participant Tool as 具体工具
    participant LLM as OpenAI API

    User->>Demo: 输入问题
    Demo->>Agent: solve(user_query)

    Agent->>Agent: _reset_state()
    Agent->>State: 初始化状态为THINKING

    loop ReAct推理循环 (最多max_steps次)
        Agent->>Agent: _execute_step()

        Note over Agent,LLM: 阶段1: 思考阶段 (Thought)
        Agent->>Agent: _get_react_prompt()
        Agent->>LLM: 发送ReAct格式提示词

        alt LLM调用成功
            LLM-->>Agent: 返回思考和行动计划
            Agent->>Agent: _parse_response()

            Note over Agent,Tool: 阶段2: 行动阶段 (Action)
            Agent->>State: 设置状态为ACTING
            Agent->>TM: execute_tool(tool_name, args)

            alt 工具执行成功
                TM->>Tool: execute(args)
                Tool-->>TM: ToolResult(成功)
                TM-->>Agent: 工具执行结果

                Note over Agent,State: 阶段3: 观察阶段 (Observation)
                Agent->>State: 设置状态为OBSERVING
                Agent->>Agent: 记录观察结果到步骤
                Agent->>State: 设置状态为THINKING

            else 工具执行失败
                TM-->>Agent: 错误信息
                Agent->>Agent: 记录错误到步骤
                Agent->>State: 设置状态为THINKING
            end

        else LLM调用失败
            Agent->>Agent: 记录LLM调用错误
            Note over Agent: 可选择重试或终止
        end

        opt 解析到最终答案
            Agent->>State: 设置状态为FINISHED
        end

        Agent->>Agent: 创建ReActStep记录
    end

    Note over Agent: 生成最终结果
    Agent->>Agent: _generate_final_result()
    Agent-->>Demo: 返回结果和执行轨迹
    Demo-->>User: 显示结果和推理过程

```

## 3. ReAct 状态机图

```mermaid
stateDiagram-v2
[*] --> THINKING: 开始推理

THINKING --> ACTING: 决定执行工具
THINKING --> FINISHED: 找到最终答案
THINKING --> ERROR: 发生错误

ACTING --> OBSERVING: 工具执行完成
ACTING --> ERROR: 工具执行失败

OBSERVING --> THINKING: 处理观察结果
OBSERVING --> ERROR: 结果处理失败

FINISHED --> [*]: 推理完成
ERROR --> [*]: 错误终止

note right of THINKING
分析问题
决定下一步行动
生成思考内容
end note

note right of ACTING
执行工具调用
获取工具结果
end note

note right of OBSERVING
处理工具输出
更新推理上下文
end note
```

## 4. 类关系图

```mermaid
classDiagram
class AgentState {
<<enumeration>>
THINKING
ACTING
OBSERVING
FINISHED
ERROR
}

class ReActStep {
+step_number: int
+thought: str
+action: Optional[Dict]
+observation: Optional[str]
+state: AgentState
+timestamp: float
+execution_time: Optional[float]
+to_dict() Dict
}

class ReActAgent {
-client: AsyncOpenAI
-model: str
-tool_manager: ToolManager
-state: AgentState
-steps: List[ReActStep]
-current_step: int
-max_steps: int
+solve(user_query: str) Dict
-_execute_step(user_query: str) None
-_get_react_prompt(user_query: str) str
-_parse_response(response: str) tuple
-_execute_tool(action: Dict) ToolResult
-_reset_state() None
+get_execution_trace() List[Dict]
}

class BaseTool {
<<abstract>>
+name: str
+description: str
+schema: dict
+execute(**kwargs) ToolResult*
+validate_input(**kwargs) Union[bool, str]
}

class ToolResult {
+status: ToolResultStatus
+content: Any
+error_message: Optional[str]
+execution_time: Optional[float]
+metadata: Optional[Dict]
+is_success: bool
+success(content, ...) ToolResult$
+error(error_message, ...) ToolResult$
}

class ToolResultStatus {
<<enumeration>>
SUCCESS
ERROR
TIMEOUT
INVALID_INPUT
}



class CalculatorTool {
+name: str
+description: str
+schema: dict
+validate_input(**kwargs) Union[bool, str]
+execute(**kwargs) ToolResult
}

class TextProcessorTool {
+name: str
+description: str
+schema: dict
+validate_input(**kwargs) Union[bool, str]
+execute(**kwargs) ToolResult
-_process_text(text: str, operation: str) str
}

class ToolManager {
-_tools: Dict[str, BaseTool]
-_execution_stats: Dict[str, Dict]
+register_tool(tool: BaseTool) bool
+unregister_tool(name: str) bool
+get_tool(name: str) Optional[BaseTool]
+execute_tool(name: str, **kwargs) ToolResult
+list_tools() List[Dict]
+get_stats() Dict
}

class Config {
+openai_api_key: str
+openai_model: str
+openai_base_url: str
+max_tokens: int
+temperature: float
+log_level: str
+tool_timeout: int
+from_env() Config$
+validate() None
+to_dict() Dict
}

ReActAgent --> AgentState
ReActAgent --> ReActStep
ReActAgent --> ToolManager
ReActAgent --> Config
ReActStep --> AgentState



ToolManager --> BaseTool
BaseTool <|-- CalculatorTool
BaseTool <|-- TextProcessorTool
BaseTool --> ToolResult
ToolResult --> ToolResultStatus
```

## 5. ReAct 推理数据流图

```mermaid
flowchart TD
subgraph "输入处理"
A[用户问题] --> B[初始化状态]
B --> C[重置推理步骤]
end

subgraph "ReAct循环核心"
C --> D[生成ReAct提示词]
D --> E[包含历史步骤上下文]
E --> F[发送到LLM]
F --> G{解析LLM响应}
end

subgraph "思考分支"
G -->|Thought| H[提取思考内容]
H --> I{是否有行动计划?}
end

subgraph "行动分支"
I -->|有Action| J[解析工具调用]
J --> K[验证工具参数]
K --> L[执行工具]
L --> M[收集观察结果]
M --> N[记录ReActStep]
end

subgraph "完成分支"
I -->|Final Answer| O[提取最终答案]
O --> P[设置FINISHED状态]
end

subgraph "循环控制"
N --> Q{达到最大步数?}
Q -->|否| D
Q -->|是| R[生成最终结果]
P --> R
end

subgraph "输出处理"

R --> S[包含执行轨迹]
S --> T[统计信息]
T --> U[返回给用户]
end

classDef inputStyle fill:#e3f2fd
classDef reactStyle fill:#f3e5f5
classDef thinkStyle fill:#e8f5e8
classDef actionStyle fill:#fff3e0
classDef outputStyle fill:#fce4ec

class A,B,C inputStyle
class D,E,F,G reactStyle
class H,I thinkStyle
class J,K,L,M,N actionStyle
class O,P,Q,R,S,T,U outputStyle
```

## 6. 提示词工程架构

```mermaid
graph TD
subgraph "ReAct提示词构建"
Base[基础角色定义] --> Tools[工具信息注入]
Tools --> Format[ReAct格式说明]
Format --> History[历史步骤上下文]
History --> Query[当前用户问题]
Query --> Final[最终提示词]
end

subgraph "提示词组件"
Role[角色：ReAct智能代理]
ToolList[可用工具列表和Schema]
Examples[ReAct格式示例]
Context[推理历史上下文]
Current[当前问题和指令]
end

subgraph "响应解析"
Response[LLM响应] --> Parser[正则表达式解析]
Parser --> Thought[提取Thought]
Parser --> Action[提取Action]
Parser --> Answer[提取Final Answer]
end

Base --> Role
Tools --> ToolList
Format --> Examples
History --> Context
Query --> Current

Final --> Response

classDef promptStyle fill:#e1f5fe
classDef componentStyle fill:#f3e5f5
classDef parseStyle fill:#e8f5e8

class Base,Tools,Format,History,Query,Final promptStyle
class Role,ToolList,Examples,Context,Current componentStyle
class Response,Parser,Thought,Action,Answer parseStyle
```

## 7. 项目文件结构

```mermaid
graph TD
Root[practical5/] --> Main[main.py]
Root --> Demo[demo.py]
Root --> Req[requirements.txt]
Root --> README[README.md]

Root --> Agent[agent/]
Agent --> AgentInit[__init__.py]
Agent --> ReactAgent[react_agent.py]

Root --> Tools[tools/]
Tools --> ToolsInit[__init__.py]
Tools --> Base[base.py]
Tools --> Manager[manager.py]
Tools --> Calc[calculator.py]
Tools --> Text[text_processor.py]

Root --> Utils[utils/]
Utils --> UtilsInit[__init__.py]
Utils --> Config[config.py]
Utils --> Logger[logger.py]

Root --> Tests[tests/]
Tests --> TestsInit[__init__.py]
Tests --> TestReact[test_react_agent.py]

Root --> Logs[logs/]
Logs --> MainLog[main.log]

classDef rootStyle fill:#e3f2fd
classDef moduleStyle fill:#f3e5f5
classDef fileStyle fill:#e8f5e8

class Root rootStyle
class Agent,Tools,Utils,Tests,Logs moduleStyle
class Main,Demo,Req,README,AgentInit,ReactAgent,ToolsInit,Base,Manager,Calc,Text,UtilsInit,Config,Logger,TestsInit,TestReact,MainLog fileStyle
```

## 架构特点总结

### 1. ReAct 模式核心特征

- **循环推理**: 实现了完整的"思考-行动-观察"循环
- **状态管理**: 清晰的状态机设计，追踪推理过程
- **步骤追踪**: 详细记录每个推理步骤，便于调试和分析
- **提示词工程**: 专门设计的 ReAct 格式提示词

### 2. 与项目 4 的主要差异

| 特性         | 项目 4 (ToolCallingAgent) | 项目 5 (ReActAgent) |
| ------------ | ------------------------- | ------------------- |
| **推理模式** | 单次工具调用              | 循环推理过程        |
| **状态管理** | 简单对话历史              | 复杂状态机          |
| **执行轨迹** | 基本统计信息              | 详细步骤记录        |
| **提示词**   | 工具调用格式              | ReAct 专用格式      |
| **错误处理** | 基础异常处理              | 状态感知恢复        |

### 3. 设计模式应用

- **状态机模式**: AgentState 枚举和状态转换逻辑
- **策略模式**: 不同状态下的不同处理策略
- **观察者模式**: 步骤追踪和日志记录
- **工厂模式**: ToolResult 的创建方法
- **模板方法模式**: ReAct 推理循环的固定流程

### 4. 技术亮点

- **异步编程**: 全面使用 async/await 提升性能
- **类型注解**: 完整的类型提示增强代码可读性
- **数据类**: 使用@dataclass 简化数据模型定义
- **枚举类型**: 类型安全的状态和结果状态定义
- **正则表达式**: 智能解析 LLM 的结构化响应

### 5. 可扩展性设计

- **模块化架构**: 清晰的层次分离，便于扩展
- **插件化工具**: 基于 BaseTool 的工具系统
- **配置驱动**: 灵活的配置管理系统
- **日志系统**: 完善的调试和监控支持

这个架构设计体现了 ReAct 推理模式的核心思想，为构建更智能、更可解释的 AI 代理系统提供了坚实的基础。相比项目 4 的简单工具调用，项目 5 实现了真正的循环推理能力，能够处理更复杂的多步骤问题。
