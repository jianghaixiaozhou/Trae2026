from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional, Tuple
import time
import asyncio
import aiohttp

from config import Config

class BaseAdapter(ABC):

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.model_info = Config.MODELS.get(model_id, {})
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT),
                headers=self._get_web_headers()
            )
        return self._session

    async def close_session(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_web_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': self.model_info.get("web_url", ""),
            'Referer': self.model_info.get("web_url", "") + "/",
        }

    def _get_api_headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        api_key = Config.get_api_key(self.model_id)
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        return headers

    @abstractmethod
    async def _call_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        pass

    @abstractmethod
    async def _call_api_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        yield

    @abstractmethod
    async def _call_web(self, messages: List[Dict[str, str]]) -> Optional[str]:
        pass

    @abstractmethod
    async def _call_web_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        yield

    @abstractmethod
    async def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        pass

    @abstractmethod
    async def _mock_response_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        yield

    async def _resolve_source(self) -> str:
        if Config.MOCK_MODE:
            return "mock"
        if Config.has_api_key(self.model_id):
            return "api"
        return "web"

    async def chat(self, messages: List[Dict[str, str]]) -> Tuple[Dict[str, Any], str]:
        source = await self._resolve_source()
        content = None

        if source == "api":
            try:
                content = await self._call_api(messages)
                if content:
                    return self.build_response(content, self.model_id), "api"
            except Exception:
                pass
            source = "web"

        if source == "web":
            try:
                content = await self._call_web(messages)
                if content:
                    return self.build_response(content, self.model_id), "web"
            except Exception:
                pass
            source = "mock"

        content = await self._mock_response(messages)
        return self.build_response(content, self.model_id), "mock"

    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Tuple[Dict[str, Any], str], None]:
        source = await self._resolve_source()

        if source == "api":
            try:
                has_content = False
                async for chunk in self._call_api_stream(messages):
                    has_content = True
                    yield self.build_stream_chunk(chunk, self.model_id), "api"
                if has_content:
                    yield self.build_stream_chunk("", self.model_id, finish=True), "api"
                    return
            except Exception:
                pass
            source = "web"

        if source == "web":
            try:
                has_content = False
                async for chunk in self._call_web_stream(messages):
                    has_content = True
                    yield self.build_stream_chunk(chunk, self.model_id), "web"
                if has_content:
                    yield self.build_stream_chunk("", self.model_id, finish=True), "web"
                    return
            except Exception:
                pass
            source = "mock"

        async for chunk in self._mock_response_stream(messages):
            yield self.build_stream_chunk(chunk, self.model_id), "mock"
        yield self.build_stream_chunk("", self.model_id, finish=True), "mock"

    def build_response(self, content: str, model: str) -> Dict[str, Any]:
        return {
            "id": f"chatcmpl-{int(time.time() * 1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
                "index": 0
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }

    def build_stream_chunk(self, content: str, model: str, finish: bool = False) -> Dict[str, Any]:
        return {
            "id": f"chatcmpl-{int(time.time() * 1000)}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "delta": {"content": content} if content else {},
                "finish_reason": "stop" if finish else None,
                "index": 0
            }]
        }
