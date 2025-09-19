"""
异步工具基类

这个模块定义了异步工具的基础接口和通用功能。
专注于异步编程的核心概念，移除了复杂的高级特性。

学习要点：
1. 抽象基类的设计 (ABC)
2. 异步方法的定义
3. 数据模型的使用 (Pydantic)
4. 基础的输入验证和错误处理
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class ToolResultStatus(Enum):
    """
    工具执行结果状态枚举
    
    💡 对比TypeScript:
    enum ToolResultStatus {
        SUCCESS = "success",
        ERROR = "error",
        TIMEOUT = "timeout",
        INVALID_INPUT = "invalid_input"
    }
    
    学习要点：
    - 枚举类型的定义和使用
    - 状态管理的设计
    """
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"


class ToolResult(BaseModel):
    """
    工具执行结果模型
    
    💡 对比TypeScript:
    interface ToolResult {
        status: ToolResultStatus;
        content: any;
        errorMessage?: string;
        executionTime: number;
        timestamp: number;
    }
    
    学习要点：
    - Pydantic 模型的定义
    - 数据验证和序列化
    - 可选字段的处理
    - 静态方法的使用
    """
    status: ToolResultStatus
    content: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time: float = Field(default=0.0, description="执行时间（秒）")
    timestamp: float = Field(default_factory=time.time, description="时间戳")
    
    def is_success(self) -> bool:
        """检查是否执行成功"""
        return self.status == ToolResultStatus.SUCCESS
    
    def is_error(self) -> bool:
        """检查是否执行失败"""
        return self.status == ToolResultStatus.ERROR
    
    def is_timeout(self) -> bool:
        """检查是否超时"""
        return self.status == ToolResultStatus.TIMEOUT
    
    def is_invalid_input(self) -> bool:
        """检查是否输入无效"""
        return self.status == ToolResultStatus.INVALID_INPUT
    
    @classmethod
    def success(cls, content: Any, execution_time: float = 0.0) -> "ToolResult":
        """创建成功结果"""
        return cls(
            status=ToolResultStatus.SUCCESS,
            content=content,
            execution_time=execution_time
        )
    
    @classmethod
    def error(cls, error_message: str, execution_time: float = 0.0) -> "ToolResult":
        """创建错误结果"""
        return cls(
            status=ToolResultStatus.ERROR,
            error_message=error_message,
            execution_time=execution_time
        )
    
    @classmethod
    def timeout(cls, error_message: str = "执行超时", execution_time: float = 0.0) -> "ToolResult":
        """创建超时结果"""
        return cls(
            status=ToolResultStatus.TIMEOUT,
            error_message=error_message,
            execution_time=execution_time
        )
    
    @classmethod
    def invalid_input(cls, error_message: str, execution_time: float = 0.0) -> "ToolResult":
        """创建输入无效结果"""
        return cls(
            status=ToolResultStatus.INVALID_INPUT,
            error_message=error_message,
            execution_time=execution_time
        )


class AsyncBaseTool(ABC):
    """
    异步工具基类 - 简化版
    
    💡 对比TypeScript:
    abstract class AsyncBaseTool {
        protected name: string;
        protected description: string;
        protected timeout: number;
        
        constructor(name: string, description: string, timeout: number = 30) {
            this.name = name;
            this.description = description;
            this.timeout = timeout;
        }
        
        abstract get schema(): object;
        
        async validateInput(params: any): Promise<boolean | string> {
            // 默认验证逻辑
            return true;
        }
        
        abstract execute(params: any): Promise<ToolResult>;
        
        async executeWithTimeout(params: any): Promise<ToolResult> {
            const startTime = Date.now();
            
            try {
                const result = await Promise.race([
                    this.execute(params),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Timeout')), this.timeout * 1000)
                    )
                ]);
                
                const executionTime = (Date.now() - startTime) / 1000;
                result.executionTime = executionTime;
                return result;
                
            } catch (error) {
                const executionTime = (Date.now() - startTime) / 1000;
                
                if (error.message === 'Timeout') {
                    return ToolResult.timeout('执行超时', executionTime);
                }
                
                return ToolResult.error(error.message, executionTime);
            }
        }
    }
    
    学习要点：
    - 抽象基类的设计和实现
    - 异步方法的超时处理
    - 输入验证的基础实现
    - 错误处理的统一化
    """
    
    def __init__(self, name: str, description: str, timeout: float = 30.0):
        """
        初始化异步工具
        
        学习要点：
        - 基类构造函数的设计
        - 参数验证和默认值
        - 实例属性的初始化
        
        Args:
            name: 工具名称
            description: 工具描述
            timeout: 超时时间（秒）
        """
        if not name or not isinstance(name, str):
            raise ValueError("工具名称不能为空且必须是字符串")
        
        if not description or not isinstance(description, str):
            raise ValueError("工具描述不能为空且必须是字符串")
        
        if timeout <= 0:
            raise ValueError("超时时间必须大于0")
        
        self.name = name
        self.description = description
        self.timeout = timeout
    
    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """
        工具的输入参数模式
        
        学习要点：
        - 抽象属性的定义
        - JSON Schema 的使用
        - 接口设计的重要性
        
        Returns:
            Dict[str, Any]: JSON Schema 格式的参数定义
        """
        pass
    
    async def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        验证输入参数
        
        学习要点：
        - 异步验证方法的实现
        - 基础的参数验证逻辑
        - 返回值的设计（成功返回True，失败返回错误信息）
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            Union[bool, str]: True表示验证通过，字符串表示错误信息
        """
        # 基础验证：检查必需参数
        schema = self.schema
        if "required" in schema and isinstance(schema["required"], list):
            for required_field in schema["required"]:
                if required_field not in kwargs:
                    return f"缺少必需参数: {required_field}"
        
        # 基础类型验证
        if "properties" in schema:
            for field_name, field_schema in schema["properties"].items():
                if field_name in kwargs:
                    value = kwargs[field_name]
                    field_type = field_schema.get("type")
                    
                    # 简单的类型检查
                    if field_type == "string" and not isinstance(value, str):
                        return f"参数 {field_name} 必须是字符串类型"
                    elif field_type == "number" and not isinstance(value, (int, float)):
                        return f"参数 {field_name} 必须是数字类型"
                    elif field_type == "boolean" and not isinstance(value, bool):
                        return f"参数 {field_name} 必须是布尔类型"
        
        return True
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具的核心逻辑
        
        学习要点：
        - 抽象方法的定义
        - 异步执行的接口设计
        - 统一的返回值类型
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    async def execute_with_timeout(self, **kwargs) -> ToolResult:
        """
        带超时控制的执行方法
        
        学习要点：
        - asyncio.wait_for 的使用
        - 超时处理的实现
        - 执行时间的计算
        - 异常处理的统一化
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        start_time = time.time()
        
        try:
            # 使用 asyncio.wait_for 实现超时控制
            result = await asyncio.wait_for(
                self.execute(**kwargs),
                timeout=self.timeout
            )
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 更新执行时间
            if hasattr(result, 'execution_time'):
                result.execution_time = execution_time
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return ToolResult.timeout(
                f"工具 '{self.name}' 执行超时（{self.timeout}秒）",
                execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                f"工具 '{self.name}' 执行异常: {str(e)}",
                execution_time
            )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"AsyncTool(name='{self.name}', description='{self.description}')"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (
            f"AsyncBaseTool(name='{self.name}', "
            f"description='{self.description}', "
            f"timeout={self.timeout})"
        )


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    # 简单的测试工具实现
    class TestCalculatorTool(AsyncBaseTool):
        """测试计算器工具"""
        
        def __init__(self):
            super().__init__(
                name="test_calculator",
                description="简单的测试计算器",
                timeout=5.0
            )
        
        @property
        def schema(self) -> Dict[str, Any]:
            return {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "运算类型",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "a": {"type": "number", "description": "第一个数"},
                    "b": {"type": "number", "description": "第二个数"}
                },
                "required": ["operation", "a", "b"]
            }
        
        async def execute(self, **kwargs) -> ToolResult:
            operation = kwargs["operation"]
            a = kwargs["a"]
            b = kwargs["b"]
            
            # 模拟异步操作
            await asyncio.sleep(0.1)
            
            try:
                if operation == "add":
                    result = a + b
                elif operation == "subtract":
                    result = a - b
                elif operation == "multiply":
                    result = a * b
                elif operation == "divide":
                    if b == 0:
                        return ToolResult.error("除数不能为零")
                    result = a / b
                else:
                    return ToolResult.error(f"不支持的运算类型: {operation}")
                
                return ToolResult.success({
                    "operation": operation,
                    "operands": [a, b],
                    "result": result
                })
                
            except Exception as e:
                return ToolResult.error(f"计算异常: {str(e)}")
    
    async def test_base_tool():
        """测试基础工具功能"""
        print("🧪 测试异步基础工具")
        print("=" * 40)
        
        # 创建测试工具
        calculator = TestCalculatorTool()
        print(f"工具信息: {calculator}")
        print(f"工具模式: {calculator.schema}")
        
        # 测试输入验证
        print("\n🔍 测试输入验证:")
        
        # 有效输入
        valid_params = {"operation": "add", "a": 10, "b": 5}
        validation_result = await calculator.validate_input(**valid_params)
        print(f"有效输入验证: {validation_result}")
        
        # 无效输入（缺少参数）
        invalid_params = {"operation": "add", "a": 10}
        validation_result = await calculator.validate_input(**invalid_params)
        print(f"无效输入验证: {validation_result}")
        
        # 测试工具执行
        print("\n🚀 测试工具执行:")
        
        # 正常执行
        result = await calculator.execute_with_timeout(**valid_params)
        print(f"加法结果: {result.content}")
        print(f"执行时间: {result.execution_time:.3f}秒")
        
        # 除零错误
        divide_zero_params = {"operation": "divide", "a": 10, "b": 0}
        result = await calculator.execute_with_timeout(**divide_zero_params)
        print(f"除零错误: {result.error_message}")
        
        # 测试不同运算
        operations = [
            {"operation": "subtract", "a": 10, "b": 3},
            {"operation": "multiply", "a": 4, "b": 5},
            {"operation": "divide", "a": 15, "b": 3}
        ]
        
        print("\n📊 测试多种运算:")
        for params in operations:
            result = await calculator.execute_with_timeout(**params)
            if result.is_success():
                content = result.content
                print(f"{content['operation']}: {content['operands'][0]} {content['operation']} {content['operands'][1]} = {content['result']}")
            else:
                print(f"错误: {result.error_message}")
        
        print("\n✅ 基础工具测试完成!")
    
    # 运行测试
    asyncio.run(test_base_tool())