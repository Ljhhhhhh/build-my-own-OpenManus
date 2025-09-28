"""
Docker沙箱演示程序

展示DockerSandbox的容器隔离功能，包括：
1. 多语言代码执行
2. 容器隔离验证
3. 安全控制演示
4. 实际应用场景

对于JavaScript开发者：
这类似于演示微服务架构或容器化应用的功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage3_docker_sandbox import DockerSandbox
from utils.logger import get_logger


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"🐳 {title}")
    print('='*60)


def print_result(title: str, result: dict, show_details: bool = True):
    """格式化打印执行结果"""
    status_icon = "✅" if result['success'] else "❌"
    
    print(f"\n{status_icon} {title}")
    print("-" * 50)
    
    if show_details:
        print(f"执行状态: {status_icon} {'成功' if result['success'] else '失败'}")
        print(f"容器ID: {result.get('container_id', 'N/A')}")
        print(f"使用镜像: {result.get('image', 'N/A')}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        print(f"退出码: {result['exit_code']}")
        
        if result['success'] and result['output']:
            print(f"\n📤 输出:")
            print(result['output'])
        
        if not result['success'] and result['error']:
            print(f"\n🚨 错误:")
            print(result['error'])
    
    print("-" * 50)


def demo_multi_language_execution():
    """演示多语言代码执行"""
    print_section("多语言代码执行演示")
    
    sandbox = DockerSandbox(timeout=15, memory_limit="128m", enable_network=False)
    
    # 显示Docker状态
    docker_status = sandbox.get_docker_status()
    print(f"🐳 Docker状态: {docker_status['status']}")
    if docker_status['status'] == 'connected':
        print(f"   版本: {docker_status['version']}")
        print(f"   运行中容器: {docker_status['containers_running']}")
        print(f"   总容器数: {docker_status['containers_total']}")
        print(f"   镜像数量: {docker_status['images_count']}")
    
    # 多语言代码示例
    language_examples = [
        {
            "language": "python",
            "title": "Python数据科学计算",
            "code": """
import math
import json
from datetime import datetime

# 数据科学计算示例
data = {
    "experiment": "Docker Python Execution",
    "timestamp": datetime.now().isoformat(),
    "calculations": {
        "pi": math.pi,
        "e": math.e,
        "sqrt_2": math.sqrt(2),
        "factorial_10": math.factorial(10)
    },
    "statistics": {
        "mean": lambda x: sum(x) / len(x),
        "variance": lambda x: sum((i - sum(x)/len(x))**2 for i in x) / len(x)
    }
}

# 计算示例数据的统计信息
sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean_val = sum(sample_data) / len(sample_data)
variance_val = sum((x - mean_val)**2 for x in sample_data) / len(sample_data)

print("🐍 Python在Docker容器中执行")
print(f"样本数据: {sample_data}")
print(f"平均值: {mean_val}")
print(f"方差: {variance_val:.2f}")
print(f"π的值: {data['calculations']['pi']:.6f}")
print(f"10的阶乘: {data['calculations']['factorial_10']}")
"""
        },
        {
            "language": "javascript",
            "title": "JavaScript Web开发模拟",
            "code": """
// JavaScript Web开发模拟
const webApp = {
    name: "Docker Node.js App",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    features: ["REST API", "Database", "Authentication"],
    
    // 模拟API响应
    generateApiResponse: function(endpoint) {
        return {
            status: "success",
            endpoint: endpoint,
            data: {
                message: "Hello from containerized Node.js!",
                timestamp: this.timestamp,
                random: Math.random()
            }
        };
    },
    
    // 模拟数据处理
    processData: function(data) {
        return data.map(item => ({
            id: item,
            value: item * 2,
            squared: item ** 2
        }));
    }
};

console.log("🟨 JavaScript在Docker容器中执行");
console.log(`应用: ${webApp.name} v${webApp.version}`);
console.log(`功能: ${webApp.features.join(", ")}`);

// 模拟API调用
const apiResponse = webApp.generateApiResponse("/api/users");
console.log("API响应:", JSON.stringify(apiResponse, null, 2));

