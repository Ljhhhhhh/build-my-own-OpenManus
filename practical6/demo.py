"""
项目6：多模态代理 - 演示程序

这个文件包含了多模态代理的各种使用示例和演示。

学习要点：
- 实际应用场景的演示
- 异步编程的实践
- 错误处理的最佳实践
- 用户体验的优化
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any

from agent import MultimodalAgent, MultimodalTaskType
from tools import ImageAnalysisType, BrowserActionType
from utils.config import get_config
from utils.logger import setup_logger


class MultimodalDemo:
    """多模态代理演示类"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger("demo", level=logging.INFO)
        self.agent = None
    
    async def initialize(self):
        """初始化代理"""
        self.logger.info("初始化多模态代理...")
        self.agent = MultimodalAgent(config=self.config)
        self.logger.info("代理初始化完成")
    
    async def demo_image_analysis(self):
        """演示图像分析功能"""
        print("\n" + "="*60)
        print("🖼️  演示1: 图像分析功能")
        print("="*60)
        
        # 创建示例图像路径（用户需要提供实际图像）
        sample_images = [
            "sample_image.jpg",
            "document.png",
            "screenshot.png"
        ]
        
        for image_path in sample_images:
            if Path(image_path).exists():
                print(f"\n📸 分析图像: {image_path}")
                
                try:
                    result = await self.agent.analyze_image(
                        image=image_path,
                        prompt="请详细分析这张图片的内容",
                        analysis_type=ImageAnalysisType.DETAILED
                    )
                    
                    self._print_demo_result("图像分析", result)
                    break
                    
                except Exception as e:
                    print(f"❌ 图像分析失败: {e}")
        else:
            print("ℹ️  未找到示例图像文件，跳过图像分析演示")
            print("   请将图像文件命名为 'sample_image.jpg' 并放在当前目录")
    
    async def demo_web_automation(self):
        """演示浏览器自动化功能"""
        print("\n" + "="*60)
        print("🌐 演示2: 浏览器自动化功能")
        print("="*60)
        
        try:
            # 演示网页导航和搜索
            print("\n🔍 演示：访问搜索引擎并搜索")
            
            result = await self.agent.automate_browser(
                task_description="访问百度首页，搜索'人工智能'，并获取搜索结果",
                url="https://www.baidu.com"
            )
            
            self._print_demo_result("浏览器自动化", result)
            
        except Exception as e:
            print(f"❌ 浏览器自动化失败: {e}")
            print("   请确保已安装Chrome浏览器和相关依赖")
    
    async def demo_multimodal_task(self):
        """演示多模态任务"""
        print("\n" + "="*60)
        print("🔄 演示3: 多模态任务（图像+网页）")
        print("="*60)
        
        # 检查是否有示例图像
        sample_image = "product_image.jpg"
        if Path(sample_image).exists():
            try:
                print(f"\n🛍️  演示：分析产品图像并搜索相关信息")
                
                result = await self.agent.visual_web_task(
                    image=sample_image,
                    task_description="分析这个产品的特征，然后在购物网站上搜索类似产品"
                )
                
                self._print_demo_result("多模态任务", result)
                
            except Exception as e:
                print(f"❌ 多模态任务失败: {e}")
        else:
            print("ℹ️  未找到产品图像文件，跳过多模态任务演示")
            print("   请将产品图像命名为 'product_image.jpg' 并放在当前目录")
    
    async def demo_text_processing(self):
        """演示文本处理功能"""
        print("\n" + "="*60)
        print("📝 演示4: 文本处理功能")
        print("="*60)
        
        try:
            # 演示复杂的文本分析任务
            text_query = """
            请帮我分析以下文本的情感倾向，并总结主要观点：
            "这款新产品的设计非常出色，用户界面直观易用。
            但是价格有点偏高，性价比一般。总体来说还是值得推荐的。"
            """
            
            print("\n📊 演示：文本情感分析和摘要")
            
            result = await self.agent.solve_multimodal(
                user_query=text_query,
                task_type=MultimodalTaskType.GENERAL
            )
            
            self._print_demo_result("文本处理", result)
            
        except Exception as e:
            print(f"❌ 文本处理失败: {e}")
    
    async def demo_calculation_task(self):
        """演示计算任务"""
        print("\n" + "="*60)
        print("🧮 演示5: 数学计算功能")
        print("="*60)
        
        try:
            # 演示复杂计算
            calc_query = """
            请帮我计算以下问题：
            一个圆的半径是5米，请计算它的面积和周长。
            然后告诉我如果半径增加20%，面积会增加多少？
            """
            
            print("\n📐 演示：几何计算")
            
            result = await self.agent.solve_multimodal(
                user_query=calc_query,
                task_type=MultimodalTaskType.GENERAL
            )
            
            self._print_demo_result("数学计算", result)
            
        except Exception as e:
            print(f"❌ 计算任务失败: {e}")
    
    def _print_demo_result(self, demo_name: str, result: Dict[str, Any]):
        """打印演示结果"""
        print(f"\n✅ {demo_name}完成!")
        print(f"⏱️  执行时间: {result['execution_stats']['total_time']:.2f}秒")
        print(f"🔄 推理步骤: {result['execution_stats']['total_steps']}")
        
        if 'multimodal_info' in result:
            multimodal_info = result['multimodal_info']
            tools_used = multimodal_info.get('tools_used', [])
            if tools_used:
                print(f"🛠️  使用工具: {', '.join(tools_used)}")
        
        print("\n📋 结果:")
        print("-" * 40)
        answer = result.get('answer', '未找到答案')
        # 限制输出长度以保持演示的可读性
        if len(answer) > 300:
            answer = answer[:300] + "..."
        print(answer)
    
    async def run_all_demos(self):
        """运行所有演示"""
        print("🚀 多模态代理功能演示")
        print("=" * 60)
        print("本演示将展示多模态代理的各种功能：")
        print("1. 图像分析")
        print("2. 浏览器自动化")
        print("3. 多模态任务")
        print("4. 文本处理")
        print("5. 数学计算")
        print("\n⚠️  注意：某些演示需要网络连接和相应的图像文件")
        
        input("\n按回车键开始演示...")
        
        try:
            await self.initialize()
            
            # 运行各个演示
            await self.demo_text_processing()
            await self.demo_calculation_task()
            await self.demo_image_analysis()
            await self.demo_web_automation()
            await self.demo_multimodal_task()
            
            print("\n" + "="*60)
            print("🎉 所有演示完成!")
            print("="*60)
            
        except Exception as e:
            print(f"❌ 演示过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    async def interactive_demo(self):
        """交互式演示"""
        print("🤖 多模态代理 - 交互式演示")
        print("=" * 60)
        print("可用命令：")
        print("1. image <图像路径> <描述> - 分析图像")
        print("2. web <任务描述> - 浏览器自动化")
        print("3. calc <数学问题> - 数学计算")
        print("4. text <文本任务> - 文本处理")
        print("5. help - 显示帮助")
        print("6. quit - 退出")
        print("=" * 60)
        
        try:
            await self.initialize()
            
            while True:
                try:
                    command = input("\n💬 请输入命令: ").strip()
                    
                    if not command:
                        continue
                    
                    if command.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if command.lower() == 'help':
                        self._show_help()
                        continue
                    
                    await self._process_interactive_command(command)
                    
                except KeyboardInterrupt:
                    print("\n⏹️  操作中断")
                    continue
                except Exception as e:
                    print(f"❌ 命令执行失败: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
        
        print("\n👋 演示结束，感谢使用!")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 命令帮助:")
        print("-" * 40)
        print("image <路径> <描述>  - 分析指定图像")
        print("  示例: image photo.jpg 请描述这张图片")
        print()
        print("web <任务>          - 执行网页自动化任务")
        print("  示例: web 访问百度搜索人工智能")
        print()
        print("calc <问题>         - 解决数学计算问题")
        print("  示例: calc 计算圆周率乘以5的平方")
        print()
        print("text <任务>         - 处理文本相关任务")
        print("  示例: text 分析这段话的情感倾向")
    
    async def _process_interactive_command(self, command: str):
        """处理交互式命令"""
        parts = command.split(' ', 2)
        cmd_type = parts[0].lower()
        
        if cmd_type == 'image' and len(parts) >= 3:
            image_path = parts[1]
            description = parts[2]
            
            if not Path(image_path).exists():
                print(f"❌ 图像文件不存在: {image_path}")
                return
            
            print(f"🖼️  分析图像: {image_path}")
            result = await self.agent.analyze_image(
                image=image_path,
                prompt=description
            )
            self._print_demo_result("图像分析", result)
        
        elif cmd_type == 'web' and len(parts) >= 2:
            task = ' '.join(parts[1:])
            print(f"🌐 执行网页任务: {task}")
            result = await self.agent.automate_browser(task)
            self._print_demo_result("浏览器自动化", result)
        
        elif cmd_type in ['calc', 'calculate'] and len(parts) >= 2:
            problem = ' '.join(parts[1:])
            print(f"🧮 计算问题: {problem}")
            result = await self.agent.solve_multimodal(
                user_query=problem,
                task_type=MultimodalTaskType.GENERAL
            )
            self._print_demo_result("数学计算", result)
        
        elif cmd_type == 'text' and len(parts) >= 2:
            task = ' '.join(parts[1:])
            print(f"📝 文本任务: {task}")
            result = await self.agent.solve_multimodal(
                user_query=task,
                task_type=MultimodalTaskType.GENERAL
            )
            self._print_demo_result("文本处理", result)
        
        else:
            print("❌ 无效命令，输入 'help' 查看帮助")


async def main():
    """主函数"""
    import sys
    
    demo = MultimodalDemo()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        await demo.interactive_demo()
    else:
        await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())