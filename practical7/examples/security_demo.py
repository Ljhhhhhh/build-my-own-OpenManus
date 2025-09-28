"""
安全演示程序

展示SafeSandbox的安全功能，包括：
1. 安全代码执行
2. 危险代码拦截
3. 安全配置管理
4. 实际应用场景

对于JavaScript开发者：
这类似于演示Web应用中的内容安全策略(CSP)或沙箱iframe的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage2_safe_sandbox import SafeSandbox
from utils.logger import get_logger


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"🔒 {title}")
    print('='*60)


def print_result(title: str, result: dict, show_details: bool = True):
    """格式化打印执行结果"""
    status_icon = "✅" if result['success'] else "❌"
    security_icon = "🛡️" if result.get('security_checks_passed') else "🚨"
    
    print(f"\n{status_icon} {title}")
    print("-" * 50)
    
    if show_details:
        print(f"执行状态: {status_icon} {'成功' if result['success'] else '失败'}")
        print(f"安全检查: {security_icon} {'通过' if result.get('security_checks_passed') else '拦截'}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        
        if result.get('security_enabled') is not None:
            print(f"安全模式: {'启用' if result['security_enabled'] else '禁用'}")
        
        if result['success'] and result['output']:
            print(f"\n📤 输出:")
            print(result['output'])
        
        if not result['success'] and result['error']:
            print(f"\n🚨 错误:")
            print(result['error'])
    
    print("-" * 50)


def demo_safe_code_execution():
    """演示安全代码执行"""
    print_section("安全代码执行演示")
    
    sandbox = SafeSandbox(timeout=10, memory_limit=128, enable_security=True)
    
    # 显示沙箱配置
    info = sandbox.get_info()
    security_info = sandbox.get_security_info()
    
    print(f"🔧 沙箱配置:")
    print(f"  类型: {info['type']}")
    print(f"  超时: {info['timeout']}秒")
    print(f"  内存限制: {info['memory_limit_mb']}MB")
    print(f"  安全检查: {'启用' if info['security_enabled'] else '禁用'}")
    print(f"  危险关键词: {security_info['dangerous_keywords_count']}个")
    print(f"  危险模块: {security_info['dangerous_imports_count']}个")
    print(f"  安全模块: {security_info['safe_imports_count']}个")
    
    # 测试各种安全代码
    safe_codes = [
        {
            "title": "数学计算",
            "code": """
import math

# 计算圆的面积和周长
radius = 5
area = math.pi * radius ** 2
circumference = 2 * math.pi * radius

print(f"半径: {radius}")
print(f"面积: {area:.2f}")
print(f"周长: {circumference:.2f}")
"""
        },
        {
            "title": "数据处理",
            "code": """
import json
from datetime import datetime

# 处理学生成绩数据
students = [
    {"name": "张三", "scores": [85, 92, 78]},
    {"name": "李四", "scores": [90, 88, 95]},
    {"name": "王五", "scores": [76, 84, 89]}
]

# 计算平均分
for student in students:
    avg_score = sum(student["scores"]) / len(student["scores"])
    student["average"] = round(avg_score, 2)

# 生成报告
report = {
    "generated_at": datetime.now().isoformat(),
    "total_students": len(students),
    "students": students
}

print("📊 学生成绩报告:")
print(json.dumps(report, indent=2, ensure_ascii=False))
"""
        },
        {
            "title": "算法实现",
            "code": """
# 实现快速排序算法
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 测试排序
numbers = [64, 34, 25, 12, 22, 11, 90]
print(f"原始数组: {numbers}")

sorted_numbers = quicksort(numbers)
print(f"排序后: {sorted_numbers}")

# 验证排序正确性
is_sorted = all(sorted_numbers[i] <= sorted_numbers[i+1] 
               for i in range(len(sorted_numbers)-1))
print(f"排序正确: {is_sorted}")
"""
        }
    ]
    
    for test_case in safe_codes:
        result = sandbox.execute(test_case["code"], "python")
        print_result(test_case["title"], result)


def demo_security_violations():
    """演示安全违规检测"""
    print_section("安全违规检测演示")
    
    sandbox = SafeSandbox(timeout=5, memory_limit=64, enable_security=True)
    
    # 各种危险代码示例
    dangerous_codes = [
        {
            "title": "系统命令执行",
            "code": """
import os
print("尝试执行系统命令...")
os.system("whoami")  # 危险：系统命令执行
""",
            "explanation": "尝试执行系统命令，可能被恶意利用"
        },
        {
            "title": "子进程调用",
            "code": """
import subprocess
result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
print(result.stdout)
""",
            "explanation": "使用subprocess模块执行外部程序"
        },
        {
            "title": "动态代码执行",
            "code": """
