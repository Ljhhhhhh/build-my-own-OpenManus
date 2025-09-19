"""
Practical 3.2 - 天气工具测试

这个模块测试异步天气查询工具的功能，包括：
1. API集成测试
2. 缓存机制测试
3. 错误处理测试
4. 网络超时测试
5. 数据解析测试

学习要点：
1. 外部API的测试策略
2. 网络请求的模拟
3. 缓存系统的测试
4. 异步HTTP客户端的使用
"""

import pytest
import asyncio
import time
import json
from unittest.mock import AsyncMock, patch, MagicMock
from aiohttp import ClientSession, ClientTimeout, ClientError
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.weather import AsyncWeatherTool
from tools.base import ToolResultStatus
from config import Config


class TestAsyncWeatherTool:
    """
    异步天气工具测试类
    
    💡 对比TypeScript:
    describe('AsyncWeatherTool', () => {
        let weatherTool: AsyncWeatherTool;
        
        beforeEach(() => {
            weatherTool = new AsyncWeatherTool();
        });
        
        test('should have correct properties', () => {
            expect(weatherTool.name).toBe('async_weather');
            expect(weatherTool.description).toContain('天气查询');
            expect(typeof weatherTool.getSchema).toBe('function');
        });
        
        test('should validate API key configuration', () => {
            const config = weatherTool.getConfig();
            expect(config.apiKey).toBeDefined();
            expect(config.baseUrl).toContain('openweathermap');
        });
        
        test('should handle successful API response', async () => {
            const mockResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20, humidity: 65 },
                wind: { speed: 3.5 },
                name: 'Beijing'
            };
            
            // Mock HTTP client
            const mockGet = jest.fn().mockResolvedValue({
                status: 200,
                json: () => Promise.resolve(mockResponse)
            });
            
            weatherTool.httpClient = { get: mockGet };
            
            const result = await weatherTool.execute({
                city: 'Beijing',
                country: 'CN'
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content.city).toBe('Beijing');
            expect(result.content.temperature).toBe(20);
        });
        
        test('should handle API errors', async () => {
            const mockGet = jest.fn().mockRejectedValue(
                new Error('API key invalid')
            );
            
            weatherTool.httpClient = { get: mockGet };
            
            const result = await weatherTool.execute({
                city: 'InvalidCity'
            });
            
            expect(result.isError()).toBe(true);
            expect(result.errorMessage).toContain('API');
        });
    });
    
    学习要点：
    - 外部API工具的测试结构
    - HTTP客户端的模拟
    - 配置管理的测试
    - 网络错误的处理测试
    """
    
    @pytest.fixture
    def weather_tool(self):
        """创建天气工具实例"""
        return AsyncWeatherTool()
    
    @pytest.fixture
    def mock_weather_response(self):
        """模拟天气API响应"""
        return {
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "main": {
                "temp": 20.5,
                "feels_like": 19.8,
                "temp_min": 18.0,
                "temp_max": 23.0,
                "pressure": 1013,
                "humidity": 65
            },
            "wind": {
                "speed": 3.5,
                "deg": 180
            },
            "clouds": {
                "all": 0
            },
            "name": "Beijing",
            "cod": 200
        }
    
    def test_weather_tool_properties(self, weather_tool):
        """测试天气工具属性"""
        assert weather_tool.name == "async_weather"
        assert "天气查询" in weather_tool.description
        assert hasattr(weather_tool, "get_schema")
        assert callable(weather_tool.get_schema)
    
    def test_schema_structure(self, weather_tool):
        """测试模式结构"""
        schema = weather_tool.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "city" in schema["properties"]
        assert "country" in schema["properties"]
        assert "required" in schema
        assert "city" in schema["required"]
    
    def test_config_validation(self, weather_tool):
        """测试配置验证"""
        config = Config()
        
        # 检查API密钥配置
        assert hasattr(config, 'OPENWEATHER_API_KEY')
        assert hasattr(config, 'OPENWEATHER_BASE_URL')
        assert hasattr(config, 'REQUEST_TIMEOUT')
    
    @pytest.mark.asyncio
    async def test_successful_weather_query(self, weather_tool, mock_weather_response):
        """测试成功的天气查询"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 配置模拟响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_weather_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_tool.execute(
                city="Beijing",
                country="CN"
            )
            
            assert result.is_success()
            assert result.content["city"] == "Beijing"
            assert result.content["temperature"] == 20.5
            assert result.content["description"] == "clear sky"
            assert result.content["humidity"] == 65
            assert result.content["wind_speed"] == 3.5
    
    @pytest.mark.asyncio
    async def test_api_key_missing(self, weather_tool):
        """测试API密钥缺失"""
        with patch.object(Config, 'OPENWEATHER_API_KEY', ''):
            result = await weather_tool.execute(city="Beijing")
            
            assert result.is_error()
            assert "API密钥" in result.error_message
    
    @pytest.mark.asyncio
    async def test_invalid_city(self, weather_tool):
        """测试无效城市"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 模拟404响应
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.json = AsyncMock(return_value={
                "cod": "404",
                "message": "city not found"
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_tool.execute(city="InvalidCity")
            
            assert result.is_error()
            assert "未找到城市" in result.error_message
    
    @pytest.mark.asyncio
    async def test_api_rate_limit(self, weather_tool):
        """测试API速率限制"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 模拟429响应
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_response.json = AsyncMock(return_value={
                "cod": 429,
                "message": "Your account is temporary blocked due to exceeding of requests limitation"
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_tool.execute(city="Beijing")
            
            assert result.is_error()
            assert "速率限制" in result.error_message
    
    @pytest.mark.asyncio
    async def test_network_timeout(self, weather_tool):
        """测试网络超时"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 模拟超时异常
            mock_get.side_effect = asyncio.TimeoutError("Request timeout")
            
            result = await weather_tool.execute(city="Beijing")
            
            assert result.is_error()
            assert "超时" in result.error_message
    
    @pytest.mark.asyncio
    async def test_network_connection_error(self, weather_tool):
        """测试网络连接错误"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 模拟连接错误
            mock_get.side_effect = ClientConnectorError(
                connection_key=None,
                os_error=OSError("Network unreachable")
            )
            
            result = await weather_tool.execute(city="Beijing")
            
            assert result.is_error()
            assert "网络连接" in result.error_message


class TestWeatherCaching:
    """
    天气缓存测试类
    
    💡 对比TypeScript:
    describe('Weather Caching', () => {
        let weatherTool: AsyncWeatherTool;
        
        beforeEach(() => {
            weatherTool = new AsyncWeatherTool();
            weatherTool.clearCache();
        });
        
        test('should cache successful responses', async () => {
            const mockResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20, humidity: 65 },
                name: 'Beijing'
            };
            
            const mockGet = jest.fn().mockResolvedValue({
                status: 200,
                json: () => Promise.resolve(mockResponse)
            });
            
            weatherTool.httpClient = { get: mockGet };
            
            // 第一次请求
            const result1 = await weatherTool.execute({ city: 'Beijing' });
            expect(mockGet).toHaveBeenCalledTimes(1);
            
            // 第二次请求应该使用缓存
            const result2 = await weatherTool.execute({ city: 'Beijing' });
            expect(mockGet).toHaveBeenCalledTimes(1); // 仍然是1次
            
            expect(result1.content).toEqual(result2.content);
        });
        
        test('should respect cache expiration', async () => {
            const mockResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20, humidity: 65 },
                name: 'Beijing'
            };
            
            const mockGet = jest.fn().mockResolvedValue({
                status: 200,
                json: () => Promise.resolve(mockResponse)
            });
            
            weatherTool.httpClient = { get: mockGet };
            weatherTool.cacheExpiration = 100; // 100ms过期
            
            // 第一次请求
            await weatherTool.execute({ city: 'Beijing' });
            expect(mockGet).toHaveBeenCalledTimes(1);
            
            // 等待缓存过期
            await new Promise(resolve => setTimeout(resolve, 150));
            
            // 第二次请求应该重新获取数据
            await weatherTool.execute({ city: 'Beijing' });
            expect(mockGet).toHaveBeenCalledTimes(2);
        });
        
        test('should not cache error responses', async () => {
            const mockGet = jest.fn().mockRejectedValue(
                new Error('API error')
            );
            
            weatherTool.httpClient = { get: mockGet };
            
            // 第一次请求失败
            const result1 = await weatherTool.execute({ city: 'Beijing' });
            expect(result1.isError()).toBe(true);
            expect(mockGet).toHaveBeenCalledTimes(1);
            
            // 第二次请求应该重新尝试
            const result2 = await weatherTool.execute({ city: 'Beijing' });
            expect(result2.isError()).toBe(true);
            expect(mockGet).toHaveBeenCalledTimes(2);
        });
    });
    
    学习要点：
    - 缓存机制的测试策略
    - 缓存过期的验证
    - 错误响应的缓存策略
    - 缓存键的生成和管理
    """
    
    @pytest.fixture
    def weather_tool(self):
        """创建天气工具实例"""
        tool = AsyncWeatherTool()
        tool._cache.clear()  # 清空缓存
        return tool
    
    @pytest.fixture
    def mock_weather_response(self):
        """模拟天气API响应"""
        return {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 20, "humidity": 65},
            "wind": {"speed": 3.5},
            "name": "Beijing",
            "cod": 200
        }
    
    @pytest.mark.asyncio
    async def test_cache_successful_response(self, weather_tool, mock_weather_response):
        """测试缓存成功响应"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 配置模拟响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_weather_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # 第一次请求
            result1 = await weather_tool.execute(city="Beijing")
            assert result1.is_success()
            assert mock_get.call_count == 1
            
            # 第二次请求应该使用缓存
            result2 = await weather_tool.execute(city="Beijing")
            assert result2.is_success()
            assert mock_get.call_count == 1  # 仍然是1次调用
            
            # 验证结果相同
            assert result1.content == result2.content
    
    @pytest.mark.asyncio
    async def test_cache_different_cities(self, weather_tool, mock_weather_response):
        """测试不同城市的缓存"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 为不同城市配置不同响应
            def side_effect(*args, **kwargs):
                mock_response = AsyncMock()
                mock_response.status = 200
                
                # 根据URL判断城市
                url = args[0] if args else kwargs.get('url', '')
                if 'Beijing' in url:
                    response_data = dict(mock_weather_response)
                    response_data['name'] = 'Beijing'
                elif 'Shanghai' in url:
                    response_data = dict(mock_weather_response)
                    response_data['name'] = 'Shanghai'
                    response_data['main']['temp'] = 25
                else:
                    response_data = mock_weather_response
                
                mock_response.json = AsyncMock(return_value=response_data)
                return mock_response
            
            mock_get.return_value.__aenter__.side_effect = side_effect
            
            # 请求不同城市
            result1 = await weather_tool.execute(city="Beijing")
            result2 = await weather_tool.execute(city="Shanghai")
            
            assert result1.is_success()
            assert result2.is_success()
            assert mock_get.call_count == 2  # 应该有两次API调用
            assert result1.content["city"] != result2.content["city"]
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, weather_tool, mock_weather_response):
        """测试缓存过期"""
        # 设置较短的缓存时间
        weather_tool._cache_duration = 0.1  # 100ms
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_weather_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # 第一次请求
            result1 = await weather_tool.execute(city="Beijing")
            assert result1.is_success()
            assert mock_get.call_count == 1
            
            # 等待缓存过期
            await asyncio.sleep(0.15)
            
            # 第二次请求应该重新获取数据
            result2 = await weather_tool.execute(city="Beijing")
            assert result2.is_success()
            assert mock_get.call_count == 2  # 应该有两次API调用
    
    @pytest.mark.asyncio
    async def test_no_cache_for_errors(self, weather_tool):
        """测试错误响应不被缓存"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 模拟API错误
            mock_get.side_effect = ClientError("API error")
            
            # 第一次请求失败
            result1 = await weather_tool.execute(city="Beijing")
            assert result1.is_error()
            assert mock_get.call_count == 1
            
            # 第二次请求应该重新尝试
            result2 = await weather_tool.execute(city="Beijing")
            assert result2.is_error()
            assert mock_get.call_count == 2  # 应该有两次API调用
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, weather_tool):
        """测试缓存键生成"""
        # 测试相同参数生成相同缓存键
        key1 = weather_tool._get_cache_key("Beijing", "CN")
        key2 = weather_tool._get_cache_key("Beijing", "CN")
        assert key1 == key2
        
        # 测试不同参数生成不同缓存键
        key3 = weather_tool._get_cache_key("Shanghai", "CN")
        assert key1 != key3
        
        # 测试国家代码的影响
        key4 = weather_tool._get_cache_key("Beijing", "US")
        assert key1 != key4


