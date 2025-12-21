"""
LLM服务
"""
import json
import requests
from typing import Dict, Any
from models_v2 import LLMConfig


class LLMService:
    """LLM服务实现"""
    
    def chat(self, prompt: str, config: LLMConfig) -> str:
        """调用LLM API"""
        url = f"{config.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_output_tokens
        }
        
        if config.log_requests:
            print(f"\n=== LLM Request ===")
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=config.timeout / 1000  # 转换为秒
            )
            response.raise_for_status()
            
            result = response.json()
            
            if config.log_requests:
                print(f"\n=== LLM Response ===")
                print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 提取响应内容
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"LLM调用失败: {str(e)}")
            raise
