"""
基础使用示例

展示如何使用SimpleSandbox执行各种类型的代码，
包括数学计算、字符串处理、循环等常见编程任务。

对于JavaScript开发者：
这类似于Node.js中使用vm模块或child_process执行代码的示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage1_simple_sandbox import SimpleSandbox
from utils.logger import get_logger


def print_result(title: str, result: dict):
    """格式化打印执行结果"""
    print(f"\n📋 {title}")
    print("=" * 50)
    print(f"执行状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"执行时间: {result['execution_time']:.3f}秒")
    print(f"退出码: {result['exit_code']}")
    
    if result['output']:
        print(f"\n📤 输出内容:")
        print(result['output'])
    
    if result['error']:
        print(f"\n🚨 错误信息:")
        print(result['error'])
    
    print("-" * 50)


def demo_basic_calculations():
    """演示基础数学计算"""
    sandbox = SimpleSandbox(timeout=10)
    
    code = """
# 基础数学运算
a = 10
b = 3

print(f"加法: {a} + {b} = {a + b}")
print(f"减法: {a} - {b} = {a - b}")
print(f"乘法: {a} * {b} = {a * b}")
print(f"除法: {a} / {b} = {a / b:.2f}")
print(f"整除: {a} // {b} = {a // b}")
print(f"取余: {a} % {b} = {a % b}")
print(f"幂运算: {a} ** {b} = {a ** b}")

# 使用math模块
import math
print(f"\\n数学函数:")
print(f"平方根: sqrt({a}) = {math.sqrt(a):.2f}")
print(f"对数: log({a}) = {math.log(a):.2f}")
print(f"正弦: sin({a}) = {math.sin(a):.2f}")
"""
    
    result = sandbox.execute(code, "python")
    print_result("基础数学计算", result)


def demo_string_processing():
    """演示字符串处理"""
    sandbox = SimpleSandbox(timeout=10)
    
    code = """
# 字符串操作
text = "Hello, Python Sandbox!"

print(f"原始字符串: {text}")
print(f"长度: {len(text)}")
print(f"大写: {text.upper()}")
print(f"小写: {text.lower()}")
print(f"首字母大写: {text.title()}")

# 字符串分割和连接
words = text.split()
print(f"\\n分割后的单词: {words}")
print(f"单词数量: {len(words)}")

# 字符串替换
new_text = text.replace("Python", "JavaScript")
print(f"替换后: {new_text}")

# 字符串格式化
name = "开发者"
age = 25
print(f"\\n格式化字符串: 你好，{name}！你今年{age}岁。")

# 多行字符串
poem = '''
编程如诗，
代码如画，
沙箱执行，
安全无忧。
'''
print(f"多行字符串:{poem}")
"""
    
    result = sandbox.execute(code, "python")
    print_result("字符串处理", result)


def demo_data_structures():
    """演示数据结构操作"""
    sandbox = SimpleSandbox(timeout=10)
    
    code = """
# 列表操作
numbers = [1, 2, 3, 4, 5]
print(f"原始列表: {numbers}")

# 列表方法
numbers.append(6)
print(f"添加元素后: {numbers}")

numbers.insert(0, 0)
print(f"插入元素后: {numbers}")

# 列表推导式
squares = [x**2 for x in numbers]
print(f"平方数列表: {squares}")

# 字典操作
person = {
    "name": "张三",
    "age": 30,
    "city": "北京",
    "skills": ["Python", "JavaScript", "Docker"]
}

print(f"\\n个人信息:")
for key, value in person.items():
    print(f"{key}: {value}")

# 集合操作
set1 = {1, 2, 3, 4, 5}
set2 = {4, 5, 6, 7, 8}

print(f"\\n集合1: {set1}")
print(f"集合2: {set2}")
print(f"交集: {set1 & set2}")
print(f"并集: {set1 | set2}")
print(f"差集: {set1 - set2}")
"""
    
    result = sandbox.execute(code, "python")
    print_result("数据结构操作", result)


def demo_control_flow():
    """演示控制流程"""
    sandbox = SimpleSandbox(timeout=10)
    
    code = """
# 条件语句
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "D"

print(f"分数: {score}, 等级: {grade}")

# for循环
print("\\n九九乘法表（部分）:")
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} × {j} = {i*j:2d}", end="  ")
    print()

