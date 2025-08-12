from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import List
from models.xliff import (
    FileProcessRequest,
    TmxProcessResponse, 
    TmxData,
    ValidationResponse
)
from services.tmx_processor import TmxProcessorService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tmx", tags=["TMX Processing"])
tmx_service = TmxProcessorService()

@router.post("/process", response_model=TmxProcessResponse)
async def process_tmx(request: FileProcessRequest):
    """
    处理TMX内容
    
    接收TMX文件内容，返回解析后的翻译单元数据
    """
    try:
        data = tmx_service.process_tmx(
            file_name=request.fileName,
            content=request.content
        )
        return TmxProcessResponse(
            data=data,
            success=True,
            message=f"成功处理 {len(data)} 个TMX翻译单元"
        )
    except Exception as e:
        logger.error(f"处理TMX失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload", response_model=TmxProcessResponse)
async def upload_tmx(file: UploadFile = File(...)):
    """
    上传并处理TMX文件
    
    接收TMX文件上传，返回解析后的翻译单元数据
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.tmx', '.xml')):
            raise HTTPException(
                status_code=400,
                detail="不支持的文件格式，请上传TMX文件"
            )
        
        # 读取文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 处理TMX
        data = tmx_service.process_tmx(
            file_name=file.filename,
            content=content_str
        )
        
        return TmxProcessResponse(
            data=data,
            success=True,
            message=f"成功处理 {len(data)} 个TMX翻译单元"
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="文件编码错误，请确保文件为UTF-8编码"
        )
    except Exception as e:
        logger.error(f"上传处理TMX失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResponse)
async def validate_tmx(content: str = Body(..., embed=True)):
    """
    验证TMX内容格式
    
    检查提供的内容是否为有效的TMX格式
    """
    try:
        valid, message, unit_count = tmx_service.validate_tmx(content)
        return ValidationResponse(
            valid=valid,
            message=message,
            unit_count=unit_count
        )
    except Exception as e:
        logger.error(f"验证TMX失败: {str(e)}")
        return ValidationResponse(
            valid=False,
            message=f"验证过程出错: {str(e)}",
            unit_count=0
        )

@router.get("/health")
async def health_check():
    """
    TMX处理服务健康检查
    """
    return {
        "status": "healthy",
        "service": "tmx-processor"
    }