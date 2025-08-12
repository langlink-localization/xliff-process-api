from translate.storage import xliff
from typing import List, Dict, Any
import logging
import re
from lxml import etree
from models.xliff import XliffData

logger = logging.getLogger(__name__)

class XliffProcessorService:
    """XLIFF文件处理服务"""
    
    @staticmethod
    def process_xliff(file_name: str, content: str) -> List[XliffData]:
        """
        解析XLIFF内容并提取翻译单元
        
        Args:
            file_name: 文件名
            content: XLIFF文件内容
            
        Returns:
            XliffData对象列表
        """
        try:
            # 使用translate-toolkit解析XLIFF
            store = xliff.xlifffile()
            store.parse(content.encode('utf-8'))
            
            data = []
            
            # 获取文件级别的语言属性
            file_src_lang = ""
            file_tgt_lang = ""
            if hasattr(store, 'document') and store.document is not None:
                root = store.document.getroot()
                if root is not None:
                    # 尝试从根元素获取
                    file_node = root.find('.//{urn:oasis:names:tc:xliff:document:1.2}file')
                    if file_node is None:
                        file_node = root.find('.//file')
                    
                    if file_node is not None:
                        file_src_lang = (file_node.get('source-language') or "").lower()
                        file_tgt_lang = (file_node.get('target-language') or "").lower()
            
            for index, unit in enumerate(store.units):
                # 跳过header单元
                if unit.isheader():
                    continue
                
                # 提取单元属性
                unit_full_id = unit.getid()
                if not unit_full_id:
                    continue
                
                # 提取真实的单元ID（去掉文件路径部分）
                if '\x04' in unit_full_id:
                    unit_id = unit_full_id.split('\x04')[-1]  # 取最后一部分作为真实ID
                else:
                    unit_id = unit_full_id
                
                # 获取翻译百分比（支持多种属性名）
                percent = -1
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    percent_value = (
                        element.get('percent') or 
                        element.get('mq:percent') or 
                        element.get('{urn:oasis:names:tc:xliff:document:2.0}percent') or
                        element.get('{urn:oasis:names:tc:xliff:document:1.2}percent')
                    )
                    if percent_value:
                        try:
                            percent = float(percent_value)
                        except ValueError:
                            percent = -1
                
                # 获取源语言和目标语言 - 优先从单元获取，否则使用文件级别的
                src_lang = ""
                tgt_lang = ""
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    src_lang = (element.get('source-language') or "").lower()
                    tgt_lang = (element.get('target-language') or "").lower()
                
                # 如果单元级别没有语言信息，使用文件级别的
                if not src_lang:
                    src_lang = file_src_lang
                if not tgt_lang:
                    tgt_lang = file_tgt_lang
                
                # 构建数据对象
                xliff_data = XliffData(
                    fileName=file_name,
                    segNumber=index + 1,
                    unitId=unit_id,  # 保存真实的单元ID
                    percent=percent,
                    source=unit.source or "",
                    target=unit.target or "",
                    srcLang=src_lang,
                    tgtLang=tgt_lang
                )
                
                data.append(xliff_data)
            
            return data
            
        except Exception as e:
            logger.error(f"处理XLIFF文件失败: {str(e)}")
            raise
    
    @staticmethod
    def validate_xliff(content: str) -> tuple[bool, str, int]:
        """
        验证XLIFF内容格式
        
        Args:
            content: XLIFF文件内容
            
        Returns:
            (是否有效, 消息, 单元数量)
        """
        try:
            store = xliff.xlifffile()
            store.parse(content.encode('utf-8'))
            
            # 计算非header单元的数量
            unit_count = sum(1 for unit in store.units if not unit.isheader())
            
            return True, "XLIFF格式有效", unit_count
        except Exception as e:
            return False, f"XLIFF格式无效: {str(e)}", 0
    
    @staticmethod
    def process_xliff_with_tags(file_name: str, content: str) -> List[XliffData]:
        """
        专门用于AI翻译的XLIFF处理器，保留内部标记
        使用更精确的方法避免DOM解析器添加命名空间
        
        Args:
            file_name: 文件名
            content: XLIFF文件内容
            
        Returns:
            XliffData对象列表，保留原始标签
        """
        try:
            # 先使用translate-toolkit获取基本结构
            store = xliff.xlifffile()
            store.parse(content.encode('utf-8'))
            
            data = []
            unit_index = 0
            
            for unit in store.units:
                if unit.isheader():
                    continue
                
                unit_full_id = unit.getid()
                if not unit_full_id:
                    continue
                
                # 提取真实的单元ID（去掉文件路径部分）
                if '\x04' in unit_full_id:
                    unit_id = unit_full_id.split('\x04')[-1]  # 取最后一部分作为真实ID
                else:
                    unit_id = unit_full_id
                
                unit_index += 1
                
                # 获取百分比属性
                percent = -1
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    percent_value = (
                        element.get('percent') or 
                        element.get('mq:percent') or 
                        element.get('{urn:oasis:names:tc:xliff:document:2.0}percent') or
                        element.get('{urn:oasis:names:tc:xliff:document:1.2}percent')
                    )
                    if percent_value:
                        try:
                            percent = float(percent_value)
                        except ValueError:
                            percent = -1
                
                # 使用正则表达式从原始XML中提取内容，避免DOM解析器修改
                source = XliffProcessorService._extract_element_content(content, 'source', unit_id)
                target = XliffProcessorService._extract_element_content(content, 'target', unit_id)
                
                # 如果正则提取失败，fallback到translate-toolkit方法
                if not source:
                    source = unit.source or ""
                if not target:
                    target = unit.target or ""
                
                # 获取语言信息
                src_lang = ""
                tgt_lang = ""
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    src_lang = (element.get('source-language') or "").lower()
                    tgt_lang = (element.get('target-language') or "").lower()
                
                # 如果单元级别没有语言信息，尝试从文件级别获取
                if not src_lang or not tgt_lang:
                    file_src_lang, file_tgt_lang = XliffProcessorService._get_file_languages(content)
                    if not src_lang:
                        src_lang = file_src_lang
                    if not tgt_lang:
                        tgt_lang = file_tgt_lang
                
                xliff_data = XliffData(
                    fileName=file_name,
                    segNumber=unit_index,
                    unitId=unit_id,  # 保存真实的单元ID
                    percent=percent,
                    source=source,
                    target=target,
                    srcLang=src_lang,
                    tgtLang=tgt_lang
                )
                
                data.append(xliff_data)
            
            return data
            
        except Exception as e:
            logger.error(f"处理带标签的XLIFF文件失败: {str(e)}")
            raise
    
    @staticmethod
    def _extract_element_content(xml_content: str, element_name: str, unit_id: str) -> str:
        """
        从原始XML内容中提取指定元素的内容，保持原始格式
        
        Args:
            xml_content: 原始XML内容
            element_name: 元素名称（source或target）
            unit_id: 单元ID
            
        Returns:
            元素内容
        """
        try:
            # 构建匹配特定trans-unit或unit中的source/target元素的正则表达式
            unit_pattern = rf'<(?:trans-unit|unit)[^>]*id=["\']{re.escape(unit_id)}["\'][^>]*>([\s\S]*?)</(?:trans-unit|unit)>'
            
            unit_match = re.search(unit_pattern, xml_content, re.IGNORECASE)
            if not unit_match:
                return ""
            
            unit_content = unit_match.group(1)
            
            # 在unit内容中查找source或target元素
            element_pattern = rf'<{element_name}[^>]*>([\s\S]*?)</{element_name}>'
            
            element_match = re.search(element_pattern, unit_content, re.IGNORECASE)
            if not element_match:
                return ""
            
            content = element_match.group(1).strip()
            
            # 解码HTML实体
            content = XliffProcessorService._decode_html_entities(content)
            
            return content
        except Exception as e:
            logger.error(f"提取{element_name}内容失败: {str(e)}")
            return ""
    
    @staticmethod
    def _get_file_languages(xml_content: str) -> tuple[str, str]:
        """
        从文件级别获取语言信息
        
        Args:
            xml_content: XML内容
            
        Returns:
            (源语言, 目标语言)
        """
        try:
            # 查找file元素的语言属性
            file_pattern = r'<file[^>]*source-language=["\'"]([^"\']*)["\'][^>]*target-language=["\'"]([^"\']*)["\'][^>]*>'
            match = re.search(file_pattern, xml_content, re.IGNORECASE)
            if match:
                return match.group(1).lower(), match.group(2).lower()
            
            # 尝试另一种属性顺序
            file_pattern2 = r'<file[^>]*target-language=["\'"]([^"\']*)["\'][^>]*source-language=["\'"]([^"\']*)["\'][^>]*>'
            match2 = re.search(file_pattern2, xml_content, re.IGNORECASE)
            if match2:
                return match2.group(2).lower(), match2.group(1).lower()
            
            return "", ""
        except Exception:
            return "", ""
    
    @staticmethod
    def _decode_html_entities(text: str) -> str:
        """
        解码HTML实体
        
        Args:
            text: 包含HTML实体的文本
            
        Returns:
            解码后的文本
        """
        # 常见HTML实体解码
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        
        return text
    
    @staticmethod
    def replace_xliff_targets(content: str, translations: List[dict]) -> tuple[str, int]:
        """
        使用字符串替换方式更新XLIFF文件的target内容
        保持原始标记格式不变
        
        Args:
            content: 原始XLIFF文件内容
            translations: 翻译数据列表，包含segNumber, aiResult, mtResult
            
        Returns:
            (更新后的内容, 替换数量)
        """
        updated_content = content
        replacements_count = 0
        
        for translation in translations:
            if not translation.get('aiResult') and not translation.get('mtResult'):
                continue
            
            new_target_content = translation.get('aiResult') or translation.get('mtResult') or ''
            # 优先使用unitId，如果没有则fallback到segNumber（向后兼容）
            unit_id = translation.get('unitId') or str(translation['segNumber'])
            
            # 查找对应的trans-unit或unit
            unit_pattern = rf'(<(?:trans-unit|unit)[^>]*id=["\']{re.escape(unit_id)}["\'][^>]*>)([\s\S]*?)(</(?:trans-unit|unit)>)'
            unit_match = re.search(unit_pattern, updated_content, re.IGNORECASE)
            
            if not unit_match:
                continue
            
            unit_start = unit_match.group(1)
            unit_content = unit_match.group(2)
            unit_end = unit_match.group(3)
            
            # 在unit内容中查找并替换target
            target_pattern = r'<target[^>]*>[\s\S]*?</target>'
            target_match = re.search(target_pattern, unit_content, re.IGNORECASE)
            
            if target_match:
                # 如果已有target，替换其内容
                existing_target = target_match.group(0)
                
                # 提取target的属性
                target_attr_pattern = r'<target([^>]*?)>'
                target_attr_match = re.search(target_attr_pattern, existing_target, re.IGNORECASE)
                target_attributes = target_attr_match.group(1) if target_attr_match else ''
                
                new_target = f'<target{target_attributes}>{new_target_content}</target>'
                new_unit_content = unit_content.replace(existing_target, new_target)
                
                updated_content = updated_content.replace(
                    unit_match.group(0),
                    unit_start + new_unit_content + unit_end
                )
                
                replacements_count += 1
            else:
                # 如果没有target，创建新的target
                source_pattern = r'(<source[^>]*>[\s\S]*?</source>)'
                source_match = re.search(source_pattern, unit_content, re.IGNORECASE)
                
                if source_match:
                    new_target = f'\n        <target>{new_target_content}</target>'
                    new_unit_content = unit_content.replace(
                        source_match.group(0),
                        source_match.group(0) + new_target
                    )
                    
                    updated_content = updated_content.replace(
                        unit_match.group(0),
                        unit_start + new_unit_content + unit_end
                    )
                    
                    replacements_count += 1
        
        return updated_content, replacements_count