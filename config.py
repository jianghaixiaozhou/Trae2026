import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    API_KEYS = {
        "doubao": os.getenv("DOUBAO_API_KEY", ""),
        "baidu": os.getenv("BAIDU_API_KEY", ""),
        "xunfei": os.getenv("XUNFEI_API_KEY", ""),
        "kimi": os.getenv("KIMI_API_KEY", ""),
        "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
    }

    MODELS = {
        "doubao": {
            "id": "doubao",
            "name": "豆包",
            "description": "字节跳动豆包AI",
            "api_url": "https://api.doubao.com/v1/chat/completions",
            "web_url": "https://www.doubao.com",
        },
        "baidu": {
            "id": "baidu",
            "name": "文心一言",
            "description": "百度文心一言",
            "api_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
            "web_url": "https://yiyan.baidu.com",
        },
        "xunfei": {
            "id": "xunfei",
            "name": "讯飞星火",
            "description": "科大讯飞星火认知大模型",
            "api_url": "https://spark-api.xf-yun.com/v3/chat/completions",
            "web_url": "https://xinghuo.xfyun.cn",
        },
        "kimi": {
            "id": "kimi",
            "name": "Kimi",
            "description": "Moonshot AI Kimi",
            "api_url": "https://api.moonshot.cn/v1/chat/completions",
            "web_url": "https://kimi.moonshot.cn",
        },
        "deepseek": {
            "id": "deepseek",
            "name": "DeepSeek",
            "description": "深度求索DeepSeek",
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "web_url": "https://chat.deepseek.com",
        },
    }

    @classmethod
    def get_api_key(cls, model_id: str) -> str:
        return cls.API_KEYS.get(model_id, "")

    @classmethod
    def has_api_key(cls, model_id: str) -> bool:
        return bool(cls.API_KEYS.get(model_id, ""))
