"""
天气查询工具 - 基于OpenWeatherMap API的天气信息获取

这个模块实现了天气查询工具，支持：
1. 根据城市名查询当前天气
2. 异步HTTP请求处理
3. API密钥管理和验证
4. 结构化的天气数据返回

学习要点：
1. 异步HTTP客户端的使用（aiohttp）
2. 外部API的集成和错误处理
3. 环境变量的安全管理
4. 数据转换和格式化
5. 网络请求的超时和重试机制
"""

import asyncio
import aiohttp
import os
import time
from typing import Any, Dict, Optional
from .base import BaseTool, ToolResult


class WeatherTool(BaseTool):
    """
    天气查询工具
    
    使用OpenWeatherMap API获取天气信息
    需要API密钥：https://openweathermap.org/api
    
    学习要点：
    - 外部API集成的最佳实践
    - 异步HTTP请求的处理
    - API密钥的安全管理
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化天气工具
        
        学习要点：
        - 可选参数的处理
        - 环境变量的读取
        - API配置的管理
        
        Args:
            api_key: OpenWeatherMap API密钥，如果不提供则从环境变量读取
        """
        super().__init__(
            name="weather",
            description="查询指定城市的当前天气信息"
        )
        
        # API配置
        self.api_key = api_key or os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.timeout = 10  # 请求超时时间（秒）
        
        if not self.api_key:
            raise ValueError(
                "Weather API密钥未配置。请设置WEATHER_API_KEY环境变量或在初始化时提供api_key参数。"
                "获取API密钥：https://openweathermap.org/api"
            )
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回天气工具的JSON Schema
        
        学习要点：
        - 复杂参数结构的定义
        - 枚举值的约束
        - 默认值的设置
        """
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，可以是中文或英文",
                    "examples": ["北京", "Beijing", "上海", "Shanghai", "New York"]
                },
                "country": {
                    "type": "string",
                    "description": "国家代码（可选），如CN、US等",
                    "examples": ["CN", "US", "JP"],
                    "pattern": "^[A-Z]{2}$"
                },
                "units": {
                    "type": "string",
                    "description": "温度单位",
                    "enum": ["metric", "imperial", "kelvin"],
                    "default": "metric"
                },
                "lang": {
                    "type": "string", 
                    "description": "返回语言",
                    "enum": ["zh_cn", "en", "ja"],
                    "default": "zh_cn"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        }
    
    def _build_query_params(self, city: str, country: Optional[str] = None,
                           units: str = "metric", lang: str = "zh_cn") -> Dict[str, str]:
        """
        构建API查询参数
        
        学习要点：
        - 参数构建的封装
        - 字符串格式化
        - 条件参数的处理
        
        Args:
            city: 城市名称
            country: 国家代码
            units: 温度单位
            lang: 语言
            
        Returns:
            Dict: API查询参数
        """
        # 构建查询字符串
        query = city
        if country:
            query = f"{city},{country}"
        
        return {
            'q': query,
            'appid': self.api_key,
            'units': units,
            'lang': lang
        }
    
    def _format_weather_data(self, data: Dict[str, Any], units: str) -> Dict[str, Any]:
        """
        格式化天气数据
        
        学习要点：
        - 数据转换和格式化
        - 嵌套字典的处理
        - 单位转换的处理
        
        Args:
            data: API返回的原始数据
            units: 温度单位
            
        Returns:
            Dict: 格式化后的天气数据
        """
        # 温度单位符号
        temp_unit = {
            'metric': '°C',
            'imperial': '°F', 
            'kelvin': 'K'
        }.get(units, '°C')
        
        # 提取主要天气信息
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        clouds = data.get('clouds', {})
        sys = data.get('sys', {})
        
        return {
            'city': data.get('name', '未知'),
            'country': sys.get('country', '未知'),
            'coordinates': {
                'latitude': data.get('coord', {}).get('lat'),
                'longitude': data.get('coord', {}).get('lon')
            },
            'weather': {
                'main': weather.get('main', '未知'),
                'description': weather.get('description', '无描述'),
                'icon': weather.get('icon')
            },
            'temperature': {
                'current': f"{main.get('temp', 0)}{temp_unit}",
                'feels_like': f"{main.get('feels_like', 0)}{temp_unit}",
                'min': f"{main.get('temp_min', 0)}{temp_unit}",
                'max': f"{main.get('temp_max', 0)}{temp_unit}"
            },
            'humidity': f"{main.get('humidity', 0)}%",
            'pressure': f"{main.get('pressure', 0)} hPa",
            'visibility': f"{data.get('visibility', 0) / 1000:.1f} km" if data.get('visibility') else "未知",
            'wind': {
                'speed': f"{wind.get('speed', 0)} m/s",
                'direction': f"{wind.get('deg', 0)}°"
            },
            'clouds': f"{clouds.get('all', 0)}%",
            'sunrise': time.strftime('%H:%M:%S', time.localtime(sys.get('sunrise', 0))),
            'sunset': time.strftime('%H:%M:%S', time.localtime(sys.get('sunset', 0))),
            'timezone': f"UTC{data.get('timezone', 0) // 3600:+d}",
            'data_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('dt', 0)))
        }
    
    async def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        发起HTTP请求
        
        学习要点：
        - 异步HTTP客户端的使用
        - 超时处理
        - HTTP状态码的处理
        - 异常处理的层次化
        
        Args:
            params: 请求参数
            
        Returns:
            Dict: API响应数据
            
        Raises:
            aiohttp.ClientError: 网络请求错误
            ValueError: API响应错误
        """
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    # 检查HTTP状态码
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise ValueError("API密钥无效或已过期")
                    elif response.status == 404:
                        raise ValueError("找不到指定的城市")
                    elif response.status == 429:
                        raise ValueError("API请求频率超限，请稍后重试")
                    else:
                        error_text = await response.text()
                        raise ValueError(f"API请求失败 (状态码: {response.status}): {error_text}")
                        
            except asyncio.TimeoutError:
                raise ValueError(f"请求超时（{self.timeout}秒）")
            except aiohttp.ClientError as e:
                raise ValueError(f"网络请求错误: {e}")
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行天气查询
        
        学习要点：
        - 完整的异步工作流程
        - 多层错误处理
        - 执行时间统计
        - 结构化结果返回
        
        Args:
            **kwargs: 包含city等参数的字典
            
        Returns:
            ToolResult: 天气查询结果
        """
        start_time = time.time()
        
        try:
            # 验证输入参数
            validation_result = self.validate_input(**kwargs)
            if validation_result is not True:
                return ToolResult.invalid_input(validation_result)
            
            # 提取参数
            city = kwargs['city'].strip()
            country = kwargs.get('country', '').strip() or None
            units = kwargs.get('units', 'metric')
            lang = kwargs.get('lang', 'zh_cn')
            
            # 构建请求参数
            params = self._build_query_params(city, country, units, lang)
            
            # 发起API请求
            raw_data = await self._make_request(params)
            
            # 格式化数据
            formatted_data = self._format_weather_data(raw_data, units)
            
            execution_time = time.time() - start_time
            
            return ToolResult.success(
                content=formatted_data,
                execution_time=execution_time,
                metadata={
                    'tool': self.name,
                    'api_provider': 'OpenWeatherMap',
                    'query_city': city,
                    'query_country': country,
                    'units': units,
                    'language': lang
                }
            )
            
        except ValueError as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=str(e),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=f"天气查询过程中发生未知错误: {e}",
                execution_time=execution_time
            )


# 使用示例和测试代码
if __name__ == "__main__":
    """
    模块测试代码
    
    注意：需要设置WEATHER_API_KEY环境变量
    """
    import asyncio
    
    async def test_weather_tool():
        """测试天气工具的各种功能"""
        try:
            # 创建天气工具（需要API密钥）
            weather = WeatherTool()
            
            print(f"=== {weather.name} 工具测试 ===")
            print(f"描述: {weather.description}")
            print(f"Schema: {weather.schema}")
            print()
            
            # 测试用例
            test_cases = [
                {"city": "北京"},
                {"city": "Shanghai", "country": "CN"},
                {"city": "New York", "country": "US", "units": "imperial"},
                {"city": "Tokyo", "country": "JP", "lang": "en"},
                {"city": "不存在的城市"},  # 测试错误情况
            ]
            
            for case in test_cases:
                print(f"测试查询: {case}")
                result = await weather.execute(**case)
                
                if result.status == "success":
                    data = result.content
                    print(f"城市: {data['city']}, {data['country']}")
                    print(f"天气: {data['weather']['description']}")
                    print(f"温度: {data['temperature']['current']}")
                    print(f"湿度: {data['humidity']}")
                else:
                    print(f"查询失败: {result.error_message}")
                
                print("-" * 50)
                
        except ValueError as e:
            print(f"初始化失败: {e}")
            print("请设置WEATHER_API_KEY环境变量")
    
    # 运行测试
    asyncio.run(test_weather_tool())