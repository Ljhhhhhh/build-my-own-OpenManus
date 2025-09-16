# OpenManus AI 应用开发快速开始模板

## 项目结构模板

```
ai_agent_project/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── agent_config.toml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── react.py
│   │   └── tool_calling.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── calculator.py
│   │   ├── weather.py
│   │   └── manager.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── conversation.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_memory.py
├── examples/
│   ├── simple_chat.py
│   ├── tool_calling_demo.py
│   └── react_demo.py
└── docs/
    ├── architecture.md
    ├── api_reference.md
    └── deployment.md
```

## 快速开始脚本

### setup.py

```python
#!/usr/bin/env python3
"""
快速设置脚本
运行此脚本来初始化项目环境
"""

import os
import subprocess
import sys
from pathlib import Path

def create_virtual_env():
    """创建虚拟环境"""
    print("🔧 创建虚拟环境...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    print("✅ 虚拟环境创建完成")

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")

    # 根据操作系统选择激活脚本
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        pip_path = "venv/bin/pip"

    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("✅ 依赖安装完成")

def create_env_file():
    """创建环境变量文件"""
    print("🔑 创建环境配置文件...")

    env_content = """
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 其他API配置
WEATHER_API_KEY=your_weather_api_key_here

# 应用配置
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=20
MAX_REACT_STEPS=10

# 开发配置
DEBUG=True
TEST_MODE=False
    """.strip()

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("✅ 环境配置文件创建完成")
    print("⚠️  请编辑 .env 文件，填入你的API密钥")

def create_project_structure():
    """创建项目目录结构"""
    print("📁 创建项目目录结构...")

    directories = [
        "src/agent",
        "src/tools",
        "src/memory",
        "src/utils",
        "config",
        "tests",
        "examples",
        "docs",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # 创建 __init__.py 文件
        if directory.startswith("src/"):
            init_file = Path(directory) / "__init__.py"
            init_file.touch()

    print("✅ 项目目录结构创建完成")

def main():
    """主函数"""
    print("🚀 OpenManus AI应用开发环境初始化")
    print("=" * 50)

    try:
        create_project_structure()
        create_virtual_env()
        install_dependencies()
        create_env_file()

        print("\n🎉 项目初始化完成！")
        print("\n下一步：")
        print("1. 编辑 .env 文件，填入你的API密钥")
        print("2. 激活虚拟环境：")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("3. 运行示例：python examples/simple_chat.py")

    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### requirements.txt

```
# 核心依赖
openai>=1.0.0
pydantic>=2.0.0
aiohttp>=3.8.0
python-dotenv>=1.0.0

# 配置管理
toml>=0.10.2
pyyaml>=6.0

# 工具相关
requests>=2.28.0
jsonschema>=4.0.0

# 日志和调试
loguru>=0.7.0
rich>=13.0.0

# 测试
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# 开发工具
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# 可选依赖（根据需要取消注释）
# playwright>=1.40.0  # 浏览器自动化
# pillow>=10.0.0      # 图像处理
# docker>=6.0.0       # Docker集成
# fastapi>=0.104.0    # Web API
# uvicorn>=0.24.0     # ASGI服务器
```

## 核心模板文件

### src/main.py

```python
#!/usr/bin/env python3
"""
OpenManus AI应用主入口
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
os.sys.path.insert(0, str(project_root))

from src.agent.tool_calling import ToolCallingAgent
from src.utils.logger import setup_logger

def check_environment():
    """检查环境配置"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        logger.info("请检查 .env 文件配置")
        return False

    return True

