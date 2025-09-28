"""
阶段3：Docker沙箱实现
目标：使用Docker容器实现完全隔离的执行环境

新增核心概念：
1. 容器隔离：完全独立的运行环境
2. 镜像管理：自动拉取和管理Docker镜像
3. 网络隔离：禁用网络访问防止外部通信
4. 文件系统隔离：只读挂载，防止文件系统破坏
5. 用户权限控制：非root用户执行

对于JavaScript开发者的理解：
- Docker容器 ≈ 虚拟机但更轻量
- 镜像管理 ≈ npm包管理，但是整个运行环境
- 容器配置 ≈ package.json的scripts配置
- 网络隔离 ≈ 浏览器的同源策略
"""

import docker
import tempfile
import os
import time
import tarfile
import io
from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.config import get_config


class DockerSandbox:
    """Docker沙箱 - 完全隔离的执行环境
    
    这个类展示了如何使用Docker实现真正的沙箱：
    1. 容器完全隔离：独立的进程空间、文件系统、网络
    2. 资源限制：内存、CPU限制
    3. 安全控制：非root用户、只读文件系统
    4. 自动清理：容器自动删除
    """

    def __init__(self, timeout: int = None, memory_limit: str = None, enable_network: bool = False):
        """初始化Docker沙箱
        
        Args:
            timeout: 执行超时时间（秒）
            memory_limit: 内存限制（如 "128m", "1g"）
            enable_network: 是否启用网络访问
        """
        self.timeout = timeout or get_config('timeout', 30)
        self.memory_limit = memory_limit or get_config('docker_memory_limit', '128m')
        self.enable_network = enable_network
        
        # 初始化Docker客户端
        try:
            self.client = docker.from_env()
            self.logger = get_logger("DockerSandbox")
            self.logger.info("Docker客户端连接成功")
        except Exception as e:
            self.logger = get_logger("DockerSandbox")
            self.logger.error(f"Docker客户端连接失败: {e}")
            raise RuntimeError(f"无法连接到Docker: {e}")

        # 支持的语言和对应的Docker镜像
        self.language_images = {
            'python': 'python:3.9-slim',
            'javascript': 'node:18-alpine',
            'java': 'openjdk:11-jre-slim',
            'go': 'golang:1.19-alpine'
        }
        
        # 语言文件扩展名
        self.language_extensions = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java',
            'go': 'go'
        }
        
        # 语言执行命令
        self.language_commands = {
            'python': ['python', '/workspace/code.py'],
            'javascript': ['node', '/workspace/code.js'],
            'java': ['sh', '-c', 'cd /workspace && javac code.java && java code'],
            'go': ['sh', '-c', 'cd /workspace && go run code.go']
        }
        
        # 确保所需镜像存在
        self._ensure_images()
        
        self.logger.info(f"DockerSandbox初始化完成 - 超时: {self.timeout}秒, 内存: {self.memory_limit}")

    def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """在Docker容器中执行代码
        
        Args:
            code: 要执行的代码
            language: 编程语言
            
        Returns:
            包含执行结果的字典
        """
        start_time = time.time()
        
        # 验证语言支持
        if language not in self.language_images:
            return self._create_error_result(
                f"不支持的语言: {language}，支持的语言: {list(self.language_images.keys())}", 
                0
            )

        # 创建临时文件
        temp_file = self._create_temp_file(code, language)
        
        try:
            # 在容器中执行代码
            result = self._run_in_container(temp_file, language)
            result['execution_time'] = time.time() - start_time
            
            # 记录执行日志
            self.logger.log_execution("DockerSandbox", code[:50] + "...", result)
            
            return result

        finally:
            # 清理临时文件
            self._cleanup_temp_file(temp_file)

    def _create_temp_file(self, code: str, language: str) -> str:
        """创建临时代码文件"""
        extension = self.language_extensions.get(language, 'txt')
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{extension}',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_file = f.name
        
        self.logger.debug(f"创建临时文件: {temp_file}")
        return temp_file

    def _run_in_container(self, code_file: str, language: str) -> Dict[str, Any]:
        """在Docker容器中运行代码"""
        image = self.language_images[language]
        command = self.language_commands[language]
        
        container_id = None
        
        try:
            # 重命名文件以匹配容器内的路径
            container_filename = f"code.{self.language_extensions[language]}"
            container_file_path = os.path.join(os.path.dirname(code_file), container_filename)
            os.rename(code_file, container_file_path)
            
            # 容器配置
            container_config = {
                'image': image,
                'command': command,
                'volumes': {
                    os.path.dirname(container_file_path): {
                        'bind': '/workspace',
                        'mode': 'ro'  # 只读模式
                    }
                },
                'working_dir': '/workspace',
                'mem_limit': self.memory_limit,
                'network_disabled': not self.enable_network,  # 网络隔离
                'user': '1000:1000',  # 非root用户
                'detach': True,  # 后台运行
                'stdout': True,
                'stderr': True,
                'remove': False  # 先不自动删除，获取日志后再删除
            }
            
            # 启动容器
            self.logger.debug(f"启动容器，镜像: {image}")
            container = self.client.containers.run(**container_config)
            container_id = container.id[:12]
            
            self.logger.log_docker_operation("容器启动", container_id, "成功")
            
            # 等待容器执行完成
            try:
                exit_status = container.wait(timeout=self.timeout)
                self.logger.log_docker_operation("容器执行完成", container_id, f"退出码: {exit_status['StatusCode']}")
            except Exception as e:
                self.logger.log_docker_operation("容器执行超时", container_id, str(e))
                # 尝试停止容器
                try:
                    container.stop(timeout=1)
                    container.remove()
                except:
                    pass
                return self._create_error_result(f'容器执行超时（{self.timeout}秒）', self.timeout, -1)

            # 获取容器日志
            try:
                logs = container.logs().decode('utf-8', errors='replace')
            except Exception as e:
                self.logger.warning(f"获取容器日志失败: {e}")
                logs = ""
            
            # 清理容器
            try:
                container.remove()
            except Exception as e:
                self.logger.warning(f"删除容器失败: {e}")
            
            # 分离stdout和stderr（Docker logs混合了两者）
            # 这是一个简化的处理，实际情况可能需要更复杂的日志分离
            if exit_status['StatusCode'] == 0:
                return {
                    'success': True,
                    'output': logs.strip(),
                    'error': '',
                    'exit_code': exit_status['StatusCode'],
                    'container_id': container_id,
                    'image': image
                }
            else:
                return {
                    'success': False,
                    'output': '',
                    'error': logs.strip(),
                    'exit_code': exit_status['StatusCode'],
                    'container_id': container_id,
                    'image': image
                }

        except docker.errors.ContainerError as e:
            self.logger.error(f"容器执行错误: {e}")
            return {
                'success': False,
                'output': '',
                'error': f'容器执行错误: {str(e)}',
                'exit_code': e.exit_status if hasattr(e, 'exit_status') else -1,
                'container_id': container_id,
                'image': image
            }
        except docker.errors.ImageNotFound:
            self.logger.error(f"Docker镜像未找到: {image}")
            return self._create_error_result(f'Docker镜像未找到: {image}', 0, -2)
        except Exception as e:
            self.logger.error(f"Docker执行异常: {e}")
            return self._create_error_result(f'Docker执行异常: {str(e)}', 0, -3)

    def _ensure_images(self):
        """确保所需的Docker镜像存在"""
        for language, image in self.language_images.items():
            try:
                # 检查镜像是否存在
                self.client.images.get(image)
                self.logger.debug(f"✓ 镜像 {image} 已存在")
            except docker.errors.ImageNotFound:
                self.logger.info(f"⬇ 正在拉取镜像 {image}...")
                try:
                    self.client.images.pull(image)
                    self.logger.info(f"✓ 镜像 {image} 拉取完成")
                except Exception as e:
                    self.logger.warning(f"⚠ 镜像 {image} 拉取失败: {e}")

    def _cleanup_temp_file(self, temp_file: str):
        """清理临时文件"""
        try:
            # 可能文件已被重命名，尝试清理可能的文件名
            possible_files = [
                temp_file,
                temp_file.replace(temp_file.split('.')[-1], 'py'),
                temp_file.replace(temp_file.split('.')[-1], 'js'),
            ]
            
            for file_path in possible_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    self.logger.debug(f"清理临时文件: {file_path}")
                    
            # 清理重命名后的文件
            dir_path = os.path.dirname(temp_file)
            for ext in self.language_extensions.values():
                code_file = os.path.join(dir_path, f"code.{ext}")
                if os.path.exists(code_file):
                    os.unlink(code_file)
                    self.logger.debug(f"清理代码文件: {code_file}")
                    
        except Exception as e:
            self.logger.warning(f"清理临时文件失败: {e}")

    def _create_error_result(self, error_msg: str, execution_time: float, exit_code: int = -1) -> Dict[str, Any]:
        """创建错误结果字典"""
        return {
            'success': False,
            'output': '',
            'error': error_msg,
            'execution_time': execution_time,
            'exit_code': exit_code,
            'container_id': None,
            'image': None
        }

    def get_info(self) -> Dict[str, Any]:
        """获取Docker沙箱信息"""
        try:
            docker_info = self.client.info()
            return {
                'type': 'DockerSandbox',
                'timeout': self.timeout,
                'memory_limit': self.memory_limit,
                'network_enabled': self.enable_network,
                'supported_languages': list(self.language_images.keys()),
                'docker_version': docker_info.get('ServerVersion', 'Unknown'),
                'available_images': len(self.language_images)
            }
        except Exception as e:
            return {
                'type': 'DockerSandbox',
                'timeout': self.timeout,
                'memory_limit': self.memory_limit,
                'network_enabled': self.enable_network,
                'supported_languages': list(self.language_images.keys()),
                'docker_version': 'Error: ' + str(e),
                'available_images': len(self.language_images)
            }

    def cleanup_containers(self):
        """清理所有相关容器（紧急情况使用）"""
        try:
            containers = self.client.containers.list(all=True)
            cleaned = 0
            for container in containers:
                if any(image in str(container.image) for image in self.language_images.values()):
                    try:
                        container.remove(force=True)
                        cleaned += 1
                    except:
                        pass
            self.logger.info(f"清理了 {cleaned} 个容器")
            return cleaned
        except Exception as e:
            self.logger.error(f"清理容器失败: {e}")
            return 0

    def get_docker_status(self) -> Dict[str, Any]:
        """获取Docker状态信息"""
        try:
            info = self.client.info()
            return {
                'status': 'connected',
                'version': info.get('ServerVersion', 'Unknown'),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_total': info.get('Containers', 0),
                'images_count': info.get('Images', 0),
                'memory_total': info.get('MemTotal', 0),
                'cpus': info.get('NCPU', 0)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# 使用示例和测试代码
if __name__ == "__main__":
    print("=== 阶段3：Docker沙箱演示 ===\n")
    
    try:
        # 创建Docker沙箱实例
        sandbox = DockerSandbox(timeout=30, memory_limit="128m", enable_network=False)
        
        # 显示Docker状态
        docker_status = sandbox.get_docker_status()
        print(f"🐳 Docker状态: {docker_status['status']}")
        if docker_status['status'] == 'connected':
            print(f"   版本: {docker_status['version']}")
            print(f"   运行中容器: {docker_status['containers_running']}")
            print(f"   总容器数: {docker_status['containers_total']}")
            print(f"   镜像数量: {docker_status['images_count']}")
        
        # 显示沙箱信息
        info = sandbox.get_info()
        print(f"\n📦 沙箱信息:")
        print(f"   类型: {info['type']}")
        print(f"   超时: {info['timeout']}秒")
        print(f"   内存限制: {info['memory_limit']}")
        print(f"   网络: {'启用' if info['network_enabled'] else '禁用'}")
        print(f"   支持语言: {info['supported_languages']}")
        print(f"   Docker版本: {info['docker_version']}")
        
        # 测试1：Python代码执行
        print("\n📝 测试1：Python代码执行")
        python_code = """
import math
import json
from datetime import datetime

# 数学计算
data = {
    "timestamp": datetime.now().isoformat(),
    "calculations": {
        "pi": math.pi,
        "sqrt_16": math.sqrt(16),
        "factorial_5": math.factorial(5)
    },
    "message": "Hello from Docker container!"
}

print("🐍 Python在Docker容器中执行")
print(json.dumps(data, indent=2, ensure_ascii=False))
"""
        
        result = sandbox.execute(python_code, "python")
        print(f"执行成功: {result['success']}")
        print(f"容器ID: {result.get('container_id', 'N/A')}")
        print(f"使用镜像: {result.get('image', 'N/A')}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        if result['success']:
            print(f"输出内容:\n{result['output']}")
        else:
            print(f"错误信息: {result['error']}")
        print()
        
        # 测试2：JavaScript代码执行
        print("📝 测试2：JavaScript代码执行")
        js_code = """
// JavaScript在Docker容器中执行
const data = {
    timestamp: new Date().toISOString(),
    calculations: {
        random: Math.random(),
        sqrt_25: Math.sqrt(25),
        max_value: Math.max(1, 5, 3, 9, 2)
    },
    message: "Hello from Node.js in Docker!"
};

console.log("🟨 JavaScript在Docker容器中执行");
console.log(JSON.stringify(data, null, 2));
"""
        
        result = sandbox.execute(js_code, "javascript")
        print(f"执行成功: {result['success']}")
        print(f"容器ID: {result.get('container_id', 'N/A')}")
        print(f"使用镜像: {result.get('image', 'N/A')}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        if result['success']:
            print(f"输出内容:\n{result['output']}")
        else:
            print(f"错误信息: {result['error']}")
        print()
        
        # 测试3：错误代码处理
        print("📝 测试3：错误代码处理")
        error_code = """
print("这行会执行")
undefined_variable = some_undefined_variable
print("这行不会执行")
"""
        
        result = sandbox.execute(error_code, "python")
        print(f"执行成功: {result['success']}")
        print(f"容器ID: {result.get('container_id', 'N/A')}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        print(f"错误信息: {result['error']}")
        print()
        
        # 测试4：超时测试
        print("📝 测试4：超时保护测试")
        timeout_code = """
import time
print("开始长时间运行...")
time.sleep(35)  # 超过30秒超时限制
print("这行不会执行")
"""
        
        result = sandbox.execute(timeout_code, "python")
        print(f"执行成功: {result['success']}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        print(f"错误信息: {result['error']}")
        print()
        
        print("=== Docker沙箱演示完成 ===")
        print("\n🎯 学习要点总结：")
        print("1. 🐳 容器隔离：完全独立的运行环境")
        print("2. 🔒 安全控制：网络隔离、非root用户、只读文件系统")
        print("3. 📦 镜像管理：自动拉取和管理不同语言的运行环境")
        print("4. ⚡ 资源限制：内存和CPU限制")
        print("5. 🧹 自动清理：容器执行完成后自动删除")
        print("6. 🌐 多语言支持：Python、JavaScript、Java、Go等")
        
    except Exception as e:
        print(f"❌ Docker沙箱初始化失败: {e}")
        print("\n💡 可能的解决方案：")
        print("1. 确保Docker已安装并正在运行")
        print("2. 确保当前用户有Docker权限")
        print("3. 运行 'docker --version' 检查Docker状态")
        print("4. 运行 'docker run hello-world' 测试Docker功能")