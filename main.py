from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import xliff, tmx, file_replacement
from config import settings
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
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 添加认证中间件
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 检查是否是排除的路径
    if request.url.path in settings.EXCLUDE_PATHS:
        response = await call_next(request)
        return response
    
    # 获取access_key
    access_key = None
    
    # 从 X-Access-Key header 获取 (优先)
    access_key = request.headers.get("X-Access-Key")
    
    # 从 Authorization header 获取 (fallback)
    if not access_key:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_key = auth_header[7:]
    
    # 从查询参数获取 (最后选择)
    if not access_key:
        access_key = request.query_params.get("access_key")
    
    # 验证 access_key
    if not access_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access key required"}
        )
    
    if access_key != settings.ACCESS_KEY:
        logger.warning(f"Invalid access key attempted from {request.client.host}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid access key"}
        )
    
    response = await call_next(request)
    return response

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
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )