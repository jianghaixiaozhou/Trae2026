import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from .base import BaseAdapter

class BaiduAdapter(BaseAdapter):

    def __init__(self):
        super().__init__("baidu")

    async def _call_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        session = await self.get_session()
        async with session.post(
            self.model_info["api_url"],
            json={"messages": messages, "stream": False},
            headers=self._get_api_headers()
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("result") or result.get("choices", [{}])[0].get("message", {}).get("content")
        return None

    async def _call_api_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        session = await self.get_session()
        async with session.post(
            self.model_info["api_url"],
            json={"messages": messages, "stream": True},
            headers=self._get_api_headers()
        ) as resp:
            if resp.status == 200:
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        try:
                            chunk = json.loads(data)
                            content = chunk.get("result", "") or chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except:
                            pass
            else:
                raise Exception(f"API returned {resp.status}")

    async def _call_web(self, messages: List[Dict[str, str]]) -> Optional[str]:
        return None

    async def _call_web_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        return
        yield

    async def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        user_msg = messages[-1].get("content", "") if messages else ""
        return f"[模拟响应] 你好！我是文心一言。你问的是：「{user_msg}」\n\n文心一言是百度开发的大语言模型，具备多轮对话、知识问答、创意写作等能力。当前为模拟响应模式，配置 API Key 后可获得真实回复。"

    async def _mock_response_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        response = await self._mock_response(messages)
        for char in response:
            yield char
            await asyncio.sleep(0.02)
