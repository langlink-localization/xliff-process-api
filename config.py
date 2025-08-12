import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ACCESS_KEY = os.getenv("API_ACCESS_KEY", "your-secure-access-key-here")
    API_TITLE = "XLIFF Process API Server"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "基于Translate Toolkit的XLIFF处理API服务"
    
    # CORS设置
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000").split(",")
    
    # 如果没有通过环境变量配置，使用默认值
    if not CORS_ORIGINS or CORS_ORIGINS == [""]:
        CORS_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:3000",
            "https://langlink-localization.github.io"  # 添加生产环境域名
        ]
    
    # 服务器设置
    HOST = "0.0.0.0"
    PORT = 8848
    
    # 不需要认证的端点
    EXCLUDE_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health"
    ]

settings = Settings()