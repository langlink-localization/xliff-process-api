# API 安全配置指南

## 概述

为了保护 XLIFF Process API 服务器的安全，我们实施了基于访问密钥（Access Key）的认证机制。所有 API 端点（除公开端点外）都需要提供有效的访问密钥才能访问。

## 快速开始

### 1. 设置访问密钥

#### 方法一：使用环境变量文件（推荐）

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件
# 将 API_ACCESS_KEY 的值修改为你的密钥
API_ACCESS_KEY=your-secure-access-key-here
```

#### 方法二：直接设置环境变量

```bash
export API_ACCESS_KEY=your-secure-access-key-here
python main.py
```

### 2. 生成安全的访问密钥

建议使用以下方法生成安全的随机密钥：

```bash
# 使用 OpenSSL
openssl rand -hex 32

# 使用 Python
python -c "import secrets; print(secrets.token_hex(32))"

# 使用 UUID
python -c "import uuid; print(str(uuid.uuid4()))"
```

## 认证方式

### 方式一：Authorization Header（推荐）

在请求头中添加 Bearer Token：

```http
Authorization: Bearer your-access-key-here
```

示例：
```bash
curl -X POST "http://localhost:8848/api/xliff/process" \
  -H "Authorization: Bearer your-access-key-here" \
  -H "Content-Type: application/json" \
  -d '{"fileName": "test.xliff", "content": "..."}'
```

### 方式二：查询参数

在 URL 中添加 `access_key` 参数：

```http
http://localhost:8848/api/xliff/process?access_key=your-access-key-here
```

示例：
```bash
curl -X POST "http://localhost:8848/api/xliff/process?access_key=your-access-key-here" \
  -H "Content-Type: application/json" \
  -d '{"fileName": "test.xliff", "content": "..."}'
```

## 公开端点

以下端点不需要认证：

| 端点 | 说明 |
|------|------|
| `/` | 根路径，返回服务基本信息 |
| `/health` | 健康检查端点 |
| `/docs` | Swagger API 文档 |
| `/redoc` | ReDoc API 文档 |
| `/openapi.json` | OpenAPI 规范文件 |

## 测试认证功能

运行测试脚本验证认证功能是否正常工作：

```bash
# 确保服务器正在运行
python main.py

# 在另一个终端运行测试
python test_auth.py
```

## 安全最佳实践

### 1. 密钥管理

- **永远不要**将真实的访问密钥提交到版本控制系统
- 使用强随机密钥（至少 32 个字符）
- 定期轮换访问密钥
- 为不同环境使用不同的密钥（开发、测试、生产）

### 2. 传输安全

- 在生产环境中始终使用 HTTPS
- 使用 Authorization Header 而不是查询参数（避免密钥出现在日志中）
- 配置适当的 CORS 策略

### 3. 监控和日志

- 监控失败的认证尝试
- 记录异常的访问模式
- 设置告警机制

### 4. 环境隔离

```bash
# 开发环境
API_ACCESS_KEY=dev-key-only-for-development

# 测试环境  
API_ACCESS_KEY=test-key-for-testing

# 生产环境
API_ACCESS_KEY=production-secure-random-key
```

## Docker 部署安全配置

### 使用 Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - API_ACCESS_KEY=${API_ACCESS_KEY}
    env_file:
      - .env  # 从文件读取环境变量
```

### 使用 Docker Run

```bash
docker run -p 8848:8848 \
  -e API_ACCESS_KEY=your-secure-key \
  xliff-process-api
```

### 使用 Docker Secrets（推荐用于生产）

```bash
# 创建 secret
echo "your-secure-key" | docker secret create api_access_key -

# 在 docker-compose.yml 中使用
services:
  api:
    secrets:
      - api_access_key
    environment:
      - API_ACCESS_KEY_FILE=/run/secrets/api_access_key
```

## 故障排除

### 问题：收到 401 Unauthorized 错误

- 检查是否提供了访问密钥
- 确认请求格式正确（Bearer token 或查询参数）

### 问题：收到 403 Forbidden 错误

- 验证访问密钥是否正确
- 检查 .env 文件中的 API_ACCESS_KEY 值
- 确认环境变量已正确加载

### 问题：公开端点也需要认证

- 检查 config.py 中的 EXCLUDE_PATHS 配置
- 确认中间件配置正确

## 客户端集成示例

### JavaScript/TypeScript

```typescript
class APIClient {
  private baseURL: string;
  private accessKey: string;
  
  constructor(baseURL: string, accessKey: string) {
    this.baseURL = baseURL;
    this.accessKey = accessKey;
  }
  
  async request(endpoint: string, options: RequestInit = {}) {
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${this.accessKey}`,
      'Content-Type': 'application/json',
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('未授权：需要提供访问密钥');
      } else if (response.status === 403) {
        throw new Error('禁止访问：访问密钥无效');
      }
      throw new Error(`请求失败: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// 使用示例
const client = new APIClient('http://localhost:8848', 'your-access-key');
const result = await client.request('/api/xliff/process', {
  method: 'POST',
  body: JSON.stringify({ fileName: 'test.xliff', content: '...' }),
});
```

### Python

```python
import requests
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str, access_key: str):
        self.base_url = base_url
        self.access_key = access_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_key}'
        })
    
    def request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code == 401:
            raise Exception('未授权：需要提供访问密钥')
        elif response.status_code == 403:
            raise Exception('禁止访问：访问密钥无效')
        
        response.raise_for_status()
        return response.json()

# 使用示例
client = APIClient('http://localhost:8848', 'your-access-key')
result = client.request('/api/xliff/process', 'POST', 
                        json={'fileName': 'test.xliff', 'content': '...'})
```

## 更多信息

- 查看 [README.md](README.md) 了解完整的 API 文档
- 查看 [test_auth.py](test_auth.py) 了解认证测试示例
- 查看 [config.py](config.py) 了解配置选项