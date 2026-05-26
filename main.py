from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adapters import get_adapter, get_model_status
from config import Config

app = FastAPI(title="免费大模型中转服务", description="中转调用免费国产大模型的API服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

SUPPORTED_MODELS = list(Config.MODELS.keys())

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "suggestion": "请稍后重试"
            }
        }
    )

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/v1/models")
async def list_models():
    models = []
    for model_id, info in Config.MODELS.items():
        status = get_model_status(model_id)
        models.append({
            "id": info["id"],
            "name": info["name"],
            "description": info["description"],
            "status": status
        })
    return {"data": models, "object": "list"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if request.model.lower() not in SUPPORTED_MODELS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "UNSUPPORTED_MODEL",
                    "message": f"不支持的模型: {request.model}",
                    "suggestion": f"可用模型: {', '.join(SUPPORTED_MODELS)}"
                }
            }
        )

    adapter = get_adapter(request.model)
    if not adapter:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "UNSUPPORTED_MODEL",
                    "message": f"不支持的模型: {request.model}",
                    "suggestion": f"可用模型: {', '.join(SUPPORTED_MODELS)}"
                }
            }
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    if request.stream:
        async def generate():
            try:
                async for chunk, source in adapter.chat_stream(messages):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_chunk = {
                    "error": {
                        "code": "UPSTREAM_ERROR",
                        "message": str(e),
                        "suggestion": "请稍后重试或切换其他模型"
                    }
                }
                yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"X-Response-Source": "streaming"}
        )
    else:
        try:
            result, source = await adapter.chat(messages)
            return JSONResponse(
                content=result,
                headers={"X-Response-Source": source}
            )
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": {
                        "code": "UPSTREAM_ERROR",
                        "message": f"{request.model}服务暂时不可用: {str(e)}",
                        "suggestion": "请稍后重试或切换其他模型"
                    }
                }
            )

@app.get("/health")
async def health_check():
    return {"status": "ok", "mock_mode": Config.MOCK_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
