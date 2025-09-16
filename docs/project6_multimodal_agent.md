## 阶段四：高级功能集成

### 项目6: 多模态代理

#### 项目目标
- 集成图像处理和浏览器自动化功能
- 实现多模态输入处理（文本+图像）
- 构建能够理解和操作网页的智能代理

#### 核心代码实现

**1. 多模态工具基类**

```python
# src/tools/multimodal_base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import base64
import io

class MultimodalTool(ABC):
    """多模态工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, 
                     text_input: Optional[str] = None,
                     image_input: Optional[Union[str, Image.Image]] = None,
                     **kwargs) -> Dict[str, Any]:
        """执行多模态工具"""
        pass
    
    def encode_image(self, image: Union[str, Image.Image]) -> str:
        """将图像编码为base64字符串"""
        if isinstance(image, str):
            # 如果是文件路径
            with open(image, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        elif isinstance(image, Image.Image):
            # 如果是PIL图像对象
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            raise ValueError("不支持的图像格式")
    
    def decode_image(self, base64_string: str) -> Image.Image:
        """将base64字符串解码为PIL图像"""
        image_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(image_data))
```

**2. 图像分析工具**

```python
# src/tools/image_analyzer.py
import openai
from typing import Dict, Any, Optional, Union
from PIL import Image
from .multimodal_base import MultimodalTool

class ImageAnalyzer(MultimodalTool):
    """图像分析工具"""
    
    def __init__(self, api_key: str):
        super().__init__(
            name="image_analyzer",
            description="分析图像内容，提取文字、识别对象、描述场景"
        )
        self.client = openai.OpenAI(api_key=api_key)
    
    async def execute(self, 
                     text_input: Optional[str] = None,
                     image_input: Optional[Union[str, Image.Image]] = None,
                     analysis_type: str = "describe",
                     **kwargs) -> Dict[str, Any]:
        """执行图像分析"""
        if not image_input:
            return {"error": "需要提供图像输入"}
        
        try:
            # 编码图像
            base64_image = self.encode_image(image_input)
            
            # 构建提示词
            if analysis_type == "describe":
                prompt = text_input or "请详细描述这张图片的内容"
            elif analysis_type == "ocr":
                prompt = "请提取图片中的所有文字内容"
            elif analysis_type == "objects":
                prompt = "请识别图片中的所有对象和物品"
            else:
                prompt = text_input or "请分析这张图片"
            
            # 调用GPT-4V
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": result,
                "prompt_used": prompt
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

**3. 浏览器自动化工具**

```python
# src/tools/browser_automation.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import io
from typing import Dict, Any, Optional, List
from .multimodal_base import MultimodalTool

