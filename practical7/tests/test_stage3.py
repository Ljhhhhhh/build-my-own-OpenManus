"""
阶段3：Docker沙箱测试用例

测试DockerSandbox的容器隔离功能：
1. Docker连接和状态检查
2. 多语言代码执行
3. 容器隔离验证
4. 资源限制测试
5. 网络隔离测试
6. 安全控制测试

对于JavaScript开发者：
这类似于测试容器化应用或微服务的功能
"""

import pytest
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage3_docker_sandbox import DockerSandbox


class TestDockerSandbox:
    """DockerSandbox容器隔离功能测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        try:
            self.sandbox = DockerSandbox(timeout=10, memory_limit="64m", enable_network=False)
            self.docker_available = True
        except Exception as e:
            self.docker_available = False
            pytest.skip(f"Docker不可用，跳过测试: {e}")
    
    def test_docker_connection(self):
        """测试Docker连接"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        status = self.sandbox.get_docker_status()
        assert status['status'] == 'connected'
        assert 'version' in status
        assert isinstance(status['containers_total'], int)
        assert isinstance(status['images_count'], int)
    
    def test_sandbox_initialization(self):
        """测试Docker沙箱初始化"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        info = self.sandbox.get_info()
        assert info['type'] == 'DockerSandbox'
        assert info['timeout'] == 10
        assert info['memory_limit'] == "64m"
        assert info['network_enabled'] is False
        assert 'python' in info['supported_languages']
        assert 'javascript' in info['supported_languages']
    
    def test_python_code_execution(self):
        """测试Python代码在容器中执行"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        python_code = """
import math
print("Hello from Docker Python!")
result = math.sqrt(16)
print(f"sqrt(16) = {result}")
"""
        
        result = self.sandbox.execute(python_code, "python")
        
        assert result['success'] is True
        assert "Hello from Docker Python!" in result['output']
        assert "sqrt(16) = 4.0" in result['output']
        assert result['exit_code'] == 0
        assert result['container_id'] is not None
        assert result['image'] == 'python:3.9-slim'
        assert result['execution_time'] > 0
    
    def test_javascript_code_execution(self):
        """测试JavaScript代码在容器中执行"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        js_code = """
console.log("Hello from Docker Node.js!");
const result = Math.sqrt(25);
console.log(`sqrt(25) = ${result}`);
"""
        
        result = self.sandbox.execute(js_code, "javascript")
        
        assert result['success'] is True
        assert "Hello from Docker Node.js!" in result['output']
        assert "sqrt(25) = 5" in result['output']
        assert result['exit_code'] == 0
        assert result['container_id'] is not None
        assert result['image'] == 'node:18-alpine'
    
    def test_error_handling_in_container(self):
        """测试容器中的错误处理"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        error_code = """
print("Before error")
undefined_variable = some_undefined_variable
print("After error")
"""
        
        result = self.sandbox.execute(error_code, "python")
        
        assert result['success'] is False
        assert "Before error" in result['error']
        assert "NameError" in result['error']
        assert "some_undefined_variable" in result['error']
        assert result['exit_code'] != 0
        assert result['container_id'] is not None
    
    def test_timeout_protection(self):
        """测试容器超时保护"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 创建短超时的沙箱
        short_timeout_sandbox = DockerSandbox(timeout=3, memory_limit="64m")
        
        timeout_code = """
import time
print("Starting long operation...")
time.sleep(5)  # 超过3秒超时限制
print("This should not be printed")
"""
        
        result = short_timeout_sandbox.execute(timeout_code, "python")
        
        assert result['success'] is False
        assert "超时" in result['error']
        assert result['execution_time'] >= 3  # 应该接近超时时间
    
    def test_container_isolation(self):
        """测试容器隔离 - 多次执行互不影响"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 第一次执行 - 创建变量
        code1 = """
test_variable = "first_execution"
print(f"Variable: {test_variable}")
"""
        
        result1 = self.sandbox.execute(code1, "python")
        assert result1['success'] is True
        assert "Variable: first_execution" in result1['output']
        
        # 第二次执行 - 尝试访问前一次的变量（应该失败）
        code2 = """
try:
    print(f"Previous variable: {test_variable}")
except NameError:
    print("Variable not found - containers are isolated!")
"""
        
        result2 = self.sandbox.execute(code2, "python")
        assert result2['success'] is True
        assert "containers are isolated!" in result2['output']
    
    def test_file_system_isolation(self):
        """测试文件系统隔离"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 尝试写入文件到容器外部（应该失败或被限制）
        file_code = """
import tempfile
import os

# 在容器内创建临时文件
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("test content")
    temp_path = f.name

print(f"Created file: {temp_path}")

# 验证文件存在
if os.path.exists(temp_path):
    with open(temp_path, 'r') as f:
        content = f.read()
    print(f"File content: {content}")
    os.unlink(temp_path)
    print("File cleaned up")
else:
    print("File not found")
"""
        
        result = self.sandbox.execute(file_code, "python")
        assert result['success'] is True
        assert "Created file:" in result['output']
        assert "File content: test content" in result['output']
        assert "File cleaned up" in result['output']
    
    def test_unsupported_language(self):
        """测试不支持的语言"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        result = self.sandbox.execute("print('test')", "unsupported_lang")
        
        assert result['success'] is False
        assert "不支持的语言" in result['error']
        assert result['container_id'] is None
        assert result['image'] is None
    
    def test_empty_code_execution(self):
        """测试空代码执行"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        result = self.sandbox.execute("", "python")
        
        assert result['success'] is True
        assert result['output'] == ''
        assert result['exit_code'] == 0
    
    def test_unicode_support_in_container(self):
        """测试容器中的Unicode支持"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        unicode_code = """
