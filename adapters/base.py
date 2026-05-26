from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator

class BaseAdapter(ABC):
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        pass
    
    def build_response(self, content: str, model: str) -> Dict[str, Any]:
        return {
            "id": f"chatcmpl-{id(self)}",
            "object": "chat.completion",
            "created": 0,
            "model": model,
            "choices": [{
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
                "index": 0
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    def build_stream_chunk(self, content: str, model: str, finish: bool = False) -> Dict[str, Any]:
        return {
            "id": f"chatcmpl-{id(self)}",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": model,
            "choices": [{
                "delta": {"content": content} if content else {},
                "finish_reason": "stop" if finish else None,
                "index": 0
            }]
        }