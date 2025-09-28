"""
沙箱执行环境 - 快速演示程序

这个程序快速演示三个阶段沙箱的核心功能和差异：
1. SimpleSandbox: 基础进程隔离
2. SafeSandbox: 安全检查和资源限制  
3. DockerSandbox: 容器完全隔离

对于JavaScript开发者：
这类似于一个功能对比演示，展示不同安全级别的代码执行环境
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stage1_simple_sandbox import SimpleSandbox
from stage2_safe_sandbox import SafeSandbox
from stage3_docker_sandbox import DockerSandbox


def print_section(title: str, icon: str = "🔧"):
    """打印章节标题"""
    print(f"\n{icon} {title}")
    print("=" * (len(title) + 4))


def print_result(sandbox_name: str, result: dict):
    """格式化打印执行结果"""
    status_icon = "✅" if result['success'] else "❌"
    print(f"{status_icon} {sandbox_name}: {result['execution_time']:.3f}秒")
    
    if result['success'] and result.get('output'):
        # 只显示输出的前两行
        lines = result['output'].strip().split('\n')[:2]
        for line in lines:
            print(f"   {line}")
        if len(result['output'].strip().split('\n')) > 2:
            print("   ...")
    
    if not result['success']:
        error_msg = result['error'][:100] + "..." if len(result['error']) > 100 else result['error']
        print(f"   错误: {error_msg}")


def demo_basic_execution():
    """演示基础代码执行"""
    print_section("基础代码执行对比", "🚀")
    
    # 创建三个沙箱实例
    sandboxes = {}
    
    try:
        sandboxes['SimpleSandbox'] = SimpleSandbox(timeout=5)
        print("✅ SimpleSandbox 初始化成功")
    except Exception as e:
        print(f"❌ SimpleSandbox 初始化失败: {e}")
    
    try:
        sandboxes['SafeSandbox'] = SafeSandbox(timeout=5, memory_limit=64, enable_security=True)
        print("✅ SafeSandbox 初始化成功")
    except Exception as e:
        print(f"❌ SafeSandbox 初始化失败: {e}")
    
    try:
        sandboxes['DockerSandbox'] = DockerSandbox(timeout=10, memory_limit="64m")
        print("✅ DockerSandbox 初始化成功")
    except Exception as e:
        print(f"❌ DockerSandbox 初始化失败: {e}")
    
    # 测试代码
    test_code = """
import math
print("Hello from sandbox!")
result = math.sqrt(16) + math.pi
print(f"计算结果: {result:.2f}")
"""
    
    print(f"\n📝 测试代码:")
    print("```python")
    print(test_code.strip())
    print("```")
    
    print(f"\n📊 执行结果:")
    
    for name, sandbox in sandboxes.items():
        if sandbox:
            try:
                result = sandbox.execute(test_code, "python")
                print_result(name, result)
            except Exception as e:
                print(f"❌ {name}: 执行异常 - {e}")
        else:
            print(f"❌ {name}: 不可用")


def demo_security_features():
    """演示安全功能差异"""
    print_section("安全功能对比", "🛡️")
    
    # 只测试有安全功能的沙箱
    sandboxes = {}
    
    try:
        sandboxes['SimpleSandbox'] = SimpleSandbox(timeout=5)
    except:
        pass
    
    try:
        sandboxes['SafeSandbox'] = SafeSandbox(timeout=5, enable_security=True)
    except:
        pass
    
    # 危险代码测试
    dangerous_codes = [
        {
            "name": "系统命令执行",
            "code": "import os; os.system('echo dangerous')"
        },
        {
            "name": "动态代码执行", 
            "code": "eval('print(\"dynamic code\")')"
        },
        {
            "name": "文件系统访问",
            "code": "open('/etc/passwd', 'r').read()"
        }
    ]
    
    for test in dangerous_codes:
        print(f"\n🚨 测试: {test['name']}")
        print(f"代码: {test['code']}")
        
        for name, sandbox in sandboxes.items():
            if sandbox:
                try:
                    result = sandbox.execute(test['code'], "python")
                    if result['success']:
                        print(f"❌ {name}: 危险代码执行成功（安全风险！）")
                    else:
                        if "安全检查失败" in result['error']:
                            print(f"✅ {name}: 安全检查拦截")
                        else:
                            print(f"⚠️  {name}: 执行失败（其他原因）")
                except Exception as e:
                    print(f"❌ {name}: 异常 - {e}")


def demo_isolation_features():
    """演示隔离功能"""
    print_section("隔离功能演示", "🔒")
    
    # 创建Docker沙箱（如果可用）
    try:
        docker_sandbox = DockerSandbox(timeout=10, memory_limit="64m")
        print("✅ Docker沙箱可用，演示容器隔离")
        
        # 测试容器隔离
        isolation_test = """
