### 项目8: MCP服务器实现

#### 项目目标
- 实现MCP（模型通信协议）服务器
- 支持工具注册和发现
- 处理来自客户端的工具调用请求
- 提供可扩展的分布式工具架构

#### 核心代码实现

**1. MCP协议基础**

```python
# src/mcp/protocol.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json

@dataclass
class MCPRequest:
    """MCP请求"""
    id: Optional[int] = None
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)

@dataclass
class MCPResponse:
    """MCP响应"""
    id: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)

@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
```

**2. MCP服务器实现**

```python
# src/mcp/server.py
import asyncio
import json
import logging
from typing import Dict, Any, Callable, Awaitable, Optional

from .protocol import MCPRequest, MCPResponse, ToolInfo

class MCPServer:
    """MCP服务器基类"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.tools: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.tool_info: Dict[str, ToolInfo] = {}
        self.logger = logging.getLogger(f"mcp.server.{name}")
        
        # 注册内置方法
        self.register_tool("server/info", self._server_info, "获取服务器信息")
        self.register_tool("tools/list", self._list_tools, "列出可用工具")
        self.register_tool("tools/call", self._call_tool, "调用工具")
    
    def register_tool(self, name: str, func: Callable[..., Awaitable[Any]], 
                      description: str, input_schema: Optional[Dict] = None):
        """注册工具"""
        self.tools[name] = func
        self.tool_info[name] = ToolInfo(
            name=name,
            description=description,
            input_schema=input_schema or {}
        )
    
    async def _list_tools(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """列出工具"""
        return {
            'tools': [info.__dict__ for info in self.tool_info.values()]
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Any:
        """调用工具"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if not tool_name or tool_name not in self.tools:
            raise ValueError(f"未找到工具: {tool_name}")
        
        return await self.tools[tool_name](**arguments)
    
    async def _server_info(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """服务器信息"""
        return {
            'name': self.name,
            'version': self.version,
            'protocolVersion': '2024-11-05'
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理请求"""
        try:
            method = request.method
            params = request.params or {}
            
            if method in self.tools:
                result = await self.tools[method](params)
                return MCPResponse(id=request.id, result=result)
            else:
                error = {
                    'code': -32601,
                    'message': f'方法未找到: {method}'
                }
                return MCPResponse(id=request.id, error=error)
                
        except Exception as e:
            self.logger.error(f"请求处理错误: {e}")
            error = {
                'code': -32603,
                'message': f'内部错误: {str(e)}'
            }
            return MCPResponse(id=request.id, error=error)
    
    async def start_stdio_server(self):
        """启动标准输入输出服务器"""
        self.logger.info(f"启动MCP服务器: {self.name}")
        
        try:
            while True:
                # 从标准输入读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )
                
                if not line.strip():
                    continue
                
                try:
                    # 解析请求
                    request_data = json.loads(line)
                    request = MCPRequest(
                        id=request_data.get('id'),
                        method=request_data['method'],
                        params=request_data.get('params')
                    )
                    
                    # 处理请求
                    response = await self.handle_request(request)
                    
                    # 发送响应
                    print(response.to_json(), flush=True)
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析错误: {e}")
                except Exception as e:
                    self.logger.error(f"请求处理错误: {e}")
                    
        except KeyboardInterrupt:
             self.logger.info("服务器停止")
         except EOFError:
             self.logger.info("输入流结束，服务器停止")
```

**3. MCP客户端实现**

```python
# src/mcp/client.py
import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from .protocol import MCPRequest, MCPResponse, ToolInfo

class MCPClient:
    """MCP客户端实现"""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.tools: Dict[str, ToolInfo] = {}
        self.request_id = 0
    
    async def connect(self):
        """连接到MCP服务器"""
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # 获取服务器信息
        server_info = await self.call_method('server/info')
        print(f"连接到服务器: {server_info}")
        
        # 获取工具列表
        await self.refresh_tools()
    
    async def disconnect(self):
        """断开连接"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
    
    async def call_method(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """调用MCP方法"""
        if not self.process:
            raise RuntimeError("未连接到服务器")
        
        self.request_id += 1
        request = MCPRequest(
            id=self.request_id,
            method=method,
            params=params
        )
        
        # 发送请求
        request_json = request.to_json() + '\n'
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # 读取响应
        response_line = self.process.stdout.readline().strip()
        response_data = json.loads(response_line)
        
        response = MCPResponse(
            id=response_data.get('id'),
            result=response_data.get('result'),
            error=response_data.get('error')
        )
        
        if response.error:
            raise RuntimeError(f"MCP错误: {response.error}")
        
        return response.result
    
    async def refresh_tools(self):
        """刷新工具列表"""
        result = await self.call_method('tools/list')
        self.tools = {}
        
        for tool_data in result.get('tools', []):
            tool_info = ToolInfo(
                name=tool_data['name'],
                description=tool_data['description'],
                input_schema=tool_data['inputSchema']
            )
            self.tools[tool_info.name] = tool_info
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未知工具: {tool_name}")
        
        params = {
            'name': tool_name,
            'arguments': arguments
        }
        
        return await self.call_method('tools/call', params)
    
    def list_tools(self) -> List[ToolInfo]:
        """列出可用工具"""
        return list(self.tools.values())

# 使用示例
async def main():
    # 启动文件系统MCP服务器
    client = MCPClient(['python', '-m', 'mcp_servers.filesystem'])
    
    try:
        await client.connect()
        
        # 列出工具
        tools = client.list_tools()
        print("可用工具:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        # 调用工具
        result = await client.call_tool('read_file', {
            'path': '/path/to/file.txt'
        })
        print(f"文件内容: {result}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**4. 集成MCP的代理**

```python
# src/agents/mcp_agent.py
import asyncio
from typing import Dict, Any, List, Optional
from ..mcp.client import MCPClient
from ..agents.react_agent import ReActAgent

class MCPAgent(ReActAgent):
    """集成MCP协议的代理"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_servers = config.get('mcp_servers', [])
        
        # 初始化MCP客户端
        asyncio.create_task(self._initialize_mcp_clients())
    
    async def _initialize_mcp_clients(self):
        """初始化MCP客户端"""
        for server_config in self.mcp_servers:
            server_name = server_config['name']
            server_command = server_config['command']
            
            client = MCPClient(server_command)
            await client.connect()
            
            self.mcp_clients[server_name] = client
            
            # 注册MCP工具
            for tool in client.list_tools():
                tool_name = f"{server_name}_{tool.name}"
                self.tools[tool_name] = self._create_mcp_tool_wrapper(server_name, tool.name)
    
    def _create_mcp_tool_wrapper(self, server_name: str, tool_name: str):
        """创建MCP工具包装器"""
        async def mcp_tool_wrapper(**kwargs) -> Dict[str, Any]:
            try:
                client = self.mcp_clients[server_name]
                result = await client.call_tool(tool_name, kwargs)
                return {
                    "tool": f"{server_name}_{tool_name}",
                    "success": True,
                    "result": result
                }
            except Exception as e:
                return {
                    "tool": f"{server_name}_{tool_name}",
                    "success": False,
                    "error": str(e)
                }
        
        return mcp_tool_wrapper
    
    async def cleanup(self):
        """清理资源"""
        for client in self.mcp_clients.values():
            await client.disconnect()
```

#### 学习要点

1. **协议理解**：掌握MCP协议的消息格式和交互模式
2. **服务器开发**：实现工具注册、请求处理和响应生成
3. **客户端开发**：实现服务器连接、工具调用和错误处理
4. **分布式架构**：理解分布式工具系统的设计原则