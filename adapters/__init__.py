from .doubao import DoubaoAdapter
from .baidu import BaiduAdapter
from .xunfei import XunfeiAdapter
from .kimi import KimiAdapter
from .deepseek import DeepSeekAdapter
from config import Config

_adapters = {
    "doubao": DoubaoAdapter(),
    "baidu": BaiduAdapter(),
    "xunfei": XunfeiAdapter(),
    "kimi": KimiAdapter(),
    "deepseek": DeepSeekAdapter(),
}

def get_adapter(model_name: str):
    return _adapters.get(model_name.lower())

def list_adapters():
    return list(_adapters.keys())

def get_model_status(model_id: str) -> str:
    if Config.MOCK_MODE:
        return "mock_only"
    if Config.has_api_key(model_id):
        return "available"
    return "unavailable"