import os
import tempfile

print(f"进程ID: {os.getpid()}")
print(f"工作目录: {os.getcwd()}")

# 创建临时文件
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("container test")
    temp_path = f.name

print(f"临时文件: {temp_path}")
print("容器隔离测试完成")
"""
        
        print("\n📝 隔离测试代码:")
        print("- 获取进程ID和工作目录")
        print("- 创建临时文件")
        print("- 验证容器环境")
        
        result = docker_sandbox.execute(isolation_test, "python")
        print(f"\n📊 执行结果:")
        print_result("DockerSandbox", result)
        
        if result.get('container_id'):
            print(f"🐳 容器ID: {result['container_id']}")
        
    except Exception as e:
        print(f"❌ Docker沙箱不可用: {e}")
        print("💡 请确保Docker已安装并运行")


def demo_performance_comparison():
    """演示性能对比"""
    print_section("性能对比", "⚡")
    
    # 创建可用的沙箱
    sandboxes = {}
    
    try:
        sandboxes['SimpleSandbox'] = SimpleSandbox(timeout=10)
    except:
        pass
    
    try:
        sandboxes['SafeSandbox'] = SafeSandbox(timeout=10, enable_security=True)
    except:
        pass
    
    try:
        sandboxes['DockerSandbox'] = DockerSandbox(timeout=15, memory_limit="128m")
    except:
        pass
    
    # 性能测试代码
    perf_code = """
# 简单的计算密集型任务
total = 0
for i in range(10000):
    total += i * i

print(f"计算完成: {total}")
"""
    
    print("📝 性能测试: 计算1万个数的平方和")
    print("\n📊 执行时间对比:")
    
    results = {}
    for name, sandbox in sandboxes.items():
        if sandbox:
            try:
                result = sandbox.execute(perf_code, "python")
                results[name] = result['execution_time']
                print_result(name, result)
            except Exception as e:
                print(f"❌ {name}: 执行异常")
    
    # 性能分析
    if len(results) > 1:
        fastest = min(results.values())
        slowest = max(results.values())
        
        print(f"\n📈 性能分析:")
        print(f"最快: {fastest:.3f}秒")
        print(f"最慢: {slowest:.3f}秒") 
        print(f"性能差异: {slowest/fastest:.2f}倍")


def main():
    """主演示函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🚀 沙箱执行环境 - 快速演示                    ║
║                                                              ║
║  展示三个阶段沙箱的核心功能和差异：                           ║
║  📦 SimpleSandbox  - 基础进程隔离                            ║
║  🛡️  SafeSandbox    - 安全检查和资源限制                     ║
║  🐳 DockerSandbox  - 容器完全隔离                            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    try:
        # 运行各项演示
        demo_basic_execution()
        demo_security_features()
        demo_isolation_features()
        demo_performance_comparison()
        
        print_section("演示总结", "🎉")
        print("✅ 快速演示完成！")
        print("\n💡 关键学习要点:")
        print("1. 📦 SimpleSandbox: 基础隔离，性能最好，安全性最低")
        print("2. 🛡️  SafeSandbox: 平衡安全和性能，适合大多数场景")
        print("3. 🐳 DockerSandbox: 最高安全性，完全隔离，性能开销较大")
        print("4. 🔒 安全检查能有效拦截危险代码")
        print("5. ⚡ 不同沙箱有不同的性能特征")
        
        print("\n🚀 下一步:")
        print("- 运行 'python main.py' 进入交互式模式")
        print("- 运行 'python main.py --demo' 查看完整演示")
        print("- 运行 'python main.py --benchmark' 进行性能测试")
        
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        print("💡 请检查依赖是否正确安装")


if __name__ == "__main__":
    main()