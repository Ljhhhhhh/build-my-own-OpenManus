"""
浏览器自动化工具

基于Selenium WebDriver的浏览器自动化工具，支持网页导航、元素操作、截图等功能。

学习要点：
- Selenium WebDriver的使用
- 浏览器自动化的最佳实践
- 元素定位策略
- 异常处理和重试机制
- 资源管理和清理
"""

import asyncio
import logging
import time
import base64
from typing import Optional, Dict, Any, List, Union, Tuple
from pathlib import Path
from contextlib import asynccontextmanager
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementNotInteractableException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

from .multimodal_base import MultimodalTool, MultimodalInput, ToolResult, ToolResultStatus
from ..utils.config import Config

logger = logging.getLogger(__name__)


class BrowserActionType:
    """浏览器操作类型常量"""
    NAVIGATE = "navigate"           # 导航到URL
    CLICK = "click"                # 点击元素
    INPUT = "input"                # 输入文本
    SCROLL = "scroll"              # 滚动页面
    SCREENSHOT = "screenshot"       # 截图
    GET_TEXT = "get_text"          # 获取文本
    GET_ATTRIBUTE = "get_attribute" # 获取属性
    WAIT = "wait"                  # 等待
    EXECUTE_SCRIPT = "execute_script" # 执行JavaScript
    BACK = "back"                  # 后退
    FORWARD = "forward"            # 前进
    REFRESH = "refresh"            # 刷新


class ElementLocator:
    """元素定位器"""
    
    @staticmethod
    def parse_selector(selector: str) -> Tuple[By, str]:
        """
        解析选择器字符串
        
        支持的格式：
        - id:element_id
        - class:class_name
        - tag:tag_name
        - css:css_selector
        - xpath:xpath_expression
        - name:name_attribute
        - text:link_text
        
        Args:
            selector: 选择器字符串
            
        Returns:
            (By类型, 选择器值)
        """
        if ':' not in selector:
            # 默认使用CSS选择器
            return By.CSS_SELECTOR, selector
        
        selector_type, selector_value = selector.split(':', 1)
        
        selector_map = {
            'id': By.ID,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'name': By.NAME,
            'text': By.LINK_TEXT,
            'partial_text': By.PARTIAL_LINK_TEXT
        }
        
        by_type = selector_map.get(selector_type.lower(), By.CSS_SELECTOR)
        return by_type, selector_value


