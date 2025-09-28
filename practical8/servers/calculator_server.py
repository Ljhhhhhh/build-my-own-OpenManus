"""
计算器MCP服务器

这个模块实现了一个专门提供计算器功能的MCP服务器。

对于JavaScript开发者的说明：
- 这里展示了如何将工具包装成MCP服务器
- 使用了Python的if __name__ == "__main__"，类似于Node.js的require.main === module
- 异步主函数模式类似于JavaScript的顶级await
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径，确保能够导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import MCPServer, MCPTool
from mcp.protocol import ToolInfo, ToolParameter
from tools.calculator import CalculatorTool, AdvancedCalculatorTool
from utils.logger import setup_logging
from utils.config import get_config


class CalculatorMCPTool(MCPTool):
    """
    计算器MCP工具包装器
    
    将CalculatorTool包装成符合MCP接口的工具
    
    类似于JavaScript中的:
    class CalculatorMCPTool extends MCPTool {
        private calculator: CalculatorTool;
        
        constructor() {
            super();
            this.calculator = new CalculatorTool();
        }
        
        getInfo(): ToolInfo {
            return this.calculator.getSchema();
        }
        
        async execute(arguments: Record<string, any>): Promise<any> {
            const result = await this.calculator.execute(arguments);
            return result.data;
        }
    }
    """
    
    def __init__(self):
        """初始化计算器MCP工具"""
        self.calculator = CalculatorTool()
    
    def get_info(self) -> ToolInfo:
        """
        获取工具信息
        
        Returns:
            ToolInfo: 工具信息
        """
        return ToolInfo(
            name=self.calculator.name,
            description=self.calculator.description,
            parameters=[
                ToolParameter(
                    name=param.name,
                    type=param.type,
                    description=param.description,
                    required=param.required
                )
                for param in self.calculator.parameters
            ]
        )
    
    async def execute(self, arguments: dict) -> any:
        """
        执行计算器工具
        
        Args:
            arguments: 工具参数
            
        Returns:
            any: 执行结果
        """
        result = await self.calculator.execute(arguments)
        
        if result.success:
            return result.data
        else:
            raise Exception(result.error)


class AdvancedCalculatorMCPTool(MCPTool):
    """
    高级计算器MCP工具包装器
    
    将AdvancedCalculatorTool包装成符合MCP接口的工具
    """
    
    def __init__(self):
        """初始化高级计算器MCP工具"""
        self.calculator = AdvancedCalculatorTool()
    
    def get_info(self) -> ToolInfo:
        """获取工具信息"""
        return ToolInfo(
            name=self.calculator.name,
            description=self.calculator.description,
            parameters=[
                ToolParameter(
                    name=param.name,
                    type=param.type,
                    description=param.description,
                    required=param.required
                )
                for param in self.calculator.parameters
            ]
        )
    
    async def execute(self, arguments: dict) -> any:
        """执行高级计算器工具"""
        result = await self.calculator.execute(arguments)
        
        if result.success:
            return result.data
        else:
            raise Exception(result.error)


async def main():
    """
    主函数 - 启动计算器MCP服务器
    
    类似于JavaScript中的:
    async function main(): Promise<void> {
        // 设置日志
        const logger = setupLogging();
        
        // 创建服务器
        const server = new MCPServer("Calculator-MCP-Server");
        
        // 注册工具
        server.registerTool(new CalculatorMCPTool());
        server.registerTool(new AdvancedCalculatorMCPTool());
        
        // 启动服务器
        logger.info("Starting Calculator MCP Server...");
        await server.start();
    }
    
    // 如果是主模块，运行主函数
    if (require.main === module) {
        main().catch(console.error);
    }
    """
    try:
        # 设置日志
        logger = setup_logging(log_level="INFO")
        logger.info("Initializing Calculator MCP Server...")
        
        # 创建MCP服务器
        server = MCPServer("Calculator-MCP-Server")
        
        # 注册工具
        calculator_tool = CalculatorMCPTool()
        advanced_calculator_tool = AdvancedCalculatorMCPTool()
        
        server.register_tool(calculator_tool)
        server.register_tool(advanced_calculator_tool)
        
        logger.info("Tools registered:")
        logger.info(f"  - {calculator_tool.get_info().name}: {calculator_tool.get_info().description}")
        logger.info(f"  - {advanced_calculator_tool.get_info().name}: {advanced_calculator_tool.get_info().description}")
        
        # 启动服务器
        logger.info("Starting Calculator MCP Server...")
        logger.info("Server is ready to accept requests on stdin/stdout")
        
        await server.start()
    
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def create_calculator_server() -> MCPServer:
    """
    创建计算器服务器的工厂函数
    
    这个函数可以被其他模块调用来创建服务器实例
    
    Returns:
        MCPServer: 配置好的计算器服务器
    
    类似于JavaScript中的:
    function createCalculatorServer(): MCPServer {
        const server = new MCPServer("Calculator-MCP-Server");
        server.registerTool(new CalculatorMCPTool());
        server.registerTool(new AdvancedCalculatorMCPTool());
        return server;
    }
    """
    server = MCPServer("Calculator-MCP-Server")
    server.register_tool(CalculatorMCPTool())
    server.register_tool(AdvancedCalculatorMCPTool())
    return server


# 如果作为主程序运行，启动服务器
if __name__ == "__main__":
    """
    程序入口点
    
    类似于JavaScript中的:
    if (require.main === module) {
        main().catch((error) => {
            console.error("Fatal error:", error);
            process.exit(1);
        });
    }
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)