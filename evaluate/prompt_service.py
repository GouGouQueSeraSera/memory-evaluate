"""
Prompt模板服务
"""
import re
from typing import Dict, Any


class PromptTemplateService:
    """Prompt模板服务"""
    
    def __init__(self, templates: Dict[str, str]):
        """
        初始化
        
        Args:
            templates: 模板字典，key为模板名称，value为模板内容
        """
        self.templates = templates
    
    def get_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        获取填充后的Prompt
        
        Args:
            template_name: 模板名称
            variables: 变量字典
            
        Returns:
            填充后的Prompt
        """
        if template_name not in self.templates:
            raise ValueError(f"模板不存在: {template_name}")
        
        template = self.templates[template_name]
        return self._replace_variables(template, variables)
    
    def _replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        替换模板中的变量
        
        Args:
            template: 模板内容
            variables: 变量字典
            
        Returns:
            替换后的内容
        """
        result = template
        
        # 替换 {{variable_name}} 格式的变量
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        
        return result
