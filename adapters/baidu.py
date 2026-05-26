import asyncio
import aiohttp
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseAdapter

class BaiduAdapter(BaseAdapter):
    
    def __init__(self):
        self.model = "baidu"
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Origin': 'https://yiyan.baidu.com',
                    'Referer': 'https://yiyan.baidu.com/',
                }
            )
        return self.session
    
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        user_msg = messages[-1].get("content", "") if messages else ""
        
        session = await self._get_session()
        try:
            async with session.post(
                "https://yiyan.baidu.com/api/text/completion",
                json={
                    "prompt": user_msg,
                    "model": "ERNIE-Bot",
                    "temperature": 0.7
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("result", "")
                    if content:
                        return self.build_response(content, self.model)
                return self.build_response(f"【文心一言】你问的是：{user_msg}\n\n文心一言是百度开发的大语言模型，具备多轮对话、知识问答、创意写作等能力。当前为模拟响应模式。", self.model)
        except Exception as e:
            return self.build_response(f"【文心一言】你问的是：{user_msg}\n\n文心一言是百度开发的大语言模型，具备多轮对话、知识问答、创意写作等能力。当前为模拟响应模式。\n\n错误信息：{str(e)}", self.model)
    
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        user_msg = messages[-1].get("content", "") if messages else ""
        response = f"【文心一言】你问的是：{user_msg}\n\n文心一言是百度开发的大语言模型，具备多轮对话、知识问答、创意写作等能力。当前为模拟响应模式。\n\n在实际部署中，如果网络可以访问文心一言官网，可以直接模拟网页请求获取真实响应。"
        
        for char in response:
            yield self.build_stream_chunk(char, self.model)
            await asyncio.sleep(0.03)
        yield self.build_stream_chunk("", self.model, finish=True)