// 模拟数据处理
const sampleData = [1, 2, 3, 4, 5];
const processedData = webApp.processData(sampleData);
console.log("处理后的数据:", JSON.stringify(processedData, null, 2));
"""
        }
    ]
    
    for example in language_examples:
        result = sandbox.execute(example["code"], example["language"])
        print_result(f"{example['title']} ({example['language'].upper()})", result)


def demo_container_isolation():
    """演示容器隔离功能"""
    print_section("容器隔离功能演示")
    
    sandbox = DockerSandbox(timeout=10, memory_limit="64m")
    
    print("🔒 测试容器之间的完全隔离\n")
    
    # 测试1：变量隔离
    print("📝 测试1：变量隔离")
    
    # 第一个容器：设置变量
    code1 = """
# 在第一个容器中设置变量
global_var = "I am in container 1"
local_data = {"container": 1, "data": [1, 2, 3]}

print(f"容器1设置变量: {global_var}")
print(f"容器1数据: {local_data}")

# 尝试写入文件
import tempfile
import os

temp_file = "/tmp/container1_data.txt"
try:
    with open(temp_file, "w") as f:
        f.write("Data from container 1")
    print(f"容器1创建文件: {temp_file}")
except Exception as e:
    print(f"容器1文件操作失败: {e}")
"""
    
    result1 = sandbox.execute(code1, "python")
    print_result("容器1执行", result1, show_details=False)
    
    # 第二个容器：尝试访问第一个容器的变量
    code2 = """
# 在第二个容器中尝试访问第一个容器的变量
print("容器2尝试访问容器1的变量...")

try:
    print(f"全局变量: {global_var}")
except NameError:
    print("✅ 无法访问容器1的全局变量 - 变量隔离成功!")

try:
    print(f"本地数据: {local_data}")
except NameError:
    print("✅ 无法访问容器1的本地数据 - 数据隔离成功!")

# 尝试访问第一个容器创建的文件
import os
temp_file = "/tmp/container1_data.txt"

if os.path.exists(temp_file):
    print("❌ 可以访问容器1的文件 - 文件隔离失败!")
else:
    print("✅ 无法访问容器1的文件 - 文件系统隔离成功!")

print("容器2有自己独立的环境")
"""
    
    result2 = sandbox.execute(code2, "python")
    print_result("容器2执行", result2, show_details=False)
    
    # 测试2：进程隔离
    print("\n📝 测试2：进程隔离")
    
    process_code = """
import os
import psutil

print(f"当前进程ID: {os.getpid()}")
print(f"父进程ID: {os.getppid()}")

# 获取系统信息
try:
    cpu_count = psutil.cpu_count()
    memory_info = psutil.virtual_memory()
    
    print(f"CPU核心数: {cpu_count}")
    print(f"总内存: {memory_info.total / (1024**3):.2f} GB")
    print(f"可用内存: {memory_info.available / (1024**3):.2f} GB")
    
    # 列出运行的进程（只显示前5个）
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        processes.append(f"PID {proc.info['pid']}: {proc.info['name']}")
        if len(processes) >= 5:
            break
    
    print("运行的进程（前5个）:")
    for proc in processes:
        print(f"  {proc}")
        
except Exception as e:
    print(f"获取系统信息失败: {e}")
"""
    
    result3 = sandbox.execute(process_code, "python")
    print_result("进程隔离测试", result3)


def demo_security_features():
    """演示安全功能"""
    print_section("安全功能演示")
    
    sandbox = DockerSandbox(timeout=10, memory_limit="64m", enable_network=False)
    
    security_tests = [
        {
            "title": "网络隔离测试",
            "description": "尝试访问外部网络（应该失败）",
            "code": """
import socket
import urllib.request

print("🔒 测试网络隔离...")

# 测试1：Socket连接
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('google.com', 80))
    sock.close()
    
    if result == 0:
        print("❌ 网络连接成功 - 网络隔离失败!")
    else:
        print("✅ 网络连接失败 - 网络隔离成功!")
except Exception as e:
    print(f"✅ 网络访问异常 - 网络隔离成功: {e}")

# 测试2：HTTP请求
try:
    response = urllib.request.urlopen('http://httpbin.org/ip', timeout=3)
    print("❌ HTTP请求成功 - 网络隔离失败!")
except Exception as e:
    print(f"✅ HTTP请求失败 - 网络隔离成功: {e}")
"""
        },
        {
            "title": "文件系统安全测试",
            "description": "测试文件系统访问限制",
            "code": """
import os
import tempfile

print("🔒 测试文件系统安全...")

