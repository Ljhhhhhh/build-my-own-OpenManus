"""
Practical 3.2 - 测试包

这个包包含了异步工具框架的测试用例，展示了：
1. 异步测试的编写方法
2. 模拟和存根的使用
3. 测试覆盖率的考虑
4. 集成测试的实现

学习要点：
1. pytest-asyncio的使用
2. 异步测试的最佳实践
3. 模拟外部依赖的方法
4. 测试数据的管理
"""

__version__ = "1.0.0"
__author__ = "Practical 3.2 Team"

# 导出测试工具
from .test_base import *
from .test_calculator import *
from .test_weather import *
from .test_manager import *

__all__ = [
    "test_base",
    "test_calculator", 
    "test_weather",
    "test_manager"
]