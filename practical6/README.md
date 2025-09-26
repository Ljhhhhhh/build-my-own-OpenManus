# 项目6：多模态代理

基于项目5的ReAct推理代理，扩展实现多模态智能代理，支持图像处理和浏览器自动化功能。

## 功能特性

### 🎯 核心功能
- **多模态输入处理**：同时处理文本和图像输入
- **图像分析能力**：集成GPT-4V进行图像内容分析、OCR、对象识别
- **浏览器自动化**：实现网页导航、元素操作、截图等功能
- **智能决策**：基于多模态信息进行推理和行动

### 🛠️ 技术栈
- **Python 3.8+**
- **OpenAI GPT-4V** - 图像分析
- **Selenium WebDriver** - 浏览器自动化
- **PIL/Pillow** - 图像处理
- **Pydantic** - 数据验证
- **AsyncIO** - 异步编程

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd practical6

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 2. 配置说明

在 `.env` 文件中配置以下必需项：

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
VISION_MODEL=gpt-4-vision-preview

# 浏览器配置
BROWSER_TYPE=chrome
BROWSER_HEADLESS=true
```

### 3. 运行示例

```bash
# 运行演示程序
python demo.py

# 运行主程序
python main.py
```

## 项目结构

```
practical6/
├── README.md                    # 项目说明文档
├── requirements.txt             # 依赖包列表
├── .env.example                # 环境变量示例
├── main.py                     # 主程序入口
├── demo.py                     # 演示程序
├── 方案.md                     # 实施方案文档
├── agent/
│   ├── __init__.py
│   └── multimodal_agent.py     # 多模态代理主类
├── tools/
│   ├── __init__.py
│   ├── base.py                 # 基础工具类
│   ├── manager.py              # 工具管理器
│   ├── calculator.py           # 计算器工具
│   ├── text_processor.py       # 文本处理工具
│   ├── multimodal_base.py      # 多模态工具基类
│   ├── image_analyzer.py       # 图像分析工具
│   └── browser_automation.py   # 浏览器自动化工具
├── utils/
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   └── logger.py               # 日志系统
├── tests/
│   ├── __init__.py
│   ├── test_multimodal_agent.py
│   ├── test_image_analyzer.py
│   └── test_browser_tool.py
└── logs/
    └── multimodal.log          # 日志文件
```

## 使用示例

### 图像分析

```python
from agent.multimodal_agent import MultimodalAgent
from utils.config import get_config

# 初始化代理
config = get_config()
agent = MultimodalAgent(config)

# 分析图像
result = await agent.process({
    "text": "请分析这张图片中的内容",
    "image": "path/to/image.jpg",
    "task_type": "image_analysis"
})

print(result)
```

### 浏览器自动化

```python
# 网页操作
result = await agent.process({
    "text": "请打开百度首页并搜索'人工智能'",
    "task_type": "web_automation"
})

print(result)
```

### 多模态任务

```python
# 结合图像和网页操作
result = await agent.process({
    "text": "分析这张产品图片，然后在购物网站上搜索类似产品",
    "image": "product.jpg",
    "task_type": "general"
})

print(result)
```

## 开发指南

### 添加新工具

1. 继承 `MultimodalTool` 基类
2. 实现 `execute` 方法
3. 在 `ToolManager` 中注册工具

```python
from tools.multimodal_base import MultimodalTool

class CustomTool(MultimodalTool):
    name = "custom_tool"
    description = "自定义工具描述"
    
    async def execute(self, text: str, image: Optional[str] = None, **kwargs) -> ToolResult:
        # 实现工具逻辑
        pass
```

### 扩展代理功能

1. 修改 `MultimodalAgent` 类
2. 扩展 `process` 方法
3. 添加新的推理逻辑

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_image_analyzer.py

# 运行测试并显示覆盖率
pytest --cov=.
```

## 配置选项

### 图像处理配置

- `MAX_IMAGE_SIZE`: 最大图像文件大小（字节）
- `IMAGE_QUALITY`: JPEG压缩质量（1-100）
- `MAX_IMAGE_WIDTH/HEIGHT`: 最大图像尺寸

### 浏览器配置

- `BROWSER_TYPE`: 浏览器类型（chrome/firefox/edge）
- `BROWSER_HEADLESS`: 是否无头模式
- `BROWSER_TIMEOUT`: 操作超时时间

### GPT-4V配置

- `VISION_MODEL`: 视觉模型名称
- `MAX_VISION_TOKENS`: 最大token数
- `VISION_DETAIL`: 图像分析详细程度

## 故障排除

### 常见问题

1. **OpenAI API错误**
   - 检查API Key是否正确
   - 确认账户有GPT-4V访问权限

2. **浏览器启动失败**
   - 安装Chrome浏览器
   - 检查WebDriver配置

3. **图像处理错误**
   - 检查图像格式是否支持
   - 确认图像文件大小未超限

### 日志查看

```bash
# 查看应用日志
tail -f logs/multimodal.log

# 调整日志级别
export LOG_LEVEL=DEBUG
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持图像分析和浏览器自动化
- 基于ReAct推理模式的多模态代理

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。