# 测试1：尝试访问系统敏感文件
sensitive_files = ['/etc/passwd', '/etc/shadow', '/root/.bashrc']

for file_path in sensitive_files:
    try:
        with open(file_path, 'r') as f:
            content = f.read()[:100]
        print(f"❌ 可以读取 {file_path} - 文件系统安全失败!")
    except Exception as e:
        print(f"✅ 无法读取 {file_path} - 文件系统安全成功: {type(e).__name__}")

# 测试2：尝试在系统目录写入文件
system_dirs = ['/etc', '/root', '/usr/bin']

for dir_path in system_dirs:
    try:
        test_file = os.path.join(dir_path, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        print(f"❌ 可以写入 {dir_path} - 文件系统安全失败!")
        os.unlink(test_file)  # 清理
    except Exception as e:
        print(f"✅ 无法写入 {dir_path} - 文件系统安全成功: {type(e).__name__}")

# 测试3：在允许的临时目录操作
try:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('临时文件测试')
        temp_path = f.name
    
    with open(temp_path, 'r') as f:
        content = f.read()
    
    os.unlink(temp_path)
    print(f"✅ 临时文件操作成功: {content}")
except Exception as e:
    print(f"❌ 临时文件操作失败: {e}")
"""
        },
        {
            "title": "资源限制测试",
            "description": "测试内存和CPU资源限制",
            "code": """
import psutil
import time

print("🔒 测试资源限制...")

# 测试1：内存信息
try:
    memory = psutil.virtual_memory()
    print(f"总内存: {memory.total / (1024**2):.0f} MB")
    print(f"可用内存: {memory.available / (1024**2):.0f} MB")
    print(f"内存使用率: {memory.percent:.1f}%")
except Exception as e:
    print(f"获取内存信息失败: {e}")

# 测试2：CPU信息
try:
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU核心数: {cpu_count}")
    print(f"CPU使用率: {cpu_percent:.1f}%")
except Exception as e:
    print(f"获取CPU信息失败: {e}")

# 测试3：尝试消耗大量内存（应该被限制）
print("尝试分配大量内存...")
try:
    # 尝试分配100MB内存
    big_list = []
    for i in range(1000000):  # 100万个整数
        big_list.append(i)
    
    print(f"成功分配内存，列表长度: {len(big_list)}")
    del big_list  # 释放内存
    print("内存已释放")
except MemoryError:
    print("✅ 内存分配被限制 - 资源限制生效!")
except Exception as e:
    print(f"内存分配异常: {e}")
"""
        }
    ]
    
    for test in security_tests:
        print(f"\n📋 {test['title']}")
        print(f"💡 {test['description']}")
        
        result = sandbox.execute(test["code"], "python")
        
        if result['success']:
            print("✅ 测试执行成功")
            print("📤 输出:")
            # 限制输出长度以保持可读性
            output_lines = result['output'].split('\n')
            for line in output_lines[:15]:  # 只显示前15行
                print(f"   {line}")
            if len(output_lines) > 15:
                print(f"   ... (还有 {len(output_lines) - 15} 行)")
        else:
            print("❌ 测试执行失败")
            print(f"🚨 错误: {result['error']}")
        
        print()


def demo_real_world_scenarios():
    """演示真实世界应用场景"""
    print_section("真实世界应用场景")
    
    sandbox = DockerSandbox(timeout=20, memory_limit="256m", enable_network=False)
    
    scenarios = [
        {
            "title": "在线代码执行平台",
            "description": "模拟在线IDE或编程学习平台的代码执行",
            "code": """
# 模拟学生提交的编程作业
def bubble_sort(arr):
    \"\"\"冒泡排序算法实现\"\"\"
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def quick_sort(arr):
    \"\"\"快速排序算法实现\"\"\"
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 测试数据
import random
import time

test_data = [random.randint(1, 100) for _ in range(20)]
print(f"原始数据: {test_data}")

# 测试冒泡排序
start_time = time.time()
bubble_result = bubble_sort(test_data.copy())
bubble_time = time.time() - start_time

print(f"冒泡排序结果: {bubble_result}")
print(f"冒泡排序耗时: {bubble_time:.4f}秒")

# 测试快速排序
start_time = time.time()
quick_result = quick_sort(test_data.copy())
quick_time = time.time() - start_time

print(f"快速排序结果: {quick_result}")
print(f"快速排序耗时: {quick_time:.4f}秒")

# 验证结果
print(f"排序结果一致: {bubble_result == quick_result}")
print(f"快速排序性能提升: {bubble_time / quick_time:.2f}倍")
"""
        },
        {
            "title": "数据分析沙箱",
            "description": "安全执行用户提交的数据分析脚本",
            "code": """
import json
import math
from datetime import datetime, timedelta

# 模拟电商销售数据
sales_data = [
    {"date": "2024-01-01", "product": "笔记本电脑", "category": "电子产品", "price": 5999, "quantity": 2},
    {"date": "2024-01-02", "product": "手机", "category": "电子产品", "price": 3999, "quantity": 3},
    {"date": "2024-01-03", "product": "书籍", "category": "图书", "price": 29, "quantity": 10},
    {"date": "2024-01-04", "product": "耳机", "category": "电子产品", "price": 299, "quantity": 5},
    {"date": "2024-01-05", "product": "咖啡", "category": "食品", "price": 25, "quantity": 20},
]

print("📊 电商销售数据分析")
print("=" * 40)

# 基础统计
total_revenue = sum(item["price"] * item["quantity"] for item in sales_data)
total_items = sum(item["quantity"] for item in sales_data)
avg_order_value = total_revenue / len(sales_data)

print(f"总收入: ¥{total_revenue:,}")
print(f"总销量: {total_items} 件")
print(f"平均订单价值: ¥{avg_order_value:.2f}")

# 按类别分析
category_stats = {}
for item in sales_data:
    category = item["category"]
    if category not in category_stats:
        category_stats[category] = {"revenue": 0, "quantity": 0, "orders": 0}
    
    category_stats[category]["revenue"] += item["price"] * item["quantity"]
    category_stats[category]["quantity"] += item["quantity"]
    category_stats[category]["orders"] += 1

print("\\n📈 按类别统计:")
for category, stats in category_stats.items():
    print(f"{category}:")
    print(f"  收入: ¥{stats['revenue']:,}")
    print(f"  销量: {stats['quantity']} 件")
    print(f"  订单数: {stats['orders']}")
    print(f"  平均单价: ¥{stats['revenue'] / stats['quantity']:.2f}")

# 找出最佳产品
best_product = max(sales_data, key=lambda x: x["price"] * x["quantity"])
print(f"\\n🏆 最佳产品: {best_product['product']}")
print(f"   收入贡献: ¥{best_product['price'] * best_product['quantity']:,}")

# 生成JSON报告
report = {
    "analysis_date": datetime.now().isoformat(),
    "summary": {
        "total_revenue": total_revenue,
        "total_items": total_items,
        "average_order_value": round(avg_order_value, 2)
    },
    "category_breakdown": category_stats,
    "best_product": best_product
}

print("\\n📄 JSON报告:")
print(json.dumps(report, indent=2, ensure_ascii=False))
"""
        },
        {
            "title": "AI模型推理沙箱",
            "description": "安全执行机器学习模型推理代码",
            "code": """
import math
import random

# 模拟简单的线性回归模型
class SimpleLinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None
        self.trained = False
    
    def train(self, x_data, y_data):
        \"\"\"训练线性回归模型\"\"\"
        n = len(x_data)
        sum_x = sum(x_data)
        sum_y = sum(y_data)
        sum_xy = sum(x * y for x, y in zip(x_data, y_data))
        sum_x2 = sum(x * x for x in x_data)
        
        # 计算斜率和截距
        self.slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        self.intercept = (sum_y - self.slope * sum_x) / n
        self.trained = True
        
        print(f"模型训练完成:")
        print(f"  斜率: {self.slope:.4f}")
        print(f"  截距: {self.intercept:.4f}")
    
    def predict(self, x):
        \"\"\"预测\"\"\"
        if not self.trained:
            raise ValueError("模型尚未训练")
        return self.slope * x + self.intercept
    
    def evaluate(self, x_test, y_test):
        \"\"\"评估模型\"\"\"
        predictions = [self.predict(x) for x in x_test]
        mse = sum((pred - actual) ** 2 for pred, actual in zip(predictions, y_test)) / len(y_test)
        rmse = math.sqrt(mse)
        
        return {
            "mse": mse,
            "rmse": rmse,
            "predictions": predictions
        }

# 生成模拟数据（房价预测）
print("🤖 AI模型推理演示 - 房价预测")
print("=" * 40)

# 训练数据：房屋面积 -> 房价（万元）
random.seed(42)  # 确保结果可重现
x_train = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]
y_train = [x * 0.8 + random.uniform(-5, 5) + 20 for x in x_train]  # 添加噪声

