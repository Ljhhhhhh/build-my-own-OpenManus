"""
MCP客户端实现

这个模块实现了MCP客户端，用于连接MCP服务器并调用远程工具。

对于JavaScript开发者的说明：
- 这里使用了Python的subprocess模块，类似于Node.js的child_process
- asyncio用于异步操作，类似于JavaScript的Promise和async/await
- 进程间通信通过stdin/stdout进行，类似于Node.js的IPC
"""

import asyncio
import subprocess
import json
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict

from .protocol import (
    MCPRequest, MCPResponse, ToolInfo, MCPMethod, MCPError,
    create_list_tools_request, create_call_tool_request, create_initialize_request
)
from utils.logger import get_logger
from utils.config import get_config


class MCPClientError(Exception):
    """MCP客户端异常类"""
    pass


class MCPServerConnection:
    """
    MCP服务器连接
    
    管理与单个MCP服务器的连接和通信
    
    类似于JavaScript中的:
    class MCPServerConnection {
        private process: ChildProcess;
        private connected: boolean = false;
        
        constructor(serverCommand: string[]) {
            this.serverCommand = serverCommand;
            this.logger = getLogger("mcp-client");
        }
    }
    """
    
    def __init__(self, server_command: List[str], server_name: str = None):
        """
        初始化服务器连接
        
        Args:
            server_command: 启动服务器的命令列表，例如 ["python", "server.py"]
            server_name: 服务器名称，用于日志和调试
        """
        self.server_command = server_command
        self.server_name = server_name or f"server-{uuid.uuid4().hex[:8]}"
        self.process: Optional[subprocess.Popen] = None
        self.connected = False
        self.tools_cache: Dict[str, Dict[str, Any]] = {}
        self.request_id_counter = 0
        
        self.logger = get_logger(f"mcp-client-{self.server_name}")
        self.config = get_config()
    
    async def connect(self) -> bool:
        """
        连接到MCP服务器
        
        Returns:
            bool: 是否连接成功
        
        类似于JavaScript中的:
        async connect(): Promise<boolean> {
            try {
                this.process = spawn(this.serverCommand[0], this.serverCommand.slice(1), {
                    stdio: ['pipe', 'pipe', 'pipe']
                });
                
                // 发送初始化请求
                const initResponse = await this.sendRequest(createInitializeRequest());
                this.connected = initResponse.success;
                
                return this.connected;
            } catch (error) {
                this.logger.error(`Connection failed: ${error.message}`);
                return false;
            }
        }
        """
        try:
            self.logger.info(f"Connecting to MCP server: {' '.join(self.server_command)}")
            
            # 启动服务器进程
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # 无缓冲，确保实时通信
            )
            
            # 发送初始化请求
            init_request = create_initialize_request(self._next_request_id())
            response = await self._send_request(init_request)
            
            if response and not response.error_info:
                self.connected = True
                self.logger.info(f"Successfully connected to MCP server: {self.server_name}")
                
                # 预加载工具列表
                await self._load_tools()
                
                return True
            else:
                error_msg = response.error_info.get("message", "Unknown error") if response and response.error_info else "No response"
                self.logger.error(f"Initialization failed: {error_msg}")
                await self.disconnect()
                return False
        
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            await self.disconnect()
            return False
    
    async def disconnect(self) -> None:
        """
        断开与服务器的连接
        
        类似于JavaScript中的:
        async disconnect(): Promise<void> {
            if (this.process) {
                this.process.kill();
                this.process = null;
            }
            this.connected = false;
            this.logger.info("Disconnected from MCP server");
        }
        """
        if self.process:
            try:
                self.process.terminate()
                # 等待进程结束，最多等待5秒
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()  # 强制终止
                    self.process.wait()
            except Exception as e:
                self.logger.warning(f"Error during disconnect: {e}")
            finally:
                self.process = None
        
        self.connected = False
        self.tools_cache.clear()
        self.logger.info(f"Disconnected from MCP server: {self.server_name}")
    
    async def list_tools(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        获取服务器上可用的工具列表
        
        Args:
            use_cache: 是否使用缓存的工具列表
            
        Returns:
            List[Dict]: 工具信息列表
        
        类似于JavaScript中的:
        async listTools(useCache: boolean = true): Promise<ToolInfo[]> {
            if (useCache && Object.keys(this.toolsCache).length > 0) {
                return Object.values(this.toolsCache);
            }
            
            const request = createListToolsRequest(this.nextRequestId());
            const response = await this.sendRequest(request);
            
            if (response.error) {
                throw new Error(`Failed to list tools: ${response.error.message}`);
            }
            
            return response.result.tools;
        }
        """
        if not self.connected:
            raise MCPClientError("Not connected to server")
        
        if use_cache and self.tools_cache:
            return list(self.tools_cache.values())
        
        request = create_list_tools_request(self._next_request_id())
        response = await self._send_request(request)
        
        if response and response.error_info:
            raise MCPClientError(f"Failed to list tools: {response.error_info.get('message', 'Unknown error')}")
        
        if response and response.result:
            tools = response.result.get("tools", [])
            # 更新缓存
            self.tools_cache = {tool["name"]: tool for tool in tools}
            return tools
        
        return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用服务器上的工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            Any: 工具执行结果
        
        类似于JavaScript中的:
        async callTool(toolName: string, arguments: Record<string, any>): Promise<any> {
            if (!this.connected) {
                throw new Error("Not connected to server");
            }
            
            const request = createCallToolRequest(this.nextRequestId(), toolName, arguments);
            const response = await this.sendRequest(request);
            
            if (response.error) {
                throw new Error(`Tool call failed: ${response.error.message}`);
            }
            
            return response.result;
        }
        """
        if not self.connected:
            raise MCPClientError("Not connected to server")
        
        self.logger.info(f"Calling tool: {tool_name}", tool=tool_name, arguments=arguments)
        
        request = create_call_tool_request(self._next_request_id(), tool_name, arguments)
        response = await self._send_request(request)
        
        if response and response.error_info:
            error_msg = response.error_info.get("message", "Unknown error")
            self.logger.error(f"Tool call failed: {error_msg}", tool=tool_name, error=error_msg)
            raise MCPClientError(f"Tool call failed: {error_msg}")
        
        if response and response.result:
            self.logger.info(f"Tool call successful: {tool_name}", tool=tool_name)
            return response.result
        
        raise MCPClientError("No response from server")
    
    async def ping(self) -> bool:
        """
        发送心跳检测
        
        Returns:
            bool: 服务器是否响应
        """
        if not self.connected:
            return False
        
        try:
            request = MCPRequest(
                id=self._next_request_id(),
                method=MCPMethod.PING.value
            )
            response = await self._send_request(request, timeout=5)
            return response is not None and not response.error_info
        except Exception:
            return False
    
    async def _send_request(self, request: MCPRequest, timeout: int = None) -> Optional[MCPResponse]:
        """
        发送请求到服务器
        
        Args:
            request: 要发送的请求
            timeout: 超时时间（秒）
            
        Returns:
            Optional[MCPResponse]: 服务器响应
        
        类似于JavaScript中的:
        private async sendRequest(request: MCPRequest, timeout?: number): Promise<MCPResponse | null> {
            if (!this.process) {
                throw new Error("Process not available");
            }
            
            // 发送请求
            this.process.stdin.write(JSON.stringify(request) + '\n');
            
            // 等待响应
            return new Promise((resolve, reject) => {
                const timer = timeout ? setTimeout(() => {
                    reject(new Error("Request timeout"));
                }, timeout * 1000) : null;
                
                this.process.stdout.once('data', (data) => {
                    if (timer) clearTimeout(timer);
                    try {
                        const response = JSON.parse(data.toString());
                        resolve(MCPResponse.fromJSON(response));
                    } catch (error) {
                        reject(error);
                    }
                });
            });
        }
        """
        if not self.process:
            raise MCPClientError("Process not available")
        
        timeout = timeout or self.config.server_timeout
        
        try:
            # 发送请求
            request_json = request.to_json()
            self.logger.debug(f"Sending request: {request.method}", request_id=request.id)
            
            self.process.stdin.write(request_json + "\n")
            self.process.stdin.flush()
            
            # 等待响应
            response_line = await asyncio.wait_for(
                self._read_response_line(),
                timeout=timeout
            )
            
            if response_line:
                response_data = json.loads(response_line)
                response = MCPResponse(**response_data)
                self.logger.debug(f"Received response: {response.id}", response_id=response.id)
                return response
            
            return None
        
        except asyncio.TimeoutError:
            self.logger.error(f"Request timeout: {request.method}", request_id=request.id)
            raise MCPClientError(f"Request timeout after {timeout} seconds")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            raise MCPClientError(f"Invalid JSON response: {e}")
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            raise MCPClientError(f"Request failed: {e}")
    
    async def _read_response_line(self) -> Optional[str]:
        """
        从服务器读取一行响应
        
        Returns:
            Optional[str]: 响应行，如果EOF则返回None
        """
        if not self.process or not self.process.stdout:
            return None
        
        loop = asyncio.get_event_loop()
        
        try:
            # 在线程池中读取，避免阻塞事件循环
            line = await loop.run_in_executor(None, self.process.stdout.readline)
            return line.strip() if line else None
        except Exception:
            return None
    
    async def _load_tools(self) -> None:
        """预加载工具列表到缓存"""
        try:
            await self.list_tools(use_cache=False)
        except Exception as e:
            self.logger.warning(f"Failed to preload tools: {e}")
    
    def _next_request_id(self) -> str:
        """
        生成下一个请求ID
        
        Returns:
            str: 唯一的请求ID
        """
        self.request_id_counter += 1
        return f"{self.server_name}-{self.request_id_counter}"
    
    def is_connected(self) -> bool:
        """
        检查是否已连接
        
        Returns:
            bool: 连接状态
        """
        return self.connected and self.process is not None and self.process.poll() is None
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        获取服务器信息
        
        Returns:
            Dict: 服务器信息
        """
        return {
            "name": self.server_name,
            "command": self.server_command,
            "connected": self.is_connected(),
            "tools_count": len(self.tools_cache)
        }


class MCPClient:
    """
    MCP客户端主类
    
    管理多个MCP服务器连接，提供统一的工具调用接口
    
    类似于JavaScript中的:
    class MCPClient {
        private connections: Map<string, MCPServerConnection> = new Map();
        
        constructor() {
            this.logger = getLogger("mcp-client");
        }
    }
    """
    
    def __init__(self):
        """初始化MCP客户端"""
        self.connections: Dict[str, MCPServerConnection] = {}
        self.logger = get_logger("mcp-client")
        self.config = get_config()
    
    async def add_server(self, server_name: str, server_command: List[str]) -> bool:
        """
        添加MCP服务器
        
        Args:
            server_name: 服务器名称
            server_command: 启动服务器的命令
            
        Returns:
            bool: 是否添加成功
        
        类似于JavaScript中的:
        async addServer(serverName: string, serverCommand: string[]): Promise<boolean> {
            if (this.connections.has(serverName)) {
                throw new Error(`Server already exists: ${serverName}`);
            }
            
            const connection = new MCPServerConnection(serverCommand, serverName);
            const connected = await connection.connect();
            
            if (connected) {
                this.connections.set(serverName, connection);
                this.logger.info(`Server added: ${serverName}`);
                return true;
            }
            
            return false;
        }
        """
        if server_name in self.connections:
            raise MCPClientError(f"Server already exists: {server_name}")
        
        connection = MCPServerConnection(server_command, server_name)
        connected = await connection.connect()
        
        if connected:
            self.connections[server_name] = connection
            self.logger.info(f"Server added: {server_name}")
            return True
        
        return False
    
    async def remove_server(self, server_name: str) -> bool:
        """
        移除MCP服务器
        
        Args:
            server_name: 服务器名称
            
        Returns:
            bool: 是否移除成功
        """
        if server_name not in self.connections:
            return False
        
        connection = self.connections[server_name]
        await connection.disconnect()
        del self.connections[server_name]
        
        self.logger.info(f"Server removed: {server_name}")
        return True
    
    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有服务器的工具列表
        
        Returns:
            Dict[str, List[Dict]]: 按服务器分组的工具列表
        """
        all_tools = {}
        
        for server_name, connection in self.connections.items():
            try:
                if connection.is_connected():
                    tools = await connection.list_tools()
                    all_tools[server_name] = tools
                else:
                    all_tools[server_name] = []
            except Exception as e:
                self.logger.error(f"Failed to list tools from {server_name}: {e}")
                all_tools[server_name] = []
        
        return all_tools
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用指定服务器上的工具
        
        Args:
            server_name: 服务器名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            Any: 工具执行结果
        """
        if server_name not in self.connections:
            raise MCPClientError(f"Server not found: {server_name}")
        
        connection = self.connections[server_name]
        if not connection.is_connected():
            raise MCPClientError(f"Server not connected: {server_name}")
        
        return await connection.call_tool(tool_name, arguments)
    
    async def find_and_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        查找并调用工具（自动选择服务器）
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            Any: 工具执行结果
        """
        # 查找拥有该工具的服务器
        for server_name, connection in self.connections.items():
            if connection.is_connected() and tool_name in connection.tools_cache:
                return await connection.call_tool(tool_name, arguments)
        
        raise MCPClientError(f"Tool not found on any server: {tool_name}")
    
    async def disconnect_all(self) -> None:
        """断开所有服务器连接"""
        for connection in self.connections.values():
            await connection.disconnect()
        
        self.connections.clear()
        self.logger.info("All servers disconnected")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取客户端状态
        
        Returns:
            Dict: 客户端状态信息
        """
        return {
            "servers_count": len(self.connections),
            "connected_servers": [
                name for name, conn in self.connections.items() 
                if conn.is_connected()
            ],
            "servers": {
                name: conn.get_server_info() 
                for name, conn in self.connections.items()
            }
        }


# 导出主要的类
__all__ = [
    "MCPClient",
    "MCPServerConnection", 
    "MCPClientError"
]