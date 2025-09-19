"""
Practical 3.2 - 生产级示例

这个示例展示了如何将异步工具框架应用到生产环境中，包括：
1. 完整的日志系统
2. 配置管理
3. 健康检查
4. 监控和告警
5. 优雅关闭
6. 部署配置

学习要点：
1. 生产级Python应用的架构
2. 日志和监控的最佳实践
3. 配置管理的标准化
4. 错误处理和恢复机制
5. 性能优化的实际应用
"""

import asyncio
import sys
import os
import json
import logging
import signal
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base import AsyncBaseTool, ToolResult, ToolResultStatus
from tools import AsyncToolManager, AsyncCalculatorTool, AsyncWeatherTool
from config import Config


# 配置日志系统
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    设置生产级日志系统
    
    💡 对比TypeScript:
    import winston from 'winston';
    
    const setupLogging = (logLevel: string = 'info', logFile?: string) => {
        const transports: winston.transport[] = [
            new winston.transports.Console({
                format: winston.format.combine(
                    winston.format.colorize(),
                    winston.format.timestamp(),
                    winston.format.printf(({ timestamp, level, message, ...meta }) => {
                        return `${timestamp} [${level}] ${message} ${Object.keys(meta).length ? JSON.stringify(meta) : ''}`;
                    })
                )
            })
        ];
        
        if (logFile) {
            transports.push(
                new winston.transports.File({
                    filename: logFile,
                    format: winston.format.combine(
                        winston.format.timestamp(),
                        winston.format.json()
                    )
                })
            );
        }
        
        const logger = winston.createLogger({
            level: logLevel.toLowerCase(),
            transports,
            exceptionHandlers: [
                new winston.transports.File({ filename: 'exceptions.log' })
            ],
            rejectionHandlers: [
                new winston.transports.File({ filename: 'rejections.log' })
            ]
        });
        
        return logger;
    };
    
    学习要点：
    - 结构化日志的配置
    - 多输出目标的管理
    - 日志级别的控制
    - 异常日志的处理
    """
    # 创建日志格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 设置根日志器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


@dataclass
class HealthCheckResult:
    """
    健康检查结果
    
    💡 对比TypeScript:
    interface HealthCheckResult {
        service: string;
        status: 'healthy' | 'unhealthy' | 'degraded';
        timestamp: string;
        responseTime: number;
        details?: Record<string, any>;
        error?: string;
    }
    
    学习要点：
    - 健康检查的标准化
    - 状态枚举的定义
    - 详细信息的结构化
    """
    service: str
    status: str  # 'healthy', 'unhealthy', 'degraded'
    timestamp: str
    response_time: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthChecker:
    """
    健康检查器
    
    💡 对比TypeScript:
    class HealthChecker {
        private checks: Map<string, () => Promise<HealthCheckResult>> = new Map();
        private logger: winston.Logger;
        
        constructor(logger: winston.Logger) {
            this.logger = logger;
        }
        
        registerCheck(name: string, checkFn: () => Promise<HealthCheckResult>): void {
            this.checks.set(name, checkFn);
            this.logger.info(`Health check registered: ${name}`);
        }
        
        async runCheck(name: string): Promise<HealthCheckResult> {
            const checkFn = this.checks.get(name);
            if (!checkFn) {
                return {
                    service: name,
                    status: 'unhealthy',
                    timestamp: new Date().toISOString(),
                    responseTime: 0,
                    error: 'Check not found'
                };
            }
            
            const startTime = Date.now();
            try {
                const result = await checkFn();
                const responseTime = Date.now() - startTime;
                return { ...result, responseTime };
            } catch (error) {
                const responseTime = Date.now() - startTime;
                return {
                    service: name,
                    status: 'unhealthy',
                    timestamp: new Date().toISOString(),
                    responseTime,
                    error: error.message
                };
            }
        }
        
        async runAllChecks(): Promise<Record<string, HealthCheckResult>> {
            const results: Record<string, HealthCheckResult> = {};
            
            for (const [name] of this.checks) {
                results[name] = await this.runCheck(name);
            }
            
            return results;
        }
        
        getOverallStatus(results: Record<string, HealthCheckResult>): 'healthy' | 'unhealthy' | 'degraded' {
            const statuses = Object.values(results).map(r => r.status);
            
            if (statuses.every(s => s === 'healthy')) {
                return 'healthy';
            } else if (statuses.some(s => s === 'unhealthy')) {
                return 'unhealthy';
            } else {
                return 'degraded';
            }
        }
    }
    
    学习要点：
    - 健康检查的设计模式
    - 异步检查的管理
    - 状态聚合的逻辑
    - 错误处理的完整性
    """
    
    def __init__(self, logger: logging.Logger):
        self.checks: Dict[str, Callable[[], Any]] = {}
        self.logger = logger
    
    def register_check(self, name: str, check_fn: Callable[[], Any]):
        """注册健康检查"""
        self.checks[name] = check_fn
        self.logger.info(f"Health check registered: {name}")
    
    async def run_check(self, name: str) -> HealthCheckResult:
        """运行单个健康检查"""
        if name not in self.checks:
            return HealthCheckResult(
                service=name,
                status="unhealthy",
                timestamp=datetime.now().isoformat(),
                response_time=0.0,
                error="Check not found"
            )
        
        start_time = time.time()
        try:
            check_fn = self.checks[name]
            if asyncio.iscoroutinefunction(check_fn):
                result = await check_fn()
            else:
                result = check_fn()
            
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, HealthCheckResult):
                result.response_time = response_time
                return result
            else:
                return HealthCheckResult(
                    service=name,
                    status="healthy",
                    timestamp=datetime.now().isoformat(),
                    response_time=response_time,
                    details={"result": str(result)}
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Health check failed for {name}: {e}")
            
            return HealthCheckResult(
                service=name,
                status="unhealthy",
                timestamp=datetime.now().isoformat(),
                response_time=response_time,
                error=str(e)
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """运行所有健康检查"""
        results = {}
        
        for name in self.checks:
            results[name] = await self.run_check(name)
        
        return results
    
    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> str:
        """获取整体健康状态"""
        statuses = [result.status for result in results.values()]
        
        if all(status == "healthy" for status in statuses):
            return "healthy"
        elif any(status == "unhealthy" for status in statuses):
            return "unhealthy"
        else:
            return "degraded"


@dataclass
class MetricPoint:
    """
    指标数据点
    
    💡 对比TypeScript:
    interface MetricPoint {
        name: string;
        value: number;
        timestamp: string;
        tags?: Record<string, string>;
        unit?: string;
    }
    
    学习要点：
    - 指标数据的标准化
    - 时间序列数据的结构
    - 标签系统的设计
    """
    name: str
    value: float
    timestamp: str
    tags: Optional[Dict[str, str]] = None
    unit: Optional[str] = None


class MetricsCollector:
    """
    指标收集器
    
    💡 对比TypeScript:
    class MetricsCollector {
        private metrics: MetricPoint[] = [];
        private counters: Map<string, number> = new Map();
        private gauges: Map<string, number> = new Map();
        private histograms: Map<string, number[]> = new Map();
        private logger: winston.Logger;
        
        constructor(logger: winston.Logger) {
            this.logger = logger;
        }
        
        counter(name: string, value: number = 1, tags?: Record<string, string>): void {
            const key = this.getMetricKey(name, tags);
            const current = this.counters.get(key) || 0;
            this.counters.set(key, current + value);
            
            this.recordMetric({
                name,
                value: current + value,
                timestamp: new Date().toISOString(),
                tags,
                unit: 'count'
            });
        }
        
        gauge(name: string, value: number, tags?: Record<string, string>): void {
            const key = this.getMetricKey(name, tags);
            this.gauges.set(key, value);
            
            this.recordMetric({
                name,
                value,
                timestamp: new Date().toISOString(),
                tags,
                unit: 'gauge'
            });
        }
        
        histogram(name: string, value: number, tags?: Record<string, string>): void {
            const key = this.getMetricKey(name, tags);
            const values = this.histograms.get(key) || [];
            values.push(value);
            this.histograms.set(key, values);
            
            this.recordMetric({
                name,
                value,
                timestamp: new Date().toISOString(),
                tags,
                unit: 'histogram'
            });
        }
        
        private recordMetric(metric: MetricPoint): void {
            this.metrics.push(metric);
            
            // 保持最近1000个指标
            if (this.metrics.length > 1000) {
                this.metrics = this.metrics.slice(-1000);
            }
        }
        
        private getMetricKey(name: string, tags?: Record<string, string>): string {
            if (!tags) return name;
            const tagStr = Object.entries(tags)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([k, v]) => `${k}=${v}`)
                .join(',');
            return `${name}{${tagStr}}`;
        }
        
        getMetrics(): MetricPoint[] {
            return [...this.metrics];
        }
        
        getCounters(): Record<string, number> {
            return Object.fromEntries(this.counters);
        }
        
        getGauges(): Record<string, number> {
            return Object.fromEntries(this.gauges);
        }
        
        getHistograms(): Record<string, number[]> {
            return Object.fromEntries(this.histograms);
        }
        
        reset(): void {
            this.metrics = [];
            this.counters.clear();
            this.gauges.clear();
            this.histograms.clear();
            this.logger.info('Metrics reset');
        }
    }
    
    学习要点：
    - 指标收集的设计模式
    - 不同指标类型的处理
    - 内存管理的考虑
    - 标签系统的实现
    """
    
    def __init__(self, logger: logging.Logger):
        self.metrics: List[MetricPoint] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.logger = logger
    
    def counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """计数器指标"""
        key = self._get_metric_key(name, tags)
        current = self.counters.get(key, 0.0)
        self.counters[key] = current + value
        
        self._record_metric(MetricPoint(
            name=name,
            value=current + value,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            unit="count"
        ))
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """仪表盘指标"""
        key = self._get_metric_key(name, tags)
        self.gauges[key] = value
        
        self._record_metric(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            unit="gauge"
        ))
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """直方图指标"""
        key = self._get_metric_key(name, tags)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        
        self._record_metric(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            unit="histogram"
        ))
    
    def _record_metric(self, metric: MetricPoint):
        """记录指标"""
        self.metrics.append(metric)
        
        # 保持最近1000个指标
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def _get_metric_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """生成指标键"""
        if not tags:
            return name
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"
    
    def get_metrics(self) -> List[MetricPoint]:
        """获取所有指标"""
        return self.metrics.copy()
    
    def get_counters(self) -> Dict[str, float]:
        """获取计数器"""
        return self.counters.copy()
    
    def get_gauges(self) -> Dict[str, float]:
        """获取仪表盘"""
        return self.gauges.copy()
    
    def get_histograms(self) -> Dict[str, List[float]]:
        """获取直方图"""
        return {k: v.copy() for k, v in self.histograms.items()}
    
    def reset(self):
        """重置所有指标"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.logger.info("Metrics reset")


