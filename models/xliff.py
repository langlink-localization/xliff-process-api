from pydantic import BaseModel
from typing import Optional, List, Union

class XliffData(BaseModel):
    """XLIFF数据单元模型"""
    fileName: str
    segNumber: int
    unitId: str  # 添加真实的XLIFF单元ID
    percent: float
    source: str
    target: str
    srcLang: str
    tgtLang: str

class TmxData(BaseModel):
    """TMX数据单元模型"""
    id: Union[int, str]
    fileName: str
    segNumber: int
    percent: float
    source: str
    target: str
    noTagSource: Optional[str] = None
    noTagTarget: Optional[str] = None
    contextId: Optional[str] = None
    creator: Optional[str] = None
    changer: Optional[str] = None
    srcLang: Optional[str] = None
    tgtLang: Optional[str] = None

class FileProcessRequest(BaseModel):
    """文件处理请求模型"""
    fileName: str
    content: str

class XliffProcessResponse(BaseModel):
    """XLIFF处理响应模型"""
    data: List[XliffData]
    success: bool
    message: Optional[str] = None

class TmxProcessResponse(BaseModel):
    """TMX处理响应模型"""
    data: List[TmxData]
    success: bool
    message: Optional[str] = None

class ValidationResponse(BaseModel):
    """验证响应模型"""
    valid: bool
    message: str
    unit_count: int

class TranslationReplacementData(BaseModel):
    """译文替换数据模型"""
    segNumber: int
    unitId: Optional[str] = None  # 添加XLIFF单元ID支持
    aiResult: Optional[str] = None
    mtResult: Optional[str] = None

class FileReplacementRequest(BaseModel):
    """文件译文替换请求模型"""
    fileName: str
    content: str
    translations: List[TranslationReplacementData]

class FileReplacementResponse(BaseModel):
    """文件译文替换响应模型"""
    content: str
    success: bool
    message: Optional[str] = None
    replacements_count: int