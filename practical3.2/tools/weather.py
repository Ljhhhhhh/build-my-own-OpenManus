"""
异步天气查询工具 - 高级版本

这个模块实现了一个异步的天气查询工具，支持通过城市名查询当前天气信息。
相比practical3.1，这里引入了真实的外部API调用、异步HTTP请求、缓存机制等高级特性。

学习要点：
1. 异步HTTP客户端的使用 (aiohttp)
2. 外部API的集成和调用
3. 环境变量和配置管理
4. 缓存机制的实现
5. 网络错误处理和重试
6. 数据解析和格式化
7. 速率限制和API配额管理
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from urllib.parse import urlencode

from .base import AsyncBaseTool, ToolResult, tool_timer
from config import Config


class AsyncWeatherTool(AsyncBaseTool):
    """
    异步天气查询工具
    
    💡 对比TypeScript:
    class AsyncWeatherTool extends AsyncBaseTool {
        private apiKey: string;
        private baseUrl: string;
        private cache: Map<string, CacheEntry>;
        private httpClient: AxiosInstance;
        
        constructor() {
            super("async_weather", "异步天气查询工具", 30.0, 3);
            
            this.apiKey = process.env.OPENWEATHER_API_KEY || '';
            this.baseUrl = 'https://api.openweathermap.org/data/2.5';
            this.cache = new Map();
            
            this.httpClient = axios.create({
                timeout: 10000,
                headers: {
                    'User-Agent': 'AsyncWeatherTool/1.0'
                }
            });
        }
        
        get schema(): object {
            return {
                type: "object",
                properties: {
                    city: {
                        type: "string",
                        minLength: 1,
                        maxLength: 100,
                        description: "城市名称（支持中英文）"
                    },
                    country: {
                        type: "string",
                        pattern: "^[A-Z]{2}$",
                        description: "国家代码（ISO 3166-1 alpha-2）"
                    },
                    units: {
                        type: "string",
                        enum: ["metric", "imperial", "kelvin"],
                        default: "metric",
                        description: "温度单位"
                    },
                    lang: {
                        type: "string",
                        enum: ["zh_cn", "en", "ja", "ko"],
                        default: "zh_cn",
                        description: "返回语言"
                    },
                    use_cache: {
                        type: "boolean",
                        default: true,
                        description: "是否使用缓存"
                    }
                },
                required: ["city"]
            };
        }
        
        async validateInput(params: any): Promise<boolean | string> {
            // 验证逻辑
        }
        
        async execute(params: any): Promise<ToolResult> {
            // 执行逻辑
        }
    }
    
    学习要点：
    - 外部API集成的完整实现
    - 异步HTTP请求的处理
    - 缓存机制的设计和实现
    - 配置管理的最佳实践
    - 错误处理和重试机制
    """
    
    def __init__(self):
        """
        初始化异步天气查询工具
        
        学习要点：
        - 外部依赖的初始化
        - 配置的加载和验证
        - 缓存系统的设置
        - HTTP客户端的配置
        """
        super().__init__(
            name="async_weather",
            description="异步天气查询工具，支持查询全球城市的当前天气信息",
            timeout=30.0,
            max_retries=3
        )
        
        # 加载配置
        self.config = Config()
        self.api_key = self.config.get('OPENWEATHER_API_KEY', '')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        
        # 缓存设置
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=10)  # 缓存10分钟
        
        # HTTP客户端设置
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_timeout = aiohttp.ClientTimeout(total=10)
        
        # API配额管理
        self.request_count = 0
        self.last_request_time = datetime.now()
        self.rate_limit_per_minute = 60  # OpenWeather免费版限制
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回天气工具的JSON Schema
        
        学习要点：
        - 复杂Schema的设计
        - 字符串模式验证
        - 枚举值的定义
        - 国际化支持的考虑
        
        Returns:
            Dict[str, Any]: JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "城市名称（支持中英文，如：北京、Beijing、New York）"
                },
                "country": {
                    "type": "string",
                    "pattern": "^[A-Z]{2}$",
                    "description": "国家代码（可选，ISO 3166-1 alpha-2格式，如：CN、US、JP）"
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial", "kelvin"],
                    "default": "metric",
                    "description": "温度单位（metric=摄氏度，imperial=华氏度，kelvin=开尔文）"
                },
                "lang": {
                    "type": "string",
                    "enum": ["zh_cn", "en", "ja", "ko", "fr", "de", "es", "ru"],
                    "default": "zh_cn",
                    "description": "返回语言（zh_cn=中文，en=英文）"
                },
                "use_cache": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否使用缓存（提高响应速度，减少API调用）"
                },
                "include_forecast": {
                    "type": "boolean",
                    "default": False,
                    "description": "是否包含未来几小时的天气预报"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        }
    
    async def validate_input(self, **kwargs) -> Union[bool, str]:
        """
        异步输入验证
        
        💡 对比TypeScript:
        async validateInput(params: any): Promise<boolean | string> {
            // API密钥验证
            if (!this.apiKey) {
                return "未配置OpenWeather API密钥，请设置OPENWEATHER_API_KEY环境变量";
            }
            
            // 城市名验证
            const { city, country, units, lang } = params;
            
            if (!city || typeof city !== 'string') {
                return "城市名称不能为空且必须是字符串";
            }
            
            if (city.trim().length === 0) {
                return "城市名称不能为空白字符";
            }
            
            if (city.length > 100) {
                return "城市名称长度不能超过100个字符";
            }
            
            // 国家代码验证
            if (country && (typeof country !== 'string' || !/^[A-Z]{2}$/.test(country))) {
                return "国家代码必须是2位大写字母（ISO 3166-1 alpha-2格式）";
            }
            
            // 单位验证
            if (units && !['metric', 'imperial', 'kelvin'].includes(units)) {
                return "温度单位必须是 metric、imperial 或 kelvin 之一";
            }
            
            // 语言验证
            const supportedLangs = ['zh_cn', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru'];
            if (lang && !supportedLangs.includes(lang)) {
                return `语言代码必须是以下之一: ${supportedLangs.join(', ')}`;
            }
            
            // 速率限制检查
            return await this.checkRateLimit();
        }
        
        学习要点：
        - API密钥的验证
        - 字符串格式的验证
        - 正则表达式的使用
        - 速率限制的检查
        - 详细错误信息的提供
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            Union[bool, str]: 验证结果
        """
        # API密钥验证
        if not self.api_key:
            return ("未配置OpenWeather API密钥。请在.env文件中设置OPENWEATHER_API_KEY，"
                   "或访问 https://openweathermap.org/api 获取免费API密钥")
        
        # 基础参数验证
        city = kwargs.get('city')
        if not city:
            return "城市名称不能为空"
        
        if not isinstance(city, str):
            return "城市名称必须是字符串"
        
        city = city.strip()
        if not city:
            return "城市名称不能为空白字符"
        
        if len(city) > 100:
            return "城市名称长度不能超过100个字符"
        
        # 国家代码验证
        country = kwargs.get('country')
        if country:
            if not isinstance(country, str):
                return "国家代码必须是字符串"
            
            import re
            if not re.match(r'^[A-Z]{2}$', country):
                return "国家代码必须是2位大写字母（如：CN、US、JP）"
        
        # 温度单位验证
        units = kwargs.get('units', 'metric')
        if units not in ['metric', 'imperial', 'kelvin']:
            return "温度单位必须是 metric（摄氏度）、imperial（华氏度）或 kelvin（开尔文）之一"
        
        # 语言验证
        lang = kwargs.get('lang', 'zh_cn')
        supported_langs = ['zh_cn', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru']
        if lang not in supported_langs:
            return f"语言代码必须是以下之一: {', '.join(supported_langs)}"
        
        # 速率限制检查
        rate_limit_check = await self._check_rate_limit()
        if rate_limit_check is not True:
            return rate_limit_check
        
        return True
    
    @tool_timer
    async def execute(self, **kwargs) -> ToolResult:
        """
        异步执行天气查询
        
        💡 对比TypeScript:
        @toolTimer
        async execute(params: any): Promise<ToolResult> {
            try {
                const { city, country, units = 'metric', lang = 'zh_cn', use_cache = true, include_forecast = false } = params;
                
                // 构建缓存键
                const cacheKey = this.buildCacheKey(city, country, units, lang);
                
                // 检查缓存
                if (use_cache) {
                    const cachedResult = this.getFromCache(cacheKey);
                    if (cachedResult) {
                        return ToolResult.success(cachedResult.data, {
                            ...cachedResult.metadata,
                            from_cache: true,
                            cache_age: Date.now() - cachedResult.timestamp
                        });
                    }
                }
                
                // 确保HTTP客户端已初始化
                await this.ensureHttpClient();
                
                // 构建API请求
                const weatherData = await this.fetchWeatherData(city, country, units, lang);
                
                // 获取预报数据（如果需要）
                let forecastData = null;
                if (include_forecast) {
                    forecastData = await this.fetchForecastData(city, country, units, lang);
                }
                
                // 格式化结果
                const formattedResult = this.formatWeatherData(weatherData, forecastData, units);
                
                // 更新缓存
                if (use_cache) {
                    this.updateCache(cacheKey, formattedResult, weatherData);
                }
                
                // 构建元数据
                const metadata = {
                    city,
                    country,
                    units,
                    lang,
                    api_source: 'OpenWeatherMap',
                    request_time: new Date().toISOString(),
                    from_cache: false,
                    include_forecast
                };
                
                return ToolResult.success(formattedResult, metadata);
                
            } catch (error) {
                return this.handleError(error);
            }
        }
        
        学习要点：
        - 异步HTTP请求的完整流程
        - 缓存机制的实现和使用
        - 外部API的调用和数据处理
        - 错误处理的完整性
        - 元数据的构建和管理
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            ToolResult: 执行结果
        """
        try:
            city = kwargs['city'].strip()
            country = kwargs.get('country')
            units = kwargs.get('units', 'metric')
            lang = kwargs.get('lang', 'zh_cn')
            use_cache = kwargs.get('use_cache', True)
            include_forecast = kwargs.get('include_forecast', False)
            
            # 构建缓存键
            cache_key = self._build_cache_key(city, country, units, lang)
            
            # 检查缓存
            if use_cache:
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    return ToolResult.success(
                        content=cached_result['data'],
                        metadata={
                            **cached_result['metadata'],
                            'from_cache': True,
                            'cache_age_seconds': (datetime.now() - cached_result['timestamp']).total_seconds()
                        }
                    )
            
            # 确保HTTP客户端已初始化
            await self._ensure_http_client()
            
            # 获取天气数据
            weather_data = await self._fetch_weather_data(city, country, units, lang)
            
            # 获取预报数据（如果需要）
            forecast_data = None
            if include_forecast:
                try:
                    forecast_data = await self._fetch_forecast_data(city, country, units, lang)
                except Exception as e:
                    # 预报数据获取失败不影响主要功能
                    print(f"警告：获取预报数据失败: {e}")
            
            # 格式化结果
            formatted_result = self._format_weather_data(weather_data, forecast_data, units)
            
            # 更新缓存
            if use_cache:
                self._update_cache(cache_key, formatted_result, weather_data)
            
            # 构建元数据
            metadata = {
                'city': city,
                'country': country,
                'units': units,
                'lang': lang,
                'api_source': 'OpenWeatherMap',
                'request_time': datetime.now().isoformat(),
                'from_cache': False,
                'include_forecast': include_forecast,
                'api_calls_used': 1 + (1 if include_forecast else 0)
            }
            
            return ToolResult.success(
                content=formatted_result,
                metadata=metadata
            )
            
        except aiohttp.ClientTimeout:
            return ToolResult.error("网络请求超时，请检查网络连接或稍后重试")
        
        except aiohttp.ClientError as e:
            return ToolResult.error(f"网络请求失败: {str(e)}")
        
        except json.JSONDecodeError:
            return ToolResult.error("API返回数据格式错误，无法解析JSON")
        
        except KeyError as e:
            return ToolResult.error(f"API返回数据缺少必要字段: {str(e)}")
        
        except Exception as e:
            return ToolResult.error(f"天气查询异常: {str(e)}")
    
    async def _ensure_http_client(self):
        """
        确保HTTP客户端已初始化
        
        学习要点：
        - 异步资源的延迟初始化
        - HTTP客户端的配置
        - 连接池的管理
        """
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=10,  # 连接池大小
                limit_per_host=5,  # 每个主机的连接数
                ttl_dns_cache=300,  # DNS缓存时间
                use_dns_cache=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.request_timeout,
                headers={
                    'User-Agent': 'AsyncWeatherTool/1.0',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
            )
    
    async def _fetch_weather_data(self, city: str, country: Optional[str], 
                                units: str, lang: str) -> Dict[str, Any]:
        """
        获取天气数据
        
        学习要点：
        - 异步HTTP请求的实现
        - URL参数的构建
        - API响应的处理
        - 错误状态码的处理
        
        Args:
            city: 城市名称
            country: 国家代码
            units: 温度单位
            lang: 语言
            
        Returns:
            Dict[str, Any]: 天气数据
        """
        # 构建查询参数
        query_params = {
            'q': f"{city},{country}" if country else city,
            'appid': self.api_key,
            'units': units,
            'lang': lang
        }
        
        url = f"{self.base_url}/weather?{urlencode(query_params)}"
        
        # 发送请求
        async with self.session.get(url) as response:
            # 更新请求计数
            self.request_count += 1
            self.last_request_time = datetime.now()
            
            # 检查响应状态
            if response.status == 200:
                return await response.json()
            elif response.status == 401:
                raise Exception("API密钥无效，请检查OPENWEATHER_API_KEY配置")
            elif response.status == 404:
                raise Exception(f"未找到城市 '{city}' 的天气信息，请检查城市名称拼写")
            elif response.status == 429:
                raise Exception("API调用频率超限，请稍后重试")
            else:
                error_text = await response.text()
                raise Exception(f"API请求失败 (状态码: {response.status}): {error_text}")
    
    async def _fetch_forecast_data(self, city: str, country: Optional[str], 
                                 units: str, lang: str) -> Dict[str, Any]:
        """
        获取预报数据
        
        学习要点：
        - 多个API端点的调用
        - 数据的组合和处理
        - 可选功能的实现
        
        Args:
            city: 城市名称
            country: 国家代码
            units: 温度单位
            lang: 语言
            
        Returns:
            Dict[str, Any]: 预报数据
        """
        query_params = {
            'q': f"{city},{country}" if country else city,
            'appid': self.api_key,
            'units': units,
            'lang': lang,
            'cnt': 8  # 未来24小时（每3小时一个数据点）
        }
        
        url = f"{self.base_url}/forecast?{urlencode(query_params)}"
        
        async with self.session.get(url) as response:
            self.request_count += 1
            
            if response.status == 200:
                return await response.json()
            else:
                # 预报数据获取失败不抛出异常，返回None
                return None
    
    def _format_weather_data(self, weather_data: Dict[str, Any], 
                           forecast_data: Optional[Dict[str, Any]], 
                           units: str) -> str:
        """
        格式化天气数据
        
        学习要点：
        - 数据的解析和提取
        - 字符串格式化技巧
        - 国际化的处理
        - 可选数据的处理
        
        Args:
            weather_data: 当前天气数据
            forecast_data: 预报数据
            units: 温度单位
            
        Returns:
            str: 格式化后的天气信息
        """
        try:
            # 提取基本信息
            city_name = weather_data['name']
            country = weather_data['sys']['country']
            
            # 提取天气信息
            main = weather_data['main']
            weather = weather_data['weather'][0]
            wind = weather_data.get('wind', {})
            clouds = weather_data.get('clouds', {})
            
            # 温度单位符号
            temp_unit = {
                'metric': '°C',
                'imperial': '°F',
                'kelvin': 'K'
            }.get(units, '°C')
            
            # 风速单位
            wind_unit = 'km/h' if units == 'metric' else 'mph'
            
            # 构建基本天气信息
            result = f"🌍 {city_name}, {country} 当前天气\n"
            result += "=" * 30 + "\n\n"
            
            result += f"🌡️  温度: {main['temp']:.1f}{temp_unit}\n"
            result += f"🤔  体感温度: {main['feels_like']:.1f}{temp_unit}\n"
            result += f"📊  温度范围: {main['temp_min']:.1f}{temp_unit} ~ {main['temp_max']:.1f}{temp_unit}\n"
            
            result += f"☁️  天气: {weather['description']}\n"
            result += f"💧  湿度: {main['humidity']}%\n"
            result += f"🌪️  气压: {main['pressure']} hPa\n"
            
            if 'speed' in wind:
                result += f"💨  风速: {wind['speed']:.1f} {wind_unit}"
                if 'deg' in wind:
                    direction = self._get_wind_direction(wind['deg'])
                    result += f" ({direction})"
                result += "\n"
            
            if 'all' in clouds:
                result += f"☁️  云量: {clouds['all']}%\n"
            
            # 添加能见度信息
            if 'visibility' in weather_data:
                visibility_km = weather_data['visibility'] / 1000
                result += f"👁️  能见度: {visibility_km:.1f} km\n"
            
            # 添加日出日落信息
            if 'sunrise' in weather_data['sys'] and 'sunset' in weather_data['sys']:
                sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
                sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
                result += f"🌅  日出: {sunrise.strftime('%H:%M')}\n"
                result += f"🌇  日落: {sunset.strftime('%H:%M')}\n"
            
            # 添加预报信息
            if forecast_data and 'list' in forecast_data:
                result += "\n📅 未来24小时预报\n"
                result += "-" * 20 + "\n"
                
                for i, forecast in enumerate(forecast_data['list'][:8]):
                    time = datetime.fromtimestamp(forecast['dt'])
                    temp = forecast['main']['temp']
                    desc = forecast['weather'][0]['description']
                    result += f"{time.strftime('%H:%M')} | {temp:.1f}{temp_unit} | {desc}\n"
            
            # 添加数据更新时间
            update_time = datetime.fromtimestamp(weather_data['dt'])
            result += f"\n⏰ 数据更新时间: {update_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except KeyError as e:
            raise Exception(f"天气数据格式错误，缺少字段: {e}")
        except Exception as e:
            raise Exception(f"格式化天气数据失败: {e}")
    
    def _get_wind_direction(self, degrees: float) -> str:
        """
        根据角度获取风向
        
        学习要点：
        - 数值范围的映射
        - 条件判断的优化
        - 国际化字符串的处理
        
        Args:
            degrees: 风向角度
            
        Returns:
            str: 风向描述
        """
        directions = [
            "北", "北北东", "东北", "东北东",
            "东", "东南东", "东南", "南南东",
            "南", "南南西", "西南", "西南西",
            "西", "西北西", "西北", "北北西"
        ]
        
        index = int((degrees + 11.25) / 22.5) % 16
        return directions[index]
    
    async def _check_rate_limit(self) -> Union[bool, str]:
        """
        检查API调用速率限制
        
        学习要点：
        - 速率限制的实现
        - 时间窗口的计算
        - 异步等待的使用
        
        Returns:
            Union[bool, str]: 检查结果
        """
        now = datetime.now()
        time_diff = (now - self.last_request_time).total_seconds()
        
        # 如果距离上次请求超过1分钟，重置计数
        if time_diff > 60:
            self.request_count = 0
            self.last_request_time = now
        
        # 检查是否超过速率限制
        if self.request_count >= self.rate_limit_per_minute:
            wait_time = 60 - time_diff
            return f"API调用频率超限，请等待 {wait_time:.0f} 秒后重试"
        
        return True
    
    def _build_cache_key(self, city: str, country: Optional[str], 
                        units: str, lang: str) -> str:
        """
        构建缓存键
        
        学习要点：
        - 缓存键的设计原则
        - 字符串的标准化处理
        - 哈希值的使用
        
        Args:
            city: 城市名称
            country: 国家代码
            units: 温度单位
            lang: 语言
            
        Returns:
            str: 缓存键
        """
        key_parts = [
            city.lower().strip(),
            country.upper() if country else '',
            units,
            lang
        ]
        return '|'.join(key_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取数据
        
        学习要点：
        - 缓存的读取和验证
        - 过期时间的检查
        - 缓存命中率的优化
        
        Args:
            cache_key: 缓存键
            
        Returns:
            Optional[Dict[str, Any]]: 缓存数据
        """
        if cache_key not in self.cache:
            return None
        
        cache_entry = self.cache[cache_key]
        
        # 检查是否过期
        if datetime.now() - cache_entry['timestamp'] > self.cache_ttl:
            del self.cache[cache_key]
            return None
        
        return cache_entry
    
    def _update_cache(self, cache_key: str, formatted_result: str, 
                     raw_data: Dict[str, Any]):
        """
        更新缓存
        
        学习要点：
        - 缓存的写入和更新
        - 缓存大小的控制
        - 内存使用的优化
        
        Args:
            cache_key: 缓存键
            formatted_result: 格式化结果
            raw_data: 原始数据
        """
        # 限制缓存大小
        if len(self.cache) > 100:
            # 删除最旧的缓存项
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'data': formatted_result,
            'timestamp': datetime.now(),
            'metadata': {
                'city': raw_data['name'],
                'country': raw_data['sys']['country'],
                'coordinates': raw_data['coord']
            }
        }
    
    async def cleanup(self):
        """
        清理资源
        
        学习要点：
        - 异步资源的清理
        - 连接池的关闭
        - 内存的释放
        """
        if self.session and not self.session.closed:
            await self.session.close()
        
        self.cache.clear()


