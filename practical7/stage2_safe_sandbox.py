"""
阶段2：安全沙箱实现
目标：在基础沙箱上添加安全检查和资源限制

新增核心概念：
1. 代码安全检查：检测危险操作和恶意代码
2. 资源限制：限制内存使用和CPU时间
3. 黑名单过滤：阻止危险的导入和函数调用
4. 白名单机制：只允许安全的操作

对于JavaScript开发者的理解：
- 代码检查 ≈ ESLint的安全规则
- 资源限制 ≈ Node.js的--max-old-space-size
- 黑名单 ≈ 内容安全策略(CSP)的限制
"""

import re
import ast
import resource
import psutil
import os
from typing import Dict, Any, List, Set
from stage1_simple_sandbox import SimpleSandbox
from utils.logger import get_logger
from utils.config import get_config


class SafeSandbox(SimpleSandbox):
    """安全沙箱 - 在基础沙箱上添加安全控制
    
    这个类展示了如何在基础功能上添加安全层：
    1. 代码静态分析和安全检查
    2. 运行时资源限制
    3. 危险操作拦截
    4. 详细的安全日志记录
    """

    def __init__(self, timeout: int = None, memory_limit: int = None, enable_security: bool = True):
        """初始化安全沙箱
        
        Args:
            timeout: 执行超时时间（秒）
            memory_limit: 内存限制（MB）
            enable_security: 是否启用安全检查
        """
        super().__init__(timeout)
        
        self.memory_limit = memory_limit or get_config('memory_limit', 128)
        self.memory_limit_bytes = self.memory_limit * 1024 * 1024  # 转换为字节
        self.enable_security = enable_security
        
        # 更新日志记录器
        self.logger = get_logger("SafeSandbox")
        
        # 初始化安全配置
        self._init_security_config()
        
        self.logger.info(f"SafeSandbox初始化完成 - 超时: {self.timeout}秒, 内存限制: {self.memory_limit}MB")

    def _init_security_config(self):
        """初始化安全配置"""
        # 危险关键词 - 直接的危险操作
        self.dangerous_keywords = {
            # 系统操作
            'os.system', 'os.popen', 'os.spawn', 'os.exec',
            'subprocess.', 'commands.',
            
            # 文件系统操作
            'open(', 'file(', 'input(', 'raw_input(',
            
            # 动态执行
            'eval(', 'exec(', 'compile(',
            
            # 网络操作
            'socket.', 'urllib', 'requests.',
            
            # 进程操作
            'multiprocessing.', 'threading.',
            
            # 系统信息
            '__import__', 'globals()', 'locals()', 'vars()',
            
            # 危险模块
            'ctypes', 'pickle', 'marshal'
        }
        
        # 危险导入模块
        self.dangerous_imports = {
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'urllib2', 'urllib3',
            'requests', 'httplib', 'ftplib', 'smtplib', 'telnetlib',
            'multiprocessing', 'threading', 'thread', '_thread',
            'ctypes', 'pickle', 'marshal', 'shelve', 'dbm',
            'sqlite3', 'mysql', 'psycopg2',
            'webbrowser', 'platform', 'getpass'
        }
        
        # 允许的安全模块（白名单）
        self.safe_imports = {
            'math', 'random', 'datetime', 'time', 'calendar',
            'json', 'csv', 'base64', 'hashlib', 'hmac',
            'string', 're', 'collections', 'itertools', 'functools',
            'operator', 'copy', 'pprint', 'textwrap',
            'decimal', 'fractions', 'statistics',
            'tempfile'  # 允许临时文件操作
        }
        
        # 危险函数调用模式
        self.dangerous_patterns = [
            r'__.*__\(',  # 魔术方法调用
            r'getattr\(',  # 动态属性获取
            r'setattr\(',  # 动态属性设置
            r'delattr\(',  # 动态属性删除
            r'hasattr\(',  # 属性检查（可能用于探测）
        ]

    def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """安全执行代码
        
        执行流程：
        1. 代码安全检查（静态分析）
        2. 设置资源限制
        3. 执行代码（调用父类方法）
        4. 记录安全信息
        
        Args:
            code: 要执行的代码
            language: 编程语言
            
        Returns:
            包含执行结果和安全信息的字典
        """
        # 1. 代码安全检查
        if self.enable_security:
            security_result = self._validate_code_security(code, language)
            if not security_result['is_safe']:
                self.logger.log_security_check(code, False, security_result['reason'])
                return self._create_security_error_result(security_result['reason'])
            
            self.logger.log_security_check(code, True)
        
        # 2. 设置资源限制
        if self.enable_security:
            self._set_resource_limits()
        
        # 3. 执行代码（调用父类方法）
        result = super().execute(code, language)
        
        # 4. 添加安全信息到结果中
        result.update({
            'security_enabled': self.enable_security,
            'memory_limit_mb': self.memory_limit,
            'security_checks_passed': True if self.enable_security else None
        })
        
        return result

    def _validate_code_security(self, code: str, language: str) -> Dict[str, Any]:
        """验证代码安全性
        
        Args:
            code: 要检查的代码
            language: 编程语言
            
        Returns:
            安全检查结果字典
        """
        if language != 'python':
            # 目前只支持Python的安全检查
            return {'is_safe': True, 'reason': ''}
        
        # 1. 检查危险关键词
        keyword_result = self._check_dangerous_keywords(code)
        if not keyword_result['is_safe']:
            return keyword_result
        
        # 2. 检查危险导入
        import_result = self._check_dangerous_imports(code)
        if not import_result['is_safe']:
            return import_result
        
        # 3. 检查危险模式
        pattern_result = self._check_dangerous_patterns(code)
        if not pattern_result['is_safe']:
            return pattern_result
        
        # 4. AST语法树分析（更深层的检查）
        ast_result = self._check_ast_security(code)
        if not ast_result['is_safe']:
            return ast_result
        
        return {'is_safe': True, 'reason': ''}

    def _check_dangerous_keywords(self, code: str) -> Dict[str, Any]:
        """检查危险关键词"""
        for keyword in self.dangerous_keywords:
            if keyword in code:
                return {
                    'is_safe': False,
                    'reason': f'代码包含危险关键词: {keyword}'
                }
        return {'is_safe': True, 'reason': ''}

    def _check_dangerous_imports(self, code: str) -> Dict[str, Any]:
        """检查危险导入"""
        # 检查 import module 语句
        import_pattern = r'import\s+(\w+)'
        matches = re.findall(import_pattern, code)
        for module in matches:
            if module in self.dangerous_imports:
                return {
                    'is_safe': False,
                    'reason': f'代码尝试导入危险模块: {module}'
                }
            # 检查是否在安全模块白名单中
            if module not in self.safe_imports and module not in ['builtins']:
                return {
                    'is_safe': False,
                    'reason': f'代码尝试导入危险模块: {module}'
                }
        
        # 检查 from module import 语句
        from_import_pattern = r'from\s+(\w+)\s+import'
        matches = re.findall(from_import_pattern, code)
        for module in matches:
            if module in self.dangerous_imports:
                return {
                    'is_safe': False,
                    'reason': f'代码尝试导入危险模块: {module}'
                }
            # 对于from import，只检查模块本身是否安全
            if module not in self.safe_imports and module not in ['builtins']:
                return {
                    'is_safe': False,
                    'reason': f'代码尝试导入危险模块: {module}'
                }
        
        return {'is_safe': True, 'reason': ''}

    def _check_dangerous_patterns(self, code: str) -> Dict[str, Any]:
        """检查危险模式"""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code):
                return {
                    'is_safe': False,
                    'reason': f'代码包含危险模式: {pattern}'
                }
        return {'is_safe': True, 'reason': ''}

    def _check_ast_security(self, code: str) -> Dict[str, Any]:
        """使用AST进行深层安全检查"""
        try:
            tree = ast.parse(code)
            
            # 检查AST节点
            for node in ast.walk(tree):
                # 检查函数调用
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in ['eval', 'exec', 'compile', '__import__']:
                            return {
                                'is_safe': False,
                                'reason': f'代码包含危险函数调用: {func_name}'
                            }
                
                # 检查属性访问
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id == 'os' and node.attr in ['system', 'popen']:
                            return {
                                'is_safe': False,
                                'reason': f'代码尝试访问危险属性: os.{node.attr}'
                            }
                
                # 检查全局变量访问
                if isinstance(node, ast.Global):
                    return {
                        'is_safe': False,
                        'reason': '代码尝试修改全局变量'
                    }
            
            return {'is_safe': True, 'reason': ''}
            
        except SyntaxError:
            # 语法错误会在执行时被捕获，这里不需要特殊处理
            return {'is_safe': True, 'reason': ''}
        except Exception as e:
            self.logger.warning(f"AST安全检查异常: {e}")
            return {'is_safe': True, 'reason': ''}

    def _set_resource_limits(self):
        """设置进程资源限制
        
        注意：资源限制在某些系统上可能不完全生效
        """
        try:
            # 设置内存限制（虚拟内存）
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit_bytes, self.memory_limit_bytes))
            
            # 设置CPU时间限制
            resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
            
            # 设置文件描述符限制
            resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
            
            self.logger.debug(f"资源限制设置完成 - 内存: {self.memory_limit}MB, CPU: {self.timeout}秒")
            
        except Exception as e:
            # 某些系统可能不支持资源限制
            self.logger.warning(f"设置资源限制失败: {e}")

    def _create_security_error_result(self, reason: str) -> Dict[str, Any]:
        """创建安全错误结果"""
        return {
            'success': False,
            'output': '',
            'error': f'安全检查失败: {reason}',
            'execution_time': 0,
            'exit_code': -100,  # 特殊退出码表示安全错误
            'security_enabled': True,
            'security_checks_passed': False,
            'security_error': reason
        }

    def get_security_info(self) -> Dict[str, Any]:
        """获取安全配置信息"""
        return {
            'security_enabled': self.enable_security,
            'memory_limit_mb': self.memory_limit,
            'dangerous_keywords_count': len(self.dangerous_keywords),
            'dangerous_imports_count': len(self.dangerous_imports),
            'safe_imports_count': len(self.safe_imports),
            'dangerous_patterns_count': len(self.dangerous_patterns)
        }

    def get_info(self) -> Dict[str, Any]:
        """获取沙箱信息（覆盖父类方法）"""
        base_info = super().get_info()
        base_info.update({
            'type': 'SafeSandbox',
            'memory_limit_mb': self.memory_limit,
            'security_enabled': self.enable_security
        })
        return base_info