print("训练数据:")
for x, y in zip(x_train, y_train):
    print(f"  {x}平米 -> {y:.1f}万元")

# 训练模型
model = SimpleLinearRegression()
model.train(x_train, y_train)

# 测试数据
x_test = [75, 85, 95, 105, 115]
y_test = [x * 0.8 + random.uniform(-3, 3) + 20 for x in x_test]

print(f"\\n测试数据:")
for x, y in zip(x_test, y_test):
    print(f"  {x}平米 -> {y:.1f}万元（实际）")

# 模型评估
evaluation = model.evaluate(x_test, y_test)

print(f"\\n📊 模型评估:")
print(f"  均方误差 (MSE): {evaluation['mse']:.2f}")
print(f"  均方根误差 (RMSE): {evaluation['rmse']:.2f}")

print(f"\\n🔮 预测结果:")
for x, actual, pred in zip(x_test, y_test, evaluation['predictions']):
    error = abs(pred - actual)
    print(f"  {x}平米: 预测 {pred:.1f}万元, 实际 {actual:.1f}万元, 误差 {error:.1f}万元")

# 新房价预测
new_houses = [65, 125, 150]
print(f"\\n🏠 新房价预测:")
for size in new_houses:
    predicted_price = model.predict(size)
    print(f"  {size}平米房屋预测价格: {predicted_price:.1f}万元")
