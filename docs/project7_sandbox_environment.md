### 项目7: 沙箱执行环境

#### 项目目标
- 实现安全的代码执行环境
- 支持多种编程语言
- 提供资源限制和安全隔离
- 集成到AI代理工作流中

#### 核心代码实现

**1. 沙箱基类**

```python
# src/sandbox/base_sandbox.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import uuid

@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: str
    error: str
    execution_time: float
    memory_usage: Optional[int] = None
    exit_code: Optional[int] = None
    session_id: str = ""

@dataclass
class SandboxConfig:
    """沙箱配置"""
    timeout: int = 30  # 超时时间（秒）
    memory_limit: int = 512  # 内存限制（MB）
    cpu_limit: float = 1.0  # CPU限制
    network_access: bool = False  # 网络访问
    file_system_access: bool = False  # 文件系统访问
    allowed_imports: List[str] = None  # 允许的导入模块

class BaseSandbox(ABC):
    """沙箱基类"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.sessions = {}  # 活跃会话
    
    @abstractmethod
    async def execute(self, code: str, language: str = "python", 
                     session_id: Optional[str] = None) -> ExecutionResult:
        """执行代码"""
        pass
    
    @abstractmethod
    async def create_session(self) -> str:
        """创建新会话"""
        pass
    
    @abstractmethod
    async def destroy_session(self, session_id: str) -> bool:
        """销毁会话"""
        pass
    
    def generate_session_id(self) -> str:
        """生成会话ID"""
        return str(uuid.uuid4())
```

**2. Docker沙箱实现**

```python
# src/sandbox/docker_sandbox.py
import docker
import asyncio
import tempfile
import os
from typing import Dict, Any, Optional
from .base_sandbox import BaseSandbox, ExecutionResult, SandboxConfig

class DockerSandbox(BaseSandbox):
    """Docker沙箱实现"""
    
    def __init__(self, config: SandboxConfig):
        super().__init__(config)
        self.client = docker.from_env()
        self.language_images = {
            'python': 'python:3.9-slim',
            'javascript': 'node:16-slim',
            'java': 'openjdk:11-slim',
            'go': 'golang:1.19-slim'
        }
    
    async def execute(self, code: str, language: str = "python", 
                     session_id: Optional[str] = None) -> ExecutionResult:
        """在Docker容器中执行代码"""
        start_time = time.time()
        
        try:
            # 选择镜像
            image = self.language_images.get(language)
            if not image:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"不支持的语言: {language}",
                    execution_time=0
                )
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # 运行容器
                result = await self._run_container(image, temp_file, language)
                execution_time = time.time() - start_time
                
                return ExecutionResult(
                    success=result['exit_code'] == 0,
                    output=result['output'],
                    error=result['error'],
                    execution_time=execution_time,
                    exit_code=result['exit_code'],
                    session_id=session_id or ""
                )
                
            finally:
                # 清理临时文件
                os.unlink(temp_file)
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )
    
    async def _run_container(self, image: str, code_file: str, language: str) -> Dict[str, Any]:
        """运行Docker容器"""
        # 构建运行命令
        command = self._get_run_command(language, os.path.basename(code_file))
        
        # 容器配置
        container_config = {
            'image': image,
            'command': command,
            'volumes': {os.path.dirname(code_file): {'bind': '/workspace', 'mode': 'ro'}},
            'working_dir': '/workspace',
            'mem_limit': f'{self.config.memory_limit}m',
            'cpu_period': 100000,
            'cpu_quota': int(100000 * self.config.cpu_limit),
            'network_disabled': not self.config.network_access,
            'remove': True,
            'stdout': True,
            'stderr': True
        }
        
        # 运行容器
        container = self.client.containers.run(**container_config, detach=True)
        
        try:
            # 等待执行完成
            result = container.wait(timeout=self.config.timeout)
            
            # 获取输出
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # 分离stdout和stderr
            output_lines = []
            error_lines = []
            
            for line in logs.split('\n'):
                if line.strip():
                    output_lines.append(line)
            
            return {
                'exit_code': result['StatusCode'],
                'output': '\n'.join(output_lines),
                'error': '' if result['StatusCode'] == 0 else '\n'.join(output_lines)
            }
            
        except docker.errors.ContainerError as e:
            return {
                'exit_code': e.exit_status,
                'output': '',
                'error': str(e)
            }
        except Exception as e:
            return {
                'exit_code': -1,
                'output': '',
                'error': str(e)
            }
    
    def _get_file_extension(self, language: str) -> str:
        """获取文件扩展名"""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'go': '.go'
        }
        return extensions.get(language, '.txt')
    
    def _get_run_command(self, language: str, filename: str) -> List[str]:
        """获取运行命令"""
        commands = {
            'python': ['python', filename],
            'javascript': ['node', filename],
            'java': ['sh', '-c', f'javac {filename} && java {filename[:-5]}'],
            'go': ['go', 'run', filename]
        }
        return commands.get(language, ['cat', filename])
    
    async def create_session(self) -> str:
        """创建新会话"""
        session_id = self.generate_session_id()
        # Docker沙箱通常是无状态的，这里只是记录会话
        self.sessions[session_id] = {
            'created_at': time.time(),
            'last_used': time.time()
        }
        return session_id
    
    async def destroy_session(self, session_id: str) -> bool:
         """销毁会话"""
         if session_id in self.sessions:
             del self.sessions[session_id]
             return True
         return False
 ```

