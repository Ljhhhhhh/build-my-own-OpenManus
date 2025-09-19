"""
异步天气工具

这个模块实现了一个简化的异步天气查询工具。
专注于异步HTTP请求和外部API调用的核心概念，移除了复杂的缓存机制和高级特性。

学习要点：
1. 异步HTTP请求的实现
2. 外部API的调用和处理
3. JSON数据的解析
4. 基础错误处理
"""

import asyncio
import aiohttp
from typing import Dict, Any, Union, Optional

from .base import AsyncBaseTool, ToolResult


class AsyncWeatherTool(AsyncBaseTool):
    """
    异步天气查询工具
    
    💡 对比TypeScript:
    class AsyncWeatherTool extends AsyncBaseTool {
        private apiKey: string;
        private baseUrl: string;
        
        constructor(apiKey: string) {
            super("async_weather", "异步天气查询工具", 30.0);
            this.apiKey = apiKey;
            this.baseUrl = "http://api.openweathermap.org/data/2.5";
        }
        
        get schema(): object {
            return {
                type: "object",
                properties: {
                    city: {
                        type: "string",
                        description: "要查询天气的城市名称"
                    },
                    country: {
                        type: "string",
                        description: "国家代码（可选）"
                    },
                    units: {
                        type: "string",
                        enum: ["metric", "imperial", "standard"],
                        default: "metric",
                        description: "温度单位"
                    }
                },
                required: ["city"]
            };
        }
        
        async validateInput(params: any): Promise<boolean | string> {
            const { city, country, units } = params;
            
            if (!city || typeof city !== "string" || city.trim().length === 0) {
                return "城市名称不能为空";
            }
            
            if (country && (typeof country !== "string" || country.length !== 2)) {
                return "国家代码必须是2位字母";
            }
            
            if (units && !["metric", "imperial", "standard"].includes(units)) {
                return "无效的温度单位";
            }
            
            return true;
        }
        
        async execute(params: any): Promise<ToolResult> {
            const { city, country, units = "metric" } = params;
            
            try {
                // 构建查询参数
                const location = country ? `${city},${country}` : city;
                const url = `${this.baseUrl}/weather?q=${encodeURIComponent(location)}&appid=${this.apiKey}&units=${units}`;
                
                // 发送HTTP请求
                const response = await fetch(url);
                
                if (!response.ok) {
                    if (response.status === 404) {
                        return ToolResult.error(`未找到城市: ${city}`);
                    }
                    return ToolResult.error(`API请求失败: ${response.status}`);
                }
                
                const data = await response.json();
                
                // 解析天气数据
                const weatherInfo = {
                    city: data.name,
                    country: data.sys.country,
                    temperature: data.main.temp,
                    feels_like: data.main.feels_like,
                    humidity: data.main.humidity,
                    pressure: data.main.pressure,
                    description: data.weather[0].description,
                    wind_speed: data.wind?.speed || 0,
                    units: units
                };
                
                return ToolResult.success(weatherInfo);
                
            } catch (error) {
                return ToolResult.error(`天气查询失败: ${error.message}`);
            }
        }
    }
    
    学习要点：
    - 异步HTTP请求的完整实现
    - 外部API的集成和调用
    - JSON数据的解析和处理
    - 错误处理的基础实践
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化异步天气工具
        
        学习要点：
        - 外部依赖的管理
        - API密钥的处理
        - 配置参数的设置
        
        Args:
            api_key: OpenWeatherMap API密钥（可选，用于演示）
        """
        super().__init__(
            name="async_weather",
            description="异步天气查询工具，支持全球城市天气查询",
            timeout=30.0
        )
        
        # API配置
        self.api_key = api_key or "demo_key"  # 演示用密钥
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # 支持的温度单位
        self.supported_units = {
            "metric": "摄氏度",
            "imperial": "华氏度", 
            "standard": "开尔文"
        }
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        定义工具的输入参数模式
        
        学习要点：
        - API参数的定义
        - 枚举值的使用
        - 可选参数的处理
        - 默认值的设置
        
        Returns:
            Dict[str, Any]: JSON Schema 格式的参数定义
        """
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称",
                    "minLength": 1,
                    "maxLength": 100
                },
                "country": {
                    "type": "string",
                    "description": "国家代码（可选，如：US, CN, JP）",
                    "pattern": "^[A-Z]{2}$"
                },
                "units": {
                    "type": "string",
                    "enum": list(self.supported_units.keys()),
                    "default": "metric",
                    "description": "温度单位：metric(摄氏度), imperial(华氏度), standard(开尔文)"
                }
            },
            "required": ["city"]
        }
    
    async def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        验证输入参数
        
        学习要点：
        - 字符串参数的验证
        - 长度和格式检查
        - 枚举值的验证
        - 可选参数的处理
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            Union[bool, str]: True表示验证通过，字符串表示错误信息
        """
        # 调用基类的基础验证
        base_validation = await super().validate_input(**kwargs)
        if base_validation is not True:
            return base_validation
        
        city = kwargs.get("city")
        country = kwargs.get("country")
        units = kwargs.get("units", "metric")
        
        # 验证城市名称
        if not city or not isinstance(city, str):
            return "城市名称不能为空且必须是字符串"
        
        if len(city.strip()) == 0:
            return "城市名称不能为空白字符"
        
        if len(city) > 100:
            return "城市名称长度不能超过100个字符"
        
        # 验证国家代码（可选）
        if country is not None:
            if not isinstance(country, str):
                return "国家代码必须是字符串"
            
            if len(country) != 2:
                return "国家代码必须是2位字母（如：US, CN, JP）"
            
            if not country.isalpha() or not country.isupper():
                return "国家代码必须是2位大写字母"
        
        # 验证温度单位
        if units not in self.supported_units:
            return f"不支持的温度单位: {units}。支持的单位: {list(self.supported_units.keys())}"
        
        return True
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行天气查询
        
        学习要点：
        - 异步HTTP请求的实现
        - aiohttp库的使用
        - JSON数据的解析
        - 错误处理和状态码检查
        - 超时处理
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 查询结果
        """
        try:
            city = kwargs["city"].strip()
            country = kwargs.get("country")
            units = kwargs.get("units", "metric")
            
            # 构建查询位置
            location = f"{city},{country}" if country else city
            
            # 构建API URL
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units,
                "lang": "zh_cn"  # 中文描述
            }
            
            # 发送异步HTTP请求
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=25)) as response:
                    
                    # 检查响应状态
                    if response.status == 404:
                        return ToolResult.error(f"未找到城市: {city}")
                    elif response.status == 401:
                        return ToolResult.error("API密钥无效或已过期")
                    elif response.status == 429:
                        return ToolResult.error("API请求频率超限，请稍后重试")
                    elif response.status != 200:
                        return ToolResult.error(f"API请求失败，状态码: {response.status}")
                    
                    # 解析JSON响应
                    data = await response.json()
                    
                    # 提取天气信息
                    weather_info = self._parse_weather_data(data, units)
                    
                    return ToolResult.success(weather_info)
        
        except asyncio.TimeoutError:
            return ToolResult.error("天气查询超时，请检查网络连接")
        except aiohttp.ClientError as e:
            return ToolResult.error(f"网络请求错误: {str(e)}")
        except KeyError as e:
            return ToolResult.error(f"API响应数据格式错误，缺少字段: {str(e)}")
        except Exception as e:
            return ToolResult.error(f"天气查询失败: {str(e)}")
    
    def _parse_weather_data(self, data: Dict[str, Any], units: str) -> Dict[str, Any]:
        """
        解析天气API响应数据
        
        学习要点：
        - JSON数据的解析和提取
        - 数据结构的转换
        - 安全的字典访问
        - 数据格式化
        
        Args:
            data: API响应的JSON数据
            units: 温度单位
            
        Returns:
            Dict[str, Any]: 格式化后的天气信息
        """
        # 基础信息
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "coordinates": {
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"]
            }
        }
        
        # 温度信息
        main_data = data["main"]
        weather_info.update({
            "temperature": main_data["temp"],
            "feels_like": main_data["feels_like"],
            "min_temperature": main_data.get("temp_min"),
            "max_temperature": main_data.get("temp_max"),
            "humidity": main_data["humidity"],
            "pressure": main_data["pressure"]
        })
        
        # 天气描述
        weather_data = data["weather"][0]
        weather_info.update({
            "condition": weather_data["main"],
            "description": weather_data["description"],
            "icon": weather_data["icon"]
        })
        
        # 风力信息
        wind_data = data.get("wind", {})
        weather_info["wind"] = {
            "speed": wind_data.get("speed", 0),
            "direction": wind_data.get("deg")
        }
        
        # 其他信息
        weather_info.update({
            "visibility": data.get("visibility"),
            "cloudiness": data.get("clouds", {}).get("all"),
            "units": units,
            "unit_symbol": self._get_temperature_symbol(units),
            "timestamp": data["dt"]
        })
        
        # 格式化显示
        weather_info["formatted"] = self._format_weather_display(weather_info)
        
        return weather_info
    
    def _get_temperature_symbol(self, units: str) -> str:
        """
        获取温度单位符号
        
        Args:
            units: 温度单位
            
        Returns:
            str: 温度符号
        """
        symbols = {
            "metric": "°C",
            "imperial": "°F",
            "standard": "K"
        }
        return symbols.get(units, "°C")
    
    def _format_weather_display(self, weather_info: Dict[str, Any]) -> str:
        """
        格式化天气信息显示
        
        学习要点：
        - 字符串格式化
        - 数据展示的优化
        - 用户友好的信息呈现
        
        Args:
            weather_info: 天气信息字典
            
        Returns:
            str: 格式化后的天气描述
        """
        city = weather_info["city"]
        country = weather_info["country"]
        temp = weather_info["temperature"]
        feels_like = weather_info["feels_like"]
        description = weather_info["description"]
        humidity = weather_info["humidity"]
        wind_speed = weather_info["wind"]["speed"]
        symbol = weather_info["unit_symbol"]
        
        formatted = f"""