# while循环
print("\\n斐波那契数列（前10项）:")
a, b = 0, 1
count = 0
fib_sequence = []

while count < 10:
    fib_sequence.append(a)
    a, b = b, a + b
    count += 1

print(fib_sequence)

# 异常处理
print("\\n异常处理示例:")
try:
    result = 10 / 2
    print(f"正常计算: 10 / 2 = {result}")
    
    result = 10 / 0  # 这会引发异常
except ZeroDivisionError:
    print("捕获到除零错误！")
except Exception as e:
    print(f"其他异常: {e}")
finally:
    print("异常处理完成")
"""
    
    result = sandbox.execute(code, "python")
    print_result("控制流程", result)


def demo_functions_and_classes():
    """演示函数和类"""
    sandbox = SimpleSandbox(timeout=10)
    
    code = """
# 函数定义
def greet(name, language="中文"):
    greetings = {
        "中文": f"你好，{name}！",
        "英文": f"Hello, {name}!",
        "日文": f"こんにちは、{name}！"
    }
    return greetings.get(language, f"Hi, {name}!")

# 函数调用
print(greet("小明"))
print(greet("Tom", "英文"))
print(greet("田中", "日文"))

# 类定义
class Calculator:
    def __init__(self, name):
        self.name = name
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} × {b} = {result}")
        return result
    
    def get_history(self):
        return self.history

# 使用类
calc = Calculator("我的计算器")
print(f"\\n{calc.name}:")

result1 = calc.add(5, 3)
print(f"5 + 3 = {result1}")

result2 = calc.multiply(4, 6)
print(f"4 × 6 = {result2}")

print("\\n计算历史:")
for record in calc.get_history():
    print(f"  {record}")

# 装饰器示例
def timer_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"函数 {func.__name__} 执行时间: {end - start:.4f}秒")
        return result
    return wrapper

@timer_decorator
def slow_function():
    import time
    time.sleep(0.1)  # 模拟耗时操作
    return "完成"

print(f"\\n装饰器示例:")
result = slow_function()
print(f"结果: {result}")
"""
    
    result = sandbox.execute(code, "python")
    print_result("函数和类", result)


def demo_file_operations():
    """演示文件操作（在沙箱中）"""
    sandbox = SimpleSandbox(timeout=10)
    
    code = """
import tempfile
import os

# 在临时目录中创建文件
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    f.write("这是在沙箱中创建的文件\\n")
    f.write("包含多行内容\\n")
    f.write("用于演示文件操作\\n")
    temp_file = f.name

print(f"创建临时文件: {os.path.basename(temp_file)}")

# 读取文件
with open(temp_file, 'r') as f:
    content = f.read()
    print(f"\\n文件内容:")
    print(content)

# 按行读取
with open(temp_file, 'r') as f:
    lines = f.readlines()
    print(f"文件共有 {len(lines)} 行")
    for i, line in enumerate(lines, 1):
        print(f"第{i}行: {line.strip()}")

# 文件信息
file_size = os.path.getsize(temp_file)
print(f"\\n文件大小: {file_size} 字节")

# 清理文件
os.unlink(temp_file)
print("临时文件已清理")
"""
    
    result = sandbox.execute(code, "python")
    print_result("文件操作", result)


def main():
    """主函数 - 运行所有演示"""
    print("🚀 SimpleSandbox 基础使用示例")
    print("=" * 60)
    print("这个示例展示了如何使用基础沙箱执行各种Python代码")
    print("包括数学计算、字符串处理、数据结构、控制流程等")
    
    # 获取日志记录器
    logger = get_logger("BasicUsageDemo")
    logger.info("开始运行基础使用示例")
    
    try:
        # 运行各种演示
        demo_basic_calculations()
        demo_string_processing()
        demo_data_structures()
        demo_control_flow()
        demo_functions_and_classes()
        demo_file_operations()
        
        print("\n🎉 所有演示完成！")
        print("\n💡 学习要点:")
        print("1. SimpleSandbox可以执行各种复杂的Python代码")
        print("2. 每次执行都在独立的进程中，互不影响")
        print("3. 可以捕获所有输出和错误信息")
        print("4. 支持超时保护，防止程序无限运行")
        print("5. 临时文件会被自动清理")
        
        logger.info("基础使用示例运行完成")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        print(f"\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    main()