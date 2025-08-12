from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import List
from models.xliff import (
    FileProcessRequest, 
    XliffProcessResponse, 
    XliffData,
    ValidationResponse
)
from services.xliff_processor import XliffProcessorService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/xliff", tags=["XLIFF Processing"])
xliff_service = XliffProcessorService()

@router.post("/process", response_model=XliffProcessResponse)
async def process_xliff(request: FileProcessRequest):
    """
    处理XLIFF内容
    
    接收XLIFF文件内容，返回解析后的翻译单元数据
    """
    try:
        data = xliff_service.process_xliff(
            file_name=request.fileName,
            content=request.content
        )
        return XliffProcessResponse(
            data=data,
            success=True,
            message=f"成功处理 {len(data)} 个翻译单元"
        )
    except Exception as e:
        logger.error(f"处理XLIFF失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload", response_model=XliffProcessResponse)
async def upload_xliff(file: UploadFile = File(...)):
    """
    上传并处理XLIFF文件
    
    接收XLIFF文件上传，返回解析后的翻译单元数据
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xliff', '.xlf', '.xliff2', '.xml')):
            raise HTTPException(
                status_code=400,
                detail="不支持的文件格式，请上传XLIFF文件"
            )
        
        # 读取文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 处理XLIFF
        data = xliff_service.process_xliff(
            file_name=file.filename,
            content=content_str
        )
        
        return XliffProcessResponse(
            data=data,
            success=True,
            message=f"成功处理 {len(data)} 个翻译单元"
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="文件编码错误，请确保文件为UTF-8编码"
        )
    except Exception as e:
        logger.error(f"上传处理XLIFF失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/process-with-tags", response_model=XliffProcessResponse)
async def process_xliff_with_tags(request: FileProcessRequest):
    """
    处理XLIFF内容（保留内部标签）
    
    专门用于AI翻译的XLIFF处理器，保留内部标记，使用更精确的方法避免DOM解析器添加命名空间
    """
    try:
        data = xliff_service.process_xliff_with_tags(
            file_name=request.fileName,
            content=request.content
        )
        return XliffProcessResponse(
            data=data,
            success=True,
            message=f"成功处理带标签的 {len(data)} 个翻译单元"
        )
    except Exception as e:
        logger.error(f"处理带标签的XLIFF失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResponse)
async def validate_xliff(content: str = Body(..., embed=True)):
    """
    验证XLIFF内容格式
    
    检查提供的内容是否为有效的XLIFF格式
    """
    try:
        valid, message, unit_count = xliff_service.validate_xliff(content)
        return ValidationResponse(
            valid=valid,
            message=message,
            unit_count=unit_count
        )
    except Exception as e:
        logger.error(f"验证XLIFF失败: {str(e)}")
        return ValidationResponse(
            valid=False,
            message=f"验证过程出错: {str(e)}",
            unit_count=0
        )

@router.get("/health")
async def health_check():
    """
    XLIFF处理服务健康检查
    """
    return {
        "status": "healthy",
        "service": "xliff-processor"
    }