# 项目2：配置驱动助手

## 项目目标

- 学会使用 Pydantic 进行数据验证
- 掌握 TOML 配置文件处理
- 理解配置驱动开发模式

## 核心特性

- **Pydantic 数据模型**：类型安全的配置验证
- **TOML 配置文件**：人性化的配置格式
- **配置驱动架构**：通过配置文件控制助手行为
- **多助手支持**：可创建不同配置的专业助手

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 3. 配置助手
编辑 `assistant_config.toml` 文件，自定义助手行为：
- 助手名称和描述
- 系统提示词
- LLM 参数（模型、温度、最大token等）

### 4. 运行程序
```bash
python config_driven_assistant.py
```

## 学习要点

### Pydantic 数据验证
- 类型注解和验证
- Field 字段配置
- 数据序列化和反序列化

### TOML 配置文件
- 人性化的配置格式
- 嵌套配置结构
- 配置文件解析

### 配置驱动开发
- 分离配置和代码
- 灵活的参数控制
- 多环境配置支持

## 文件结构

- `config_driven_assistant.py` - 主程序文件
- `assistant_config.toml` - 助手配置文件
- `python_assistant.toml` - Python编程助手配置示例
- `creative_assistant.toml` - 创意写作助手配置示例
- `requirements.txt` - 项目依赖
- `.env.example` - 环境变量模板