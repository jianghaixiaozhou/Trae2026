from .doubao import DoubaoAdapter
from .baidu import BaiduAdapter
from .xunfei import XunfeiAdapter
from .kimi import KimiAdapter
from .deepseek import DeepSeekAdapter

_adapters = {
    "doubao": DoubaoAdapter(),
    "baidu": BaiduAdapter(),
    "xunfei": XunfeiAdapter(),
    "kimi": KimiAdapter(),
    "deepseek": DeepSeekAdapter()
}

def get_adapter(model_name: str):
    return _adapters.get(model_name.lower())

def list_adapters():
    return list(_adapters.keys())