class BrowserTool(MultimodalTool):
    """浏览器自动化工具"""
    
    def __init__(self, headless: bool = False):
        super().__init__(
            name="browser_tool",
            description="自动化浏览器操作：导航、点击、输入、截图等"
        )
        self.headless = headless
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """设置浏览器驱动"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    async def execute(self, 
                     text_input: Optional[str] = None,
                     image_input: Optional[Image.Image] = None,
                     action: str = "navigate",
                     **kwargs) -> Dict[str, Any]:
        """执行浏览器操作"""
        try:
            if action == "navigate":
                return await self._navigate(kwargs.get('url', text_input))
            elif action == "click":
                return await self._click(kwargs.get('selector', text_input))
            elif action == "input":
                return await self._input(
                    kwargs.get('selector'), 
                    kwargs.get('text', text_input)
                )
            elif action == "screenshot":
                return await self._screenshot()
            elif action == "get_text":
                return await self._get_text(kwargs.get('selector', text_input))
            elif action == "scroll":
                return await self._scroll(kwargs.get('direction', 'down'))
            else:
                return {"error": f"不支持的操作: {action}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _navigate(self, url: str) -> Dict[str, Any]:
        """导航到指定URL"""
        self.driver.get(url)
        time.sleep(2)  # 等待页面加载
        return {
            "success": True,
            "action": "navigate",
            "url": url,
            "title": self.driver.title
        }
    
    async def _click(self, selector: str) -> Dict[str, Any]:
        """点击元素"""
        element = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()
        return {
            "success": True,
            "action": "click",
            "selector": selector
        }
    
    async def _input(self, selector: str, text: str) -> Dict[str, Any]:
        """输入文本"""
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.clear()
        element.send_keys(text)
        return {
            "success": True,
            "action": "input",
            "selector": selector,
            "text": text
        }
    
    async def _screenshot(self) -> Dict[str, Any]:
        """截取屏幕截图"""
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        base64_image = self.encode_image(image)
        
        return {
            "success": True,
            "action": "screenshot",
            "image": base64_image,
            "size": image.size
        }
    
    async def _get_text(self, selector: str) -> Dict[str, Any]:
        """获取元素文本"""
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        text = element.text
        return {
            "success": True,
            "action": "get_text",
            "selector": selector,
            "text": text
        }
    
    async def _scroll(self, direction: str) -> Dict[str, Any]:
        """滚动页面"""
        if direction == "down":
            self.driver.execute_script("window.scrollBy(0, 500);")
        elif direction == "up":
            self.driver.execute_script("window.scrollBy(0, -500);")
        elif direction == "top":
            self.driver.execute_script("window.scrollTo(0, 0);")
        elif direction == "bottom":
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        return {
            "success": True,
            "action": "scroll",
            "direction": direction
        }
    
    def close(self):
         """关闭浏览器"""
         if self.driver:
             self.driver.quit()
 ```

**4. 多模态代理主类**

```python
# src/agents/multimodal_agent.py
import asyncio
from typing import Dict, Any, List, Optional, Union
from PIL import Image
from ..tools.image_analyzer import ImageAnalyzer
from ..tools.browser_automation import BrowserTool
from ..agents.react_agent import ReActAgent

class MultimodalAgent(ReActAgent):
    """多模态智能代理"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 初始化多模态工具
        self.image_analyzer = ImageAnalyzer(config['openai_api_key'])
        self.browser_tool = BrowserTool(headless=config.get('headless', False))
        
        # 注册工具
        self.tools.update({
            'analyze_image': self.image_analyzer,
            'browser_action': self.browser_tool
        })
    
    async def process_multimodal_input(self, 
                                     text: Optional[str] = None,
                                     image: Optional[Union[str, Image.Image]] = None,
                                     task_type: str = "general") -> Dict[str, Any]:
        """处理多模态输入"""
        context = {
            "text_input": text,
            "has_image": image is not None,
            "task_type": task_type
        }
        
        # 如果有图像输入，先分析图像
        if image:
            image_analysis = await self.image_analyzer.execute(
                text_input="请详细分析这张图片，包括内容、文字、对象等",
                image_input=image
            )
            context["image_analysis"] = image_analysis
        
        # 构建任务描述
        if task_type == "web_automation":
            task_description = self._build_web_task(text, context)
        elif task_type == "image_analysis":
            task_description = self._build_image_task(text, context)
        else:
            task_description = text or "请处理提供的多模态输入"
        
        # 执行ReAct循环
        return await self.solve(task_description, context=context)
    
    def _build_web_task(self, text: str, context: Dict) -> str:
        """构建网页自动化任务描述"""
        base_task = text or "执行网页操作"
        
        if context.get("has_image"):
            return f"""{base_task}
            
可用信息：
- 图像分析结果：{context.get('image_analysis', {}).get('result', '无')}
- 可用操作：导航、点击、输入、截图、获取文本、滚动

请根据图像内容和用户需求，制定并执行网页操作计划。"""
        else:
            return f"{base_task}\n\n请使用浏览器工具完成网页操作任务。"
    
    def _build_image_task(self, text: str, context: Dict) -> str:
        """构建图像分析任务描述"""
        base_task = text or "分析图像内容"
        
        if context.get("image_analysis"):
            analysis = context["image_analysis"].get('result', '')
            return f"""{base_task}
            
图像分析结果：
{analysis}

请基于以上分析结果，回答用户的问题或完成指定任务。"""
        else:
            return base_task
    
    async def web_screenshot_and_analyze(self, url: str, 
                                       analysis_prompt: str = None) -> Dict[str, Any]:
        """访问网页并分析截图"""
        try:
            # 导航到网页
            nav_result = await self.browser_tool.execute(
                action="navigate", url=url
            )
            
            if not nav_result.get("success"):
                return {"error": f"无法访问网页: {nav_result.get('error')}"}
            
            # 截图
            screenshot_result = await self.browser_tool.execute(
                action="screenshot"
            )
            
            if not screenshot_result.get("success"):
                return {"error": f"截图失败: {screenshot_result.get('error')}"}
            
            # 分析截图
            image_base64 = screenshot_result["image"]
            image = self.image_analyzer.decode_image(image_base64)
            
            analysis_result = await self.image_analyzer.execute(
                text_input=analysis_prompt or "请分析这个网页的内容和布局",
                image_input=image
            )
            
            return {
                "success": True,
                "url": url,
                "page_title": nav_result.get("title"),
                "screenshot": image_base64,
                "analysis": analysis_result
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'browser_tool'):
            self.browser_tool.close()

# 使用示例
async def main():
    config = {
        'openai_api_key': 'your-api-key',
        'model': 'gpt-4',
        'headless': False
    }
    
    agent = MultimodalAgent(config)
    
    try:
        # 示例1：分析图像
        print("=== 图像分析示例 ===")
        result1 = await agent.process_multimodal_input(
            text="这张图片中有什么内容？请详细描述",
            image="path/to/your/image.jpg",
            task_type="image_analysis"
        )
        print(f"结果: {result1}")
        
        # 示例2：网页截图分析
        print("\n=== 网页分析示例 ===")
        result2 = await agent.web_screenshot_and_analyze(
            url="https://www.example.com",
            analysis_prompt="请分析这个网页的主要功能和内容结构"
        )
        print(f"结果: {result2}")
        
        # 示例3：基于图像的网页操作
        print("\n=== 多模态网页操作示例 ===")
        result3 = await agent.process_multimodal_input(
            text="请根据这张截图，帮我点击登录按钮",
            image="path/to/screenshot.png",
            task_type="web_automation"
        )
        print(f"结果: {result3}")
        
    finally:
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 学习要点

1. **多模态处理**：同时处理文本和图像输入
2. **工具集成**：将不同类型的工具整合到统一接口
3. **上下文管理**：在多模态环境中维护任务上下文
4. **资源管理**：正确管理浏览器等外部资源