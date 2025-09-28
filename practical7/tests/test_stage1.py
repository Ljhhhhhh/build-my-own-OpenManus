"""
阶段1：基础沙箱测试用例

使用pytest框架测试SimpleSandbox的各项功能：
1. 基本代码执行
2. 错误处理
3. 超时保护
4. 多语言支持
5. 边界条件测试

对于JavaScript开发者：
这类似于使用Jest或Mocha编写的单元测试
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage1_simple_sandbox import SimpleSandbox


class TestSimpleSandbox:
    """SimpleSandbox测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.sandbox = SimpleSandbox(timeout=5)
    
    def test_sandbox_initialization(self):
        """测试沙箱初始化"""
        assert self.sandbox.timeout == 5
        assert 'python' in self.sandbox.supported_languages
        assert self.sandbox.language_extensions['python'] == 'py'
        assert self.sandbox.language_commands['python'] == 'python'
    
    def test_simple_python_execution(self):
        """测试简单Python代码执行"""
        code = """
print("Hello World")
result = 1 + 1
print(f"1 + 1 = {result}")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert "Hello World" in result['output']
        assert "1 + 1 = 2" in result['output']
        assert result['exit_code'] == 0
        assert result['execution_time'] > 0
        assert result['error'] == ''
    
    def test_python_with_error(self):
        """测试包含错误的Python代码"""
        code = """
print("Before error")
undefined_variable = some_undefined_variable
print("After error")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is False
        assert "Before error" in result['output']
        assert "NameError" in result['error']
        assert "some_undefined_variable" in result['error']
        assert result['exit_code'] != 0
    
    def test_timeout_protection(self):
        """测试超时保护功能"""
        code = """
import time
print("Starting long operation...")
time.sleep(10)  # 超过5秒超时限制
print("This should not be printed")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is False
        assert "超时" in result['error']
        assert result['exit_code'] == -1
        assert result['execution_time'] >= 5  # 应该接近超时时间
    
    def test_empty_code(self):
        """测试空代码"""
        result = self.sandbox.execute("", "python")
        
        assert result['success'] is True
        assert result['output'] == ''
        assert result['error'] == ''
        assert result['exit_code'] == 0
    
    def test_code_with_only_comments(self):
        """测试只有注释的代码"""
        code = """
# This is a comment
# Another comment
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert result['output'] == ''
        assert result['error'] == ''
        assert result['exit_code'] == 0
    
    def test_multiline_output(self):
        """测试多行输出"""
        code = """
for i in range(3):
    print(f"Line {i + 1}")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert "Line 1" in result['output']
        assert "Line 2" in result['output']
        assert "Line 3" in result['output']
    
    def test_unsupported_language(self):
        """测试不支持的语言"""
        result = self.sandbox.execute("console.log('test')", "unsupported_lang")
        
        assert result['success'] is False
        assert "不支持的语言" in result['error']
        assert result['exit_code'] == -1
    
    def test_syntax_error(self):
        """测试语法错误"""
        code = """
print("Missing closing quote
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is False
        assert "SyntaxError" in result['error'] or "EOL" in result['error']
        assert result['exit_code'] != 0
    
    def test_import_and_calculation(self):
        """测试导入模块和计算"""
        code = """
import math
print(f"π = {math.pi}")
print(f"sqrt(16) = {math.sqrt(16)}")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert "π = 3.14" in result['output']
        assert "sqrt(16) = 4.0" in result['output']
    
    def test_get_info(self):
        """测试获取沙箱信息"""
        info = self.sandbox.get_info()
        
        assert info['type'] == 'SimpleSandbox'
        assert info['timeout'] == 5
        assert 'python' in info['supported_languages']
        assert 'python' in info['language_commands']
    
    def test_unicode_support(self):
        """测试Unicode字符支持"""
        code = """
print("你好，世界！")
print("🐍 Python沙箱测试")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert "你好，世界！" in result['output']
        assert "🐍 Python沙箱测试" in result['output']
    
    def test_large_output(self):
        """测试大量输出"""
        code = """
for i in range(100):
    print(f"Output line {i}")
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert "Output line 0" in result['output']
        assert "Output line 99" in result['output']
    
    def test_stderr_capture(self):
        """测试标准错误捕获"""
        code = """
import sys
print("This goes to stdout")
print("This goes to stderr", file=sys.stderr)
"""
        result = self.sandbox.execute(code, "python")
        
        assert result['success'] is True
        assert "This goes to stdout" in result['output']
        assert "This goes to stderr" in result['error']


class TestSandboxEdgeCases:
    """沙箱边界条件测试"""
    
    def test_very_short_timeout(self):
        """测试极短超时时间"""
        sandbox = SimpleSandbox(timeout=1)
        code = """
import time
time.sleep(2)
"""
        result = sandbox.execute(code, "python")
        
        assert result['success'] is False
        assert "超时" in result['error']
    
    def test_zero_timeout(self):
        """测试零超时时间"""
        sandbox = SimpleSandbox(timeout=0)
        # 即使超时为0，简单代码也应该能执行
        result = sandbox.execute("print('quick')", "python")
        
        # 这个测试的结果可能因系统而异
        # 主要是验证不会崩溃
        assert 'success' in result
        assert 'execution_time' in result
    
    def test_negative_timeout(self):
        """测试负数超时时间"""
        # 应该使用默认值或处理异常
        sandbox = SimpleSandbox(timeout=-1)
        result = sandbox.execute("print('test')", "python")
        
        # 验证不会崩溃
        assert 'success' in result


if __name__ == "__main__":
    # 直接运行测试
    print("=== 运行阶段1基础沙箱测试 ===\n")
    
    # 创建测试实例
    test_instance = TestSimpleSandbox()
    test_instance.setup_method()
    
    # 运行一些关键测试
    tests_to_run = [
        ("基本功能测试", test_instance.test_simple_python_execution),
        ("错误处理测试", test_instance.test_python_with_error),
        ("超时保护测试", test_instance.test_timeout_protection),
        ("Unicode支持测试", test_instance.test_unicode_support),
        ("沙箱信息测试", test_instance.test_get_info),
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
    
    print(f"=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！基础沙箱功能正常。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查实现。")