async def interactive_chat():
    """交互式聊天"""
    if not check_environment():
        return

    # 初始化代理
    agent = ToolCallingAgent(
        api_key=os.getenv("OPENAI_API_KEY"),
        weather_api_key=os.getenv("WEATHER_API_KEY")
    )

    logger.info("🤖 AI助手已启动！")
    logger.info("可用工具：")
    for tool in agent.get_available_tools():
        logger.info(f"  - {tool['name']}: {tool['description']}")

    logger.info("\n输入 'quit' 或 'exit' 退出")
    logger.info("输入 'clear' 清空对话历史")
    logger.info("输入 'tools' 查看可用工具")

    while True:
        try:
            user_input = input("\n👤 你: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                logger.info("👋 再见！")
                break
            elif user_input.lower() == 'clear':
                agent.clear_history()
                logger.info("🧹 对话历史已清空")
                continue
            elif user_input.lower() == 'tools':
                logger.info("🔧 可用工具：")
                for tool in agent.get_available_tools():
                    logger.info(f"  - {tool['name']}: {tool['description']}")
                continue
            elif not user_input:
                continue

            # 处理用户消息
            logger.info("🤔 思考中...")
            response = await agent.process_message(user_input)
            logger.info(f"🤖 助手: {response}")

        except KeyboardInterrupt:
            logger.info("\n👋 再见！")
            break
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")

async def batch_process():
    """批处理模式"""
    # 这里可以实现批量处理逻辑
    pass

def main():
    """主函数"""
    # 设置日志
    setup_logger()

    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="OpenManus AI应用")
    parser.add_argument("--mode", choices=["chat", "batch"], default="chat",
                       help="运行模式：chat(交互式) 或 batch(批处理)")
    parser.add_argument("--config", help="配置文件路径")

    args = parser.parse_args()

    try:
        if args.mode == "chat":
            asyncio.run(interactive_chat())
        elif args.mode == "batch":
            asyncio.run(batch_process())
    except Exception as e:
        logger.error(f"应用启动失败: {e}")

if __name__ == "__main__":
    main()
```

### src/utils/logger.py

```python
"""
日志配置模块
"""

import os
import sys
from pathlib import Path
from loguru import logger

def setup_logger(log_level: str = None, log_file: str = None):
    """设置日志配置"""
    # 移除默认处理器
    logger.remove()

    # 获取日志级别
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")

    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True
    )

    # 添加文件处理器
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_file or log_dir / "app.log"

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )

    logger.add(
        log_file,
        format=file_format,
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )

    logger.info(f"日志系统已初始化，级别: {log_level}")
```

### config/agent_config.toml

```toml
# AI代理配置文件

[agent]
name = "OpenManus助手"
description = "基于OpenManus架构的AI助手"
max_conversation_history = 20
max_react_steps = 10
system_prompt = """
你是一个智能AI助手，能够使用各种工具来帮助用户解决问题。
你应该：
1. 仔细理解用户的需求
2. 选择合适的工具来完成任务
3. 提供清晰、准确的回答
4. 在必要时询问澄清问题
"""

[llm]
provider = "openai"
model = "gpt-3.5-turbo"
max_tokens = 1500
temperature = 0.7
top_p = 1.0
frequency_penalty = 0.0
presence_penalty = 0.0

[tools]
# 启用的工具列表
enabled = ["calculator", "weather"]

[tools.calculator]
enabled = true
max_expression_length = 1000

[tools.weather]
enabled = true
default_country = "CN"
cache_duration = 300  # 5分钟缓存

[memory]
type = "conversation"
max_tokens = 4000
compression_threshold = 0.8

[logging]
level = "INFO"
file_rotation = "10 MB"
file_retention = "7 days"
```

## 示例文件

### examples/simple_chat.py

```python
#!/usr/bin/env python3
"""
简单聊天机器人示例
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from src.agent.tool_calling import ToolCallingAgent

async def main():
    """简单聊天示例"""
    print("🤖 简单聊天机器人示例")
    print("=" * 30)

    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请在 .env 文件中设置 OPENAI_API_KEY")
        return

    # 创建代理
    agent = ToolCallingAgent(api_key=api_key)

    print("助手已启动！输入 'quit' 退出\n")

    # 预设问题
    sample_questions = [
        "你好！",
        "计算 15 * 23 + 45",
        "什么是人工智能？",
        "帮我解释一下Python的装饰器"
    ]

    print("💡 你可以尝试这些问题：")
    for i, q in enumerate(sample_questions, 1):
        print(f"  {i}. {q}")
    print()

    while True:
        try:
            user_input = input("👤 你: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break

            if not user_input:
                continue

            response = await agent.process_message(user_input)
            print(f"🤖 助手: {response}\n")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

### tests/test_agent.py

```python
"""
代理测试模块
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

