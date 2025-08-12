from fastapi import APIRouter, HTTPException
from models.xliff import (
    FileReplacementRequest,
    FileReplacementResponse
)
from services.xliff_processor import XliffProcessorService
from services.tmx_processor import TmxProcessorService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/replacement", tags=["File Translation Replacement"])

@router.post("/xliff", response_model=FileReplacementResponse)
async def replace_xliff_translations(request: FileReplacementRequest):
    """
    替换XLIFF文件中的翻译内容
    
    根据提供的翻译数据，更新XLIFF文件中对应的target元素
    """
    try:
        # 转换翻译数据格式
        translations = []
        for trans in request.translations:
            translations.append({
                'segNumber': trans.segNumber,
                'unitId': trans.unitId,  # 传递unitId
                'aiResult': trans.aiResult,
                'mtResult': trans.mtResult
            })
        
        # 执行替换操作
        updated_content, replacements_count = XliffProcessorService.replace_xliff_targets(
            content=request.content,
            translations=translations
        )
        
        return FileReplacementResponse(
            content=updated_content,
            success=True,
            message=f"成功替换 {replacements_count} 个翻译单元",
            replacements_count=replacements_count
        )
        
    except Exception as e:
        logger.error(f"XLIFF翻译替换失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tmx", response_model=FileReplacementResponse)
async def replace_tmx_translations(request: FileReplacementRequest):
    """
    替换TMX文件中的翻译内容
    
    根据提供的翻译数据，更新TMX文件中对应的target段落
    """
    try:
        # 转换翻译数据格式
        translations = []
        for trans in request.translations:
            translations.append({
                'segNumber': trans.segNumber,
                'unitId': trans.unitId,  # 传递unitId
                'aiResult': trans.aiResult,
                'mtResult': trans.mtResult
            })
        
        # 执行替换操作
        updated_content, replacements_count = TmxProcessorService.replace_tmx_targets(
            content=request.content,
            translations=translations
        )
        
        return FileReplacementResponse(
            content=updated_content,
            success=True,
            message=f"成功替换 {replacements_count} 个翻译单元",
            replacements_count=replacements_count
        )
        
    except Exception as e:
        logger.error(f"TMX翻译替换失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auto", response_model=FileReplacementResponse)
async def auto_replace_translations(request: FileReplacementRequest):
    """
    自动检测文件类型并替换翻译内容
    
    根据文件内容自动判断是XLIFF还是TMX，然后执行相应的替换操作
    """
    try:
        # 简单的文件类型检测
        content_lower = request.content.lower()
        
        if '<xliff' in content_lower or '<trans-unit' in content_lower or '<unit' in content_lower:
            # 处理XLIFF文件
            translations = []
            for trans in request.translations:
                translations.append({
                    'segNumber': trans.segNumber,
                    'unitId': trans.unitId,  # 传递unitId
                    'aiResult': trans.aiResult,
                    'mtResult': trans.mtResult
                })
            
            updated_content, replacements_count = XliffProcessorService.replace_xliff_targets(
                content=request.content,
                translations=translations
            )
            
            file_type = "XLIFF"
            
        elif '<tmx' in content_lower or '<tu' in content_lower:
            # 处理TMX文件
            translations = []
            for trans in request.translations:
                translations.append({
                    'segNumber': trans.segNumber,
                    'unitId': trans.unitId,  # 传递unitId
                    'aiResult': trans.aiResult,
                    'mtResult': trans.mtResult
                })
            
            updated_content, replacements_count = TmxProcessorService.replace_tmx_targets(
                content=request.content,
                translations=translations
            )
            
            file_type = "TMX"
            
        else:
            raise HTTPException(
                status_code=400,
                detail="无法识别文件类型，请确保文件为有效的XLIFF或TMX格式"
            )
        
        return FileReplacementResponse(
            content=updated_content,
            success=True,
            message=f"成功自动识别为{file_type}文件并替换 {replacements_count} 个翻译单元",
            replacements_count=replacements_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"自动翻译替换失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check():
    """
    文件替换服务健康检查
    """
    return {
        "status": "healthy",
        "service": "file-replacement"
    }