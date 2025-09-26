"""
项目6：多模态代理 - 主程序入口

这个文件是多模态代理的主程序入口，提供命令行界面来测试各种功能。

学习要点：
- 命令行参数解析
- 异步主函数的实现
- 错误处理和用户友好的输出
- 配置管理的实际应用
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from agent import MultimodalAgent, MultimodalTaskType
from utils.config import get_config
from utils.logger import setup_logger


async def main():
    """主函数"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(
        description="多模态代理 - 支持图像分析和浏览器自动化的智能代理"
    )
    
    parser.add_argument(
        "query",
        help="用户查询或任务描述"
    )
    
    parser.add_argument(
        "--image", "-i",
        type=str,
        help="图像文件路径（支持jpg, png, gif等格式）"
    )
    
    parser.add_argument(
        "--task-type", "-t",
        choices=["image_analysis", "web_automation", "multimodal_search", "visual_web_task", "general"],
        default="general",
        help="任务类型（默认：general）"
    )
    
    parser.add_argument(
        "--max-steps", "-s",
        type=int,
        default=15,
        help="最大推理步骤数（默认：15）"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径（.env文件）"
    )
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = get_config(args.config)
        
        # 设置日志
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logger = setup_logger("multimodal_agent", level=log_level)
        
        logger.info("🚀 启动多模态代理...")
        
        # 验证图像文件
        image_path = None
        if args.image:
            image_path = Path(args.image)
            if not image_path.exists():
                print(f"❌ 错误：图像文件不存在 - {args.image}")
                return 1
            
            if not image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                print(f"❌ 错误：不支持的图像格式 - {image_path.suffix}")
                return 1
        
        # 创建多模态代理
        agent = MultimodalAgent(
            config=config,
            max_steps=args.max_steps
        )
        
        print(f"📝 任务: {args.query}")
        if image_path:
            print(f"🖼️  图像: {image_path}")
        print(f"🎯 任务类型: {args.task_type}")
        print("=" * 60)
        
        # 执行任务
        result = await agent.solve_multimodal(
            user_query=args.query,
            image=str(image_path) if image_path else None,
            task_type=args.task_type
        )
        
        # 显示结果
        print_result(result, args.verbose)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_result(result: dict, verbose: bool = False):
    """打印执行结果"""
    print("\n🎉 执行完成!")
    print("=" * 60)
    
    # 基本信息
    print(f"✅ 状态: {result['status']}")
    print(f"⏱️  执行时间: {result['execution_stats']['total_time']:.2f}秒")
    print(f"🔄 推理步骤: {result['execution_stats']['total_steps']}")
    
    # 多模态信息
    if 'multimodal_info' in result:
        multimodal_info = result['multimodal_info']
        print(f"🖼️  图像输入: {'是' if multimodal_info['had_image_input'] else '否'}")
        print(f"🛠️  使用工具: {', '.join(multimodal_info['tools_used'])}")
    
    print("\n📋 最终答案:")
    print("-" * 40)
    print(result.get('answer', '未找到答案'))
    
    # 详细信息
    if verbose:
        print("\n🔍 详细执行轨迹:")
        print("-" * 40)
        
        for i, step in enumerate(result.get('steps', []), 1):
            print(f"\n步骤 {i}:")
            print(f"  💭 思考: {step['thought']}")
            
            if step.get('action'):
                action = step['action']
                print(f"  🎬 行动: {action['name']}")
                if verbose and action.get('parameters'):
                    print(f"  📝 参数: {action['parameters']}")
            
            if step.get('observation'):
                obs = step['observation']
                if len(obs) > 200 and not verbose:
                    obs = obs[:200] + "..."
                print(f"  👀 观察: {obs}")
            
            print(f"  ⏱️  耗时: {step.get('execution_time', 0):.2f}秒")


def interactive_mode():
    """交互模式"""
    print("🤖 多模态代理 - 交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 60)
    
    try:
        config = get_config()
        logger = setup_logger("multimodal_agent", level=logging.INFO)
        
        # 创建代理（在交互模式中复用）
        agent = None
        
        while True:
            try:
                # 获取用户输入
                query = input("\n📝 请输入您的问题: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                # 询问是否有图像
                image_path = input("🖼️  图像路径（可选，直接回车跳过）: ").strip()
                if image_path and not Path(image_path).exists():
                    print("❌ 图像文件不存在，忽略图像输入")
                    image_path = None
                
                # 创建代理（如果还没有）
                if agent is None:
                    agent = MultimodalAgent(config=config)
                
                print("\n🔄 正在处理...")
                
                # 执行任务
                result = asyncio.run(agent.solve_multimodal(
                    user_query=query,
                    image=image_path if image_path else None,
                    task_type="general"
                ))
                
                # 显示结果
                print_result(result, verbose=False)
                
            except KeyboardInterrupt:
                print("\n⏹️  操作中断")
                continue
            except Exception as e:
                print(f"❌ 处理出错: {e}")
                continue
    
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return 1
    
    print("\n👋 再见!")
    return 0


if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) == 1:
        # 没有参数，启动交互模式
        exit_code = interactive_mode()
    else:
        # 有参数，运行主函数
        exit_code = asyncio.run(main())
    
    sys.exit(exit_code)