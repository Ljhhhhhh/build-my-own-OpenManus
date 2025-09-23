# Practical4 项目架构图表

## 1. 整体系统架构图

```mermaid
graph TB
    subgraph "用户交互层"
        UI[用户界面<br/>main.py]
        Demo[演示程序<br/>ToolCallingDemo]
    end

    subgraph "核心代理层"
        Agent[工具调用代理<br/>ToolCallingAgent]
        History[对话历史管理]
        Stats[统计信息]
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
    end

    subgraph "基础设施层"
        Config[配置管理<br/>Config]
        Logger[日志系统<br/>Logger]
        Utils[工具函数]
    end

    UI --> Demo
    Demo --> Agent
    Agent --> History
    Agent --> Stats
    Agent --> TM
    Agent --> OpenAI

    TM --> TR
    TM --> TE
    TE --> CT
    TE --> TPT
    CT --> BT
    TPT --> BT

    OpenAI --> LLM

    Agent --> Config
    Agent --> Logger
    TM --> Logger
    CT --> Logger
    TPT --> Logger

    classDef userLayer fill:#e1f5fe
    classDef coreLayer fill:#f3e5f5
    classDef toolLayer fill:#e8f5e8
    classDef llmLayer fill:#fff3e0
    classDef infraLayer fill:#fce4ec

    class UI,Demo userLayer
    class Agent,History,Stats coreLayer
    class TM,TR,TE,CT,TPT,BT toolLayer
    class OpenAI,LLM llmLayer
    class Config,Logger,Utils infraLayer
```

## 2. 工具调用流程图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Demo as 演示程序
    participant Agent as 工具调用代理
    participant TM as 工具管理器
    participant Tool as 具体工具
    participant LLM as OpenAI API

    User->>Demo: 输入问题
    Demo->>Agent: process_request(user_input)

    Agent->>Agent: 添加到对话历史
    Agent->>Agent: 准备系统提示词
    Agent->>Agent: 获取工具schema

    Agent->>LLM: 发送请求(消息+工具schema)
    LLM-->>Agent: 返回响应(可能包含工具调用)

    alt 包含工具调用
        Agent->>TM: execute_tool(tool_name, args)
        TM->>Tool: execute(args)
        Tool-->>TM: ToolResult
        TM-->>Agent: 工具执行结果

        Agent->>Agent: 添加工具结果到历史
        Agent->>LLM: 再次请求最终回复
        LLM-->>Agent: 最终回复
    end

    Agent-->>Demo: 返回最终回复
    Demo-->>User: 显示结果
```

## 3. 类关系图

```mermaid
classDiagram
    class BaseTool {
        <<abstract>>
        +schema: dict
        +execute(args: dict) ToolResult*
    }

    class ToolResult {
        +status: ToolResultStatus
        +content: str
        +metadata: dict
        +error: str
        +create_success(content, metadata) ToolResult$
        +create_error(error, metadata) ToolResult$
    }

    class ToolResultStatus {
        <<enumeration>>
        SUCCESS
        ERROR
        TIMEOUT
    }

    class CalculatorTool {
        +name: str
        +description: str
        +schema: dict
        +validate_input(args: dict) bool
        +execute(args: dict) ToolResult
    }

    class TextProcessorTool {
        +name: str
        +description: str
        +schema: dict
        +validate_input(args: dict) bool
        +execute(args: dict) ToolResult
        -_process_text(text: str, operation: str) str
    }

    class ToolManager {
        -tools: dict
        -stats: dict
        +register_tool(tool: BaseTool) bool
        +unregister_tool(name: str) bool
        +get_tool(name: str) BaseTool
        +execute_tool(name: str, args: dict) ToolResult
        +get_tools_schema() list
        +get_stats() dict
    }

    class ToolCallingAgent {
        -client: OpenAI
        -model: str
        -tool_manager: ToolManager
        -conversation_history: list
        -stats: dict
        +register_tool(tool: BaseTool) bool
        +process_request(user_input: str) str
        -_handle_tool_calls(response) str
        -_get_system_prompt() str
        +clear_history() void
        +get_stats() dict
    }

    class Config {
        +openai_api_key: str
        +openai_model: str
        +openai_base_url: str
        +max_tokens: int
        +temperature: float
        +from_env() Config$
        +validate() bool
        +to_dict() dict
    }

    class LoggerMixin {
        +logger: Logger
    }

    BaseTool <|-- CalculatorTool
    BaseTool <|-- TextProcessorTool
    BaseTool --> ToolResult
    ToolResult --> ToolResultStatus

    ToolManager --> BaseTool
    ToolCallingAgent --> ToolManager
    ToolCallingAgent --> Config

    CalculatorTool --|> LoggerMixin
    TextProcessorTool --|> LoggerMixin
    ToolManager --|> LoggerMixin
    ToolCallingAgent --|> LoggerMixin
