"""
项目7：沙箱执行环境 - 主程序入口

这是一个完整的沙箱执行环境实现，展示了从基础到高级的三个阶段：
1. 阶段1：基础沙箱 - subprocess进程隔离
2. 阶段2：安全沙箱 - 代码安全检查和资源限制
3. 阶段3：Docker沙箱 - 容器完全隔离

对于JavaScript开发者：
这类似于一个完整的代码执行平台，如CodePen、JSFiddle或在线IDE
"""

import sys
import os
import argparse
import json
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stage1_simple_sandbox import SimpleSandbox
from stage2_safe_sandbox import SafeSandbox
from stage3_docker_sandbox import DockerSandbox
from utils.logger import get_logger
from utils.config import get_config


class SandboxManager:
    """沙箱管理器 - 统一管理三个阶段的沙箱实现"""
    
    def __init__(self):
        """初始化沙箱管理器"""
        self.logger = get_logger("SandboxManager")
        self.sandboxes = {}
        self._init_sandboxes()
    
    def _init_sandboxes(self):
        """初始化所有沙箱实例"""
        try:
            # 阶段1：基础沙箱
            self.sandboxes['simple'] = SimpleSandbox(
                timeout=get_config('timeout', 10)
            )
            self.logger.info("SimpleSandbox初始化成功")
            
            # 阶段2：安全沙箱
            self.sandboxes['safe'] = SafeSandbox(
                timeout=get_config('timeout', 10),
                memory_limit=get_config('memory_limit', 128),
                enable_security=True
            )
            self.logger.info("SafeSandbox初始化成功")
            
            # 阶段3：Docker沙箱（可能失败）
            try:
                self.sandboxes['docker'] = DockerSandbox(
                    timeout=get_config('timeout', 30),
                    memory_limit=get_config('docker_memory_limit', '128m'),
                    enable_network=False
                )
                self.logger.info("DockerSandbox初始化成功")
            except Exception as e:
                self.logger.warning(f"DockerSandbox初始化失败: {e}")
                self.sandboxes['docker'] = None
                
        except Exception as e:
            self.logger.error(f"沙箱初始化失败: {e}")
            raise
    
    def execute(self, code: str, language: str = "python", sandbox_type: str = "safe") -> Dict[str, Any]:
        """执行代码
        
        Args:
            code: 要执行的代码
            language: 编程语言
            sandbox_type: 沙箱类型 ('simple', 'safe', 'docker')
            
        Returns:
            执行结果字典
        """
        if sandbox_type not in self.sandboxes:
            return {
                'success': False,
                'error': f'不支持的沙箱类型: {sandbox_type}',
                'sandbox_type': sandbox_type,
                'execution_time': 0
            }
        
        sandbox = self.sandboxes[sandbox_type]
        if sandbox is None:
            return {
                'success': False,
                'error': f'沙箱 {sandbox_type} 不可用',
                'sandbox_type': sandbox_type,
                'execution_time': 0
            }
        
        try:
            result = sandbox.execute(code, language)
            result['sandbox_type'] = sandbox_type
            return result
        except Exception as e:
            self.logger.error(f"代码执行异常: {e}")
            return {
                'success': False,
                'error': f'执行异常: {str(e)}',
                'sandbox_type': sandbox_type,
                'execution_time': 0
            }
    
    def get_sandbox_info(self, sandbox_type: str) -> Dict[str, Any]:
        """获取沙箱信息"""
        if sandbox_type not in self.sandboxes:
            return {'error': f'不支持的沙箱类型: {sandbox_type}'}
        
        sandbox = self.sandboxes[sandbox_type]
        if sandbox is None:
            return {'error': f'沙箱 {sandbox_type} 不可用'}
        
        return sandbox.get_info()
    
    def get_available_sandboxes(self) -> Dict[str, bool]:
        """获取可用的沙箱列表"""
        return {
            name: sandbox is not None 
            for name, sandbox in self.sandboxes.items()
        }
    
    def compare_sandboxes(self, code: str, language: str = "python") -> Dict[str, Any]:
        """比较不同沙箱的执行结果"""
        results = {}
        
        for sandbox_type, sandbox in self.sandboxes.items():
            if sandbox is not None:
                try:
                    result = sandbox.execute(code, language)
                    results[sandbox_type] = {
                        'success': result['success'],
                        'execution_time': result['execution_time'],
                        'output_length': len(result.get('output', '')),
                        'error': result.get('error', '') if not result['success'] else None
                    }
                except Exception as e:
                    results[sandbox_type] = {
                        'success': False,
                        'execution_time': 0,
                        'output_length': 0,
                        'error': str(e)
                    }
            else:
                results[sandbox_type] = {
                    'success': False,
                    'execution_time': 0,
                    'output_length': 0,
                    'error': '沙箱不可用'
                }
        
        return results


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 沙箱执行环境 v1.0                      ║
║                                                              ║
║  三阶段渐进式学习：                                           ║
║  📦 阶段1: SimpleSandbox  - 基础进程隔离                     ║
║  🛡️  阶段2: SafeSandbox    - 安全检查和资源限制              ║
║  🐳 阶段3: DockerSandbox  - 容器完全隔离                     ║
║                                                              ║
║  支持语言: Python, JavaScript, Java, Go                     ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def interactive_mode():
    """交互式模式"""
    print("🎯 进入交互式模式")
    print("输入 'help' 查看帮助，输入 'quit' 退出\n")
    
    manager = SandboxManager()
    
    # 显示可用沙箱
    available = manager.get_available_sandboxes()
    print("📦 可用沙箱:")
    for name, is_available in available.items():
        status = "✅" if is_available else "❌"
        print(f"  {status} {name}")
    print()
    
    current_sandbox = "safe"  # 默认使用安全沙箱
    current_language = "python"  # 默认使用Python
    
    while True:
        try:
            command = input(f"[{current_sandbox}:{current_language}] > ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if command.lower() == 'help':
                print_help()
                continue
            
            if command.startswith('sandbox '):
                new_sandbox = command.split()[1]
                if new_sandbox in available and available[new_sandbox]:
                    current_sandbox = new_sandbox
                    print(f"✅ 切换到沙箱: {current_sandbox}")
                else:
                    print(f"❌ 沙箱不可用: {new_sandbox}")
                continue
            
            if command.startswith('language '):
                new_language = command.split()[1]
                current_language = new_language
                print(f"✅ 切换到语言: {current_language}")
                continue
            
            if command == 'info':
                info = manager.get_sandbox_info(current_sandbox)
                print(f"📋 {current_sandbox} 沙箱信息:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                continue
            
            if command == 'compare':
                print("请输入要比较的代码（输入空行结束）:")
                code_lines = []
                while True:
                    line = input("  ")
                    if not line:
                        break
                    code_lines.append(line)
                
                if code_lines:
                    code = '\n'.join(code_lines)
                    results = manager.compare_sandboxes(code, current_language)
                    print("\n📊 沙箱比较结果:")
                    for sandbox_type, result in results.items():
                        status = "✅" if result['success'] else "❌"
                        print(f"  {status} {sandbox_type}: {result['execution_time']:.3f}s")
                        if result['error']:
                            print(f"    错误: {result['error']}")
                continue
            
            # 执行代码
            if command.startswith('exec '):
                code = command[5:]  # 去掉 'exec ' 前缀
            else:
                code = command
            
            result = manager.execute(code, current_language, current_sandbox)
            
            if result['success']:
                print(f"✅ 执行成功 ({result['execution_time']:.3f}s)")
                if result.get('output'):
                    print("📤 输出:")
                    print(result['output'])
            else:
                print(f"❌ 执行失败 ({result['execution_time']:.3f}s)")
                print(f"🚨 错误: {result['error']}")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 异常: {e}")


def print_help():
    """打印帮助信息"""
    help_text = """
🔧 可用命令:
  help                    - 显示此帮助信息
  quit/exit/q            - 退出程序
  sandbox <type>         - 切换沙箱类型 (simple/safe/docker)
  language <lang>        - 切换编程语言 (python/javascript/java/go)
  info                   - 显示当前沙箱信息
  compare                - 比较不同沙箱的执行结果
  exec <code>            - 执行代码
  <code>                 - 直接执行代码

📝 示例:
  sandbox docker         - 切换到Docker沙箱
  language javascript    - 切换到JavaScript
  print("Hello World")   - 执行Python代码
  console.log("Hello")   - 执行JavaScript代码
"""
    print(help_text)


def demo_mode():
    """演示模式"""
    print("🎬 运行完整演示\n")
    
    manager = SandboxManager()
    
    # 演示代码示例
    demo_codes = [
        {
            "title": "基础数学计算",
            "language": "python",
            "code": """
import math
print("🧮 数学计算演示")
print(f"π = {math.pi:.6f}")
print(f"e = {math.e:.6f}")
print(f"sqrt(2) = {math.sqrt(2):.6f}")
"""
        },
        {
            "title": "JavaScript数组操作",
            "language": "javascript",
            "code": """
console.log("📊 JavaScript数组操作演示");
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`原数组: ${numbers}`);
console.log(`翻倍后: ${doubled}`);
console.log(`总和: ${sum}`);
"""
        },
        {
            "title": "数据处理",
            "language": "python",
            "code": """
import json
from datetime import datetime

data = {
    "timestamp": datetime.now().isoformat(),
    "users": [
        {"name": "Alice", "age": 25, "city": "北京"},
        {"name": "Bob", "age": 30, "city": "上海"},
        {"name": "Charlie", "age": 35, "city": "深圳"}
    ]
}

print("👥 用户数据处理")
print(f"总用户数: {len(data['users'])}")
avg_age = sum(user['age'] for user in data['users']) / len(data['users'])
print(f"平均年龄: {avg_age:.1f}岁")

cities = set(user['city'] for user in data['users'])
print(f"涉及城市: {', '.join(cities)}")
"""
        }
    ]
    
    # 获取可用沙箱
    available = manager.get_available_sandboxes()
    sandbox_types = [name for name, is_available in available.items() if is_available]
    
    print(f"📦 将在以下沙箱中运行演示: {', '.join(sandbox_types)}\n")
    
    for i, demo in enumerate(demo_codes, 1):
        print(f"{'='*60}")
        print(f"🎯 演示 {i}: {demo['title']} ({demo['language'].upper()})")
        print('='*60)
        
        for sandbox_type in sandbox_types:
            print(f"\n🔧 使用 {sandbox_type} 沙箱:")
            
            result = manager.execute(demo['code'], demo['language'], sandbox_type)
            
            if result['success']:
                print(f"✅ 执行成功 - 耗时: {result['execution_time']:.3f}秒")
                if result.get('container_id'):
                    print(f"🐳 容器ID: {result['container_id']}")
                if result.get('output'):
                    print("📤 输出:")
                    for line in result['output'].split('\n'):
                        if line.strip():
                            print(f"   {line}")
            else:
                print(f"❌ 执行失败 - 耗时: {result['execution_time']:.3f}秒")
                print(f"🚨 错误: {result['error']}")
        
        print()
    
    print("🎉 演示完成！")


def benchmark_mode():
    """性能测试模式"""
    print("⚡ 性能测试模式\n")
    
    manager = SandboxManager()
    available = manager.get_available_sandboxes()
    
    # 性能测试代码
    benchmark_code = """
# 计算斐波那契数列（递归版本）
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 计算前20个斐波那契数
results = []
for i in range(20):
    fib = fibonacci(i)
    results.append(fib)

print(f"前20个斐波那契数: {results}")
print(f"第19个斐波那契数: {results[-1]}")
"""
    
    print("🧮 性能测试：计算斐波那契数列")
    print("代码长度:", len(benchmark_code), "字符")
    print()
    
    results = {}
    
    for sandbox_type, is_available in available.items():
        if not is_available:
            continue
        
        print(f"🔧 测试 {sandbox_type} 沙箱...")
        
        # 运行3次取平均值
        times = []
        for run in range(3):
            result = manager.execute(benchmark_code, "python", sandbox_type)
            if result['success']:
                times.append(result['execution_time'])
            else:
                print(f"  ❌ 第{run+1}次运行失败: {result['error']}")
                break
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            results[sandbox_type] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'runs': len(times)
            }
            
            print(f"  ✅ 平均耗时: {avg_time:.3f}秒")
            print(f"  📊 最快: {min_time:.3f}秒, 最慢: {max_time:.3f}秒")
        else:
            results[sandbox_type] = None
            print(f"  ❌ 测试失败")
        
        print()
    
    # 性能比较
    if len([r for r in results.values() if r is not None]) > 1:
        print("📊 性能比较:")
        sorted_results = sorted(
            [(name, data) for name, data in results.items() if data is not None],
            key=lambda x: x[1]['avg_time']
        )
        
        fastest = sorted_results[0]
        print(f"🏆 最快: {fastest[0]} ({fastest[1]['avg_time']:.3f}秒)")
        
        for i, (name, data) in enumerate(sorted_results[1:], 1):
            slowdown = data['avg_time'] / fastest[1]['avg_time']
            print(f"#{i+1}: {name} ({data['avg_time']:.3f}秒, {slowdown:.2f}x)")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="沙箱执行环境 - 三阶段渐进式学习项目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                    # 交互式模式
  python main.py --demo            # 演示模式
  python main.py --benchmark       # 性能测试模式
  python main.py --execute "print('Hello')" --sandbox safe
        """
    )
    
    parser.add_argument('--demo', action='store_true', help='运行演示模式')
    parser.add_argument('--benchmark', action='store_true', help='运行性能测试模式')
    parser.add_argument('--execute', '-e', help='执行指定代码')
    parser.add_argument('--language', '-l', default='python', help='编程语言 (默认: python)')
    parser.add_argument('--sandbox', '-s', default='safe', help='沙箱类型 (默认: safe)')
    parser.add_argument('--output', '-o', help='输出结果到文件')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    try:
        if args.demo:
            demo_mode()
        elif args.benchmark:
            benchmark_mode()
        elif args.execute:
            # 单次执行模式
            manager = SandboxManager()
            result = manager.execute(args.execute, args.language, args.sandbox)
            
            if args.output:
                # 输出到文件
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"✅ 结果已保存到: {args.output}")
            else:
                # 输出到控制台
                if result['success']:
                    print(f"✅ 执行成功 ({result['execution_time']:.3f}s)")
                    if result.get('output'):
                        print("📤 输出:")
                        print(result['output'])
                else:
                    print(f"❌ 执行失败 ({result['execution_time']:.3f}s)")
                    print(f"🚨 错误: {result['error']}")
        else:
            # 默认交互式模式
            interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())