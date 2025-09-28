"""
阶段1：基础沙箱实现
目标：理解沙箱的本质 - 进程隔离和输入输出控制

核心概念学习：
1. 进程隔离：使用subprocess创建独立进程
2. 输入输出控制：捕获程序的输出和错误
3. 超时保护：防止无限循环或长时间运行
4. 资源清理：确保临时文件被正确删除

对于JavaScript开发者的理解：
- subprocess.run() ≈ child_process.spawn() 
- 临时文件 ≈ fs.writeFileSync() + fs.unlinkSync()
- 超时控制 ≈ setTimeout() + process.kill()
"""

import subprocess
import tempfile
import os
import time
from typing import Dict, Any
from utils.logger import get_logger
from utils.config import get_config


class SimpleSandbox:
    """最简单的沙箱实现 - 30行核心代码
    
    这个类展示了沙箱的基本原理：
    1. 将代码写入临时文件
    2. 使用subprocess在独立进程中执行
    3. 捕获输出和错误信息
    4. 清理临时资源
    """

    def __init__(self, timeout: int = None):
        """初始化基础沙箱
        
        Args:
            timeout: 执行超时时间（秒），默认从配置读取
        """
        self.timeout = timeout or get_config('timeout', 10)
        self.logger = get_logger("SimpleSandbox")
        
        # 支持的语言配置
        self.supported_languages = get_config('supported_languages', ['python', 'javascript'])
        self.language_extensions = get_config('language_extensions', {
            'python': 'py',
            'javascript': 'js'
        })
        self.language_commands = get_config('language_commands', {
            'python': 'python',
            'javascript': 'node'
        })
        
        self.logger.info(f"SimpleSandbox初始化完成 - 超时: {self.timeout}秒")

    def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """执行代码并返回结果
        
        这是沙箱的核心方法，展示了代码执行的完整流程：
        
        Args:
            code: 要执行的代码字符串
            language: 编程语言类型
            
        Returns:
            包含执行结果的字典：
            - success: 是否执行成功
            - output: 标准输出
            - error: 错误信息
            - execution_time: 执行时间
            - exit_code: 退出码
        """
        start_time = time.time()
        
        # 验证语言支持
        if language not in self.supported_languages:
            error_msg = f"不支持的语言: {language}，支持的语言: {self.supported_languages}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg, 0)

        # 1. 创建临时文件 - 类似JavaScript中的fs.writeFileSync()
        temp_file = self._create_temp_file(code, language)
        
        try:
            # 2. 执行代码 - 类似JavaScript中的child_process.spawn()
            result = self._execute_in_subprocess(temp_file, language)
            
            # 3. 计算执行时间并返回结果
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            
            # 记录执行日志
            self.logger.log_execution("SimpleSandbox", code[:50] + "...", result)
            
            return result

        finally:
            # 4. 清理临时文件 - 确保资源释放
            self._cleanup_temp_file(temp_file)

    def _create_temp_file(self, code: str, language: str) -> str:
        """创建临时文件
        
        Args:
            code: 代码内容
            language: 编程语言
            
        Returns:
            临时文件路径
        """
        extension = self.language_extensions.get(language, 'txt')
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{extension}',
            delete=False,  # 不自动删除，手动控制
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_file = f.name
        
        self.logger.debug(f"创建临时文件: {temp_file}")
        return temp_file

    def _execute_in_subprocess(self, temp_file: str, language: str) -> Dict[str, Any]:
        """在子进程中执行代码
        
        Args:
            temp_file: 临时文件路径
            language: 编程语言
            
        Returns:
            执行结果字典
        """
        command = self.language_commands.get(language)
        if not command:
            return self._create_error_result(f"未找到语言 {language} 的执行命令", 0)

        try:
            # 执行命令 - 核心的30行代码就在这里！
            result = subprocess.run(
                [command, temp_file],
                capture_output=True,    # 捕获输出和错误
                text=True,             # 以文本模式处理输出
                timeout=self.timeout,  # 设置超时
                encoding='utf-8'       # 指定编码
            )

            # 返回执行结果
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'exit_code': result.returncode,
                'command': f"{command} {os.path.basename(temp_file)}"
            }

        except subprocess.TimeoutExpired:
            # 处理超时情况
            error_msg = f'代码执行超时（{self.timeout}秒）'
            self.logger.warning(error_msg)
            return self._create_error_result(error_msg, self.timeout, exit_code=-1)
            
        except FileNotFoundError:
            # 处理命令不存在的情况
            error_msg = f'未找到执行命令: {command}，请确保已安装相应的运行环境'
            self.logger.error(error_msg)
            return self._create_error_result(error_msg, 0, exit_code=-2)
            
        except Exception as e:
            # 处理其他异常
            error_msg = f'执行过程中发生异常: {str(e)}'
            self.logger.error(error_msg)
            return self._create_error_result(error_msg, 0, exit_code=-3)

    def _cleanup_temp_file(self, temp_file: str) -> None:
        """清理临时文件
        
        Args:
            temp_file: 临时文件路径
        """
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                self.logger.debug(f"清理临时文件: {temp_file}")
        except Exception as e:
            self.logger.warning(f"清理临时文件失败: {e}")

    def _create_error_result(self, error_msg: str, execution_time: float, exit_code: int = -1) -> Dict[str, Any]:
        """创建错误结果字典
        
        Args:
            error_msg: 错误信息
            execution_time: 执行时间
            exit_code: 退出码
            
        Returns:
            错误结果字典
        """
        return {
            'success': False,
            'output': '',
            'error': error_msg,
            'execution_time': execution_time,
            'exit_code': exit_code
        }

    def get_info(self) -> Dict[str, Any]:
        """获取沙箱信息
        
        Returns:
            沙箱配置信息
        """
        return {
            'type': 'SimpleSandbox',
            'timeout': self.timeout,
            'supported_languages': self.supported_languages,
            'language_commands': self.language_commands
        }


