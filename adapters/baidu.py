import asyncio
import aiohttp
import json
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseAdapter

class BaiduAdapter(BaseAdapter):
    
    def __init__(self):
        self.model = "baidu"
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        session = await self._get_session()
        try:
            data = {
                "model": "ERNIE-Bot",
                "messages": messages,
                "stream": False
            }
            
            async with session.post(
                "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("result", "")
                    return self.build_response(content, self.model)
                else:
                    return self.build_response("文心一言服务暂时不可用，请稍后重试", self.model)
        except Exception as e:
            return self.build_response(f"请求失败: {str(e)}", self.model)
    
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        session = await self._get_session()
        try:
            data = {
                "model": "ERNIE-Bot",
                "messages": messages,
                "stream": True
            }
            
            async with session.post(
                "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            try:
                                chunk = json.loads(line[6:])
                                content = chunk.get("result", "")
                                if content:
                                    yield self.build_stream_chunk(content, self.model)
                            except:
                                pass
                    yield self.build_stream_chunk("", self.model, finish=True)
                else:
                    yield self.build_stream_chunk("文心一言服务暂时不可用，请稍后重试", self.model)
                    yield self.build_stream_chunk("", self.model, finish=True)
        except Exception as e:
            yield self.build_stream_chunk(f"请求失败: {str(e)}", self.model)
            yield self.build_stream_chunk("", self.model, finish=True)