from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import xliff, tmx, file_replacement
import uvicorn
import logging
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("XLIFF Process API Server 启动中...")
    yield
    # 关闭时执行
    logger.info("XLIFF Process API Server 关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="XLIFF Process API Server",
    description="基于Translate Toolkit的XLIFF处理API服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],  # 常见前端开发端口
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(xliff.router)
app.include_router(tmx.router)
app.include_router(file_replacement.router)

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "XLIFF Process API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "xliff-process-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )