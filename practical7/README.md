# 项目7：沙箱执行环境

> 🚀 **三阶段渐进式学习项目** - 从基础进程隔离到Docker容器完全隔离

一个完整的代码执行沙箱实现，展示了从简单到复杂的三个发展阶段，帮助开发者深入理解沙箱技术的核心原理和实际应用。

## 🎯 项目目标

通过**渐进式学习**掌握沙箱环境的核心概念和实战技能：

1. **理解沙箱本质**：从最简单的代码隔离开始
2. **掌握核心技术**：逐步学习 subprocess → 安全检查 → Docker 的演进
3. **实战驱动学习**：每个阶段都有可运行的完整代码
4. **循序渐进**：从 30 行代码到完整沙箱系统

## 🏗️ 架构设计

### 三层渐进式架构

```
阶段1：基础沙箱 (30行核心代码)
┌─────────────────────────────────┐
│        SimpleSandbox            │
│  ┌─────────────────────────────┐ │
│  │    subprocess.run()         │ │
│  └─────────────────────────────┘ │
└─────────────────────────────────┘

阶段2：安全沙箱 (100行安全增强)
┌─────────────────────────────────┐
│        SafeSandbox              │
│  ┌─────────────┐ ┌─────────────┐ │
│  │ 资源限制     │ │ 安全检查     │ │
│  └─────────────┘ └─────────────┘ │
└─────────────────────────────────┘

阶段3：Docker沙箱 (200行容器隔离)
┌─────────────────────────────────┐
│       DockerSandbox             │
│  ┌─────────────┐ ┌─────────────┐ │
│  │ 容器隔离     │ │ 镜像管理     │ │
│  └─────────────┘ └─────────────┘ │
└─────────────────────────────────┘
```

## 📁 项目结构

```
practical7/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖包
├── .env.example                # 环境配置示例
├── main.py                     # 主程序入口
├── demo.py                     # 快速演示程序
├── stage1_simple_sandbox.py     # 阶段1：基础沙箱
├── stage2_safe_sandbox.py       # 阶段2：安全沙箱
├── stage3_docker_sandbox.py     # 阶段3：Docker沙箱
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   └── logger.py               # 日志工具
├── tests/                      # 测试用例
│   ├── __init__.py
│   ├── test_stage1.py          # 阶段1测试
│   ├── test_stage2.py          # 阶段2测试
│   └── test_stage3.py          # 阶段3测试
└── examples/                   # 使用示例
    ├── __init__.py
    ├── basic_usage.py          # 基础使用示例
    ├── security_demo.py        # 安全演示
    └── docker_demo.py          # Docker演示
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd practical7

# 安装Python依赖
pip install -r requirements.txt

# 可选：安装Docker（用于阶段3）
# 请参考Docker官方文档安装
```

### 2. 快速演示

```bash
# 运行快速演示（推荐首次使用）
python demo.py

# 运行完整演示
python main.py --demo

# 进入交互式模式
python main.py

# 性能测试
python main.py --benchmark
```

### 3. 单独测试各阶段

```bash
# 测试阶段1：基础沙箱
python stage1_simple_sandbox.py
python tests/test_stage1.py

# 测试阶段2：安全沙箱
python stage2_safe_sandbox.py
python tests/test_stage2.py

# 测试阶段3：Docker沙箱（需要Docker）
python stage3_docker_sandbox.py
python tests/test_stage3.py
```

## 📚 三个学习阶段

### 🚀 阶段1：基础沙箱 (SimpleSandbox)

**目标**：理解沙箱的本质概念

**核心特性**：
- ✅ 进程隔离：使用 `subprocess` 创建独立进程
- ✅ 输入输出控制：捕获程序输出和错误
- ✅ 超时保护：防止无限循环
- ✅ 资源清理：自动清理临时文件
- ✅ 多语言支持：Python、JavaScript

**核心代码**（30行）：
```python
def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
    # 1. 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # 2. 执行代码
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'execution_time': time.time() - start_time
        }
    finally:
        # 3. 清理临时文件
        os.unlink(temp_file)
```

### 🛡️ 阶段2：安全沙箱 (SafeSandbox)

**目标**：添加安全控制和资源限制

**新增特性**：
- 🔒 代码安全检查：检测危险操作和恶意代码
- 📊 资源限制：内存和CPU时间限制
- 🚫 黑名单过滤：阻止危险的导入和函数调用
- ✅ 白名单机制：只允许安全的操作
- 🌳 AST分析：深层语法树安全检查

**安全检查示例**：
```python
def _validate_code_security(self, code: str) -> Dict[str, Any]:
    # 1. 检查危险关键词
    dangerous_keywords = ['os.system', 'eval', 'exec', 'subprocess']
    
    # 2. 检查危险导入
    dangerous_imports = ['os', 'sys', 'subprocess', 'socket']
    
    # 3. AST语法树分析
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.func.id in ['eval', 'exec']:
            return {'is_safe': False, 'reason': '包含危险函数调用'}
    
    return {'is_safe': True, 'reason': ''}
```

### 🐳 阶段3：Docker沙箱 (DockerSandbox)

**目标**：使用Docker容器实现完全隔离

**最高级特性**：
- 🐳 容器隔离：完全独立的运行环境
- 🔒 网络隔离：禁用网络访问
- 📁 文件系统隔离：只读挂载
- 👤 用户权限控制：非root用户执行
- 📦 镜像管理：自动拉取和管理Docker镜像
- 🧹 自动清理：容器执行完成后自动删除

**Docker配置示例**：
```python
container_config = {
    'image': 'python:3.9-slim',
    'command': ['python', '/workspace/code.py'],
    'volumes': {code_dir: {'bind': '/workspace', 'mode': 'ro'}},
    'mem_limit': '128m',
    'network_disabled': True,  # 网络隔离
    'user': '1000:1000',      # 非root用户
    'remove': True            # 自动删除
}
```

## 🔧 使用方法

### 命令行接口

```bash
# 交互式模式
python main.py

# 执行单行代码
python main.py --execute "print('Hello World')" --sandbox safe

# 指定语言和沙箱类型
python main.py --execute "console.log('Hello')" --language javascript --sandbox docker

# 输出结果到文件
python main.py --execute "print('test')" --output result.json

# 静默模式
python main.py --execute "print('test')" --quiet
```

### 编程接口

```python
from stage2_safe_sandbox import SafeSandbox

# 创建安全沙箱
sandbox = SafeSandbox(
    timeout=10,           # 超时时间
    memory_limit=128,     # 内存限制(MB)
    enable_security=True  # 启用安全检查
)

# 执行Python代码
result = sandbox.execute("""
import math
print(f"π = {math.pi:.6f}")
""", "python")

if result['success']:
    print("输出:", result['output'])
else:
    print("错误:", result['error'])
```

### 交互式模式命令

在交互式模式中，支持以下命令：

```
help                    - 显示帮助信息
quit/exit/q            - 退出程序
sandbox <type>         - 切换沙箱类型 (simple/safe/docker)
language <lang>        - 切换编程语言 (python/javascript)
info                   - 显示当前沙箱信息
compare                - 比较不同沙箱的执行结果
<code>                 - 直接执行代码
```

## 🧪 测试和验证

### 运行测试套件

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定阶段测试
python tests/test_stage1.py
python tests/test_stage2.py
python tests/test_stage3.py  # 需要Docker

# 运行性能测试
python main.py --benchmark
```

### 安全测试示例

```python
# 测试危险代码拦截
dangerous_codes = [
    "import os; os.system('rm -rf /')",  # 系统命令
    "eval('malicious_code')",            # 动态执行
    "open('/etc/passwd').read()",        # 文件访问
]

safe_sandbox = SafeSandbox(enable_security=True)
for code in dangerous_codes:
    result = safe_sandbox.execute(code)
    assert not result['success']  # 应该被拦截
