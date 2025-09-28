"""
MCP (Model Communication Protocol) 协议定义

这个模块定义了MCP协议的核心数据结构和消息格式。
MCP协议基于JSON-RPC 2.0，用于AI代理与工具服务器之间的通信。

对于JavaScript开发者的说明：
- 这里使用Python的dataclass，类似于TypeScript的interface
- Optional[T] 相当于 T | undefined
- Dict 相当于 Record<string, any>
- List 相当于 Array
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any, Union
import json
from enum import Enum


class MCPMessageType(Enum):
    """
    MCP消息类型枚举
    
    类似于TypeScript中的:
    enum MCPMessageType {
        REQUEST = "request",
        RESPONSE = "response", 
        ERROR = "error"
    }
    """
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"


class MCPMethod(Enum):
    """
    MCP支持的方法类型
    
    这些方法定义了客户端可以向服务器发送的请求类型
    """
    # 工具相关方法
    LIST_TOOLS = "tools/list"          # 获取可用工具列表
    CALL_TOOL = "tools/call"           # 调用特定工具
    
    # 服务器信息方法
    INITIALIZE = "initialize"          # 初始化连接
    PING = "ping"                     # 心跳检测


@dataclass
class ToolParameter:
    """
    工具参数定义
    
    对应JavaScript中的:
    interface ToolParameter {
        name: string;
        type: string;
        description: string;
        required: boolean;
    }
    """
    name: str                    # 参数名称
    type: str                    # 参数类型 (string, number, boolean, object, array)
    description: str             # 参数描述
    required: bool = True        # 是否必需参数


@dataclass 
class ToolInfo:
    """
    工具信息定义
    
    描述一个可用工具的完整信息，包括名称、描述和参数
    """
    name: str                           # 工具名称
    description: str                    # 工具描述
    parameters: List[ToolParameter]     # 工具参数列表
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式，用于JSON序列化
        
        类似于JavaScript中的:
        toJSON(): object {
            return { ...this };
        }
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [asdict(param) for param in self.parameters]
        }


@dataclass
class MCPRequest:
    """
    MCP请求消息
    
    基于JSON-RPC 2.0格式的请求消息
    
    对应JavaScript中的:
    interface MCPRequest {
        jsonrpc: "2.0";
        id: string | number;
        method: string;
        params?: Record<string, any>;
    }
    """
    jsonrpc: str = "2.0"                    # JSON-RPC版本
    id: Union[str, int] = "1"               # 请求ID，用于匹配请求和响应
    method: str = ""                        # 请求方法
    params: Optional[Dict[str, Any]] = None # 请求参数
    
    def to_json(self) -> str:
        """
        序列化为JSON字符串
        
        类似于JavaScript中的:
        toJSON(): string {
            return JSON.stringify(this);
        }
        """
        data = asdict(self)
        # 移除None值的参数
        if data["params"] is None:
            del data["params"]
        return json.dumps(data, default=str)  # 添加default=str处理不可序列化的对象
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPRequest":
        """
        从JSON字符串反序列化
        
        类似于JavaScript中的:
        static fromJSON(jsonStr: string): MCPRequest {
            return Object.assign(new MCPRequest(), JSON.parse(jsonStr));
        }
        """
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class MCPResponse:
    """
    MCP响应消息
    
    基于JSON-RPC 2.0格式的响应消息
    """
    jsonrpc: str = "2.0"                    # JSON-RPC版本
    id: Union[str, int] = "1"               # 对应的请求ID
    result: Optional[Any] = None            # 成功响应的结果
    error_info: Optional[Dict[str, Any]] = None  # 错误信息（重命名避免与类方法冲突）
    
    def to_json(self) -> str:
        """序列化为JSON字符串"""
        # 手动构建数据字典，只包含实例字段
        data = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        
        # 只添加非None的result或error
        if self.result is not None:
            data["result"] = self.result
        if self.error_info is not None:
            data["error"] = self.error_info  # 在JSON中仍使用"error"字段名
            
        return json.dumps(data, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPResponse":
        """从JSON字符串反序列化"""
        data = json.loads(json_str)
        # 将JSON中的"error"字段映射到error_info
        if "error" in data:
            data["error_info"] = data.pop("error")
        return cls(**data)
    
    @classmethod
    def success(cls, request_id: Union[str, int], result: Any) -> "MCPResponse":
        """
        创建成功响应
        
        这是一个工厂方法，类似于JavaScript中的:
        static success(requestId: string | number, result: any): MCPResponse {
            return new MCPResponse({ id: requestId, result });
        }
        """
        return cls(id=request_id, result=result)
    
    @classmethod
    def error(cls, request_id: Union[str, int], code: int, message: str, data: Any = None) -> "MCPResponse":
        """
        创建错误响应
        
        错误格式遵循JSON-RPC 2.0标准
        """
        error_obj = {
            "code": code,
            "message": message
        }
        if data is not None:
            error_obj["data"] = data
            
        return cls(id=request_id, error_info=error_obj)


class MCPError:
    """
    MCP错误代码定义
    
    基于JSON-RPC 2.0错误代码标准
    """
    # JSON-RPC 2.0 标准错误代码
    PARSE_ERROR = -32700        # 解析错误
    INVALID_REQUEST = -32600    # 无效请求
    METHOD_NOT_FOUND = -32601   # 方法未找到
    INVALID_PARAMS = -32602     # 无效参数
    INTERNAL_ERROR = -32603     # 内部错误
    
    # MCP特定错误代码
    TOOL_NOT_FOUND = -32001     # 工具未找到
    TOOL_EXECUTION_ERROR = -32002  # 工具执行错误
    SERVER_NOT_AVAILABLE = -32003  # 服务器不可用


def create_list_tools_request(request_id: Union[str, int] = "1") -> MCPRequest:
    """
    创建获取工具列表的请求
    
    这是一个便利函数，简化常用请求的创建
    
    类似于JavaScript中的:
    function createListToolsRequest(requestId: string | number = "1"): MCPRequest {
        return new MCPRequest({
            id: requestId,
            method: "tools/list"
        });
    }
    """
    return MCPRequest(
        id=request_id,
        method=MCPMethod.LIST_TOOLS.value
    )


def create_call_tool_request(
    request_id: Union[str, int],
    tool_name: str,
    arguments: Dict[str, Any]
) -> MCPRequest:
    """
    创建调用工具的请求
    
    Args:
        request_id: 请求ID
        tool_name: 工具名称
        arguments: 工具参数
    
    Returns:
        MCPRequest: 格式化的工具调用请求
    """
    return MCPRequest(
        id=request_id,
        method=MCPMethod.CALL_TOOL.value,
        params={
            "name": tool_name,
            "arguments": arguments
        }
    )


def create_initialize_request(request_id: Union[str, int] = "1") -> MCPRequest:
    """
    创建初始化请求
    
    用于建立客户端与服务器之间的连接
    """
    return MCPRequest(
        id=request_id,
        method=MCPMethod.INITIALIZE.value,
        params={
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "MCP-Python-Client",
                "version": "1.0.0"
            }
        }
    )


# 导出主要的类和函数，方便其他模块使用
__all__ = [
    "MCPMessageType",
    "MCPMethod", 
    "ToolParameter",
    "ToolInfo",
    "MCPRequest",
    "MCPResponse",
    "MCPError",
    "create_list_tools_request",
    "create_call_tool_request",
    "create_initialize_request"
]