```

## 4. 数据流图

```mermaid
flowchart TD
    subgraph "输入处理"
        A[用户输入] --> B[输入验证]
        B --> C[添加到对话历史]
    end

    subgraph "LLM处理"
        C --> D[构建系统提示词]
        D --> E[获取工具Schema]
        E --> F[发送到OpenAI API]
        F --> G{是否包含工具调用?}
    end

    subgraph "工具调用处理"
        G -->|是| H[解析工具调用]
        H --> I[验证工具参数]
        I --> J[执行工具]
        J --> K[收集工具结果]
        K --> L[添加结果到历史]
        L --> M[再次调用LLM]
        M --> N[获取最终回复]
    end

    subgraph "直接回复"
        G -->|否| O[直接返回LLM回复]
    end

    subgraph "输出处理"
        N --> P[格式化输出]
        O --> P
        P --> Q[更新统计信息]
        Q --> R[返回给用户]
    end

    classDef inputStyle fill:#e3f2fd
    classDef llmStyle fill:#f3e5f5
    classDef toolStyle fill:#e8f5e8
    classDef outputStyle fill:#fff3e0

    class A,B,C inputStyle
    class D,E,F,G llmStyle
    class H,I,J,K,L,M,N toolStyle
    class O,P,Q,R outputStyle
```

## 5. 配置和日志系统架构

```mermaid
graph LR
    subgraph "配置系统"
        ENV[环境变量] --> Config[Config类]
        DOTENV[.env文件] --> Config
        Config --> Validation[配置验证]
        Validation --> App[应用程序]
    end

    subgraph "日志系统"
        Logger[Logger配置] --> Console[控制台输出]
        Logger --> File[文件输出]
        Logger --> Rotation[日志轮转]

        Mixin[LoggerMixin] --> Classes[各个类]
        Decorator[日志装饰器] --> Functions[函数调用]
    end

    App --> Logger

    classDef configStyle fill:#e1f5fe
    classDef logStyle fill:#f3e5f5

    class ENV,DOTENV,Config,Validation,App configStyle
    class Logger,Console,File,Rotation,Mixin,Classes,Decorator,Functions logStyle
```

## 6. 项目文件结构

```mermaid
graph TD
    Root[practical4/] --> Main[main.py]
    Root --> Req[requirements.txt]
    Root --> README[README.md]

    Root --> Agent[agent/]
    Agent --> AgentInit[__init__.py]
    Agent --> ToolAgent[tool_calling_agent.py]

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

    Root --> Logs[logs/]
    Logs --> DemoLog[demo.log]
    Logs --> AppLog[practical4.log]

    classDef rootStyle fill:#e3f2fd
    classDef moduleStyle fill:#f3e5f5
    classDef fileStyle fill:#e8f5e8

    class Root rootStyle
    class Agent,Tools,Utils,Logs moduleStyle
    class Main,Req,README,AgentInit,ToolAgent,ToolsInit,Base,Manager,Calc,Text,UtilsInit,Config,Logger,DemoLog,AppLog fileStyle
```

## 架构特点总结

### 1. 分层架构

- **用户交互层**: 处理用户输入和输出展示
- **核心代理层**: 管理对话流程和 LLM 交互
- **工具管理层**: 统一管理和调度各种工具
- **具体工具层**: 实现具体的功能工具
- **基础设施层**: 提供配置、日志等支撑服务

### 2. 设计模式应用

- **抽象工厂模式**: BaseTool 抽象基类
- **策略模式**: 不同工具的不同执行策略
- **单例模式**: Config 配置管理
- **装饰器模式**: 日志装饰器
- **混入模式**: LoggerMixin 提供日志功能

### 3. 异步编程

- 全面使用 async/await 处理异步操作
- 支持并发工具调用
- 非阻塞的用户交互

### 4. 错误处理和日志

- 完善的异常处理机制
- 分级日志记录
- 统计信息收集

这个架构设计体现了现代 Python 应用的最佳实践，为构建可扩展的 AI 代理系统提供了良好的基础。