user_input = "print('Hello from eval')"
eval(user_input)  # 危险：动态代码执行
""",
            "explanation": "使用eval执行动态代码，存在代码注入风险"
        },
        {
            "title": "文件系统访问",
            "code": """
# 尝试读取系统文件
with open("/etc/passwd", "r") as f:
    content = f.read()
    print(content)
""",
            "explanation": "尝试访问系统敏感文件"
        },
        {
            "title": "网络操作",
            "code": """
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("google.com", 80))
""",
            "explanation": "尝试建立网络连接"
        },
        {
            "title": "模块导入攻击",
            "code": """
import sys
sys.path.insert(0, "/tmp")
import malicious_module  # 假设的恶意模块
""",
            "explanation": "尝试导入可能的恶意模块"
        }
    ]
    
    print("🚨 以下代码将被安全检查拦截：\n")
    
    for i, test_case in enumerate(dangerous_codes, 1):
        print(f"📝 测试 {i}: {test_case['title']}")
        print(f"💡 说明: {test_case['explanation']}")
        
        result = sandbox.execute(test_case["code"], "python")
        
        # 简化显示，只显示关键信息
        status = "✅ 成功拦截" if not result['success'] else "❌ 未拦截"
        print(f"🛡️ 安全检查: {status}")
        
        if not result['success']:
            print(f"🚨 拦截原因: {result['error']}")
        
        print()


def demo_security_bypass_attempts():
    """演示安全绕过尝试（都应该被拦截）"""
    print_section("安全绕过尝试演示")
    
    sandbox = SafeSandbox(enable_security=True)
    
    bypass_attempts = [
        {
            "title": "字符串拼接绕过",
            "code": """
import_str = "imp" + "ort os"
# 这种简单的字符串拼接无法绕过静态检查
""",
            "explanation": "尝试通过字符串拼接绕过关键词检测"
        },
        {
            "title": "注释混淆",
            "code": """
import os  # 这只是一个注释，不是真的导入... 才怪！
os.system("echo 'bypassed'")
""",
            "explanation": "在注释中隐藏真实意图"
        },
        {
            "title": "多行字符串隐藏",
            "code": '''
code = """
import os
os.system("ls")
"""
# 即使在字符串中，关键词检查也会发现
''',
            "explanation": "在多行字符串中隐藏危险代码"
        }
    ]
    
    print("🔍 以下是一些常见的安全绕过尝试，都应该被拦截：\n")
    
    for i, attempt in enumerate(bypass_attempts, 1):
        print(f"🎯 尝试 {i}: {attempt['title']}")
        print(f"💡 说明: {attempt['explanation']}")
        
        result = sandbox.execute(attempt["code"], "python")
        
        if not result['success']:
            print("✅ 绕过失败 - 安全检查有效")
            print(f"🛡️ 拦截原因: {result['error']}")
        else:
            print("❌ 绕过成功 - 需要改进安全检查")
        
        print()


def demo_security_configuration():
    """演示安全配置管理"""
    print_section("安全配置管理演示")
    
    # 创建不同配置的沙箱
    configs = [
        {
            "name": "高安全模式",
            "sandbox": SafeSandbox(timeout=5, memory_limit=32, enable_security=True),
            "description": "严格的安全检查，适用于不信任的代码"
        },
        {
            "name": "开发模式", 
            "sandbox": SafeSandbox(timeout=30, memory_limit=256, enable_security=False),
            "description": "禁用安全检查，适用于开发和调试"
        },
        {
            "name": "教学模式",
            "sandbox": SafeSandbox(timeout=10, memory_limit=128, enable_security=True),
            "description": "平衡的配置，适用于编程教学"
        }
    ]
    
    # 测试代码（包含一些边界情况）
    test_code = """
import math
import tempfile

# 创建临时文件（这是安全的）
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("Hello from sandbox!")
    temp_path = f.name

print(f"创建临时文件: {temp_path}")

# 数学计算
result = math.factorial(5)
print(f"5的阶乘: {result}")
"""
    
    print("🔧 测试不同安全配置下的代码执行：\n")
    
    for config in configs:
        print(f"📋 {config['name']}")
        print(f"💡 {config['description']}")
        
        info = config['sandbox'].get_info()
        print(f"⚙️  配置: 超时{info['timeout']}秒, 内存{info['memory_limit_mb']}MB, "
              f"安全{'启用' if info['security_enabled'] else '禁用'}")
        
        result = config['sandbox'].execute(test_code, "python")
        
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"🎯 执行结果: {status}")
        
        if result['success']:
            print(f"⏱️  执行时间: {result['execution_time']:.3f}秒")
        else:
            print(f"🚨 错误: {result['error']}")
        
        print()


def demo_real_world_scenarios():
    """演示真实世界应用场景"""
    print_section("真实世界应用场景")
    
    sandbox = SafeSandbox(timeout=15, memory_limit=128, enable_security=True)
    
    scenarios = [
        {
            "title": "在线编程判题",
            "description": "模拟在线编程平台的代码执行",
            "code": """
