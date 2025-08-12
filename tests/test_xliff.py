import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.xliff_processor import XliffProcessorService
from services.tmx_processor import TmxProcessorService

client = TestClient(app)

# 测试用XLIFF内容
SAMPLE_XLIFF = """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="zh" datatype="plaintext">
    <body>
      <trans-unit id="1" percent="100">
        <source>Hello World</source>
        <target>你好世界</target>
      </trans-unit>
      <trans-unit id="2" percent="50">
        <source>Welcome to the application</source>
        <target>欢迎使用应用程序</target>
      </trans-unit>
      <trans-unit id="3">
        <source>Exit</source>
        <target></target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

# 测试用TMX内容
SAMPLE_TMX = """<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header>
    <prop type="x-filename">test.tmx</prop>
  </header>
  <body>
    <tu tuid="1" creationid="user1" changeid="user2">
      <prop type="x-context">context1</prop>
      <tuv xml:lang="en">
        <seg>Hello World</seg>
      </tuv>
      <tuv xml:lang="zh">
        <seg>你好世界</seg>
      </tuv>
    </tu>
    <tu tuid="2">
      <tuv xml:lang="en">
        <seg>Welcome to the application</seg>
      </tuv>
      <tuv xml:lang="zh">
        <seg>欢迎使用应用程序</seg>
      </tuv>
    </tu>
    <tu tuid="3">
      <tuv xml:lang="en">
        <seg>Exit</seg>
      </tuv>
      <tuv xml:lang="zh">
        <seg></seg>
      </tuv>
    </tu>
  </body>
</tmx>"""

# 带标签的XLIFF内容
XLIFF_WITH_TAGS = """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2">
  <file source-language="en" target-language="zh">
    <body>
      <trans-unit id="1" percent="100">
        <source>Click <g id="1">here</g> to continue</source>
        <target>点击<g id="1">这里</g>继续</target>
      </trans-unit>
      <trans-unit id="2">
        <source>The <ph id="ph1">&lt;b&gt;</ph>bold<ph id="ph2">&lt;/b&gt;</ph> text</source>
        <target></target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

def test_process_xliff_service():
    """测试XLIFF处理服务"""
    service = XliffProcessorService()
    
    result = service.process_xliff("test.xliff", SAMPLE_XLIFF)
    
    assert len(result) == 3
    assert result[0].source == "Hello World"
    assert result[0].target == "你好世界"
    assert result[0].percent == 100
    assert result[0].srcLang == "en"
    assert result[0].tgtLang == "zh"
    
    assert result[1].source == "Welcome to the application"
    assert result[1].percent == 50
    
    assert result[2].source == "Exit"
    assert result[2].target == ""
    assert result[2].percent == -1

def test_validate_xliff():
    """测试XLIFF验证功能"""
    service = XliffProcessorService()
    
    # 测试有效的XLIFF
    valid, message, count = service.validate_xliff(SAMPLE_XLIFF)
    assert valid is True
    assert "有效" in message
    assert count == 3
    
    # 测试无效的XLIFF
    invalid_xliff = "<?xml version='1.0'?><invalid>Not XLIFF</invalid>"
    valid, message, count = service.validate_xliff(invalid_xliff)
    assert valid is False
    assert "无效" in message
    assert count == 0