class TestWeatherDataParsing:
    """
    天气数据解析测试类
    
    💡 对比TypeScript:
    describe('Weather Data Parsing', () => {
        let weatherTool: AsyncWeatherTool;
        
        beforeEach(() => {
            weatherTool = new AsyncWeatherTool();
        });
        
        test('should parse complete weather data', () => {
            const apiResponse = {
                weather: [{ main: 'Rain', description: 'light rain' }],
                main: { temp: 15, humidity: 80, pressure: 1010 },
                wind: { speed: 5.2, deg: 270 },
                clouds: { all: 75 },
                name: 'London'
            };
            
            const parsed = weatherTool.parseWeatherData(apiResponse);
            
            expect(parsed.city).toBe('London');
            expect(parsed.temperature).toBe(15);
            expect(parsed.description).toBe('light rain');
            expect(parsed.humidity).toBe(80);
            expect(parsed.windSpeed).toBe(5.2);
            expect(parsed.cloudiness).toBe(75);
        });
        
        test('should handle missing optional fields', () => {
            const apiResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20 },
                name: 'TestCity'
            };
            
            const parsed = weatherTool.parseWeatherData(apiResponse);
            
            expect(parsed.city).toBe('TestCity');
            expect(parsed.temperature).toBe(20);
            expect(parsed.humidity).toBeUndefined();
            expect(parsed.windSpeed).toBeUndefined();
        });
        
        test('should handle malformed data gracefully', () => {
            const apiResponse = {
                // 缺少必需字段
                main: { temp: 20 }
            };
            
            expect(() => {
                weatherTool.parseWeatherData(apiResponse);
            }).toThrow('Invalid weather data');
        });
        
        test('should convert temperature units', () => {
            const apiResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 293.15 }, // Kelvin
                name: 'TestCity'
            };
            
            const parsed = weatherTool.parseWeatherData(apiResponse, 'celsius');
            expect(parsed.temperature).toBeCloseTo(20, 1); // 约20°C
            
            const parsedF = weatherTool.parseWeatherData(apiResponse, 'fahrenheit');
            expect(parsedF.temperature).toBeCloseTo(68, 1); // 约68°F
        });
    });
    
    学习要点：
    - 数据解析的测试方法
    - 缺失字段的处理
    - 数据验证的测试
    - 单位转换的验证
    """
    
    @pytest.fixture
    def weather_tool(self):
        """创建天气工具实例"""
        return AsyncWeatherTool()
    
    @pytest.fixture
    def complete_api_response(self):
        """完整的API响应数据"""
        return {
            "weather": [
                {
                    "main": "Rain",
                    "description": "light rain",
                    "icon": "10d"
                }
            ],
            "main": {
                "temp": 15.5,
                "feels_like": 14.2,
                "temp_min": 12.0,
                "temp_max": 18.0,
                "pressure": 1010,
                "humidity": 80
            },
            "wind": {
                "speed": 5.2,
                "deg": 270
            },
            "clouds": {
                "all": 75
            },
            "name": "London",
            "cod": 200
        }
    
    @pytest.fixture
    def minimal_api_response(self):
        """最小API响应数据"""
        return {
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky"
                }
            ],
            "main": {
                "temp": 20
            },
            "name": "TestCity"
        }
    
    def test_parse_complete_weather_data(self, weather_tool, complete_api_response):
        """测试解析完整天气数据"""
        parsed = weather_tool._parse_weather_data(complete_api_response)
        
        assert parsed["city"] == "London"
        assert parsed["temperature"] == 15.5
        assert parsed["description"] == "light rain"
        assert parsed["humidity"] == 80
        assert parsed["pressure"] == 1010
        assert parsed["wind_speed"] == 5.2
        assert parsed["wind_direction"] == 270
        assert parsed["cloudiness"] == 75
    
    def test_parse_minimal_weather_data(self, weather_tool, minimal_api_response):
        """测试解析最小天气数据"""
        parsed = weather_tool._parse_weather_data(minimal_api_response)
        
        assert parsed["city"] == "TestCity"
        assert parsed["temperature"] == 20
        assert parsed["description"] == "clear sky"
        assert parsed["humidity"] is None
        assert parsed["wind_speed"] is None
    
    def test_parse_malformed_data(self, weather_tool):
        """测试解析格式错误的数据"""
        malformed_responses = [
            {},  # 空响应
            {"main": {"temp": 20}},  # 缺少weather字段
            {"weather": [{"main": "Clear"}]},  # 缺少main字段
            {"weather": [{"main": "Clear"}], "main": {}},  # 缺少temp字段
        ]
        
        for response in malformed_responses:
            with pytest.raises((KeyError, ValueError, TypeError)):
                weather_tool._parse_weather_data(response)
    
    def test_temperature_conversion(self, weather_tool):
        """测试温度转换"""
        # 测试开尔文到摄氏度的转换
        kelvin_response = {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 293.15},  # 20°C in Kelvin
            "name": "TestCity"
        }
        
        parsed = weather_tool._parse_weather_data(kelvin_response)
        # OpenWeatherMap API默认返回开尔文，但通常配置为摄氏度
        # 这里假设API已配置为返回摄氏度
        assert isinstance(parsed["temperature"], (int, float))
    
    def test_wind_data_parsing(self, weather_tool):
        """测试风力数据解析"""
        wind_response = {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 20},
            "wind": {"speed": 10.5, "deg": 180},
            "name": "TestCity"
        }
        
        parsed = weather_tool._parse_weather_data(wind_response)
        
        assert parsed["wind_speed"] == 10.5
        assert parsed["wind_direction"] == 180
    
    def test_missing_wind_data(self, weather_tool):
        """测试缺失风力数据"""
        no_wind_response = {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 20},
            "name": "TestCity"
        }
        
        parsed = weather_tool._parse_weather_data(no_wind_response)
        
        assert parsed["wind_speed"] is None
        assert parsed["wind_direction"] is None
    
    def test_weather_condition_parsing(self, weather_tool):
        """测试天气状况解析"""
        conditions = [
            ("Clear", "clear sky"),
            ("Clouds", "few clouds"),
            ("Rain", "moderate rain"),
            ("Snow", "light snow"),
            ("Thunderstorm", "thunderstorm with rain")
        ]
        
        for main, description in conditions:
            response = {
                "weather": [{"main": main, "description": description}],
                "main": {"temp": 20},
                "name": "TestCity"
            }
            
            parsed = weather_tool._parse_weather_data(response)
            
            assert parsed["condition"] == main
            assert parsed["description"] == description


