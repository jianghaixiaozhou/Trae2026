import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    DOUBAN_API_URL = "https://api.doubao.com"
    BAIDU_API_URL = "https://aip.baidubce.com"
    XUNFEI_API_URL = "https://spark-api.xf-yun.com"
    
    SUPPORTED_MODELS = [
        "doubao",
        "baidu",
        "xunfei",
        "kimi",
        "deepseek"
    ]