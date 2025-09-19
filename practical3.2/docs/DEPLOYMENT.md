# 部署指南

## 📋 概述

本指南详细介绍了如何在不同环境中部署Practical 3.2异步工具框架，包括开发环境、测试环境和生产环境的配置和最佳实践。

## 🏗️ 系统要求

### 最低要求
- **Python**: 3.8+
- **内存**: 512MB RAM
- **存储**: 100MB 可用空间
- **网络**: 互联网连接（用于API调用）

### 推荐配置
- **Python**: 3.11+
- **内存**: 2GB+ RAM
- **存储**: 1GB+ 可用空间
- **CPU**: 2+ 核心
- **网络**: 稳定的互联网连接

### 支持的操作系统
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+
- CentOS 7+
- Docker容器环境

## 🚀 快速部署

### 1. 本地开发环境

#### Windows环境
```powershell
# 克隆项目
git clone <repository-url>
cd practical3.2

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，设置必要的配置

# 运行测试
pytest

# 启动应用
python main.py
```

#### Linux/macOS环境
```bash
# 克隆项目
git clone <repository-url>
cd practical3.2

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行测试
pytest

# 启动应用
python main.py
```

### 2. Docker部署

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口（如果有Web服务）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; asyncio.run(__import__('main').health_check())" || exit 1

