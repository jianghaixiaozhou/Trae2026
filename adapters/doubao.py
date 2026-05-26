import asyncio
import aiohttp
import json
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseAdapter

class DoubaoAdapter(BaseAdapter):
    
    def __init__(self):
        self.model = "doubao"
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Origin': 'https://www.doubao.com',
                    'Referer': 'https://www.doubao.com/',
                }
            )
        return self.session
    
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        user_msg = messages[-1].get("content", "") if messages else ""
        
        session = await self._get_session()
        try:
            async with session.post(
                "https://api.doubao.com/open_api/chat/completions",
                json={
                    "model": "Doubao-3",
                    "messages": messages,
                    "stream": False
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        return self.build_response(content, self.model)
                return self.build_response(f"【豆包】你问的是：{user_msg}\n\n豆包是字节跳动开发的智能助手，可以回答各种问题。当前为模拟响应模式。", self.model)
        except Exception as e:
            return self.build_response(f"【豆包】你问的是：{user_msg}\n\n豆包是字节跳动开发的智能助手，可以回答各种问题。当前为模拟响应模式。\n\n错误信息：{str(e)}", self.model)
    
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        user_msg = messages[-1].get("content", "") if messages else ""
        response = f"【豆包】你问的是：{user_msg}\n\n豆包是字节跳动开发的智能助手，可以回答各种问题。当前为模拟响应模式。\n\n在实际部署中，如果网络可以访问豆包官网，可以直接模拟网页请求获取真实响应。"
        
        for char in response:
            yield self.build_stream_chunk(char, self.model)
            await asyncio.sleep(0.03)
        yield self.build_stream_chunk("", self.model, finish=True)