```

## 📊 性能对比

基于实际测试的性能数据：

| 沙箱类型 | 启动时间 | 执行开销 | 安全级别 | 隔离程度 |
|---------|---------|---------|---------|---------|
| SimpleSandbox | ~0.01s | 最低 | ⭐ | 进程级 |
| SafeSandbox | ~0.02s | 低 | ⭐⭐⭐ | 进程级+安全检查 |
| DockerSandbox | ~0.2s | 中等 | ⭐⭐⭐⭐⭐ | 容器级完全隔离 |

**选择建议**：
- 🏃‍♂️ **高性能场景**：使用 SimpleSandbox
- ⚖️ **平衡场景**：使用 SafeSandbox（推荐）
- 🔒 **高安全场景**：使用 DockerSandbox

## 🔒 安全特性

### 阶段2安全检查

- ✅ **关键词检测**：`os.system`, `eval`, `exec`, `subprocess` 等
- ✅ **模块导入控制**：黑名单 + 白名单机制
- ✅ **AST语法分析**：深层代码结构检查
- ✅ **资源限制**：内存、CPU时间限制

### 阶段3容器隔离

- 🐳 **完全隔离**：独立的进程空间、文件系统、网络
- 🔒 **网络隔离**：禁用所有网络访问
- 📁 **只读文件系统**：防止恶意文件操作
- 👤 **非特权用户**：以普通用户身份运行
- ⏱️ **资源限制**：精确的内存和CPU控制

## 🌍 支持的编程语言

| 语言 | 阶段1 | 阶段2 | 阶段3 | Docker镜像 |
|-----|-------|-------|-------|------------|
| Python | ✅ | ✅ | ✅ | python:3.9-slim |
| JavaScript | ✅ | ❌ | ✅ | node:18-alpine |
| Java | ❌ | ❌ | ✅ | openjdk:11-jre-slim |
| Go | ❌ | ❌ | ✅ | golang:1.19-alpine |

> 注：阶段2的安全检查目前只支持Python，其他语言会跳过安全检查

## 🛠️ 配置选项

### 环境变量配置

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
SANDBOX_TIMEOUT=30                    # 默认超时时间（秒）
SANDBOX_MEMORY_LIMIT=128             # 内存限制（MB）
DOCKER_MEMORY_LIMIT=128m             # Docker容器内存限制
DOCKER_NETWORK_DISABLED=true        # 是否禁用网络
LOG_LEVEL=INFO                       # 日志级别
```

### 编程配置

```python
from utils.config import get_config, set_config

# 获取配置
timeout = get_config('timeout', 30)

# 设置配置
set_config('timeout', 60)
```

## 🚨 故障排除

### 常见问题

1. **Docker相关错误**
   ```bash
   # 检查Docker状态
   docker --version
   docker run hello-world
   
   # 确保Docker服务运行
   sudo systemctl start docker  # Linux
   # 或启动Docker Desktop      # macOS/Windows
   ```

2. **权限问题**
   ```bash
   # 添加用户到docker组（Linux）
   sudo usermod -aG docker $USER
   # 重新登录生效
   ```

3. **依赖安装问题**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

4. **资源限制失败**
   - 某些系统可能不支持资源限制
   - 这不影响基本功能，只是警告信息

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或设置环境变量
export LOG_LEVEL=DEBUG
```

## 🎓 学习要点

### 对于JavaScript开发者

| 概念 | JavaScript等价 | Python沙箱实现 |
|------|----------------|----------------|
| 进程隔离 | `child_process.spawn()` | `subprocess.run()` |
| 代码执行 | `vm.runInNewContext()` | `exec()` in subprocess |
| 容器化 | Docker for Node.js | Docker for Python |
| 资源限制 | `--max-old-space-size` | `resource.setrlimit()` |
| 超时控制 | `setTimeout()` | `timeout` parameter |

### 核心概念掌握

1. **进程隔离**：每次执行都在独立进程中
2. **输入输出控制**：捕获程序的所有输出
3. **超时保护**：防止程序无限运行
4. **安全检查**：静态分析检测危险操作
5. **资源限制**：控制内存和CPU使用
6. **容器隔离**：Docker提供的完全隔离

## 🤝 贡献指南

欢迎贡献代码和改进建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢 Docker 社区提供的优秀容器技术
- 感谢 Python 社区的 subprocess 和 ast 模块
- 感谢所有为开源安全工具做出贡献的开发者

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)

---

> 🎯 **学习目标达成**：通过这个项目，你将深入理解沙箱技术的核心原理，掌握从基础到高级的三种实现方式，为构建安全的代码执行环境打下坚实基础！