import asyncio
import json
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseAdapter

class DoubaoAdapter(BaseAdapter):
    
    def __init__(self):
        self.model = "doubao"
        self.mock_responses = [
            "你好！我是豆包，很高兴为你服务！",
            "感谢你的提问，让我来帮你解答。",
            "这个问题很有趣，让我仔细思考一下...",
            "根据我的分析，答案应该是这样的：",
            "好的，我来为你详细解释一下。",
            "豆包正在努力思考中，请稍等...",
            "这个问题涉及到多个方面，让我逐一分析。",
            "我来帮你梳理一下思路："
        ]
    
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        user_msg = messages[-1].get("content", "") if messages else ""
        response = f"【豆包】你问的是：{user_msg}\n\n这是豆包给你的回答。由于当前环境无法访问外部API，这是一个模拟响应。\n\n在实际部署环境中，你将获得真实的AI回复。\n\n豆包是字节跳动开发的AI助手，可以帮助你解答各种问题！"
        return self.build_response(response, self.model)
    
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        user_msg = messages[-1].get("content", "") if messages else ""
        response = f"【豆包】你问的是：{user_msg}\n\n这是豆包给你的回答。由于当前环境无法访问外部API，这是一个模拟响应。\n\n在实际部署环境中，你将获得真实的AI回复。\n\n豆包是字节跳动开发的AI助手，可以帮助你解答各种问题！"
        
        for char in response:
            yield self.build_stream_chunk(char, self.model)
            await asyncio.sleep(0.03)
        yield self.build_stream_chunk("", self.model, finish=True)