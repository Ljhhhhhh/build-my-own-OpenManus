"""
命令行界面模块

提供聊天机器人的命令行交互界面。
"""

import asyncio
import sys
from typing import Optional
from colorama import Fore, Style, init

from chatbot import SimpleChatBot
from logger import logger
from exceptions import ChatBotError, ValidationError, APIError

# 初始化 colorama
init(autoreset=True)


class ChatBotCLI:
    """聊天机器人命令行界面"""
    
    def __init__(self):
        self.bot: Optional[SimpleChatBot] = None
        self.running = False
    
    def print_welcome(self) -> None:
        """打印欢迎信息"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🤖 简单聊天机器人 v1.0.0")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}欢迎使用！输入消息开始对话。")
        print(f"{Fore.YELLOW}可用命令:")
        print(f"{Fore.YELLOW}  /help    - 显示帮助信息")
        print(f"{Fore.YELLOW}  /clear   - 清空对话历史")
        print(f"{Fore.YELLOW}  /status  - 显示状态信息")
        print(f"{Fore.YELLOW}  /system  - 设置系统消息")
        print(f"{Fore.YELLOW}  /stream  - 切换流式输出模式")
        print(f"{Fore.YELLOW}  /quit    - 退出程序")
        print(f"{Fore.CYAN}{'='*60}")
        print()
    
    def print_help(self) -> None:
        """打印帮助信息"""
        print(f"{Fore.CYAN}📖 帮助信息:")
        print(f"{Fore.WHITE}  直接输入消息与机器人对话")
        print(f"{Fore.WHITE}  使用 '/' 开头的命令执行特殊操作")
        print()
        print(f"{Fore.YELLOW}命令列表:")
        print(f"{Fore.WHITE}  /help    - 显示此帮助信息")
        print(f"{Fore.WHITE}  /clear   - 清空对话历史记录")
        print(f"{Fore.WHITE}  /status  - 显示机器人状态和配置")
        print(f"{Fore.WHITE}  /system  - 设置系统消息（角色设定）")
        print(f"{Fore.WHITE}  /stream  - 切换流式输出模式")
        print(f"{Fore.WHITE}  /quit    - 退出聊天程序")
        print()
    
    def print_status(self) -> None:
        """打印状态信息"""
        if not self.bot:
            print(f"{Fore.RED}❌ 机器人未初始化")
            return
        
        summary = self.bot.get_conversation_summary()
        print(f"{Fore.CYAN}📊 机器人状态:")
        print(f"{Fore.WHITE}  模型: {summary['model']}")
        print(f"{Fore.WHITE}  最大令牌数: {summary['max_tokens']}")
        print(f"{Fore.WHITE}  温度: {summary['temperature']}")
        print(f"{Fore.WHITE}  对话消息数: {summary['message_count']}")
        
        if summary['last_messages']:
            print(f"{Fore.WHITE}  最近消息:")
            for msg in summary['last_messages']:
                print(f"{Fore.LIGHTBLACK_EX}    {msg}")
        print()
    
    async def handle_system_command(self) -> None:
        """处理系统消息设置命令"""
        print(f"{Fore.CYAN}🔧 设置系统消息（角色设定）:")
        print(f"{Fore.YELLOW}请输入系统消息，用于设定机器人的角色和行为:")
        print(f"{Fore.LIGHTBLACK_EX}（例如：你是一个友善的助手，总是用简洁明了的方式回答问题）")
        
        try:
            system_message = input(f"{Fore.WHITE}系统消息: ").strip()
            if system_message:
                self.bot.set_system_message(system_message)
                print(f"{Fore.GREEN}✅ 系统消息已设置，对话历史已清空")
            else:
                print(f"{Fore.YELLOW}⚠️  系统消息为空，未进行设置")
        except ValidationError as e:
            print(f"{Fore.RED}❌ {e}")
        print()
    
    async def handle_user_input(self, user_input: str, stream_mode: bool = False) -> bool:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            stream_mode: 是否使用流式模式
            
        Returns:
            是否继续运行
        """
        user_input = user_input.strip()
        
        # 处理命令
        if user_input.startswith('/'):
            command = user_input[1:].lower()
            
            if command == 'quit' or command == 'q':
                return False
            elif command == 'help' or command == 'h':
                self.print_help()
            elif command == 'clear' or command == 'c':
                self.bot.clear_history()
                print(f"{Fore.GREEN}✅ 对话历史已清空")
                print()
            elif command == 'status' or command == 's':
                self.print_status()
            elif command == 'system':
                await self.handle_system_command()
            elif command == 'stream':
                return 'toggle_stream'  # 特殊返回值，用于切换流式模式
            else:
                print(f"{Fore.RED}❌ 未知命令: {command}")
                print(f"{Fore.YELLOW}输入 /help 查看可用命令")
                print()
            
            return True
        
        # 处理普通消息
        if not user_input:
            return True
        
        try:
            print(f"{Fore.BLUE}🤖 机器人: ", end="")
            
            if stream_mode:
                # 流式输出
                async for chunk in self.bot.chat_stream(user_input):
                    print(chunk, end="", flush=True)
                print()  # 换行
            else:
                # 普通输出
                response = await self.bot.chat(user_input)
                print(f"{Fore.WHITE}{response}")
            
            print()  # 额外换行
            
        except ValidationError as e:
            print(f"{Fore.RED}❌ 输入验证错误: {e}")
            print()
        except APIError as e:
            print(f"{Fore.RED}❌ API 错误: {e}")
            print(f"{Fore.YELLOW}💡 请检查网络连接和 API 密钥配置")
            print()
        except ChatBotError as e:
            print(f"{Fore.RED}❌ 聊天机器人错误: {e}")
            print()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  操作被用户中断")
            return True
        except Exception as e:
            logger.error(f"未预期的错误: {e}")
            print(f"{Fore.RED}❌ 发生未预期的错误: {e}")
            print()
        
        return True
    
    async def run(self) -> None:
        """运行聊天机器人CLI"""
        try:
            # 初始化机器人
            self.bot = SimpleChatBot()
            self.running = True
            stream_mode = False
            
            # 显示欢迎信息
            self.print_welcome()
            
            while self.running:
                try:
                    # 显示提示符
                    mode_indicator = "📡" if stream_mode else "💬"
                    user_input = input(f"{Fore.GREEN}{mode_indicator} 你: ")
                    
                    # 处理输入
                    result = await self.handle_user_input(user_input, stream_mode)
                    
                    if result == 'toggle_stream':
                        stream_mode = not stream_mode
                        mode_text = "流式" if stream_mode else "普通"
                        print(f"{Fore.CYAN}🔄 已切换到{mode_text}输出模式")
                        print()
                    elif not result:
                        break
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}👋 再见！")
                    break
                except EOFError:
                    print(f"\n{Fore.YELLOW}👋 再见！")
                    break
        
        except Exception as e:
            logger.error(f"CLI 运行时发生错误: {e}")
            print(f"{Fore.RED}❌ 程序运行时发生错误: {e}")
            sys.exit(1)
        
        finally:
            if self.bot:
                # 关闭机器人客户端
                try:
                    await self.bot.client.close()
                except:
                    pass
            
            print(f"{Fore.CYAN}👋 感谢使用简单聊天机器人！")


async def main():
    """主函数"""
    cli = ChatBotCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        sys.exit(1)