# 测试代码
if __name__ == "__main__":
    """
    测试异步天气查询工具
    
    学习要点：
    - 异步工具的测试方法
    - 外部API的模拟测试
    - 错误情况的测试
    - 缓存机制的测试
    """
    
    async def test_async_weather():
        """测试异步天气工具"""
        print("🌤️ 测试异步天气查询工具")
        print("=" * 40)
        
        weather_tool = AsyncWeatherTool()
        
        # 检查API密钥配置
        if not weather_tool.api_key:
            print("⚠️  警告：未配置OpenWeather API密钥")
            print("请在.env文件中设置OPENWEATHER_API_KEY")
            print("或访问 https://openweathermap.org/api 获取免费API密钥")
            return
        
        try:
            # 测试用例
            test_cases = [
                {
                    "name": "北京天气查询",
                    "params": {"city": "Beijing", "country": "CN", "lang": "zh_cn"}
                },
                {
                    "name": "纽约天气查询",
                    "params": {"city": "New York", "country": "US", "units": "imperial", "lang": "en"}
                },
                {
                    "name": "东京天气查询（含预报）",
                    "params": {"city": "Tokyo", "country": "JP", "include_forecast": True}
                },
                {
                    "name": "上海天气查询（使用缓存）",
                    "params": {"city": "Shanghai", "use_cache": True}
                }
            ]
            
            print("\n1. 测试天气查询:")
            for i, test_case in enumerate(test_cases):
                print(f"\n{i+1}. {test_case['name']}")
                print("-" * 30)
                
                result = await weather_tool.execute_with_timeout(**test_case['params'])
                
                if result.is_success():
                    print("✅ 查询成功")
                    print(result.content[:200] + "..." if len(result.content) > 200 else result.content)
                    
                    # 显示元数据
                    if result.metadata:
                        print(f"\n📊 元数据:")
                        for key, value in result.metadata.items():
                            print(f"  {key}: {value}")
                else:
                    print(f"❌ 查询失败: {result.error_message}")
                
                # 添加延迟避免速率限制
                await asyncio.sleep(1)
            
            # 测试缓存功能
            print("\n\n2. 测试缓存功能:")
            print("-" * 30)
            
            # 第一次查询
            start_time = datetime.now()
            result1 = await weather_tool.execute_with_timeout(city="Beijing", use_cache=True)
            time1 = (datetime.now() - start_time).total_seconds()
            
            # 第二次查询（应该使用缓存）
            start_time = datetime.now()
            result2 = await weather_tool.execute_with_timeout(city="Beijing", use_cache=True)
            time2 = (datetime.now() - start_time).total_seconds()
            
            print(f"第一次查询耗时: {time1:.2f}秒")
            print(f"第二次查询耗时: {time2:.2f}秒")
            
            if result2.metadata and result2.metadata.get('from_cache'):
                print("✅ 缓存功能正常工作")
            else:
                print("⚠️  缓存功能可能未生效")
            
            # 测试输入验证
            print("\n\n3. 测试输入验证:")
            print("-" * 30)
            
            validation_cases = [
                {"city": ""},  # 空城市名
                {"city": "Beijing", "country": "invalid"},  # 无效国家代码
                {"city": "Beijing", "units": "invalid"},  # 无效单位
                {"city": "Beijing", "lang": "invalid"}  # 无效语言
            ]
            
            for i, case in enumerate(validation_cases):
                validation_result = await weather_tool.validate_input(**case)
                status = "✅" if validation_result is not True else "❌"
                print(f"  {status} 验证案例 {i+1}: {validation_result}")
            
            # 显示工具统计
            print("\n\n4. 工具统计:")
            print("-" * 30)
            stats = weather_tool.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            print(f"  API调用次数: {weather_tool.request_count}")
            print(f"  缓存项数量: {len(weather_tool.cache)}")
            
        finally:
            # 清理资源
            await weather_tool.cleanup()
        
        print("\n✅ 异步天气查询工具测试完成！")
    
    # 运行测试
    asyncio.run(test_async_weather())