# 用户提交的算法题解答
def two_sum(nums, target):
    \"\"\"
    给定一个整数数组 nums 和一个目标值 target，
    请你在该数组中找出和为目标值的那两个整数，并返回它们的数组下标。
    \"\"\"
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[num] = i
    return []

# 测试用例
test_cases = [
    ([2, 7, 11, 15], 9),
    ([3, 2, 4], 6),
    ([3, 3], 6)
]

print("🧮 Two Sum 算法测试:")
for i, (nums, target) in enumerate(test_cases, 1):
    result = two_sum(nums, target)
    print(f"测试 {i}: nums={nums}, target={target} -> {result}")
"""
        },
        {
            "title": "数据分析脚本",
            "description": "安全执行用户提交的数据分析代码",
            "code": """
import json
import math
from datetime import datetime

# 模拟销售数据
sales_data = [
    {"date": "2024-01-01", "product": "A", "amount": 1200},
    {"date": "2024-01-02", "product": "B", "amount": 800},
    {"date": "2024-01-03", "product": "A", "amount": 1500},
    {"date": "2024-01-04", "product": "C", "amount": 600},
    {"date": "2024-01-05", "product": "B", "amount": 900},
]

# 数据分析
total_sales = sum(item["amount"] for item in sales_data)
avg_sales = total_sales / len(sales_data)

# 按产品分组
product_sales = {}
for item in sales_data:
    product = item["product"]
    if product not in product_sales:
        product_sales[product] = 0
    product_sales[product] += item["amount"]

# 生成报告
report = {
    "analysis_date": datetime.now().isoformat(),
    "total_sales": total_sales,
    "average_sales": round(avg_sales, 2),
    "product_breakdown": product_sales,
    "top_product": max(product_sales, key=product_sales.get)
}

print("📊 销售数据分析报告:")
print(json.dumps(report, indent=2, ensure_ascii=False))
"""
        },
        {
            "title": "教学代码验证",
            "description": "验证学生提交的编程作业",
            "code": """
# 学生作业：实现斐波那契数列
def fibonacci(n):
    \"\"\"计算斐波那契数列的第n项\"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

def fibonacci_optimized(n):
    \"\"\"优化版本：使用动态规划\"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# 测试和比较
print("🔢 斐波那契数列测试:")
for i in range(10):
    fib1 = fibonacci(i)
    fib2 = fibonacci_optimized(i)
    print(f"F({i}) = {fib1} (递归) = {fib2} (优化)")
    assert fib1 == fib2, f"结果不一致: {fib1} != {fib2}"

print("✅ 所有测试通过！")
"""
        }
    ]
    
    print("🌍 以下是一些真实世界的应用场景：\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📋 场景 {i}: {scenario['title']}")
        print(f"💡 描述: {scenario['description']}")
        
        result = sandbox.execute(scenario["code"], "python")
        
        if result['success']:
            print("✅ 执行成功")
            print(f"⏱️  执行时间: {result['execution_time']:.3f}秒")
            print("📤 输出:")
            # 限制输出长度以保持可读性
            output_lines = result['output'].split('\n')
            if len(output_lines) > 10:
                print('\n'.join(output_lines[:10]))
                print(f"... (还有 {len(output_lines) - 10} 行)")
            else:
                print(result['output'])
        else:
            print("❌ 执行失败")
            print(f"🚨 错误: {result['error']}")
        
        print()


def main():
    """主函数 - 运行所有安全演示"""
    print("🔒 SafeSandbox 安全功能演示")
    print("=" * 60)
    print("这个演示展示了安全沙箱的各种功能和应用场景")
    
    # 获取日志记录器
    logger = get_logger("SecurityDemo")
    logger.info("开始运行安全演示")
    
    try:
        # 运行各种演示
        demo_safe_code_execution()
        demo_security_violations()
        demo_security_bypass_attempts()
        demo_security_configuration()
        demo_real_world_scenarios()
        
        print_section("演示总结")
        print("🎉 所有安全演示完成！")
        print("\n💡 关键学习要点:")
        print("1. 🛡️  多层安全检查：关键词、模块、AST分析")
        print("2. 🚨 危险操作拦截：系统命令、文件访问、网络操作")
        print("3. ⚙️  灵活配置：可根据需求调整安全级别")
        print("4. 📊 实际应用：在线判题、数据分析、教学验证")
        print("5. 🔍 绕过防护：静态分析能检测大部分绕过尝试")
        print("6. 📝 详细日志：完整记录安全检查过程")
        
        logger.info("安全演示运行完成")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        print(f"\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    main()