def test_api_process_endpoint():
    """测试API处理端点"""
    response = client.post(
        "/api/xliff/process",
        json={
            "fileName": "test.xliff",
            "content": SAMPLE_XLIFF
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["data"][0]["source"] == "Hello World"
    assert data["data"][0]["target"] == "你好世界"

def test_api_validate_endpoint():
    """测试API验证端点"""
    response = client.post(
        "/api/xliff/validate",
        json={"content": SAMPLE_XLIFF}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["unit_count"] == 3

def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "1.0.0"

# TMX测试用例
def test_process_tmx_service():
    """测试TMX处理服务"""
    service = TmxProcessorService()
    
    result = service.process_tmx("test.tmx", SAMPLE_TMX)
    
    assert len(result) == 3
    assert result[0].source == "Hello World"
    assert result[0].target == "你好世界"
    assert result[0].contextId == "context1"
    assert result[0].creator == "user1"
    assert result[0].changer == "user2"
    assert result[0].srcLang == "en"
    assert result[0].tgtLang == "zh"
    
    assert result[1].source == "Welcome to the application"
    assert result[2].source == "Exit"
    assert result[2].target == ""

def test_validate_tmx():
    """测试TMX验证功能"""
    service = TmxProcessorService()
    
    # 测试有效的TMX
    valid, message, count = service.validate_tmx(SAMPLE_TMX)
    assert valid is True
    assert "有效" in message
    assert count == 3
    
    # 测试无效的TMX
    invalid_tmx = "<?xml version='1.0'?><invalid>Not TMX</invalid>"
    valid, message, count = service.validate_tmx(invalid_tmx)
    assert valid is False
    assert "无效" in message
    assert count == 0

def test_api_process_tmx_endpoint():
    """测试TMX处理API端点"""
    response = client.post(
        "/api/tmx/process",
        json={
            "fileName": "test.tmx",
            "content": SAMPLE_TMX
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["data"][0]["source"] == "Hello World"
    assert data["data"][0]["target"] == "你好世界"

def test_api_validate_tmx_endpoint():
    """测试TMX验证API端点"""
    response = client.post(
        "/api/tmx/validate",
        json={"content": SAMPLE_TMX}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["unit_count"] == 3

def test_xliff_with_tags_processing():
    """测试带标签的XLIFF处理"""
    service = XliffProcessorService()
    
    result = service.process_xliff_with_tags("test_tags.xliff", XLIFF_WITH_TAGS)
    
    assert len(result) == 2
    assert "<g id=\"1\">" in result[0].source
    assert "<g id=\"1\">" in result[0].target
    assert "<ph id=\"ph1\">" in result[1].source

def test_api_process_xliff_with_tags_endpoint():
    """测试带标签的XLIFF处理API端点"""
    response = client.post(
        "/api/xliff/process-with-tags",
        json={
            "fileName": "test_tags.xliff",
            "content": XLIFF_WITH_TAGS
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert "<g id=\"1\">" in data["data"][0]["source"]

def test_xliff_translation_replacement():
    """测试XLIFF翻译替换"""
    service = XliffProcessorService()
    
    translations = [
        {"segNumber": 3, "aiResult": "退出应用程序", "mtResult": None}
    ]
    
    updated_content, count = service.replace_xliff_targets(SAMPLE_XLIFF, translations)
    
    assert count == 1
    assert "退出应用程序" in updated_content
    assert "<target>退出应用程序</target>" in updated_content

def test_tmx_translation_replacement():
    """测试TMX翻译替换"""
    service = TmxProcessorService()
    
    translations = [
        {"segNumber": 3, "aiResult": "退出应用程序", "mtResult": None}
    ]
    
    updated_content, count = service.replace_tmx_targets(SAMPLE_TMX, translations)
    
    assert count == 1
    assert "退出应用程序" in updated_content

def test_api_xliff_replacement_endpoint():
    """测试XLIFF替换API端点"""
    response = client.post(
        "/api/replacement/xliff",
        json={
            "fileName": "test.xliff",
            "content": SAMPLE_XLIFF,
            "translations": [
                {"segNumber": 3, "aiResult": "退出应用程序"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["replacements_count"] == 1
    assert "退出应用程序" in data["content"]

def test_api_tmx_replacement_endpoint():
    """测试TMX替换API端点"""
    response = client.post(
        "/api/replacement/tmx",
        json={
            "fileName": "test.tmx",
            "content": SAMPLE_TMX,
            "translations": [
                {"segNumber": 3, "aiResult": "退出应用程序"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["replacements_count"] == 1
    assert "退出应用程序" in data["content"]

def test_api_auto_replacement_endpoint():
    """测试自动识别替换API端点"""
    # 测试XLIFF自动识别
    response = client.post(
        "/api/replacement/auto",
        json={
            "fileName": "test.xliff",
            "content": SAMPLE_XLIFF,
            "translations": [
                {"segNumber": 3, "aiResult": "退出应用程序"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "XLIFF" in data["message"]
    assert data["replacements_count"] == 1
    
    # 测试TMX自动识别
    response = client.post(
        "/api/replacement/auto",
        json={
            "fileName": "test.tmx",
            "content": SAMPLE_TMX,
            "translations": [
                {"segNumber": 3, "aiResult": "退出应用程序"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "TMX" in data["message"]
    assert data["replacements_count"] == 1

def test_tmx_tag_cleaning():
    """测试TMX标签清理功能"""
    service = TmxProcessorService()
    
    # 测试带标签的内容
    tagged_content = 'Hello <ph>&lt;mq:rxt displaytext="\\n" val="\\n" /&gt;</ph>World'
    cleaned = service.clean_tmx_tags(tagged_content)
    assert cleaned == "Hello \nWorld"
    
    # 测试颜色标签
    color_content = '<bpt>&lt;mq:rxt val="&lt;font color=red&gt;"&gt;</bpt>Red Text<ept>&lt;/mq:rxt val="&lt;/font&gt;"&gt;</ept>'
    cleaned = service.clean_tmx_tags(color_content)
    assert cleaned == "<font color=red>Red Text</font>"

def test_all_health_endpoints():
    """测试所有健康检查端点"""
    endpoints = ["/health", "/api/xliff/health", "/api/tmx/health", "/api/replacement/health"]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])