# 这里需要根据实际的代理实现进行测试

@pytest.mark.asyncio
async def test_agent_initialization():
    """测试代理初始化"""
    # 模拟测试
    pass

@pytest.mark.asyncio
async def test_tool_calling():
    """测试工具调用"""
    # 模拟测试
    pass

@pytest.mark.asyncio
async def test_conversation_memory():
    """测试对话记忆"""
    # 模拟测试
    pass
```

## 快速部署脚本

### deploy.sh (Linux/MacOS)

```bash
#!/bin/bash

# OpenManus AI应用部署脚本

set -e

echo "🚀 开始部署 OpenManus AI应用"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 创建项目目录
PROJECT_NAME="my_ai_agent"
echo "📁 创建项目目录: $PROJECT_NAME"
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# 下载项目模板（这里假设有一个模板仓库）
echo "📥 下载项目模板"
# git clone https://github.com/your-repo/openManus-template.git .

# 创建虚拟环境
echo "🔧 创建虚拟环境"
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖"
pip install -r requirements.txt

# 创建配置文件
echo "⚙️ 创建配置文件"
cp .env.example .env

echo "✅ 部署完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，填入你的API密钥"
echo "2. 激活虚拟环境: source venv/bin/activate"
echo "3. 运行应用: python src/main.py"
```

### deploy.bat (Windows)

```batch
@echo off
echo 🚀 开始部署 OpenManus AI应用

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到PATH
    pause
    exit /b 1
)

REM 创建项目目录
set PROJECT_NAME=my_ai_agent
echo 📁 创建项目目录: %PROJECT_NAME%
mkdir %PROJECT_NAME%
cd %PROJECT_NAME%

REM 创建虚拟环境
echo 🔧 创建虚拟环境
python -m venv venv
call venv\Scripts\activate

REM 安装依赖
echo 📦 安装依赖
pip install -r requirements.txt

REM 创建配置文件
echo ⚙️ 创建配置文件
copy .env.example .env

echo ✅ 部署完成！
echo.
echo 下一步：
echo 1. 编辑 .env 文件，填入你的API密钥
echo 2. 激活虚拟环境: venv\Scripts\activate
echo 3. 运行应用: python src\main.py
pause
```

## 使用说明

### 1. 快速开始

```bash
# 1. 克隆或下载项目模板
git clone <template-repo> my_ai_project
cd my_ai_project

# 2. 运行初始化脚本
python setup.py

# 3. 编辑环境配置
# 编辑 .env 文件，填入你的API密钥

# 4. 激活虚拟环境
source venv/bin/activate  # Linux/MacOS
# 或
venv\Scripts\activate     # Windows

# 5. 运行应用
python src/main.py
```

### 2. 开发模式

```bash
# 安装开发依赖
pip install -e .

# 运行测试
pytest tests/

# 代码格式化
black src/

# 类型检查
mypy src/
```

### 3. 生产部署

```bash
# 使用Docker部署
docker build -t my-ai-agent .
docker run -d --name ai-agent -p 8000:8000 my-ai-agent

# 或使用systemd服务
sudo cp deploy/ai-agent.service /etc/systemd/system/
sudo systemctl enable ai-agent
sudo systemctl start ai-agent
```

## 常见问题解决

### Q1: 虚拟环境创建失败

**解决方案：**

```bash
# 确保Python版本 >= 3.8
python --version

# 如果使用conda
conda create -n ai_agent python=3.9
conda activate ai_agent
```

### Q2: 依赖安装失败

**解决方案：**

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Q3: API 调用失败

**解决方案：**

1. 检查 API 密钥是否正确
2. 检查网络连接
3. 确认 API 配额是否充足
4. 查看日志文件获取详细错误信息

### Q4: 工具调用异常

**解决方案：**

1. 检查工具参数格式
2. 确认工具权限设置
3. 查看工具执行日志
4. 验证 JSON Schema 定义

通过这个快速开始模板，你可以在几分钟内搭建起一个完整的 AI 应用开发环境，并开始你的学习和开发之旅！