# 启动命令
CMD ["python", "main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  async-tools:
    build: .
    container_name: practical3.2-app
    environment:
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - LOG_LEVEL=INFO
      - MAX_CONCURRENT=10
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    ports:
      - "8000:8000"
    restart: unless-stopped
    networks:
      - app-network
    depends_on:
      - redis
    
  redis:
    image: redis:7-alpine
    container_name: practical3.2-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network

volumes:
  redis_data:

networks:
  app-network:
    driver: bridge
```

#### 构建和运行
```bash
# 构建镜像
docker build -t practical3.2:latest .

# 使用docker-compose运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🔧 环境配置

### 1. 环境变量配置

#### 开发环境 (.env.development)
```bash
# API配置
OPENWEATHER_API_KEY=your_development_api_key
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# 应用配置
LOG_LEVEL=DEBUG
MAX_CONCURRENT=5
CACHE_TTL=300

# 调试配置
DEBUG=true
ENABLE_PROFILING=true
```

#### 测试环境 (.env.testing)
```bash
# API配置
OPENWEATHER_API_KEY=test_api_key
REQUEST_TIMEOUT=10
MAX_RETRIES=1

# 应用配置
LOG_LEVEL=WARNING
MAX_CONCURRENT=3
CACHE_TTL=60

# 测试配置
TESTING=true
MOCK_EXTERNAL_APIS=true
```

#### 生产环境 (.env.production)
```bash
# API配置
OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
REQUEST_TIMEOUT=30
MAX_RETRIES=5

# 应用配置
LOG_LEVEL=INFO
MAX_CONCURRENT=20
CACHE_TTL=600

# 生产配置
DEBUG=false
ENABLE_METRICS=true
SENTRY_DSN=${SENTRY_DSN}
```

### 2. 配置管理脚本

#### config_manager.py
```python
import os
import shutil
from pathlib import Path

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.env_files = {
            'development': '.env.development',
            'testing': '.env.testing',
            'production': '.env.production'
        }
    
    def set_environment(self, env: str):
        """设置环境配置"""
        if env not in self.env_files:
            raise ValueError(f"未知环境: {env}")
        
        source_file = self.project_root / self.env_files[env]
        target_file = self.project_root / '.env'
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"已切换到 {env} 环境")
        else:
            raise FileNotFoundError(f"环境配置文件不存在: {source_file}")
    
    def validate_config(self):
        """验证配置完整性"""
        required_vars = [
            'OPENWEATHER_API_KEY',
            'LOG_LEVEL',
            'MAX_CONCURRENT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"缺少必需的环境变量: {missing_vars}")
        
        print("配置验证通过")

# 使用示例
if __name__ == "__main__":
    import sys
    
    config_manager = ConfigManager(Path(__file__).parent)
    
    if len(sys.argv) > 1:
        env = sys.argv[1]
        config_manager.set_environment(env)
        config_manager.validate_config()
    else:
        print("用法: python config_manager.py <environment>")
        print("可用环境: development, testing, production")
```

## 🌐 Web服务部署

### 1. FastAPI集成

#### web_server.py
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uvicorn

from tools.manager import AsyncToolManager
from tools.calculator import AsyncCalculatorTool
from tools.weather import AsyncWeatherTool
from config import Config

app = FastAPI(
    title="Async Tools API",
    description="异步工具框架Web API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局工具管理器
tool_manager: Optional[AsyncToolManager] = None

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    data: Any = None
    message: str = ""
    execution_time: Optional[float] = None

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global tool_manager
    
    config = Config.get_instance()
    tool_manager = AsyncToolManager(max_concurrent=config.get("max_concurrent", 10))
    
    # 注册工具
    calculator = AsyncCalculatorTool()
    await tool_manager.register_tool(calculator)
    
    if config.get("openweather_api_key"):
        weather = AsyncWeatherTool(
            api_key=config.get("openweather_api_key"),
            cache_ttl=config.get("cache_ttl", 300)
        )
        await tool_manager.register_tool(weather)
    
    print("工具管理器初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global tool_manager
    if tool_manager:
        # 清理资源
        print("清理工具管理器资源")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Async Tools API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

@app.get("/tools")
async def list_tools():
    """获取可用工具列表"""
    if not tool_manager:
        raise HTTPException(status_code=500, detail="工具管理器未初始化")
    
    tools = tool_manager.get_registered_tools()
    return {"tools": tools}

@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """执行工具"""
    if not tool_manager:
        raise HTTPException(status_code=500, detail="工具管理器未初始化")
    
    try:
        result = await tool_manager.execute_tool(
            request.tool_name, 
            **request.parameters
        )
        
        return ToolResponse(
            success=result.success,
            data=result.data,
            message=result.message,
            execution_time=result.execution_time
        )
    
    except KeyError:
        raise HTTPException(status_code=404, detail=f"工具不存在: {request.tool_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch")
async def execute_batch(requests: list[ToolRequest]):
    """批量执行工具"""
    if not tool_manager:
        raise HTTPException(status_code=500, detail="工具管理器未初始化")
    
    tasks = [
        {"tool_name": req.tool_name, **req.parameters}
        for req in requests
    ]
    
    try:
        results = await tool_manager.execute_batch(tasks)
        
        return [
            ToolResponse(
                success=result.success,
                data=result.data,
                message=result.message,
                execution_time=result.execution_time
            )
            for result in results
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    config = Config.get_instance()
    
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=config.get("debug", False),
        log_level=config.get("log_level", "info").lower()
    )
```

### 2. Nginx配置

#### nginx.conf
```nginx
upstream async_tools_backend {
    server 127.0.0.1:8000;
    # 如果有多个实例，可以添加更多服务器
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 日志配置
    access_log /var/log/nginx/async_tools_access.log;
    error_log /var/log/nginx/async_tools_error.log;
    
    # 限制请求大小
    client_max_body_size 10M;
    
    # 代理配置
    location / {
        proxy_pass http://async_tools_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 静态文件缓存
    location /static/ {
        alias /path/to/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health {
        proxy_pass http://async_tools_backend/health;
        access_log off;
    }
}
```

## 📊 监控和日志

### 1. 日志配置

#### logging_config.py
```python
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any

def setup_production_logging(
    log_dir: Path = Path("logs"),
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> Dict[str, logging.Logger]:
    """设置生产环境日志"""
    
    # 创建日志目录
    log_dir.mkdir(exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
        '[%(filename)s:%(lineno)d]'
    )
    
    loggers = {}
    
    # 应用日志
    app_logger = logging.getLogger("async_tools")
    app_logger.setLevel(getattr(logging, log_level.upper()))
    
    app_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)
    
    # 错误日志
    error_logger = logging.getLogger("async_tools.error")
    error_logger.setLevel(logging.ERROR)
    
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)
    
    # 性能日志
    perf_logger = logging.getLogger("async_tools.performance")
    perf_logger.setLevel(logging.INFO)
    
    perf_handler = logging.handlers.RotatingFileHandler(
        log_dir / "performance.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    perf_handler.setFormatter(formatter)
    perf_logger.addHandler(perf_handler)
    
    # 控制台输出（可选）
    if os.getenv("LOG_TO_CONSOLE", "false").lower() == "true":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        app_logger.addHandler(console_handler)
    
    loggers.update({
        "app": app_logger,
        "error": error_logger,
        "performance": perf_logger
    })
    
    return loggers
```

### 2. 指标收集

#### metrics.py
```python
import time
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """递增计数器"""
        key = self._make_key(name, tags)
        self._counters[key] += value
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """设置仪表值"""
        key = self._make_key(name, tags)
        self._gauges[key] = value
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """记录直方图数据"""
        key = self._make_key(name, tags)
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            tags=tags or {}
        )
        self._metrics[key].append(point)
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """生成指标键"""
        if not tags:
            return name
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                name: [
                    {
                        "timestamp": point.timestamp,
                        "value": point.value,
                        "tags": point.tags
                    }
                    for point in points
                ]
                for name, points in self._metrics.items()
            }
        }
    
    def export_prometheus(self) -> str:
        """导出Prometheus格式"""
        lines = []
        
        # 计数器
        for name, value in self._counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # 仪表
        for name, value in self._gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        return "\n".join(lines)

# 全局指标收集器
metrics = MetricsCollector()

def track_execution_time(func_name: str):
    """执行时间跟踪装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                metrics.histogram(
                    "execution_time",
                    execution_time,
                    {"function": func_name, "status": "success"}
                )
                metrics.increment(
                    "function_calls",
                    tags={"function": func_name, "status": "success"}
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                metrics.histogram(
                    "execution_time",
                    execution_time,
                    {"function": func_name, "status": "error"}
                )
                metrics.increment(
                    "function_calls",
                    tags={"function": func_name, "status": "error"}
                )
                
                raise
        return wrapper
    return decorator
```

### 3. 健康检查

#### health_check.py
```python
import asyncio
import aiohttp
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"

@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str
    response_time: float
    details: Dict[str, Any] = None

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks: List[callable] = []
    
    def register_check(self, check_func: callable):
        """注册健康检查函数"""
        self.checks.append(check_func)
    
    async def run_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        results = []
        
        for check in self.checks:
            try:
                result = await check()
                results.append(result)
            except Exception as e:
                results.append(HealthCheckResult(
                    name=check.__name__,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                    response_time=0.0
                ))
        
        # 计算总体状态
        overall_status = self._calculate_overall_status(results)
        
        return {
            "status": overall_status.value,
            "timestamp": asyncio.get_event_loop().time(),
            "checks": [
                {
                    "name": result.name,
                    "status": result.status.value,
                    "message": result.message,
                    "response_time": result.response_time,
                    "details": result.details
                }
                for result in results
            ]
        }
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """计算总体健康状态"""
        if not results:
            return HealthStatus.UNHEALTHY
        
        unhealthy_count = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

# 具体的健康检查函数
async def check_database_connection() -> HealthCheckResult:
    """检查数据库连接"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        # 这里应该是实际的数据库连接检查
        await asyncio.sleep(0.01)  # 模拟检查
        
        response_time = asyncio.get_event_loop().time() - start_time
        
        return HealthCheckResult(
            name="database",
            status=HealthStatus.HEALTHY,
            message="数据库连接正常",
            response_time=response_time
        )
    except Exception as e:
        response_time = asyncio.get_event_loop().time() - start_time
        
        return HealthCheckResult(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"数据库连接失败: {e}",
            response_time=response_time
        )

async def check_external_api() -> HealthCheckResult:
    """检查外部API"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://httpbin.org/status/200", timeout=5) as response:
                response_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    return HealthCheckResult(
                        name="external_api",
                        status=HealthStatus.HEALTHY,
                        message="外部API正常",
                        response_time=response_time
                    )
                else:
                    return HealthCheckResult(
                        name="external_api",
                        status=HealthStatus.DEGRADED,
                        message=f"外部API返回状态码: {response.status}",
                        response_time=response_time
                    )
    except Exception as e:
        response_time = asyncio.get_event_loop().time() - start_time
        
        return HealthCheckResult(
            name="external_api",
            status=HealthStatus.UNHEALTHY,
            message=f"外部API检查失败: {e}",
            response_time=response_time
        )

# 全局健康检查器
health_checker = HealthChecker()
health_checker.register_check(check_database_connection)
health_checker.register_check(check_external_api)
```

## 🔒 安全配置

### 1. 环境变量安全

#### secrets_manager.py
```python
import os
import base64
from cryptography.fernet import Fernet
from typing import Optional

class SecretsManager:
    """密钥管理器"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
            if key:
                key = base64.urlsafe_b64decode(key.encode())
            else:
                key = Fernet.generate_key()
                print(f"生成的加密密钥: {base64.urlsafe_b64encode(key).decode()}")
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def get_secret(self, key: str) -> Optional[str]:
        """获取加密的环境变量"""
        encrypted_value = os.getenv(f"{key}_ENCRYPTED")
        if encrypted_value:
            return self.decrypt(encrypted_value)
        
        # 回退到普通环境变量
        return os.getenv(key)

# 使用示例
secrets = SecretsManager()
api_key = secrets.get_secret("OPENWEATHER_API_KEY")
```

### 2. API安全

#### security.py
```python
import jwt
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class JWTManager:
    """JWT管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, data: Dict[str, Any], expires_in: int = 3600) -> str:
        """创建JWT令牌"""
        payload = data.copy()
        payload.update({
            "exp": time.time() + expires_in,
            "iat": time.time()
        })
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌"
            )

# 全局JWT管理器
jwt_manager = JWTManager(os.getenv("JWT_SECRET_KEY", "your-secret-key"))

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)
    return payload

# 使用示例
@app.post("/protected-endpoint")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.get('username')}"}
```

## 🚀 性能优化

### 1. 连接池配置

#### connection_pool.py
```python
import aiohttp
import asyncio
from typing import Optional

class HTTPConnectionPool:
    """HTTP连接池管理器"""
    
    def __init__(
        self,
        connector_limit: int = 100,
        connector_limit_per_host: int = 30,
        timeout: int = 30
    ):
        self.connector = aiohttp.TCPConnector(
            limit=connector_limit,
            limit_per_host=connector_limit_per_host,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=self.timeout
            )
        return self.session
    
    async def close(self):
        """关闭连接池"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        if self.connector:
            await self.connector.close()

# 全局连接池
http_pool = HTTPConnectionPool()
```

### 2. 缓存策略

#### cache.py
```python
import asyncio
import time
import json
from typing import Any, Optional, Dict, Callable
from functools import wraps

class AsyncCache:
    """异步缓存"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup()
    
    def _start_cleanup(self):
        """启动清理任务"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
    
    async def _cleanup_expired(self):
        """清理过期缓存"""
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, item in self._cache.items()
                    if item["expires_at"] < current_time
                ]
                
                for key in expired_keys:
                    del self._cache[key]
                
                await asyncio.sleep(60)  # 每分钟清理一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"缓存清理错误: {e}")
                await asyncio.sleep(60)
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            item = self._cache[key]
            if item["expires_at"] > time.time():
                return item["value"]
            else:
                del self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

# 缓存装饰器
def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 全局缓存实例
cache = AsyncCache()
```

## 📋 部署检查清单

### 生产环境部署前检查

- [ ] **环境配置**
  - [ ] 所有必需的环境变量已设置
  - [ ] API密钥和敏感信息已加密存储
  - [ ] 日志级别设置为INFO或WARNING
  - [ ] 调试模式已关闭

- [ ] **安全配置**
  - [ ] HTTPS已启用
  - [ ] 安全头已配置
  - [ ] JWT密钥已设置
  - [ ] 输入验证已实现

- [ ] **性能配置**
  - [ ] 连接池参数已优化
  - [ ] 缓存策略已配置
  - [ ] 并发限制已设置
  - [ ] 超时参数已调整

- [ ] **监控和日志**
  - [ ] 日志轮转已配置
  - [ ] 指标收集已启用
  - [ ] 健康检查已实现
  - [ ] 告警规则已设置

- [ ] **测试验证**
  - [ ] 所有单元测试通过
  - [ ] 集成测试通过
  - [ ] 性能测试通过
  - [ ] 安全测试通过

- [ ] **备份和恢复**
  - [ ] 数据备份策略已制定
  - [ ] 恢复流程已测试
  - [ ] 配置文件已备份

### 部署后验证

- [ ] **功能验证**
  - [ ] 所有API端点正常响应
  - [ ] 工具执行功能正常
  - [ ] 错误处理机制正常

- [ ] **性能验证**
  - [ ] 响应时间在预期范围内
  - [ ] 并发处理能力满足需求
  - [ ] 内存使用在合理范围内

- [ ] **监控验证**
  - [ ] 日志正常输出
  - [ ] 指标正常收集
  - [ ] 健康检查正常
  - [ ] 告警系统正常

## 🆘 故障排除

### 常见问题和解决方案

#### 1. 应用启动失败
```bash
# 检查日志
tail -f logs/app.log

# 检查配置
python -c "from config import Config; Config.get_instance().validate()"

# 检查依赖
pip check
```

#### 2. API响应缓慢
```bash
# 检查性能指标
curl http://localhost:8000/metrics

# 检查连接池状态
# 在代码中添加连接池监控

# 检查外部API状态
curl -w "@curl-format.txt" -o /dev/null -s "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"
```

#### 3. 内存泄漏
```bash
# 使用内存分析工具
pip install memory-profiler
python -m memory_profiler main.py

# 检查异步任务
# 确保所有异步任务都正确清理
```

#### 4. 数据库连接问题
```bash
# 检查连接池配置
# 调整连接池参数

# 检查网络连接
telnet database_host database_port
```

---

*本部署指南涵盖了从开发到生产的完整部署流程。根据具体需求调整配置参数和部署策略。*