print("你好，Docker世界！")
print("🐳 Docker容器测试")
print("Ελληνικά, Русский, العربية")
"""
        
        result = self.sandbox.execute(unicode_code, "python")
        
        assert result['success'] is True
        assert "你好，Docker世界！" in result['output']
        assert "🐳 Docker容器测试" in result['output']
    
    def test_memory_limit_configuration(self):
        """测试内存限制配置"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 创建不同内存限制的沙箱
        small_memory_sandbox = DockerSandbox(timeout=10, memory_limit="32m")
        
        info = small_memory_sandbox.get_info()
        assert info['memory_limit'] == "32m"
        
        # 测试基本功能仍然正常
        result = small_memory_sandbox.execute("print('Memory test')", "python")
        assert result['success'] is True
        assert "Memory test" in result['output']
    
    def test_network_isolation(self):
        """测试网络隔离"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 测试网络请求（应该失败，因为网络被禁用）
        network_code = """
import socket
import sys

try:
    # 尝试创建socket连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('google.com', 80))
    sock.close()
    
    if result == 0:
        print("Network connection successful")
    else:
        print("Network connection failed")
except Exception as e:
    print(f"Network error: {e}")
"""
        
        result = self.sandbox.execute(network_code, "python")
        
        # 网络应该被禁用，所以连接应该失败
        assert result['success'] is True
        assert ("Network connection failed" in result['output'] or 
                "Network error:" in result['output'])


class TestDockerSandboxAdvanced:
    """Docker沙箱高级功能测试"""
    
    def setup_method(self):
        """设置测试环境"""
        try:
            self.sandbox = DockerSandbox(timeout=15, memory_limit="128m", enable_network=False)
            self.docker_available = True
        except Exception:
            self.docker_available = False
            pytest.skip("Docker不可用")
    
    def test_multiple_language_support(self):
        """测试多语言支持"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # Python测试
        python_result = self.sandbox.execute('print("Python works!")', "python")
        assert python_result['success'] is True
        assert "Python works!" in python_result['output']
        
        # JavaScript测试
        js_result = self.sandbox.execute('console.log("JavaScript works!");', "javascript")
        assert js_result['success'] is True
        assert "JavaScript works!" in js_result['output']
    
    def test_container_cleanup(self):
        """测试容器清理功能"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 执行一些代码
        result = self.sandbox.execute("print('cleanup test')", "python")
        assert result['success'] is True
        
        # 检查容器是否被清理（通过Docker状态）
        status = self.sandbox.get_docker_status()
        # 由于容器设置为自动删除，运行中的容器数应该为0
        assert status['containers_running'] == 0
    
    def test_concurrent_execution_isolation(self):
        """测试并发执行的隔离性"""
        if not self.docker_available:
            pytest.skip("Docker不可用")
        
        # 创建多个沙箱实例
        sandbox1 = DockerSandbox(timeout=10, memory_limit="64m")
        sandbox2 = DockerSandbox(timeout=10, memory_limit="64m")
        
        # 并发执行不同的代码
        code1 = 'print("Sandbox 1 execution")'
        code2 = 'print("Sandbox 2 execution")'
        
        result1 = sandbox1.execute(code1, "python")
        result2 = sandbox2.execute(code2, "python")
        
        assert result1['success'] is True
        assert result2['success'] is True
        assert "Sandbox 1 execution" in result1['output']
        assert "Sandbox 2 execution" in result2['output']
        
        # 确保容器ID不同
        assert result1['container_id'] != result2['container_id']


if __name__ == "__main__":
    # 直接运行测试
    print("=== 运行阶段3 Docker沙箱测试 ===\n")
    
    # 检查Docker是否可用
    try:
        test_sandbox = DockerSandbox(timeout=5)
        docker_available = True
        print("✅ Docker连接成功")
    except Exception as e:
        docker_available = False
        print(f"❌ Docker不可用: {e}")
        print("\n💡 请确保：")
        print("1. Docker已安装并正在运行")
        print("2. 当前用户有Docker权限")
        print("3. 运行 'docker --version' 检查Docker状态")
        exit(1)
    
    # 创建测试实例
    test_instance = TestDockerSandbox()
    test_instance.setup_method()
    
    # 运行关键测试
    tests_to_run = [
        ("Docker连接测试", test_instance.test_docker_connection),
        ("沙箱初始化测试", test_instance.test_sandbox_initialization),
        ("Python代码执行测试", test_instance.test_python_code_execution),
        ("JavaScript代码执行测试", test_instance.test_javascript_code_execution),
        ("错误处理测试", test_instance.test_error_handling_in_container),
        ("容器隔离测试", test_instance.test_container_isolation),
        ("文件系统隔离测试", test_instance.test_file_system_isolation),
        ("Unicode支持测试", test_instance.test_unicode_support_in_container),
        ("网络隔离测试", test_instance.test_network_isolation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests_to_run:
        try:
            print(f"🧪 {test_name}...")
            test_func()
            print(f"✅ {test_name} - 通过")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} - 失败: {e}")
            failed += 1
        print()
    
    # 测试高级功能
    print("🧪 高级功能测试...")
    try:
        advanced_test = TestDockerSandboxAdvanced()
        advanced_test.setup_method()
        advanced_test.test_multiple_language_support()
        print("✅ 高级功能测试 - 通过")
        passed += 1
    except Exception as e:
        print(f"❌ 高级功能测试 - 失败: {e}")
        failed += 1
    print()
    
    print(f"=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！Docker沙箱功能正常。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查实现。")