# 使用示例和测试代码
if __name__ == "__main__":
    print("=== 阶段1：基础沙箱演示 ===\n")
    
    # 创建沙箱实例
    sandbox = SimpleSandbox(timeout=5)
    
    # 显示沙箱信息
    info = sandbox.get_info()
    print(f"沙箱类型: {info['type']}")
    print(f"超时设置: {info['timeout']}秒")
    print(f"支持语言: {info['supported_languages']}\n")
    
    # 测试1：简单的Python代码
    print("📝 测试1：简单Python代码")
    python_code = """
print("Hello from SimpleSandbox!")
result = 2 + 3
print(f"计算结果: 2 + 3 = {result}")

# 测试循环
for i in range(3):
    print(f"循环 {i + 1}")
"""
    
    result = sandbox.execute(python_code, "python")
    print(f"执行成功: {result['success']}")
    print(f"执行时间: {result['execution_time']:.3f}秒")
    print(f"输出内容:\n{result['output']}")
    if result['error']:
        print(f"错误信息: {result['error']}")
    print()
    
    # 测试2：有错误的Python代码
    print("📝 测试2：包含错误的Python代码")
    error_code = """
print("这行代码正常")
undefined_variable = some_undefined_variable  # 这里会出错
print("这行不会执行")
"""
    
    result = sandbox.execute(error_code, "python")
    print(f"执行成功: {result['success']}")
    print(f"执行时间: {result['execution_time']:.3f}秒")
    print(f"输出内容: {result['output']}")
    print(f"错误信息: {result['error']}")
    print()
    
    # 测试3：超时测试（如果系统支持）
    print("📝 测试3：超时保护测试")
    timeout_code = """
import time
print("开始长时间运行...")
time.sleep(10)  # 睡眠10秒，会触发超时
print("这行不会执行")
"""
    
    result = sandbox.execute(timeout_code, "python")
    print(f"执行成功: {result['success']}")
    print(f"执行时间: {result['execution_time']:.3f}秒")
    print(f"错误信息: {result['error']}")
    print()
    
    print("=== 基础沙箱演示完成 ===")
    print("\n🎯 学习要点总结：")
    print("1. 进程隔离：每次执行都在独立的进程中")
    print("2. 输入输出控制：可以捕获程序的所有输出")
    print("3. 超时保护：防止程序无限运行")
    print("4. 错误处理：能够区分正常输出和错误信息")
    print("5. 资源清理：自动清理临时文件")