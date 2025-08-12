from translate.storage import tmx
from typing import List, Optional
import logging
import re
from lxml import etree
from models.xliff import TmxData

logger = logging.getLogger(__name__)

class TmxProcessorService:
    """TMX文件处理服务"""
    
    @staticmethod
    def process_tmx(file_name: str, content: str) -> List[TmxData]:
        """
        解析TMX内容并提取翻译单元
        
        Args:
            file_name: 文件名
            content: TMX文件内容
            
        Returns:
            TmxData对象列表
        """
        try:
            # 使用translate-toolkit解析TMX
            store = tmx.tmxfile()
            store.parse(content.encode('utf-8'))
            
            data = []
            
            for index, unit in enumerate(store.units):
                if unit.isheader():
                    continue
                
                unit_id = unit.getid()
                if not unit_id:
                    unit_id = str(index + 1)
                
                # 获取源文本和目标文本
                source = unit.source or ""
                target = unit.target or ""
                
                # 获取TMX特有属性
                creator = ""
                changer = ""
                context_id = ""
                
                if hasattr(unit, 'xmlelement') and unit.xmlelement is not None:
                    element = unit.xmlelement
                    creator = element.get('creationid', '')
                    changer = element.get('changeid', '')
                    
                    # 查找context属性
                    props = element.xpath('.//prop[@type="x-context"]')
                    if props:
                        context_id = props[0].text or ""
                
                # 清理标签获得无标签版本
                no_tag_source = TmxProcessorService.clean_tmx_tags(source)
                no_tag_target = TmxProcessorService.clean_tmx_tags(target)
                
                # 尝试获取语言信息
                src_lang = ""
                tgt_lang = ""
                
                if hasattr(unit, 'xmlelement') and unit.xmlelement is not None:
                    tuvs = unit.xmlelement.xpath('.//tuv')
                    if len(tuvs) >= 2:
                        src_lang = tuvs[0].get('xml:lang') or tuvs[0].get('lang') or ""
                        tgt_lang = tuvs[1].get('xml:lang') or tuvs[1].get('lang') or ""
                        src_lang = src_lang.lower()
                        tgt_lang = tgt_lang.lower()
                
                tmx_data = TmxData(
                    id=unit_id,
                    fileName=file_name,
                    segNumber=index + 1,
                    percent=-1,  # TMX通常没有percent属性
                    source=source,
                    target=target,
                    noTagSource=no_tag_source,
                    noTagTarget=no_tag_target,
                    contextId=context_id,
                    creator=creator,
                    changer=changer,
                    srcLang=src_lang,
                    tgtLang=tgt_lang
                )
                
                data.append(tmx_data)
            
            return data
            
        except Exception as e:
            logger.error(f"处理TMX文件失败: {str(e)}")
            raise
    
    @staticmethod
    def validate_tmx(content: str) -> tuple[bool, str, int]:
        """
        验证TMX内容格式
        
        Args:
            content: TMX文件内容
            
        Returns:
            (是否有效, 消息, 单元数量)
        """
        try:
            store = tmx.tmxfile()
            store.parse(content.encode('utf-8'))
            
            # 计算非header单元的数量
            unit_count = sum(1 for unit in store.units if not unit.isheader())
            
            return True, "TMX格式有效", unit_count
        except Exception as e:
            return False, f"TMX格式无效: {str(e)}", 0
    
    @staticmethod
    def clean_tmx_tags(content: str) -> str:
        """
        清理TMX标签，获得纯文本内容
        
        Args:
            content: 含有标签的TMX内容
            
        Returns:
            清理后的纯文本内容
        """
        if not content:
            return ""
        
        # 先解码HTML实体，方便后续处理
        cleaned_content = content
        cleaned_content = cleaned_content.replace('&amp;lt;', '&lt;')
        cleaned_content = cleaned_content.replace('&amp;gt;', '&gt;')
        cleaned_content = cleaned_content.replace('&amp;', '&')
        cleaned_content = cleaned_content.replace('&quot;', '"')
        
        # 步骤1: 处理换行标签
        # <ph>&lt;mq:rxt displaytext="\n" val="\n" /&gt;</ph> 替换为\n
        cleaned_content = re.sub(r'<ph>&lt;mq:rxt[^>]*val="\\n"[^>]*/&gt;</ph>', '\n', cleaned_content)
        
        # <ph>&lt;mq:ch val=" " /&gt;</ph> 直接删除
        cleaned_content = re.sub(r'<ph>&lt;mq:ch val="\s*"\s*/&gt;</ph>', '', cleaned_content)
        
        # 处理直接的<mq:ch val=" " />格式也直接删除
        cleaned_content = re.sub(r'<mq:ch val="\s*"\s*/>', '', cleaned_content)
        
        # 步骤2: 处理带颜色标签
        # 处理bpt/ept包裹的mq:rxt标签
        bpt_ept_pattern = r'<bpt[^>]*>&lt;mq:rxt[^>]*val="&lt;([^&]*)&gt;"[^>]*&gt;</bpt>(.*?)<ept[^>]*>&lt;/mq:rxt[^>]*val="&lt;/([^&]*)&gt;"[^>]*&gt;</ept>'
        
        def replace_bpt_ept(match):
            open_tag = match.group(1)
            content_inner = match.group(2)
            close_tag = match.group(3)
            return f'<{open_tag}>{content_inner}</{close_tag}>'
        
        cleaned_content = re.sub(bpt_ept_pattern, replace_bpt_ept, cleaned_content)
        
        # 处理直接的mq:rxt标签
        direct_rxt_pattern = r'<mq:rxt[^>]*val="&lt;([^&]*)&gt;"[^>]*>(.*?)</mq:rxt[^>]*val="&lt;/([^&]*)&gt;"[^>]*>'
        
        def replace_direct_rxt(match):
            open_tag = match.group(1)
            content_inner = match.group(2)
            close_tag = match.group(3)
            return f'<{open_tag}>{content_inner}</{close_tag}>'
        
        cleaned_content = re.sub(direct_rxt_pattern, replace_direct_rxt, cleaned_content)
        
        # 步骤3: 清理剩余的所有标签
        cleaned_content = re.sub(r'</?(?:bpt|ept|ph|it|mq:[a-z\-]+)[^>]*>', '', cleaned_content)
        
        # 步骤4: 解码剩余的HTML实体
        cleaned_content = cleaned_content.replace('&lt;', '<')
        cleaned_content = cleaned_content.replace('&gt;', '>')
        cleaned_content = cleaned_content.replace('&quot;', '"')
        
        return cleaned_content
    
    @staticmethod
    def replace_tmx_targets(content: str, translations: List[dict]) -> tuple[str, int]:
        """
        替换TMX文件中的target内容
        
        Args:
            content: 原始TMX文件内容
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
            seg_id = str(translation['segNumber'])
            
            # 查找对应的tu元素
            tu_pattern = rf'(<tu[^>]*(?:id=["\']{re.escape(seg_id)}["\']|tuid=["\']{re.escape(seg_id)}["\'])[^>]*>)([\s\S]*?)(</tu>)'
            tu_match = re.search(tu_pattern, updated_content, re.IGNORECASE)
            
            if not tu_match:
                continue
            
            tu_start = tu_match.group(1)
            tu_content = tu_match.group(2)
            tu_end = tu_match.group(3)
            
            # 在tu内容中查找第二个tuv（target）
            tuv_pattern = r'<tuv[^>]*>[\s\S]*?</tuv>'
            tuv_matches = re.findall(tuv_pattern, tu_content, re.IGNORECASE)
            
            if len(tuv_matches) >= 2:
                target_tuv = tuv_matches[1]  # 第二个tuv是target
                
                # 替换target tuv中的seg内容
                seg_pattern = r'(<seg[^>]*>)[\s\S]*?(</seg>)'
                new_target_tuv = re.sub(seg_pattern, rf'\g<1>{new_target_content}\g<2>', target_tuv, flags=re.IGNORECASE)
                
                new_tu_content = tu_content.replace(target_tuv, new_target_tuv)
                
                updated_content = updated_content.replace(
                    tu_match.group(0),
                    tu_start + new_tu_content + tu_end
                )
                
                replacements_count += 1
        
        return updated_content, replacements_count