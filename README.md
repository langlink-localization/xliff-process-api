# XLIFF Process API

基于Python和[Translate Toolkit](https://github.com/translate/translate)构建的高性能XLIFF处理API服务器，用于替代JavaScript/TypeScript的XLIFF处理方案。

> **致谢**: 本项目基于优秀的开源项目 [Translate Toolkit](https://github.com/translate/translate) 构建，该项目为翻译文件格式处理提供了强大的Python库支持。

## 功能特性

- ✅ 完整支持XLIFF 1.2/2.0/2.1格式
- ✅ RESTful API接口
- ✅ 自动生成API文档（Swagger/ReDoc）
- ✅ 文件上传和内容处理
- ✅ XLIFF格式验证
- ✅ Docker容器化部署
- ✅ 高性能异步处理
- ✅ CORS支持

## 技术栈

- **Python 3.13**: 主要开发语言
- **FastAPI**: 高性能Web框架
- **Translate Toolkit**: XLIFF文件处理核心库
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器
- **Docker**: 容器化部署

## 快速开始

### 1. 本地开发

#### 安装依赖

```bash
cd xliff-process-api
pip install -r requirements.txt
```

#### 配置访问密钥

复制环境变量配置文件并设置你的访问密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的访问密钥：
```env
API_ACCESS_KEY=your-secure-access-key-here
```

建议使用以下命令生成安全的随机密钥：
```bash
openssl rand -hex 32
```

#### 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:8848` 启动

### 2. Docker部署

#### 使用Docker Compose

首先设置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件设置 API_ACCESS_KEY
```

启动服务：
```bash
docker-compose up -d
```

#### 单独构建Docker镜像

```bash
docker build -t xliff-process-api .
docker run -p 8848:8848 -e API_ACCESS_KEY=your-secure-key xliff-process-api
```

## API文档

启动服务器后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8848/docs`
- ReDoc: `http://localhost:8848/redoc`

## API认证

为了保护API安全，所有API端点（除了健康检查和文档端点）都需要提供访问密钥进行认证。

### 认证方式

支持两种认证方式：

#### 1. Authorization Header（推荐）

在请求头中添加 Bearer Token：
```
Authorization: Bearer your-access-key-here
```

#### 2. 查询参数

在URL中添加 `access_key` 参数：
```
http://localhost:8848/api/xliff/process?access_key=your-access-key-here
```

### 无需认证的端点

以下端点不需要认证：
- `/` - 根路径
- `/health` - 健康检查
- `/docs` - Swagger文档
- `/redoc` - ReDoc文档
- `/openapi.json` - OpenAPI规范

## API端点

### XLIFF处理

#### 1. 标准XLIFF处理
**POST** `/api/xliff/process`

#### 2. 带标签XLIFF处理（保留内部标记）
**POST** `/api/xliff/process-with-tags`

#### 3. 上传XLIFF文件
**POST** `/api/xliff/upload`

#### 4. 验证XLIFF格式
**POST** `/api/xliff/validate`

请求体：
```json
{
  "fileName": "example.xliff",
  "content": "<?xml version=\"1.0\"?>..."
}
```

响应：
```json
{
  "data": [
    {
      "fileName": "example.xliff",
      "segNumber": 1,
      "percent": 100,
      "source": "Hello World",
      "target": "你好世界",
      "srcLang": "en",
      "tgtLang": "zh"
    }
  ],
  "success": true,
  "message": "成功处理 1 个翻译单元"
}
```

### TMX处理

#### 1. 处理TMX内容
**POST** `/api/tmx/process`

#### 2. 上传TMX文件
**POST** `/api/tmx/upload`

#### 3. 验证TMX格式
**POST** `/api/tmx/validate`

请求体：
```json
{
  "fileName": "example.tmx",
  "content": "<?xml version=\"1.0\"?>..."
}
```

响应：
```json
{
  "data": [
    {
      "id": "1",
      "fileName": "example.tmx",
      "segNumber": 1,
      "percent": -1,
      "source": "Hello World",
      "target": "你好世界",
      "noTagSource": "Hello World",
      "noTagTarget": "你好世界",
      "contextId": "context1",
      "creator": "user1",
      "changer": "user2",
      "srcLang": "en",
      "tgtLang": "zh"
    }
  ],
  "success": true,
  "message": "成功处理 1 个TMX翻译单元"
}
```

### 翻译替换

#### 1. 替换XLIFF翻译
**POST** `/api/replacement/xliff`

#### 2. 替换TMX翻译
**POST** `/api/replacement/tmx`

#### 3. 自动识别并替换
**POST** `/api/replacement/auto`

请求体：
```json
{
  "fileName": "example.xliff",
  "content": "<?xml version=\"1.0\"?>...",
  "translations": [
    {
      "segNumber": 1,
      "aiResult": "AI翻译结果",
      "mtResult": "机器翻译结果"
    }
  ]
}
```

响应：
```json
{
  "content": "更新后的文件内容...",
  "success": true,
  "message": "成功替换 1 个翻译单元",
  "replacements_count": 1
}
```

### 健康检查

#### 1. 总体健康检查
**GET** `/health`

#### 2. 各服务健康检查
- **GET** `/api/xliff/health`
- **GET** `/api/tmx/health`  
- **GET** `/api/replacement/health`

响应：
```json
{
  "status": "healthy",
  "service": "xliff-process-api",
  "version": "1.0.0"
}
```

## 项目结构

```
xliff-process-api/
├── api/
│   └── routes/
│       └── xliff.py          # XLIFF相关路由
├── models/
│   └── xliff.py              # 数据模型定义
├── services/
│   └── xliff_processor.py    # XLIFF处理服务
├── tests/
│   ├── test_xliff.py         # 单元测试
│   └── fixtures/             # 测试数据
├── main.py                   # 主应用程序
├── requirements.txt          # 依赖包列表
├── Dockerfile               # Docker镜像定义
├── docker-compose.yml       # Docker Compose配置
└── README.md               # 项目文档
```

## 测试

运行测试：

```bash
pytest tests/ -v
```

## 客户端集成示例

### JavaScript/TypeScript

```typescript
const API_ACCESS_KEY = 'your-access-key-here';
const API_BASE_URL = 'http://localhost:8848';

// 处理XLIFF文件（使用 Authorization Header）
async function processXliff(fileName: string, content: string) {
  const response = await fetch(`${API_BASE_URL}/api/xliff/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_ACCESS_KEY}`
    },
    body: JSON.stringify({
      fileName,
      content
    }),
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('认证失败：需要提供访问密钥');
    } else if (response.status === 403) {
      throw new Error('认证失败：访问密钥无效');
    }
    throw new Error(`请求失败: ${response.statusText}`);
  }
  
  const result = await response.json();
  return result.data;
}

// 上传XLIFF文件（使用查询参数）
async function uploadXliff(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/xliff/upload?access_key=${API_ACCESS_KEY}`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('认证失败：需要提供访问密钥');
    } else if (response.status === 403) {
      throw new Error('认证失败：访问密钥无效');
    }
    throw new Error(`请求失败: ${response.statusText}`);
  }
  
  const result = await response.json();
  return result.data;
}
```

### Python

```python
import requests