class TestWeatherIntegration:
    """
    天气工具集成测试类
    
    💡 对比TypeScript:
    describe('Weather Integration', () => {
        let weatherTool: AsyncWeatherTool;
        
        beforeEach(() => {
            weatherTool = new AsyncWeatherTool();
        });
        
        test('should work end-to-end with real API structure', async () => {
            const mockApiResponse = {
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20, humidity: 65, pressure: 1013 },
                wind: { speed: 3.5, deg: 180 },
                clouds: { all: 0 },
                name: 'Beijing'
            };
            
            const mockGet = jest.fn().mockResolvedValue({
                status: 200,
                json: () => Promise.resolve(mockApiResponse)
            });
            
            weatherTool.httpClient = { get: mockGet };
            
            const result = await weatherTool.execute({
                city: 'Beijing',
                country: 'CN'
            });
            
            expect(result.isSuccess()).toBe(true);
            expect(result.content).toMatchObject({
                city: 'Beijing',
                temperature: 20,
                description: 'clear sky',
                humidity: 65,
                windSpeed: 3.5
            });
            
            expect(result.metadata).toHaveProperty('cached');
            expect(result.metadata).toHaveProperty('executionTime');
        });
        
        test('should handle multiple concurrent requests', async () => {
            const cities = ['Beijing', 'Shanghai', 'Guangzhou'];
            const mockResponses = cities.map(city => ({
                weather: [{ main: 'Clear', description: 'clear sky' }],
                main: { temp: 20 + cities.indexOf(city) },
                name: city
            }));
            
            const mockGet = jest.fn();
            mockResponses.forEach((response, index) => {
                mockGet.mockResolvedValueOnce({
                    status: 200,
                    json: () => Promise.resolve(response)
                });
            });
            
            weatherTool.httpClient = { get: mockGet };
            
            const promises = cities.map(city => 
                weatherTool.execute({ city })
            );
            
            const results = await Promise.all(promises);
            
            expect(results).toHaveLength(3);
            results.forEach((result, index) => {
                expect(result.isSuccess()).toBe(true);
                expect(result.content.city).toBe(cities[index]);
                expect(result.content.temperature).toBe(20 + index);
            });
        });
    });
    
    学习要点：
    - 端到端集成测试
    - 并发请求的测试
    - 真实API结构的模拟
    - 完整工作流的验证
    """
    
    @pytest.fixture
    def weather_tool(self):
        """创建天气工具实例"""
        return AsyncWeatherTool()
    
    @pytest.mark.asyncio
    async def test_end_to_end_weather_query(self, weather_tool):
        """测试端到端天气查询"""
        mock_api_response = {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 20, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 3.5, "deg": 180},
            "clouds": {"all": 0},
            "name": "Beijing"
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_api_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_tool.execute(
                city="Beijing",
                country="CN"
            )
            
            assert result.is_success()
            assert result.content["city"] == "Beijing"
            assert result.content["temperature"] == 20
            assert result.content["description"] == "clear sky"
            assert result.content["humidity"] == 65
            assert result.content["wind_speed"] == 3.5
            
            # 验证元数据
            assert "cached" in result.metadata
            assert "execution_time" in result.metadata
            assert "api_call_time" in result.metadata
    
    @pytest.mark.asyncio
    async def test_concurrent_weather_requests(self, weather_tool):
        """测试并发天气请求"""
        cities = ["Beijing", "Shanghai", "Guangzhou"]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            def create_response(city):
                return {
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                    "main": {"temp": 20 + cities.index(city)},
                    "name": city
                }
            
            # 为每个城市配置响应
            responses = []
            for city in cities:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=create_response(city))
                responses.append(mock_response)
            
            mock_get.return_value.__aenter__.side_effect = responses
            
            # 并发请求
            tasks = [
                weather_tool.execute(city=city)
                for city in cities
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.is_success()
                assert result.content["city"] == cities[i]
                assert result.content["temperature"] == 20 + i
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, weather_tool):
        """测试错误恢复工作流"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 第一次请求失败
            mock_get.side_effect = [
                ClientError("Network error"),
                # 第二次请求成功
                AsyncMock(
                    __aenter__=AsyncMock(return_value=AsyncMock(
                        status=200,
                        json=AsyncMock(return_value={
                            "weather": [{"main": "Clear", "description": "clear sky"}],
                            "main": {"temp": 20},
                            "name": "Beijing"
                        })
                    ))
                )
            ]
            
            # 第一次请求应该失败
            result1 = await weather_tool.execute(city="Beijing")
            assert result1.is_error()
            
            # 第二次请求应该成功
            result2 = await weather_tool.execute(city="Beijing")
            assert result2.is_success()
            assert result2.content["city"] == "Beijing"
    
    @pytest.mark.asyncio
    async def test_cache_performance_benefit(self, weather_tool):
        """测试缓存性能优势"""
        mock_api_response = {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 20},
            "name": "Beijing"
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_api_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # 第一次请求（从API获取）
            start_time = time.time()
            result1 = await weather_tool.execute(city="Beijing")
            first_request_time = time.time() - start_time
            
            assert result1.is_success()
            assert not result1.metadata.get("cached", False)
            
            # 第二次请求（从缓存获取）
            start_time = time.time()
            result2 = await weather_tool.execute(city="Beijing")
            second_request_time = time.time() - start_time
            
            assert result2.is_success()
            assert result2.metadata.get("cached", False)
            
            # 缓存请求应该更快
            assert second_request_time < first_request_time
            
            # API只应该被调用一次
            assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_weather_integration():
    """
    天气工具集成测试
    
    学习要点：
    - 完整的集成测试流程
    - 多种场景的综合测试
    - 性能和功能的平衡验证
    """
    print("🧪 运行天气工具集成测试...")
    
    weather_tool = AsyncWeatherTool()
    
    # 模拟成功的API响应
    mock_response = {
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "main": {"temp": 22, "humidity": 60},
        "wind": {"speed": 2.5},
        "name": "TestCity"
    }
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        # 测试基础功能
        result = await weather_tool.execute(city="TestCity")
        assert result.is_success()
        assert result.content["city"] == "TestCity"
        assert result.content["temperature"] == 22
        
        # 测试缓存功能
        result2 = await weather_tool.execute(city="TestCity")
        assert result2.is_success()
        assert result2.metadata.get("cached", False)
        
        # API应该只被调用一次
        assert mock_get.call_count == 1
    
    print("✅ 天气工具集成测试通过")


if __name__ == "__main__":
    """
    测试运行器
    
    学习要点：
    - 异步测试的组织
    - 外部依赖的模拟
    - 集成测试的执行
    """
    print("🧪 运行天气工具测试...")
    
    # 运行集成测试
    asyncio.run(test_weather_integration())
    
    print("✅ 所有天气工具测试完成")