🌤️ {city}, {country} 天气信息:
🌡️ 温度: {temp}{symbol} (体感: {feels_like}{symbol})
☁️ 天气: {description}
💧 湿度: {humidity}%
💨 风速: {wind_speed} m/s
        """.strip()
        
        return formatted


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_async_weather():
        """
        测试异步天气查询功能
        
        学习要点：
        - 异步测试的编写
        - HTTP请求的测试
        - 错误情况的模拟
        - 结果验证的方法
        """
        print("🌤️ 测试异步天气查询工具")
        print("=" * 40)
        
        # 创建天气工具实例（使用演示密钥）
        weather_tool = AsyncWeatherTool()
        print(f"工具信息: {weather_tool}")
        print(f"支持的温度单位: {list(weather_tool.supported_units.keys())}")
        
        # 测试用例（注意：由于使用演示密钥，实际请求会失败，这里主要测试验证逻辑）
        test_cases = [
            {"city": "Beijing", "country": "CN", "units": "metric", "description": "北京天气查询"},
            {"city": "Shanghai", "units": "metric", "description": "上海天气查询"},
            {"city": "New York", "country": "US", "units": "imperial", "description": "纽约天气查询"},
            {"city": "Tokyo", "country": "JP", "units": "metric", "description": "东京天气查询"},
        ]
        
        print("\n🧪 测试输入验证:")
        for i, test_case in enumerate(test_cases, 1):
            city = test_case["city"]
            country = test_case.get("country")
            units = test_case.get("units", "metric")
            description = test_case["description"]
            
            # 测试输入验证
            validation_result = await weather_tool.validate_input(
                city=city, country=country, units=units
            )
            
            if validation_result is True:
                print(f"  {i}. {description}: 输入验证通过 ✅")
            else:
                print(f"  {i}. {description}: 输入验证失败 - {validation_result} ❌")
        
        # 测试错误情况
        print("\n🚫 测试错误情况:")
        
        error_cases = [
            {"city": "", "description": "空城市名称"},
            {"city": "Beijing", "country": "CHN", "description": "无效国家代码（3位）"},
            {"city": "Shanghai", "country": "cn", "description": "小写国家代码"},
            {"city": "Tokyo", "units": "celsius", "description": "无效温度单位"},
            {"city": None, "description": "None城市名称"},
            {"city": "A" * 101, "description": "城市名称过长"},
        ]
        
        for i, error_case in enumerate(error_cases, 1):
            try:
                validation_result = await weather_tool.validate_input(**{k: v for k, v in error_case.items() if k != "description"})
                if validation_result is not True:
                    print(f"  {i}. {error_case['description']}: 验证失败 - {validation_result} ✅")
                else:
                    print(f"  {i}. {error_case['description']}: 意外通过验证 ❌")
            except Exception as e:
                print(f"  {i}. {error_case['description']}: 异常 - {str(e)} ✅")
        
        # 测试API调用（注意：由于使用演示密钥，会返回错误，这是预期的）
        print("\n🌐 测试API调用（演示密钥，预期失败）:")
        
        demo_case = {"city": "Beijing", "country": "CN", "units": "metric"}
        result = await weather_tool.execute_with_timeout(**demo_case)
        
        if result.is_error():
            print(f"  API调用失败（预期）: {result.error_message} ✅")
        else:
            print(f"  API调用成功（意外）: {result.content} ❌")
        
        # 测试数据解析功能
        print("\n📊 测试数据解析功能:")
        
        # 模拟API响应数据
        mock_api_response = {
            "coord": {"lon": 116.3972, "lat": 39.9075},
            "weather": [{"id": 800, "main": "Clear", "description": "晴朗", "icon": "01d"}],
            "main": {
                "temp": 25.5,
                "feels_like": 27.2,
                "temp_min": 22.1,
                "temp_max": 28.3,
                "pressure": 1013,
                "humidity": 65
            },
            "wind": {"speed": 3.2, "deg": 180},
            "clouds": {"all": 10},
            "visibility": 10000,
            "dt": 1640995200,
            "sys": {"country": "CN"},
            "name": "Beijing"
        }
        
        try:
            parsed_data = weather_tool._parse_weather_data(mock_api_response, "metric")
            print(f"  数据解析成功 ✅")
            print(f"  城市: {parsed_data['city']}")
            print(f"  温度: {parsed_data['temperature']}°C")
            print(f"  描述: {parsed_data['description']}")
            print(f"  格式化显示:")
            print(f"    {parsed_data['formatted']}")
        except Exception as e:
            print(f"  数据解析失败: {str(e)} ❌")
        
        print("\n✅ 异步天气查询测试完成!")
        print("\n💡 提示: 要进行真实的天气查询，请:")
        print("  1. 注册 OpenWeatherMap 账号获取API密钥")
        print("  2. 创建工具时传入真实的API密钥")
        print("  3. 确保网络连接正常")
    
    # 运行测试
    asyncio.run(test_async_weather())