API_ACCESS_KEY = 'your-access-key-here'
API_BASE_URL = 'http://localhost:8848'

def process_xliff(file_name: str, content: str):
    """处理XLIFF文件"""
    headers = {
        'Authorization': f'Bearer {API_ACCESS_KEY}'
    }
    
    response = requests.post(
        f'{API_BASE_URL}/api/xliff/process',
        headers=headers,
        json={
            'fileName': file_name,
            'content': content
        }
    )
    
    if response.status_code == 401:
        raise Exception('认证失败：需要提供访问密钥')
    elif response.status_code == 403:
        raise Exception('认证失败：访问密钥无效')
    
    response.raise_for_status()
    return response.json()['data']

def upload_xliff(file_path: str):
    """上传XLIFF文件"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        params = {'access_key': API_ACCESS_KEY}
        
        response = requests.post(
            f'{API_BASE_URL}/api/xliff/upload',
            files=files,
            params=params
        )
        
        response.raise_for_status()
        return response.json()['data']
```

### cURL

```bash
# 使用 Authorization Header
curl -X POST "http://localhost:8848/api/xliff/process" \
  -H "Authorization: Bearer your-access-key-here" \
  -H "Content-Type: application/json" \
  -d '{"fileName": "test.xliff", "content": "<?xml version=\"1.0\"?>..."}'

# 使用查询参数
curl -X POST "http://localhost:8848/api/xliff/process?access_key=your-access-key-here" \
  -H "Content-Type: application/json" \
  -d '{"fileName": "test.xliff", "content": "<?xml version=\"1.0\"?>..."}'
```

## 性能优化建议

1. **缓存**: 集成Redis缓存频繁访问的XLIFF解析结果
2. **异步队列**: 使用Celery处理大文件
3. **负载均衡**: 使用Nginx或Traefik进行负载均衡
4. **监控**: 集成Prometheus和Grafana进行性能监控

## 环境变量

可以通过环境变量配置服务器：

- `API_ACCESS_KEY`: API访问密钥（必填，用于保护API安全）
- `LOG_LEVEL`: 日志级别 (debug, info, warning, error)
- `HOST`: 服务器主机地址 (默认: 0.0.0.0)
- `PORT`: 服务器端口 (默认: 8848)

## 对比原JavaScript方案的优势

| 特性 | JavaScript方案 | Python + Translate Toolkit方案 |
|-----|--------------|--------------------------------|
| XLIFF格式支持 | 基础DOM解析 | 完整的XLIFF 1.2/2.0/2.1支持 |
| 性能 | 单线程限制 | 多进程/异步处理 |
| 扩展性 | 需要自行实现 | 丰富的翻译工具生态 |
| 维护性 | 自定义解析逻辑 | 标准化的API接口 |
| 错误处理 | 基础 | 完善的异常处理机制 |

## 致谢

本项目基于以下优秀的开源项目：

- **[Translate Toolkit](https://github.com/translate/translate)**: 提供了强大的翻译文件格式处理能力，是本API服务器的核心依赖
- **[FastAPI](https://fastapi.tiangolo.com/)**: 现代化、快速的Python Web框架
- **Python翻译工具生态系统**: 感谢所有为Python翻译工具生态做出贡献的开发者们

特别感谢Translate Toolkit项目团队，他们的工作使得专业级的翻译文件处理成为可能。

## 许可证

MIT License

本项目遵循MIT许可证，但请注意我们依赖的Translate Toolkit项目有自己的许可证要求。

## 贡献

欢迎提交Issue和Pull Request！

在贡献代码前，请确保：
1. 遵循现有的代码风格
2. 添加适当的测试
3. 更新相关文档

## 支持

如有问题，请提交Issue或联系维护团队。