# 使用示例和测试代码
if __name__ == "__main__":
    print("=== 阶段2：安全沙箱演示 ===\n")
    
    # 创建安全沙箱实例
    sandbox = SafeSandbox(timeout=10, memory_limit=64, enable_security=True)
    
    # 显示沙箱信息
    info = sandbox.get_info()
    security_info = sandbox.get_security_info()
    
    print(f"沙箱类型: {info['type']}")
    print(f"超时设置: {info['timeout']}秒")
    print(f"内存限制: {info['memory_limit_mb']}MB")
    print(f"安全检查: {'启用' if info['security_enabled'] else '禁用'}")
    print(f"危险关键词数量: {security_info['dangerous_keywords_count']}")
    print(f"危险模块数量: {security_info['dangerous_imports_count']}")
    print(f"安全模块数量: {security_info['safe_imports_count']}\n")
    
    # 测试1：安全的Python代码
    print("📝 测试1：安全的Python代码")
    safe_code = """
import math
import random

# 数学计算
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
average = total / len(numbers)

print(f"数字列表: {numbers}")
print(f"总和: {total}")
print(f"平均值: {average}")

# 使用安全的模块
pi_value = math.pi
random_number = random.randint(1, 100)

print(f"π的值: {pi_value}")
print(f"随机数: {random_number}")
"""
    
    result = sandbox.execute(safe_code, "python")
    print(f"执行成功: {result['success']}")
    print(f"安全检查通过: {result['security_checks_passed']}")
    print(f"执行时间: {result['execution_time']:.3f}秒")
    if result['success']:
        print(f"输出内容:\n{result['output']}")
    else:
        print(f"错误信息: {result['error']}")
    print()
    
    # 测试2：包含危险关键词的代码
    print("📝 测试2：包含危险关键词的代码")
    dangerous_code1 = """
import os
print("尝试执行系统命令")
os.system("ls -la")  # 危险操作
"""
    
    result = sandbox.execute(dangerous_code1, "python")
    print(f"执行成功: {result['success']}")
    print(f"安全检查通过: {result['security_checks_passed']}")
    print(f"错误信息: {result['error']}")
    print()
    
    # 测试3：尝试导入危险模块
    print("📝 测试3：尝试导入危险模块")
    dangerous_code2 = """
import subprocess
print("尝试使用subprocess")
subprocess.run(["echo", "hello"])
"""
    
    result = sandbox.execute(dangerous_code2, "python")
    print(f"执行成功: {result['success']}")
    print(f"安全检查通过: {result['security_checks_passed']}")
    print(f"错误信息: {result['error']}")
    print()
    
    # 测试4：尝试使用eval函数
    print("📝 测试4：尝试使用eval函数")
    dangerous_code3 = """
user_input = "print('Hello from eval')"
eval(user_input)  # 危险的动态执行
"""
    
    result = sandbox.execute(dangerous_code3, "python")
    print(f"执行成功: {result['success']}")
    print(f"安全检查通过: {result['security_checks_passed']}")
    print(f"错误信息: {result['error']}")
    print()
    
    # 测试5：测试禁用安全检查的情况
    print("📝 测试5：禁用安全检查")
    unsafe_sandbox = SafeSandbox(timeout=5, enable_security=False)
    
    result = unsafe_sandbox.execute(safe_code, "python")
    print(f"执行成功: {result['success']}")
    print(f"安全检查: {'启用' if result['security_enabled'] else '禁用'}")
    print(f"执行时间: {result['execution_time']:.3f}秒")
    print()
    
    print("=== 安全沙箱演示完成 ===")
    print("\n🎯 学习要点总结：")
    print("1. 代码安全检查：静态分析检测危险操作")
    print("2. 模块导入控制：黑名单+白名单机制")
    print("3. 资源限制：内存和CPU时间限制")
    print("4. AST分析：深层语法树安全检查")
    print("5. 灵活配置：可以启用/禁用安全功能")
    print("6. 详细日志：记录所有安全检查过程")