"""
主程序入口

简单聊天机器人的主程序入口点。
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cli import main as cli_main
from logger import logger
from exceptions import ConfigurationError


def check_environment() -> None:
    """检查运行环境"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  未找到 .env 文件")
            print(f"📝 请复制 {env_example} 为 .env 并配置您的 API 密钥")
            print("💡 或者设置 OPENAI_API_KEY 环境变量")
        else:
            print("⚠️  未找到配置文件")
            print("💡 请设置 OPENAI_API_KEY 环境变量")
        print()
    
    # 检查 API 密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 未设置 OPENAI_API_KEY")
        print("💡 请在 .env 文件中设置您的 OpenAI API 密钥")
        print("   或者设置环境变量: set OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)


async def main():
    """主函数"""
    try:
        # 检查环境
        check_environment()
        
        # 启动 CLI
        logger.info("启动聊天机器人...")
        await cli_main()
        
    except ConfigurationError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        logger.error(f"程序运行时发生错误: {e}")
        print(f"❌ 程序运行时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())