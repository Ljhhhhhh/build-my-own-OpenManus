#!/usr/bin/env python3
"""
配置驱动助手演示脚本
展示如何使用不同的配置文件创建专业化的AI助手
"""

import asyncio
import os
from config_driven_assistant import ConfigDrivenAssistant

async def demo_config_validation():
    """演示配置验证功能"""
    print("🔍 配置验证演示")
    print("=" * 50)
    
    # 测试配置文件列表
    config_files = [
        "assistant_config.toml",
        "python_assistant.toml", 
        "creative_assistant.toml",
        "business_assistant.toml"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                print(f"\n📁 加载配置: {config_file}")
                assistant = ConfigDrivenAssistant(config_file)
                info = assistant.get_info()
                
                print(f"   ✅ 助手名称: {info['name']}")
                print(f"   📝 描述: {info['description']}")
                print(f"   🤖 模型: {info['model']}")
                print(f"   🌡️  温度: {info['temperature']}")
                print(f"   📊 最大历史: {info['max_history']}")
                
            except Exception as e:
                print(f"   ❌ 配置加载失败: {e}")
        else:
            print(f"\n📁 配置文件不存在: {config_file}")

async def demo_pydantic_validation():
    """演示Pydantic数据验证"""
    print("\n\n🛡️ Pydantic数据验证演示")
    print("=" * 50)
    
    from config_driven_assistant import LLMConfig, AssistantConfig
    
    # 测试有效配置
    print("\n1️⃣ 测试有效配置")
    try:
        llm_config = LLMConfig(
            model=os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo"),
            temperature=0.7,
            max_tokens=1000
        )
        print(f"   ✅ LLM配置创建成功: {llm_config.model}")
    except Exception as e:
        print(f"   ❌ LLM配置创建失败: {e}")
    
    # 测试无效温度
    print("\n2️⃣ 测试无效温度参数")
    try:
        invalid_config = LLMConfig(
            model=os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo"),
            temperature=3.0,  # 超出范围
            max_tokens=1000
        )
        print(f"   ❌ 应该失败但成功了: {invalid_config.temperature}")
    except Exception as e:
        print(f"   ✅ 正确捕获验证错误: {e}")
    
    # 测试无效token数
    print("\n3️⃣ 测试无效token数")
    try:
        invalid_config = LLMConfig(
            model=os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo"),
            temperature=0.7,
            max_tokens=0  # 小于最小值
        )
        print(f"   ❌ 应该失败但成功了: {invalid_config.max_tokens}")
    except Exception as e:
        print(f"   ✅ 正确捕获验证错误: {e}")

async def demo_different_assistants():
    """演示不同类型的助手"""
    print("\n\n🎭 不同助手类型演示")
    print("=" * 50)
    
    # 测试问题
    test_questions = {
        "python_assistant.toml": "如何使用Python创建一个简单的Web API？",
        "creative_assistant.toml": "帮我写一个关于未来城市的短篇故事开头",
        "business_assistant.toml": "分析一下电商行业的发展趋势"
    }
    
    for config_file, question in test_questions.items():
        if os.path.exists(config_file):
            try:
                print(f"\n🤖 使用配置: {config_file}")
                assistant = ConfigDrivenAssistant(config_file)
                info = assistant.get_info()
                print(f"   助手: {info['name']}")
                print(f"   问题: {question}")
                
                # 检查是否有API密钥
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key and api_key != 'your_openai_api_key_here':
                    print("   正在生成回复...")
                    response = await assistant.process_message(question)
                    print(f"   回复: {response[:200]}...")
                else:
                    print("   💡 需要配置OPENAI_API_KEY进行实际测试")
                    
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")

async def demo_config_features():
    """演示配置功能特性"""
    print("\n\n⚙️ 配置功能特性演示")
    print("=" * 50)
    
    if os.path.exists("assistant_config.toml"):
        try:
            assistant = ConfigDrivenAssistant("assistant_config.toml")
            
            print("\n1️⃣ 助手信息")
            info = assistant.get_info()
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            print("\n2️⃣ 对话历史管理")
            print(f"   初始历史长度: {assistant.get_history_length()}")
            
            # 模拟添加消息
            assistant.conversation_history.append({"role": "user", "content": "测试消息1"})
            assistant.conversation_history.append({"role": "assistant", "content": "测试回复1"})
            print(f"   添加消息后: {assistant.get_history_length()}")
            
            # 清空历史
            assistant.clear_history()
            print(f"   清空后: {assistant.get_history_length()}")
            
            print("\n3️⃣ 配置重载")
            assistant.reload_config()
            
        except Exception as e:
            print(f"❌ 功能演示失败: {e}")

async def main():
    """主演示程序"""
    print("🚀 配置驱动助手 - 功能演示")
    print("基于项目1的基础，展示Pydantic和TOML配置的强大功能")
    print("=" * 70)
    
    # 运行各种演示
    await demo_config_validation()
    await demo_pydantic_validation()
    await demo_different_assistants()
    await demo_config_features()
    
    print("\n" + "=" * 70)
    print("✅ 所有演示完成！")
    print("\n💡 学习要点总结:")
    print("   • Pydantic提供强大的数据验证功能")
    print("   • TOML配置文件易于阅读和维护")
    print("   • 配置驱动开发提高了代码的灵活性")
    print("   • 不同配置可以创建专业化的助手")
    print("   • 类型安全和错误处理让程序更健壮")

if __name__ == "__main__":
    asyncio.run(main())