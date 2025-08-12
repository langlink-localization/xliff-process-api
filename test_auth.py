#!/usr/bin/env python3
"""
测试API认证功能
"""
import requests
import sys

# 配置
API_BASE_URL = "http://localhost:8848"
VALID_ACCESS_KEY = "sk-xliff-api-2024-secure-key-change-this-in-production"  # 从 .env 文件获取
INVALID_ACCESS_KEY = "invalid-key-12345"

def test_no_auth():
    """测试不带认证的请求"""
    print("1. 测试不带认证的请求...")
    
    # 测试受保护的端点
    response = requests.post(f"{API_BASE_URL}/api/xliff/validate", 
                            json={"content": "test"})
    
    if response.status_code == 401:
        print("   ✅ 未提供密钥，返回401 Unauthorized")
    else:
        print(f"   ❌ 预期401，实际返回 {response.status_code}")
        return False
    
    # 测试公开端点
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        print("   ✅ 健康检查端点无需认证")
    else:
        print(f"   ❌ 健康检查失败，返回 {response.status_code}")
        return False
    
    return True

def test_invalid_auth():
    """测试使用无效密钥"""
    print("\n2. 测试使用无效密钥...")
    
    # 使用 Header
    headers = {"Authorization": f"Bearer {INVALID_ACCESS_KEY}"}
    response = requests.post(f"{API_BASE_URL}/api/xliff/validate", 
                            headers=headers,
                            json={"content": "test"})
    
    if response.status_code == 403:
        print("   ✅ 无效密钥（Header），返回403 Forbidden")
    else:
        print(f"   ❌ 预期403，实际返回 {response.status_code}")
        return False
    
    # 使用查询参数
    response = requests.post(f"{API_BASE_URL}/api/xliff/validate?access_key={INVALID_ACCESS_KEY}", 
                            json={"content": "test"})
    
    if response.status_code == 403:
        print("   ✅ 无效密钥（查询参数），返回403 Forbidden")
    else:
        print(f"   ❌ 预期403，实际返回 {response.status_code}")
        return False
    
    return True

def test_valid_auth():
    """测试使用有效密钥"""
    print("\n3. 测试使用有效密钥...")
    
    # 准备测试数据
    test_xliff = '''<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="zh" datatype="plaintext" original="test.txt">
    <body>
      <trans-unit id="1">
        <source>Hello World</source>
        <target>你好世界</target>
      </trans-unit>
    </body>
  </file>
</xliff>'''
    
    # 使用 Header
    headers = {"Authorization": f"Bearer {VALID_ACCESS_KEY}"}
    response = requests.post(f"{API_BASE_URL}/api/xliff/validate", 
                            headers=headers,
                            json={"content": test_xliff})
    
    if response.status_code == 200:
        data = response.json()
        if data.get("valid"):
            print("   ✅ 有效密钥（Header），请求成功")
        else:
            print("   ⚠️ 请求成功但XLIFF验证失败")
    else:
        print(f"   ❌ 预期200，实际返回 {response.status_code}")
        print(f"      响应: {response.text}")
        return False
    
    # 使用查询参数
    response = requests.post(f"{API_BASE_URL}/api/xliff/validate?access_key={VALID_ACCESS_KEY}", 
                            json={"content": test_xliff})
    
    if response.status_code == 200:
        data = response.json()
        if data.get("valid"):
            print("   ✅ 有效密钥（查询参数），请求成功")
        else:
            print("   ⚠️ 请求成功但XLIFF验证失败")
    else:
        print(f"   ❌ 预期200，实际返回 {response.status_code}")
        print(f"      响应: {response.text}")
        return False
    
    return True

def test_public_endpoints():
    """测试公开端点"""
    print("\n4. 测试公开端点...")
    
    endpoints = [
        ("/", "根路径"),
        ("/health", "健康检查")
    ]
    
    for endpoint, name in endpoints:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            print(f"   ✅ {name} 无需认证")
        else:
            print(f"   ❌ {name} 返回 {response.status_code}")
            return False
    
    return True

def main():
    print("=" * 50)
    print("XLIFF Process API 认证测试")
    print("=" * 50)
    
    try:
        # 检查服务器是否运行
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ 服务器未响应，请先启动服务器")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务器，请确保服务器运行在 http://localhost:8848")
        sys.exit(1)
    
    # 运行测试
    tests = [
        test_no_auth,
        test_invalid_auth,
        test_valid_auth,
        test_public_endpoints
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 50)
    if all(results):
        print("✅ 所有测试通过！API认证功能正常工作。")
    else:
        print("❌ 部分测试失败，请检查配置。")
        sys.exit(1)

if __name__ == "__main__":
    main()