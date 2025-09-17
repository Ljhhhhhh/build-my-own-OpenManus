# learning_examples.py
"""
Python AI开发学习示例
专为前端开发者设计，对比JavaScript概念
"""

import asyncio
from typing import List, Dict, Optional, Union
import json

# ============================================================================
# 1. 类型注解示例 (Type Hints) - 类似TypeScript
# ============================================================================

def greet_user(name: str, age: int) -> str:
    """
    类型注解示例 - 类似TypeScript的类型声明
    
    JavaScript/TypeScript 对比:
    function greetUser(name: string, age: number): string {
        return `Hello ${name}, you are ${age} years old`;
    }
    """
    return f"Hello {name}, you are {age} years old"

# 复杂类型注解
UserData = Dict[str, Union[str, int]]  # 类似 type UserData = {[key: string]: string | number}

def process_users(users: List[UserData]) -> Optional[str]:
    """
    处理用户数据 - 展示复杂类型注解
    
    TypeScript 对比:
    type UserData = {[key: string]: string | number};
    function processUsers(users: UserData[]): string | null
    """
    if not users:
        return None
    
    return f"Processed {len(users)} users"

# ============================================================================
# 2. 异步编程示例 (async/await) - 类似JavaScript Promise
# ============================================================================

async def fetch_data(url: str) -> Dict:
    """
    模拟异步数据获取 - 类似JavaScript的fetch
    
    JavaScript 对比:
    async function fetchData(url) {
        const response = await fetch(url);
        return await response.json();
    }
    """
    # 模拟网络延迟
    await asyncio.sleep(1)
    
    # 模拟返回数据
    return {
        "url": url,
        "data": "Some fetched data",
        "status": "success"
    }

async def fetch_multiple_data(urls: List[str]) -> List[Dict]:
    """
    并发获取多个数据 - 类似JavaScript的Promise.all
    
    JavaScript 对比:
    async function fetchMultipleData(urls) {
        const promises = urls.map(url => fetchData(url));
        return await Promise.all(promises);
    }
    """
    # 创建多个异步任务
    tasks = [fetch_data(url) for url in urls]
    
    # 等待所有任务完成 - 类似Promise.all
    results = await asyncio.gather(*tasks)
    
    return results

# ============================================================================
# 3. 错误处理示例 - 类似JavaScript的try/catch
# ============================================================================

async def safe_api_call(endpoint: str) -> Dict:
    """
    安全的API调用 - 展示错误处理
    
    JavaScript 对比:
    async function safeApiCall(endpoint) {
        try {
            const result = await fetchData(endpoint);
            return { success: true, data: result };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    """
    try:
        result = await fetch_data(endpoint)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# 4. 类定义示例 - 类似JavaScript Class
# ============================================================================

class DataManager:
    """
    数据管理器类 - 展示Python类的使用
    
    JavaScript 对比:
    class DataManager {
        constructor() {
            this.cache = new Map();
        }
        
        async getData(key) {
            // ... 实现
        }
    }
    """
    
    def __init__(self):
        """构造函数 - 类似JavaScript的constructor"""
        self.cache: Dict[str, any] = {}
        self.request_count: int = 0
    
    async def get_data(self, key: str) -> Optional[Dict]:
        """异步获取数据 - 带缓存功能"""
        # 检查缓存
        if key in self.cache:
            print(f"📦 从缓存获取数据: {key}")
            return self.cache[key]
        
        # 获取新数据
        print(f"🌐 从网络获取数据: {key}")
        data = await fetch_data(f"https://api.example.com/{key}")
        
        # 存入缓存
        self.cache[key] = data
        self.request_count += 1
        
        return data
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "cached_items": len(self.cache),
            "total_requests": self.request_count
        }

# ============================================================================
# 5. 实际使用示例
# ============================================================================

async def main_example():
    """主示例函数 - 展示所有概念的综合使用"""
    
    print("🚀 Python AI开发学习示例")
    print("=" * 50)
    
    # 1. 基本类型注解使用
    print("\n1️⃣ 类型注解示例:")
    message = greet_user("张三", 25)
    print(f"   {message}")
    
    # 2. 异步编程示例
    print("\n2️⃣ 异步编程示例:")
    print("   开始异步获取数据...")
    
    # 单个异步调用
    result = await fetch_data("https://api.example.com/user/1")
    print(f"   单个请求结果: {result}")
    
    # 并发异步调用
    urls = [
        "https://api.example.com/user/1",
        "https://api.example.com/user/2", 
        "https://api.example.com/user/3"
    ]
    
    results = await fetch_multiple_data(urls)
    print(f"   并发请求结果: 获取了 {len(results)} 个结果")
    
    # 3. 错误处理示例
    print("\n3️⃣ 错误处理示例:")
    safe_result = await safe_api_call("https://api.example.com/data")
    print(f"   安全调用结果: {safe_result}")
    
    # 4. 类使用示例
    print("\n4️⃣ 类使用示例:")
    manager = DataManager()
    
    # 第一次获取 - 从网络
    data1 = await manager.get_data("user_profile")
    
    # 第二次获取 - 从缓存
    data2 = await manager.get_data("user_profile")
    
    stats = manager.get_stats()
    print(f"   统计信息: {stats}")
    
    print("\n✅ 所有示例执行完成！")

# ============================================================================
# 6. 对比总结
# ============================================================================

def print_comparison():
    """打印Python与JavaScript的对比总结"""
    
    comparison = """
    
🔄 Python vs JavaScript 对比总结:

┌─────────────────┬─────────────────────┬─────────────────────┐
│     概念        │      JavaScript     │       Python        │
├─────────────────┼─────────────────────┼─────────────────────┤
│   类型注解      │  TypeScript types   │   Type Hints        │
│   异步编程      │  async/await        │   async/await       │
│   错误处理      │  try/catch          │   try/except        │
│   类定义        │  class              │   class             │
│   构造函数      │  constructor()      │   __init__()        │
│   字符串模板    │  `Hello ${name}`    │   f"Hello {name}"   │
│   数组/列表     │  Array              │   List              │
│   对象/字典     │  Object             │   Dict              │
│   空值          │  null/undefined     │   None              │
│   布尔值        │  true/false         │   True/False        │
└─────────────────┴─────────────────────┴─────────────────────┘

💡 学习建议:
1. Python的异步编程与JavaScript非常相似
2. 类型注解让代码更安全，类似TypeScript
3. 错误处理模式基本一致
4. Python更注重代码可读性和简洁性
    """
    
    print(comparison)

if __name__ == "__main__":
    # 打印对比总结
    print_comparison()
    
    # 运行示例
    print("\n🎯 运行实际示例:")
    asyncio.run(main_example())