"""
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['title']}")
        print(f"💡 描述: {scenario['description']}")
        
        result = sandbox.execute(scenario["code"], "python")
        
        if result['success']:
            print("✅ 执行成功")
            print(f"⏱️  执行时间: {result['execution_time']:.3f}秒")
            print(f"🐳 容器ID: {result['container_id']}")
            print("📤 输出:")
            # 限制输出长度以保持可读性
            output_lines = result['output'].split('\n')
            for line in output_lines[:25]:  # 显示前25行
                print(f"   {line}")
            if len(output_lines) > 25:
                print(f"   ... (还有 {len(output_lines) - 25} 行)")
        else:
            print("❌ 执行失败")
            print(f"🚨 错误: {result['error']}")
        
        print()


def main():
    """主函数 - 运行所有Docker演示"""
    print("🐳 DockerSandbox 容器隔离功能演示")
    print("=" * 60)
    print("这个演示展示了Docker沙箱的完全隔离功能和实际应用场景")
    
    # 获取日志记录器
    logger = get_logger("DockerDemo")
    logger.info("开始运行Docker演示")
    
    try:
        # 检查Docker是否可用
        test_sandbox = DockerSandbox(timeout=5)
        logger.info("Docker连接成功")
        
        # 运行各种演示
        demo_multi_language_execution()
        demo_container_isolation()
        demo_security_features()
        demo_real_world_scenarios()
        
        print_section("演示总结")
        print("🎉 所有Docker演示完成！")
        print("\n💡 关键学习要点:")
        print("1. 🐳 完全隔离：每个容器都是独立的运行环境")
        print("2. 🔒 安全控制：网络隔离、文件系统保护、非root用户")
        print("3. 📦 镜像管理：自动拉取和管理不同语言的运行环境")
        print("4. ⚡ 资源限制：精确控制内存和CPU使用")
        print("5. 🧹 自动清理：容器执行完成后自动删除")
        print("6. 🌐 多语言支持：Python、JavaScript、Java、Go等")
        print("7. 🚀 实际应用：在线IDE、数据分析、AI推理等场景")
        
        logger.info("Docker演示运行完成")
        
    except Exception as e:
        logger.error(f"Docker演示过程中发生错误: {e}")
        print(f"\n❌ Docker演示失败: {e}")
        print("\n💡 可能的解决方案：")
        print("1. 确保Docker已安装并正在运行")
        print("2. 确保当前用户有Docker权限")
        print("3. 运行 'docker --version' 检查Docker状态")
        print("4. 运行 'docker run hello-world' 测试Docker功能")


if __name__ == "__main__":
    main()