class BrowserTool(MultimodalTool):
    """
    浏览器自动化工具
    
    使用Selenium WebDriver进行浏览器自动化操作。
    
    学习要点：
    - WebDriver的生命周期管理
    - 异步上下文管理器的使用
    - 元素等待策略
    - 错误处理和重试机制
    - 资源清理的重要性
    """
    
    name = "browser_tool"
    description = "浏览器自动化工具，支持网页导航、元素操作、截图等功能"
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._driver_lock = asyncio.Lock()
    
    async def execute_multimodal(
        self,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> ToolResult:
        """
        执行浏览器自动化操作
        
        Args:
            multimodal_input: 多模态输入数据
            **kwargs: 额外参数，包括：
                - action: 操作类型
                - url: 目标URL
                - selector: 元素选择器
                - text: 输入文本
                - timeout: 超时时间
                - screenshot_path: 截图保存路径
                
        Returns:
            操作结果
        """
        try:
            # 验证输入
            self._validate_multimodal_input(multimodal_input)
            
            # 解析操作参数
            action = kwargs.get("action", BrowserActionType.NAVIGATE)
            
            # 确保浏览器已启动
            async with self._get_driver() as driver:
                # 执行具体操作
                result = await self._execute_browser_action(
                    driver,
                    action,
                    multimodal_input,
                    **kwargs
                )
                
                return ToolResult(
                    status=ToolResultStatus.SUCCESS,
                    data=result,
                    message=f"浏览器操作完成: {action}"
                )
                
        except Exception as e:
            logger.error(f"浏览器操作失败: {e}")
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data={"error": str(e)},
                message=f"浏览器操作失败: {e}"
            )
    
    @asynccontextmanager
    async def _get_driver(self):
        """
        获取WebDriver实例的异步上下文管理器
        
        确保WebDriver的正确初始化和清理。
        """
        async with self._driver_lock:
            if self.driver is None:
                await self._initialize_driver()
            
            try:
                yield self.driver
            except Exception as e:
                logger.error(f"WebDriver操作异常: {e}")
                # 如果出现严重错误，重新初始化driver
                if isinstance(e, WebDriverException):
                    await self._cleanup_driver()
                    await self._initialize_driver()
                raise
    
    async def _initialize_driver(self) -> None:
        """初始化WebDriver"""
        try:
            logger.info("初始化WebDriver...")
            
            # 配置Chrome选项
            options = ChromeOptions()
            
            if self.config.browser_headless:
                options.add_argument("--headless")
            
            # 基本配置
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # 禁用图片加载以提高速度
            
            # 窗口大小
            options.add_argument(f"--window-size={self.config.browser_window_width},{self.config.browser_window_height}")
            
            # 用户代理
            if self.config.browser_user_agent:
                options.add_argument(f"--user-agent={self.config.browser_user_agent}")
            
            # 下载目录
            if self.config.browser_download_dir:
                prefs = {
                    "download.default_directory": str(Path(self.config.browser_download_dir).absolute())
                }
                options.add_experimental_option("prefs", prefs)
            
            # 日志级别
            options.add_argument(f"--log-level={self.config.webdriver_log_level}")
            
            # 初始化Service
            if self.config.webdriver_auto_install:
                service = ChromeService(ChromeDriverManager().install())
            else:
                service = ChromeService(self.config.webdriver_path) if self.config.webdriver_path else None
            
            # 创建WebDriver实例
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 设置超时
            self.driver.implicitly_wait(self.config.browser_timeout)
            self.driver.set_page_load_timeout(self.config.browser_timeout)
            
            # 创建WebDriverWait实例
            self.wait = WebDriverWait(self.driver, self.config.browser_timeout)
            
            logger.info("WebDriver初始化成功")
            
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {e}")
            await self._cleanup_driver()
            raise
    
    async def _cleanup_driver(self) -> None:
        """清理WebDriver资源"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver已清理")
            except Exception as e:
                logger.warning(f"WebDriver清理时出现异常: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    async def _execute_browser_action(
        self,
        driver: webdriver.Chrome,
        action: str,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行具体的浏览器操作
        
        Args:
            driver: WebDriver实例
            action: 操作类型
            multimodal_input: 多模态输入
            **kwargs: 操作参数
            
        Returns:
            操作结果
        """
        action_map = {
            BrowserActionType.NAVIGATE: self._navigate,
            BrowserActionType.CLICK: self._click_element,
            BrowserActionType.INPUT: self._input_text,
            BrowserActionType.SCROLL: self._scroll_page,
            BrowserActionType.SCREENSHOT: self._take_screenshot,
            BrowserActionType.GET_TEXT: self._get_text,
            BrowserActionType.GET_ATTRIBUTE: self._get_attribute,
            BrowserActionType.WAIT: self._wait_for_element,
            BrowserActionType.EXECUTE_SCRIPT: self._execute_script,
            BrowserActionType.BACK: self._go_back,
            BrowserActionType.FORWARD: self._go_forward,
            BrowserActionType.REFRESH: self._refresh_page,
        }
        
        action_func = action_map.get(action)
        if not action_func:
            raise ValueError(f"不支持的操作类型: {action}")
        
        return await action_func(driver, multimodal_input, **kwargs)
    
    async def _navigate(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """导航到指定URL"""
        url = kwargs.get("url") or multimodal_input.text
        
        if not url:
            raise ValueError("导航操作需要提供URL")
        
        # 确保URL格式正确
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        logger.info(f"导航到: {url}")
        driver.get(url)
        
        # 等待页面加载完成
        await asyncio.sleep(1)
        
        return {
            "action": "navigate",
            "url": url,
            "current_url": driver.current_url,
            "title": driver.title
        }
    
    async def _click_element(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """点击元素"""
        selector = kwargs.get("selector")
        if not selector:
            raise ValueError("点击操作需要提供元素选择器")
        
        by, value = ElementLocator.parse_selector(selector)
        
        # 等待元素可点击
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        
        # 滚动到元素位置
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        await asyncio.sleep(0.5)
        
        # 点击元素
        element.click()
        
        logger.info(f"点击元素: {selector}")
        
        return {
            "action": "click",
            "selector": selector,
            "element_text": element.text,
            "element_tag": element.tag_name
        }
    
    async def _input_text(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """输入文本"""
        selector = kwargs.get("selector")
        text = kwargs.get("text") or multimodal_input.text
        clear_first = kwargs.get("clear_first", True)
        
        if not selector:
            raise ValueError("输入操作需要提供元素选择器")
        
        if not text:
            raise ValueError("输入操作需要提供文本内容")
        
        by, value = ElementLocator.parse_selector(selector)
        
        # 等待元素可输入
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        
        # 滚动到元素位置
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        await asyncio.sleep(0.5)
        
        # 清空现有内容
        if clear_first:
            element.clear()
        
        # 输入文本
        element.send_keys(text)
        
        logger.info(f"输入文本到 {selector}: {text}")
        
        return {
            "action": "input",
            "selector": selector,
            "text": text,
            "element_value": element.get_attribute("value")
        }
    
    async def _scroll_page(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """滚动页面"""
        direction = kwargs.get("direction", "down")  # up, down, top, bottom
        pixels = kwargs.get("pixels", 500)
        
        if direction == "down":
            driver.execute_script(f"window.scrollBy(0, {pixels});")
        elif direction == "up":
            driver.execute_script(f"window.scrollBy(0, -{pixels});")
        elif direction == "top":
            driver.execute_script("window.scrollTo(0, 0);")
        elif direction == "bottom":
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        await asyncio.sleep(1)  # 等待滚动完成
        
        logger.info(f"页面滚动: {direction}")
        
        return {
            "action": "scroll",
            "direction": direction,
            "pixels": pixels if direction in ["up", "down"] else None
        }
    
    async def _take_screenshot(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """截图"""
        screenshot_path = kwargs.get("screenshot_path")
        return_base64 = kwargs.get("return_base64", True)
        
        # 获取截图
        screenshot_data = driver.get_screenshot_as_png()
        
        result = {
            "action": "screenshot",
            "timestamp": time.time(),
            "page_title": driver.title,
            "current_url": driver.current_url
        }
        
        # 保存到文件
        if screenshot_path:
            Path(screenshot_path).write_bytes(screenshot_data)
            result["screenshot_path"] = screenshot_path
            logger.info(f"截图已保存: {screenshot_path}")
        
        # 返回Base64数据
        if return_base64:
            result["screenshot_base64"] = base64.b64encode(screenshot_data).decode('utf-8')
        
        return result
    
    async def _get_text(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """获取元素文本"""
        selector = kwargs.get("selector")
        
        if selector:
            by, value = ElementLocator.parse_selector(selector)
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            text = element.text
        else:
            # 获取整个页面的文本
            text = driver.find_element(By.TAG_NAME, "body").text
        
        logger.info(f"获取文本: {len(text)} 字符")
        
        return {
            "action": "get_text",
            "selector": selector,
            "text": text,
            "text_length": len(text)
        }
    
    async def _get_attribute(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """获取元素属性"""
        selector = kwargs.get("selector")
        attribute = kwargs.get("attribute", "value")
        
        if not selector:
            raise ValueError("获取属性操作需要提供元素选择器")
        
        by, value = ElementLocator.parse_selector(selector)
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        attr_value = element.get_attribute(attribute)
        
        logger.info(f"获取属性 {attribute}: {attr_value}")
        
        return {
            "action": "get_attribute",
            "selector": selector,
            "attribute": attribute,
            "value": attr_value
        }
    
    async def _wait_for_element(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """等待元素出现"""
        selector = kwargs.get("selector")
        timeout = kwargs.get("timeout", self.config.browser_timeout)
        
        if not selector:
            raise ValueError("等待操作需要提供元素选择器")
        
        by, value = ElementLocator.parse_selector(selector)
        wait = WebDriverWait(driver, timeout)
        
        element = wait.until(EC.presence_of_element_located((by, value)))
        
        logger.info(f"元素已出现: {selector}")
        
        return {
            "action": "wait",
            "selector": selector,
            "element_found": True,
            "element_text": element.text
        }
    
    async def _execute_script(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """执行JavaScript"""
        script = kwargs.get("script") or multimodal_input.text
        
        if not script:
            raise ValueError("执行脚本操作需要提供JavaScript代码")
        
        result = driver.execute_script(script)
        
        logger.info(f"执行JavaScript: {script[:100]}...")
        
        return {
            "action": "execute_script",
            "script": script,
            "result": result
        }
    
    async def _go_back(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """后退"""
        driver.back()
        await asyncio.sleep(1)
        
        return {
            "action": "back",
            "current_url": driver.current_url,
            "title": driver.title
        }
    
    async def _go_forward(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """前进"""
        driver.forward()
        await asyncio.sleep(1)
        
        return {
            "action": "forward",
            "current_url": driver.current_url,
            "title": driver.title
        }
    
    async def _refresh_page(
        self,
        driver: webdriver.Chrome,
        multimodal_input: MultimodalInput,
        **kwargs
    ) -> Dict[str, Any]:
        """刷新页面"""
        driver.refresh()
        await asyncio.sleep(2)
        
        return {
            "action": "refresh",
            "current_url": driver.current_url,
            "title": driver.title
        }
    
    def get_supported_task_types(self) -> List[str]:
        """获取支持的任务类型"""
        return ["web_automation", "browser_control", "web_scraping", "general"]
    
    def get_supported_actions(self) -> List[str]:
        """获取支持的操作类型"""
        return [
            BrowserActionType.NAVIGATE,
            BrowserActionType.CLICK,
            BrowserActionType.INPUT,
            BrowserActionType.SCROLL,
            BrowserActionType.SCREENSHOT,
            BrowserActionType.GET_TEXT,
            BrowserActionType.GET_ATTRIBUTE,
            BrowserActionType.WAIT,
            BrowserActionType.EXECUTE_SCRIPT,
            BrowserActionType.BACK,
            BrowserActionType.FORWARD,
            BrowserActionType.REFRESH,
        ]
    
    async def close(self) -> None:
        """关闭浏览器并清理资源"""
        await self._cleanup_driver()
        logger.info("浏览器工具已关闭")
    
    def __del__(self):
        """析构函数，确保资源清理"""
        if self.driver:
            try:
                asyncio.create_task(self._cleanup_driver())
            except Exception:
                pass