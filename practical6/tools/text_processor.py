"""
文本处理工具 - 多功能文本处理工具

这个模块实现了一个功能丰富的文本处理工具，支持：
1. 文本转换（大小写、反转等）
2. 文本分析（字符统计、词频等）
3. 文本格式化（去除空格、换行等）

学习要点：
1. 复杂工具的参数设计
2. 多功能工具的实现模式
3. 字符串处理的常用方法
4. 正则表达式的使用
"""

import re
import time
from collections import Counter
from typing import Any, Dict, List, Optional
from .base import BaseTool, ToolResult


class TextProcessorTool(BaseTool):
    """
    文本处理工具
    
    支持多种文本处理操作，包括转换、分析和格式化功能。
    
    学习要点：
    - 多功能工具的设计模式
    - 参数验证的复杂逻辑
    - 字符串处理的最佳实践
    """
    
    def __init__(self):
        """
        初始化文本处理工具
        """
        super().__init__(
            name="text_processor",
            description="多功能文本处理工具，支持文本转换、分析和格式化"
        )
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        返回工具的JSON Schema
        
        学习要点：
        - 复杂参数结构的定义
        - 条件验证的实现
        - 枚举值的使用
        """
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要处理的文本内容"
                },
                "operation": {
                    "type": "string",
                    "enum": [
                        "uppercase", "lowercase", "capitalize", "title",
                        "reverse", "word_count", "char_count", "line_count",
                        "word_frequency", "remove_spaces", "remove_newlines",
                        "extract_emails", "extract_urls", "replace"
                    ],
                    "description": "要执行的文本处理操作"
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "find": {
                            "type": "string",
                            "description": "替换操作中要查找的文本"
                        },
                        "replace_with": {
                            "type": "string",
                            "description": "替换操作中的替换文本"
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "default": True,
                            "description": "是否区分大小写"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "限制结果数量（用于词频分析等）"
                        }
                    },
                    "additionalProperties": False,
                    "description": "操作的可选参数"
                }
            },
            "required": ["text", "operation"],
            "additionalProperties": False
        }
    
    def validate_input(self, **kwargs) -> bool | str:
        """
        验证输入参数
        
        学习要点：
        - 复杂参数验证逻辑
        - 条件验证的实现
        """
        # 调用父类的基本验证
        base_result = super().validate_input(**kwargs)
        if base_result is not True:
            return base_result
        
        operation = kwargs.get('operation')
        options = kwargs.get('options', {})
        
        # 替换操作需要额外参数
        if operation == 'replace':
            if 'find' not in options:
                return "替换操作需要提供 'find' 参数"
            if 'replace_with' not in options:
                return "替换操作需要提供 'replace_with' 参数"
        
        return True
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行文本处理工具
        
        学习要点：
        - 多分支逻辑的组织
        - 字符串处理方法的使用
        - 正则表达式的应用
        
        Args:
            **kwargs: 包含text, operation和可选options参数
            
        Returns:
            ToolResult: 处理结果
        """
        start_time = time.time()
        
        try:
            # 验证输入
            validation_result = self.validate_input(**kwargs)
            if validation_result is not True:
                return ToolResult.invalid_input(validation_result)
            
            text = kwargs['text']
            operation = kwargs['operation']
            options = kwargs.get('options', {})
            
            # 执行相应的文本处理操作
            result = await self._process_text(text, operation, options)
            
            execution_time = time.time() - start_time
            
            return ToolResult.success(
                content={
                    'operation': operation,
                    'original_text': text[:100] + "..." if len(text) > 100 else text,
                    'result': result,
                    'options': options
                },
                execution_time=execution_time,
                metadata={
                    'tool': self.name,
                    'operation_type': operation,
                    'text_length': len(text)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                error_message=f"文本处理过程中发生错误: {e}",
                execution_time=execution_time
            )
    
    async def _process_text(self, text: str, operation: str, options: Dict[str, Any]) -> Any:
        """
        执行具体的文本处理操作
        
        学习要点：
        - 私有方法的使用
        - 字符串处理的各种技巧
        - 正则表达式的实际应用
        
        Args:
            text: 要处理的文本
            operation: 操作类型
            options: 操作选项
            
        Returns:
            Any: 处理结果
        """
        # 文本转换操作
        if operation == "uppercase":
            return text.upper()
        
        elif operation == "lowercase":
            return text.lower()
        
        elif operation == "capitalize":
            return text.capitalize()
        
        elif operation == "title":
            return text.title()
        
        elif operation == "reverse":
            return text[::-1]
        
        # 文本分析操作
        elif operation == "word_count":
            words = text.split()
            return len(words)
        
        elif operation == "char_count":
            return len(text)
        
        elif operation == "line_count":
            return len(text.splitlines())
        
        elif operation == "word_frequency":
            words = text.lower().split()
            # 移除标点符号
            words = [re.sub(r'[^\w]', '', word) for word in words if word]
            counter = Counter(words)
            
            limit = options.get('limit', 10)
            return dict(counter.most_common(limit))
        
        # 文本格式化操作
        elif operation == "remove_spaces":
            return re.sub(r'\s+', ' ', text).strip()
        
        elif operation == "remove_newlines":
            return text.replace('\n', ' ').replace('\r', ' ')
        
        # 文本提取操作
        elif operation == "extract_emails":
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            limit = options.get('limit')
            return emails[:limit] if limit else emails
        
        elif operation == "extract_urls":
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            limit = options.get('limit')
            return urls[:limit] if limit else urls
        
        # 文本替换操作
        elif operation == "replace":
            find_text = options['find']
            replace_with = options['replace_with']
            case_sensitive = options.get('case_sensitive', True)
            
            if case_sensitive:
                return text.replace(find_text, replace_with)
            else:
                # 不区分大小写的替换
                pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                return pattern.sub(replace_with, text)
        
        else:
            raise ValueError(f"不支持的操作类型: {operation}")
    
    def get_supported_operations(self) -> List[str]:
        """
        获取支持的操作列表
        
        Returns:
            List[str]: 支持的操作类型列表
        """
        return [
            "uppercase", "lowercase", "capitalize", "title",
            "reverse", "word_count", "char_count", "line_count",
            "word_frequency", "remove_spaces", "remove_newlines",
            "extract_emails", "extract_urls", "replace"
        ]
    
    def get_operation_description(self, operation: str) -> Optional[str]:
        """
        获取操作的详细描述
        
        Args:
            operation: 操作类型
            
        Returns:
            Optional[str]: 操作描述
        """
        descriptions = {
            "uppercase": "将文本转换为大写",
            "lowercase": "将文本转换为小写",
            "capitalize": "将文本首字母大写",
            "title": "将文本转换为标题格式",
            "reverse": "反转文本",
            "word_count": "统计单词数量",
            "char_count": "统计字符数量",
            "line_count": "统计行数",
            "word_frequency": "分析词频",
            "remove_spaces": "移除多余空格",
            "remove_newlines": "移除换行符",
            "extract_emails": "提取邮箱地址",
            "extract_urls": "提取URL链接",
            "replace": "替换文本"
        }
        return descriptions.get(operation)