class ProductionToolManager(AsyncToolManager):
    """
    生产级工具管理器
    
    💡 对比TypeScript:
    class ProductionToolManager extends AsyncToolManager {
        private logger: winston.Logger;
        private metricsCollector: MetricsCollector;
        private healthChecker: HealthChecker;
        private isShuttingDown: boolean = false;
        
        constructor(
            logger: winston.Logger,
            metricsCollector: MetricsCollector,
            healthChecker: HealthChecker,
            options: ToolManagerOptions = {}
        ) {
            super(options);
            this.logger = logger;
            this.metricsCollector = metricsCollector;
            this.healthChecker = healthChecker;
            
            this.setupHealthChecks();
            this.setupMetrics();
        }
        
        async executeTool(toolName: string, params: any): Promise<ToolResult> {
            if (this.isShuttingDown) {
                throw new Error('Tool manager is shutting down');
            }
            
            const startTime = Date.now();
            this.metricsCollector.counter('tool_executions_total', 1, { tool: toolName });
            
            try {
                this.logger.info(`Executing tool: ${toolName}`, { params });
                
                const result = await super.executeTool(toolName, params);
                
                const duration = Date.now() - startTime;
                this.metricsCollector.histogram('tool_execution_duration_ms', duration, { tool: toolName });
                
                if (result.isSuccess()) {
                    this.metricsCollector.counter('tool_executions_success_total', 1, { tool: toolName });
                    this.logger.info(`Tool execution successful: ${toolName}`, { duration });
                } else {
                    this.metricsCollector.counter('tool_executions_error_total', 1, { tool: toolName });
                    this.logger.error(`Tool execution failed: ${toolName}`, { 
                        error: result.errorMessage,
                        duration 
                    });
                }
                
                return result;
                
            } catch (error) {
                const duration = Date.now() - startTime;
                this.metricsCollector.counter('tool_executions_error_total', 1, { tool: toolName });
                this.metricsCollector.histogram('tool_execution_duration_ms', duration, { tool: toolName });
                
                this.logger.error(`Tool execution exception: ${toolName}`, { 
                    error: error.message,
                    duration 
                });
                
                throw error;
            }
        }
        
        private setupHealthChecks(): void {
            this.healthChecker.registerCheck('tool_manager', async () => {
                const toolCount = this.getRegisteredTools().length;
                const isHealthy = toolCount > 0 && !this.isShuttingDown;
                
                return {
                    service: 'tool_manager',
                    status: isHealthy ? 'healthy' : 'unhealthy',
                    timestamp: new Date().toISOString(),
                    responseTime: 0,
                    details: {
                        registeredTools: toolCount,
                        isShuttingDown: this.isShuttingDown
                    }
                };
            });
        }
        
        private setupMetrics(): void {
            // 定期更新指标
            setInterval(() => {
                const toolCount = this.getRegisteredTools().length;
                this.metricsCollector.gauge('registered_tools_count', toolCount);
                
                const activeTaskCount = this.getActiveTaskCount();
                this.metricsCollector.gauge('active_tasks_count', activeTaskCount);
            }, 5000);
        }
        
        async gracefulShutdown(): Promise<void> {
            this.logger.info('Starting graceful shutdown...');
            this.isShuttingDown = true;
            
            try {
                await super.cleanup();
                this.logger.info('Graceful shutdown completed');
            } catch (error) {
                this.logger.error('Error during graceful shutdown', { error: error.message });
                throw error;
            }
        }
    }
    
    学习要点：
    - 生产级管理器的扩展
    - 日志和指标的集成
    - 健康检查的实现
    - 优雅关闭的处理
    """
    
    def __init__(self, logger: logging.Logger, metrics_collector: MetricsCollector, 
                 health_checker: HealthChecker, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.metrics_collector = metrics_collector
        self.health_checker = health_checker
        self.is_shutting_down = False
        
        self._setup_health_checks()
        self._setup_metrics()
    
    async def execute_tool(self, tool_name: str, **params) -> ToolResult:
        """执行工具（带监控）"""
        if self.is_shutting_down:
            raise RuntimeError("Tool manager is shutting down")
        
        start_time = time.time()
        self.metrics_collector.counter("tool_executions_total", 1.0, {"tool": tool_name})
        
        try:
            self.logger.info(f"Executing tool: {tool_name}", extra={"params": params})
            
            result = await super().execute_tool(tool_name, **params)
            
            duration = (time.time() - start_time) * 1000
            self.metrics_collector.histogram("tool_execution_duration_ms", duration, {"tool": tool_name})
            
            if result.is_success():
                self.metrics_collector.counter("tool_executions_success_total", 1.0, {"tool": tool_name})
                self.logger.info(f"Tool execution successful: {tool_name}", extra={"duration": duration})
            else:
                self.metrics_collector.counter("tool_executions_error_total", 1.0, {"tool": tool_name})
                self.logger.error(f"Tool execution failed: {tool_name}", extra={
                    "error": result.error_message,
                    "duration": duration
                })
            
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.metrics_collector.counter("tool_executions_error_total", 1.0, {"tool": tool_name})
            self.metrics_collector.histogram("tool_execution_duration_ms", duration, {"tool": tool_name})
            
            self.logger.error(f"Tool execution exception: {tool_name}", extra={
                "error": str(e),
                "duration": duration
            })
            
            raise
    
    def _setup_health_checks(self):
        """设置健康检查"""
        async def tool_manager_health():
            tool_count = len(self.tools)
            is_healthy = tool_count > 0 and not self.is_shutting_down
            
            return HealthCheckResult(
                service="tool_manager",
                status="healthy" if is_healthy else "unhealthy",
                timestamp=datetime.now().isoformat(),
                response_time=0.0,
                details={
                    "registered_tools": tool_count,
                    "is_shutting_down": self.is_shutting_down
                }
            )
        
        self.health_checker.register_check("tool_manager", tool_manager_health)
    
    def _setup_metrics(self):
        """设置指标收集"""
        # 这里可以设置定期指标更新
        pass
    
    async def graceful_shutdown(self):
        """优雅关闭"""
        self.logger.info("Starting graceful shutdown...")
        self.is_shutting_down = True
        
        try:
            await self.cleanup()
            self.logger.info("Graceful shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during graceful shutdown: {e}")
            raise


class ProductionApplication:
    """
    生产级应用程序
    
    💡 对比TypeScript:
    class ProductionApplication {
        private logger: winston.Logger;
        private config: Config;
        private toolManager: ProductionToolManager;
        private metricsCollector: MetricsCollector;
        private healthChecker: HealthChecker;
        private isRunning: boolean = false;
        private shutdownPromise?: Promise<void>;
        
        constructor() {
            this.setupSignalHandlers();
        }
        
        async initialize(): Promise<void> {
            this.logger = setupLogging(
                process.env.LOG_LEVEL || 'info',
                process.env.LOG_FILE
            );
            
            this.config = new Config();
            this.metricsCollector = new MetricsCollector(this.logger);
            this.healthChecker = new HealthChecker(this.logger);
            
            this.toolManager = new ProductionToolManager(
                this.logger,
                this.metricsCollector,
                this.healthChecker,
                {
                    maxConcurrentTasks: this.config.maxConcurrentTasks,
                    defaultTimeout: this.config.defaultTimeout
                }
            );
            
            await this.registerTools();
            
            this.logger.info('Application initialized successfully');
        }
        
        private async registerTools(): Promise<void> {
            const calculator = new AsyncCalculatorTool();
            await this.toolManager.registerTool(calculator);
            
            if (this.config.weatherApiKey) {
                const weather = new AsyncWeatherTool();
                await this.toolManager.registerTool(weather);
            }
            
            this.logger.info('Tools registered successfully');
        }
        
        async start(): Promise<void> {
            if (this.isRunning) {
                throw new Error('Application is already running');
            }
            
            this.isRunning = true;
            this.logger.info('Application starting...');
            
            // 启动健康检查定时器
            this.startHealthCheckTimer();
            
            // 启动指标收集定时器
            this.startMetricsTimer();
            
            this.logger.info('Application started successfully');
        }
        
        private startHealthCheckTimer(): void {
            setInterval(async () => {
                try {
                    const results = await this.healthChecker.runAllChecks();
                    const overallStatus = this.healthChecker.getOverallStatus(results);
                    
                    this.logger.debug('Health check completed', { 
                        status: overallStatus,
                        results 
                    });
                    
                    this.metricsCollector.gauge('health_status', 
                        overallStatus === 'healthy' ? 1 : 0
                    );
                } catch (error) {
                    this.logger.error('Health check failed', { error: error.message });
                }
            }, 30000); // 每30秒检查一次
        }
        
        private startMetricsTimer(): void {
            setInterval(() => {
                const memoryUsage = process.memoryUsage();
                this.metricsCollector.gauge('memory_usage_mb', memoryUsage.heapUsed / 1024 / 1024);
                this.metricsCollector.gauge('memory_total_mb', memoryUsage.heapTotal / 1024 / 1024);
                
                const uptime = process.uptime();
                this.metricsCollector.gauge('uptime_seconds', uptime);
            }, 10000); // 每10秒收集一次
        }
        
        async executeWorkflow(): Promise<void> {
            this.logger.info('Starting workflow execution...');
            
            try {
                // 执行一些示例工作流
                const calcResult = await this.toolManager.executeTool('async_calculator', {
                    operation: 'add',
                    operands: [1, 2, 3, 4, 5]
                });
                
                this.logger.info('Calculation completed', { result: calcResult.content });
                
                if (this.config.weatherApiKey) {
                    const weatherResult = await this.toolManager.executeTool('async_weather', {
                        city: 'Beijing'
                    });
                    
                    this.logger.info('Weather query completed', { 
                        success: weatherResult.isSuccess() 
                    });
                }
                
                this.logger.info('Workflow execution completed');
                
            } catch (error) {
                this.logger.error('Workflow execution failed', { error: error.message });
                throw error;
            }
        }
        
        private setupSignalHandlers(): void {
            const gracefulShutdown = () => {
                if (this.shutdownPromise) {
                    return this.shutdownPromise;
                }
                
                this.shutdownPromise = this.shutdown();
                return this.shutdownPromise;
            };
            
            process.on('SIGTERM', gracefulShutdown);
            process.on('SIGINT', gracefulShutdown);
        }
        
        async shutdown(): Promise<void> {
            if (!this.isRunning) {
                return;
            }
            
            this.logger.info('Application shutting down...');
            this.isRunning = false;
            
            try {
                if (this.toolManager) {
                    await this.toolManager.gracefulShutdown();
                }
                
                this.logger.info('Application shutdown completed');
            } catch (error) {
                this.logger.error('Error during shutdown', { error: error.message });
                throw error;
            }
        }
        
        getHealthStatus(): Promise<Record<string, HealthCheckResult>> {
            return this.healthChecker.runAllChecks();
        }
        
        getMetrics(): {
            points: MetricPoint[];
            counters: Record<string, number>;
            gauges: Record<string, number>;
            histograms: Record<string, number[]>;
        } {
            return {
                points: this.metricsCollector.getMetrics(),
                counters: this.metricsCollector.getCounters(),
                gauges: this.metricsCollector.getGauges(),
                histograms: this.metricsCollector.getHistograms()
            };
        }
    }
    
    学习要点：
    - 生产级应用的完整架构
    - 生命周期管理的实现
    - 信号处理和优雅关闭
    - 监控和健康检查的集成
    - 配置管理的最佳实践
    """
    
    def __init__(self):
        self.logger = None
        self.config = None
        self.tool_manager = None
        self.metrics_collector = None
        self.health_checker = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        self._setup_signal_handlers()
    
    async def initialize(self):
        """初始化应用程序"""
        # 设置日志
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE")
        self.logger = setup_logging(log_level, log_file)
        
        # 加载配置
        self.config = Config()
        
        # 创建组件
        self.metrics_collector = MetricsCollector(self.logger)
        self.health_checker = HealthChecker(self.logger)
        
        # 创建生产级工具管理器
        self.tool_manager = ProductionToolManager(
            logger=self.logger,
            metrics_collector=self.metrics_collector,
            health_checker=self.health_checker,
            max_concurrent_tasks=self.config.max_concurrent_tasks,
            default_timeout=self.config.default_timeout
        )
        
        # 注册工具
        await self._register_tools()
        
        self.logger.info("Application initialized successfully")
    
    async def _register_tools(self):
        """注册工具"""
        # 注册计算器工具
        calculator = AsyncCalculatorTool()
        await self.tool_manager.register_tool(calculator)
        
        # 如果有API密钥，注册天气工具
        if self.config.weather_api_key:
            weather = AsyncWeatherTool()
            await self.tool_manager.register_tool(weather)
        
        self.logger.info("Tools registered successfully")
    
    async def start(self):
        """启动应用程序"""
        if self.is_running:
            raise RuntimeError("Application is already running")
        
        self.is_running = True
        self.logger.info("Application starting...")
        
        # 启动后台任务
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metrics_collection_loop())
        
        self.logger.info("Application started successfully")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                results = await self.health_checker.run_all_checks()
                overall_status = self.health_checker.get_overall_status(results)
                
                self.logger.debug(f"Health check completed: {overall_status}")
                
                # 记录健康状态指标
                self.metrics_collector.gauge(
                    "health_status",
                    1.0 if overall_status == "healthy" else 0.0
                )
                
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
            
            await asyncio.sleep(30)  # 每30秒检查一次
    
    async def _metrics_collection_loop(self):
        """指标收集循环"""
        while self.is_running:
            try:
                # 收集系统指标
                import psutil
                
                # 内存使用情况
                memory = psutil.virtual_memory()
                self.metrics_collector.gauge("memory_usage_percent", memory.percent)
                self.metrics_collector.gauge("memory_available_mb", memory.available / 1024 / 1024)
                
                # CPU使用情况
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics_collector.gauge("cpu_usage_percent", cpu_percent)
                
                # 进程信息
                process = psutil.Process()
                process_memory = process.memory_info()
                self.metrics_collector.gauge("process_memory_mb", process_memory.rss / 1024 / 1024)
                
                # 运行时间
                uptime = time.time() - process.create_time()
                self.metrics_collector.gauge("uptime_seconds", uptime)
                
            except Exception as e:
                self.logger.error(f"Metrics collection failed: {e}")
            
            await asyncio.sleep(10)  # 每10秒收集一次
    
    async def execute_workflow(self):
        """执行工作流"""
        self.logger.info("Starting workflow execution...")
        
        try:
            # 执行计算任务
            calc_result = await self.tool_manager.execute_tool(
                "async_calculator",
                operation="add",
                operands=[1, 2, 3, 4, 5]
            )
            
            self.logger.info(f"Calculation completed: {calc_result.content}")
            
            # 如果有天气API，执行天气查询
            if self.config.weather_api_key:
                weather_result = await self.tool_manager.execute_tool(
                    "async_weather",
                    city="Beijing"
                )
                
                self.logger.info(f"Weather query completed: {weather_result.is_success()}")
            
            self.logger.info("Workflow execution completed")
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def shutdown(self):
        """关闭应用程序"""
        if not self.is_running:
            return
        
        self.logger.info("Application shutting down...")
        self.is_running = False
        
        try:
            if self.tool_manager:
                await self.tool_manager.graceful_shutdown()
            
            self.shutdown_event.set()
            self.logger.info("Application shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise
    
    async def get_health_status(self) -> Dict[str, HealthCheckResult]:
        """获取健康状态"""
        return await self.health_checker.run_all_checks()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return {
            "points": [asdict(point) for point in self.metrics_collector.get_metrics()],
            "counters": self.metrics_collector.get_counters(),
            "gauges": self.metrics_collector.get_gauges(),
            "histograms": self.metrics_collector.get_histograms()
        }


async def production_example():
    """
    生产级示例演示
    
    学习要点：
    - 完整的生产级应用架构
    - 监控和健康检查的实现
    - 优雅关闭的处理
    - 错误处理和恢复
    """
    print("🏭 生产级应用示例")
    print("=" * 50)
    
    app = ProductionApplication()
    
    try:
        # 初始化应用
        print("🚀 初始化应用...")
        await app.initialize()
        
        # 启动应用
        print("▶️  启动应用...")
        await app.start()
        
        # 执行工作流
        print("⚙️  执行工作流...")
        await app.execute_workflow()
        
        # 检查健康状态
        print("\n🏥 健康检查:")
        print("-" * 20)
        health_status = await app.get_health_status()
        
        for service, result in health_status.items():
            status_emoji = "✅" if result.status == "healthy" else "❌"
            print(f"{status_emoji} {service}: {result.status} ({result.response_time:.2f}ms)")
            
            if result.details:
                for key, value in result.details.items():
                    print(f"   {key}: {value}")
        
        # 获取指标
        print("\n📊 应用指标:")
        print("-" * 20)
        metrics = app.get_metrics()
        
        print(f"计数器指标: {len(metrics['counters'])} 个")
        for name, value in list(metrics['counters'].items())[:5]:  # 显示前5个
            print(f"  {name}: {value}")
        
        print(f"仪表盘指标: {len(metrics['gauges'])} 个")
        for name, value in list(metrics['gauges'].items())[:5]:  # 显示前5个
            print(f"  {name}: {value:.2f}")
        
        print(f"直方图指标: {len(metrics['histograms'])} 个")
        for name, values in list(metrics['histograms'].items())[:3]:  # 显示前3个
            if values:
                avg_value = sum(values) / len(values)
                print(f"  {name}: {len(values)} 个数据点, 平均值: {avg_value:.2f}")
        
        # 模拟运行一段时间
        print("\n⏳ 模拟运行 10 秒...")
        await asyncio.sleep(10)
        
        # 再次检查指标
        print("\n📈 更新后的指标:")
        print("-" * 20)
        updated_metrics = app.get_metrics()
        
        print(f"指标数据点: {len(updated_metrics['points'])} 个")
        print(f"计数器指标: {len(updated_metrics['counters'])} 个")
        print(f"仪表盘指标: {len(updated_metrics['gauges'])} 个")
        
        print("\n✅ 生产级应用示例完成")
        
    except Exception as e:
        print(f"❌ 生产级应用异常: {e}")
        traceback.print_exc()
    
    finally:
        # 优雅关闭
        print("\n🛑 优雅关闭应用...")
        await app.shutdown()


async def main():
    """
    主函数 - 运行生产级示例
    
    学习要点：
    - 生产级应用的完整生命周期
    - 监控和健康检查的集成
    - 优雅关闭的实现
    - 错误处理的完整性
    """
    print("🎯 Practical 3.2 - 生产级示例")
    print("=" * 50)
    
    try:
        await production_example()
        
        print("\n🎓 生产级学习要点总结:")
        print("  1. 完整的日志系统设计")
        print("  2. 配置管理的标准化")
        print("  3. 健康检查的实现")
        print("  4. 指标收集和监控")
        print("  5. 优雅关闭的处理")
        print("  6. 信号处理的实现")
        print("  7. 生产级错误处理")
        print("  8. 性能监控的集成")
        
    except Exception as e:
        print(f"❌ 生产级示例执行异常: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    """
    程序入口点
    
    学习要点：
    - 生产级应用的启动
    - 异常处理的完整性
    - 平台兼容性的考虑
    """
    try:
        # Windows平台的事件循环策略
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # 运行主程序
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"❌ 程序启动异常: {e}")
        sys.exit(1)