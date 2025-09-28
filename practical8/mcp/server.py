"""
MCP服务器核心实现

这个模块实现了MCP服务器的核心功能，包括：
- 工具注册和管理
- 请求处理和响应生成
- 标准输入输出通信
- 错误处理和日志记录

对于JavaScript开发者的说明：
- 这里使用了Python的asyncio，类似于Node.js的异步编程模型
- sys.stdin/stdout用于进程间通信，类似于Node.js的process.stdin/stdout
- ABC (Abstract Base Class) 类似于TypeScript的abstract class
"""

import asyncio
import sys
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import asdict

from .protocol import (
    MCPRequest, MCPResponse, ToolInfo, MCPMethod, MCPError,
    create_initialize_request
)
from utils.logger import get_logger
from utils.config import get_config


class MCPTool(ABC):
    """
    MCP工具的抽象基类
    
    所有MCP工具都必须继承这个类并实现相应的方法
    
    类似于TypeScript中的:
    abstract class MCPTool {
        abstract get_info(): ToolInfo;
        abstract async execute(arguments: Record<string, any>): Promise<any>;
    }
    """
    
    @abstractmethod
    def get_info(self) -> ToolInfo:
        """
        获取工具信息
        
        Returns:
            ToolInfo: 工具的详细信息，包括名称、描述和参数
        """
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        Args:
            arguments: 工具参数
            
        Returns:
            Any: 工具执行结果
        """
        pass


class MCPServer:
    """
    MCP服务器主类
    
    负责处理客户端请求，管理工具注册，以及维护服务器状态
    
    类似于JavaScript中的:
    class MCPServer {
        private tools: Map<string, MCPTool> = new Map();
        private running: boolean = false;
        
        constructor() {
            this.logger = getLogger("mcp-server");
        }
    }
    """
    
    def __init__(self, name: str = "MCP-Server"):
        """
        初始化MCP服务器
        
        Args:
            name: 服务器名称
        """
        self.name = name
        self.tools: Dict[str, MCPTool] = {}  # 工具注册表
        self.running = False
        self.logger = get_logger("mcp-server")
        self.config = get_config()
        
        # 服务器信息
        self.server_info = {
            "name": name,
            "version": "1.0.0",
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            }
        }
        
        self.logger.info(f"MCP Server '{name}' initialized")
    
    def register_tool(self, tool: MCPTool) -> None:
        """
        注册工具
        
        Args:
            tool: 要注册的工具实例
        
        类似于JavaScript中的:
        registerTool(tool: MCPTool): void {
            const toolInfo = tool.getInfo();
            this.tools.set(toolInfo.name, tool);
            this.logger.info(`Tool registered: ${toolInfo.name}`);
        }
        """
        tool_info = tool.get_info()
        self.tools[tool_info.name] = tool
        self.logger.info(f"Tool registered: {tool_info.name}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否成功注销
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(f"Tool unregistered: {tool_name}")
            return True
        return False
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """
        获取所有已注册工具的信息
        
        Returns:
            List[Dict]: 工具信息列表
        
        类似于JavaScript中的:
        getToolsInfo(): ToolInfo[] {
            return Array.from(this.tools.values()).map(tool => tool.getInfo());
        }
        """
        return [tool.get_info().to_dict() for tool in self.tools.values()]
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        处理客户端请求
        
        这是服务器的核心方法，根据请求类型分发到相应的处理函数
        
        Args:
            request: 客户端请求
            
        Returns:
            MCPResponse: 服务器响应
        
        类似于JavaScript中的:
        async handleRequest(request: MCPRequest): Promise<MCPResponse> {
            try {
                switch (request.method) {
                    case "initialize":
                        return await this.handleInitialize(request);
                    case "tools/list":
                        return await this.handleListTools(request);
                    case "tools/call":
                        return await this.handleCallTool(request);
                    default:
                        return MCPResponse.error(request.id, -32601, "Method not found");
                }
            } catch (error) {
                return MCPResponse.error(request.id, -32603, "Internal error");
            }
        }
        """
        try:
            self.logger.debug(f"Handling request: {request.method}", method=request.method, id=request.id)
            
            # 根据方法类型分发请求
            if request.method == MCPMethod.INITIALIZE.value:
                return await self._handle_initialize(request)
            elif request.method == MCPMethod.LIST_TOOLS.value:
                return await self._handle_list_tools(request)
            elif request.method == MCPMethod.CALL_TOOL.value:
                return await self._handle_call_tool(request)
            elif request.method == MCPMethod.PING.value:
                return await self._handle_ping(request)
            else:
                return MCPResponse.error(
                    request.id,
                    MCPError.METHOD_NOT_FOUND,
                    f"Method not found: {request.method}"
                )
        
        except Exception as e:
            self.logger.error(f"Error handling request: {e}", error=str(e), request_id=request.id)
            return MCPResponse.error(
                request.id,
                MCPError.INTERNAL_ERROR,
                f"Internal server error: {str(e)}"
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """
        处理初始化请求
        
        Args:
            request: 初始化请求
            
        Returns:
            MCPResponse: 初始化响应
        """
        self.logger.info("Handling initialize request")
        
        # 返回服务器信息（确保所有值都是可序列化的）
        server_info = {
            "name": self.server_info["name"],
            "version": self.server_info["version"],
            "protocolVersion": self.server_info["protocolVersion"],
            "capabilities": self.server_info["capabilities"]
        }
        
        return MCPResponse.success(request.id, server_info)
    
    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """
        处理获取工具列表请求
        
        Args:
            request: 工具列表请求
            
        Returns:
            MCPResponse: 包含工具列表的响应
        """
        self.logger.info("Handling list tools request")
        
        tools_info = self.get_tools_info()
        return MCPResponse.success(request.id, {"tools": tools_info})
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """
        处理工具调用请求
        
        Args:
            request: 工具调用请求
            
        Returns:
            MCPResponse: 工具执行结果响应
        """
        if not request.params:
            return MCPResponse.error(
                request.id,
                MCPError.INVALID_PARAMS,
                "Missing parameters for tool call"
            )
        
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if not tool_name:
            return MCPResponse.error(
                request.id,
                MCPError.INVALID_PARAMS,
                "Missing tool name"
            )
        
        if tool_name not in self.tools:
            return MCPResponse.error(
                request.id,
                MCPError.TOOL_NOT_FOUND,
                f"Tool not found: {tool_name}"
            )
        
        try:
            self.logger.info(f"Calling tool: {tool_name}", tool=tool_name, arguments=arguments)
            
            # 执行工具
            tool = self.tools[tool_name]
            result = await tool.execute(arguments)
            
            self.logger.info(f"Tool executed successfully: {tool_name}", tool=tool_name, result=str(result))
            
            return MCPResponse.success(request.id, {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            })
        
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}", tool=tool_name, error=str(e))
            return MCPResponse.error(
                request.id,
                MCPError.TOOL_EXECUTION_ERROR,
                f"Tool execution failed: {str(e)}"
            )
    
    async def _handle_ping(self, request: MCPRequest) -> MCPResponse:
        """
        处理心跳检测请求
        
        Args:
            request: 心跳请求
            
        Returns:
            MCPResponse: 心跳响应
        """
        return MCPResponse.success(request.id, {"status": "ok", "timestamp": asyncio.get_event_loop().time()})
    
    async def start(self) -> None:
        """
        启动MCP服务器
        
        服务器将监听标准输入，处理来自客户端的请求
        
        类似于JavaScript中的:
        async start(): Promise<void> {
            this.running = true;
            this.logger.info("MCP Server started");
            
            // 监听stdin输入
            process.stdin.on('data', async (data) => {
                const request = JSON.parse(data.toString());
                const response = await this.handleRequest(request);
                process.stdout.write(JSON.stringify(response) + '\n');
            });
        }
        """
        self.running = True
        self.logger.info(f"MCP Server '{self.name}' started, listening on stdin/stdout")
        
        try:
            # 读取标准输入的循环
            while self.running:
                # 读取一行输入
                line = await self._read_line()
                if not line:
                    break
                
                try:
                    # 解析请求
                    request_data = json.loads(line)
                    request = MCPRequest(**request_data)
                    
                    # 处理请求
                    response = await self.handle_request(request)
                    
                    # 发送响应
                    await self._write_response(response)
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                    error_response = MCPResponse.error(
                        "unknown",
                        MCPError.PARSE_ERROR,
                        f"Parse error: {str(e)}"
                    )
                    await self._write_response(error_response)
                
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")
                    error_response = MCPResponse.error(
                        "unknown",
                        MCPError.INTERNAL_ERROR,
                        f"Internal error: {str(e)}"
                    )
                    await self._write_response(error_response)
        
        except KeyboardInterrupt:
            self.logger.info("Server interrupted by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """
        停止MCP服务器
        """
        self.running = False
        self.logger.info(f"MCP Server '{self.name}' stopped")
    
    async def _read_line(self) -> Optional[str]:
        """
        从标准输入读取一行
        
        Returns:
            Optional[str]: 读取的行，如果EOF则返回None
        
        类似于JavaScript中的:
        async readLine(): Promise<string | null> {
            return new Promise((resolve) => {
                process.stdin.once('data', (data) => {
                    resolve(data.toString().trim());
                });
            });
        }
        """
        loop = asyncio.get_event_loop()
        
        # 在单独的线程中读取stdin，避免阻塞事件循环
        try:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            return line.strip() if line else None
        except EOFError:
            return None
    
    async def _write_response(self, response: MCPResponse) -> None:
        """
        向标准输出写入响应
        
        Args:
            response: 要发送的响应
        """
        response_json = response.to_json()
        sys.stdout.write(response_json + "\n")
        sys.stdout.flush()
        
        self.logger.debug(f"Response sent: {response.id}", response_id=response.id)


# 便利函数，用于快速创建和启动服务器
async def create_and_run_server(name: str = "MCP-Server", tools: List[MCPTool] = None) -> None:
    """
    创建并运行MCP服务器
    
    这是一个便利函数，简化服务器的创建和启动过程
    
    Args:
        name: 服务器名称
        tools: 要注册的工具列表
    
    类似于JavaScript中的:
    async function createAndRunServer(name: string = "MCP-Server", tools: MCPTool[] = []): Promise<void> {
        const server = new MCPServer(name);
        
        for (const tool of tools) {
            server.registerTool(tool);
        }
        
        await server.start();
    }
    """
    server = MCPServer(name)
    
    # 注册工具
    if tools:
        for tool in tools:
            server.register_tool(tool)
    
    # 启动服务器
    await server.start()


# 导出主要的类和函数
__all__ = [
    "MCPTool",
    "MCPServer", 
    "create_and_run_server"
]