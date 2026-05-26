from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import random

from adapters import get_adapter

app = FastAPI(title="免费大模型中转服务", description="中转调用免费国产大模型的API服务")

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "doubao"
    messages: List[ChatMessage]
    stream: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/v1/models")
async def list_models():
    models = [
        {"id": "doubao", "name": "豆包", "description": "字节跳动豆包AI"},
        {"id": "baidu", "name": "文心一言", "description": "百度文心一言"},
        {"id": "xunfei", "name": "讯飞星火", "description": "科大讯飞星火认知大模型"},
        {"id": "kimi", "name": "Kimi", "description": "Moonshot AI Kimi"},
        {"id": "deepseek", "name": "DeepSeek", "description": "深度求索DeepSeek"}
    ]
    return {"data": models, "object": "list"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    adapter = get_adapter(request.model)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"不支持的模型: {request.model}")
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    if request.stream:
        async def generate():
            async for chunk in adapter.chat_stream(messages):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        result = await adapter.chat(messages)
        return result

@app.websocket("/ws/chat")
async def websocket_chat(websocket: Request):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            model = payload.get("model", "doubao")
            messages = payload.get("messages", [])
            
            adapter = get_adapter(model)
            if not adapter:
                await websocket.send_json({"error": f"不支持的模型: {model}"})
                continue
            
            async for chunk in adapter.chat_stream(messages):
                await websocket.send_json(chunk)
            await websocket.send_json({"finish": True})
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    from config import Config
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