**3. 沙箱代理集成**

```python
# src/agents/sandbox_agent.py
import asyncio
from typing import Dict, Any, List, Optional
from ..sandbox.docker_sandbox import DockerSandbox, SandboxConfig
from ..agents.react_agent import ReActAgent

class SandboxAgent(ReActAgent):
    """集成沙箱执行环境的代理"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 初始化沙箱
        sandbox_config = SandboxConfig(
            timeout=config.get('sandbox_timeout', 30),
            memory_limit=config.get('sandbox_memory_limit', 512),
            cpu_limit=config.get('sandbox_cpu_limit', 1.0),
            network_access=config.get('sandbox_network_access', False)
        )
        
        self.sandbox = DockerSandbox(sandbox_config)
        
        # 注册沙箱工具
        self.tools['execute_code'] = self._execute_code_tool
        self.tools['create_sandbox_session'] = self._create_session_tool
        self.tools['destroy_sandbox_session'] = self._destroy_session_tool
    
    async def _execute_code_tool(self, code: str, language: str = "python", 
                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """代码执行工具"""
        try:
            result = await self.sandbox.execute(code, language, session_id)
            return {
                "tool": "execute_code",
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time,
                "language": language
            }
        except Exception as e:
            return {
                "tool": "execute_code",
                "success": False,
                "error": str(e)
            }
    
    async def _create_session_tool(self) -> Dict[str, Any]:
        """创建沙箱会话工具"""
        try:
            session_id = await self.sandbox.create_session()
            return {
                "tool": "create_sandbox_session",
                "success": True,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "tool": "create_sandbox_session",
                "success": False,
                "error": str(e)
            }
    
    async def _destroy_session_tool(self, session_id: str) -> Dict[str, Any]:
        """销毁沙箱会话工具"""
        try:
            success = await self.sandbox.destroy_session(session_id)
            return {
                "tool": "destroy_sandbox_session",
                "success": success,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "tool": "destroy_sandbox_session",
                "success": False,
                "error": str(e)
            }
    
    async def solve_coding_problem(self, problem_description: str) -> Dict[str, Any]:
        """解决编程问题"""
        enhanced_prompt = f"""
{problem_description}

你是一个编程助手，可以执行代码来验证解决方案。
可用工具：
1. execute_code(code, language) - 执行代码
2. create_sandbox_session() - 创建新的执行会话
3. destroy_sandbox_session(session_id) - 销毁执行会话

请分析问题，编写代码，执行验证，并提供最终解决方案。
"""
        
        return await self.solve(enhanced_prompt)

# 使用示例
async def main():
    config = {
        'openai_api_key': 'your-api-key',
        'model': 'gpt-4',
        'sandbox_timeout': 30,
        'sandbox_memory_limit': 256,
        'sandbox_network_access': False
    }
    
    agent = SandboxAgent(config)
    
    # 示例：解决编程问题
    problems = [
        "编写一个Python函数来计算斐波那契数列的第n项",
        "实现一个JavaScript函数来判断一个字符串是否为回文",
        "用Python编写一个简单的计算器，支持加减乘除运算"
    ]
    
    for i, problem in enumerate(problems, 1):
        print(f"\n=== 问题 {i} ===")
        print(f"问题：{problem}")
        print("=" * 50)
        
        result = await agent.solve_coding_problem(problem)
        print(f"解决方案：{result}")
        
        # 显示执行轨迹
        print("\n执行轨迹：")
        for trace in agent.get_execution_trace():
            print(f"步骤 {trace['step']}: {trace['thought']}")
            if trace['action']:
                print(f"  行动: {trace['action']}")
            if trace['observation']:
                print(f"  观察: {trace['observation'][:200]}...")  # 截断长输出
        
        print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **安全隔离**：使用Docker容器提供安全的执行环境
2. **资源限制**：控制CPU、内存和执行时间
3. **多语言支持**：支持不同编程语言的执行
4. **会话管理**：管理长期的代码执行会话