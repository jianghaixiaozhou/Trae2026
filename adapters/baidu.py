import asyncio
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseAdapter

class BaiduAdapter(BaseAdapter):
    
    def __init__(self):
        self.model = "baidu"
    
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        user_msg = messages[-1].get("content", "") if messages else ""
        response = f"【文心一言】你问的是：{user_msg}\n\n这是文心一言给你的回答。由于当前环境无法访问外部API，这是一个模拟响应。\n\n在实际部署环境中，你将获得真实的AI回复。\n\n文心一言是百度开发的大语言模型，具备多轮对话、知识问答、创意写作等能力！"
        return self.build_response(response, self.model)
    
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        user_msg = messages[-1].get("content", "") if messages else ""
        response = f"【文心一言】你问的是：{user_msg}\n\n这是文心一言给你的回答。由于当前环境无法访问外部API，这是一个模拟响应。\n\n在实际部署环境中，你将获得真实的AI回复。\n\n文心一言是百度开发的大语言模型，具备多轮对话、知识问答、创意写作等能力！"
        
        for char in response:
            yield self.build_stream_chunk(char, self.model)
            await asyncio.sleep(0.03)
        yield self.build_stream_chunk("", self.model, finish=True)