"""
浏览器自动化工具测试用例

测试BrowserTool的各种功能。

学习要点：
- 浏览器自动化测试
- Selenium WebDriver模拟
- 异步上下文管理器测试
- 资源清理测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from contextlib import asynccontextmanager

from tools import BrowserTool, BrowserActionType, MultimodalInput, ToolResultStatus
from utils.config import Config


class TestBrowserTool:
    """浏览器工具测试类"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock(spec=Config)
        config.browser_headless = True
        config.browser_timeout = 30
        config.browser_window_width = 1920
        config.browser_window_height = 1080
        config.browser_user_agent = None
        config.browser_download_dir = None
        config.webdriver_auto_install = True
        config.webdriver_path = None
        config.webdriver_log_level = "WARNING"
        config.tool_timeout = 30
        return config
    
    @pytest.fixture
    def mock_webdriver(self):
        """创建模拟WebDriver"""
        driver = Mock()
        driver.current_url = "https://example.com"
        driver.title = "Example Page"
        driver.get_screenshot_as_png.return_value = b"fake_screenshot_data"
        driver.find_element.return_value = Mock()
        driver.execute_script.return_value = None
        return driver
    
    def test_browser_tool_initialization(self, mock_config):
        """测试浏览器工具初始化"""
        tool = BrowserTool(mock_config)
        
        assert tool.name == "browser_tool"
        assert tool.config == mock_config
        assert tool.driver is None
        assert tool.wait is None
    
    def test_get_supported_actions(self, mock_config):
        """测试获取支持的操作类型"""
        tool = BrowserTool(mock_config)
        
        supported_actions = tool.get_supported_actions()
        
        assert BrowserActionType.NAVIGATE in supported_actions
        assert BrowserActionType.CLICK in supported_actions
        assert BrowserActionType.INPUT in supported_actions
        assert BrowserActionType.SCROLL in supported_actions
        assert BrowserActionType.SCREENSHOT in supported_actions
        assert BrowserActionType.GET_TEXT in supported_actions
        assert BrowserActionType.EXECUTE_SCRIPT in supported_actions
    
    def test_get_supported_task_types(self, mock_config):
        """测试获取支持的任务类型"""
        tool = BrowserTool(mock_config)
        
        supported_types = tool.get_supported_task_types()
        
        assert "web_automation" in supported_types
        assert "browser_control" in supported_types
        assert "web_scraping" in supported_types
        assert "general" in supported_types
    
    @pytest.mark.asyncio
    async def test_initialize_driver(self, mock_config):
        """测试WebDriver初始化"""
        tool = BrowserTool(mock_config)
        
        with patch('tools.browser_automation.webdriver.Chrome') as mock_chrome, \
             patch('tools.browser_automation.ChromeDriverManager') as mock_manager, \
             patch('tools.browser_automation.ChromeService') as mock_service:
            
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            mock_manager.return_value.install.return_value = "/path/to/chromedriver"
            
            await tool._initialize_driver()
            
            assert tool.driver == mock_driver
            assert tool.wait is not None
            mock_driver.implicitly_wait.assert_called_once_with(30)
            mock_driver.set_page_load_timeout.assert_called_once_with(30)
    
    @pytest.mark.asyncio
    async def test_cleanup_driver(self, mock_config, mock_webdriver):
        """测试WebDriver清理"""
        tool = BrowserTool(mock_config)
        tool.driver = mock_webdriver
        
        await tool._cleanup_driver()
        
        assert tool.driver is None
        assert tool.wait is None
        mock_webdriver.quit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_navigate_action(self, mock_config, mock_webdriver):
        """测试导航操作"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="https://example.com",
            task_type="web_automation"
        )
        
        result = await tool._navigate(mock_webdriver, multimodal_input, url="https://example.com")
        
        assert result["action"] == "navigate"
        assert result["url"] == "https://example.com"
        assert result["current_url"] == "https://example.com"
        assert result["title"] == "Example Page"
        mock_webdriver.get.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_navigate_action_with_url_formatting(self, mock_config, mock_webdriver):
        """测试导航操作（URL格式化）"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="example.com",
            task_type="web_automation"
        )
        
        result = await tool._navigate(mock_webdriver, multimodal_input, url="example.com")
        
        # 应该自动添加https://前缀
        mock_webdriver.get.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_click_element_action(self, mock_config, mock_webdriver):
        """测试点击元素操作"""
        tool = BrowserTool(mock_config)
        
        # Mock WebDriverWait和元素
        mock_element = Mock()
        mock_element.text = "Click Me"
        mock_element.tag_name = "button"
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        tool.wait = mock_wait
        
        multimodal_input = MultimodalInput(
            text="点击按钮",
            task_type="web_automation"
        )
        
        result = await tool._click_element(
            mock_webdriver, 
            multimodal_input, 
            selector="css:button.submit"
        )
        
        assert result["action"] == "click"
        assert result["selector"] == "css:button.submit"
        assert result["element_text"] == "Click Me"
        assert result["element_tag"] == "button"
        mock_element.click.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_input_text_action(self, mock_config, mock_webdriver):
        """测试输入文本操作"""
        tool = BrowserTool(mock_config)
        
        # Mock WebDriverWait和元素
        mock_element = Mock()
        mock_element.get_attribute.return_value = "test input"
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        tool.wait = mock_wait
        
        multimodal_input = MultimodalInput(
            text="输入测试文本",
            task_type="web_automation"
        )
        
        result = await tool._input_text(
            mock_webdriver,
            multimodal_input,
            selector="id:username",
            text="test input"
        )
        
        assert result["action"] == "input"
        assert result["selector"] == "id:username"
        assert result["text"] == "test input"
        assert result["element_value"] == "test input"
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("test input")
    
    @pytest.mark.asyncio
    async def test_scroll_page_action(self, mock_config, mock_webdriver):
        """测试页面滚动操作"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="向下滚动",
            task_type="web_automation"
        )
        
        # 测试向下滚动
        result = await tool._scroll_page(
            mock_webdriver,
            multimodal_input,
            direction="down",
            pixels=500
        )
        
        assert result["action"] == "scroll"
        assert result["direction"] == "down"
        assert result["pixels"] == 500
        mock_webdriver.execute_script.assert_called_with("window.scrollBy(0, 500);")
    
    @pytest.mark.asyncio
    async def test_take_screenshot_action(self, mock_config, mock_webdriver):
        """测试截图操作"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="截图",
            task_type="web_automation"
        )
        
        result = await tool._take_screenshot(
            mock_webdriver,
            multimodal_input,
            return_base64=True
        )
        
        assert result["action"] == "screenshot"
        assert result["page_title"] == "Example Page"
        assert result["current_url"] == "https://example.com"
        assert "screenshot_base64" in result
        assert "timestamp" in result
        mock_webdriver.get_screenshot_as_png.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_text_action(self, mock_config, mock_webdriver):
        """测试获取文本操作"""
        tool = BrowserTool(mock_config)
        
        # Mock元素和WebDriverWait
        mock_element = Mock()
        mock_element.text = "页面文本内容"
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        tool.wait = mock_wait
        
        multimodal_input = MultimodalInput(
            text="获取文本",
            task_type="web_automation"
        )
        
        result = await tool._get_text(
            mock_webdriver,
            multimodal_input,
            selector="css:.content"
        )
        
        assert result["action"] == "get_text"
        assert result["selector"] == "css:.content"
        assert result["text"] == "页面文本内容"
        assert result["text_length"] == len("页面文本内容")
    
    @pytest.mark.asyncio
    async def test_execute_script_action(self, mock_config, mock_webdriver):
        """测试执行JavaScript操作"""
        tool = BrowserTool(mock_config)
        
        mock_webdriver.execute_script.return_value = "script result"
        
        multimodal_input = MultimodalInput(
            text="return document.title;",
            task_type="web_automation"
        )
        
        result = await tool._execute_script(
            mock_webdriver,
            multimodal_input,
            script="return document.title;"
        )
        
        assert result["action"] == "execute_script"
        assert result["script"] == "return document.title;"
        assert result["result"] == "script result"
        mock_webdriver.execute_script.assert_called_once_with("return document.title;")
    
    def test_element_locator_parse_selector(self):
        """测试元素定位器选择器解析"""
        from tools.browser_automation import ElementLocator
        from selenium.webdriver.common.by import By
        
        # 测试各种选择器格式
        test_cases = [
            ("id:username", (By.ID, "username")),
            ("class:btn-primary", (By.CLASS_NAME, "btn-primary")),
            ("css:.container", (By.CSS_SELECTOR, ".container")),
            ("xpath://div[@id='main']", (By.XPATH, "//div[@id='main']")),
            ("name:email", (By.NAME, "email")),
            ("text:Click Here", (By.LINK_TEXT, "Click Here")),
            (".container", (By.CSS_SELECTOR, ".container")),  # 默认CSS选择器
        ]
        
        for selector_str, expected in test_cases:
            by_type, value = ElementLocator.parse_selector(selector_str)
            assert by_type == expected[0]
            assert value == expected[1]
    
    @pytest.mark.asyncio
    async def test_execute_multimodal_success(self, mock_config):
        """测试成功执行多模态操作"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="https://example.com",
            task_type="web_automation"
        )
        
        # Mock _get_driver上下文管理器
        mock_driver = Mock()
        
        @asynccontextmanager
        async def mock_get_driver():
            yield mock_driver
        
        # Mock _execute_browser_action
        expected_action_result = {
            "action": "navigate",
            "url": "https://example.com",
            "success": True
        }
        
        with patch.object(tool, '_get_driver', mock_get_driver), \
             patch.object(tool, '_execute_browser_action', return_value=expected_action_result) as mock_execute:
            
            result = await tool.execute_multimodal(
                multimodal_input,
                action=BrowserActionType.NAVIGATE
            )
            
            assert result.status == ToolResultStatus.SUCCESS
            assert result.data == expected_action_result
            assert "浏览器操作完成" in result.message
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_multimodal_error(self, mock_config):
        """测试执行多模态操作错误"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="test",
            task_type="web_automation"
        )
        
        # Mock _get_driver抛出异常
        @asynccontextmanager
        async def mock_get_driver():
            raise Exception("WebDriver initialization failed")
            yield  # 这行不会执行
        
        with patch.object(tool, '_get_driver', mock_get_driver):
            result = await tool.execute_multimodal(multimodal_input)
            
            assert result.status == ToolResultStatus.ERROR
            assert "WebDriver initialization failed" in result.data["error"]
    
    @pytest.mark.asyncio
    async def test_close_method(self, mock_config, mock_webdriver):
        """测试关闭方法"""
        tool = BrowserTool(mock_config)
        tool.driver = mock_webdriver
        
        await tool.close()
        
        assert tool.driver is None
        mock_webdriver.quit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_action_validation_errors(self, mock_config, mock_webdriver):
        """测试操作验证错误"""
        tool = BrowserTool(mock_config)
        
        multimodal_input = MultimodalInput(
            text="test",
            task_type="web_automation"
        )
        
        # 测试点击操作缺少选择器
        with pytest.raises(ValueError) as exc_info:
            await tool._click_element(mock_webdriver, multimodal_input)
        
        assert "点击操作需要提供元素选择器" in str(exc_info.value)
        
        # 测试输入操作缺少选择器
        with pytest.raises(ValueError) as exc_info:
            await tool._input_text(mock_webdriver, multimodal_input)
        
        assert "输入操作需要提供元素选择器" in str(exc_info.value)
        
        # 测试导航操作缺少URL
        multimodal_input_empty = MultimodalInput(
            text="",
            task_type="web_automation"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await tool._navigate(mock_webdriver, multimodal_input_empty)
        
        assert "导航操作需要提供URL" in str(exc_info.value)


# 集成测试
class TestBrowserToolIntegration:
    """浏览器工具集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_browser_workflow(self, mock_config):
        """测试完整的浏览器工作流程"""
        tool = BrowserTool(mock_config)
        
        # Mock整个WebDriver工作流程
        mock_driver = Mock()
        mock_driver.current_url = "https://example.com"
        mock_driver.title = "Example Page"
        
        mock_element = Mock()
        mock_element.text = "Submit"
        mock_element.tag_name = "button"
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        
        with patch('tools.browser_automation.webdriver.Chrome', return_value=mock_driver), \
             patch('tools.browser_automation.ChromeDriverManager'), \
             patch('tools.browser_automation.ChromeService'), \
             patch('tools.browser_automation.WebDriverWait', return_value=mock_wait):
            
            # 测试导航
            multimodal_input = MultimodalInput(
                text="https://example.com",
                task_type="web_automation"
            )
            
            result = await tool.execute_multimodal(
                multimodal_input,
                action=BrowserActionType.NAVIGATE
            )
            
            assert result.status == ToolResultStatus.SUCCESS
            assert result.data["action"] == "navigate"
            
            # 清理
            await tool.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])