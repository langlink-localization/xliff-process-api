from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

class AccessKeyAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(AccessKeyAuth, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[str]:
        # 检查是否是排除的路径
        if request.url.path in settings.EXCLUDE_PATHS:
            return None
            
        # 首先尝试从 Authorization header 获取
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme"
                )
            if credentials.credentials != settings.ACCESS_KEY:
                logger.warning(f"Invalid access key attempted from {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid access key"
                )
            return credentials.credentials
        
        # 如果没有 Authorization header，尝试从查询参数获取
        access_key = request.query_params.get("access_key")
        if access_key:
            if access_key != settings.ACCESS_KEY:
                logger.warning(f"Invalid access key attempted from {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid access key"
                )
            return access_key
        
        # 如果都没有提供
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 创建认证实例
auth = AccessKeyAuth()

# 中间件函数，用于全局验证
async def verify_access_key(request: Request, call_next):
    # 检查是否是排除的路径
    if request.url.path in settings.EXCLUDE_PATHS:
        response = await call_next(request)
        return response
    
    # 获取access_key
    access_key = None
    
    # 从 Authorization header 获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_key = auth_header[7:]
    
    # 从查询参数获取
    if not access_key:
        access_key = request.query_params.get("access_key")
    
    # 从表单数据获取（用于文件上传）
    if not access_key and request.method == "POST":
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            # 对于文件上传，我们需要特殊处理
            # 这里我们暂时跳过，让各个路由处理
            pass
    
    # 验证 access_key
    if not access_key:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access key required"
        )
    
    if access_key != settings.ACCESS_KEY:
        logger.warning(f"Invalid access key attempted from {request.client.host}")
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access key"
        )
    
    response = await call_next(request)
    return response