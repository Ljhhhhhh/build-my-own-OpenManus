"""
阶段2：安全沙箱测试用例

测试SafeSandbox的安全功能：
1. 代码安全检查
2. 危险关键词检测
3. 危险模块导入检测
4. AST语法树分析
5. 资源限制功能
6. 安全配置管理

对于JavaScript开发者：
这类似于测试安全中间件或内容安全策略(CSP)的功能
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage2_safe_sandbox import SafeSandbox


class TestSafeSandbox:
    """SafeSandbox安全功能测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.sandbox = SafeSandbox(timeout=5, memory_limit=64, enable_security=True)
        self.unsafe_sandbox = SafeSandbox(timeout=5, enable_security=False)
    
    def test_sandbox_initialization(self):
        """测试安全沙箱初始化"""
        assert self.sandbox.timeout == 5
        assert self.sandbox.memory_limit == 64
        assert self.sandbox.enable_security is True
        
        info = self.sandbox.get_info()
        assert info['type'] == 'SafeSandbox'
        assert info['memory_limit_mb'] == 64
        assert info['security_enabled'] is True
    
    def test_safe_code_execution(self):
        """测试安全代码执行"""
        safe_code = """
import math
import random

# 基本计算
result = math.sqrt(16)
random_num = random.randint(1, 10)

print(f"平方根: {result}")
print(f"随机数: {random_num}")
"""
        result = self.sandbox.execute(safe_code, "python")
        
        assert result['success'] is True
        assert result['security_enabled'] is True
        assert result['security_checks_passed'] is True
        assert "平方根: 4.0" in result['output']
        assert result['exit_code'] == 0
    
    def test_dangerous_keyword_detection(self):
        """测试危险关键词检测"""
        dangerous_codes = [
            "import os; os.system('ls')",
            "eval('print(1)')",
            "exec('x = 1')",
            "subprocess.run(['ls'])",
            "__import__('os')"
        ]
        
        for code in dangerous_codes:
            result = self.sandbox.execute(code, "python")
            assert result['success'] is False
            assert result['security_checks_passed'] is False
            assert result['exit_code'] == -100  # 安全错误退出码
            assert "安全检查失败" in result['error']
    
    def test_dangerous_import_detection(self):
        """测试危险模块导入检测"""
        dangerous_imports = [
            "import os",
            "import sys", 
            "import subprocess",
            "import socket",
            "from os import system",
            "from subprocess import run"
        ]
        
        for code in dangerous_imports:
            result = self.sandbox.execute(code, "python")
            assert result['success'] is False
            assert result['security_checks_passed'] is False
            assert "危险模块" in result['error'] or "危险关键词" in result['error']
    
    def test_safe_import_whitelist(self):
        """测试安全模块白名单"""
        safe_imports = [
            "import math",
            "import random", 
            "import datetime",
            "import json",
            "from math import sqrt",
            "from datetime import datetime"
        ]
        
        for code in safe_imports:
            result = self.sandbox.execute(code, "python")
            assert result['success'] is True
            assert result['security_checks_passed'] is True
    
    def test_unauthorized_module_detection(self):
        """测试未授权模块检测"""
        # 尝试导入不在白名单中的模块
        unauthorized_code = "import unknown_module"
        result = self.sandbox.execute(unauthorized_code, "python")
        
        # 这应该被安全检查拦截
        assert result['success'] is False
        assert "未授权模块" in result['error']
    
    def test_ast_security_analysis(self):
        """测试AST语法树安全分析"""
        # 测试全局变量修改
        global_code = """
global x
x = 10
"""
        result = self.sandbox.execute(global_code, "python")
        assert result['success'] is False
        assert "全局变量" in result['error']
    
    def test_security_disabled_mode(self):
        """测试禁用安全检查模式"""
        # 在禁用安全检查的沙箱中执行危险代码
        dangerous_code = """
print("This would be dangerous if security was enabled")
# 注意：我们不能真的执行危险代码，因为会影响系统
"""
        
        result = self.unsafe_sandbox.execute(dangerous_code, "python")
        assert result['success'] is True
        assert result['security_enabled'] is False
        assert result['security_checks_passed'] is None
    
    def test_syntax_error_handling(self):
        """测试语法错误处理"""
        syntax_error_code = """
print("Missing closing quote
"""
        result = self.sandbox.execute(syntax_error_code, "python")
        
        # 语法错误应该通过安全检查，但在执行时失败
        assert result['success'] is False
        assert result['security_checks_passed'] is True
        assert "SyntaxError" in result['error'] or "EOL" in result['error']
    
    def test_empty_code_security(self):
        """测试空代码的安全检查"""
        result = self.sandbox.execute("", "python")
        
        assert result['success'] is True
        assert result['security_checks_passed'] is True
        assert result['output'] == ''
    
    def test_comment_only_code(self):
        """测试只有注释的代码"""
        comment_code = """
# This is just a comment
# Another comment
"""
        result = self.sandbox.execute(comment_code, "python")
        
        assert result['success'] is True
        assert result['security_checks_passed'] is True
        assert result['output'] == ''
    
    def test_complex_safe_code(self):
        """测试复杂但安全的代码"""
        complex_code = """
import math
import json
from datetime import datetime

# 数据处理
data = {
    "numbers": [1, 2, 3, 4, 5],
    "timestamp": str(datetime.now()),
    "calculations": {}
}

# 数学计算
for num in data["numbers"]:
    data["calculations"][f"sqrt_{num}"] = math.sqrt(num)
    data["calculations"][f"square_{num}"] = num ** 2

# JSON序列化
json_output = json.dumps(data, indent=2)
print("处理结果:")
print(json_output)
"""
        
        result = self.sandbox.execute(complex_code, "python")
        assert result['success'] is True
        assert result['security_checks_passed'] is True
        assert "处理结果:" in result['output']
        assert "sqrt_" in result['output']
    
    def test_security_info_retrieval(self):
        """测试安全信息获取"""
        security_info = self.sandbox.get_security_info()
        
        assert security_info['security_enabled'] is True
        assert security_info['memory_limit_mb'] == 64
        assert security_info['dangerous_keywords_count'] > 0
        assert security_info['dangerous_imports_count'] > 0
        assert security_info['safe_imports_count'] > 0
    
    def test_multiple_security_violations(self):
        """测试多重安全违规"""
        # 包含多个安全问题的代码
        multi_violation_code = """
import os
import subprocess
eval("print('test')")
os.system("echo hello")
"""
        
        result = self.sandbox.execute(multi_violation_code, "python")
        assert result['success'] is False
        assert result['security_checks_passed'] is False
        # 应该检测到第一个违规就停止
        assert "危险" in result['error']


class TestSandboxResourceLimits:
    """沙箱资源限制测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.sandbox = SafeSandbox(timeout=3, memory_limit=32, enable_security=True)
    
    def test_timeout_with_security(self):
        """测试带安全检查的超时保护"""
        timeout_code = """
import time
print("开始长时间运行...")
time.sleep(5)  # 超过3秒超时限制
print("这行不会执行")
"""
        
        result = self.sandbox.execute(timeout_code, "python")
        assert result['success'] is False
        assert "超时" in result['error']
        assert result['execution_time'] >= 3
    
    def test_memory_limit_info(self):
        """测试内存限制信息"""
        info = self.sandbox.get_info()
        assert info['memory_limit_mb'] == 32
        
        security_info = self.sandbox.get_security_info()
        assert security_info['memory_limit_mb'] == 32


class TestSandboxEdgeCases:
    """沙箱边界条件测试"""
    
    def test_unicode_in_dangerous_code(self):
        """测试包含Unicode字符的危险代码"""
        sandbox = SafeSandbox(enable_security=True)
        
        unicode_dangerous_code = """
# 这是中文注释
import os  # 危险导入
print("你好世界")
"""
        
        result = sandbox.execute(unicode_dangerous_code, "python")
        assert result['success'] is False
        assert "危险模块" in result['error']
    
    def test_case_sensitivity_security(self):
        """测试安全检查的大小写敏感性"""
        sandbox = SafeSandbox(enable_security=True)
        
        # 当前实现是大小写敏感的，这是正确的
        case_code = "import OS"  # 大写的OS
        result = sandbox.execute(case_code, "python")
        
        # 应该被检测为未授权模块
        assert result['success'] is False
    
    def test_whitespace_in_dangerous_code(self):
        """测试危险代码中的空白字符"""
        sandbox = SafeSandbox(enable_security=True)
        
        whitespace_code = "import   os"  # 多个空格
        result = sandbox.execute(whitespace_code, "python")
        
        assert result['success'] is False
        assert "危险模块" in result['error']


if __name__ == "__main__":
    # 直接运行测试
    print("=== 运行阶段2安全沙箱测试 ===\n")
    
    # 创建测试实例
    test_instance = TestSafeSandbox()
    test_instance.setup_method()
    
    # 运行关键测试
    tests_to_run = [
        ("沙箱初始化测试", test_instance.test_sandbox_initialization),
        ("安全代码执行测试", test_instance.test_safe_code_execution),
        ("危险关键词检测测试", test_instance.test_dangerous_keyword_detection),
        ("危险模块导入检测测试", test_instance.test_dangerous_import_detection),
        ("安全模块白名单测试", test_instance.test_safe_import_whitelist),
        ("复杂安全代码测试", test_instance.test_complex_safe_code),
        ("安全信息获取测试", test_instance.test_security_info_retrieval),
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
    
    # 测试资源限制
    print("🧪 资源限制测试...")
    try:
        resource_test = TestSandboxResourceLimits()
        resource_test.setup_method()
        resource_test.test_memory_limit_info()
        print("✅ 资源限制测试 - 通过")
        passed += 1
    except Exception as e:
        print(f"❌ 资源限制测试 - 失败: {e}")
        failed += 1
    print()
    
    print(f"=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！安全沙箱功能正常。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查实现。")